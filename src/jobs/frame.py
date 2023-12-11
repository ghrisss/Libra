from datetime import datetime
from time import time

import av
import cv2
import depthai as dai

from src.configs import DEBUG, FRAME
from src.controllers.device import DeviceController
from src.controllers.files import FilesController
from src.controllers.frame import FrameController
from src.jobs.cv import VisionJob


class FrameJob():
    
    def run(self, numero_frames = 1, vision_mode = False, frame_name = FRAME.get('NAME')):
        inicio = datetime.timestamp(datetime.now())
        i = 0
        # TODO: ter telas de carregamento no GUI para momentos como esse, de preparação
        FrameController.getImageSetting()
        codec = av.CodecContext.create("mjpeg", "r")
        try:
            while True:
                colorFrames = DeviceController.rgbOut.tryGet() # metodo tryGet(): tenta recuperar uma mensagem da queue. Caso não tenha mensagem, retorna imediatamente com 'nullptr'
                if colorFrames is not None:
                    frame = colorFrames.getCvFrame()
                    # frame = cv2.pyrDown(frame)
                    if FRAME.get("TIME") > 5: # mostra o video de onde será tirado o frame caso o tempo para a captura seja maior que 5 segundos
                        cv2.imshow(f'Capture in {FRAME.get("TIME")} seconds', frame)

                if DeviceController.frameOut.has():
                    file_name = f"{frame_name}_{int(time() * 1000)}.png"
                    data = DeviceController.frameOut.get().getData()
                    packets = codec.parse(data)
                    packets = codec.parse(data)
                    for packet in packets:
                        frames = codec.decode(packet)
                        if frames:
                            frame = frames[0].to_ndarray(format='bgr24')
                            cv2.imwrite(file_name, frame)
                            
                            if vision_mode:
                                vision_job = VisionJob()
                                vision_job.analysis(file_name)
                            FilesController.transferFile(dir_name=frame_name, file_name=file_name)
                            i += 1
                    if i == numero_frames:
                        break
                        
                key = cv2.waitKey(1)
                
                if key in (ord('q'), ord('Q')):
                    break
                else:
                    atual = datetime.timestamp(datetime.now())
                    if atual - inicio >= FRAME.get('TIME'):
                        ctrl = dai.CameraControl()
                        ctrl.setCaptureStill(True)
                        DeviceController.controlIn.send(ctrl)
        except Exception as e:
            print('[frameJob] ERROR: ', e)
            FilesController.transferFile(dir_name="error_frames", file_name=file_name)
            
        if vision_mode:
            return vision_job.rivet_conference
