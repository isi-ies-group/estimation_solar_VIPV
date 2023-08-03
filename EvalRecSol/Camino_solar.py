'''
---------------------------------------------------------------
--- LIBRERÍA - EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR --- 
---                 MÓDULO DE CAMINO SOLAR                  ---
---------------------------------------------------------------
'''
# Importa las librerias


from matplotlib import pyplot as plt
import pandas as pd
from pvlib import solarposition
import pytz
import numpy as np
import cv2
from EvalRecSol import Utilidades_generales as u_g
from EvalRecSol import Gestion_fotografia as g_f


# Función que muestra el diagrama del camino solar durante un año


def diagrama_solar(site_location):
    '''
    --------------------
    --- Camino solar ---
    --------------------------------------------------------------------------

    La función 'diagrama_solar()' nos permite ver en un diagrama las 
    posiciones que sigue el Sol para una localización concreta en un plano.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    site_location :
        Estructura con los valores de la ubicación, latitud, longitud y 
        zona horaria

    '''

    times = pd.date_range('2021-01-01 00:00:00', '2022-01-01', closed='left',
                          freq='H', tz=site_location.tz)
    solpos = solarposition.get_solarposition(
        times, site_location.latitude, site_location.longitude)
    # Elimina los puntos de noche
    solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]

    ax = plt.subplot(1, 1, 1, projection='polar')
    # Dibuja los bucles de Analemma
    points = ax.scatter(np.radians(solpos.azimuth), solpos.apparent_zenith,
                        s=2, label=None, c=solpos.index.dayofyear)
    ax.figure.colorbar(points)

    # Dibuja las etiquetas de hora
    for hour in np.unique(solpos.index.hour):
        # Escoge la etiqueta de posición de menor radio para cada hora
        subset = solpos.loc[solpos.index.hour == hour, :]
        r = subset.apparent_zenith
        pos = solpos.loc[r.idxmin(), :]
        ax.text(np.radians(pos['azimuth']), pos['apparent_zenith'], str(hour))

    # Dibuja días individuales: equinocios y solsticios
    for date in pd.to_datetime(['2021-03-21', '2021-06-21', '2021-12-21']):
        times = pd.date_range(date, date+pd.Timedelta('24h'),
                              freq='5min', tz=site_location.tz)
        solpos = solarposition.get_solarposition(
            times, site_location.latitude, site_location.longitude)
        solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]
        label = date.strftime('%Y-%m-%d')
        ax.plot(np.radians(solpos.azimuth),
                solpos.apparent_zenith, label=label)

    ax.figure.legend(loc='upper left')

    # Cambia las coordenadas para ser un compas
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rmax(90)

    plt.show()


# Función que muestra la trayectoria del Sol


