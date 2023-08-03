'''
---------------------------------------------------------------
--- LIBRERÍA - EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR --- 
---             MÓDULO DE UTILIDADES GENERALES              ---
---------------------------------------------------------------
'''
# Importa las librerias


import cv2
from math import atan2, degrees
import numpy as np


# Muestra y guarda la imagen procesada


def _mostrar_resultado(img):
    '''
    ---------------------------
    --- Mostramos resultado ---
    --------------------------------------------------------------------------

    Mostraremos la imagen procesada en blanco y negro con el camino solar en 
    gris, guardandola en un archivo '.jpg'.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    img :
        Imagen como matriz

    '''

    # Mostrar la imagen
    cv2.imshow('Imagen procesada', img)
    # Guardar la imagen
    cv2.imwrite('downloads\gsv_0_procesada.jpg', img)


# Definimos la función para cerrar las ventanas abiertas


def _cierre_ventanas():
    '''
    ------------------------------
    --- Cierre de las ventanas ---
    --------------------------------------------------------------------------

    Para cerrar las ventanas abiertas, emplearemos las teclas 
     - 'ESCAPE'
     - 'SPACE'

    --------------------------------------------------------------------------
    '''

    # Detención de la ejecución al pulsar TECLA
    # ESCAPE --> (1048603) o ESPACIO --> (1048608)
    cv2.waitKey(1048603 or 1048608)
    # Cierre de la ventana
    cv2.destroyAllWindows()


# Función para obtener clave de la API de Google


def obtener_clave_API(nombre):
    '''
    ---------------------------------
    --- Obtención clave de '.txt' ---
    --------------------------------------------------------------------------

    Le pasamos el nombre del archivo que almacena la clave de la API de 
    Google, devolviendo su valor.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    nombre :
        Cadena de caracteres del archivo con la contraseña

    Devolución
    ----------
    clave:
        Cadena de caracteres de la contraseña  

    '''

    # Abrimos 'nombre.txt'
    archivo = open(nombre, 'r')

    # Leemos la clave
    clave = archivo.read()

    # Cerramos el archivo
    archivo.close()

    # Devolvemos la contraseña
    return clave


# Función que obtiene el rumbo entre dos coordenadas


def _angulo_entre_dos_coordenadas(p1, p2):
    '''
    -----------------------------------
    --- Rumbo entre dos coordenadas ---
    --------------------------------------------------------------------------

    Función que  pasando las coordenadas de dos puntos del mapa, devuelve el 
    ángulo que conforman los dos puntos.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    p1 :
        Vector bidimensional con las coordenadas del punto origen
    p2 :
        Vector bidimensional con las coordenadas del punto final

    Devolución
    ----------
    direccion :
        Ángulo formado por los puntos origen y final  

    '''

    # Diferencia en el eje X
    xDiff = p2[0] - p1[0]

    # Diferencia en el eje Y
    yDiff = p2[1] - p1[1]

    # Calculamos el ángulo entre los puntos
    direccion = (degrees(atan2(yDiff, xDiff))) % 360

    # Devolvemos el ángulo
    return direccion


# Función que convierte los píxeles a coordenadas polares


def _pixel_a_polares(x, y, foto, ang_c, direccion):
    '''
    -------------------------------------------------
    ---- Conversor píxeles a coordenadas polares ----
    --------------------------------------------------------------------------

    Queremos conocer las coordenadas locales de la fotografía en función de la 
    orientación de la imagen y del pixel en el que nos encontramos mediante 
    una función.

    Azimuth = -{ Ángulo horizontal de la cámara * 
                (-0.5 + Pixel hotizontal / Dimensión horizontal de la imagen) 
                - Dirección lente referenciada a sur }

    Donde --> Sur (0°), Este (90°), Norte (180°) y Oeste (270°)

    Altitud = Ángulo vertical de la cámara * 
                { 1 - Pixel vertical / Dimensión vertical de la imagen }

    --------------------------------------------------------------------------

    Parámetros
    ----------
    x :
        Valor horizontal del punto
    y :
        Valor valor vertical del punto
    foto :
        Imagen con la que trabajar
    ang_c :
        Ángulo de la cámara empleada
    direccion :
        Dirección central de la lente


    Devolución
    ----------
    coord :
        Vector bidimensional con las coordenadas del azimuth y 
        la elevación solar

    '''

    # Dirección se refiere al rumbo del centro de la imagen -->
    # Sur (0°), Este(90°), Norte (180°) y Oeste (270°)

    direccion %= 360

    # Cálculo del azimuth
    azimuth = -(ang_c[0]*(- 0.5 + x/len(foto)) - direccion)

    # Basado en funcionamiento de una 'brújula antihoraria' pero
    # fijando el 0° al Sur y manteniendo los valores comprendidos entre
    # 0 y 360 grados.
    if azimuth > 360:
        azimuth -= 360
    if azimuth < 0:
        azimuth += 360
    if azimuth == 360 or azimuth == 0:
        azimuth = 0

    # Cálculo de la elevación solar
    altitud = ang_c[1]*(1-(y/len(foto[0])))

    coord = [azimuth, altitud]
    return coord


# Función que convierte las coordenadas polares a píxeles


