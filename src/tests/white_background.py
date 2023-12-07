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
original_image = cv2.imread(f"{root_dir}\\created_files\\background_test\\demostration_frames_1701694079748.png")
fill_hole_2 = cv2.imread(f"{root_dir}\\created_files\\background_test\\fill_hole.jpeg")
fill_hole_2 = cv2.cvtColor(fill_hole_2, cv2.COLOR_BGR2GRAY)
fill_hole_2 = cv2.threshold(fill_hole_2, 85, 255, cv2.THRESH_BINARY)[1]
crop_original = cv2.imread(f"{root_dir}\\created_files\\background_test\\crop_original.jpeg")
# cv2.imshow('[1] original' ,fill_hole_2)
# cv2.imwrite('[1].jpeg', original_image)

rivet_circles = cv2.HoughCircles(fill_hole_2, cv2.HOUGH_GRADIENT, 1, 150, param1 = 70,
               param2 = 12, minRadius = 20, maxRadius = 50)

image_center = (crop_original.shape[0]/2, crop_original.shape[1]/2)
image_center = np.array(image_center)

center_list = [(a,b) for (a, b, r) in rivet_circles[0, :]]

distance_from_center = [np.linalg.norm(c - image_center) for c in center_list]
print(distance_from_center)
rivet_distance = []
for i, _ in enumerate(distance_from_center):
    if 620 > distance_from_center[i] > 400:
        rivet_distance.append(i)
        
rivet_circles = rivet_circles[0][[rivet_distance]]

if rivet_circles is not None:
    
    rivet_conference = {}
    
    drawing_image = crop_original.copy()
    for (a, b, r) in rivet_circles[0, :]:
        rivet_center_coordinates = (int(a), int(b))
        rivet_radius = int(r)
        cv2.circle(drawing_image, rivet_center_coordinates, rivet_radius, (255, 0, 0), 2)
        # cv2.circle(drawing_image, rivet_center_coordinates, 1, (0, 0, 255), 3)
    cv2.imshow("desenho", drawing_image)
    
    for i, (a, b, r) in enumerate(rivet_circles[0, :]):
        rivet_conference[f'{i}'] = []
        rivet_center_coordinates = (int(a), int(b))
        rivet_radius = int(r)
        # print(f'coordenadas centro do rebite {i+1}', rivet_center_coordinates)
        # print(f'raio do círculo do rebite {i+1}', rivet_radius)
        rivet_image = crop_original[rivet_center_coordinates[1]-rivet_radius-20:rivet_center_coordinates[1]+rivet_radius+20, 
                                rivet_center_coordinates[0]-rivet_radius-20:rivet_center_coordinates[0]+rivet_radius+20]
        cv2.imshow("rebite", rivet_image)
        cv2.waitKey()
        cv2.destroyAllWindows()

cv2.waitKey()
cv2.destroyAllWindows()