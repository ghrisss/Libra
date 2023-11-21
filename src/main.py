from src.configs import FRAME
from src.controllers.device import DeviceController
from src.controllers.pipeline import PipelineController
from src.jobs.frame import FrameJob
from src.jobs.manager import ManagerJob
from src.models.device import Device

def preparacao():
  FRAME['CV'] = True
  
def operacao():
  FRAME['CV'] = False
  

if FRAME.get('CV'):
  # operação
  frame_job = FrameJob()
  Device.setColorCameraEnable(True) and Device.setFrameEnable(True)
  pipeline = PipelineController.getPipeline()
  DeviceController.setDevice(pipeline=pipeline)
  frame_job.run()
else:
  # preparação
  managerJob = ManagerJob()
  managerJob.run()
  


'''
TODO:

- para diminuir o log no terminal, apenas mostrar no terminal mensagens após um determinado tempo sem mudança, ou de tempos em tempos
  Outra solução seria comparar os valores do job com o model, e havendo mudança seria impresso no og, o que evitaria prints com valores 0 repetidos
- fazer uma forma de caso seja utilizado a tecla 'esc' em qualquer input, voltar para o input anterior
- as parte de comando através da key vinda do cv2.waitKey() poderia ser feito mo FrameController, uma vez que a nomeclatura faz mais sentido e dessa forma poderia ser reaproveitado 
  funções como a de encerrar o loop do video, e o de captura
- Fazer um executável do programa python, e as configurações do arquivo 'configs.py' podem ser alterados através da interface criada como PySimpleGUI

TODO: toda a parte de mostrar a imagem para a o usuário ficara na parte de views
FIXME: verificar a questão do primeiro video abrir em background e os demais abrirem em primeiro plano, até encerrar a conexão com a câmera
'''