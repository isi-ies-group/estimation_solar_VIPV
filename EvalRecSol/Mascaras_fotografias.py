'''
---------------------------------------------------------------
--- LIBRERÍA - EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR ---
---       MÓDULO DE TRATAMIENTO MÁSCARAS DE IMAGENES        ---
---------------------------------------------------------------
'''
# Importa las librerias


import numpy as np
import cv2


# Función que procesa la máscara 1


def _mask_1(Foto):
    '''
    ---------------------------------
    --- Máscara 1 - Escalas color ---
    --------------------------------------------------------------------------

    La máscara que se aplicará en primer lugar es una que convierte la imagen 
    en una imagen en escala de grises, también extrae el color de azul de la 
    imagen original y se determinan los bordes de la imagen. Los bordes serán 
    considerados sombras (0) junto todos los valores que no se encuentran en 
    el rango de gris y azul preestalecido; el resto de los puntos serán cielo 
    (255).

    --------------------------------------------------------------------------

    Parámetros
    ----------
    Foto :
        Cadena de caracteres con el nombre de la imagen

    Devolución
    ----------
    img :
        Imagen con la máscara  

    '''
    
    # Apertura imagen
    imagen = cv2.imread(Foto)

    # Apertura imagen en escala de grises
    imagen_grey = cv2.imread(str(Foto), cv2.IMREAD_GRAYSCALE)

    # Bordes imagen
    img_bordes = cv2.Canny(imagen, 100, 200)

    # Matriz imagen en escala de color azul
    img_blue = np.array(imagen)[:, :, 0]

    # Matriz imagen
    img = np.array(imagen)[:, :, 0]

    # Conversor blanco y negro
    
    for i in range(len(img)):
        for j in range(len(img[i])):
            # Establecemos valores mínimos de la escala azul y escala de grises
            # para la determinación del cielo.
            if img_blue[i][j] > 197 and imagen_grey[i][j] > 129:
                img[i][j] = 255
            # Los bordes de la imagen se asignan como sombra.
            elif img_bordes[i][j] == 255:
                img[i][j] = 0
            # El resto de puntos se establecen como sombra.
            else:
                img[i][j] = 0

    # img = [[255 if (img_blue[i][j] > 197 and imagen_grey[i][j] > 129) else 0 if (img_bordes[i][j] == 255) else 0 for j in range(len(img[i]))]for i in range(len(img))]

    # Guarda la imagen de la máscara
    # cv2.imwrite('downloads\gsv_0_procesada1.jpg', img)

    return img


# Función que procesa la máscara 2


def _mask_2(Foto):
    '''
    ------------------------------
    --- Máscara 2 - Escala HSV ---
    --------------------------------------------------------------------------

    La máscara que se aplicará en segundo lugar convertirá la imagen a HSV, de 
    la cual se establecerán varios rangos de colores a extraer, 
    estableciéndolos como cielo (255); el resto de puntos serán sombras (0).

    --------------------------------------------------------------------------

    Parámetros
    ----------
    Foto :
        Cadena de caracteres con el nombre de la imagen

    Devolución
    ----------
    mask :
        Imagen con la máscara

    '''

    # Lectura de la imagen
    imagen = cv2.imread(Foto)

    # Convertir BGR a HSV
    hsv = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)

    # Definimos rangos de color en HSV de las máscaras
    # Máscara 1
    lower_blue1 = np.array([0, 0, 255])
    upper_blue1 = np.array([180, 180, 255])
    # Máscara 2
    lower_blue2 = np.array([85, 50, 150])
    upper_blue2 = np.array([180, 255, 255])
    # Máscara 3
    lower_blue3 = np.array([0, 0, 0])
    upper_blue3 = np.array([10, 255, 255])
    # Máscara 4
    lower_blue4 = np.array([85, 0, 209])
    upper_blue4 = np.array([110, 60, 255])

    # Umbral de la imagen HSV para definir ciertos colores
    mask1 = cv2.inRange(hsv, lower_blue1, upper_blue1)
    mask2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
    mask3 = cv2.inRange(hsv, lower_blue3, upper_blue3)
    mask4 = cv2.inRange(hsv, lower_blue4, upper_blue4)
    # Solapamos las 4 máscaras de colores en HSV
    mask = mask1 + mask2 + mask3 + mask4

    # Bit a bit y máscaras en la imagen original
    # res = cv2.bitwise_and(imagen,imagen, mask= mask)

    # Guarda la imagen de la máscara
    # cv2.imwrite('downloads\gsv_0_procesada2.jpg', mask)

    return mask


