import cv2
import numpy as np


class VisionController():
    
    def HighlightDetails(input_image, size = 3, center = 10):
        kernel = np.ones((size,size))
        for j, line in enumerate(kernel):
            kernel[j] = np.negative(line)
        kernel[size//2,size//2] = center
        kernel = kernel/(np.sum(kernel))
        convoluted_image = cv2.filter2D(src=input_image, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=((size-1)//2,(size-1)//2))
        
        return convoluted_image
    
    
    def removeBorderObjects(input_image):
        pad = cv2.copyMakeBorder(input_image, 1,1,1,1, cv2.BORDER_CONSTANT, value=255)
        pad_h, pad_w = pad.shape
        border_mask = np.zeros([pad_h+2, pad_w+2], np.uint8)
        floodfill_image = cv2.floodFill(pad, border_mask, (0,0), 0, (5), (0), flags=8)[1]
        floodfill_image = floodfill_image[1:pad_h-1, 1:pad_w-1]
        
        return floodfill_image
    
    
    def perimeterParticleFilter(input_image, maximum_particle):
        # verificar como fazer o filtro de perimetro com connected components também
        img_contours, _ = cv2.findContours(input_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        particles_contours = [contour for contour in img_contours if cv2.arcLength(contour, closed=True) <= maximum_particle]
        
        particles_mask = np.zeros(input_image.shape, np.uint8)
        particles_mask.fill(255)
        [cv2.drawContours(particles_mask, [cnts], -1, (0, 0, 0), -1) for cnts in particles_contours]
        particle_filtered_image = input_image.copy()
        particle_filtered_image[particles_mask==0]=0
        
        return particle_filtered_image
    
    
    def areaParticleFilter(input_image, remove = True,  minimum_particle = 0,  maximum_particle = 0):
        labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(input_image, 4, cv2.CV_32S)

        particles_mask = np.zeros(input_image.shape, np.uint8)
        if remove == True:
            particles_mask.fill(255)
        
        for foreground_object in range(1, labels_count): # aqui exclui-se o fundo(background) que é sempre contabilizado como uma label
            area = stats[foreground_object, cv2.CC_STAT_AREA]
            if minimum_particle < area < maximum_particle:
                if remove == True:
                    particles_mask[labels == foreground_object] = 0
                else:
                    particles_mask[labels == foreground_object] = 255

        if remove == True:
            particle_filtered_image = input_image.copy()
            particle_filtered_image[particles_mask==0]=0
        else:
            particle_filtered_image = particles_mask
        
        return particle_filtered_image
    
    
    def boundingRectWidthFilter(input_image, remove = True, minimum_value = 0, maximum_value = 0):
        labels_count, labels, stats, centroids = cv2.connectedComponentsWithStats(input_image, 4, cv2.CV_32S)
        
        particles_mask = np.zeros(input_image.shape, np.uint8)
        if remove == True:
            particles_mask.fill(255)
        
        for foreground_object in range(1, labels_count):
            width = stats[foreground_object, cv2.CC_STAT_WIDTH]
            if minimum_value < width < maximum_value:
                if remove == True:
                    particles_mask[labels == foreground_object] = 0
                else:
                    particles_mask[labels == foreground_object] = 255
        
        if remove == True:
            particle_filtered_image = input_image.copy()
            particle_filtered_image[particles_mask==0]=0
        else:
            particle_filtered_image = particles_mask
        
        return particle_filtered_image
    
    
    def convexHull(input_image):
        convex_contours, _ = cv2.findContours(input_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        convex_hull_image = input_image.copy()
        for cnts in convex_contours:
            convex_hull = cv2.convexHull(cnts)
            cv2.fillPoly(convex_hull_image, pts =[convex_hull], color=(255,255,255))
            
        return convex_hull_image
    
    
    def crop_ring(input_image, original_image):
        circles_roi = cv2.HoughCircles(input_image, cv2.HOUGH_GRADIENT, 1, 1000, param1 = 255,
               param2 = 23, minRadius = 500, maxRadius = 700)
        if circles_roi is not None:
            image_center =  (original_image.shape[1]/2, original_image.shape[0]/2)
            image_center = np.array(image_center)
            
            radius_list = [r for (a, b, r) in circles_roi[0, :]] # cria um array com todos os raios dos circulos encontrados
            circles_center_list = [(a,b) for (a, b, r) in circles_roi[0, :]]
            nearest_to_center = min(circles_center_list, key = lambda c: np.linalg.norm(c - image_center))
            roi_circle_index = circles_center_list.index(nearest_to_center) # verifica qual o índice do circulo na lista está mais ao centro da imagem
            (a, b, r) = circles_roi[0, :][roi_circle_index] # determina as coordenadas do círculo ,mais ao centro da imagem, também sendo o círculo de maior interesse
            
            center_coordinates = (int(a), int(b))
            radius = int(r)
            
            img_h, img_w = input_image.shape[:2]
            mask = np.zeros((img_h, img_w), np.uint8)
            roi_mask = cv2.circle(mask, center_coordinates, radius, (255,255,255), -1)
            masked_image = cv2.bitwise_and(original_image, original_image, mask=roi_mask)
            roi_mask_image = masked_image[center_coordinates[1]-radius-50:center_coordinates[1]+radius+50, 
                         center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]
            
            roi_image = original_image[center_coordinates[1]-radius-50:center_coordinates[1]+radius+50, 
                         center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]
        else:
            print('ERRO DE OPERAÇÃO: anel de curto não encontrado')
            roi_image = None
            roi_mask_image = None
            
        return roi_image, roi_mask_image
    
    
    def fill_holes(input_image):
        fill_pad = cv2.copyMakeBorder(input_image, 1,1,1,1, cv2.BORDER_CONSTANT, value=0) # adiciona um pixel a mais em branco por toda a borda
        pad_h, pad_w = fill_pad.shape # pega as medidas de toda a borda
        mask = np.zeros((pad_h+2, pad_w+2), np.uint8)
        
        floodfill_hole = cv2.floodFill(fill_pad, mask, (0,0), 255)[1];
        floodfill_hole = floodfill_hole[1:pad_h-1, 1:pad_w-1]
        floodfill_hole_inv = cv2.bitwise_not(floodfill_hole)
        fill_hole = input_image | floodfill_hole_inv
        
        return fill_hole
    
    def bcg_filter(input_image, brightness, contrast, gamma):
        brightness_value = brightness
        brightness = int((brightness_value - 0) * (255 - (-255)) / (510 - 0) + (-255))
        contrast_value = contrast
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
        cal = cv2.addWeighted(input_image, alpha_brightness,  
                            input_image, 0, gamma_brightness)
        # contraste
        alpha_contrast = float(131 * (contrast + 127)) / (127 * (131 - contrast)) 
        gamma_contrast = 127 * (1 - alpha_contrast) 
        cal = cv2.addWeighted(cal, alpha_contrast,  
                            cal, 0, gamma_contrast)
        # gamma
        invGamma = gamma
        lookUpTable = table = np.array([((j / 255.0) ** invGamma) * 255
            for j in np.arange(0, 256)]).astype("uint8")
        bcg_image = cv2.LUT(cal, lookUpTable)
        
        return bcg_image
    
    def numberHolesParticleFilter(input_image, minimum_holes = 0):
        analised_contours, hierarchy_list = cv2.findContours(input_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        hierarchy = hierarchy_list[0]
        external_contour = [h for h in range(len(hierarchy)) if hierarchy[h][-1] == -1]
        for cnt in external_contour:
            holes = [contour for contour in hierarchy if contour[-1]==cnt]
            if len(holes) <= minimum_holes:
                no_mark_mask = np.zeros(input_image.shape, np.uint8)
                no_mark_mask.fill(255)
                [cv2.drawContours(no_mark_mask, analised_contours, cnt, (0, 0, 0), -1)]
                if len(external_contour) == 1:
                    rivet_contour = hierarchy[cnt][2]
                    [cv2.drawContours(no_mark_mask, analised_contours, rivet_contour, (255, 255, 255), -1)]
                    no_mark_mask = cv2.erode(no_mark_mask, np.ones((3,3), np.uint8))
                particle_filtered_image = input_image.copy()
                particle_filtered_image[no_mark_mask==0]=0
            else:
                particle_filtered_image = input_image.copy()

        return particle_filtered_image