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

### chamar a imagem e defini-la em uma variável para ela
root_dir = Path(__file__).parent.parent.parent
original_image = cv2.imread(f"{root_dir}/\\created_files\\treated_frames\\treated_frames_1695727149213.jpeg")
# original_image = cv2.pyrDown(original_image)
# cv2.imshow('original' ,original_image)


### transforma-la em tons de cinza
pb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
# cv2.namedWindow('PB', cv2.WINDOW_NORMAL)
# cv2.imshow('PB' ,pb_image)


### aplicar um filtro gaussiano
blurred_image = cv2.GaussianBlur(pb_image, (7,7), 0)
# cv2.imshow('blur', blurred_image)


### aplicar um filtro de convolução - filtro passa alta (criar uma matriz com o numpy)
kernel = np.array([
    [-1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1],
    [-1, -1, 30, -1, -1],
    [-1, -1, -1, -1, -1],
    [-1, -1, -1, -1, -1],
    ])
kernel = kernel/(np.sum(kernel))

convoluted_image = cv2.filter2D(src=blurred_image, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_REFLECT, anchor=(1,1))
# cv2.namedWindow('convolution', cv2.WINDOW_NORMAL)
# cv2.imshow('convolution', convoluted_image)


### limiarizar a imagem
thresh_image = cv2.threshold(convoluted_image, 68, 255, cv2.THRESH_BINARY)[1]
# cv2.namedWindow('thresholding', cv2.WINDOW_NORMAL)
# cv2.imshow('thresholding', thresh_image)


### aplicar um filtro passa-baixa
low_pass_image = cv2.morphologyEx(src=thresh_image, op=cv2.MORPH_HITMISS , kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)), iterations=1)
# cv2.namedWindow('low pass', cv2.WINDOW_NORMAL)
# cv2.imshow('low pass', low_pass_image)
low_pass_image = cv2.threshold(low_pass_image, 136, 255, cv2.THRESH_BINARY)[1]
# cv2.namedWindow('low pass filtered', cv2.WINDOW_NORMAL)
# cv2.imshow('low pass filtered', low_pass_image)


### (morfologia avançada) remover objetos das bordas da imagem
pad = cv2.copyMakeBorder(low_pass_image, 1,1,1,1, cv2.BORDER_CONSTANT, value=255) # adiciona um pixel a mais em branco por toda a borda
# o pad é criado pois a função floodfill verifica um ponto selecionado e suas redondeza para preenche-lo com determinada cor, sendo o pixel na borda, 
# suas redondeza estariam fora da borda, por isso é adicionado pixels as redondezas da borda
pad_h, pad_w = pad.shape # pega as medidas e toda a borda
border_mask = np.zeros([pad_h+2, pad_w+2], np.uint8) # cria uma máscara de zeros (toda preta) 2 pixels maior em cada dimensão (exigencia para a função floodfill)

floodfill_image = cv2.floodFill(pad, border_mask, (0,0), 0, (5), (0), flags=8)[1] # preenche toda a borda branca externa de preto
floodfill_image = floodfill_image[1:pad_h-1, 1:pad_w-1] # aqui é feito a imagem retornar ao seu tamanho original
# cv2.namedWindow('removed border objects', cv2.WINDOW_NORMAL)
# cv2.imshow('removed border objects', floodfill_image)


