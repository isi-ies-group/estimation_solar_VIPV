'''
---------------------------------------------------------------
--- LIBRERÍA - EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR --- 
---               MÓDULO DE GESTIÓN DE RUTAS                ---
---------------------------------------------------------------
'''
# Importa las librerias


import googlemaps
import datetime
import pandas as pd
from pvlib import location
import numpy as np
import requests
import matplotlib.pyplot as plt
from EvalRecSol import Utilidades_generales as u_g
from EvalRecSol import Procesado_completo_imagenes as p_c_i


# Función que genera las indicaciones de una ruta


def ruta_google_maps(clave, coords_inicio, coords_meta, instante):
    '''
    -------------------------------------
    --- Google Maps - Obtención rutas ---
    --------------------------------------------------------------------------

    Pasando la clave de la API de Google y las coordenadas de partida y meta,
    obtenemos los puntos más representativos de las diversas rutas.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave :
        Contraseña de la API de Google
    coords_inicio : 
        Coordenadas del punto de partida de la ruta
    coords_meta:
        Coordenadas del punto destino de la ruta
    instante :
        Fecha y hora de comienzo de la ruta

    Devolución
    ----------
    directions_result :
        Lista de las posibles rutas de ese trayecto con infomación empleada
        por un dispositivo de navegación o GPS

    '''

    # Inicializamos datos cliente
    gmaps = googlemaps.Client(key=clave)

    # Definimos variable de fecha y hora actual
    now = instante

    # Obtenemos las estructuras de datos de las rutas
    directions_result = gmaps.directions(coords_inicio, coords_meta,
                                         mode="driving", alternatives='True',
                                         avoid='highways',
                                         optimize_waypoints='False',
                                         departure_time=now)
    return directions_result


# Función que determina la distancia de una ruta


def _get_distance(dir_res, opc):
    '''
    ---------------------------------------------------
    --- Google Maps - Obtención longitud de la ruta ---
    --------------------------------------------------------------------------

    Pasando la estructura de datos de las posibles rutas y la ruta deseada, 
    determinamos la longitud de la ruta y la imprimimos por consola.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    dir_res :
        Lista de las posibles rutas de ese trayecto con infomación empleada
        por un dispositivo de navegación o GPS
    opc :
        Opción de ruta a emplear

    Devolución
    ----------
    legs :
        Distancia en metros de la ruta 

    '''

    distance = 0
    # Extraemos los pasos de la ruta
    legs = dir_res[opc].get("legs")
    for leg in legs:
        # Sumamos los tramos a una variable global
        distance += leg.get("distance").get("value")
    print(distance, 'metros')
    return legs


# Función que almacena las coordenadas de los puntos con indicaciones


def coord_ruta(dir_res, opc):
    '''
    ---------------------------------------------------------
    --- Google Maps - Extracción coordenadas de las rutas ---
    --------------------------------------------------------------------------

    Pasando la estructura de datos de las posibles rutas y la ruta deseada,
    extraemos las coordenadas de los puntos representativos para añadirlos a
    una estructura que devolvemos. 

    La variable de la estructura llamda 'Tunel' se debe a la posibilidad de 
    solape de un tunel con una calle y que la ruta sea por el tunel. 
    Quedaría por implementar ya que ha sido inicializada manualmente.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    dir_res :
        Lista de las posibles rutas de ese trayecto con infomación empleada
        por un dispositivo de navegación o GPS
    opc :
        Opción de ruta a emplear

    Devolución
    ----------
    ruta :
        Estructura de datos de la ruta con la latitud, la longitud y si hay o
        no tunel

    Nota
    ----
    La variable 'Tunel' se le asigna autmáticamente el valor de 0 por la 
    imposibilidad de conocer esta información sin proceder manualmente. 
    Quedando como posible punto a implementar en el futuro

    '''

    # Creamos una nueva estructura de datos
    ruta = pd.DataFrame({'Latitud': [], 'Longitud': [], 'Tunel': []})
    legs = dir_res[opc].get('legs')
    # Añadimos el punto de origen de la ruta
    ruta = ruta.append({'Latitud': legs[0]['start_location'].get('lat'),
                        'Longitud': legs[0]['start_location'].get('lng'),
                        'Tunel': 0}, ignore_index=True)
    x = 0
    for x in range(len(legs[0].get('steps'))):
        # Añadimos los puntos finales de cada tramo
        ruta = ruta.append({'Latitud': legs[0].get('steps')[x].get('end_location').get('lat'),
                            'Longitud': legs[0].get('steps')[x].get('end_location').get('lng'),
                            'Tunel': 0}, ignore_index=True)
    return ruta


# Función que almacena las coordenadas de los puntos en un '.csv'


def coord_ruta_csv(dir_res, opc):
    '''
    ------------------------------------------------------------------
    --- Google Maps - Extracción coordenadas de las rutas a '.csv' ---
    --------------------------------------------------------------------------

    Pasando la estructura de datos de las posibles rutas y la ruta deseada,
    extraemos las coordenadas de los puntos representativos para añadirlos a
    una estructura que guardamos en un archivo '.csv' y devolviendo el nombre 
    del archivo en el que ha sido guardado.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    dir_res :
        Lista de las posibles rutas de ese trayecto con infomación empleada
        por un dispositivo de navegación o GPS
    opc :
        Opción de ruta a emplear

    Devolución
    ----------
    nombre :
        Cadena de caracteres con el nombre del '.csv' donde se ha almacenado
        la estructura de datos de la ruta   

    '''

    # Creamos una nueva estructura de datos
    ruta = pd.DataFrame({'Latitud': [], 'Longitud': [], 'Tunel': []})
    legs = dir_res[opc].get('legs')
    # Añadimos el punto de origen de la ruta
    ruta = ruta.append({'Latitud': legs[0]['start_location'].get('lat'),
                        'Longitud': legs[0]['start_location'].get('lng'),
                       'Tunel': 0}, ignore_index=True)
    x = 0
    for x in range(len(legs[0].get('steps'))):
        # Añadimos los puntos finales de cada tramo
        ruta = ruta.append({'Latitud': legs[0].get('steps')[x].get('end_location').get('lat'),
                            'Longitud': legs[0].get('steps')[x].get('end_location').get('lng'),
                            'Tunel': 0}, ignore_index=True)

    # Guardamos la estructura de datos en archivos '.csv' en función de su
    # posición en la lista
    if opc == 0:
        ruta.to_csv('Coordenadas_ruta_A', index=False)
        nombre = 'Coordenadas_ruta_A'
    elif opc == 1:
        ruta.to_csv('Coordenadas_ruta_B', index=False)
        nombre = 'Coordenadas_ruta_B'
    elif opc == 2:
        ruta.to_csv('Coordenadas_ruta_C', index=False)
        nombre = 'Coordenadas_ruta_C'

    return nombre


