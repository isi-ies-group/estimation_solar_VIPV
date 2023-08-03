# -*- coding: utf-8 -*-
"""
Created on Tue May 23 19:40:02 2023

@author: Ruben
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
import google_streetview.api
from pvlib import solarposition

from core import PhotoProjection
from image_aux import draw_solar_path, draw_lines_aux
import masks

# %% params
PATH_FIGURAS_PAPER = 'figuras'

tz ='Europe/Madrid'
lat, lon = 40.4537039, -3.7267926  # IES atras fila3
foto_ancho, foto_alto = 640, 480  # max 640x640 pixels
dia_fotos = '2022-02-21'


def descarga_imagen_api(heading, pitch, fov):
    gsv_params = {
        'size': f'{foto_ancho}x{foto_alto}',
        'location': f'{lat},{lon}',
        'heading': str(heading),
        'pitch': str(pitch),
        'fov': str(fov),
        'key': 'GCV_KEY'
    }

    # Create a results object
    results = google_streetview.api.results([gsv_params])
    results.download_links(PATH_FIGURAS_PAPER)
    print(results.metadata[0]['date'])
    print('Lugar exacto toma foto', results.metadata[0]['location'])

    return results

def pinta_sunpath(ax, lista_fechas_pintar, color=None):

    times = pd.date_range('2019-01-01 00:00:00', '2020-01-01', inclusive='left',
                          freq='H', tz=tz)

    solpos = solarposition.get_solarposition(times, lat, lon)
    # remove nighttime
    solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]
    
    ax.scatter(solpos.azimuth, solpos.apparent_elevation, s=0.1, marker= '.', 
                        color='black', label=None)
    
    # for hour in np.unique(solpos.index.hour):
    #     # choose label position by the largest elevation for each hour
    #     subset = solpos.loc[solpos.index.hour == hour, :]
    #     height = subset.apparent_elevation
    #     pos = solpos.loc[height.idxmax(), :]
    #     ax.text(pos['azimuth'], pos['apparent_elevation'], str(hour))
    
    for date in pd.to_datetime(lista_fechas_pintar):
        times = pd.date_range(date, date+pd.Timedelta('24h'), freq='5min', tz=tz)
        solpos = solarposition.get_solarposition(times, lat, lon)
        solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]
        label = date.strftime('%m-%d')
        ax.plot(solpos.azimuth, solpos.apparent_elevation, color=color, label=label)
    
    ax.plot([0, 360], [0, 0], ':', color='black')
    
    # ax.figure.legend(loc='upper left')
    ax.set_xlabel('Solar Azimuth [°]')
    ax.set_ylabel('Solar Elevation [°]')

def pinta_campo_visual(foto_proyeccion, ax, color, alpha):
    u, v = np.meshgrid(np.arange(start=0, stop=640+1, step=5),
                       np.arange(start=0, stop=480+1, step=5))
    h, p = foto_proyeccion.pixels2vectors(u, v)
    h[h < 0] = h[h < 0]+360 # pixels2vectors devuelve valores negativos
    
    ax.plot(h, p, marker='', color=color, alpha=alpha)


def genera_image_fig(heading, pitch, subfig):
    # Define parameters for street view api
    fov = 90  # GoPro-like 70º, movil a 1:1 lente Wide 53º, 4:3 lente UW 96º
    results = descarga_imagen_api(heading, pitch, fov)

    nombre_fichero = f'figura 1 - {subfig}'
    fig, ax = plt.subplots(figsize=(foto_ancho, foto_alto))
    imagen_compuesta_0 = Image.open(
        f'{PATH_FIGURAS_PAPER}/{results.metadata[0]["_file"]}').resize((foto_ancho, foto_alto))
    ax.imshow(imagen_compuesta_0)

    plt.axis('off')


heading = 180
pitch = 45
fov = 90

results = descarga_imagen_api(heading=heading, pitch=pitch, fov=fov)

fig, ax6 = plt.subplots(figsize=(foto_ancho, foto_alto))
ax6.imshow(plt.imread(f'{PATH_FIGURAS_PAPER}/gsv_0.jpg'))

proyeccion_foto_compuesta = PhotoProjection(fov=fov, width=foto_ancho, height=foto_alto, h0=heading, p0=pitch)

solpos = solarposition.get_solarposition(pd.Timestamp('2022-06-15T12H50', tz=tz), lat, lon)

u, v = proyeccion_foto_compuesta.vectors2pixels(solpos.azimuth, solpos.apparent_elevation)

ax6.plot(u, v, color='yellow', marker='o', markersize=50)
ax6.plot(u, v, color='red', marker='o', markersize=10)
ax6.annotate('[u,v]', xy=(u+25, v),
            xycoords='data', annotation_clip=False, fontsize=30, va='center', color='red')

ax6.plot(foto_ancho/2, foto_alto/2, color='black', marker='o', markersize=10)
ax6.annotate('[0,0]', xy=(foto_ancho/2+25, foto_alto/2),
            xycoords='data', annotation_clip=False, fontsize=30, va='center')

plt.axis('off')

