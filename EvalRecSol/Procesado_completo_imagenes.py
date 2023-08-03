'''
---------------------------------------------------------------
--- LIBRERÍA - EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR --- 
---           MÓDULO DE PROCESADO COMPLETO IMAGENES         ---
---------------------------------------------------------------
'''
# Importa las librerias


import pandas as pd
import numpy as np
from EvalRecSol import Gestion_fotografia as g_f
from EvalRecSol import Camino_solar as c_s
from EvalRecSol import Irradiancia as i
from EvalRecSol import Mascaras_fotografias as m_f
import cv2


# Función que hace el completo procesado de la imagen


def _proceso_imagen(params, site, direccion, inicio, fin, periodo,
                    inclinacion_modulo, rumbo, save=0):
    '''
    -------------------------------
    --- Proceso completo imagen ---
    --------------------------------------------------------------------------

    Obtiene la foto de la API de Street View, aplica las tres máscaras a la 
    imagen y su posterior unificación; se aplica la función que obtiene el 
    camino solar prosiguiendo con la obtención de la irradiancia de los puntos 
    del camino. Devolviendo la imagen procesada, la estructura de datos del 
    camino solar y de la irradiancia junto con el nombre de la fotografía de 
    la API.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    params :
        Fichero requerido para API de Google Street View
    site :
        Datos referentes a la ubicación, latitud, longitud y zona horaria
    direccion :
        Orientación del centro de la imagen en coordenadas anti-brújula
    inicio :
        Intante de tiempo inicio
    fin :
        Instante de tiempo fin
    periodo :
        Paso de tiempo entre los puntos del camino solar
    inclinacion_modulo :
        Inclinación del módulo fotovoltaico
    rumbo :
        Orientación del centro de la imagen en coordenadas brújula
    save :
        Variable que guarda las imágenes original y procesada si tiene un 
        valor distinto a cero

    Devolución
    ----------
    img :
        Matrix de valores de la imagen en binario
    puntosSol :
        Estructura de datos con los puntos del camino solar
    irradiancia_dia :
        Estructura de datos con las irradiancias del camino solar
    Foto :
        Cadena de caracteres con el nombre de la imagen de la API de
        Google Street View

    '''

    # LLamada a la función para obtener la imagen de Street View
    g_f._obtencion_foto_SW(params)

    # LLamada a la función para ver la imagen de Street View
    Foto = g_f._get_path_foto()

# Guardamos la imagen original
    if save == 1:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_E_original.jpg', cv2.imread(Foto))
    elif save == 2:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SE_original.jpg', cv2.imread(Foto))
    elif save == 3:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_S_original.jpg', cv2.imread(Foto))
    elif save == 4:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SO_original.jpg', cv2.imread(Foto))
    elif save == 5:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_O_original.jpg', cv2.imread(Foto))

    # Ejecutamos la función que muestra las dimensiones de la fotografía
    # dimensiones_imagen(Foto)

    # Ejecutamos la función que obtiene el camino del Sol en una imagen
    img, puntosSol = c_s.caminoSolar(m_f.mask_unica(Foto), site, direccion,
                                     inicio, fin, periodo)

    # Empleamos la función para obtener los datos a una inclinación determinada
    # y con la orientación de la foto
    irradiancia_dia = i._get_irradiance(site, inicio, periodo,
                                        inclinacion_modulo, rumbo,
                                        np.array(puntosSol['Fecha y hora']),
                                        puntosSol)

    # Guardamos la imagen procesada
    if save == 1:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_E_procesada.jpg', img)

    elif save == 2:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SE_procesada.jpg', img)

    elif save == 3:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_S_procesada.jpg', img)

    elif save == 4:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SO_procesada.jpg', img)

    elif save == 5:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_O_procesada.jpg', img)

    return img, puntosSol, irradiancia_dia, Foto


# Función que procesa el camino solar de Este a Oeste


