'''
----------------------------------------------------
--- EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR ---
------------------------------------------------------------------------------
'''

# Importa la libreria

from EvalRecSol import Gestor_rutas as gr
from EvalRecSol import Procesado_completo_imagenes as pci
from EvalRecSol import Irradiancia as i
from EvalRecSol import Mascaras_fotografias as mf
from EvalRecSol import Camino_solar as cs
from EvalRecSol import Gestion_fotografia as gf
from EvalRecSol import Utilidades_generales as ug
from pvlib import location
import datetime
import numpy as np
import pandas as pd


# Obtenemos la clave de la API de Google

clave = ug.obtener_clave_API('PASSWORD.txt')


'''
---------------------------------------------
--- Parámetros ubicación, cámara  y fechas ---
---------------------------------------------
Definimos los parámetros a emplear durante la ejecucción.

- Dimensiones de la fotografía, siendo el máximo 640x640 píxeles que genera la 
API de Google Street View.
- Coordenadas de la ubicación, la latitud, la longitud y la orientación de la 
imagen (Orientación N(0), E(90), S(180), O(270)).
- Zona horaria de la ubicación, emplearemos la zona horaria de Madrid y la 
península.
- Inclinación de la lente para ajustar el horizonte al borde inferior.
- Establecemos el campo de visión horizontal que nos devolverá la API de 
Google Street View.
- Al ser las coordenadas del azimuth solar diferentes de las de una brujula, 
realizaremos un cambio de referencia.
- Definimos la fecha y el periodo de tiempo entre cada punto a obtener la 
posición del sol.
- Consideraremos que los módulos se encuentran a una inclinación 
predeterminada
'''

# Datos empleados de la fotografia

# p_h = 640  # Número de pixeles horizontal - máx 640 píxeles
# p_v = 640  # Número de pixeles vertical - máx 640 píxeles
# tamaño = str(p_h)+'x' + str(p_v)  # Tamaño imagen - máx 640x640 píxeles

# Datos empleados de la ubicacción

# lat, lon = 40.4168838, -3.6783211  # Latitud y Longitud
# lat, lon = 40.4365999,-3.5970465  # Latitud y Longitud
# localizacion = str(lat) + ',' + str(lon)
# rumbo = 18  # Orientación N(0), E(90), S(180), O(270)

# Zona horaria

# zona_horaria = 'Europe/Madrid'

# Creación objeto para almacenar latitud, longitud y zona horaria

# site = location.Location(lat, lon, tz=zona_horaria)

# Datos empleados de la cámara

# inclinacion = 45  # Inclinación lente
# campo_visual_H = 90  # Campo de visión horizontal

# Cambio de referencia en brújula
# Dirección --> Sur (0°), Este(90°), Norte (180°) y Oeste (270°)

# direccion = (180 - rumbo) % 360

# Inclinación superficie módulos fotovoltáicos

# inclinacion_modulo = 25


'''
-------------
--- Rutas ---
-------------
'''

Ruta_A_i = pd.read_csv('rutas\Ruta_A_irradiancia', index_col=False)
Ruta_B_i = pd.read_csv('rutas\Ruta_B_irradiancia', index_col=False)
Ruta_C_i = pd.read_csv('rutas\Ruta_C_irradiancia', index_col=False)
Rutas_i = [Ruta_A_i, Ruta_B_i, Ruta_C_i]
tiempo_rutas_i = [16, 16, 26]  # En minutos

# Ruta_A = pd.read_csv('rutas\Ruta_A', index_col=False)
# Ruta_B = pd.read_csv('rutas\Ruta_B', index_col=False)
# Ruta_C = pd.read_csv('rutas\Ruta_C', index_col=False)
# Rutas = [Ruta_A, Ruta_B, Ruta_C]
# tiempo_rutas = [16, 16, 26]  # En minutos

# Rutas = [Ruta_A, Ruta_B]
# tiempo_rutas = [16, 16]  # En minutos
# Rutas = pd.read_csv('rutas\Ruta_C', index_col=False)
# tiempo_rutas = 26

# Rutas = pd.read_csv('rutas\Ruta_test_B', index_col=False)
# tiempo_rutas = 16


'''
--------------
--- Tiempo ---
--------------
'''

# inicio = datetime.datetime.today()
# inicio = datetime.datetime(2021, 5, 13, 11, 50, 54)
# fin = inicio + datetime.timedelta(minutes=tiempo_rutas)

# Valores de fechas toma fotos Street View

# inicio = datetime.datetime(2021, 9, 7, 0, 0, 0)  # Inicio (Y,M,D,h,m,s)
# fin = datetime.datetime(2021, 9, 8, 0, 0, 0)  # Fin (Y,M,D,h,m,s)
# periodo = '1min'  # Valor de periodo en minutos


'''
------------------------
--- Guardar imagenes ---
------------------------
'''

# Guardar imagen si save es 'True'

# save = False


'''
-----------------------
--- API Street View ---
-----------------------
'''

# Define parametros para Google Street View api

# params = [{
#     'size': tamaño,  # Tamaño imagen - max 640x640 pixels
#     'location': localizacion,  # Coordenadas polares
#     'heading': rumbo,  # Orientación N(0), E(90), S(180), O(270)
#     'pitch': inclinacion,  # Inclinación lente
#     'fov': campo_visual_H,  # Campo de visión horizontal
#     'key': clave
# }]