# Función que añade coordenadas intermedias a una ruta de Google Maps


def _rutas_maps_ampliadas(dir_res, opc):
    '''
    -------------------------------------------------------
    --- Aumento de los puntos de la ruta de Google Maps ---
    --------------------------------------------------------------------------

    Recibiendo la ruta seleccionada, se aumentan los puntos entre las 
    coordenadas definidas por Google Maps para disponer de un paso entre
    puntos de 10 metros.   

    --------------------------------------------------------------------------

    Parámetros
    ----------
    dir_res :
        Lista de las posibles rutas de ese trayecto con infomación empleada
        por un dispositivo de navegación o GPS
    opc :
        Opción de ruta a emplear

    Devolución
    ----------
    ruta_compleja :
        Estructura de datos con coordenadas cada 10 metros de la ruta  

    '''

    ruta_simple = pd.DataFrame({'Latitud': [], 'Longitud': [], 'Tunel': [],
                                'Distancia': []})
    legs = dir_res[opc].get('legs')
    ruta_simple = ruta_simple.append({'Latitud': legs[0]['start_location'].get('lat'),
                                      'Longitud': legs[0]['start_location'].get('lng'),
                                      'Tunel': 0, 'Distancia': 0}, ignore_index=True)

    # DataFrame con puntos Google Maps
    x = 0
    for x in range(len(legs[0].get('steps'))):
        ruta_simple = ruta_simple.append({'Latitud': legs[0].get('steps')[x].get('end_location').get('lat'),
                                          'Longitud': legs[0].get('steps')[x].get('end_location').get('lng'),
                                          'Tunel': 0, 'Distancia': legs[0].get('steps')[x].get('distance').get('value')}, ignore_index=True)

    # DataFrame con puntos intermedios
    ruta_compleja = pd.DataFrame({'Latitud': [], 'Longitud': [], 'Tunel': []})
    for i in range(len(ruta_simple)-1):

        tramo_I = [ruta_simple['Latitud'][i], ruta_simple['Longitud'][i]]
        tramo_F = [ruta_simple['Latitud'][i+1], ruta_simple['Longitud'][i+1]]

        x, y = u_g._puntos_intermedios(
            tramo_I, tramo_F, ruta_simple['Distancia'][i+1])

        for j in range(len(x)):
            ruta_compleja = ruta_compleja.append({'Latitud': x[j],
                                                  'Longitud': y[j],
                                                  'Tunel': 0},
                                                  ignore_index=True)

    ruta_compleja = ruta_compleja.append({'Latitud': ruta_simple['Latitud'][len(ruta_simple)-1],
                                          'Longitud': ruta_simple['Longitud'][len(ruta_simple)-1],
                                          'Tunel': 0}, ignore_index=True)

    return ruta_compleja


# Función que añade los tiempos de ruta a la estructura de datos


def _tiempos_ruta(fechaYhora, duracion, ruta):
    '''
    --------------------------------------------------
    --- Google Maps - Instantes en las coordenadas ---
    --------------------------------------------------------------------------

    Pasamos la fecha y la hora de partido, la duración de la ruta y la 
    estructura de datos de la ruta; añadiendo los tiempos en que se ubica en 
    cada momento para cada coordenadas en la estructura de datos.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    fechaYhora :
        Fecha y hora de inicio de la ruta
    duracion :
        Duración en minutos del trayecto
    ruta :
        Estructura de datos con la información de la ruta

    Devoluciones
    ------------
    Tiempo :
        Lista de fechas y horas de cada punto del trayecto
    
    '''

    Tiempo = []

    # Fijamos un paso promedio entre los puntos de la ruta
    paso = duracion*60/len(ruta)
    # Definimmos el incremento  mediante el paso para poder emplearlo
    # como Timestramp
    incremento_tiempo_ruta = datetime.timedelta(0, paso)

    for i in range(len(ruta)):
        # Añadimos los tiempos a las coordenadas
        Tiempo.append(fechaYhora)
        fechaYhora += incremento_tiempo_ruta

    return Tiempo


# Función que realiza una ruta con sus irradiancias


