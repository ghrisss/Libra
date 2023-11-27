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
import imutils
import numpy as np

from src.configs import SAVE
from src.controllers.files import FilesController
from src.tests.mark_identification_methods import (hole_number, shape_matching,
                                                   template_matching)

### chamar a imagem e defini-la em uma variável para ela
root_dir = Path(__file__).parent.parent.parent
original_image = cv2.imread(f"{root_dir}/\\created_files\\visit_frames\\visit_frames_1700244364874.png")
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
kernel = np.ones((7,7))
for j, line in enumerate(kernel):
    kernel[j] = np.negative(line)
kernel[7//2,7//2] = 60
kernel = kernel/(np.sum(kernel))
convoluted_image = cv2.filter2D(src=blurred_image, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(3,3))
# cv2.namedWindow('[4] convolution', cv2.WINDOW_NORMAL)
# cv2.imshow('[4] convolution', convoluted_image)
# cv2.imwrite('[4].jpeg', convoluted_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### limiarizar a imagem
thresh_image = cv2.threshold(convoluted_image, 80, 255, cv2.THRESH_BINARY)[1]
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
particles_contours = [contour for contour in img_contours if cv2.arcLength(contour, closed=True) <= 250]
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
# cv2.namedWindow('[12] aplicacao convex hull', cv2.WINDOW_NORMAL)
# cv2.imshow('[12] aplicacao convex hull', convex_hull_image)
# cv2.imwrite('[12].jpeg', convex_hull_image)
# cv2.waitKey()
# cv2.destroyAllWindows()



### é feito a máscara com a imagem original com a seção total circular
circles = cv2.HoughCircles(convex_hull_image, cv2.HOUGH_GRADIENT, 1, 150, param1 = 255,
               param2 = 15, minRadius = 250, maxRadius = 500)
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
# crop_filtered_roi = filtered_particles[center_coordinates[1]-radius-50:center_coordinates[1]+200,
#                                        center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]
crop_filtered_roi = filtered_particles[center_coordinates[1]-radius-50:center_coordinates[1]+radius+50,
                                       center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]
# cv2.imshow('[15] recorte da regiao de interesse', crop_filtered_roi)
# cv2.imwrite('[15].jpeg', crop_filtered_roi)
# cv2.waitKey()
# cv2.destroyAllWindows()



### (morfologia avançada) preenchimento de buracos, locais onde são localizadas as arruelas, atribuí-la a uma variável
fill_pad = cv2.copyMakeBorder(crop_filtered_roi, 1,1,1,1, cv2.BORDER_CONSTANT, value=0) # adiciona um pixel a mais em branco por toda a borda
# era utilizado anteriormente, quandoa  ideia era fazer a análise com metade do anel de curto apenas
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
particles_contours_2 = [cnts for cnts in img_contours_2 if cv2.boundingRect(cnts)[2] <= 50] # OBS: x, y, w, h = cv2.boundingRect(cnts)
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
rivet_circles = cv2.HoughCircles(fill_hole_2, cv2.HOUGH_GRADIENT, 1, 150, param1 = 70,
               param2 = 12, minRadius = 20, maxRadius = 50)



### nesta máscara é colocado uma delimitação/marcação nas posições dos rebites encontrados
masked_image = cv2.bitwise_and(original_image, original_image, mask=roi_mask)
# cv2.namedWindow('[22] imagem original com mascara aplicada', cv2.WINDOW_NORMAL)
# cv2.imshow("[22] imagem original com mascara aplicada", masked_image)
# roi_image = masked_image[center_coordinates[1]-radius-50:center_coordinates[1]+200, 
#                          center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]
roi_image = masked_image[center_coordinates[1]-radius-50:center_coordinates[1]+radius+50, 
                         center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]

 
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
        if SAVE:
            dir_name = 'rivet_post_visit'
            file_name = f'{dir_name}_{int(time() * 1000)}.png'
            cv2.imwrite(f'{file_name}', rivet_image)
            FilesController.transferFile(dir_name=dir_name, file_name=file_name)
        cv2.imshow("pontos de analise encontrados", rivet_image)

        '''-------------------------------------------------------------------------------------------------------------------------------------------------------------------'''

        metodo = 3

        match metodo:
            
            #! Template Matching
            case 1:
                method_result = template_matching.templateMatching(rivet_image)
                # template matching
                '''methods = [cv.TM_CCOEFF, cv.TM_CCOEFF_NORMED, cv.TM_CCORR,
                    cv.TM_CCORR_NORMED, cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]'''
                template_image = cv2.imread(f"{root_dir}/\\match_pictures\\template_match\\template_filtered.jpeg", cv2.IMREAD_UNCHANGED)
                # cv2.imshow("[30] imagem de template", template_image)
                
                template_width, template_heigth = template_image.shape[::-1]
                
                found = None
                for n, scale in enumerate(np.linspace(0.8, 1.2, 20)):
                    resized_image = imutils.resize(method_result, width = int(method_result.shape[1] * scale))
                    ratio = method_result.shape[1] / float(resized_image.shape[1])
                
                    if resized_image.shape[0] < template_heigth or resized_image.shape[1] < template_width:
                        break
                    
                    template_result = cv2.matchTemplate(resized_image, template_image, cv2.TM_CCORR_NORMED)
                    min_confidence_value, max_confidence_value, min_location, max_location = cv2.minMaxLoc(template_result)
                    print(f'best match confidence {n+1}: ', max_confidence_value)

                    confidence_threshold = 0.3
                    if found is None or max_confidence_value > found[0]:
                        found = (max_confidence_value, max_location, r)
                    cv2.imshow("[31]local de analise", resized_image)
                    cv2.waitKey()
                    cv2.destroyAllWindows()
                        
                max_confidence_value, max_location, r = found
                
                min_confidence_value, max_confidence_value, min_location, max_location = cv2.minMaxLoc(template_result)
                print('best match confidence: ', max_confidence_value)
                
                confidence_threshold = 0.3
                if max_confidence_value > confidence_threshold:
                    print(f'arruela {i+1} rebitada')
                    top_left = max_location
                    bottom_right = (top_left[0] + template_width, top_left[1] + template_heigth)
                    
                    cv2.rectangle(method_result, top_left, bottom_right, 0, 2)
                cv2.imshow("[31]local de analise", method_result)
                
                cv2.waitKey()
                cv2.destroyAllWindows()


            #! Shape Matching
            case 2:
                method_result = shape_matching.shapeMatching(rivet_image)
                # shape matching (espero que seja o template matching só que limiarizado)
                template_image = cv2.imread(f"{root_dir}/\\match_pictures\\shape_match\\pattern_template_2.jpeg", cv2.IMREAD_UNCHANGED)
                # match_mask = np.zeros(method_result.shape, np.uint8)
                # interest_width, interest_heigth = method_result.shape[::1]
                # mask_width = int(interest_width//2-template_width//2)
                # mask_heigth = int(interest_heigth//2-template_heigth//2)
                # match_mask[mask_heigth:mask_heigth+template_heigth, mask_width:mask_width+template_width] = template_image
                # template_image = match_mask
                template_width, template_heigth = template_image.shape[::-1]
                cv2.imshow("[39] imagem de template", template_image)
                template_contours, _ = cv2.findContours(template_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                template_contours = sorted(template_contours, key=cv2.contourArea, reverse=True)
                template_pattern = template_contours[0]
                
                for i, scale in enumerate(np.linspace(0.9, 1.1, 20)):
                    resized_image = imutils.resize(method_result, width = int(method_result.shape[1] * scale))
                    ratio = method_result.shape[1] / float(resized_image.shape[1])
                    if resized_image.shape[0] < template_heigth or resized_image.shape[1] < template_width:
                        break
                    analised_pattern_contours, _ = cv2.findContours(method_result, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
                    analised_pattern_contours = sorted(analised_pattern_contours, key=cv2.contourArea, reverse=True)
                    analised_pattern = analised_pattern_contours[0]
                    # cv2.drawContours(rivet_copy, analised_pattern, -1, (0, 255, 0), 3)
                    # cv2.imshow("[40] imagem do contorno", rivet_copy)
                    result = cv2.matchShapes(analised_pattern, template_image, 3, 0.0)
                    print(f'a diferença entre as imagens é de: {result}')
                
                match_threshold = 0.2
                print('o ponto está rebitado') if result > match_threshold else print('O ponto não está rebitado')

                cv2.waitKey()
                cv2.destroyAllWindows()


            #! Details Analysis
            case 3:                 
                method_result = hole_number.detailAnalysis(rivet_image)
                # análise dos buracos
                analised_pattern_contours, hierarchy_list = cv2.findContours(method_result, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                if hierarchy_list is not None:
                    hierarchy = hierarchy_list[0]
                    pattern_holes = len(hierarchy) - 1
                    if pattern_holes > 2:
                        print('O ponto está rebitado')
                        rivet_conference.get(f'{i}').append(True)
                    else:
                        print('O ponto não está rebitado')
                        rivet_conference.get(f'{i}').append(False)
                else:
                    print('O ponto não está rebitado')
                    rivet_conference.get(f'{i}').append(False)
                # cv2.imshow('[39] imagem filtrado apenas de rebites com marcação', only_mark_rivet)

### verificação/segmentação da arruela com base em sua cor
        segmentation_blur = cv2.medianBlur(rivet_image, 9)
        hsv_image = cv2.cvtColor(segmentation_blur, cv2.COLOR_BGR2HSV)
        # cv2.imshow("espaço de cores HSV", hsv_image)
        segmentation_mask = cv2.inRange(hsv_image, (18,52,108), (33, 255, 215))
        # if SAVE:
        #     dir_name = 'rivet_color_frames'
        #     file_name = f'{dir_name}_{int(time() * 1000)}.png'
        #     cv2.imwrite(f'{file_name}', segmentation_mask)
        #     FilesController.transferFile(dir_name=dir_name, file_name=file_name)
        # cv2.imshow('local de arruela', segmentation_mask)
        segmented_rivet = cv2.bitwise_and(rivet_image,rivet_image,mask=segmentation_mask)
        color_presence, hierarchy_list = cv2.findContours(segmentation_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        rivet_conference.get(f'{i}').append(True) if len(color_presence)>0 else rivet_conference.get(f'{i}').append(False)
        # cv2.imshow('arruela com sua mascara', segmented_rivet)

        cv2.waitKey()
        cv2.destroyAllWindows()
        
# TODO: esse dicionário vai conter na key o número do revite, e value uma lista com True e False para o caso de ter rebite e se tem arruelas, e será feita a conferenência aqui
print("situação dos rebites:\n", rivet_conference)

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