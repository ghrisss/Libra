import cv2
import numpy as np

def detailAnalysis(input_image):
    # grayscaling
    pb_rivet = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    
    # filtro com mediana de borramento
    median_rivet = cv2.medianBlur(pb_rivet, 3)
    
    # filtro de convolução
    kernel = np.ones((15,15))
    for j, line in enumerate(kernel):
        kernel[j] = np.negative(line)
    kernel[15//2,15//2] = 280
    kernel = kernel/(np.sum(kernel))
    convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(7,7))
    
    # limiarização
    thresh_rivet = cv2.threshold(convoluted_rivet, 120, 255, cv2.THRESH_BINARY)[1]
    # cv2.imshow('[32] imagem rivet limiarizada', thresh_rivet)
    
    # remoção objetos das bordas
    pad = cv2.copyMakeBorder(thresh_rivet, 1,1,1,1, cv2.BORDER_CONSTANT, value=255)
    pad_h, pad_w = pad.shape
    border_mask = np.zeros([pad_h+2, pad_w+2], np.uint8)
    floodfill_rivet = cv2.floodFill(pad, border_mask, (0,0), 0, (5), (0), flags=8)[1]
    floodfill_rivet = floodfill_rivet[1:pad_h-1, 1:pad_w-1]
    # cv2.imshow('[33] imagem sem borda', floodfill_rivet)
    
    # fechamento morfológico
    kernel = np.ones((3,3), np.uint8)
    close_rivet = cv2.morphologyEx(floodfill_rivet, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)))
    # cv2.imshow('[32] imagem rivet fechamento', close_rivet)
    
    
    # filtro de partículas (pela area)
    number_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(close_rivet, 4, cv2.CV_32S)
    
    rivet_details = np.zeros(floodfill_rivet.shape, np.uint8)

    for n_label in range(1, number_labels):
        area = stats[n_label, cv2.CC_STAT_AREA]
        if 200 < area < 900:
            rivet_details[labels == n_label] = 255
    # cv2.imshow('[33] imagem com particulas da região de interesse filtradas pela sua área', rivet_details)
    
    
    # filtro de partículas (pela comprimento)
    number_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(rivet_details, 4, cv2.CV_32S)
        
    no_mark_circle = np.zeros(rivet_details.shape, np.uint8)
    
    for n_label in range(1, number_labels):
        width = stats[n_label, cv2.CC_STAT_WIDTH]
        if width < 58:
            no_mark_circle[labels == n_label] = 255
            
            
    return no_mark_circle

def confirmAnalysis(input_image):
    # grayscaling
    pb_rivet = cv2.cvtColor(input_image, cv2.COLOR_BGR2GRAY)
    
    # filtro com mediana de borramento
    median_rivet = cv2.medianBlur(pb_rivet, 3)
    
    # filtro de convolução
    kernel = np.ones((15,15))
    for j, line in enumerate(kernel):
        kernel[j] = np.negative(line)
    kernel[15//2,15//2] = 280
    kernel = kernel/(np.sum(kernel))
    convoluted_rivet = cv2.filter2D(src=median_rivet, ddepth=-1, kernel=cv2.flip(kernel, -1), borderType=cv2.BORDER_ISOLATED, anchor=(7,7))
    
    # limiarização
    thresh_rivet = cv2.threshold(convoluted_rivet, 120, 255, cv2.THRESH_BINARY)[1]
    # cv2.imshow('[32] imagem rivet limiarizada', thresh_rivet)
    
    # abertura morfológico
    kernel = np.ones((3,3), np.uint8)
    open_rivet = cv2.morphologyEx(thresh_rivet, cv2.MORPH_OPEN, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)))
    # cv2.imshow('[32] imagem rivet fechamento', open_rivet)
    
    # remoção objetos das bordas
    pad = cv2.copyMakeBorder(open_rivet, 1,1,1,1, cv2.BORDER_CONSTANT, value=255)
    pad_h, pad_w = pad.shape
    border_mask = np.zeros([pad_h+2, pad_w+2], np.uint8)
    floodfill_rivet = cv2.floodFill(pad, border_mask, (0,0), 0, (5), (0), flags=8)[1]
    floodfill_rivet = floodfill_rivet[1:pad_h-1, 1:pad_w-1]
    # cv2.imshow('[33] imagem sem borda', floodfill_rivet)
    
    # fechamento morfológico
    kernel = np.ones((3,3), np.uint8)
    close_rivet = cv2.morphologyEx(floodfill_rivet, cv2.MORPH_CLOSE, kernel=cv2.getStructuringElement(cv2.MORPH_CROSS, ksize=(3,3)))
    # cv2.imshow('[32] imagem rivet fechamento', close_rivet)
    
    
    # filtro de partículas (pela area)
    number_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(close_rivet, 4, cv2.CV_32S)
    
    rivet_details = np.zeros(floodfill_rivet.shape, np.uint8)

    for n_label in range(1, number_labels):
        area = stats[n_label, cv2.CC_STAT_AREA]
        if 200 < area < 900:
            rivet_details[labels == n_label] = 255
    # cv2.imshow('[33] imagem com particulas da região de interesse filtradas pela sua área', rivet_details)
    
    
    # filtro de partículas (pela comprimento)
    number_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(rivet_details, 4, cv2.CV_32S)
        
    no_mark_circle = np.zeros(rivet_details.shape, np.uint8)
    
    for n_label in range(1, number_labels):
        width = stats[n_label, cv2.CC_STAT_WIDTH]
        if width < 58:
            no_mark_circle[labels == n_label] = 255
            
            
    return no_mark_circle