def de_Este_a_Oeste(params, site, direccion, inicio, fin, periodo,
                    inclinacion_modulo, save=False):
    '''
    ---------------------------------
    --- Procesado de Este a Oeste ---
    --------------------------------------------------------------------------

    Procesa cinco imágenes (Este, Sureste, Sur, Suroeste, Oeste) con un 
    procesado completo de cada una de las fotos, guardando cada una con su 
    camino solar representado sobre la imagen de la API. Para finalizar 
    unifica las cinco estructuras de en una única, devolviendo la unificación 
    de las estructuras.  

    --------------------------------------------------------------------------

    Parámetros
    ----------
    params :
       Fichero requerido para API de Google Street View 
    site :
        Datos referentes a la ubicación, latitud, longitud y zona horaria
    direccion :
        Orientación del centro de la imagen en coordenadas anti-brújula
    inicio :
        Intante de tiempo inicio
    fin :
        Instante de tiempo fin
    periodo :
        Paso de tiempo entre los puntos del camino solar
    inclinacion_modulo :
        Inclinación del módulo fotovoltaico
    save :
        Variable que guarda las imágenes original y procesada de cada 
        procesado si es True

    Devolución
    ----------
    PuntosSol :
           Estructura de datos de los puntos del camino solar en una ubicación

    '''
    if save == False:

        # Orientación Este
        params[0]['heading'] = 90
        direccion = (180 - 90) % 360
        img_E, puntosSol_E, irradiancia_dia_E, Foto_E = _proceso_imagen(params, site,
                                                                        direccion, inicio,
                                                                        fin, periodo,
                                                                        inclinacion_modulo,
                                                                        90)
        c_s._camino_en_imagenSV_multiple(puntosSol_E, Foto_E, 'E', '1')

        # Orientación Sur - Este
        params[0]['heading'] = 135
        direccion = (180 - 135) % 360
        img_SE, puntosSol_SE, irradiancia_dia_SE, Foto_SE = _proceso_imagen(params, site,
                                                                            direccion, inicio,
                                                                            fin, periodo,
                                                                            inclinacion_modulo,
                                                                            135)
        c_s._camino_en_imagenSV_multiple(puntosSol_SE, Foto_SE, 'SE', '2')

        # Orientación Sur
        params[0]['heading'] = 180
        direccion = (180 - 180) % 360
        img_S, puntosSol_S, irradiancia_dia_S, Foto_S = _proceso_imagen(params, site,
                                                                        direccion, inicio,
                                                                        fin, periodo,
                                                                        inclinacion_modulo,
                                                                        180)
        c_s._camino_en_imagenSV_multiple(puntosSol_S, Foto_S, 'S', '3')

        # Orientación Sur - Oeste
        params[0]['heading'] = 225
        direccion = (180 - 225) % 360
        img_SO, puntosSol_SO, irradiancia_dia_SO, Foto_SO = _proceso_imagen(params, site,
                                                                            direccion, inicio,
                                                                            fin, periodo,
                                                                            inclinacion_modulo,
                                                                            225)
        c_s._camino_en_imagenSV_multiple(puntosSol_SO, Foto_SO, 'SO', '4')

        # Orientación Oeste
        params[0]['heading'] = 270
        direccion = (180 - 270) % 360
        img_O, puntosSol_O, irradiancia_dia_O, Foto_O = _proceso_imagen(params, site,
                                                                        direccion, inicio,
                                                                        fin, periodo,
                                                                        inclinacion_modulo,
                                                                        270)
        c_s._camino_en_imagenSV_multiple(puntosSol_O, Foto_O, 'O', '5')

    else:

        # Orientación Este
        params[0]['heading'] = 90
        direccion = (180 - 90) % 360
        img_E, puntosSol_E, irradiancia_dia_E, Foto_E = _proceso_imagen(params, site,
                                                                        direccion, inicio,
                                                                        fin, periodo,
                                                                        inclinacion_modulo,
                                                                        90, 1)
        c_s._camino_en_imagenSV_multiple(puntosSol_E, Foto_E, 'E', '1')

        # Orientación Sur - Este
        params[0]['heading'] = 135
        direccion = (180 - 135) % 360
        img_SE, puntosSol_SE, irradiancia_dia_SE, Foto_SE = _proceso_imagen(params, site,
                                                                            direccion, inicio,
                                                                            fin, periodo,
                                                                            inclinacion_modulo,
                                                                            135, 2)
        c_s._camino_en_imagenSV_multiple(puntosSol_SE, Foto_SE, 'SE', '2')

        # Orientación Sur
        params[0]['heading'] = 180
        direccion = (180 - 180) % 360
        img_S, puntosSol_S, irradiancia_dia_S, Foto_S = _proceso_imagen(params, site,
                                                                        direccion, inicio,
                                                                        fin, periodo,
                                                                        inclinacion_modulo,
                                                                        180, 3)
        c_s._camino_en_imagenSV_multiple(puntosSol_S, Foto_S, 'S', '3')

        # Orientación Sur - Oeste
        params[0]['heading'] = 225
        direccion = (180 - 225) % 360
        img_SO, puntosSol_SO, irradiancia_dia_SO, Foto_SO = _proceso_imagen(params, site,
                                                                            direccion, inicio,
                                                                            fin, periodo,
                                                                            inclinacion_modulo,
                                                                            225, 4)
        c_s._camino_en_imagenSV_multiple(puntosSol_SO, Foto_SO, 'SO', '4')

        # Orientación Oeste
        params[0]['heading'] = 270
        direccion = (180 - 270) % 360
        img_O, puntosSol_O, irradiancia_dia_O, Foto_O = _proceso_imagen(params, site,
                                                                        direccion, inicio,
                                                                        fin, periodo,
                                                                        inclinacion_modulo,
                                                                        270, 5)
        c_s._camino_en_imagenSV_multiple(puntosSol_O, Foto_O, 'O', '5')

    # Concatenamos los valores de las diversas fotos
    PuntosSol = pd.concat([puntosSol_E, puntosSol_SE, puntosSol_S,
                           puntosSol_SO, puntosSol_O],
                          keys=["E", "SE", "S", "SO", "O"])

    return PuntosSol


