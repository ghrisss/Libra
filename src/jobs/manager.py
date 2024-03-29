import sys

import cv2

from src.configs import DEBUG
from src.controllers.device import DeviceController
from src.controllers.frame import FrameController
from src.controllers.pipeline import PipelineController
from src.jobs.draft import DraftJob
from src.jobs.frame import FrameJob
from src.jobs.video import videoJob
from src.models.device import Device


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
                    rsp = input("o tamanho do recorte da imagem está bom? S(sim) ou N(não)? ")
                    crop = False if rsp.upper() in('S', 'SIM', 'VERDADEIRO','TRUE') else True
                    Device.device.close()
            self.job.run(rgb_node=pipeline.getNode(0))
        
    def runFrame(self, numero_frames = 1):
        if Device.getUseCamera():
            pipeline = PipelineController.getPipeline()
            DeviceController.setDevice(pipeline=pipeline)
            self.job.run(numero_frames)
    
    def run(self):
        try:
            print('='*120)
            print("     ---     ESCOLHA DE MODOS        ---     \nPressione 1 para Video \nPressione 2 para Configuração \nPressione 3 para Captura de Imagens")
            modo = input("Selecione a operação que deseja: ")
        except KeyboardInterrupt:
            sys.exit(0)
        while True:
            try:
                Device.setUseCamera(True)
                Device.setColorCameraEnable(True)
                # match modo:
                
                    # case '1':
                if modo=='1':
                        Device.setVideoEnable(True)
                        self.job = videoJob()
                        print('*'*120)
                        print('[ManagerJob] Rodando video')
                        self.runVideo()
                        cv2.destroyAllWindows()
                            
                    # case '2':
                elif modo=='2':
                        # rsp = input("Será feito um crop da imagem - S(sim) ou N(não)? (funcionalidade em implementação, não habilitada no momento)") # ?: eventualmente ter um botão para explicar o que é um crop?
                        # crop = False if rsp.upper() in('S', 'SIM', 'VERDADEIRO','TRUE') else False # primeira condicional foi alterado para False até ter certeza da funcionalidade e utilizade de existir essa função)
                        crop=False
                        if crop:
                            FrameController.setCropState(case=False) # aqui foi alterado para False até ter certeza da funcionalidade e utilizade de existir essa função)
                        else:
                            FrameController.setCropState(case=False)
                        Device.setDraftEnable(True)
                        self.job = DraftJob()
                        print('*'*120)
                        print('[ManagerJob] Rodando draft')
                        self.runDraft(crop=crop)
                        cv2.destroyAllWindows()
                            
                    # case '3':
                elif modo=='3':
                        numero_frames = input("digite quantos frames deseja tirar: ")
                        Device.setFrameEnable(True)
                        self.job = FrameJob()
                        print('*'*120)
                        print('[ManagerJob] Rodando frame')
                        self.runFrame(numero_frames=int(numero_frames))
                        cv2.destroyAllWindows()
                    
                    # case _:
                else:
                        print("[ManagerJob] Utilize um modo válido")
                        modo = input("Selecione a operação que deseja: ")
                        
                if Device.device is not None and not Device.device.isClosed():
                    Device.device.close()
                    self.job = None
                    if DEBUG:
                        print("[ManagerJob] Conexão com a câmera foi encerrada: ", Device.device.isClosed())
                    print('*'*120)
                    print("     ---     ESCOLHA DE MODOS        ---     \nPressione 1 para Video \nPressione 2 para Configuração \nPressione 3 para Captura de Imagens")
                    modo = input("Selecione a operação que deseja: ")

            except KeyboardInterrupt:
                break
            except Exception as e:
                print('[Erro]', e)
                break  # se o usuário pressionar outra tecla, o loop será interrompido