### filtro de partículas (pelo perímetro), definir uma variável para essa imagem
img_contours, hierarchy = cv2.findContours(floodfill_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # retorna todos os contornos, comprime os pontos em linhas retas para apenas seus pontos extremos
print('contornos encontrados na imagem: ', len(img_contours))
# all_contours_img = original_image.copy()
# cv2.drawContours(all_contours_img, img_contours, -1, (0,255,0), 1)
# cv2.imshow('desenho contornos', all_contours_img)

particles_contours = [contour for contour in img_contours if cv2.arcLength(contour, closed=True) <= 600]
print('contornos de partículas na imagem', len(particles_contours))
# filtered_contours_img = original_image.copy()
# cv2.drawContours(filtered_contours_img, filtered_contours, -1, (0,255,0), -1)
# cv2.namedWindow('desenho de contornos de interesse', cv2.WINDOW_NORMAL)
# cv2.imshow('desenho de contornos de interesse', filtered_contours_img)

mask_holes = np.zeros(floodfill_image.shape, np.uint8)
mask_holes.fill(255)
[cv2.drawContours(mask_holes, [c], -1, (0, 0, 0), -1) for c in particles_contours]
# cv2.namedWindow('mascara', cv2.WINDOW_NORMAL)
# cv2.imshow('mascara', mask_holes)

filtered_particles = floodfill_image.copy()
filtered_particles[mask_holes==0]=0
# cv2.namedWindow('filtro de partículas', cv2.WINDOW_NORMAL)
# cv2.imshow('filtro de partículas', filtered_particles)


### retirar a seção total circular, atribuí-la a uma variável para criar a máscara na imagem original
cnts, _ = cv2.findContours(filtered_particles, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
convex_hull_image = filtered_particles.copy()
for c in cnts:
    convex_hull = cv2.convexHull(c)
    cv2.fillPoly(convex_hull_image, pts =[convex_hull], color=(255,255,255))
# cv2.namedWindow('aplicação convex hull', cv2.WINDOW_NORMAL)
# cv2.imshow('aplicação convex hull', convex_hull_image)

circles = cv2.HoughCircles(convex_hull_image, cv2.HOUGH_GRADIENT, 1, 150, param1 = 255,
               param2 = 10, minRadius = 500, maxRadius = 800)

if circles is not None:
    radius_list = [r for (a, b, r) in circles[0, :]] # cria um array com todos os raios dos circulos encontrados
    roi_radius = sorted(radius_list, reverse=True)[0] # organiza a lista de forma descrescente, e seleciona então o maior raio dentre os encontrados como o raio de interesse
    roi_circle_index = radius_list.index(roi_radius) # verifica qual o índice desse raio na lista, que consequentemente também é o mesmo índice na lista de círculos encontrados
    (a, b, r) = circles[0, :][roi_circle_index] # determina as coordenadas do círculo de maior raio, também sendo o círculo de maior interesse
    
    center_coordinates = (int(a), int(b))
    radius = int(r)
    print(center_coordinates, radius)
    img_h, img_w = original_image.shape[:2]
    mask = np.zeros((img_h, img_w), np.uint8)

    # # Draw the circumference of the circle.
    # cv2.circle(original_image, center_coordinates, radius, (0, 255, 0), 2)

    # # Draw a small circle (of radius 1) to show the center.
    # cv2.circle(original_image, center_coordinates, 1, (0, 0, 255), 3)
    # cv2.namedWindow('Detected Circle', cv2.WINDOW_NORMAL)
    # cv2.imshow("Detected Circle", original_image)
    
    roi_mask = cv2.circle(mask, center_coordinates, radius, (255,255,255), -1) # cria a máscara para recortar apenas a região de interesse
    # cv2.namedWindow('mascara roi', cv2.WINDOW_NORMAL)
    # cv2.imshow("mascara roi", roi_mask)
else:
    # TODO: fazer uma forma de fazer uma recursão que certamente identifique a seção circular de interesse, possivelmente fazendo a função HoughCircles com uma precisão menor
    pass
    


### recorte da região de interesse da seção circular, defini-la em uma variável
crop_filtered_roi = filtered_particles[center_coordinates[1]-radius:center_coordinates[1]+200, center_coordinates[0]-radius:center_coordinates[0]+radius]
# cv2.namedWindow('recorte da regiao de interesse', cv2.WINDOW_NORMAL)
cv2.imshow('recorte da regiao de interesse', crop_filtered_roi)


### (morfologia avançada) preenchimento de buracos, locais onde são localizadas as arruelas, atribuí-la a uma variável



### operação de subtração entre a região de interesse da seção circular com a sua contraparte com os buracos preenchidos



### filtro de partículas (pelo comprimento do seu retângulo de delimitação)



### (morfologia avançada) preenchimento de possíveis buracos, por conta do estado do rebite na imagem



### detecção de círculos, nesse ponto, temos a posição do centro do círculo do rebite



### é feito a máscara com a imagem original com a seção total circular



### nesta máscara é colocado uma delimitação/marcação nas posições dos rebites encontrados




key = cv2.waitKey()
if key == ord('q') or ord('Q'):
    cv2.destroyAllWindows()