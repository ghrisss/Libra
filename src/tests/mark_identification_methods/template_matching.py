import cv2
import numpy as np

from src.configs import SAVE
from src.controllers.files import FilesController

def templateMatching(input_image):
    # grayscaling
    pb_rivet_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    rivet_copy = pb_rivet_image.copy()
    
    # Equalização a imagem
    rivet_equalized = cv2.equalizeHist(rivet_copy)
    # cv2.imshow("[25] local equalizado", rivet_equalized)

    # alteração de brilho e contraste
    brightness_value = 191
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
    invGamma = 0.53
    lookUpTable = table = np.array([((j / 255.0) ** invGamma) * 255
        for j in np.arange(0, 256)]).astype("uint8")
    bcg_image = cv2.LUT(cal, lookUpTable)
    # cv2.imshow("[26] imagem com ajuste bcg", bcg_image)
    
    # filtro com mediana de borramento 1
    median_rivet = cv2.medianBlur(bcg_image, 3)
    # cv2.imshow("[27] ponto de analise com filtro de mediana para borramento", median_rivet)
    
    # filtro de convolução
    kernel = np.ones((21,21))
    for j, line in enumerate(kernel):
        kernel[j] = np.negative(line)
    kernel[21//2,21//2] = 550
    kernel = kernel/(np.sum(kernel))

    convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(10,10))
    # cv2.imshow("[28] ponto de analise com filtro de aumento de detalhes", convoluted_rivet)
    
    # filtro de borramento gaussiano 2
    blurred_rivet = cv2.GaussianBlur(convoluted_rivet, (3,3), 0)
    # if SAVE:
    #     dir_name = 'comparision_template_frames'
    #     file_name = f'{dir_name}_{int(time() * 1000)}.jpeg'
    #     cv2.imwrite(f'{file_name}', blurred_rivet)
    #     FilesController.transferFile(dir_name=dir_name, file_name=file_name)
    # cv2.imshow("[29] ponto de analise com borramento gaussiano", blurred_rivet)
    
    return blurred_rivet