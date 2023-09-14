import cv2
import sys
from src.jobs.video import videoJob
from src.jobs.draft import DraftJob
from src.jobs.frame import FrameJob
from src.models.device import Device
from src.controllers.device import DeviceController
from src.controllers.pipeline import PipelineController
from src.configs import DEBUG

class ManagerJob():
    
    job = None
    
    def runVideo(self):
        if Device.getUseCamera():
            pipeline = PipelineController.getPipeline()
            DeviceController.setDevice(pipeline=pipeline)
            self.job.run()
    
    def runDraft(self):
        if Device.getUseCamera():
            pipeline = PipelineController.getPipeline()
            DeviceController.setDevice(pipeline=pipeline)
            self.job.run(rgb_node=pipeline.getNode(0))
        
    def runFrame(self, numero_frames = 1):
        if Device.getUseCamera():
            pipeline = PipelineController.getPipeline()
            DeviceController.setDevice(pipeline=pipeline)
            self.job.run(numero_frames)
    
    def run(self):
        try:
            print('='*160)
            print("     ---     ESCOLHA DE MODOS        ---     \nPressione 1 para Video \nPressione 2 para Configuração \nPressione 3 para Captura de Imagens")
            modo = input("Selecione a operação que deseja: ")
        except KeyboardInterrupt:
            sys.exit(0)
        while True:
            try:
                Device.setUseCamera(True)
                Device.setColorCameraEnable(True)
                match modo:
                
                    case '1':
                        Device.setVideoEnable(True)
                        self.job = videoJob()
                        print('*'*160)
                        print('[ManagerJob] Rodando video')
                        self.runVideo()
                        cv2.destroyAllWindows()
                            
                    case '2':
                        Device.setDraftEnable(True)
                        self.job = DraftJob()
                        print('*'*160)
                        print('[ManagerJob] Rodando draft')
                        self.runDraft()
                        cv2.destroyAllWindows()
                            
                    case '3':
                        numero_frames = input("digite quantos frames deseja tirar: ")
                        Device.setFrameEnable(True)
                        self.job = FrameJob()
                        print('*'*160)
                        print('[ManagerJob] Rodando frame')
                        self.runFrame(numero_frames=int(numero_frames))
                        cv2.destroyAllWindows()
                    
                    case _:
                        print("Utilize um modo válido")
                        modo = input("Selecione a operação que deseja: ")
                        
                if Device.device is not None and not Device.device.isClosed():
                    Device.device.close()
                    self.job = None
                    if DEBUG:
                        print("[ManagerJob] Conexão com a câmera foi encerrada: ", Device.device.isClosed())
                    print('*'*160)
                    print("     ---     ESCOLHA DE MODOS        ---     \nPressione 1 para Video \nPressione 2 para Configuração \nPressione 3 para Captura de Imagens")
                    modo = input("Selecione a operação que deseja: ")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print('[Erro]', e)
                break  # se o usuário pressionar outra tecla, o loop será interrompido