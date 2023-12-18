from time import time

import av
import cv2
import depthai as dai
from time import sleep

from src.configs import FRAME
from src.controllers.device import DeviceController
from src.controllers.files import FilesController
from src.controllers.frame import FrameController


class videoJob():

    def run(self):
        FrameController.getImageSetting()
        codec = av.CodecContext.create("mjpeg", "r")
        ctrl = dai.CameraControl()
        ctrl.setCaptureStill(True)
        try:
            while True:
                colorFrames = DeviceController.rgbOut.get() # metodo get(): bloqueia até uma mensagem estar disponível, diferente dos metodos try, que não bloqueiam a recursão
                if colorFrames is not None:
                    frame = colorFrames.getCvFrame()
                    # frame = cv2.pyrDown(frame)
                    cv2.imshow('Press the C key to print a frame or Q key to exit', frame)
                if DeviceController.frameOut.has():
                    file_name = f"{FRAME.get('NAME')}_{int(time() * 1000)}.png"
                    data = DeviceController.frameOut.get().getData()
                    packets = codec.parse(data)
                    packets = codec.parse(data)
                    for packet in packets:
                        frames = codec.decode(packet)
                        if frames:
                            frame = frames[0].to_ndarray(format='bgr24')
                            cv2.imwrite(file_name, frame)
                            FilesController.transferFile(dir_name=FRAME.get('NAME'), file_name=file_name)
                key = cv2.waitKey(1)
                if key in (ord('q'), ord('Q')):
                    break
                elif key in (ord('c'), ord('C')):
                    DeviceController.controlIn.send(ctrl)
                    print('[FrameJob] Envio de um sinal à câmera')
        except Exception as e:
            print(e)
                
