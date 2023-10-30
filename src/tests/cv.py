import os
import sys

# Obtém o diretório raiz do projeto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print(root_dir)
# Adiciona o diretório raiz ao caminho de busca do Python
sys.path.append(root_dir)

from pathlib import Path
from time import time

import cv2
import numpy as np

from src.configs import SAVE
from src.controllers.files import FilesController

### chamar a imagem e defini-la em uma variável para ela
root_dir = Path(__file__).parent.parent.parent
original_image = cv2.imread(f"{root_dir}/\\created_files\\treated_frames\\treated_frames_1695727149213.jpeg")
# cv2.namedWindow('[1] original', cv2.WINDOW_NORMAL)
# cv2.imshow('[1] original' ,original_image)
# cv2.imwrite('[1].jpeg', original_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### transforma-la em tons de cinza
pb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
# cv2.namedWindow('[2] PB', cv2.WINDOW_NORMAL)
# cv2.imshow('[2] PB' ,pb_image)
# cv2.imwrite('[2].jpeg' ,pb_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### aplicar um filtro gaussiano
blurred_image = cv2.GaussianBlur(pb_image, (7,7), 0)
# cv2.namedWindow('[3] blur', cv2.WINDOW_NORMAL)
# cv2.imshow('[3] blur', blurred_image)
# cv2.imwrite('[3].jpeg', blurred_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



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
# cv2.namedWindow('[4] convolution', cv2.WINDOW_NORMAL)
# cv2.imshow('[4] convolution', convoluted_image)
# cv2.imwrite('[4].jpeg', convoluted_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### limiarizar a imagem
thresh_image = cv2.threshold(convoluted_image, 65, 255, cv2.THRESH_BINARY)[1]
# cv2.namedWindow('[5] thresholding', cv2.WINDOW_NORMAL)
# cv2.imshow('[5] thresholding', thresh_image)
# cv2.imwrite('[5].jpeg', thresh_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### aplicar um filtro passa-baixa
low_pass_image = cv2.morphologyEx(src=thresh_image, op=cv2.MORPH_HITMISS , kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(5,5)), iterations=1)
# cv2.namedWindow('low pass', cv2.WINDOW_NORMAL)
# cv2.imshow('low pass', low_pass_image)
low_pass_image = cv2.threshold(low_pass_image, 136, 255, cv2.THRESH_BINARY)[1]
# cv2.namedWindow('[6] low pass filtered', cv2.WINDOW_NORMAL)
# cv2.imshow('[6] low pass filtered', low_pass_image)
# cv2.imwrite('[6].jpeg', low_pass_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### (morfologia avançada) remover objetos das bordas da imagem
pad = cv2.copyMakeBorder(low_pass_image, 1,1,1,1, cv2.BORDER_CONSTANT, value=255) # adiciona um pixel a mais em branco por toda a borda
# o pad é criado pois a função floodfill verifica um ponto selecionado e suas redondeza para preenche-lo com determinada cor, sendo o pixel na borda, 
# suas redondeza estariam fora da borda, por isso é adicionado pixels as redondezas da borda
pad_h, pad_w = pad.shape # pega as medidas e toda a borda
border_mask = np.zeros([pad_h+2, pad_w+2], np.uint8) # cria uma máscara de zeros (toda preta) 2 pixels maior em cada dimensão (exigencia para a função floodfill)

floodfill_image = cv2.floodFill(pad, border_mask, (0,0), 0, (5), (0), flags=8)[1] # preenche toda a borda branca externa de preto
floodfill_image = floodfill_image[1:pad_h-1, 1:pad_w-1] # aqui é feito a imagem retornar ao seu tamanho original
# cv2.namedWindow('[7] removed border objects', cv2.WINDOW_NORMAL)
# cv2.imshow('[7] removed border objects', floodfill_image)
# cv2.imwrite('[7].jpeg', floodfill_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### filtro de partículas (pelo perímetro), definir uma variável para essa imagem
img_contours, _ = cv2.findContours(floodfill_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE) # retorna todos os contornos, comprime os pontos em linhas retas para apenas seus pontos extremos
print('contornos encontrados na imagem: ', len(img_contours))
# all_contours_img = original_image.copy()
# cv2.drawContours(all_contours_img, img_contours, -1, (0,255,0), 1)
# cv2.namedWindow('[8] desenho de todos os contornos da imagem', cv2.WINDOW_NORMAL)
# cv2.imshow('[8] desenho de todos os contornos da imagem', all_contours_img)

