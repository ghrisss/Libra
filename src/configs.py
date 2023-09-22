
COLOR_CAM = {
    'VIDEO_SIZE': [1280, 720],
    'INTERLEAVED' : False,
    'FPS' : 30.0 # para resolução 4k, o máximo de fps é 42
} # configurações de video para camera colorida

QUEUE_PARAMETERS = {
    'QUEUE_SIZE' : 30,
    'QUEUE_BLOCKING' : True
} # Fila que tanto a saída como a entrada podem ter de mensagens não lidas

DRAFT = {
    'STEP_SIZE' : 8, # tamanho do corte em pixels para o crop
    'EXP_STEP' : 500, # us por vez
    'ISO_STEP': 50,
    'LENS_STEP': 3,
    'WB_STEP': 200 # white_balance
}

DB_CONFIG = {
    'FRAME_DB': 'frame.shelve' # repositório onde é mantido os dados da calibração realizada na câmera, tendo em mente não faze-los mais de uma vez
}

FRAME = {
    'CASE' : False, # Frame é o modo de fazr captura da tela, mas nesse caso, o case sendo verdadeiro o programa apenas habilita o modo Frame, onde ao iniciar, o programa apenas faz capturas de tela
    'NAME': "test_frames",
    'TIME' : 0.4 
    # caso em modo automático de foco, tempo de exposição, devido ao tempo de calibração não utilizar tempos menor a 2 segundos
    # para os ajustes feitos manualmente, para um tempo menor que 0.2 segundo pode ser que não carregue todas as configurações realizadas no draft
}

DEBUG = True