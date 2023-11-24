import cv2
import numpy as np

from src.configs import SAVE
from src.controllers.files import FilesController

def shapeMatching(input_image):
    # grayscaling
    pb_rivet_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
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
    
    return rivet_pattern_shape