def irradiancia_ruta(clave, inicio, fin, ruta, tiempo_ruta, tamaño,
                     inclinacion, inclinacion_modulo, campo_visual_H, 
                     save = False):
    '''
    -------------------------------
    --- Irradiancia de una ruta ---
    --------------------------------------------------------------------------

    Esta función procesa una serie de coordenadas que componen la ruta con 
    todos los parámetros que se requieren para la ejecución. Para cada 
    coordenada determinamos el camino solar y almacenamos en cada coordenada, 
    en el instante que pasa por el punto y las irradiancias que se obtendrían.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave :
        Contraseña de acceso a los servicios de la API de Google
    inicio :
        Instante de tiempo en el que empieza el proceso, fecha y hora
    fin :
        Instante de tiempo en el que acaba el proceso, fecha y hora
    ruta :
        Estructura de datos de la información de la ruta
    tiempo_ruta :
        Duración de la ruta
    tamaño :
        Tamaño de la imagen (Valor típico: 640x640 píxeles)
    inclinacion :
        Inclinación de la lente
    inclinacion_modulo :
        Inclinación de los módulos fotovoltaicos
    campo_visual_H :
        Campo visual horizontal de la imagen
    save :
        Variable que guarda las imágenes del proceso si es True

    '''

    '''
    ----------------------------
    --- Parámetros ubicación ---
    ----------------------------
    Definimos los parámetros a emplear durante la ejecucción.
    - Zona horaria de la ubicación, emplearemos la zona horaria de Madrid y 
    la península.
    - Paso entre puntos del camino del Sol.
    '''

    # Zona horaria
    zona_horaria = 'Europe/Madrid'

    # Paso entre los puntos del sol
    periodo = '1min'

    # Añadimos tiempos en llegar a los puntos
    ruta['Tiempo'] = _tiempos_ruta(inicio, tiempo_ruta, ruta)

    # Variables a rellenar
    POA = []
    GHI = []

    for i in range(len(ruta)):
        # Si la ruta consta de un único punto
        if len(ruta) == 1:
            rumbo = 180
        # Empleo función que devuelve el rumbo entre los puntos de la ruta
        if i < len(ruta)-1 and len(ruta) != 1:
            origen = [ruta['Latitud'][i], ruta['Longitud'][i]]
            final = [ruta['Latitud'][i+1], ruta['Longitud'][i+1]]
            rumbo = u_g._angulo_entre_dos_coordenadas(origen, final)

        # Cambio de referencia en brújula
        # Dirección --> Sur (0°), Este(90°), Norte (180°) y Oeste (270°)
        direccion = (180 - rumbo) % 360

        # Datos empleados de la ubicacción
        localizacion = str(ruta['Latitud'][i]) + ',' + str(ruta['Longitud'][i])

        # Creación objeto para almacenar latitud, longitud y zona horaria
        site = location.Location(ruta['Latitud'][i], ruta['Longitud'][i],
                                 tz=zona_horaria)
        '''
        -----------------------
        --- API Street View ---
        -----------------------
        '''
        # Define parametros para Google Street View api
        params = [{
            'size': tamaño,  # Tamaño imagen - max 640x640 pixels
            'location': localizacion,  # Coordenadas polares
            'heading': rumbo,  # Orientación N(0), E(90), S(180), O(270)
            'pitch': inclinacion,  # Inclinación lente
            'fov': campo_visual_H,  # Campo de visión horizontal
            'key': clave
        }]

        if ruta['Tunel'][i] == 1:
            GHI.append(0)
            POA.append(0)

        else:
            # Obtenemos en una estructura de datos todos los puntos por los que pasa el
            # sol, procesando imágenes orientadas a Este, Sureste, Sur, Suroeste y Oeste.
            Puntos_Sol = p_c_i.de_Este_a_Oeste(params, site, direccion, inicio, fin,
                                               periodo, inclinacion_modulo, save)
            done = 0
            for x in range(len(Puntos_Sol)):
                # Añadimos las irradiancias de cada punto a la estructura si
                # pertenecen al camino solar
                if Puntos_Sol['Fecha y hora'][x].year == ruta['Tiempo'][i].year and Puntos_Sol['Fecha y hora'][x].month == ruta['Tiempo'][i].month and Puntos_Sol['Fecha y hora'][x].day == ruta['Tiempo'][i].day and Puntos_Sol['Fecha y hora'][x].hour == ruta['Tiempo'][i].hour and Puntos_Sol['Fecha y hora'][x].minute == ruta['Tiempo'][i].minute:
                    GHI.append(Puntos_Sol['GHI'][x])
                    POA.append(Puntos_Sol['POA'][x])
                    done = 1
                    break

            # Si no pertenecen al camino solar entonces hay sombra
            if done == 0:
                GHI.append(0)
                POA.append(0)

    ruta['GHI'] = GHI
    ruta['POA'] = POA


# Función que procesa varias rutas, definiendo lo más energética


