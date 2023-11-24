import cv2
import numpy as np

def detailAnalysis(input_image):
    # grayscaling
    pb_rivet_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    rivet_copy = pb_rivet_image.copy()
    
    # Equalização a imagem
    rivet_equalized = cv2.equalizeHist(rivet_copy)
    # cv2.imshow("[25] local equalizado", rivet_equalized)

    # alteração de brilho e contraste
    brightness_value = 196
    brightness = int((brightness_value - 0) * (255 - (-255)) / (510 - 0) + (-255)) 
    contrast_value = 133
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
    kernel = np.ones((13,13))
    for j, line in enumerate(kernel):
        kernel[j] = np.negative(line)
    kernel[13//2,13//2] = 210
    kernel = kernel/(np.sum(kernel))
    convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(6,6))
    # cv2.imshow("[28] ponto de analise com filtro de aumento de detalhes", convoluted_rivet)
    
    
    # limiarização (pelas partes escuras)
    thresh_rivet = cv2.threshold(convoluted_rivet, 43, 255, cv2.THRESH_BINARY_INV)[1]
    # cv2.imshow("[29] ponto de analise com filtro limiarizado", thresh_rivet)
    

    # Auto Median
    morphology_kernel = np.ones((3,3), np.uint8)
    morphology_kernel[::morphology_kernel.shape[0]-1, ::morphology_kernel.shape[1]-1] = 0
    automedian_rivet = cv2.morphologyEx(thresh_rivet, cv2.MORPH_OPEN, morphology_kernel)
    # cv2.imshow("[30] ponto de análise após antigo filtro automedian", automedian_rivet)
    

    # remoção objetos das bordas
    rivet_pad = cv2.copyMakeBorder(automedian_rivet, 1,1,1,1, cv2.BORDER_CONSTANT, value=255) # adiciona um pixel a mais em branco por toda a borda
    rivet_pad_h, rivet_pad_w = rivet_pad.shape # pega as medidas e toda a borda
    rivet_border_mask = np.zeros([rivet_pad_h+2, rivet_pad_w+2], np.uint8) # cria uma máscara de zeros (toda preta) 2 pixels maior em cada dimensão (exigencia para a função floodfill)
    floodfill_rivet = cv2.floodFill(rivet_pad, rivet_border_mask, (0,0), 0, (5), (0), flags=8)[1] # preenche toda a borda branca externa de preto
    floodfill_rivet = floodfill_rivet[1:rivet_pad_h-1, 1:rivet_pad_w-1] # aqui é feito a imagem retornar ao seu tamanho original
    # cv2.imshow('[31] ponto de analise com objetos da borda removidos', floodfill_rivet)                
    
    
    # filtro de partículas [1] (pela area)
    number_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(floodfill_rivet, 4, cv2.CV_32S)
        
    details_particles_mask1 = np.zeros(floodfill_rivet.shape, np.uint8)
    details_particles_mask1.fill(255)
    
    for n_label in range(1, number_labels):
        area = stats[n_label, cv2.CC_STAT_AREA]
        if area <= 60:
            details_particles_mask1[labels == n_label] = 0
    
    # cv2.imshow('[32] mascara com particulas que não fazem parte do padrão de rebite', details_particles_mask1)
    rivet_pattern_shape1 = floodfill_rivet.copy()
    rivet_pattern_shape1[details_particles_mask1==0]=0
    # cv2.imshow('[33] imagem com particulas da região de interesse filtradas pela sua área', rivet_pattern_shape1)
    
    
    # fechamento morfológico
    kernel = np.ones((3,3), np.uint8)
    close_rivet = cv2.morphologyEx(rivet_pattern_shape1, cv2.MORPH_CLOSE, kernel)
    # agroup_rivet = cv2.morphologyEx(agroup_rivet, cv2.MORPH_OPEN, morphology_kernel)
    # abertura morfológico
    kernel[::kernel.shape[0]-1, ::kernel.shape[1]-1] = 0
    open_rivet = cv2.morphologyEx(close_rivet, cv2.MORPH_OPEN, kernel)
    # agroup_rivet = cv2.morphologyEx(agroup_rivet, cv2.MORPH_CLOSE, morphology_kernel)
    # cv2.imshow("[34] ponto de analise dos detalhes com filtros morfológicos", open_rivet)
    
    
    # filtro de partículas [2] (pela area)
    number_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(open_rivet, 4, cv2.CV_32S)
    
    details_particles_mask2 = np.zeros(open_rivet.shape, np.uint8)
    details_particles_mask2.fill(255)
    
    for n_label in range(1, number_labels):
        area = stats[n_label, cv2.CC_STAT_AREA]
        if area <= 160:
            details_particles_mask2[labels == n_label] = 0
    
    rivet_pattern_shape2 = open_rivet.copy()
    rivet_pattern_shape2[details_particles_mask2==0]=0
    # cv2.imshow('[35] imagem com particulas do rebite filtradas pela sua área', rivet_pattern_shape2)
    
    
    # fechamento morfológico
    kernel = np.ones((5,5), np.uint8)
    kernel[::kernel.shape[0]-1, ::kernel.shape[1]-1] = 0
    agroup_rivet = cv2.morphologyEx(rivet_pattern_shape2, cv2.MORPH_CLOSE, kernel)
    # agroup_rivet = cv2.morphologyEx(agroup_rivet, cv2.MORPH_OPEN, morphology_kernel)
    # cv2.imshow("[36] ponto de analise dos detalhes da marcacao padrão agrupados", agroup_rivet)
    
    
    # filtro de partículas [3] (pela area)                
    number_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(agroup_rivet, 4, cv2.CV_32S)

    details_particles_mask3 = np.zeros(agroup_rivet.shape, np.uint8)
    details_particles_mask3.fill(255)

    for n_label in range(1, number_labels):
        area = stats[n_label, cv2.CC_STAT_AREA]
        if area <= 400:
            details_particles_mask3[labels == n_label] = 0
        
    rivet_pattern_shape3 = agroup_rivet.copy()
    rivet_pattern_shape3[details_particles_mask3==0]=0
    # cv2.imshow('[37] imagem com particulas além do rebite filtradas pela sua área', rivet_pattern_shape3)
    
    
    # filtro de partículas [4] (número de buracos)
    # [next, previous, first child, parent] ordem dos dados da lista hierarquia dos contorno
    analised_pattern_contours, hierarchy_list = cv2.findContours(rivet_pattern_shape3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = hierarchy_list[0]
    
    external_contour = [h for h in range(len(hierarchy)) if hierarchy[h][-1] == -1]
    for cnt in external_contour:
        holes = [contour for contour in hierarchy if contour[-1]==cnt]
        if len(holes) <= 2:
            no_mark_mask = np.zeros(rivet_pattern_shape3.shape, np.uint8)
            no_mark_mask.fill(255)
            [cv2.drawContours(no_mark_mask, analised_pattern_contours, cnt, (0, 0, 0), -1)]
            if len(external_contour) == 1:
                rivet_cnt = hierarchy[cnt][2]
                [cv2.drawContours(no_mark_mask, analised_pattern_contours, rivet_cnt, (255, 255, 255), -1)]
                no_mark_mask = cv2.erode(no_mark_mask, np.ones((3,3), np.uint8))
            # cv2.imshow('[38] mascara filtro de buracos', no_mark_mask),
            only_mark_rivet = rivet_pattern_shape3.copy()
            only_mark_rivet[no_mark_mask==0]=0
        else:
            only_mark_rivet = rivet_pattern_shape3
            
    return only_mark_rivet