# Función que hace el completo procesado de la imagen rápidamente


def _proceso_imagen_rapido(params, site, direccion, inicio, fin, periodo,
                           inclinacion_modulo, rumbo, save=0):
    '''
    --------------------------------------
    --- Proceso completo imagen rápido ---
    --------------------------------------------------------------------------

    Obtiene la foto de la API de Street View, aplica las tres máscaras a la 
    imagen y su posterior unificación; se aplica la función que obtiene el 
    camino solar prosiguiendo con la obtención de la irradiancia de los puntos 
    del camino. Devolviendo la imagen procesada, la estructura de datos del 
    camino solar y de la irradiancia junto con el nombre de la fotografía de 
    la API.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    params :
        Fichero requerido para API de Google Street View
    site :
        Datos referentes a la ubicación, latitud, longitud y zona horaria
    direccion :
        Orientación del centro de la imagen en coordenadas anti-brújula
    inicio :
        Intante de tiempo inicio
    fin :
        Instante de tiempo fin
    periodo :
        Paso de tiempo entre los puntos del camino solar
    inclinacion_modulo :
        Inclinación del módulo fotovoltaico
    rumbo :
        Orientación del centro de la imagen en coordenadas brújula
    save :
        Variable que guarda las imágenes original y procesada si tiene un 
        valor distinto a cero

    Devolución
    ----------
    img :
        Matrix de valores de la imagen en binario
    puntosSol :
        Estructura de datos con los puntos del camino solar
    irradiancia_dia :
        Estructura de datos con las irradiancias del camino solar
    Foto :
        Cadena de caracteres con el nombre de la imagen de la API de
        Google Street View

    '''

    # LLamada a la función para obtener la imagen de Street View
    g_f._obtencion_foto_SW(params)

    # LLamada a la función para ver la imagen de Street View
    Foto = g_f._get_path_foto()

    # Guardamos la imagen original
    if save == 1:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_E_original_fast.jpg', cv2.imread(Foto))
    elif save == 2:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SE_original_fast.jpg', cv2.imread(Foto))
    elif save == 3:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_S_original_fast.jpg', cv2.imread(Foto))
    elif save == 4:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SO_original_fast.jpg', cv2.imread(Foto))
    elif save == 5:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_O_original_fast.jpg', cv2.imread(Foto))

    # Ejecutamos la función que muestra las dimensiones de la fotografía
    # dimensiones_imagen(Foto)

    # Ejecutamos la función que obtiene el camino del Sol en una imagen
    img, puntosSol = c_s.caminoSolar(m_f.mask_rapida(Foto), site, direccion,
                                     inicio, fin, periodo)

    # Empleamos la función para obtener los datos a una inclinación determinada
    # y con la orientación de la foto
    irradiancia_dia = i._get_irradiance(site, inicio, periodo,
                                        inclinacion_modulo, rumbo,
                                        np.array(puntosSol['Fecha y hora']),
                                        puntosSol)

    # Guardamos la imagen procesada
    if save == 1:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_E_procesada_fast.jpg', img)
    elif save == 2:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SE_procesada_fast.jpg', img)
    elif save == 3:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_S_procesada_fast.jpg', img)
    elif save == 4:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_SO_procesada_fast.jpg', img)
    elif save == 5:
        cv2.imwrite('downloads\_' + str(site.latitude) + '_' +
                    str(site.longitude) + '_O_procesada_fast.jpg', img)

    return img, puntosSol, irradiancia_dia, Foto