particles_contours = [contour for contour in img_contours if cv2.arcLength(contour, closed=True) <= 750]
print('contornos de partículas na imagem', len(particles_contours))
# filtered_contours_img = original_image.copy()
# cv2.drawContours(filtered_contours_img, particles_contours, -1, (0,255,0), -1)
# cv2.namedWindow('[9] desenho de contornos de interesse', cv2.WINDOW_NORMAL)
# cv2.imshow('[9] desenho de contornos de interesse', filtered_contours_img)

mask_particles = np.zeros(floodfill_image.shape, np.uint8)
mask_particles.fill(255)
[cv2.drawContours(mask_particles, [cnts], -1, (0, 0, 0), -1) for cnts in particles_contours]
# cv2.namedWindow('[10] mascara com particulas filtradas [1]', cv2.WINDOW_NORMAL)
# cv2.imshow('[10] mascara com particulas filtradas [1]', mask_particles)

filtered_particles = floodfill_image.copy()
filtered_particles[mask_particles==0]=0
# cv2.namedWindow('[11] filtro de particulas [1]', cv2.WINDOW_NORMAL)
# cv2.imshow('[11] filtro de particulas [1]', filtered_particles)
# cv2.imwrite('[11].jpeg', filtered_particles)
# cv2.waitKey()
# cv2.destroyAllWindows()