def _polares_a_pixel(azi, el_s, img, ang_c, dirr):
    '''
    -------------------------------------------------
    ---- CONVERSOR COORDENADAS POLARES A PIXELES ----
    --------------------------------------------------------------------------

    Queremos conocer las coordenadas de los píxeles de la fotografía en 
    función de la orientación de la imagen y de las coordenadas locales en el 
    que nos encontramos mediante una función.

    Pixel vertical = Dimensión vertical de la imagen * 
                        ( 1 - Altitud / Campo de visión vertical )

    Pixel horizontal = Dimensión horizontal de la imagen * 
                        { 1 - ( Azimuth - Dirección referenciada al sur ) / 
                             Campo de visión horizontal de la cámara + 0.5 } 

        para el caso general que puede cambiar para poder estar siempre 
        referenciados los valores entre 0 y 360 grados.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    azi :
        Valor polar del azimuth
    el_s :
        Valor polar de la elevación solar
    img :
        Imagen con la que trabajar
    ang_c :
        Ángulo de la cámara empleada
    dirr :
        Dirección central de la lente

    Devolución
    ----------
    pixel :
        Vector bidimensional con las coordenadas vertical y horizontal

    '''

    dirr %= 360

    # Coordenada X del píxel - Vertical
    x = len(img)*(1 - (el_s/ang_c[1]))

    # Coordenada Y del píxel - Horizontal
    # Consideramos valores para los casos límites al ser posible la ubicación
    # de píxeles encontarse en valores por debajo de 0 grados o por encima de
    # 360 grados y querer que esten comprendidos entre 0 y 360 grados.
    if dirr >= 315 or dirr < 45:
        if dirr >= 315 and azi < (dirr - ang_c[0]):
            y = len(img[0])*(1-(azi + 360-((dirr-ang_c[0]/2) % 360))/ang_c[0])
        elif dirr < 45 and azi > (dirr + ang_c[0]):
            y = len(img[0])*(1-(azi - ((dirr-ang_c[0]/2) % 360))/ang_c[0])
        else:
            y = len(img[0])*(1 - ((azi - dirr) / ang_c[0] + 0.5))
    # El caso general para la obtención de la componente horizontal
    else:
        y = len(img[0])*(1 - ((azi - dirr) / ang_c[0] + 0.5))

    pixel = [int(x), int(y)]
    return pixel


# Función que calcula el punto y en una recta a partir de un punto x


def _f(x, x0, y0, x1, y1):
    '''
    -----------------------------------------------------------
    --- Ecuación de la recta que pasa por (x0,y0) y (x1,y1) ---
    --------------------------------------------------------------------------

    Devuelve el valor de y para un punto que perteneciente a una recta entre
    dos coordenadas predefinidas a partir de un punto x.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    x :
        Valor X del punto a determinar
    x0 :
        Valor X del punto origen
    y0 :
        Valor Y del punto origen
    x1 :
        Valor X del punto destinio
    y1 :
        Valor Y del punto destino

    Devolución
    ----------
    y :
        Valor Y del punto a determinar

    '''

    y = (y1-y0) / (x1-x0) * (x-x0) + y0

    return y


# Función que obtiene los puntos intermedios entre dos coordenadas


def _puntos_intermedios(origen, fin, distancia, separacion = 10):
    '''
    ---------------------------------------
    --- Puntos intermedios de una recta ---
    --------------------------------------------------------------------------

    Introduciendo las coordenadas de dos puntos y la distancia en km entre
    ambos puntos, obtiene puntos intermedios con una separación variable en
    metros.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    origen : 
        Vector con las coordenadas del punto inicial
    fin :
        Vector con las coordenadas del punto final
    distancia :
        Distancia entre el punto inicial y final en metros
    separacion :
        Distancia entre los puntos a generar en metros, estableciendo como
        predeterminada a 10 metros

    Devolución
    ----------
    x :
        Vector de valores en X
    y :
        Vector de valores en Y

    '''

    segmentos = int((distancia) // separacion)
    x = np.linspace(origen[0], fin[0], num=segmentos)
    y = _f(x, *origen, *fin)

    return x, y


# Función que pasa DataFrame a hoja de cálculo Excel '.xlsx'


def a_hoja_excel(EstructuraDatos, nombre, posicion = -1):
    '''
    -------------------------
    --- DataFrame a Excel ---
    --------------------------------------------------------------------------

    Introduciendo la lista de DataFrames o el único DataFrame y el nombre del
    archivo donde queremos almacenar la estructura de datos, generaremos un
    documento '.xlsx' para guardar los valores de la ejecución o emplearlos
    en la aplicación de Google Maps.
    
    --------------------------------------------------------------------------

    Parámetros
    ----------
    EstructuraDatos : list o DataFrame
        Lista con DataFrames o DataFrame con las rutas de coordenadas, fecha y 
        hora, energías ...
    nombre : str
        Nombre del archivo donde se guardará.
    posicion : int, opcional
        Posición de la ruta en la lista. El valor por defecto es -1, caso que
        ocurre si se pasa un DataFrame y no una lista de DataFrame.

    Devolución
    ----------
    Nada.

    '''
    if posicion == -1:
        EstructuraDatos.to_excel(str(nombre)+'.xlsx', index = False, header = True)

    else:    
        EstructuraDatos[posicion].to_excel(str(nombre)+'.xlsx', index = False, header = True)