def ruta_eficiente_irradiancia(clave, inicio, fin, Rutas, tiempo_rutas, tamaño,
                               inclinacion, inclinacion_modulo, campo_visual_H,
                               save = False):
    '''
    ------------------------------------------
    --- Irradiancia máxima de varias rutas ---
    --------------------------------------------------------------------------

    Esta función procesa una serie rutas compuestas de coordenadas que 
    componen la ruta con todos los parámetros que se requieren para la 
    ejecución. Para cada ruta, la procesamos con la función irradiancia_ruta. 
    En último lugar, compararemos las medias de las distintas irradiancias y 
    devolveremos la ruta más eficiente energéticamente y sus valore de GHI y 
    POA.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave :
        Contraseña de acceso a los servicios de la API de Google
    inicio :
        Instante de tiempo en el que empieza el proceso, fecha y hora
    fin :
        Instante de tiempo en el que acaba el proceso, fecha y hora
    Rutas :
        Vector de estructuras de datos de la información de las rutas
    tiempo_rutas :
        Vector de duración de las rutas
    tamaño :
        Tamaño de la imagen (Valor típico: 640x640 píxeles)
    inclinacion :
        Inclinación de la lente
    inclinacion_modulo :
        Inclinación de los módulos fotovoltaicos
    campo_visual_H :
        Campo visual horizontal de la imagen
    save :
        Si esta variable es True, se guardan las imágenes

    Devolución
    ----------
    Rutas[i] :
        Estructura de datos de la ruta energéticamente más favorable
    irrad_media['Energia_GHI'][i]:
        Valor de la energía en 'GHI' de la ruta en kWh/m^2
    irrad_media['Energia_POA'][i]:
        Valor de la energía en 'POA' de la ruta en kWh/m^2  

    '''

    # Procesamos todos los puntos de las múltiples rutas
    for i in range(len(Rutas)):
        irradiancia_ruta(clave, inicio, fin, Rutas[i], tiempo_rutas[i], tamaño,
                         inclinacion, inclinacion_modulo, campo_visual_H, save)

    # Creamos unas variables de energía y una estructura
    irrad_media = pd.DataFrame({'Energia_GHI': [], 'Energia_POA': []})
    e_ghi, e_poa = [], []

    # Variable a emplear para definir tiempos de cada punto
    tiempos_ruta = []
    # Establecemos los tiempos de cada paso por las coordenadas
    for i in range(len(Rutas)):
        inicio = 0
        tiempo_entre_coord = []
        for j in range(len(Rutas[i])):
            tiempo_entre_coord.append(inicio)
            inicio += tiempo_rutas[i]*60/len(Rutas[i])
        tiempos_ruta.append(tiempo_entre_coord)

    # Realizamos la integral de cada ruta para conseguir la energía de la ruta
    for i in range(len(Rutas)):
        e_ghi.append(np.trapz(Rutas[i]['GHI'], tiempos_ruta[i]))
        e_poa.append(np.trapz(Rutas[i]['POA'], tiempos_ruta[i]))

    # Se almacenan en una estructura de datos
    irrad_media['Energia_GHI'] = e_ghi
    irrad_media['Energia_POA'] = e_poa

    # Buscamos si hay varios valores repetidos
    if len(irrad_media) != len(set(irrad_media)):
        maximo = []
        # Procesamos buscando varias rutas que den la máxima energía
        for x in range(len(irrad_media)):
            if irrad_media['Energia_GHI'][x] == irrad_media['Energia_GHI'].max():
                maximo.append(x)
        # Si solo hay una ruta con valor máximo, lo imprimimos por consola y
        # lo devolvemos
        if len(maximo) == 1:
            print('\n\n\n La ruta más eficiente es la ruta', maximo[0]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[0]]/1000*0.000278), 'kWh/m^2.\n\n')
            return Rutas[maximo[0]], irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278, irrad_media['Energia_POA'][maximo[0]]/1000*0.000278
        # Si hay varias rutas con máxima energía
        else:
            t = 0
            for z in range(len(maximo)):
                # Buscamos la ruta más rápida
                if tiempo_rutas[maximo[z]] < tiempo_rutas[maximo[t]]:
                    t = z
            # Imrimimos y devolvemos la ruta más energética y más rápida
            print('\n\n\n La ruta más eficiente es la ruta', maximo[t]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[t]]/1000*0.000278), 'kWh/m^2.\n\n')
            return Rutas[maximo[t]], irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278, irrad_media['Energia_POA'][maximo[t]]/1000*0.000278

    # Si no hay valores repetidos
    elif len(irrad_media) == len(set(irrad_media)):
        for i in range(len(irrad_media)):
            # Imprimimos por consola y devolvemos la ruta con energía máxima
            if irrad_media['GHI'][i] == irrad_media['Energia_GHI'].max() and irrad_media['Energia_POA'][i] == irrad_media['Energia_POA'].max():
                print('\n\n\n La ruta más eficiente es la ruta', i+1, ', con GHI de %.5f' %
                      (irrad_media['Energia_GHI'][i]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][i]/1000*0.000278), 'kWh/m^2.\n\n')
                return Rutas[i], irrad_media['Energia_GHI'][i]/1000*0.000278, irrad_media['Energia_POA'][i]/1000*0.000278


# Función que procesa varias rutas, definiendo lo más energética


def ruta_eficiente_sin_procesado(Rutas, tiempo_rutas):
    '''
    ----------------------------------------------------------
    --- Irradiancia máxima de varias rutas sin procesarlas ---
    --------------------------------------------------------------------------

    Esta función recibe una serie rutas compuestas de coordenadas que componen 
    la ruta con todos los parámetros que se requieren para la ejecución.
    Compara las medias de las distintas irradiancias de las rutas y 
    devolvuelve la ruta más eficiente energéticamente y sus valore de GHI y 
    POA.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    Rutas :
        Vector de estructuras de datos de la información de las rutas
    tiempo_rutas :
        Vector de duración de las rutas

    Devolución
    ----------
    Rutas[i] :
        Estructura de datos de la ruta energéticamente más favorable
    irrad_media['Energia_GHI'][i]:
        Valor de la energía en 'GHI' de la ruta en kWh/m^2
    irrad_media['Energia_POA'][i]:
        Valor de la energía en 'POA' de la ruta en kWh/m^2  

    '''

    # Creamos unas variables de energía y una estructura
    irrad_media = pd.DataFrame({'Energia_GHI': [], 'Energia_POA': []})
    e_ghi, e_poa = [], []

    # Variable a emplear para definir tiempos de cada punto
    tiempos_ruta = []
    # Establecemos los tiempos de cada paso por las coordenadas
    for i in range(len(Rutas)):
        inicio = 0
        tiempo_entre_coord = []
        for j in range(len(Rutas[i])):
            tiempo_entre_coord.append(inicio)
            inicio += tiempo_rutas[i]*60/len(Rutas[i])
        tiempos_ruta.append(tiempo_entre_coord)

    # Realizamos la integral de cada ruta para conseguir la energía de la ruta
    for i in range(len(Rutas)):
        grafica_Power_time(tiempos_ruta[i], Rutas[i]['GHI'], 'GHI')
        e_ghi.append(np.trapz(Rutas[i]['GHI'], tiempos_ruta[i]))
        grafica_Power_time(tiempos_ruta[i], Rutas[i]['POA'], 'POA')
        e_poa.append(np.trapz(Rutas[i]['POA'], tiempos_ruta[i]))

    # Se almacenan en una estructura de datos
    irrad_media['Energia_GHI'] = e_ghi
    irrad_media['Energia_POA'] = e_poa

    # Pasamos las energías a kWh/m^2
    for i in range(len(e_ghi)):
        e_ghi[i] = e_ghi[i] / 1000*0.000278
        e_poa[i] = e_poa[i] / 1000*0.000278

    # Buscamos si hay varios valores repetidos
    if len(irrad_media) != len(set(irrad_media)):
        maximo = []
        # Procesamos buscando varias rutas que den la máxima energía
        for x in range(len(irrad_media)):
            if irrad_media['Energia_GHI'][x] == irrad_media['Energia_GHI'].max():
                maximo.append(x)
        # Si solo hay una ruta con valor máximo, lo imprimimos por consola y
        # lo devolvemos
        if len(maximo) == 1:
            print('\n\n\n La ruta más eficiente es la ruta', maximo[0]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[0]]/1000*0.000278), 'kWh/m^2.\n\n')
            return Rutas[maximo[0]], irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278, irrad_media['Energia_POA'][maximo[0]]/1000*0.000278, e_ghi, e_poa
        # Si hay varias rutas con máxima energía
        else:
            t = 0
            for z in range(len(maximo)):
                # Buscamos la ruta más rápida
                if tiempo_rutas[maximo[z]] < tiempo_rutas[maximo[t]]:
                    t = z
            # Imrimimos y devolvemos la ruta más energética y más rápida
            print('\n\n\n La ruta más eficiente es la ruta', maximo[t]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[t]]/1000*0.000278), 'kWh/m^2.\n\n')
            return Rutas[maximo[t]], irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278, irrad_media['Energia_POA'][maximo[t]]/1000*0.000278, e_ghi, e_poa

    # Si no hay valores repetidos
    elif len(irrad_media) == len(set(irrad_media)):
        for i in range(len(irrad_media)):
            # Imprimimos por consola y devolvemos la ruta con energía máxima
            if irrad_media['Energia_GHI'][i] == irrad_media['Energia_GHI'].max() and irrad_media['Energia_POA'][i] == irrad_media['Energia_POA'].max():
                print('\n\n\n La ruta más eficiente es la ruta', i+1, ', con GHI de %.5f' %
                      (irrad_media['Energia_GHI'][i]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][i]/1000*0.000278), 'kWh/m^2.\n\n')
                return Rutas[i], irrad_media['Energia_GHI'][i]/1000*0.000278, irrad_media['Energia_POA'][i]/1000*0.000278, e_ghi, e_poa


