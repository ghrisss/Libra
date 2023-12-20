import os
import sys

# Obtém o diretório raiz do projeto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print(root_dir)
# Adiciona o diretório raiz ao caminho de busca do Python
sys.path.append(root_dir)


from pathlib import Path
import cv2
import imutils
import numpy as np

from src.controllers.cv import VisionController


def updateThreshold(val = 128):
    global threshhold_crop_ring
    thresh_image = cv2.threshold(convoluted_image, val, 255, cv2.THRESH_BINARY)[1]
    cv2.namedWindow('altered image', cv2.WINDOW_NORMAL)
    cv2.imshow('altered image', thresh_image)
    threshhold_crop_ring = val


def updatePointsDetermination(val, operation):
    global threshhold_points_determination
    global filter_points_determination
    value_points[operation] = val
    crop_filtered_roi = cv2.threshold(convoluted_roi, value_points[0], 255, cv2.THRESH_BINARY)[1]
    threshhold_points_determination = value_points[0]
    cv2.imshow('thresh roi image', crop_filtered_roi)
    fill_hole_image = VisionController.fill_holes(crop_filtered_roi)
    # cv2.imshow('fill holes', fill_hole_image)
    interest_points_image = cv2.bitwise_xor(crop_filtered_roi, fill_hole_image)
    # cv2.imshow('interest points', interest_points_image)
    filtered_rivet_points = VisionController.boundingRectWidthFilter(interest_points_image, maximum_value=value_points[1])
    filter_points_determination = value_points[1]
    closing_rivet_points = cv2.morphologyEx(filtered_rivet_points, cv2.MORPH_CLOSE, (3,3), iterations=2)
    rivet_points_filled = VisionController.fill_holes(closing_rivet_points)
    cv2.imshow('rivet points', rivet_points_filled)


def updateRivetDetection(val, operation):
    global rivet_detection_distance
    global rivet_detection_param2
    global rivet_detection_min_radius
    global rivet_detection_max_radius
    value_rivet[operation] = val
    rivet_detection_distance  = value_rivet[0]
    rivet_detection_param2 = value_rivet[1]
    rivet_detection_min_radius = value_rivet[2]
    rivet_detection_max_radius = value_rivet[3]
    rivet_circles = cv2.HoughCircles(rivet_points_filled, cv2.HOUGH_GRADIENT, 1, value_rivet[0], param1 = 70,
        param2 = value_rivet[1], minRadius = value_rivet[2], maxRadius = value_rivet[3])
    image_center = (crop_original_roi.shape[0]/2, crop_original_roi.shape[1]/2)
    image_center = np.array(image_center)
    circles_center_list = [(a,b) for (a, b, r) in rivet_circles[0, :]]
    distance_from_center = [np.linalg.norm(c - image_center) for c in circles_center_list]
    rivet_distance = []
    for i, _ in enumerate(distance_from_center):
        if 620 > distance_from_center[i] > 400:
            rivet_distance.append(i)
    rivet_circles = rivet_circles[0][[rivet_distance]]
    
    if np.any(rivet_circles):
        drawing_image = crop_original_roi.copy()
        # --- desenho dos pontos de análise encontrado --- #
        for (a, b, r) in rivet_circles[0, :]:
            rivet_center_coordinates = (int(a), int(b))
            rivet_radius = int(r)
            cv2.circle(drawing_image, rivet_center_coordinates, rivet_radius, (255, 0, 0), 2)
    cv2.imshow('rivet detection', drawing_image)


def updateRivetColor(val, operation):
    global color_rivet_blur
    global color_rivet_low_hue
    global color_rivet_high_hue
    global color_rivet_low_sat
    global color_rivet_high_sat
    global color_rivet_low_val
    global color_rivet_high_val
    value_color[operation] = val
    if value_color[0] % 2 == 0:
        value_color[0] -= 1
    color_rivet_blur  = value_color[0]
    color_rivet_low_hue = value_color[1]
    color_rivet_high_hue = value_color[2]
    color_rivet_low_sat = value_color[3]
    color_rivet_high_sat  = value_color[4]
    color_rivet_low_val = value_color[5]
    color_rivet_high_val = value_color[6]
    segmentation_blur = cv2.medianBlur(rivet_image, value_color[0])
    hsv_image = cv2.cvtColor(segmentation_blur, cv2.COLOR_BGR2HSV)
    segmentation_mask = cv2.inRange(hsv_image, (value_color[1],value_color[3],value_color[5]), 
                                    (value_color[2], value_color[4], value_color[6]))
    segmented_rivet = cv2.bitwise_and(rivet_image,rivet_image,mask=segmentation_mask)
    cv2.imshow(f'rivet color threshold', segmented_rivet)


