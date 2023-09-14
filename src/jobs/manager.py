import keyboard
import cv2
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
        
    def runFrame(self):
        if Device.getUseCamera():
            pipeline = PipelineController.getPipeline()
            DeviceController.setDevice(pipeline=pipeline)
            # TODO: ter uma seleção de número de fotos que serão tiradas antes de ir para o Job
            self.job.run()
    
    def run(self):
        print("Selecione a operação que deseja")
        print("Pressione 1 para Video")
        print("Pressione 2 para Configuração")
        print("Pressione 3 para Captura de Imagens")
        while True:
            try:
                Device.setUseCamera(True)
                Device.setColorCameraEnable(True)

                if keyboard.is_pressed('1'):
                    Device.setVideoEnable(True)
                    self.job = videoJob()
                    print('[ManagerJob] Rodando video')
                    self.runVideo()
                    cv2.destroyAllWindows()
                        
                elif keyboard.is_pressed('2'):
                    Device.setDraftEnable(True)
                    self.job = DraftJob()
                    print('[ManagerJob] Rodando draft')
                    self.runDraft()
                    cv2.destroyAllWindows()
                        
                elif keyboard.is_pressed('3'):
                    Device.setFrameEnable(True)
                    self.job = FrameJob()
                    print('[ManagerJob] Rodando frame')
                    self.runFrame()
                    cv2.destroyAllWindows()
                        
                if Device.device is not None and not Device.device.isClosed():
                    Device.device.close()
                    self.job = None
                    if DEBUG:
                        print("[ManagerJob] Conexão com a câmera foi encerrada: ", Device.device.isClosed())
                    print('*'*160)
                    print("Selecione a operação que deseja")
                    print("Pressione 1 para Video")
                    print("Pressione 2 para Configuração")
                    print("Pressione 3 para Captura de Imagens")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print('[Erro]', e)
                break  # se o usuário pressionar outra tecla, o loop será interrompido