# Función que procesa completamente la ruta por puntos intermedios


def rutas_GMaps(clave, dir_ini, dir_fin, time_inicio):
    '''
    -------------------------------------------------
    --- Generador de rutas con puntos intermedios ---
    --------------------------------------------------------------------------

    Pasando las direcciones de inicio y fin de la ruta, se emplea el servicio
    de la API de Google Maps para la obtención de las rutas posibles con 
    solamente los puntos donde un navegador GPS hace indicaciones. Para poder
    obtener rutas con coordenadas distantes a 10 metros serán procesados y
    añadidos a una estructura de datos que es devuelta.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave :
        Contraseña para acceder a los servicios de la API de Google
    dir_ini :
        Dirección inicial del trayecto
    dir_fin :
        Dirección final del trayecto
    time_inicio :
        Fecha y hora de partida del trayecto

    Devolución
    ----------
    trayectos_procesados :
        Lista con las estructuras de datos de las posibles rutas

    '''

    # Conversión direcciones a coordenadas
    coords_inicio = _direccion_coordenadas(clave, dir_ini)
    coords_meta = _direccion_coordenadas(clave, dir_fin)

    now = time_inicio
    trayectos = ruta_google_maps(clave, coords_inicio, coords_meta, now)
    trayectos_procesados = []

    for i in range(len(trayectos)):
        ruta_i = _rutas_maps_ampliadas(trayectos, i)
        ruta_i['Tiempo'] = _tiempos_ruta(now, (trayectos[i].get('legs')[0].get(
            'duration').get('value')/60), ruta_i)
        trayectos_procesados.append(ruta_i)

    return trayectos_procesados


# Función que procesa completamente la ruta por puntos intermedios con irradiancias