def updateHighlightMark(val, operation):
    global mark_threshold
    global mimimum_particle_area_size
    global maximum_particle_area_size
    global bouding_rect_max_size
    value_highlight[operation] = val
    mark_threshold  = value_highlight[0]
    mimimum_particle_area_size = value_highlight[1]
    maximum_particle_area_size = value_highlight[2]
    bouding_rect_max_size = value_highlight[3]
    
    pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
    # median_rivet = cv2.medianBlur(pb_rivet_image, 3)
    convoluted_rivet = VisionController.HighlightDetails(pb_rivet_image, size=19, center=450)
    thresh_rivet = cv2.threshold(convoluted_rivet, value_highlight[0], 255, cv2.THRESH_BINARY)[1]
    floodfill_rivet = VisionController.removeBorderObjects(thresh_rivet)
    close_rivet = cv2.morphologyEx(floodfill_rivet, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)))
    filtered_rivet = VisionController.areaParticleFilter(close_rivet, remove = False, minimum_particle=value_highlight[1], maximum_particle=value_highlight[2])
    rivet_no_mark = VisionController.boundingRectWidthFilter(filtered_rivet, remove=False, maximum_value=value_highlight[3])
    cv2.imshow('highlight of non-rivet washer', rivet_no_mark)

def updateDetectionRivetMark(val, operation):
    global rivet_mark_distance
    global rivet_mark_param2
    global rivet_mark_min_radius
    global rivet_marl_max_radius
    value_mark[operation] = val
    rivet_mark_distance  = value_mark[0]
    rivet_mark_param2 = value_mark[1]
    rivet_mark_min_radius = value_mark[2]
    rivet_marl_max_radius = value_mark[3]
    rivet_circle = cv2.HoughCircles(rivet_no_mark, cv2.HOUGH_GRADIENT, 1, value_mark[0], param1 = 70,
        param2 = value_mark[1], minRadius = value_mark[2], maxRadius = value_mark[3])
    drawing_rivet = rivet_image.copy()
        # --- desenho dos pontos de análise encontrado --- #
    if np.any(rivet_circles):
        for (a, b, r) in rivet_circle[0, :]:
            rivet_center_coordinates = (int(a), int(b))
            rivet_radius = int(r)
            cv2.circle(drawing_rivet, rivet_center_coordinates, rivet_radius, (255, 0, 0), 2)
        cv2.imshow('rivet detection', drawing_rivet)


# ------------------------------------------------------------------------------------------------------------------------------------

root_dir = Path(__file__).parent.parent.parent
original_image = cv2.imread(f"{root_dir}\\created_files\\eixos_frames\\eixos_frames_1701434263273.png")
cv2.imshow('original', original_image)
pb_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
blurred_image = cv2.GaussianBlur(pb_image, (7,7), 0)
convoluted_image = VisionController.HighlightDetails(blurred_image, size=7, center=60)
window = "Thresh Control"
cv2.namedWindow(window)
cv2.resizeWindow(window, 1000, 320)
cv2.createTrackbar('threshold', window, 128, 255, lambda x: updateThreshold(x))
cv2.waitKey(0)
cv2.destroyAllWindows()
print(threshhold_crop_ring)

# ------------------------------------------------------------------------------------------------------------------------------------

thresh_image = cv2.threshold(convoluted_image, threshhold_crop_ring, 255, cv2.THRESH_BINARY)[1]
floodfill_image = VisionController.removeBorderObjects(thresh_image)
filtered_particles = VisionController.perimeterParticleFilter(floodfill_image, maximum_particle=250)
crop_original_roi = VisionController.crop_ring(input_image=filtered_particles, original_image=original_image) # region of interest
cv2.imshow('crop', crop_original_roi)
cv2.waitKey(0)
cv2.destroyAllWindows()


