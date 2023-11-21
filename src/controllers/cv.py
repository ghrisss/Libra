import numpy as np
import cv2

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
        img_contours, _ = cv2.findContours(input_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        particles_contours = [contour for contour in img_contours if cv2.arcLength(contour, closed=True) <= maximum_particle]
        
        particles_mask = np.zeros(input_image.shape, np.uint8)
        particles_mask.fill(255)
        [cv2.drawContours(particles_mask, [cnts], -1, (0, 0, 0), -1) for cnts in particles_contours]
        filtered_particles = input_image.copy()
        filtered_particles[particles_mask==0]=0
        
        return filtered_particles
    
    
    def areaParticleFilter(input_image , maximum_particle):
        input_contours = cv2.findContours(input_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[0]
        particles_countours = [contour for contour in input_contours if cv2.contourArea(contour) <= maximum_particle]
            
        particle_mask = np.zeros(input_image.shape, np.uint8)
        particle_mask.fill(255)
        [cv2.drawContours(particle_mask, [cnts], -1, (0, 0, 0), -1) for cnts in particles_countours]
        particle_filteres_image = input_image.copy()
        particle_filteres_image[particle_mask==0]=0
        
        return particle_filteres_image
    
    
    def convexHull(input_image):
        convex_contours, _ = cv2.findContours(input_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        convex_hull_image = input_image.copy()
        for cnts in convex_contours:
            convex_hull = cv2.convexHull(cnts)
            cv2.fillPoly(convex_hull_image, pts =[convex_hull], color=(255,255,255))
            
        return convex_hull_image
    
    
    def crop_ring(input_image, crop_image, original_image):
        circles_roi = cv2.HoughCircles(input_image, cv2.HOUGH_GRADIENT, 1, 150, param1 = 255,
               param2 = 15, minRadius = 250, maxRadius = 500)
        
        if circles_roi is not None:
            radius_list = [r for (a, b, r) in circles_roi[0, :]] # cria um array com todos os raios dos circulos encontrados
            roi_radius = sorted(radius_list, reverse=True)[0] # organiza a lista de forma descrescente, e seleciona então o maior raio dentre os encontrados como o raio de interesse
            roi_circle_index = radius_list.index(roi_radius) # verifica qual o índice desse raio na lista, que consequentemente também é o mesmo índice na lista de círculos encontrados
            (a, b, r) = circles_roi[0, :][roi_circle_index] # determina as coordenadas do círculo de maior raio, também sendo o círculo de maior interesse
            
            center_coordinates = (int(a), int(b))
            radius = int(r)
            img_h, img_w = input_image.shape[:2]
            mask = np.zeros((img_h, img_w), np.uint8)
            
            roi_mask = cv2.circle(mask, center_coordinates, radius, (255,255,255), -1)
            masked_image = cv2.bitwise_and(original_image, original_image, mask=roi_mask)
            roi_image = masked_image[center_coordinates[1]-radius-50:center_coordinates[1]+radius+50, 
                         center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]
            crop_filtered_roi = crop_image[center_coordinates[1]-radius-50:center_coordinates[1]+radius+50,
                                        center_coordinates[0]-radius-50:center_coordinates[0]+radius+50]
        else:
            print('ERRO DE OPERAÇÃO: anel de curto não encontrado')
            roi_image = None
            crop_filtered_roi = None
            
        return crop_filtered_roi, roi_image
    
    
    def fill_holes(input_image):
        floodfill_hole = input_image.copy()
        h, w = input_image.shape[:2]
        mask = np.zeros((h+2, w+2), np.uint8)
        
        cv2.floodFill(floodfill_hole, mask, (0,0), 255);
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