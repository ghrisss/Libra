import sys
import os
# Obtém o diretório raiz do projeto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print(root_dir)
# Adiciona o diretório raiz ao caminho de busca do Python
sys.path.append(root_dir)

import cv2
import numpy as np
from pathlib import Path

# chamar a imagem e defini-la em uma variável para ela
root_dir = Path(__file__).parent.parent.parent
original_image = cv2.imread(f"{root_dir}/\\created_files\\treated_frames\\treated_frames_1695727149213.jpeg")
original_image = cv2.pyrDown(original_image)
# cv2.imshow('original' ,original_image)


# transforma-la em tons de cinza
pb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
# cv2.imshow('PB' ,pb_image)


# aplicar um filtro gaussiano
blurred_image = cv2.GaussianBlur(pb_image, (7,7), 0)
# cv2.imshow('blur', blurred_image)


# aplicar um filtro de convolução - filtro passa alta (criar uma matriz com o numpy)
kernel = np.array([
    [-1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1],
    [-1, -1, 30, -1, -1],
    [-1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1],
    ])
kernel = kernel/(np.sum(kernel))

convoluted_image = cv2.filter2D(src=blurred_image, ddepth=0, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_REFLECT, anchor=(1,1))
# cv2.imshow('convolution', convoluted_image)


# limiarizar a imagem
thresh_image = cv2.threshold(convoluted_image, 70, 255, cv2.THRESH_BINARY)[1]
# cv2.imshow('thresholding', thresh_image)


# aplicar um filtro passa-baixa
kernel = np.array([
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    ])
kernel = kernel/(2*(np.sum(kernel)))

low_pass_image = cv2.filter2D(src=thresh_image, ddepth=-1, kernel=cv2.flip(kernel, -1), anchor=(1,1))
low_pass_image = cv2.threshold(low_pass_image, 70, 255, cv2.THRESH_BINARY)[1]
# cv2.imshow('low pass filtered', low_pass_image)


# (morfologia avançada) remover objetos das bordas da imagem
pad = cv2.copyMakeBorder(low_pass_image, 1,1,1,1, cv2.BORDER_CONSTANT, value=255) # adiciona um pixel de branco por toda a borda
# cv2.imshow('pad', pad)
pad_h, pad_w = pad.shape # pega as medidas e toda a borda

border_mask = np.zeros([pad_h+2, pad_w+2], np.uint8) # cria uma máscara de zeros (toda preta) 2 pixels maior em cada dimensão
# cv2.imshow('mask', border_mask)

floodfill_image = cv2.floodFill(pad, border_mask, (0,0), 0, (5), (0), flags=8)[1] # preenche toda a borda branca externa de preto
# cv2.imshow('primeiro floodfill', floodfill_image)
floodfill_image = floodfill_image[1:pad_h-1, 1:pad_w-1] # aqui é feito a imagem retornar ao seu tamanho original
# cv2.imshow('removed border objects', floodfill_image)


# filtro de partículas (pelo perímetro), definir uma variável para essa imagem



# retirar a seção total circular, atribuí-la a uma variável para criar a máscar na imagem original



# recorte da região de interesse da seção circular, defini-la em uma variável



# (morfologia avançada) preenchimento de buracos, locais onde são localizadas as arruelas, atribuí-la a uma variável



# operação de subtração entre a região de interesse da seção circular com a sua contraparte com os buracos preenchidos



# filtro de partículas (pelo comprimento do seu retângulo de delimitação)



# (morfologia avançada) preenchimento de possíveis buracos, por conta do estado do rebite na imagem



# detecção de círculos, nesse ponto, temos a posição do centro do círculo do rebite



# é feito a máscara com a imagem original com a seção total circular



# nesta máscara é colocado uma delimitação/marcação nas posições dos rebites encontrados




key = cv2.waitKey()
if key == ord('q'):
    cv2.destroyAllWindows()