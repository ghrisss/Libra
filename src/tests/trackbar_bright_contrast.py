import os
import sys

# Obtém o diretório raiz do projeto
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
print(root_dir)
# Adiciona o diretório raiz ao caminho de busca do Python
sys.path.append(root_dir)

import cv2
import numpy as np

from pathlib import Path

def BrightnessContrast(brightness): 
     
    # getTrackbarPos returns the current 
    # position of the specified trackbar. 
    brightness = cv2.getTrackbarPos('Brightness', 'bcg') 
      
    contrast = cv2.getTrackbarPos('Contrast', 'bcg') 
  
    effect = controller(img, brightness, contrast) 
  
    # The function imshow displays an image 
    # in the specified window 
    # cv2.imshow('Effect', effect)
    # filtro com mediana de borramento 1
    median_rivet = cv2.medianBlur(effect, 3)
    # cv2.imshow("[27] ponto de analise com filtro de mediana para borramento", median_rivet)
    
    # filtro de convolução
    kernel = np.ones((13,13))
    for i, line in enumerate(kernel):
        kernel[i] = np.negative(line)
    kernel[13//2,13//2] = 210
    kernel = kernel/(np.sum(kernel))

    convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(6,6))
    cv2.imshow("Effect", convoluted_rivet)


def controller(img, brightness=255, contrast=127):
    
    brightness = int((brightness - 0) * (255 - (-255)) / (510 - 0) + (-255))
    contrast = int((contrast - 0) * (127 - (-127)) / (254 - 0) + (-127)) 
  
    if brightness != 0: 
  
        if brightness > 0: 
            shadow = brightness 
            max = 255
  
        else: 
            shadow = 0
            max = 255 + brightness 

        al_pha = (max - shadow) / 255
        ga_mma = shadow

  
        # The function addWeighted calculates 
        # the weighted sum of two arrays 
        cal = cv2.addWeighted(img, al_pha, img, 0, ga_mma) 

    else: 
        cal = img 
  
    if contrast != 0: 
        Alpha = float(131 * (contrast + 127)) / (127 * (131 - contrast)) 
        Gamma = 127 * (1 - Alpha)
  
        # The function addWeighted calculates 
        # the weighted sum of two arrays 
        cal = cv2.addWeighted(cal, Alpha, cal, 0, Gamma) 
  
    # putText renders the specified text string in the image. 
    cv2.putText(cal, 'B:{},C:{}'.format(brightness, contrast), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
    
    invGamma = 0.53
    lookUpTable = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    cal = cv2.LUT(cal, lookUpTable)
  
    return cal 


if __name__ == '__main__':

    cv2.namedWindow('bcg')
    cv2.resizeWindow('bcg', 800, 80)

    root_dir = Path(__file__).parent.parent.parent
    rivet_image = cv2.imread(f"{root_dir}/\\created_files\\rivet_post_visit\\rivet_post_visit_1700483712751.png")
    
    pb_rivet_image = cv2.cvtColor(rivet_image, cv2.COLOR_BGR2GRAY)
    rivet_copy = pb_rivet_image.copy()
    rivet_equalized = cv2.equalizeHist(rivet_copy)

    img = rivet_equalized.copy()

    cv2.imshow('original', rivet_equalized) 

    cv2.createTrackbar('Brightness', 'bcg', 255, 2 * 255, BrightnessContrast)
    cv2.createTrackbar('Contrast', 'bcg', 127, 2 * 127, BrightnessContrast)  

    BrightnessContrast(0)
    
cv2.waitKey(0)