def caminoSolar(Foto, site_location, direccion, inicio, fin, periodo):
    '''
    --------------------
    --- Camino solar ---
    --------------------------------------------------------------------------

    En la función 'caminoSolar()' determinaremos el camino que recorre el sol 
    para esa ubicación sin considerar los edificios. Ubicando la imagen, 
    comprobaremos si los puntos de cielo determinados con antelación 
    pertenecen al camino del sol en esa ubicación para un día determinado. Si 
    los puntos pertenecen al camino solar, asignaremos un valor intermedio de 
    (127) al punto y añadiremos a una estructura de datos las coordenados de 
    los píxel, el azimuth y la elevación solar. Devolviendo la imagen con el 
    camino solar marcado y la estructura de datos generada.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    Foto :
        Imagen a procesar
    site_location :
        Estructura con los valores de la ubicación, latitud, longitud y 
        zona horaria
    direccion :
        Orientación del centro de la imagen en coordenadas anti-brújula
    inicio :
        Intante de tiempo inicio
    fin :
        Instante de tiempo fin
    periodo :
        Paso de tiempo entre los puntos del camino solar 

    Devolución
    ----------
    imagen :
        Imagen binaria con el camino solar
    PuntosSol :
        Estructura de datos con el camino solar en la imagen

    '''

    # Abrimos la imagen a procesar
    imagen = Foto

    # Definimos la zona horaria donde se encuentra la foto
    tz = pytz.timezone(site_location.tz)

    # Obtenemos el espacio de tiempo a emplear
    times = pd.date_range(inicio, fin, closed='left', freq=periodo, tz=tz)

    # Obtención de la posición del sol para la ubicación
    solpos = solarposition.get_solarposition(times, site_location.latitude,
                                             site_location.longitude)

    # Eliminamos las horas nocturnas
    solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]

    # Fila 0 --> Azimuth, Fila 1 --> Elevación solar, Fila 2 --> Fecha y hora
    camSol = np.array([solpos['azimuth'], solpos['apparent_elevation'],
                       solpos.index])

    # Transposición del array
    # Columna 0 --> Azimuth, Columna 1 --> Elevación solar,
    # Columna 2 --> Fecha y hora
    camSol = camSol.transpose()

    # Azimuth de los bordes de la fotografía
    ang_ca = g_f._angulo_camara('SV', 90)
    cor_pol_izq = u_g._pixel_a_polares(0, 0, Foto, ang_ca, direccion)
    cor_pol_der = u_g._pixel_a_polares(len(Foto), 0, Foto, ang_ca, direccion)

    # Cambio de Brújula --> Sur (0°), Este(90°), Norte (180°) y Oeste (270°)
    for m in range(len(camSol)):
        camSol[m][0] = (180 - camSol[m][0]) % 360

    '''
    -------------------------------------------------------------
    --- Comprobación pertenencia al camino solar y sin sombra ---
    -------------------------------------------------------------
    '''
    PuntosSol = pd.DataFrame({'Fecha y hora': [], 'Azimuth': [],
                              'Elevacion Solar': [], 'Pixel V': [], 'Pixel H': []})
    # Estructura de datos de los puntos sin sombra o cielo
    # --> [ Fecha y hora, Azimuth, Elevación Solar,
    # Pixel Vertical, Pixel Horizontal ]

    # Extraemos los valores pertenecientes a la foto
    for k in range(len(camSol)):
        # Consideramos valores para los casos límites al ser posible la ubicación
        # de píxeles encontarse en valores por debajo de 0 grados o por encima de
        # 360 grados y querer que esten comprendidos entre 0 y 360 grados.
        if direccion >= 45 and direccion < 315:
            if camSol[k, 0] <= cor_pol_izq[0] and camSol[k][0] >= cor_pol_der[0]:
                pixel = u_g._polares_a_pixel(camSol[k][0], camSol[k][1], Foto,
                                             ang_ca, direccion)
                # Pixel blanco > 240, es punto de cielo
                if imagen[pixel[0], pixel[1]] > 240:
                    # Se colorea en gris el puntpor el que pasa el Sol,
                    # valor intermedio de 0 a 255.
                    imagen[pixel[0], pixel[1]] = int(255/2)
                    # Añadiendolo a la estructura de datos
                    PuntosSol = PuntosSol.append({'Fecha y hora': camSol[k][2],
                                                  'Azimuth': camSol[k][0],
                                                  'Elevacion Solar': camSol[k][1],
                                                  'Pixel V': pixel[0],
                                                  'Pixel H': pixel[1]},
                                                 ignore_index=True)
        else:
            if camSol[k, 0] <= cor_pol_izq[0] or camSol[k][0] >= cor_pol_der[0]:
                pixel = u_g._polares_a_pixel(camSol[k][0], camSol[k][1], Foto,
                                             ang_ca, direccion)
                # Pixel blanco > 240, es punto de cielo
                if imagen[pixel[0], pixel[1]] > 240:
                    # Se colorea en gris el puntpor el que pasa el Sol,
                    # valor intermedio de 0 a 255.
                    imagen[pixel[0], pixel[1]] = int(255/2)
                    # Añadiendolo a la estructura de datos
                    PuntosSol = PuntosSol.append({'Fecha y hora': camSol[k][2],
                                                  'Azimuth': camSol[k][0],
                                                  'Elevacion Solar': camSol[k][1],
                                                  'Pixel V': pixel[0],
                                                  'Pixel H': pixel[1]},
                                                 ignore_index=True)

    return imagen, PuntosSol


# Función que pinta el camino solar en la imagen de Street View


def _camino_en_imagenSV(puntosS, foto):
    '''
    -----------------------------------------
    --- Camino solar sobre imagen inicial ---
    --------------------------------------------------------------------------

    Función que recibe los puntos por los que pasa el Sol y la imagen extraida.
    Pinta los píxeles del camino solar en rojo, muestra la imagen y la guarda.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    puntosS :
        Estructura de datos con el camino solar
    foto:
        Imagen obtenida de la API de Google Street View    

    '''

    imagen = cv2.imread(foto, 1)

    # Cambio color píxeles de camino solar a rojo
    for i in range(len(puntosS)):
        imagen[int(puntosS['Pixel V'][i]), int(
            puntosS['Pixel H'][i])] = (0, 0, 255)
    # Mostrar la imagen
    # cv2.imshow('Imagen original procesada', imagen)
    # Guardar la imagen
    # cv2.imwrite('downloads\gsv_0_solapada.jpg', imagen)

# Función que pinta el camino solar en la imagen de Street View


def _camino_en_imagenSV_multiple(puntosS, foto, nombre, num):
    '''
    -----------------------------------------
    --- Camino solar sobre imagen inicial ---
    --------------------------------------------------------------------------

    Función que recibe los puntos por los que pasa el Sol y la imagen extraida.
    Pinta los píxeles del camino solar en rojo, muestra la imagen y la guarda.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    puntosS :
        Estructura de datos con el camino solar
    foto:
        Imagen obtenida de la API de Google Street View
    nombre :
        Nombre a asignar a la imagen
    num :
        Numero a asignar a la imagen    

    '''

    imagen = cv2.imread(foto, 1)

    # Cambio color píxeles de camino solar a rojo
    for i in range(len(puntosS)):
        imagen[int(puntosS['Pixel V'][i]), int(
            puntosS['Pixel H'][i])] = (0, 0, 255)
    # Mostrar la imagen
    # cv2.imshow('Imagen original procesada'+ nombre, imagen)
    # Guardar la imagen
    # cv2.imwrite('downloads\gsv_0_solapada' + num + nombre + '.jpg', imagen)
