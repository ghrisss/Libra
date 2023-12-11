import argparse

from src.configs import FRAME
from src.controllers.device import DeviceController
from src.controllers.pipeline import PipelineController
from src.jobs.frame import FrameJob
from src.jobs.manager import ManagerJob
from src.models.device import Device

ap = argparse.ArgumentParser()
ap.add_argument('-v', '--vision', default=False, help="indica se o programa irá iniciar em modo de preparação/configuração(False) ou de operação(True)")
ap.add_argument('-n', '--name', help="Nome da pasta onde o arquivo de imagem será salvado")
args = vars(ap.parse_args())

if FRAME.get('VISION') or args['vision']:
  # operação
  frame_job = FrameJob()
  Device.setColorCameraEnable(True) and Device.setFrameEnable(True)
  pipeline = PipelineController.getPipeline()
  DeviceController.setDevice(pipeline=pipeline)
  res = frame_job.run(vision_mode = args['vision'], frame_name = args['name'])
  if res == {}:
    res = [False]
  print(res)
else:
  # preparação
  managerJob = ManagerJob()
  managerJob.run()
  

'''
TODO:

- fazer uma forma de caso seja utilizado a tecla 'esc' em qualquer input, voltar para o input anterior
- as parte de comando através da key vinda do cv2.waitKey() poderia ser feito mo FrameController, uma vez que a nomeclatura faz mais sentido e dessa forma poderia ser reaproveitado 
  funções como a de encerrar o loop do video, e o de captura

TODO: toda a parte de mostrar a imagem para a o usuário ficara na parte de views
FIXME: verificar a questão do primeiro video abrir em background e os demais abrirem em primeiro plano, até encerrar a conexão com a câmera
'''