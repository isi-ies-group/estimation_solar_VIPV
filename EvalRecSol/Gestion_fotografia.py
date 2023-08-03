'''
---------------------------------------------------------------
--- LIBRERÍA - EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR --- 
---             MÓDULO DE GESTIÓN DE IMÁGENES               ---
---------------------------------------------------------------
'''
# Importa las librerias


import google_streetview.api
import cv2
import math


# Función para obtner la imagen de Street View


def _obtencion_foto_SW (params):
    '''
    -------------------
    --- Street View ---
    --------------------------------------------------------------------------

    Se crea una estructura de datos con lo valores necesarios para obtener la 
    imagen de la API de Google Street View. Definimos una función que nos 
    guarda la imagen y varios archivos con información de la misma, 
    ejecuntándola inmediatamente después su definición.

    # Define parametros para Google Street View api
    params = [{
      # Ejemplo URL de una foto
      # https://maps.googleapis.com/maps/api/streetview?size=640x640&location=40.42046557,-3.68617543&fov=90&heading=0&pitch=37.5&key=key
      'size': tamaño, # Tamaño imagen - max 640x640 pixels
      'location': localizacion, # Coordenadas polares
      'heading': rumbo, # Orientación N(0), E(90), S(180), O(270)
      'pitch': inclinacion, # Inclinación lente
      'fov' : campo_visual_H, # Campo de visión horizontal
      'key': 'clave'
    }]

    --------------------------------------------------------------------------

    Parámetros
    ----------
    params :
        Estructura de valores necesarios para la API de Google Street View

    '''

    # Crea un objeto con el resultado
    results = google_streetview.api.results(params)

    # Resultados de la vista previa
    results.preview()

    # Guarda imagen en la carpeta 'downloads'
    results.download_links('downloads')

    # Guarda los links del objeto
    results.save_links('links.txt')

    # Guarda la metadata del objeto
    results.save_metadata('metadata.json')


# Función 'mostrar_foto_SW()'


def _get_path_foto():
    '''
    --------------------------------
    --- Lectura de la fotografía ---
    --------------------------------------------------------------------------

    Devuelve el nombre de la imagen generada por la API de Street View, con 
    opción de descomentar que se muetre la imagen.

    --------------------------------------------------------------------------

    Devolución
    ----------
    Foto :
        Cadena de caracteres con el nombre de la imagen de la API de 
        Google Street View

    '''

    # Carga de la fotografía de Street View
    Foto = 'downloads\gsv_0.jpg'

    # Mostrar foto de Street View
    # cv2.imshow('Imagen', cv2.imread(Foto))

    return Foto


# Función para obtener el ángulo de la cámara


def _angulo_camara(orientacion, campo_visual_H):
    '''
    --------------------------------------
    ---- Campo de visión de la cámara ----
    --------------------------------------------------------------------------

    Definimos una función que dependiendo del parámetro introducido, 
    obtendremos el campo de visión horizontal y vertical de la cámara 
    referenciado a la posición de la cámara. Si el parámetro es 'V' o 'H', se 
    empleará el campo de visión generado por la cámara de un iPhone SE de 
    2016; sin embargo, cualquier otro valor nos devolverá el campo de visión 
    de la imagen generada por la API de Google Street View. Ejecutandolo con 
    'SV' para que sean los valores de la API.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    orientacion :
        Valor angular del centro de la imagen 
    campo_visual_H :
        Valor angular del campo de visión horizontal

    Devolución
    ----------
    aw :
        Vector bidimensional con los campos de visión de la imagen

    '''

   # Campo de visión de la cámara

    # Cámara iPhone SE - 2016
    focale_length = 4  # Distancia focal [mm] - 4 mm (28 mm de ef) 8 mm
    sensor_width = 4.8  # Ancho sensor [mm]
    sensor_length = 3.6  # Alto sensor [mm]

    # Campo de visión = 2 · atan(dimensión sensor / (2·distancia focal))

    # Considerando que la posición de la cámara es horizontal
    angle_of_view_horizontal = math.degrees(
        2 * math.atan(sensor_width / (2 * focale_length)))
    angle_of_view_vertical = math.degrees(
        2 * math.atan(sensor_length / (2 * focale_length)))
    aw_posH = [angle_of_view_horizontal, angle_of_view_vertical]

    # Considerando que la posición de la cámara es vertical
    aw_v = angle_of_view_horizontal
    aw_h = angle_of_view_vertical
    aw_posV = [aw_h, aw_v]

    # Orientación de la cámara vertical (V) ó horizontal (H) o Street View (SW)
    if orientacion.upper() == 'H':
        # print('\nPosición cámara horizontal\n - Ángulo de visión horizontal: %0.2f°\n - Ángulo de visión vertical: %0.2f°' % (aw_posH[0], aw_posH[1]))
        return aw_posH

    elif orientacion.upper() == 'V':
        # print('\nPosición cámara vertical\n - Ángulo de visión horizontal: %0.2f°\n - Ángulo de visión vertical: %0.2f°' % (aw_h, aw_v), '\n')
        return aw_posV

    else:
        # Cámara Street View
        aw_SW = [campo_visual_H, campo_visual_H]
        # print('\nPosición de la cámara de Street View\n - Ángulo de visión horizontal: %0.2f°\n - Ángulo de visión vertical: %0.2f°' % (aw_SW[0], aw_SW[1]))
        return aw_SW


# Función que imprime las dimensiones de la fotografía


def _dimensiones_imagen(imagen):
    '''
    --------------------------------
    ---- Dimensiones fotografía ----
    --------------------------------------------------------------------------

    Para conocer las dimensiones de la imagen, empleamos una función que las 
    imprime por pantalla. Ejecutándola después.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    imagen :
        Cadena de caracteres con el nombre de la imagen

    '''

    foto = cv2.imread(imagen, 1)
    print('\n Dimensiones de la imagen')
    print(' - Largo de la imagen: ', foto.shape[0], 'píxeles')  # Lado largo
    print(' - Ancho de la imagen: ', foto.shape[1], 'píxeles\n')  # Lado corto