'''
---------------------------------
--- Procesado de única imagen ---
------------------------------------------------------------------------------
'''

# LLamada a la función para obtener la imagen de Street View

# gf._obtencion_foto_SW(params)

# LLamada a la función para ver la imagen de Street View

# Foto = gf._get_path_foto()

# Ejecutamos la función que muestra las dimensiones de la fotografía

# gf._dimensiones_imagen(Foto)

# Llamada a la función que representa el diagrama solar anual

# cs.diagrama_solar(site)

# Ejecutamos la función que obtiene el camino del Sol en una imagen

# img, puntosSol = cs.caminoSolar(mf.mask_unica(
#     Foto), site, direccion, inicio, fin, periodo)

# Empleamos la función para obtener los datos a una inclinación determinada
# y con la orientación de la foto

# irradiancia_dia = i._get_irradiance(
#     site, inicio, periodo, inclinacion_modulo, rumbo, np.array(puntosSol['Fecha y hora']), puntosSol)

# Ejecucción de la función que representa la irradiancia diaria

# i.representar_Irradiancia(irradiancia_dia)

# Llamada a la función para ver la imagen procesada y guardarla

# ug._mostrar_resultado(img)

# Llamada a la función que pinta el camino solar en la imagen de Street View

# cs._camino_en_imagenSV(puntosSol, Foto)


'''
---------------------------------------
--- Procesado de múltiples imágenes ---
------------------------------------------------------------------------------
'''

# Obtenemos en una estructura de datos todos los puntos por los que pasa el
# sol, procesando imágenes orientadas a Este, Sureste, Sur, Suroeste y Oeste.

# puntos_Sol = pci.de_Este_a_Oeste(
#     params, site, direccion, inicio, fin, periodo, inclinacion_modulo, save)

# Ejecucción de la función que representa la irradiancia diaria para el
# procesado múltiple de imágnes

# i.representar_Irradiancia(i._get_irradiance_day(
#     site, inicio, periodo, inclinacion_modulo, rumbo, np.array(puntos_Sol['Fecha y hora']), puntos_Sol))

# Ejecutamos la función de cierre de las ventanas

# ug._cierre_ventanas()


'''
---------------------------
--- Ruta más energética ---
------------------------------------------------------------------------------
'''

# Obtenemos la ruta más energética para un mismo trayecto

# Ruta_ef, GHI_M, POA_M = gr.ruta_eficiente_irradiancia(
#     clave, inicio, fin, Rutas, tiempo_rutas, tamaño, inclinacion, inclinacion_modulo, campo_visual_H, save)

# Procesado de una ruta

# gr.irradiancia_ruta(clave, inicio, fin, Rutas, tiempo_rutas, tamaño,
#                     inclinacion, inclinacion_modulo, campo_visual_H, save)

# Obtención de la ruta más eficiente pasando las rutas procesadas

Ruta_eficiente, GHI_max, POA_max, GHI_all, POA_all = gr.ruta_eficiente_sin_procesado(
    Rutas_i, tiempo_rutas_i)


'''
---------------------------------
--- Datos procesamiento rutas ---
------------------------------------------------------------------------------
'''

# Comienzo de la ruta

# instante = datetime.datetime.today()
# instante = datetime.datetime(2022, 5, 13, 11, 50, 54)

# Direcciones de la ruta

# dir_ini = 'Taco Bell, Plaza del Emperador Carlos V, 11, 28012 Madrid'
# dir_fin = 'WiZink Center, Av. Felipe II, s/n, 28009 Madrid'
# dir_fin = 'Only YOU Hotel Atocha, Paseo de la Infanta Isabel, 13, 28014 Madrid'

# dir_ini = 'Ronda de Valencia, 3, 28012 Madrid'
# dir_fin = 'Calle de José Gutiérrez Abascal, 2, 28006 Madrid'

# Obtenemos las posibles rutas entre ambas coordenadas de inicio y meta

# trayectos = gr.rutas_GMaps(clave, dir_ini, dir_fin, instante)


'''
----------------------------------------------
--- Obtención rutas procesadas automaticas ---
----------------------------------------------
'''

# Obtenemos las posibles rutas entre ambas coordenadas de inicio y meta con
# las irradiancias de cada punto

# trayectos_irradiantes, ruta_energetica, max_GHI, max_POA = gr.rutas_GMaps_irradiancias(
#     clave, dir_ini, dir_fin, instante, tamaño, inclinacion, campo_visual_H, inclinacion_modulo, save)


'''
----------------------------------------------------------
--- Obtención rutas procesadas automaticas rápidamente ---
----------------------------------------------------------
'''

# Obtenemos las posibles rutas entre ambas coordenadas de inicio y meta con
# las irradiancias de cada punto

# trayectos_irradiantes_rapido, ruta_energetica_rapido, max_GHI_rapido, max_POA_rapido = gr.rutas_GMaps_irradiancias_rapida(
#     clave, dir_ini, dir_fin, instante, tamaño, inclinacion, campo_visual_H, inclinacion_modulo, save)