if crop_original_roi is not None:
    pb_roi = cv2.cvtColor(crop_original_roi, cv2.COLOR_BGR2GRAY)
    blurred_roi = cv2.GaussianBlur(pb_roi, (5,5), 0)
    convoluted_roi = VisionController.HighlightDetails(blurred_roi, size=17, center=360)
    
    value_points = [128,0]
    window = "Points Determination Control"
    cv2.namedWindow(window)
    cv2.resizeWindow(window, 1000, 320)
    cv2.createTrackbar('threshold', window, 128, 255, lambda x: updatePointsDetermination(x, 0))
    cv2.createTrackbar('maximum particle size', window, 0, 80, lambda x: updatePointsDetermination(x, 1))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(threshhold_points_determination)
    print(filter_points_determination)
    
    # ------------------------------------------------------------------------------------------------------------------------------------
    
    crop_filtered_roi = cv2.threshold(convoluted_roi, threshhold_points_determination, 255, cv2.THRESH_BINARY)[1]
    fill_hole_image = VisionController.fill_holes(crop_filtered_roi)
    interest_points_image = cv2.bitwise_xor(crop_filtered_roi, fill_hole_image)
    filtered_rivet_points = VisionController.boundingRectWidthFilter(interest_points_image, maximum_value=filter_points_determination)
    
    closing_rivet_points = cv2.morphologyEx(filtered_rivet_points, cv2.MORPH_CLOSE, (3,3), iterations=2)
    rivet_points_filled = VisionController.fill_holes(closing_rivet_points)
    
    value_rivet = [200, 12, 20, 50]
    window = "rivet circles detection"
    cv2.namedWindow(window)
    cv2.resizeWindow(window, 1000, 320)
    cv2.createTrackbar('distance between circles', window, 200, 500, lambda x: updateRivetDetection(x, 0))
    cv2.createTrackbar('circle shape precision', window, 12, 25, lambda x: updateRivetDetection(x, 1))
    cv2.createTrackbar('minimum radius', window, 20, 100, lambda x: updateRivetDetection(x, 2))
    cv2.createTrackbar('maximum radius', window, 50, 200, lambda x: updateRivetDetection(x, 3))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    print(rivet_detection_distance)
    print(rivet_detection_param2)
    print(rivet_detection_min_radius)
    print(rivet_detection_max_radius)
    
    # ------------------------------------------------------------------------------------------------------------------------------------
    
    rivet_circles = cv2.HoughCircles(rivet_points_filled, cv2.HOUGH_GRADIENT, 1, rivet_detection_distance, param1 = 70,
        param2 = rivet_detection_param2, minRadius = rivet_detection_min_radius, maxRadius = rivet_detection_max_radius)
    
    image_center = (crop_original_roi.shape[0]/2, crop_original_roi.shape[1]/2)
    image_center = np.array(image_center)
    circles_center_list = [(a,b) for (a, b, r) in rivet_circles[0, :]]
    distance_from_center = [np.linalg.norm(c - image_center) for c in circles_center_list]
    rivet_distance = []
    for i, _ in enumerate(distance_from_center):
        if 620 > distance_from_center[i] > 400:
            rivet_distance.append(i)
    rivet_circles = rivet_circles[0][[rivet_distance]]
    
    for i, (a, b, r) in enumerate(rivet_circles[0, :]):
        rivet_center_coordinates = (int(a), int(b))
        rivet_radius = int(r)
        rivet_image = crop_original_roi[rivet_center_coordinates[1]-rivet_radius-35:rivet_center_coordinates[1]+rivet_radius+35, 
                    rivet_center_coordinates[0]-rivet_radius-35:rivet_center_coordinates[0]+rivet_radius+35]
        
        value_color = [9, 0, 179, 0, 255, 0, 255]
        window = "rivet color detection"
        cv2.namedWindow(window)
        cv2.resizeWindow(window, 1000, 320)
        cv2.createTrackbar("blur filter", window, 9,99,lambda x: updateRivetColor(x, 0))
        cv2.createTrackbar("Low Hue", window, 0,179,lambda x: updateRivetColor(x, 1))
        cv2.createTrackbar("High Hue", window, 179,179,lambda x: updateRivetColor(x, 2))
        cv2.createTrackbar("Low Sat", window, 0,255,lambda x: updateRivetColor(x, 3))
        cv2.createTrackbar("High Sat", window, 255,255,lambda x: updateRivetColor(x, 4))
        cv2.createTrackbar("Low Val", window, 0,255,lambda x: updateRivetColor(x, 5))
        cv2.createTrackbar("High Val", window, 255,255,lambda x: updateRivetColor(x, 6))
        cv2.waitKey(0)
        # cv2.destroyAllWindows()
        print(color_rivet_blur)
        low_threshold_color_rivet = (color_rivet_low_hue, color_rivet_low_sat, color_rivet_low_val)
        low_threshold_color_rivet = (color_rivet_high_hue, color_rivet_high_sat, color_rivet_high_val)
        print(low_threshold_color_rivet)
        print(low_threshold_color_rivet)
        
        # ------------------------------------------------------------------------------------------------------------------------------------
        
        segmentation_blur = cv2.medianBlur(rivet_image, color_rivet_blur)
        hsv_image = cv2.cvtColor(segmentation_blur, cv2.COLOR_BGR2HSV)
        segmentation_mask = cv2.inRange(hsv_image, (color_rivet_low_hue,color_rivet_low_sat,color_rivet_low_val),
                                        (color_rivet_high_hue, color_rivet_high_sat, color_rivet_high_val))
        segmented_rivet = cv2.bitwise_and(rivet_image,rivet_image,mask=segmentation_mask)
        
        value_highlight = [128, 100, 1800, 65]
        window = "highlight rivet mark"
        cv2.namedWindow(window)
        cv2.resizeWindow(window, 1000, 320)
        cv2.createTrackbar("threshold", window, 128,255,lambda x: updateHighlightMark(x, 0))
        cv2.createTrackbar("mimimum particle size", window, 100,500,lambda x: updateHighlightMark(x, 1))
        cv2.createTrackbar("maximum particle size", window, 1800,2500,lambda x: updateHighlightMark(x, 2))
        cv2.createTrackbar("bouding rect max size", window, 65,100,lambda x: updateHighlightMark(x, 3))
        cv2.waitKey(0)
        # cv2.destroyAllWindows()
        print(mark_threshold)
        print(mimimum_particle_area_size)
        print(maximum_particle_area_size)
        print(bouding_rect_max_size)
        
        # ------------------------------------------------------------------------------------------------------------------------------------
        
        pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
        # median_rivet = cv2.medianBlur(pb_rivet_image, 3)
        convoluted_rivet = VisionController.HighlightDetails(pb_rivet_image, size=19, center=450)
        thresh_rivet = cv2.threshold(convoluted_rivet, mark_threshold, 255, cv2.THRESH_BINARY)[1]
        floodfill_rivet = VisionController.removeBorderObjects(thresh_rivet)
        close_rivet = cv2.morphologyEx(floodfill_rivet, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)))
        filtered_rivet = VisionController.areaParticleFilter(close_rivet, remove = False, minimum_particle=mimimum_particle_area_size, maximum_particle=maximum_particle_area_size)
        rivet_no_mark = VisionController.boundingRectWidthFilter(filtered_rivet, remove=False, maximum_value=bouding_rect_max_size)
        
        value_mark = [150, 11, 20, 30]
        window = "detect rivet circular mark"
        cv2.namedWindow(window)
        cv2.resizeWindow(window, 1000, 320)
        cv2.createTrackbar('distance between circles', window, 150, 500, lambda x: updateDetectionRivetMark(x, 0))
        cv2.createTrackbar('circle shape precision', window, 11, 25, lambda x: updateDetectionRivetMark(x, 1))
        cv2.createTrackbar('minimum radius', window, 20, 40, lambda x: updateDetectionRivetMark(x, 2))
        cv2.createTrackbar('maximum radius', window, 30, 60, lambda x: updateDetectionRivetMark(x, 3))
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # ------------------------------------------------------------------------------------------------------------------------------------
        rivet_circle = cv2.HoughCircles(rivet_no_mark, cv2.HOUGH_GRADIENT, 1, 150, param1 = 255,
                                                    param2 = 11, minRadius = 20, maxRadius = 30)