# Función que procesa el camino solar de Este a Oeste rápidamente


def de_Este_a_Oeste_rapido(params, site, direccion, inicio, fin, periodo,
                           inclinacion_modulo, save=False):
    '''
    ----------------------------------------
    --- Procesado de Este a Oeste rápido ---
    --------------------------------------------------------------------------

    Procesa cinco imágenes (Este, Sureste, Sur, Suroeste, Oeste) con un 
    procesado completo de cada una de las fotos, guardando cada una con su 
    camino solar representado sobre la imagen de la API. Para finalizar 
    unifica las cinco estructuras de en una única, devolviendo la unificación 
    de las estructuras.  

    --------------------------------------------------------------------------

    Parámetros
    ----------
    params :
       Fichero requerido para API de Google Street View 
    site :
        Datos referentes a la ubicación, latitud, longitud y zona horaria
    direccion :
        Orientación del centro de la imagen en coordenadas anti-brújula
    inicio :
        Intante de tiempo inicio
    fin :
        Instante de tiempo fin
    periodo :
        Paso de tiempo entre los puntos del camino solar
    inclinacion_modulo :
        Inclinación del módulo fotovoltaico
    save :
        Variable que guarda las imágenes original y procesada de cada 
        procesado si es True

    Devolución
    ----------
    PuntosSol :
           Estructura de datos de los puntos del camino solar en una ubicación

    '''
    if save == False:

        # Orientación Este
        params[0]['heading'] = 90
        direccion = (180 - 90) % 360
        img_E, puntosSol_E, irradiancia_dia_E, Foto_E = _proceso_imagen_rapido(params, site,
                                                                               direccion, inicio,
                                                                               fin, periodo,
                                                                               inclinacion_modulo,
                                                                               90)
        c_s._camino_en_imagenSV_multiple(puntosSol_E, Foto_E, 'E', '1')

        # Orientación Sur - Este
        params[0]['heading'] = 135
        direccion = (180 - 135) % 360
        img_SE, puntosSol_SE, irradiancia_dia_SE, Foto_SE = _proceso_imagen_rapido(params, site,
                                                                                   direccion, inicio,
                                                                                   fin, periodo,
                                                                                   inclinacion_modulo,
                                                                                   135)
        c_s._camino_en_imagenSV_multiple(puntosSol_SE, Foto_SE, 'SE', '2')

        # Orientación Sur
        params[0]['heading'] = 180
        direccion = (180 - 180) % 360
        img_S, puntosSol_S, irradiancia_dia_S, Foto_S = _proceso_imagen_rapido(params, site,
                                                                               direccion, inicio,
                                                                               fin, periodo,
                                                                               inclinacion_modulo,
                                                                               180)
        c_s._camino_en_imagenSV_multiple(puntosSol_S, Foto_S, 'S', '3')

        # Orientación Sur - Oeste
        params[0]['heading'] = 225
        direccion = (180 - 225) % 360
        img_SO, puntosSol_SO, irradiancia_dia_SO, Foto_SO = _proceso_imagen_rapido(params, site,
                                                                                   direccion, inicio,
                                                                                   fin, periodo,
                                                                                   inclinacion_modulo,
                                                                                   225)
        c_s._camino_en_imagenSV_multiple(puntosSol_SO, Foto_SO, 'SO', '4')

        # Orientación Oeste
        params[0]['heading'] = 270
        direccion = (180 - 270) % 360
        img_O, puntosSol_O, irradiancia_dia_O, Foto_O = _proceso_imagen_rapido(params, site,
                                                                               direccion, inicio,
                                                                               fin, periodo,
                                                                               inclinacion_modulo,
                                                                               270)
        c_s._camino_en_imagenSV_multiple(puntosSol_O, Foto_O, 'O', '5')

    else:

        # Orientación Este
        params[0]['heading'] = 90
        direccion = (180 - 90) % 360
        img_E, puntosSol_E, irradiancia_dia_E, Foto_E = _proceso_imagen_rapido(params, site,
                                                                               direccion, inicio,
                                                                               fin, periodo,
                                                                               inclinacion_modulo,
                                                                               90, 1)
        c_s._camino_en_imagenSV_multiple(puntosSol_E, Foto_E, 'E', '1')

        # Orientación Sur - Este
        params[0]['heading'] = 135
        direccion = (180 - 135) % 360
        img_SE, puntosSol_SE, irradiancia_dia_SE, Foto_SE = _proceso_imagen_rapido(params, site,
                                                                                   direccion, inicio,
                                                                                   fin, periodo,
                                                                                   inclinacion_modulo,
                                                                                   135, 2)
        c_s._camino_en_imagenSV_multiple(puntosSol_SE, Foto_SE, 'SE', '2')

        # Orientación Sur
        params[0]['heading'] = 180
        direccion = (180 - 180) % 360
        img_S, puntosSol_S, irradiancia_dia_S, Foto_S = _proceso_imagen_rapido(params, site,
                                                                               direccion, inicio,
                                                                               fin, periodo,
                                                                               inclinacion_modulo,
                                                                               180, 3)
        c_s._camino_en_imagenSV_multiple(puntosSol_S, Foto_S, 'S', '3')

        # Orientación Sur - Oeste
        params[0]['heading'] = 225
        direccion = (180 - 225) % 360
        img_SO, puntosSol_SO, irradiancia_dia_SO, Foto_SO = _proceso_imagen_rapido(params, site,
                                                                                   direccion, inicio,
                                                                                   fin, periodo,
                                                                                   inclinacion_modulo,
                                                                                   225, 4)
        c_s._camino_en_imagenSV_multiple(puntosSol_SO, Foto_SO, 'SO', '4')

        # Orientación Oeste
        params[0]['heading'] = 270
        direccion = (180 - 270) % 360
        img_O, puntosSol_O, irradiancia_dia_O, Foto_O = _proceso_imagen_rapido(params, site,
                                                                               direccion, inicio,
                                                                               fin, periodo,
                                                                               inclinacion_modulo,
                                                                               270, 5)
        c_s._camino_en_imagenSV_multiple(puntosSol_O, Foto_O, 'O', '5')

    # Concatenamos los valores de las diversas fotos
    PuntosSol = pd.concat([puntosSol_E, puntosSol_SE, puntosSol_S,
                           puntosSol_SO, puntosSol_O],
                          keys=["E", "SE", "S", "SO", "O"])

    return PuntosSol
