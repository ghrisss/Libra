from pathlib import Path

import cv2
import numpy as np

from src.controllers.cv import VisionController
from src.configs import FRAME

# cv2.namedWindow('show', cv2.WINDOW_NORMAL)
# cv2.imshow('show', convex_hull_image)
# cv2.imwrite('show.png', convex_hull_image)
# cv2.waitKey()
# cv2.destroyAllWindows()

class VisionJob():
    def __init__(self):
        self.rivet_conference = {}
    
    def rivet_mark(self, rivet_image, rivet_number):
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
                print('O ponto está rebitado')
                self.rivet_conference.get(f'{rivet_number}').append(True)
            else:
                print('O ponto não está rebitado')
                self.rivet_conference.get(f'{rivet_number}').append(False)
        else:
            print('O ponto não está rebitado')
            self.rivet_conference.get(f'{rivet_number}').append(False)
        
        
    def rivet_presence(self, rivet_image, rivet_number):
        segmentation_blur = cv2.medianBlur(rivet_image, 9)
        hsv_image = cv2.cvtColor(segmentation_blur, cv2.COLOR_BGR2HSV)
        segmentation_mask = cv2.inRange(hsv_image, (18,52,108), (33, 255, 215))
        segmented_rivet = cv2.bitwise_and(rivet_image,rivet_image,mask=segmentation_mask)
        color_presence, _ = cv2.findContours(segmentation_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if FRAME.get('SHOW'):
            cv2.imshow('analise de presença de arruela', segmented_rivet)
        self.rivet_conference.get(f'{rivet_number}').append(True) if len(color_presence)>0 else self.rivet_conference.get(f'{rivet_number}').append(False)
    
    
    def analysis(self, image_name):
        root_dir = Path(__file__).parent.parent.parent
        original_image = cv2.imread(f"{root_dir}/\\{image_name}")
        if FRAME.get('SHOW'):
            cv2.namedWindow('captured image', cv2.WINDOW_NORMAL)
            cv2.imshow('captured image', original_image)
        pb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(pb_image, (7,7), 0)
        convoluted_image = VisionController.HighlightDetails(blurred_image, size=7, center=60)
        thresh_image = cv2.threshold(convoluted_image, 80, 255, cv2.THRESH_BINARY)[1]
        if FRAME.get('SHOW'):
            cv2.namedWindow('thresholded image', cv2.WINDOW_NORMAL)
            cv2.imshow('thresholded image', thresh_image)
        low_pass_image = cv2.morphologyEx(src=thresh_image, op=cv2.MORPH_HITMISS , kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(5,5)), iterations=1)
        low_pass_image = cv2.threshold(low_pass_image, 136, 255, cv2.THRESH_BINARY)[1]
        
        floodfill_image = VisionController.removeBorderObjects(low_pass_image)
        filtered_particles = VisionController.perimeterParticleFilter(floodfill_image, maximum_particle=200)
        convex_hull_image = VisionController.convexHull(filtered_particles)
        
        crop_filtered_roi, roi_image = VisionController.crop_ring(input_image=convex_hull_image, crop_image=filtered_particles, original_image=original_image)
        
        if crop_filtered_roi is not None:
            fill_hole_image = VisionController.fill_holes(crop_filtered_roi)
            interest_points_image = cv2.bitwise_xor(crop_filtered_roi, fill_hole_image)
            filtered_rivet_points = VisionController.areaParticleFilter(interest_points_image, maximum_particle=1100)
            closing_rivet_points = cv2.morphologyEx(filtered_rivet_points, cv2.MORPH_CLOSE, (3,3), iterations=2)
            rivet_points_filled = VisionController.fill_holes(closing_rivet_points)
            rivet_circles = cv2.HoughCircles(rivet_points_filled, cv2.HOUGH_GRADIENT, 1, 150, param1 = 70,
               param2 = 12, minRadius = 20, maxRadius = 50)
            
            if rivet_circles is not None:
                for i, (a, b, r) in enumerate(rivet_circles[0, :]):
                    self.rivet_conference[f'{i}'] = []
                    rivet_center_coordinates = (int(a), int(b))
                    rivet_radius = int(r)
                    
                    rivet_image = roi_image[rivet_center_coordinates[1]-rivet_radius-45:rivet_center_coordinates[1]+rivet_radius+45, 
                                rivet_center_coordinates[0]-rivet_radius-45:rivet_center_coordinates[0]+rivet_radius+45]
                    if FRAME.get('SHOW'):
                        cv2.imshow('rivet image', rivet_image)
                    self.rivet_mark(rivet_image, i)
                    self.rivet_presence(rivet_image, i)
                    print('situação dos pontos de análise:\n', self.rivet_conference)
                    cv2.waitKey()
                    cv2.destroyAllWindows()
            else:
                print('nenhum ponto de análise encontrado')
                
        else:
            print('anel de curto não encontrado')
            if FRAME.get('SHOW'):
                cv2.namedWindow('search for short-circuit ring', cv2.WINDOW_NORMAL)
                cv2.imshow('search for short-circuit ring', convex_hull_image)
            cv2.waitKey()
            cv2.destroyAllWindows()
        
        return self.rivet_conference