import keyboard
import cv2
from src.jobs.video import videoJob
from src.jobs.draft import DraftJob
from src.jobs.frame import FrameJob
from src.controllers.device import DeviceController
from src.controllers.pipeline import PipelineController

class ManagerJob():
    
    job = None
    
    def runVideo(self):
        pipeline = PipelineController.getPipeline(name='color')
        DeviceController.setDevice(pipeline=pipeline)
        self.job.run()
    
    def runDraft(self):
        pipeline = PipelineController.getPipeline(name='draft')
        DeviceController.setDevice(pipeline=pipeline)
        self.job.run(rgb_node=pipeline.getNode(0))
        
    def runFrame(self):
        pipeline = PipelineController.getPipeline(name='frame')
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
                if keyboard.is_pressed('1'):
                    self.job = videoJob()
                    print('[ManagerJob] Rodando video')
                    self.runVideo()
                    cv2.destroyAllWindows()
                    if DeviceController.device.isPipelineRunning():
                        DeviceController.device.close()
                        print("[ManagerJob] Conexão com a câmera foi encerrada: ", DeviceController.device.isClosed())
                elif keyboard.is_pressed('2'):
                    self.job = DraftJob()
                    print('[ManagerJob] Rodando draft')
                    self.runDraft()
                    cv2.destroyAllWindows()
                    if DeviceController.device.isPipelineRunning():
                        DeviceController.device.close()
                        print("[ManagerJob] Conexão com a câmera foi encerrada: ", DeviceController.device.isClosed())
                elif keyboard.is_pressed('3'):
                    self.job = FrameJob()
                    print('[ManagerJob] Rodando frame')
                    self.runFrame()
                    cv2.destroyAllWindows()
                    if DeviceController.device.isPipelineRunning():
                        DeviceController.device.close()
                        print("[ManagerJob] Conexão com a câmera foi encerrada: ", DeviceController.device.isClosed())
            except KeyboardInterrupt:
                break
            except Exception as e:
                print('[Erro]', e)
                break  # se o usuário pressionar outra tecla, o loop será interrompido