def rutas_GMaps_irradiancias(clave, dir_ini, dir_fin, instante, tamaño,
                             inclinacion, campo_visual_H, inclinacion_modulo,
                             save):
    '''
    ----------------------------------------------------------------------
    --- Generador de rutas con puntos intermedios con sus irradiancias ---
    --------------------------------------------------------------------------

    Pasando las direcciones de inicio y fin de la ruta junto con valores 
    destinados para el procesamiento de imágenes y referentes a los módulos, 
    se emplea el servicio de la API de Google Maps para la obtención de las 
    rutas posibles con los puntos intermedios a las indicaciones GPS posibles.
    Procesando cada ruta, se obtiene la irradiancia de cada punto de las
    diversas rutas que son añadidos a la estructura de datos. Devolviendo la
    ruta energéticamente más beneficiosa.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave :
        Contraseña para acceder a los servicios de la API de Google
    dir_ini :
        Coordenadas iniciales del trayecto
    dir_fin :
        Coordenadas finales del trayecto
    instante :
        Fecha y hora de partida del trayecto
    tamaño :
        Tamaño de la imagen (Valor típico: 640x640 píxeles)
    inclinacion :
        Inclinación de la lente
    campo_visual_H :
        Campo visual horizontal de la imagen
    inclinacion_modulo :
        Inclinación de los módulos fotovoltaicos
    save :
        Guarda las imágenes si es True

    Devolución
    ----------
    trayectos_procesados :
        Lista de estructuras de datos con todas las posibles rutas
    trayectos_procesados[i] :
        Estructura de datos de la ruta energéticamente más favorable
    irrad_media['Energia_GHI'][i]:
        Valor de la energía en 'GHI' de la ruta en kWh/m^2
    irrad_media['Energia_POA'][i]:
        Valor de la energía en 'POA' de la ruta en kWh/m^2

    '''

    # Conversión direcciones a coordenadas
    coords_inicio = _direccion_coordenadas(clave, dir_ini)
    coords_meta = _direccion_coordenadas(clave, dir_fin)

    # Obtenemos las posibles rutas
    trayectos = ruta_google_maps(clave, coords_inicio, coords_meta, instante)

    trayectos_procesados = []
    t_rutas = []

    # Procesamos las diversas rutas
    for i in range(len(trayectos)):
        tiempo_ruta = trayectos[i].get(
            'legs')[0].get('duration').get('value')/60
        t_rutas.append(tiempo_ruta)
        ruta_i = _rutas_maps_ampliadas(trayectos, i)
        irradiancia_ruta(clave, instante, (instante + datetime.timedelta(minutes=tiempo_ruta)),
                         ruta_i, tiempo_ruta, tamaño, inclinacion, inclinacion_modulo,
                         campo_visual_H, save)
        trayectos_procesados.append(ruta_i)

    # Creamos unas variables de energía y una estructura
    irrad_media = pd.DataFrame({'Energia_GHI': [], 'Energia_POA': []})
    e_ghi, e_poa = [], []

    # Variable a emplear para definir tiempos de cada punto
    tiempos_ruta = []

    # Establecemos los tiempos de cada paso por las coordenadas
    for i in range(len(trayectos_procesados)):
        inicio = 0
        tiempo_entre_coord = []
        for j in range(len(trayectos_procesados[i])):
            tiempo_entre_coord.append(inicio)
            inicio += t_rutas[i]*60/len(trayectos_procesados[i])
        tiempos_ruta.append(tiempo_entre_coord)

    # Realizamos la integral de cada ruta para conseguir la energía de la ruta
    for i in range(len(trayectos_procesados)):
        e_ghi.append(np.trapz(trayectos_procesados[i]['GHI'], tiempos_ruta[i]))
        e_poa.append(np.trapz(trayectos_procesados[i]['POA'], tiempos_ruta[i]))

    # Se almacenan en una estructura de datos
    irrad_media['Energia_GHI'] = e_ghi
    irrad_media['Energia_POA'] = e_poa

    # Buscamos si hay varios valores repetidos
    if len(irrad_media) != len(set(irrad_media)):
        maximo = []

        # Procesamos buscando varias rutas que den la máxima energía
        for x in range(len(irrad_media)):
            if irrad_media['Energia_GHI'][x] == irrad_media['Energia_GHI'].max():
                maximo.append(x)

        # Si solo hay una ruta con valor máximo, lo imprimimos por consola y
        # lo devolvemos
        if len(maximo) == 1:
            print('\n\n\n La ruta más eficiente es la ruta', maximo[0]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[0]]/1000*0.000278), 'kWh/m^2.\n\n')
            return trayectos_procesados, trayectos_procesados[maximo[0]], irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278, irrad_media['Energia_POA'][maximo[0]]/1000*0.000278

        # Si hay varias rutas con máxima energía
        else:
            t = 0
            for z in range(len(maximo)):
                # Buscamos la ruta más rápida
                if t_rutas[maximo[z]] < t_rutas[maximo[t]]:
                    t = z
            # Imrimimos y devolvemos la ruta más energética y más rápida
            print('\n\n\n La ruta más eficiente es la ruta', maximo[t]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[t]]/1000*0.000278), 'kWh/m^2.\n\n')
            return trayectos_procesados, trayectos_procesados[maximo[t]], irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278, irrad_media['Energia_POA'][maximo[t]]/1000*0.000278

    # Si no hay valores repetidos
    elif len(irrad_media) == len(set(irrad_media)):
        for i in range(len(irrad_media)):
            # Imprimimos por consola y devolvemos la ruta con energía máxima
            if irrad_media['Energia_GHI'][i] == irrad_media['Energia_GHI'].max() and irrad_media['Energia_POA'][i] == irrad_media['Energia_POA'].max():
                print('\n\n\n La ruta más eficiente es la ruta', i+1, ', con GHI de %.5f' %
                      (irrad_media['Energia_GHI'][i]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][i]/1000*0.000278), 'kWh/m^2.\n\n')
                return trayectos_procesados, trayectos_procesados[i], irrad_media['Energia_GHI'][i]/1000*0.000278, irrad_media['Energia_POA'][i]/1000*0.000278


# Función que convierte una dirección en coordenadas geográficas

def _direccion_coordenadas(clave, direccion):
    '''
    ---------------------------------------------
    --- Direcciones a Coordenadas Geográficas ---
    --------------------------------------------------------------------------

    Convierte direcciones en coordenadas geográficas, latitud y longitud.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave : str
        Clave personal de la API de Google.
    direccion : str
        Dirección de la ubicación a localizar.

    Devoluciones
    ------------
    coord : str
        Cadena con las coordenadas geográficas de la ubicación.

    '''

    params = {
        'key': clave,
        'address': direccion
    }
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json?'
    response = requests.get(base_url, params=params).json()
    response.keys()

    if response['status'] == 'OK':
        geometry = response['results'][0]['geometry']
        lat = geometry['location']['lat']
        lon = geometry['location']['lng']

    coord = str(lat) + ',' + str(lon)
    return coord


# Función que realiza una ruta con sus  rápidamente

