
COLOR_CAM = {
    'PREVIEW_SIZE' : [800, 200],
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
    'WB_STEP': 200 # WHITE BALANCE
}

# TODO: criar um shelve para os dados de configuração da camera

# TODO: criar um dicionario 'FILES' com esse frame_name, mas também com o diretório root 
FRAME_NAME = "product_frames" # pra salvar as imagens, e nãoo precisar ficar alterando isso toda vez

DEBUG = True

TIME_MODE = {
    'CASE': False, # se verdadeiro, para a função de captura de imagem, configura se está ativo e o tempo em que a foto será tirada
    'TIME' : 5
}