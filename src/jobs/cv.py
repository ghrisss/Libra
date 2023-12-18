from pathlib import Path

import cv2
import numpy as np

from src.configs import FRAME
from src.controllers.cv import VisionController
from src.controllers.files import FilesController

# cv2.namedWindow('show', cv2.WINDOW_NORMAL)
# cv2.imshow('show', convex_hull_image)
# cv2.imwrite('show.png', convex_hull_image)
# cv2.waitKey()
# cv2.destroyAllWindows()

class VisionJob():
    def __init__(self):
        self.rivet_conference = {}
    
    def rivetMark(self, rivet_image, rivet_number):
        pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
        rivet_copy = pb_rivet_image.copy()
        rivet_equalized = cv2.equalizeHist(rivet_copy)
        bcg_image = VisionController.bcg_filter(rivet_equalized, brightness=196, contrast=134, gamma=0.53)
        median_rivet = cv2.medianBlur(bcg_image, 3)
        convoluted_rivet = VisionController.HighlightDetails(median_rivet, size=13, center=210)
        thresh_rivet = cv2.threshold(convoluted_rivet, 45, 255, cv2.THRESH_BINARY_INV)[1]
        
        morphology_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        automedian_rivet = cv2.morphologyEx(thresh_rivet, cv2.MORPH_OPEN, morphology_kernel)
        
        floodfill_rivet = VisionController.removeBorderObjects(automedian_rivet)
        filtered_rivet_1 = VisionController.areaParticleFilter(floodfill_rivet, maximum_particle=60)
        
        morphology_kernel = np.ones((3,3), np.uint8)
        morphology_operations = cv2.morphologyEx(filtered_rivet_1, cv2.MORPH_CLOSE, morphology_kernel)
        morphology_kernel[::morphology_kernel.shape[0]-1, ::morphology_kernel.shape[1]-1] = 0
        morphology_operations = cv2.morphologyEx(morphology_operations, cv2.MORPH_OPEN, morphology_kernel)
        filtered_rivet_2 = VisionController.areaParticleFilter(morphology_operations, maximum_particle=160)
        
        morphology_kernel = np.ones((5,5), np.uint8)
        morphology_kernel[::morphology_kernel.shape[0]-1, ::morphology_kernel.shape[1]-1] = 0
        agroup_rivet = cv2.morphologyEx(filtered_rivet_2, cv2.MORPH_CLOSE, morphology_kernel, iterations=2)
        filtered_rivet_3 = VisionController.areaParticleFilter(agroup_rivet, maximum_particle=400)
        rivet_mark = VisionController.numberHolesParticleFilter(filtered_rivet_3, minimum_holes=2)
        if FRAME.get('SHOW'):
            cv2.imshow('análise de marcação padrão', rivet_mark)
        
        _, hierarchy_list = cv2.findContours(rivet_mark, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if hierarchy_list is not None:
            hierarchy = hierarchy_list[0]
            pattern_holes = len(hierarchy) - 1
            if pattern_holes > 2:
                self.rivet_conference.get(f'{rivet_number}').append(True)
            else:
                self.rivet_conference.get(f'{rivet_number}').append(False)
        else:
            self.rivet_conference.get(f'{rivet_number}').append(False)
        
    def rivetNoMark(self, rivet_image, rivet_number, **kwargs):
        pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
        # median_rivet = cv2.medianBlur(pb_rivet_image, 3)
        convoluted_rivet = VisionController.HighlightDetails(pb_rivet_image, size=19, center=450)
        thresh_rivet = cv2.threshold(convoluted_rivet, 128, 255, cv2.THRESH_BINARY)[1]
        
        if kwargs.get('confirmation'):
            open_rivet = cv2.morphologyEx(thresh_rivet, cv2.MORPH_OPEN, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)))
            floodfill_rivet = VisionController.removeBorderObjects(open_rivet)
            floodfill_rivet = VisionController.areaParticleFilter(floodfill_rivet, remove = False, minimum_particle=100, maximum_particle=1800)
        else:
            floodfill_rivet = VisionController.removeBorderObjects(thresh_rivet)
        if FRAME.get('SHOW'):
            cv2.imshow('análise de bordas', floodfill_rivet)
            
        close_rivet = cv2.morphologyEx(floodfill_rivet, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)))
        filtered_rivet = VisionController.areaParticleFilter(close_rivet, remove = False, minimum_particle=150, maximum_particle=1800)
        if FRAME.get('SHOW'):
            cv2.imshow('análise de filtro', filtered_rivet)
        rivet_no_mark = VisionController.boundingRectWidthFilter(filtered_rivet, remove=False, maximum_value=65)
        if FRAME.get('SHOW'):
            cv2.imshow('análise de marcação padrão', rivet_no_mark)
        
        rivet_circle = cv2.HoughCircles(rivet_no_mark, cv2.HOUGH_GRADIENT, 1, 150, param1 = 255,
                                                    param2 = 11, minRadius = 20, maxRadius = 30)
        
        if kwargs.get('confirmation'):
            if rivet_circle is not None:
                self.rivet_conference[f'{rivet_number}'][1] = False
        else:
            if rivet_circle is not None:
                self.rivet_conference.get(f'{rivet_number}').append(False)
            else:
                self.rivet_conference.get(f'{rivet_number}').append(True)
        
        
    def rivetPresence(self, rivet_image, rivet_number):
        segmentation_blur = cv2.medianBlur(rivet_image, 9)
        hsv_image = cv2.cvtColor(segmentation_blur, cv2.COLOR_BGR2HSV)
        segmentation_mask = cv2.inRange(hsv_image, (18,47,106), (82, 255, 215))
        segmented_rivet = cv2.bitwise_and(rivet_image,rivet_image,mask=segmentation_mask)
        color_presence, _ = cv2.findContours(segmentation_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(color_presence) > 0:
            image_center = (rivet_image.shape[0]/2, rivet_image.shape[1]/2)
            image_center = np.array(image_center)
            
            segmentation_mask = cv2.inRange(hsv_image, (20,21,60), (80, 255, 255))
            inverse_segmentation_mask = cv2.bitwise_not(segmentation_mask)
            confirm_rivet_mask = VisionController.removeBorderObjects(inverse_segmentation_mask)
            rivet_circles = cv2.HoughCircles(confirm_rivet_mask, cv2.HOUGH_GRADIENT, 1, 200, param1 = 255,
               param2 = 14, minRadius = 10, maxRadius = 50)
            
            for i in range(len(rivet_circles[0, :])):
                circles_center_list = [(a,b) for (a, b, r) in rivet_circles[0, :]]
                distance_from_center = [np.linalg.norm(c - image_center) for c in circles_center_list]
                for i, _ in enumerate(distance_from_center):
                    if distance_from_center[i] > 12:
                        color_presence.clear()
        if FRAME.get('SHOW'):
            cv2.imshow('analise de presença de arruela', segmented_rivet)
        
        return color_presence
    
    
    def analysis(self, image_name, metodo=2):
        root_dir = Path(__file__).parent.parent.parent
        # --- processamento para determinar o anel de curto --- #
        original_image = cv2.imread(f"{root_dir}/\\{image_name}")
        # original_image = cv2.imread(f"{root_dir}/\\created_files\\demostration_frames\\demostration_frames_1701693172012.png")
        if FRAME.get('SHOW'):
            cv2.namedWindow('captured image', cv2.WINDOW_NORMAL)
            cv2.imshow('captured image', original_image)
        pb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(pb_image, (7,7), 0)
        convoluted_image = VisionController.HighlightDetails(blurred_image, size=7, center=60)
        thresh_image = cv2.threshold(convoluted_image, 85, 255, cv2.THRESH_BINARY)[1]
        # filtro para tirar os objetos inteiros que encostam na borda
        floodfill_image = VisionController.removeBorderObjects(thresh_image)
        # filtro que retira objetos com perimetro menor que 'maximum_particle'
        filtered_particles = VisionController.perimeterParticleFilter(floodfill_image, maximum_particle=250)
        crop_original_roi = VisionController.crop_ring(input_image=filtered_particles, original_image=original_image) # region of interest

        # --- processamento para determinar os pontos de análise --- #
        if crop_original_roi is not None:
            if FRAME.get('SHOW'):
                cv2.imshow('crop of region of interest', crop_original_roi)
            pb_roi = cv2.cvtColor(crop_original_roi, cv2.COLOR_BGR2GRAY)
            blurred_roi = cv2.GaussianBlur(pb_roi, (5,5), 0)
            convoluted_roi = VisionController.HighlightDetails(blurred_roi, size=17, center=360)
            crop_filtered_roi = cv2.threshold(convoluted_roi, 55, 255, cv2.THRESH_BINARY)[1]
            fill_hole_image = VisionController.fill_holes(crop_filtered_roi)
            interest_points_image = cv2.bitwise_xor(crop_filtered_roi, fill_hole_image)
            filtered_rivet_points = VisionController.boundingRectWidthFilter(interest_points_image, maximum_value=40)
            if FRAME.get('SHOW'):
                cv2.imshow('rivet points', filtered_rivet_points)
            closing_rivet_points = cv2.morphologyEx(filtered_rivet_points, cv2.MORPH_CLOSE, (3,3), iterations=2)
            rivet_points_filled = VisionController.fill_holes(closing_rivet_points)
            rivet_circles = cv2.HoughCircles(rivet_points_filled, cv2.HOUGH_GRADIENT, 1, 200, param1 = 70,
               param2 = 15, minRadius = 20, maxRadius = 50)
            # --- filtro dos pontos proximos demais do centro da imagem --- #
            image_center = (crop_original_roi.shape[0]/2, crop_original_roi.shape[1]/2)
            image_center = np.array(image_center)
            circles_center_list = [(a,b) for (a, b, r) in rivet_circles[0, :]]
            distance_from_center = [np.linalg.norm(c - image_center) for c in circles_center_list]
            rivet_distance = []
            for i, _ in enumerate(distance_from_center):
                if 620 > distance_from_center[i] > 400:
                    rivet_distance.append(i)
            rivet_circles = rivet_circles[0][[rivet_distance]]
            
            # --- processametno e análise dos pontos encontrados --- #
            if np.any(rivet_circles):
                drawing_image = crop_original_roi.copy()
                # --- desenho dos pontos de análise encontrado --- #
                for (a, b, r) in rivet_circles[0, :]:
                    rivet_center_coordinates = (int(a), int(b))
                    rivet_radius = int(r)
                    cv2.circle(drawing_image, rivet_center_coordinates, rivet_radius, (255, 0, 0), 2)
                # --- sequencia de análise para cada ponto de análise determinado --- #
                for i, (a, b, r) in enumerate(rivet_circles[0, :]):
                    self.rivet_conference[f'{i}'] = []
                    rivet_center_coordinates = (int(a), int(b))
                    rivet_radius = int(r)
                    rivet_image = crop_original_roi[rivet_center_coordinates[1]-rivet_radius-35:rivet_center_coordinates[1]+rivet_radius+35, 
                                rivet_center_coordinates[0]-rivet_radius-35:rivet_center_coordinates[0]+rivet_radius+35]
                    if FRAME.get('SHOW'):
                        cv2.imshow('rivet image', rivet_image)
                    # --- análise da existencia de arruelas, pela sua cor --- #
                    color_presence = self.rivetPresence(rivet_image, i)
                    
                    # --- verificação de cor/presença de arruela no ponto --- #
                    if len(color_presence) == 0: # caso negativo
                        self.rivet_conference.get(f'{i}').extend((False, False))
                    else: # caso positivo
                        self.rivet_conference.get(f'{i}').append(True)
                        if metodo == 1: # metodo que busca pelos detalhes da marca em cruz
                            self.rivetMark(rivet_image, i)
                        elif metodo == 2: # metodo que identifica o detalhe circular do ponto não rebitado
                            self.rivetNoMark(rivet_image, i)
                            if self.rivet_conference[f'{i}'][1] == True:
                                self.rivetNoMark(rivet_image, i, confirmation=True)

                    if self.rivet_conference[f'{i}'][0] == self.rivet_conference[f'{i}'][1]:
                        cv2.circle(drawing_image, rivet_center_coordinates, rivet_radius, (0, 255, 0), 4)
                    else:
                        cv2.circle(drawing_image, rivet_center_coordinates, rivet_radius, (0, 0, 255), 4)
                    
                    if FRAME.get('SHOW'):
                        cv2.imshow('analysis', drawing_image)
                        cv2.waitKey()
                        cv2.destroyAllWindows()
                    name, formato = image_name.split('.')
                    cv2.imwrite(f'{name}_analysis.{formato}', drawing_image)
            else:
                print('[cvJob] ERROR: ponto das arruelas não encontrado')
                raise Exception
                
        else:
            print('[cvJob] ERROR: anel de curto não encontrado')
            if FRAME.get('SHOW'):
                cv2.namedWindow('search for short-circuit ring', cv2.WINDOW_NORMAL)
                cv2.imshow('search for short-circuit ring', filtered_particles)
            cv2.waitKey()
            cv2.destroyAllWindows()
            raise Exception
        
        cv2.waitKey()
        cv2.destroyAllWindows()