# Función que procesa la máscara 3


def _mask_3(Foto):
    '''
    ------------------------------------
    --- Máscara 3 - Contornos imagen ---
    --------------------------------------------------------------------------

    La máscara que se aplica en tercer lugar pasa la foto por el detector de 
    bordes y la rota. Procesando la foto, encuentra el primer borde por fila 
    estableciendo los valores anteriores como cielo (255) y los valores del 
    borde hasta el final de la fila como sombra (255). El proceso se repite 
    para cada fila de la imagen.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    Foto :
        Cadena de caracteres con el nombre de la imagen

    Devolución
    ----------
    img :
        Imagen con la máscara 

    '''

    # Lectura de la imagen
    imagen = cv2.imread(Foto)

    # Extracción de bordes
    img_bordes = cv2.Canny(imagen, 400, 1)

    # Cambio de colores, BGR a RGB
    imagen = cv2.cvtColor(img_bordes, cv2.COLOR_BGR2RGB)

    # Conversión a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_RGB2GRAY)

    # Obtención de imagen binaria
    _, binaria = cv2.threshold(gris, 225, 255, cv2.THRESH_BINARY_INV)

    # Detección de contornos
    contornos, _ = cv2.findContours(binaria, cv2.RETR_TREE,
                                    cv2.CHAIN_APPROX_SIMPLE)
    # Dibujo de los contornos definidos previamente
    imagen = cv2.drawContours(imagen, contornos, -1, (255, 255, 255), 2)

    # Paso a array de la imagen procesada
    imagen_array = np.array(imagen)[:, :, 0]

    # Inversión de los colores de la imagen al estar el cielo en negro y
    # la sombra en blanco.
    for i in range(len(imagen)):
        for j in range(len(imagen[i])):
            if imagen_array[i][j] == 0:
                imagen_array[i][j] = 255
            else:
                imagen_array[i][j] = 0

    # Rotación de la imagen 270 grados
    img_rot = cv2.rotate(imagen_array, cv2.ROTATE_90_COUNTERCLOCKWISE)

    # Eliminamos los bordes generados por borde de la imagen sin objetos
    for i in range(len(img_rot)-2):
        counter = 0
        for j in range(len(img_rot[i])-2):
            # Eliminamos los bordes de la propia imagen que ha sido detectados
            if i < 2 and j < 2 and img_rot[i+2][j+2] == 255:
                img_rot[i][j] = 255
            if counter < 2 and img_rot[i][j] == 0 and img_rot[i][j+2] == 255:
                img_rot[i][j] = 255
            # Filtramos pixeles en el cielo considerados sombras
            if img_rot[i][j] == 0 and img_rot[i+2][j] == 255 and i < 2:
                img_rot[i][j] = 255
            if i > (len(img_rot)-5) and counter < 2 and img_rot[i][j] == 255:
                img_rot[i+2][j] = 255
            # Contador de sombras por columnas
            if img_rot[i][j] == 0:
                counter += 1

    # Rellenado de los objetos
    for i in range(len(img_rot)-2):
        counter = 0
        for j in range(len(img_rot[i])-2):
            # Completa la columna de negro al haberse alcanzado el valor de
            # procesado del contador.
            if counter > 2 and img_rot[i][j] == 255:
                img_rot[i][j] = 0
            # Contador de sombras por columnas
            if img_rot[i][j] == 0:
                counter += 1

    # Rotación de la imagen 90 grados
    img = cv2.rotate(img_rot, cv2.ROTATE_90_CLOCKWISE)

    # Guarda la imagen de la máscara
    # cv2.imwrite('downloads\gsv_0_procesada3.jpg', img)

    return img


# Función que unifica las tres máscara


