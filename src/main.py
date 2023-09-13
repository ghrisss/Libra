from src.jobs.video import videoJob
from src.jobs.draft import DraftJob
from src.jobs.frame import FrameJob
from src.controllers.device import DeviceController
from src.controllers.pipeline import PipelineController

def runVideo():
    print('[Main] Rodando video')
    pipeline = PipelineController.getPipeline(name='color')
    DeviceController.setDevice(pipeline=pipeline)
    videoJob.run()
    # videoJob.frameVideo()
    
def runDraft():
    print('[Main] Rodando draft')
    pipeline = PipelineController.getPipeline(name='draft')
    DeviceController.setDevice(pipeline=pipeline)
    DraftJob.run(rgb_node=pipeline.getNode(0))
    
def runFrame():
    print('[Main] Rodando frame')
    pipeline = PipelineController.getPipeline(name='frame')
    DeviceController.setDevice(pipeline=pipeline)
    # TODO: ter uma seleção de número de fotos que serão tiradas antes de ir para o Job
    FrameJob.run()
    
# runVideo()
runDraft()
# runFrame()


'''
TODO
- FrameJob ser o modo focado no time_mode e VideoJob podendo absorver o print com a tecla 'c'
- ter a seleção de qual modo sera utilizado
- criar uma variável, possivelmente num model que represente qual opção foi selecionada, e com base nessa variável será criada a pipeline específica em getPipeline
  algo como 'self.config.useCamera' e 'self._conf.rgbCameraEnabled' e aí então entra na função 'self._pm.createColorCam(args)'
- para funcionar com o labview imagino que o modo padrão, no caso de não seleção deva ser o FrameJob
- ter a seleção se irá querer um crop ou não
- em caso de crop, alterar na pipeline o Tamanho do frame, e ter o padrão normalizado no configs de mesmo tamanho que o isp
- isp não precisa aparecer, assim como está no momento
- em caso de não haver crop, no uso das teclas de crop, mostrar mensagem de crop indisponível
- para diminuir o log no terminal, apenas mostrar no terminal mensagens após um determinado tempo sem mudança, ou de tempos em tempos

TODO: toda a parte de mostrar a imagem para a o usuário ficara na parte de views
'''