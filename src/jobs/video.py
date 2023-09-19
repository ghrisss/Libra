from time import time

import cv2
import depthai as dai

from src.configs import FRAME
from src.controllers.device import DeviceController
from src.controllers.files import FilesController


class videoJob():

    def run(self):
        try:
            while True:
                colorFrames = DeviceController.rgbOut.get() # metodo get(): bloqueia até uma mensagem estar disponível, diferente dos metodos try, que não bloqueiam a recursão
                if colorFrames is not None:
                    frame = colorFrames.getCvFrame()
                    # frame = cv2.pyrDown(frame)
                    cv2.imshow('Press the C key to print a frame or Q key to exit', frame)
                if DeviceController.frameOut.has():
                    file_name = f"{FRAME.get('NAME')}_{int(time() * 1000)}.jpeg"
                    with open(file_name, "wb") as f:
                        f.write(DeviceController.frameOut.get().getData())
                        print('[FrameJob] Imagem salva como:', file_name)
                        
                    FilesController.transferFile(dir_name=FRAME.get('NAME'), file_name=file_name)
                key = cv2.waitKey(1)
                if key in (ord('q'), ord('Q')):
                    break
                elif key in (ord('c'), ord('C')):
                    ctrl = dai.CameraControl()
                    ctrl.setCaptureStill(True)
                    DeviceController.controlIn.send(ctrl)
                    print('[FrameJob] Envio de um sinal à câmera')
        except Exception as e:
            print(e)
                
