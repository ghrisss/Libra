from src.configs import FRAME
from src.controllers.device import DeviceController
from src.controllers.pipeline import PipelineController
from src.jobs.frame import FrameJob
from src.jobs.manager import ManagerJob

if FRAME.get('CASE'):
    pipeline = PipelineController.getPipeline()
    DeviceController.setDevice(pipeline=pipeline)
    FrameJob.run()
else:
    managerJob = ManagerJob()
    managerJob.run()


'''
TODO:

- em caso de não haver crop, no uso das teclas de crop, mostrar mensagem de crop indisponível
  a maneira que pensei em fazer isso no momento seria verificar a variável 'aspect_ratio', onde sendo None, não existiria crop, mas a variável vai sair do local onde esstá no momento
- para diminuir o log no terminal, apenas mostrar no terminal mensagens após um determinado tempo sem mudança, ou de tempos em tempos
  Outra solução seria comparar os valores do job com o model, e havendo mudança seria impresso no og, o que evitaria prints com valores 0 repetidos
- no draft, ter uma tecla para reverter as alterações feitas
- fazer uma forma de caso seja utilizado a tecla 'esc' em qualquer input, voltar para o input anterior
- as parte de comando através da key vinda do cv2.waitKey() poderia ser feito mo FrameController, uma vez que a nomeclatura faz mais sentido e dessa forma poderia ser reaproveitado 
  funções como a de encerrar o loop do video, e o de captura
- Fazer um executável do programa python, e as configurações do arquivo 'configs.py' podem ser alterados através da interface criada como PySimpleGUI

TODO: toda a parte de mostrar a imagem para a o usuário ficara na parte de views
FIXME: verificar a questão do primeiro video abrir em background e os demais abrirem em primeiro plano, até encerrar a conexão com a câmera
'''