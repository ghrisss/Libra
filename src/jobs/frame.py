import depthai as dai
import cv2
from time import time
from datetime import datetime
from src.configs import TIME_MODE, FRAME_NAME
from src.controllers.device import DeviceController
from src.controllers.frame import FrameController

class FrameJob():
    def __init__(self) -> None:
        pass
    
    @classmethod
    def run(cls):
        
        inicio = datetime.timestamp(datetime.now())
        try:
            while True:
                colorFrames = DeviceController.rgbOut.tryGet() # metodo tryGet(): tenta recuperar uma mensagem da queue. Caso não tenha mensagem, retorna imediatamente com 'nullptr'
                if colorFrames is not None:
                    frame = colorFrames.getCvFrame()
                    # frame = cv2.pyrDown(frame)
                    if TIME_MODE.get('CASE'):
                        cv2.imshow(f'Capture in {TIME_MODE.get("TIME")} seconds', frame)
                    else:
                        cv2.imshow('Press the C key to print a frame or Q key to exit', frame)

                if DeviceController.frameOut.has():
                    file_name = f"{FRAME_NAME}_{int(time() * 1000)}.jpeg"
                    with open(file_name, "wb") as f:
                        f.write(DeviceController.frameOut.get().getData())
                        print('[FrameJob] Imagem salva como:', file_name)
                        
                    FrameController.tranferFile(dir_name=FRAME_NAME, file_name=file_name)
                    if TIME_MODE.get('CASE'):
                        break
                        
                key = cv2.waitKey(1)
                
                if key == ord('q'):
                    break
                elif TIME_MODE.get('CASE'):
                    atual = datetime.timestamp(datetime.now())
                    if atual - inicio >= TIME_MODE.get('TIME'):
                        ctrl = dai.CameraControl()
                        ctrl.setCaptureStill(True)
                        DeviceController.controlIn.send(ctrl)
                elif key == ord('c'):
                    ctrl = dai.CameraControl()
                    ctrl.setCaptureStill(True)
                    DeviceController.controlIn.send(ctrl)
                    print('[FrameJob] Envio de um sinal à câmera')
        except Exception as e:
            print(e)