def irradiancia_ruta_rapida(clave, inicio, fin, ruta, tiempo_ruta, tamaño,
                     inclinacion, inclinacion_modulo, campo_visual_H, save = False):
    '''
    --------------------------------------
    --- Irradiancia de una ruta rapida ---
    --------------------------------------------------------------------------

    Esta función procesa una serie de coordenadas que componen la ruta con 
    todos los parámetros que se requieren para la ejecución. Para cada 
    coordenada determinamos el camino solar y almacenamos en cada coordenada, 
    en el instante que pasa por el punto y las irradiancias que se obtendrían.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave :
        Contraseña de acceso a los servicios de la API de Google
    inicio :
        Instante de tiempo en el que empieza el proceso, fecha y hora
    fin :
        Instante de tiempo en el que acaba el proceso, fecha y hora
    ruta :
        Estructura de datos de la información de la ruta
    tiempo_ruta :
        Duración de la ruta
    tamaño :
        Tamaño de la imagen (Valor típico: 640x640 píxeles)
    inclinacion :
        Inclinación de la lente
    inclinacion_modulo :
        Inclinación de los módulos fotovoltaicos
    campo_visual_H :
        Campo visual horizontal de la imagen
    save :
        Variable que guarda las imágenes del proceso si es True
    
    '''

    '''
    ----------------------------
    --- Parámetros ubicación ---
    ----------------------------
    Definimos los parámetros a emplear durante la ejecucción.
    - Zona horaria de la ubicación, emplearemos la zona horaria de Madrid y 
    la península.
    - Paso entre puntos del camino del Sol.
    '''

    # Zona horaria
    zona_horaria = 'Europe/Madrid'

    # Paso entre los puntos del sol
    periodo = '1min'

    # Añadimos tiempos en llegar a los puntos
    ruta['Tiempo'] = _tiempos_ruta(inicio, tiempo_ruta, ruta)

    # Variables a rellenar
    POA = []
    GHI = []

    for i in range(len(ruta)):
        # Si la ruta consta de un único punto
        if len(ruta) == 1:
            rumbo = 180
        # Empleo función que devuelve el rumbo entre los puntos de la ruta
        if i < len(ruta)-1 and len(ruta) != 1:
            origen = [ruta['Latitud'][i], ruta['Longitud'][i]]
            final = [ruta['Latitud'][i+1], ruta['Longitud'][i+1]]
            rumbo = u_g._angulo_entre_dos_coordenadas(origen, final)

        # Cambio de referencia en brújula
        # Dirección --> Sur (0°), Este(90°), Norte (180°) y Oeste (270°)
        direccion = (180 - rumbo) % 360

        # Datos empleados de la ubicacción
        localizacion = str(ruta['Latitud'][i]) + ',' + str(ruta['Longitud'][i])

        # Creación objeto para almacenar latitud, longitud y zona horaria
        site = location.Location(ruta['Latitud'][i], ruta['Longitud'][i],
                                 tz=zona_horaria)
        '''
        -----------------------
        --- API Street View ---
        -----------------------
        '''
        # Define parametros para Google Street View api
        params = [{
            'size': tamaño,  # Tamaño imagen - max 640x640 pixels
            'location': localizacion,  # Coordenadas polares
            'heading': rumbo,  # Orientación N(0), E(90), S(180), O(270)
            'pitch': inclinacion,  # Inclinación lente
            'fov': campo_visual_H,  # Campo de visión horizontal
            'key': clave
        }]

        if ruta['Tunel'][i] == 1:
            GHI.append(0)
            POA.append(0)

        else:
            # Obtenemos en una estructura de datos todos los puntos por los que pasa el
            # sol, procesando imágenes orientadas a Este, Sureste, Sur, Suroeste y Oeste.
            Puntos_Sol = p_c_i.de_Este_a_Oeste_rapido(params, site, direccion, inicio, fin,
                                               periodo, inclinacion_modulo, save)
            done = 0
            for x in range(len(Puntos_Sol)):
                # Añadimos las irradiancias de cada punto a la estructura si
                # pertenecen al camino solar
                if Puntos_Sol['Fecha y hora'][x].year == ruta['Tiempo'][i].year and Puntos_Sol['Fecha y hora'][x].month == ruta['Tiempo'][i].month and Puntos_Sol['Fecha y hora'][x].day == ruta['Tiempo'][i].day and Puntos_Sol['Fecha y hora'][x].hour == ruta['Tiempo'][i].hour and Puntos_Sol['Fecha y hora'][x].minute == ruta['Tiempo'][i].minute:
                    GHI.append(Puntos_Sol['GHI'][x])
                    POA.append(Puntos_Sol['POA'][x])
                    done = 1
                    break

            # Si no pertenecen al camino solar entonces hay sombra
            if done == 0:
                GHI.append(0)
                POA.append(0)

    ruta['GHI'] = GHI
    ruta['POA'] = POA


# Función que procesa completamente la ruta por puntos intermedios con 
# irradiancias rápidamente