### retirar a seção total circular, atribuí-la a uma variável para criar a máscara na imagem original
convex_contours, _ = cv2.findContours(filtered_particles, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
convex_hull_image = filtered_particles.copy()
for cnts in convex_contours:
    convex_hull = cv2.convexHull(cnts)
    cv2.fillPoly(convex_hull_image, pts =[convex_hull], color=(255,255,255))
# cv2.namedWindow('[12]aplicacao convex hull', cv2.WINDOW_NORMAL)
# cv2.imshow('[12] aplicacao convex hull', convex_hull_image)
# cv2.imwrite('[12].jpeg', convex_hull_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### é feito a máscara com a imagem original com a seção total circular
circles = cv2.HoughCircles(convex_hull_image, cv2.HOUGH_GRADIENT, 1, 150, param1 = 255,
               param2 = 10, minRadius = 500, maxRadius = 800)

if circles is not None:
    radius_list = [r for (a, b, r) in circles[0, :]] # cria um array com todos os raios dos circulos encontrados
    roi_radius = sorted(radius_list, reverse=True)[0] # organiza a lista de forma descrescente, e seleciona então o maior raio dentre os encontrados como o raio de interesse
    roi_circle_index = radius_list.index(roi_radius) # verifica qual o índice desse raio na lista, que consequentemente também é o mesmo índice na lista de círculos encontrados
    (a, b, r) = circles[0, :][roi_circle_index] # determina as coordenadas do círculo de maior raio, também sendo o círculo de maior interesse
    
    center_coordinates = (int(a), int(b))
    radius = int(r)
    img_h, img_w = original_image.shape[:2]
    mask = np.zeros((img_h, img_w), np.uint8)

    # # Draw the circumference and a small circle on the center of the circle.
    # cv2.circle(original_image, center_coordinates, radius, (0, 255, 0), 2)
    # cv2.circle(original_image, center_coordinates, 1, (0, 0, 255), 3)
    # cv2.namedWindow('[13] secao circular de interesse detectado', cv2.WINDOW_NORMAL)
    # cv2.imshow("[13] secao circular de interesse detectado", original_image)
    
    roi_mask = cv2.circle(mask, center_coordinates, radius, (255,255,255), -1) # cria a máscara para recortar apenas a região de interesse
    # cv2.namedWindow('[14] mascara com a regiao de interesse', cv2.WINDOW_NORMAL)
    # cv2.imshow("[14] mascara com a regiao de interesse", roi_mask)
    # cv2.imwrite("[14].jpeg", roi_mask)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
else:
    # TODO: fazer uma forma de fazer uma recursão que certamente identifique a seção circular de interesse, possivelmente fazendo a função HoughCircles com uma precisão menor
    pass



### recorte da região de interesse da seção circular, defini-la em uma variável
crop_filtered_roi = filtered_particles[center_coordinates[1]-radius-50:center_coordinates[1]+200,
                                       center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]

# crop_filtered_roi = filtered_particles[center_coordinates[1]-200:center_coordinates[1]+radius+200,
#                                        center_coordinates[0]-radius-200:center_coordinates[0]+radius+200]

# cv2.imshow('[15] recorte da regiao de interesse', crop_filtered_roi)
# cv2.imwrite('[15].jpeg', crop_filtered_roi)
# cv2.waitKey()
# cv2.destroyAllWindows()



### (morfologia avançada) preenchimento de buracos, locais onde são localizadas as arruelas, atribuí-la a uma variável
fill_pad = cv2.copyMakeBorder(crop_filtered_roi, 1,1,1,1, cv2.BORDER_CONSTANT, value=0) # adiciona um pixel a mais em branco por toda a borda
pad_h, pad_w = fill_pad.shape # pega as medidas e toda a borda
hole_mask = np.zeros((pad_h+2, pad_w+2), np.uint8)
 
floodfill_hole = cv2.floodFill(fill_pad, hole_mask, (0,0), 255)[1];
floodfill_hole = floodfill_hole[1:pad_h-1, 1:pad_w-1]
floodfill_hole_inv = cv2.bitwise_not(floodfill_hole)

fill_hole = crop_filtered_roi | floodfill_hole_inv
# cv2.imshow("[16] preenchimento de buracos [1]", fill_hole)
# cv2.imwrite("[16].jpeg", fill_hole)
# cv2.waitKey()
# cv2.destroyAllWindows()



### operação de subtração entre a região de interesse da seção circular com a sua contraparte com os buracos preenchidos
subtraction = cv2.bitwise_xor(crop_filtered_roi, fill_hole)
# cv2.imshow("[17] resultado da operação de subtração", subtraction)
# cv2.imwrite("[17].jpeg", subtraction)
# cv2.waitKey()
# cv2.destroyAllWindows()



### filtro de partículas (pelo comprimento do seu retângulo de delimitação)
img_contours_2, _ = cv2.findContours(subtraction, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

particles_contours_2 = [cnts for cnts in img_contours_2 if cv2.boundingRect(cnts)[2] <= 70] # OBS: x, y, w, h = cv2.boundingRect(cnts)
    
mask_particles_2 = np.zeros(subtraction.shape, np.uint8)
mask_particles_2.fill(255)
[cv2.drawContours(mask_particles_2, [cnts], -1, (0, 0, 0), -1) for cnts in particles_contours_2]
# cv2.imshow('[18] mascara com particulas filtradas [2]', mask_particles_2)

filtered_particles_2 = subtraction.copy()
filtered_particles_2[mask_particles_2==0]=0
# cv2.imshow('[19] filtro de particulas [2]', filtered_particles_2)
# cv2.imwrite('[19].jpeg', filtered_particles_2)
# cv2.waitKey()
# cv2.destroyAllWindows()



### (morfologia avançada) preenchimento de possíveis buracos, por conta do estado do rebite na imagem
closing_hole = cv2.morphologyEx(filtered_particles_2, cv2.MORPH_CLOSE, (3,3), iterations=2)
# cv2.imshow('[20] fechamento para preencher os buracos', closing_hole)

floodfill_hole_2 = closing_hole.copy()
h, w = filtered_particles_2.shape[:2]
mask = np.zeros((h+2, w+2), np.uint8)
 
cv2.floodFill(floodfill_hole_2, mask, (0,0), 255);
floodfill_hole_inv_2 = cv2.bitwise_not(floodfill_hole_2)
fill_hole_2 = closing_hole | floodfill_hole_inv_2
# cv2.imshow('[21] preenchimento de buracos [2]', fill_hole_2)
# cv2.imwrite('[21].jpeg', fill_hole_2)
# cv2.waitKey()
# cv2.destroyAllWindows()

# TODO: criar uma moldura de 50x50 em preto, com o restante do quadro branco, para previnir que circulos nas bordas que não podem ser detectados apareçam

### detecção de círculos, nesse ponto, temos a posição do centro do círculo do rebite
rivet_circles = cv2.HoughCircles(fill_hole_2, cv2.HOUGH_GRADIENT, 1, 250, param1 = 255,
               param2 = 12, minRadius = 20, maxRadius = 70)



### nesta máscara é colocado uma delimitação/marcação nas posições dos rebites encontrados
masked_image = cv2.bitwise_and(original_image, original_image, mask=roi_mask)
# cv2.namedWindow('[22] imagem original com mascara aplicada', cv2.WINDOW_NORMAL)
# cv2.imshow("[22] imagem original com mascara aplicada", masked_image)
roi_image = masked_image[center_coordinates[1]-radius-50:center_coordinates[1]+200, 
                         center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]

# roi_image = masked_image[center_coordinates[1]-200:center_coordinates[1]+radius+200,
#                                        center_coordinates[0]-radius-200:center_coordinates[0]+radius+200]
 
if rivet_circles is not None:
    
    rivet_conference = {}
    
    drawing_image = roi_image.copy()
    for (a, b, r) in rivet_circles[0, :]:
        rivet_center_coordinates = (int(a), int(b))
        rivet_radius = int(r)
        cv2.circle(drawing_image, rivet_center_coordinates, rivet_radius, (0, 255, 0), 2)
        cv2.circle(drawing_image, rivet_center_coordinates, 1, (0, 0, 255), 3)
    # cv2.imshow("[23] imagem com mascara na regiao de interesse e desenho nos pontos de interesse", drawing_image)
    # cv2.imwrite("[23].jpeg", drawing_image)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    
    for i, (a, b, r) in enumerate(rivet_circles[0, :]):
        rivet_conference[f'{i}'] = []
        rivet_center_coordinates = (int(a), int(b))
        rivet_radius = int(r)
        # print(f'coordenadas centro do rebite {i+1}', rivet_center_coordinates)
        # print(f'raio do círculo do rebite {i+1}', rivet_radius)
        rivet_image = roi_image[rivet_center_coordinates[1]-rivet_radius-45:rivet_center_coordinates[1]+rivet_radius+45, 
                                rivet_center_coordinates[0]-rivet_radius-45:rivet_center_coordinates[0]+rivet_radius+45]
        # if SAVE:
        #     dir_name = 'template_frames'
        #     file_name = f'{dir_name}_{int(time() * 1000)}.jpeg'
        #     cv2.imwrite(f'{file_name}', rivet_image)
        #     FilesController.transferFile(dir_name=dir_name, file_name=file_name)
        # cv2.imshow("pontos de analise encontrados", rivet_image)

        '''-------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

        metodo = 2

        match metodo:
            
            #! Template Matching
            case 1:
                # grayscaling
                pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
                rivet_copy = pb_rivet_image.copy()
                
                # Equalização a imagem
                rivet_equalized = cv2.equalizeHist(rivet_copy)
                # cv2.imshow("[25] local equalizado", rivet_equalized)

                # alteração de brilho e contraste
                brightness_value = 191
                brightness = int((brightness_value - 0) * (255 - (-255)) / (510 - 0) + (-255)) 
                contrast_value = 132
                contrast = int((contrast_value - 0) * (127 - (-127)) / (254 - 0) + (-127)) 
                
                # brilho
                if brightness > 0: 
                    shadow = brightness 
                    max = 255
                else: 
                    shadow = 0
                    max = 255 + brightness 
                
                alpha_brightness = (max - shadow) / 255
                gamma_brightness = shadow
                cal = cv2.addWeighted(rivet_equalized, alpha_brightness,  
                                      rivet_equalized, 0, gamma_brightness)
                # contraste
                alpha_contrast = float(131 * (contrast + 127)) / (127 * (131 - contrast)) 
                gamma_contrast = 127 * (1 - alpha_contrast) 
                cal = cv2.addWeighted(cal, alpha_contrast,  
                                      cal, 0, gamma_contrast) 
                # gamma
                invGamma = 0.53
                lookUpTable = table = np.array([((j / 255.0) ** invGamma) * 255
                    for j in np.arange(0, 256)]).astype("uint8")
                bcg_image = cv2.LUT(cal, lookUpTable)
                # cv2.imshow("[26] imagem com ajuste bcg", bcg_image)
                
                # filtro com mediana de borramento 1
                median_rivet = cv2.medianBlur(bcg_image, 3)
                # cv2.imshow("[27] ponto de analise com filtro de mediana para borramento", median_rivet)
                
                # filtro de convolução
                kernel = np.ones((21,21))
                for j, line in enumerate(kernel):
                    kernel[j] = np.negative(line)
                kernel[21//2,21//2] = 550
                kernel = kernel/(np.sum(kernel))

                convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(10,10))
                # cv2.imshow("[28] ponto de analise com filtro de aumento de detalhes", convoluted_rivet)
                
                # filtro de borramento gaussiano 2
                blurred_rivet = cv2.GaussianBlur(convoluted_rivet, (3,3), 0)
                # if SAVE:
                #     dir_name = 'comparision_template_frames'
                #     file_name = f'{dir_name}_{int(time() * 1000)}.jpeg'
                #     cv2.imwrite(f'{file_name}', blurred_rivet)
                #     FilesController.transferFile(dir_name=dir_name, file_name=file_name)
                # cv2.imshow("[29] ponto de analise com borramento gaussiano", blurred_rivet)
                
                
                # template matching
                '''methods = [cv.TM_CCOEFF, cv.TM_CCOEFF_NORMED, cv.TM_CCORR,
                    cv.TM_CCORR_NORMED, cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]'''
                template_image = cv2.imread(f"{root_dir}/\\match_pictures\\template_match\\template_filtered.jpeg", cv2.IMREAD_UNCHANGED)
                # cv2.imshow("[30] imagem de template", template_image)
                
                template_width, template_heigth = template_image.shape[::-1]
                template_result = cv2.matchTemplate(blurred_rivet, template_image, cv2.TM_CCOEFF_NORMED)
                
                min_confidence_value, max_confidence_value, min_location, max_location = cv2.minMaxLoc(template_result)
                print('best match confidence: ', max_confidence_value)
                
                confidence_threshold = 0.2
                if max_confidence_value > confidence_threshold:
                    print(f'arruela {i+1} rebitada')
                    top_left = max_location
                    bottom_right = (top_left[0] + template_width, top_left[1] + template_heigth)
                    
                    cv2.rectangle(blurred_rivet, top_left, bottom_right, 0, 2)
                cv2.imshow("[31]local de analise", blurred_rivet)
                
                cv2.waitKey()
                cv2.destroyAllWindows()


            #! Shape Matching
            case 2:
                # grayscaling
                pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
                rivet_copy = pb_rivet_image.copy()
                
                # Equalização a imagem
                rivet_equalized = cv2.equalizeHist(rivet_copy)
                # cv2.imshow("[25] local equalizado", rivet_equalized)

                # alteração de brilho e contraste
                brightness_value = 146
                brightness = int((brightness_value - 0) * (255 - (-255)) / (510 - 0) + (-255)) 
                contrast_value = 132
                contrast = int((contrast_value - 0) * (127 - (-127)) / (254 - 0) + (-127)) 
                
                # brilho
                if brightness > 0: 
                    shadow = brightness 
                    max = 255
                else: 
                    shadow = 0
                    max = 255 + brightness 
                alpha_brightness = (max - shadow) / 255
                gamma_brightness = shadow
                cal = cv2.addWeighted(rivet_equalized, alpha_brightness,  
                                      rivet_equalized, 0, gamma_brightness)
                # contraste
                alpha_contrast = float(131 * (contrast + 127)) / (127 * (131 - contrast)) 
                gamma_contrast = 127 * (1 - alpha_contrast) 
                cal = cv2.addWeighted(cal, alpha_contrast,  
                                      cal, 0, gamma_contrast) 
                # gamma
                invGamma = 0.58
                lookUpTable = table = np.array([((j / 255.0) ** invGamma) * 255
                    for j in np.arange(0, 256)]).astype("uint8")
                bcg_image = cv2.LUT(cal, lookUpTable)
                # cv2.imshow("[26] imagem com ajuste bcg", bcg_image)
                
                
                # filtro com mediana de borramento 1
                median_rivet = cv2.medianBlur(bcg_image, 3)
                # cv2.imshow("[27] ponto de analise com filtro de mediana para borramento", median_rivet)
                
                
                # filtro de convolução
                kernel = np.ones((25,25))
                for j, line in enumerate(kernel):
                    kernel[j] = np.negative(line)
                kernel[25//2,25//2] = 780
                kernel = kernel/(np.sum(kernel))
                convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(12,12))
                # cv2.imshow("[28] ponto de analise com filtro de aumento de detalhes", convoluted_rivet)
                
                
                # filtro de borramento gaussiano 2
                blurred_rivet = cv2.GaussianBlur(convoluted_rivet, (3,3), 0)
                # cv2.imshow("[29] ponto de analise com filtro gaussiano", blurred_rivet)
                
                
                # limiarização
                thresh_rivet = cv2.threshold(blurred_rivet, 76, 255, cv2.THRESH_BINARY)[1]
                # cv2.imshow("[30] ponto de analise limiarizado", thresh_rivet)
                
                
                # abertura morfológica
                morphology_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
                opened_rivet = cv2.morphologyEx(thresh_rivet, cv2.MORPH_OPEN, morphology_kernel)
                # cv2.imshow("[31] ponto de analise com abertura morfologica", opened_rivet)


                # remoção de objetos das bordas
                rivet_pad = cv2.copyMakeBorder(opened_rivet, 1,1,1,1, cv2.BORDER_CONSTANT, value=255) # adiciona um pixel a mais em branco por toda a borda
                rivet_pad_h, rivet_pad_w = rivet_pad.shape # pega as medidas e toda a borda
                rivet_border_mask = np.zeros([rivet_pad_h+2, rivet_pad_w+2], np.uint8) # cria uma máscara de zeros (toda preta) 2 pixels maior em cada dimensão (exigencia para a função floodfill)
                floodfill_rivet = cv2.floodFill(rivet_pad, rivet_border_mask, (0,0), 0, (5), (0), flags=8)[1] # preenche toda a borda branca externa de preto
                floodfill_rivet = floodfill_rivet[1:rivet_pad_h-1, 1:rivet_pad_w-1] # aqui é feito a imagem retornar ao seu tamanho original
                # cv2.imshow('[32] ponto de analise com objetos da borda removidos', floodfill_rivet)
                
                
                # fechamento morfológico
                closed_rivet = cv2.morphologyEx(floodfill_rivet, cv2.MORPH_CLOSE, morphology_kernel)
                # cv2.imshow("[33] ponto de analise com fechamento morfologico", closed_rivet)
                
                
                # filtro de partículas [1] (pela área mínima)
                rivet_min_countours = cv2.findContours(closed_rivet, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
                rivet_min_particles_contours = [contour for contour in rivet_min_countours if cv2.contourArea(contour) <= 20]
                    # print('contornos encontrados na imagem: ', len(rivet_min_countours))
                    # print('contornos de partículas na imagem', len(rivet_min_particles_contours))
                rivet_mask_particles = np.zeros(closed_rivet.shape, np.uint8)
                rivet_mask_particles.fill(255)
                [cv2.drawContours(rivet_mask_particles, [cnts], -1, (0, 0, 0), -1) for cnts in rivet_min_particles_contours]


                # filtro de partículas [2] (pela área máxima)
                # [next, previous, first child, parent] ordem dos dados da lista hierarquia dos contorno
                rivet_max_countours, hierarchy_list= cv2.findContours(closed_rivet, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                hierarchy = hierarchy_list[0]
                union_contours = zip(rivet_max_countours, hierarchy)

                for i, particles_contour in enumerate(union_contours):
                    if cv2.contourArea(particles_contour[0]) >= 1900:
                        cv2.drawContours(rivet_mask_particles, [particles_contour[0]], -1, (0, 0, 0), -1)
                        if particles_contour[1][2] > 0:
                            for child_contour in union_contours:
                                if child_contour[1][3]==i:
                                    cv2.drawContours(rivet_mask_particles, [child_contour[0]], -1, (255, 255, 255), -1)
                                    cv2.drawContours(rivet_mask_particles, [child_contour[0]], -1, (0, 0, 0), 1)

                # cv2.imshow('[34] imagem com particulas do rebite filtradas pela sua área', rivet_mask_particles)

                
                # exclusão das partículas filtradas pela área
                rivet_filtered_particles = closed_rivet.copy()
                rivet_filtered_particles[rivet_mask_particles==0]=0
                # cv2.imshow('[35] filtro de particulas do rebite', rivet_filtered_particles)
                
                
                # fechamento morfológico
                array_1 = np.array([0, 0, 1, 1, 1, 0, 0])
                array_2 = np.array([0, 1, 1, 1, 1, 1, 0])
                array_3 = np.array([1, 1, 1, 1, 1, 1, 1])
                kernel = np.matrix([array_1, array_2, array_3, array_3, array_3, array_2, array_1], np.uint8)
                
                agroup_rivet = cv2.morphologyEx(rivet_filtered_particles, cv2.MORPH_CLOSE, kernel)
                # cv2.imshow("[36] ponto de analise da marca padrão agrupados", agroup_rivet)
                
                
                # filtro partículas [3] (pela área mínima)
                rivet_pattern_contours = cv2.findContours(agroup_rivet, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
                non_pattern_countours = [contour for contour in rivet_pattern_contours if cv2.contourArea(contour) <= 120]
                    
                non_pattern_mask = np.zeros(agroup_rivet.shape, np.uint8)
                non_pattern_mask.fill(255)
                [cv2.drawContours(non_pattern_mask, [cnts], -1, (0, 0, 0), -1) for cnts in non_pattern_countours]
                # cv2.imshow('[37] mascara com particulas que não fazem parte do padrão de rebite', non_pattern_mask)
                rivet_pattern_shape = agroup_rivet.copy()
                rivet_pattern_shape[non_pattern_mask==0]=0
                cv2.imshow('[38] filtro de detalhes não pertencentes ao padrão de rebite', rivet_pattern_shape)
                # cv2.imwrite('pattern_template_3.jpeg', rivet_pattern_shape[64:131, 61:127])
                
                # shape matching (espero que seja o template matching só que limiarizado)
                template_image = cv2.imread(f"{root_dir}/\\match_pictures\\shape_match\\pattern_template_2.jpeg", cv2.IMREAD_UNCHANGED)
                # template_image = cv2.bitwise_not(template_image)
                cv2.imshow("[39] imagem de template", template_image)
                template_contours, _ = cv2.findContours(template_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                template_contours = sorted(template_contours, key=cv2.contourArea, reverse=True)
                template_pattern = template_contours[0]
                # print(template_pattern)
                # print(cv2.contourArea(template_pattern))
                
                # rivet_pattern_shape = cv2.bitwise_not(rivet_pattern_shape)
                analised_pattern_contours, _ = cv2.findContours(rivet_pattern_shape, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                analised_pattern_contours = sorted(analised_pattern_contours, key=cv2.contourArea, reverse=True)
                analised_pattern = analised_pattern_contours[0]
                # print(analised_pattern)
                # print(cv2.contourArea(analised_pattern))
                result = cv2.matchShapes(analised_pattern, template_image, 1, 0.0)
                
                print(f'a diferença entre as imagens é de: {result}')
                
                # match_threshold = 0.2
                # print('o ponto está rebitado') if result > match_threshold else print('O ponto não está rebitado')
                
                cv2.waitKey()
                cv2.destroyAllWindows()


            #! Details Analysis
            case 3:
                # grayscaling
                pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
                rivet_copy = pb_rivet_image.copy()
                
                # Equalização a imagem
                rivet_equalized = cv2.equalizeHist(rivet_copy)
                # cv2.imshow("[25] local equalizado", rivet_equalized)

                # alteração de brilho e contraste
                brightness_value = 220
                brightness = int((brightness_value - 0) * (255 - (-255)) / (510 - 0) + (-255)) 
                contrast_value = 132
                contrast = int((contrast_value - 0) * (127 - (-127)) / (254 - 0) + (-127)) 
                
                # brilho
                if brightness > 0: 
                    shadow = brightness 
                    max = 255
                else: 
                    shadow = 0
                    max = 255 + brightness 
                
                alpha_brightness = (max - shadow) / 255
                gamma_brightness = shadow
                cal = cv2.addWeighted(rivet_equalized, alpha_brightness,  
                                    rivet_equalized, 0, gamma_brightness)
                # contraste
                alpha_contrast = float(131 * (contrast + 127)) / (127 * (131 - contrast)) 
                gamma_contrast = 127 * (1 - alpha_contrast) 
                cal = cv2.addWeighted(cal, alpha_contrast,  
                                    cal, 0, gamma_contrast) 
                # gamma
                invGamma = 0.65
                lookUpTable = table = np.array([((j / 255.0) ** invGamma) * 255
                    for j in np.arange(0, 256)]).astype("uint8")
                bcg_image = cv2.LUT(cal, lookUpTable)
                # cv2.imshow("[26] imagem com ajuste bcg", bcg_image)
                
                # filtro com mediana de borramento 1
                median_rivet = cv2.medianBlur(bcg_image, 3)
                # cv2.imshow("[27] ponto de analise com filtro de mediana para borramento", median_rivet)
                
                # filtro de convolução
                kernel = np.ones((17,17))
                for j, line in enumerate(kernel):
                    kernel[j] = np.negative(line)
                kernel[17//2,17//2] = 360
                kernel = kernel/(np.sum(kernel))
                convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(8,8))
                # cv2.imshow("[28] ponto de analise com filtro de aumento de detalhes", convoluted_rivet)
                
                
                # limiarização (pelas partes escuras)
                thresh_rivet = cv2.threshold(convoluted_rivet, 45, 255, cv2.THRESH_BINARY_INV)[1]
                # cv2.imshow("[29] ponto de analise com filtro limiarizado", thresh_rivet)
                
                
                # remoção objetos das bordas
                rivet_pad = cv2.copyMakeBorder(thresh_rivet, 1,1,1,1, cv2.BORDER_CONSTANT, value=255) # adiciona um pixel a mais em branco por toda a borda
                rivet_pad_h, rivet_pad_w = rivet_pad.shape # pega as medidas e toda a borda
                rivet_border_mask = np.zeros([rivet_pad_h+2, rivet_pad_w+2], np.uint8) # cria uma máscara de zeros (toda preta) 2 pixels maior em cada dimensão (exigencia para a função floodfill)
                floodfill_rivet = cv2.floodFill(rivet_pad, rivet_border_mask, (0,0), 0, (5), (0), flags=8)[1] # preenche toda a borda branca externa de preto
                floodfill_rivet = floodfill_rivet[1:rivet_pad_h-1, 1:rivet_pad_w-1] # aqui é feito a imagem retornar ao seu tamanho original
                # cv2.imshow('[30] ponto de analise com objetos da borda removidos', floodfill_rivet)
                
                
                # Auto Median
                morphology_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
                automedian_rivet = cv2.morphologyEx(floodfill_rivet, cv2.MORPH_OPEN, morphology_kernel)
                automedian_rivet = cv2.morphologyEx(automedian_rivet, cv2.MORPH_CLOSE, morphology_kernel)
                automedian_rivet = cv2.morphologyEx(automedian_rivet, cv2.MORPH_OPEN, morphology_kernel)
                # cv2.imshow("[31] ponto de análise após filtro automedian", automedian_rivet)
                
                
                # filtro de partículas [1] (pela area)
                rivet_details_contours = cv2.findContours(automedian_rivet, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
                particles_contour = [contour for contour in rivet_details_contours if cv2.contourArea(contour) <= 900]
                    
                details_particles_mask = np.zeros(automedian_rivet.shape, np.uint8)
                details_particles_mask.fill(255)
                [cv2.drawContours(details_particles_mask, [cnts], -1, (0, 0, 0), -1) for cnts in particles_contour]
                # cv2.imshow('[32] mascara com particulas que não fazem parte do padrão de rebite', non_pattern_mask)
                rivet_pattern_shape = automedian_rivet.copy()
                rivet_pattern_shape[details_particles_mask==0]=0
                # cv2.imshow('[33] imagem com particulas do rebite filtradas pela sua área', rivet_pattern_shape)
                
                
                # fechamento morfológico
                kernel = np.ones((7,7), np.uint8)
                kernel[::kernel.shape[0]-1, ::kernel.shape[1]-1] = 0
                agroup_rivet = cv2.morphologyEx(rivet_pattern_shape, cv2.MORPH_CLOSE, kernel)
                # agroup_rivet = cv2.morphologyEx(agroup_rivet, cv2.MORPH_OPEN, morphology_kernel)
                cv2.imshow("[34] ponto de analise dos detalhes da marcacao padrão agrupados", agroup_rivet)
                
                
                # filtro de partículas [2] (número de buracos)
                # [next, previous, first child, parent] ordem dos dados da lista hierarquia dos contorno
                analised_pattern_contours, hierarchy_list = cv2.findContours(agroup_rivet, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                hierarchy = hierarchy_list[0]
                if hierarchy[0][0] == -1:
                    pattern_holes = len(hierarchy) - 1
                    print('o ponto está rebitado') if pattern_holes > 2 else print('O ponto não está rebitado')
                else:
                    external_contour = [h for h in range(len(hierarchy)) if hierarchy[h][-1] == -1]
                    holes_in_pattern = []
                    for cnt in external_contour:
                        holes = [contour for contour in hierarchy if contour[-1]==cnt]
                        if len(holes) > len(holes_in_pattern):
                            holes_in_pattern = holes.copy()
                    print('o ponto está rebitado') if len(holes_in_pattern) > 2 else print('O ponto não está rebitado')

                cv2.waitKey()
                cv2.destroyAllWindows()

### verificação/segmentação da arruela com base em sua cor
        segmentation_blur = cv2.medianBlur(rivet_image, 9)
        hsv_image = cv2.cvtColor(segmentation_blur, cv2.COLOR_BGR2HSV)
        # cv2.imshow("espaço de cores HSV", hsv_image)
        segmentation_mask = cv2.inRange(hsv_image, (0,55,100), (50, 255, 255))
        if SAVE:
            dir_name = 'rivet_color_frames'
            file_name = f'{dir_name}_{int(time() * 1000)}.jpeg'
            cv2.imwrite(f'{file_name}', segmentation_mask)
            FilesController.transferFile(dir_name=dir_name, file_name=file_name)
        # cv2.imshow('local de arruela', segmentation_mask)
        segmented_rivet = cv2.bitwise_and(rivet_image,rivet_image,mask=segmentation_mask)
        # cv2.imshow('arruela com sua mascara', segmented_rivet)

# TODO: esse dicionário vai conter na key o número do revite, e value uma lista com True e False para o caso de ter rebite e se tem arruelas, e será feita a conferenência aqui
print("situação dos rebites: \n", rivet_conference)

key = cv2.waitKey()
if key == ord('q') or ord('Q'):
    cv2.destroyAllWindows()




### retirada de reflexos da arruelas
        # lower_limit = (150,150,150)
        # upper_limit = (240,240,240)
        # reflection_thresh = cv2.inRange(rivet_image, lower_limit, upper_limit)

        # close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3,3))
        # close_morph = cv2.morphologyEx(reflection_thresh, cv2.MORPH_CLOSE, close_kernel, iterations=1)
        # dilate_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
        # refection_mask = cv2.morphologyEx(close_morph, cv2.MORPH_DILATE, dilate_kernel, iterations=1)

        # rivet_image = cv2.inpaint(rivet_image, refection_mask, 1, cv2.INPAINT_NS) # non_reflective

        # # cv2.imshow("[24] local de analise sem reflexos", rivet_image)