def mask_unica(foto):
    '''
    -------------------------
    --- Máscara combinada ---
    --------------------------------------------------------------------------

    Realizamos una unificación de las tres máscaras definidas anteriormente, 
    mediante la comprobación de si en dos máscaras es cielo (255) se 
    establecerá en la imagen como cielo y viceversa. Seguido por un suavizado 
    de los píxeles que puedan haber quedado solitarios.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    foto :
        Cadena de caracteres con el nombre de la imagen

    Devolución
    ----------
    copy2 :
        Imagen con las tres máscaras

    '''

    # Matrices de las imágenes con las diversas máscaras aplicadas
    mask1 = _mask_1(foto)
    mask2 = _mask_2(foto)
    mask3 = _mask_3(foto)
    # Estableciendo la máscara 1 como la principal y con la que trabajar
    triple_mask = mask1

    # Unificar mascaras
    for i in range(len(mask3)):
        for j in range(len(mask3[i])):
            contador = 0
            # Busqueda cielo en 1
            if mask1[i][j] > 120:
                contador += 1
            # Busqueda cielo en 2
            if mask2[i][j] > 120:
                contador += 1
            # Busqueda cielo en 3
            if mask3[i][j] > 120:
                contador += 1
            # Si se detectan en cada punto los valores de cielo en dos o más
            # máscaras, se establecerá en la principal como cielo (255).
            if contador > 1:
                triple_mask[i][j] = 255
            # Si se detectan en cada punto los valores de cielo en menos de
            # dos máscaras, se establecerá en la principal como sombra (0).
            if contador < 2:
                triple_mask[i][j] = 0

    # Guarda la imagen de la máscara
    # cv2.imwrite('downloads\gsv_0_procesada4.jpg', triple_mask)

    # Suavizamos la imagen mediante una media de un subconjunto de píxeles
    # Definimos el tamaño de los subconjuntos de los procesados
    offset = 1
    offset2 = 4
    # Establecemos el valor medio de color
    threshold = 255/2
    # Copiamos dos veces la unificación de la máscara para realizar los suavizados
    copy = np.copy(triple_mask)
    copy2 = np.copy(triple_mask)

    # Realizamos el proceso de suavizado por primera vez
    for x in range(triple_mask.shape[0]):
        for y in range(triple_mask.shape[1]):
            # Excluimos los valores que pretenezcan a los bordes del porcesado
            if x < offset or y < offset:
                continue
            else:
                # Hacemos la media de cada submatriz de píxeles y asignamos el .
                # valor predominante al píxel
                if triple_mask[x-offset:x+offset, y-offset:y+offset].mean() < threshold:
                    copy[x][y] = 0
                else:
                    copy[x][y] = 255

    # Realizamos el proceso de suavizado por segunda vez
    for x in range(copy.shape[0]):
        for y in range(copy.shape[1]):
            # Excluimos los valores que pretenezcan a los bordes del porcesado
            if x < offset2 or y < offset2:
                continue
            else:
                # Hacemos la media de cada submatriz de píxeles y asignamos el .
                # valor predominante al píxel
                if copy[x-offset2:x+offset2, y-offset2:y+offset2].mean() < threshold:
                    copy2[x][y] = 0
                else:
                    copy2[x][y] = 255

    # Guarda la imagen de la máscara
    # cv2.imwrite('downloads\gsv_0_procesada5.jpg', copy2)

    return copy2


# Función que aplica una máscara binaria de forma rápida


def mask_rapida(Foto):
    '''
    ----------------------
    --- Máscara rápida ---
    --------------------------------------------------------------------------

    Con la imagen en escala de grises, se le aplican transformaciones 
    morfológicas como la apertura (erosión + dilatación), junto con un 
    detector de contornos para contruir la máscara.

    --------------------------------------------------------------------------

    Parametros
    ----------
    Foto : str
        Nombre de la imagen a procesar.

    Returns
    -------
    close :
        Imagen con la máscara aplicada.

    '''

    # Lectura de la imagen
    image = cv2.imread(Foto)

    # Conversión de la imagen a escala de grises
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Umbral del procesado
    thresh = cv2.threshold(
        gray, 0, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C + cv2.THRESH_OTSU)[1]

    # Filtrado usando área de contornos y elimninando el ruido
    cnts = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 0.0005:
            cv2.drawContours(thresh, [c], -1, (0, 0, 0), -1)

    # Cierre morfológico e inversión de la imagen
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    close = 255 - cv2.morphologyEx(thresh,
                                   cv2.MORPH_CLOSE, kernel, iterations=5)

    # Guarda la imagen de la máscara
    # cv2.imwrite('downloads\gsv_0_procesada.jpg', close)

    return close
