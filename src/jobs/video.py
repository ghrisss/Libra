import cv2
# import sys
from src.controllers.device import DeviceController

class videoJob():
            
    @classmethod
    def run(cls):
        try:
            while True:
                colorFrames = DeviceController.rgbOut.get() # metodo get(): bloqueia até uma mensagem estar disponível, diferente dos metodos try, que não bloqueiam a recursão
                cv2.imshow('Video from Color Camera', colorFrames.getCvFrame())
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
        # except KeyboardInterrupt:
        #     sys.exit(0)
        except Exception as e:
            print(e)
                
