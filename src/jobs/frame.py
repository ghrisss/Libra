import depthai as dai
import cv2
from time import time
from datetime import datetime
from src.configs import FRAME, DEBUG
from src.controllers.device import DeviceController
from src.controllers.frame import FrameController

class FrameJob():
    
    def run(self, numero_frames = 1):
        inicio = datetime.timestamp(datetime.now())
        i = 0
        try:
            while True:
                colorFrames = DeviceController.rgbOut.tryGet() # metodo tryGet(): tenta recuperar uma mensagem da queue. Caso não tenha mensagem, retorna imediatamente com 'nullptr'
                if colorFrames is not None:
                    frame = colorFrames.getCvFrame()
                    # frame = cv2.pyrDown(frame)
                    cv2.imshow(f'Capture in {FRAME.get("TIME")} seconds', frame)

                if DeviceController.frameOut.has():
                    file_name = f"{FRAME.get('NAME')}_{int(time() * 1000)}.jpeg"
                    with open(file_name, "wb") as f:
                        f.write(DeviceController.frameOut.get().getData())
                        if DEBUG:
                            print('[FrameJob] Imagem salva como:', file_name)
                        
                    FrameController.tranferFile(dir_name=FRAME.get('NAME'), file_name=file_name)
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
            print(e)