# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 09:32:11 2022

@author: Ruben
"""
import pandas as pd
from pvlib import solarposition
from PIL import Image
import cv2
import numpy as np

def draw_solar_path(ax, object, coordinates, list_dates_draw, color=None, show_lines=True):
    
    lat, lon = coordinates
    
    if show_lines:
        a = np.arange(start=-70, stop=70+1, step=1)
        for ang in np.arange(start=-70, stop=70+1, step=5):
            u, v = object.vectors2pixels(a, ang)
            ax.plot(u, v, color='black', linewidth=0.5, linestyle=':')
            u, v = object.vectors2pixels(ang, a)
            ax.plot(u, v, color='black', linewidth=0.5, linestyle=':')

    for date in pd.to_datetime(list_dates_draw):
        times = pd.date_range(
            date, date+pd.Timedelta('24h'), freq='5min', tz='Europe/Madrid')
        solpos = solarposition.get_solarposition(times, lat, lon)
        solpos = solpos.loc[solpos['apparent_elevation'] > 0, :]
        label = date.strftime('%Y-%m-%d')

        u, v = object.vectors2pixels(solpos.azimuth, solpos.apparent_elevation)
        h, p = object.pixels2vectors(u, v)
        u = u.loc[p > 0]
        v = v.loc[p > 0]

        ax.plot(u, v, '.', label=label, color=color)
        
        for ui, vi, hora in zip(u[::7], v[::7], v[::7].index.time):
            ax.plot(ui, vi, 'o', color='white')
            # ax.annotate('{0:.0f},{1:.0f}'.format(
            #     *object.pixels2vectors(ui, vi)), (ui, vi), color='black')
            ax.annotate(hora.strftime("%H:%M"), (ui, vi), color='black', fontsize=15)

    ax.set_xlim(0, object.width)
    ax.set_ylim(object.height, 0)


def draw_lines_aux(ax, object, lw=0.5, color='red'):
    ax.plot([0, object.width], [0, object.height], lw=lw, color=color)
    ax.plot([0, object.width], [object.height, 0], lw=lw, color=color)
    
    for step in range(6):
        step +=1
        ax.plot([object.width*step/6, object.width*step/6], [0, object.height], lw=lw, color=color)
        ax.plot([0, object.width], [object.height*step/6, object.height*step/6], lw=lw, color=color)

def cut_image_sun(file, object):
    image = cv2.imread(file)
    image = cv2.resize(image, (object.width, object.height))

    orig = image.copy()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # apply a Gaussian blur to the image then find the brightest region
    radius = 25

    gray = cv2.GaussianBlur(gray, (radius, radius), 0)
    (minVal, maxVal, minLoc, sun_position_centro) = cv2.minMaxLoc(gray)

    image2 = orig.copy()
    sun_cut = Image.fromarray(cv2.cvtColor(image2, cv2.COLOR_BGR2RGB))

    sun_position = (sun_position_centro[0]-radius, sun_position_centro[1]-radius,
                    sun_position_centro[0]+radius, sun_position_centro[1]+radius)
    sun_cut = sun_cut.crop(sun_position)

    return sun_cut, sun_position
