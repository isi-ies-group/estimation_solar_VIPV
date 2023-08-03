# -*- coding: utf-8 -*-

import cv2
import numpy as np


def _mask_1(Foto):


    imagen = cv2.imread(Foto)

    imagen_grey = cv2.imread(Foto, cv2.IMREAD_GRAYSCALE)

    img_bordes = cv2.Canny(imagen, 100, 200)

    img_blue = np.array(imagen)[:, :, 0]


    img = np.array(imagen)[:, :, 0]


    for i in range(len(img)):
        for j in range(len(img[i])):
            if img_blue[i][j] > 197 and imagen_grey[i][j] > 129:
                img[i][j] = 255

            elif img_bordes[i][j] == 255:
                img[i][j] = 0
            else:
                img[i][j] = 0

    return img


def _mask_2(Foto):

    imagen = cv2.imread(Foto)


    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    lower_blue1 = np.array([0, 0, 255])
    upper_blue1 = np.array([180, 180, 255])

    lower_blue2 = np.array([85, 50, 150])
    upper_blue2 = np.array([180, 255, 255])

    lower_blue3 = np.array([0, 0, 0])
    upper_blue3 = np.array([10, 255, 255])

    lower_blue4 = np.array([85, 0, 209])
    upper_blue4 = np.array([110, 60, 255])


    mask1 = cv2.inRange(hsv, lower_blue1, upper_blue1)
    mask2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    mask3 = cv2.inRange(hsv, lower_blue3, upper_blue3)
    mask4 = cv2.inRange(hsv, lower_blue4, upper_blue4)

    mask = mask1 + mask2 + mask3 + mask4


    return mask



def _mask_3(Foto):


    imagen = cv2.imread(Foto)
    img_bordes = cv2.Canny(imagen, 400, 1)
    imagen = cv2.cvtColor(img_bordes, cv2.COLOR_BGR2RGB)


    gris = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)

    _, binaria = cv2.threshold(gris, 225, 255, cv2.THRESH_BINARY_INV)

    contornos, _ = cv2.findContours(binaria, cv2.RETR_TREE,
                                    cv2.CHAIN_APPROX_SIMPLE)

    imagen = cv2.drawContours(imagen, contornos, -1, (255, 255, 255), 2)


    imagen_array = np.array(imagen)[:, :, 0]

    for i in range(len(imagen)):
        for j in range(len(imagen[i])):
            if imagen_array[i][j] == 0:
                imagen_array[i][j] = 255
            else:
                imagen_array[i][j] = 0


    img_rot = cv2.rotate(imagen_array, cv2.ROTATE_90_COUNTERCLOCKWISE)


    for i in range(len(img_rot)-2):
        counter = 0
        for j in range(len(img_rot[i])-2):

            if i < 2 and j < 2 and img_rot[i+2][j+2] == 255:
                img_rot[i][j] = 255
            if counter < 2 and img_rot[i][j] == 0 and img_rot[i][j+2] == 255:
                img_rot[i][j] = 255

            if img_rot[i][j] == 0 and img_rot[i+2][j] == 255 and i < 2:
                img_rot[i][j] = 255
            if i > (len(img_rot)-5) and counter < 2 and img_rot[i][j] == 255:
                img_rot[i+2][j] = 255

            if img_rot[i][j] == 0:
                counter += 1

    for i in range(len(img_rot)-2):
        counter = 0
        for j in range(len(img_rot[i])-2):
            if counter > 2 and img_rot[i][j] == 255:
                img_rot[i][j] = 0

            if img_rot[i][j] == 0:
                counter += 1

    img = cv2.rotate(img_rot, cv2.ROTATE_90_CLOCKWISE)


    return img


def mask_unica(foto):

    mask1 = _mask_1(foto)
    mask2 = _mask_2(foto)
    mask3 = _mask_3(foto)

    triple_mask = mask1

    for i in range(len(mask3)):
        for j in range(len(mask3[i])):
            contador = 0

            if mask1[i][j] > 120:
                contador += 1

            if mask2[i][j] > 120:
                contador += 1

            if mask3[i][j] > 120:
                contador += 1
            if contador > 1:
                triple_mask[i][j] = 255
            if contador < 2:
                triple_mask[i][j] = 0

    offset = 1
    offset2 = 4

    threshold = 255/2

    copy = np.copy(triple_mask)
    copy2 = np.copy(triple_mask)


    for x in range(triple_mask.shape[0]):
        for y in range(triple_mask.shape[1]):

            if x < offset or y < offset:
                continue
            else:
                if triple_mask[x-offset:x+offset, y-offset:y+offset].mean() < threshold:
                    copy[x][y] = 0
                else:
                    copy[x][y] = 255


    for x in range(copy.shape[0]):
        for y in range(copy.shape[1]):

            if x < offset2 or y < offset2:
                continue
            else:
                if copy[x-offset2:x+offset2, y-offset2:y+offset2].mean() < threshold:
                    copy2[x][y] = 0
                else:
                    copy2[x][y] = 255

    return copy2