def rutas_GMaps_irradiancias_rapida(clave, dir_ini, dir_fin, instante, tamaño,
                             inclinacion, campo_visual_H, inclinacion_modulo,
                             save = False):
    '''
    --------------------------------------------------------------------------
    --- Generador rutas con puntos intermedios con sus irradiancias rapido ---
    --------------------------------------------------------------------------

    Pasando las direcciones de inicio y fin de la ruta junto con valores 
    destinados para el procesamiento de imágenes y referentes a los módulos, 
    se emplea el servicio de la API de Google Maps para la obtención de las 
    rutas posibles con los puntos intermedios a las indicaciones GPS posibles.
    Procesando cada ruta, se obtiene la irradiancia de cada punto de las
    diversas rutas que son añadidos a la estructura de datos. Devolviendo la
    ruta energéticamente más beneficiosa.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    clave :
        Contraseña para acceder a los servicios de la API de Google
    dir_ini :
        Coordenadas iniciales del trayecto
    dir_fin :
        Coordenadas finales del trayecto
    instante :
        Fecha y hora de partida del trayecto
    tamaño :
        Tamaño de la imagen (Valor típico: 640x640 píxeles)
    inclinacion :
        Inclinación de la lente
    campo_visual_H :
        Campo visual horizontal de la imagen
    inclinacion_modulo :
        Inclinación de los módulos fotovoltaicos
    save :
        Guarda las imágenes si la variable es True

    Devolución
    ----------
    trayectos_procesados :
        Lista de estructuras de datos con todas las posibles rutas
    trayectos_procesados[i] :
        Estructura de datos de la ruta energéticamente más favorable
    irrad_media['Energia_GHI'][i]:
        Valor de la energía en 'GHI' de la ruta en kWh/m^2
    irrad_media['Energia_POA'][i]:
        Valor de la energía en 'POA' de la ruta en kWh/m^2

    '''

    # Conversión direcciones a coordenadas
    coords_inicio = _direccion_coordenadas(clave, dir_ini)
    coords_meta = _direccion_coordenadas(clave, dir_fin)

    # Obtenemos las posibles rutas
    trayectos = ruta_google_maps(clave, coords_inicio, coords_meta, instante)

    trayectos_procesados = []
    t_rutas = []

    # Procesamos las diversas rutas
    for i in range(len(trayectos)):
        tiempo_ruta = trayectos[i].get(
            'legs')[0].get('duration').get('value')/60
        t_rutas.append(tiempo_ruta)
        ruta_i = _rutas_maps_ampliadas(trayectos, i)
        irradiancia_ruta_rapida(clave, instante, (instante + datetime.timedelta(minutes=tiempo_ruta)),
                         ruta_i, tiempo_ruta, tamaño, inclinacion, inclinacion_modulo,
                         campo_visual_H, save)
        trayectos_procesados.append(ruta_i)

    # Creamos unas variables de energía y una estructura
    irrad_media = pd.DataFrame({'Energia_GHI': [], 'Energia_POA': []})
    e_ghi, e_poa = [], []

    # Variable a emplear para definir tiempos de cada punto
    tiempos_ruta = []

    # Establecemos los tiempos de cada paso por las coordenadas
    for i in range(len(trayectos_procesados)):
        inicio = 0
        tiempo_entre_coord = []
        for j in range(len(trayectos_procesados[i])):
            tiempo_entre_coord.append(inicio)
            inicio += t_rutas[i]*60/len(trayectos_procesados[i])
        tiempos_ruta.append(tiempo_entre_coord)

    # Realizamos la integral de cada ruta para conseguir la energía de la ruta
    for i in range(len(trayectos_procesados)):
        e_ghi.append(np.trapz(trayectos_procesados[i]['GHI'], tiempos_ruta[i]))
        e_poa.append(np.trapz(trayectos_procesados[i]['POA'], tiempos_ruta[i]))

    # Se almacenan en una estructura de datos
    irrad_media['Energia_GHI'] = e_ghi
    irrad_media['Energia_POA'] = e_poa

    # Buscamos si hay varios valores repetidos
    if len(irrad_media) != len(set(irrad_media)):
        maximo = []

        # Procesamos buscando varias rutas que den la máxima energía
        for x in range(len(irrad_media)):
            if irrad_media['Energia_GHI'][x] == irrad_media['Energia_GHI'].max():
                maximo.append(x)

        # Si solo hay una ruta con valor máximo, lo imprimimos por consola y
        # lo devolvemos
        if len(maximo) == 1:
            print('\n\n\n La ruta más eficiente es la ruta', maximo[0]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[0]]/1000*0.000278), 'kWh/m^2.\n\n')
            return trayectos_procesados, trayectos_procesados[maximo[0]], irrad_media['Energia_GHI'][maximo[0]]/1000*0.000278, irrad_media['Energia_POA'][maximo[0]]/1000*0.000278

        # Si hay varias rutas con máxima energía
        else:
            t = 0
            for z in range(len(maximo)):
                # Buscamos la ruta más rápida
                if t_rutas[maximo[z]] < t_rutas[maximo[t]]:
                    t = z
            # Imrimimos y devolvemos la ruta más energética y más rápida
            print('\n\n\n La ruta más eficiente es la ruta', maximo[t]+1, ', con GHI de %.5f' % (
                irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][maximo[t]]/1000*0.000278), 'kWh/m^2.\n\n')
            return trayectos_procesados, trayectos_procesados[maximo[t]], irrad_media['Energia_GHI'][maximo[t]]/1000*0.000278, irrad_media['Energia_POA'][maximo[t]]/1000*0.000278

    # Si no hay valores repetidos
    elif len(irrad_media) == len(set(irrad_media)):
        for i in range(len(irrad_media)):
            # Imprimimos por consola y devolvemos la ruta con energía máxima
            if irrad_media['Energia_GHI'][i] == irrad_media['Energia_GHI'].max() and irrad_media['Energia_POA'][i] == irrad_media['Energia_POA'].max():
                print('\n\n\n La ruta más eficiente es la ruta', i+1, ', con GHI de %.5f' %
                      (irrad_media['Energia_GHI'][i]/1000*0.000278), 'kWh/m^2 y con POA de %.5f' % (irrad_media['Energia_POA'][i]/1000*0.000278), 'kWh/m^2.\n\n')
                return trayectos_procesados, trayectos_procesados[i], irrad_media['Energia_GHI'][i]/1000*0.000278, irrad_media['Energia_POA'][i]/1000*0.000278


# Función que representa gráficamente la potencia con respecto al tiempo

def grafica_Power_time(x, y, tipo):
    '''
    -----------------------------------------------
    --- Gráficas potencia irradiancia vs tiempo ---
    --------------------------------------------------------------------------

    Representa la potencia con respecto al tiempo.

    --------------------------------------------------------------------------


    Parámetros
    ----------
    x : list
        Lista de tiempos de la ruta.
    y : list
        Lista de potencias de la ruta.
    tipo : str
        Cadena que distingue entre potencia GHI y POA al poner los títulos
    
    Devolución
    -------
    Nada.

    '''
    # Ajustes representación valores
    plt.scatter(x,y,color='g',zorder=1)
    plt.plot(x,y,color='r',zorder=2)
    
    # Establemcemos título y nombre de los ejes
    if tipo == 'GHI':
        plt.title("Potencia irradiancia GHI en ruta")
    elif tipo == 'POA':
        plt.title("Potencia irradiancia POA en ruta")
    plt.xlabel("Tiempo")
    plt.ylabel("Irradiancia [W/m^2]")
    
    # Representamos gráfico
    plt.show()
    