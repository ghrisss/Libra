import os
import sys

# Obtém o diretório raiz do projeto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print(root_dir)
# Adiciona o diretório raiz ao caminho de busca do Python
sys.path.append(root_dir)


import cv2
import argparse
import numpy as np
import numba as nb
import depthai as dai

from src.controllers.device import DeviceController
from src.controllers.frame import FrameController


parser = argparse.ArgumentParser()
parser.add_argument('-res', '--resolution', default='1080', choices={'1080', '4k', '12mp', '13mp'},
                    help="Select RGB resolution. Default: %(default)s")
parser.add_argument('-raw', '--enable_raw', default=False, action="store_true",
                    help='Enable the color RAW stream')
parser.add_argument('-fps', '--fps', default=15, type=int,
                    help="Camera FPS. Default: %(default)s")
parser.add_argument('-lens', '--lens_position', default=-1, type=int,
                    help="Lens position for manual focus 0..255, or auto: -1. Default: %(default)s")
parser.add_argument('-ds', '--isp_downscale', default=1, type=int,
                    help="Downscale the ISP output by this factor")

args = parser.parse_args()

streams = []
# Enable one or both streams
streams.append('raw')

''' Packing scheme for RAW10 - MIPI CSI-2
- 4 pixels: p0[9:0], p1[9:0], p2[9:0], p3[9:0]
- stored on 5 bytes (byte0..4) as:
| byte0[7:0] | byte1[7:0] | byte2[7:0] | byte3[7:0] |          byte4[7:0]             |
|    p0[9:2] |    p1[9:2] |    p2[9:2] |    p3[9:2] | p3[1:0],p2[1:0],p1[1:0],p0[1:0] |
'''
# Optimized with 'numba' as otherwise would be extremely slow (55 seconds per frame!)
@nb.njit(nb.uint16[::1] (nb.uint8[::1], nb.uint16[::1], nb.boolean), parallel=True, cache=True)
def unpack_raw10(input, out, expand16bit):
    lShift = 6 if expand16bit else 0

   #for i in np.arange(input.size // 5): # around 25ms per frame (with numba)
    for i in nb.prange(input.size // 5): # around  5ms per frame
        b4 = input[i * 5 + 4]
        out[i * 4]     = ((input[i * 5]     << 2) | ( b4       & 0x3)) << lShift
        out[i * 4 + 1] = ((input[i * 5 + 1] << 2) | ((b4 >> 2) & 0x3)) << lShift
        out[i * 4 + 2] = ((input[i * 5 + 2] << 2) | ((b4 >> 4) & 0x3)) << lShift
        out[i * 4 + 3] = ((input[i * 5 + 3] << 2) |  (b4 >> 6)       ) << lShift

    return out

rgb_res_opts = {
    '1080': dai.ColorCameraProperties.SensorResolution.THE_1080_P,
    '4k'  : dai.ColorCameraProperties.SensorResolution.THE_4_K,
    '12mp': dai.ColorCameraProperties.SensorResolution.THE_12_MP,
    '13mp': dai.ColorCameraProperties.SensorResolution.THE_13_MP,
}
rgb_res = rgb_res_opts.get(args.resolution)

pipeline = dai.Pipeline()

cam = pipeline.create(dai.node.ColorCamera)
cam.setResolution(rgb_res)
# Optional, set manual focus. 255: macro (8cm), about 120..130: infinity
focus_name = 'af'
if args.lens_position >= 0:
    cam.initialControl.setManualFocus(args.lens_position)
    focus_name = 'f' + str(args.lens_position)
cam.setIspScale(1, args.isp_downscale)
cam.setFps(args.fps)  # Default: 30

controlIn = pipeline.create(dai.node.XLinkIn)
controlIn.setStreamName('control')
controlIn.out.link(cam.inputControl)

if 'raw' in streams:
    xout_raw = pipeline.create(dai.node.XLinkOut)
    xout_raw.setStreamName('raw')
    cam.raw.link(xout_raw.input)

DeviceController.setDevice(pipeline=pipeline)

q_list = []
for s in streams:
    q = DeviceController.rawOut
    q_list.append(q)
    # Make window resizable, and configure initial size
    cv2.namedWindow(s, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(s, (960, 540))


# Manual exposure/focus set step, configurable
EXP_STEP = 500  # us
ISO_STEP = 50
LENS_STEP = 1
WB_STEP = 100

# Defaults and limits for manual focus/exposure controls
lens_pos = 130
lens_min = 0
lens_max = 255

exp_time = 20000
exp_min = 1
# Note: need to reduce FPS (see .setFps) to be able to set higher exposure time
# With the custom FW, larger exposures can be set automatically (requirements not yet updated)
exp_max = int(0.99 * 1000000 / args.fps)

sens_iso = 800
sens_min = 100
sens_max = 1600

wb_manual = 4000
wb_min = 1000
wb_max = 12000

# TODO how can we make the enums automatically iterable?
awb_mode_idx = -1
awb_mode_list = [
    dai.CameraControl.AutoWhiteBalanceMode.OFF,
    dai.CameraControl.AutoWhiteBalanceMode.AUTO,
    dai.CameraControl.AutoWhiteBalanceMode.INCANDESCENT,
    dai.CameraControl.AutoWhiteBalanceMode.FLUORESCENT,
    dai.CameraControl.AutoWhiteBalanceMode.WARM_FLUORESCENT,
    dai.CameraControl.AutoWhiteBalanceMode.DAYLIGHT,
    dai.CameraControl.AutoWhiteBalanceMode.CLOUDY_DAYLIGHT,
    dai.CameraControl.AutoWhiteBalanceMode.TWILIGHT,
    dai.CameraControl.AutoWhiteBalanceMode.SHADE,
]

anti_banding_mode_idx = -1
anti_banding_mode_list = [
    dai.CameraControl.AntiBandingMode.OFF,
    dai.CameraControl.AntiBandingMode.MAINS_50_HZ,
    dai.CameraControl.AntiBandingMode.MAINS_60_HZ,
    dai.CameraControl.AntiBandingMode.AUTO,
]

effect_mode_idx = -1
effect_mode_list = [
    dai.CameraControl.EffectMode.OFF,
    dai.CameraControl.EffectMode.MONO,
    dai.CameraControl.EffectMode.NEGATIVE,
    dai.CameraControl.EffectMode.SOLARIZE,
    dai.CameraControl.EffectMode.SEPIA,
    dai.CameraControl.EffectMode.POSTERIZE,
    dai.CameraControl.EffectMode.WHITEBOARD,
    dai.CameraControl.EffectMode.BLACKBOARD,
    dai.CameraControl.EffectMode.AQUA,
]

ae_comp = 0  # Valid: -9 .. +9
ae_lock = False
awb_lock = False
saturation = 0
contrast = 0
brightness = 0
sharpness = 0
luma_denoise = 0
chroma_denoise = 0
control = 'none'

def clamp(num, v0, v1): return max(v0, min(num, v1))
FrameController.getImageSetting()

capture_flag = False
while True:
    for q in q_list:
        name = q.getName()
        data = q.get()
        width, height = data.getWidth(), data.getHeight()
        payload = data.getData()
        capture_file_info_str = ('capture_' + name
                                 + '_' + str(width) + 'x' + str(height)
                                 + '_' + focus_name
                                 + '_' + str(data.getSequenceNum())
                                )
        if name == 'raw':
            # Preallocate the output buffer
            unpacked = np.empty(payload.size * 4 // 5, dtype=np.uint16)
            if capture_flag:
                # Save to capture file on bits [9:0] of the 16-bit pixels
                unpack_raw10(payload, unpacked, expand16bit=False)
                filename = capture_file_info_str + '_10bit.bw'
                print("Saving to file:", filename)
                unpacked.tofile(filename)
            # Full range for display, use bits [15:6] of the 16-bit pixels
            unpack_raw10(payload, unpacked, expand16bit=True)
            shape = (height, width)
            bayer = unpacked.reshape(shape).astype(np.uint16)
            # See this for the ordering, at the end of page:
            # https://docs.opencv.org/4.5.1/de/d25/imgproc_color_conversions.html
            bgr = cv2.cvtColor(bayer, cv2.COLOR_BayerBG2GRAY)
        if capture_flag:  # Save to disk if `c` was pressed
            filename = capture_file_info_str + '.png'
            print("Saving to file:", filename)
            bgr = np.ascontiguousarray(bgr)  # just in case
            cv2.imwrite(filename, bgr)
        bgr = np.ascontiguousarray(bgr)  # just in case
        cv2.imshow(name, bgr)
    # Reset capture_flag after iterating through all streams
    capture_flag = False
    key = cv2.waitKey(1)
    
    if key == ord('c'):
        capture_flag = True
        
    elif key == ord('q'):
        break