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
    
    def runDraft(self, crop = False):
        if Device.getUseCamera():
            while True:
                pipeline = PipelineController.getPipeline(crop=crop)
                DeviceController.setDevice(pipeline=pipeline)
                if not crop:
                    break
                if crop:
                    self.job.cropPreview()
                    rsp = input("o tamanho do recorte da imagem está bom? S(sim) ou N(não)?")
                    crop = False if rsp.upper() in('S', 'SIM', 'VERDADEIRO','TRUE') else True
                    Device.device.close() # TODO: talvez ver uma forma de verificar se a comunicação já foi inciciada com a câmera, com uma função, verificando se o ID é o mesmo ao invés de encerrar conexão toda vez
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
                        rsp = input("Será feito um crop da imagem - S(sim) ou N(não)? ") # ?: eventualmente ter um botão para explicar oo que é um crop?
                        crop = True if rsp.upper() in('S', 'SIM', 'VERDADEIRO','TRUE') else False
                        Device.setDraftEnable(True)
                        self.job = DraftJob()
                        print('*'*160)
                        print('[ManagerJob] Rodando draft')
                        self.runDraft(crop=crop)
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
                        print("[ManagerJob] Utilize um modo válido")
                        modo = input("[ManagerJob] Selecione a operação que deseja: ")
                        
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