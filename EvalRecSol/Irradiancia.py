'''
---------------------------------------------------------------
--- LIBRERÍA - EVALUACIÓN DEL RECURSO SOLAR DEL COCHE SOLAR --- 
---                   MÓDULO DE IRRADIANCIA                 ---
---------------------------------------------------------------
'''
# Importa las librerias


from matplotlib import pyplot as plt
import pandas as pd
from pvlib import irradiance


# Calcula el GHI del cielo despejado y le transpone a la colección del plano


def _get_irradiance(site_location, date, periodo, tilt, surface_azimuth,
                    puntos, puntosSol):
    '''
    ------------------------------------
    --- Irradiancia esperada (W/m^2) ---
    --------------------------------------------------------------------------

    Mediante una función de la librería 'pvlib', obtendremos la irradiancia en 
    W / m^2 en la ubicación y fecha determinada. Obtendremos la irradiancia 
    durante un día en el caso de no haber ninguna sombra y considerando el 
    efecto de las sombras, tanto la Irradiancia Global Horizontal (GHI) como 
    la Irradiancia en un plano inclinado (POA). Se añadiran los valores de GHI 
    y POA de los puntos del camino solar a la estructura de datos.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    site_location :
        Estructura con los valores de la ubicación, latitud, longitud y 
        zona horaria
    date :
        Fecha y hora del inicio del camino solar
    periodo :
        Paso de tiempo entre los puntos del camino solar
    tilt :
        Inclinación de los módulos
    surface_azimuth :
        Orientación de los módulos
    puntos :
        Lista de fechas y horas del camino solar
    puntosSol :
        Estructura de datos con los puntos del camino solar sin sombra

    Devolución
    ----------
    DataFrame
        Estructura de datos con los puntos del camino solar y sus irradiancias

    '''

    # Casting de cadena a int para extracción de frecuencia
    frec = int(periodo[0])

    # Ajustamos las iteraciones para obtener un día completo
    iteraciones = (24*60)/frec

    # Crea un espacio de un día mediante intervalos de duración variable
    times = pd.date_range(date, freq=str(frec)+'min', periods=iteraciones,
                          tz=site_location.tz)

    # Genera los datos del cielo despejado empleando el modelo de
    # Ineichen, por defecto
    # El métoodo get_clearsky devuelve una estructura de datos con los
    # valores GHI, DNI y DHI
    clearsky = site_location.get_clearsky(times)

    # Obtenemos el azimuth y zenith solar para usarlo en la función
    # de transposición
    solar_position = site_location.get_solarposition(times=times)

    # Uso de la función get_total_irradiance para trasponer la GHI a POA
    POA_irradiance = irradiance.get_total_irradiance(surface_tilt=tilt,
                                                     surface_azimuth=surface_azimuth, dni=clearsky['dni'],
                                                     ghi=clearsky['ghi'], dhi=clearsky['dhi'],
                                                     solar_zenith=solar_position['apparent_zenith'],
                                                     solar_azimuth=solar_position['azimuth'])

    # Copia de las estructuras de datos obtenidas
    clearsky_sombra = clearsky.copy()
    POA_irradiance_sombra = POA_irradiance.copy()

    # Listas para añadir a la estructura de datos los valores de GHI y POA
    # de los puntos sin sombra
    GHI = []
    POA = []

    # Asignamos un '0' a los valores donde se producen sombras
    # Si los puntos no producen sombra, los incluimos en la lista para la
    # estuctura de datos
    for i in range(len(clearsky_sombra)):
        if clearsky_sombra.index[i] not in puntos:
            clearsky_sombra['ghi'][i] = 0
            clearsky_sombra['dni'][i] = 0
            clearsky_sombra['dhi'][i] = 0
        else:
            GHI.append(clearsky_sombra['ghi'][i])

    for i in range(len(POA_irradiance)):
        if POA_irradiance_sombra.index[i] not in puntos:
            POA_irradiance_sombra['poa_global'][i] = 0
            POA_irradiance_sombra['poa_direct'][i] = 0
            POA_irradiance_sombra['poa_diffuse'][i] = 0
            POA_irradiance_sombra['poa_sky_diffuse'][i] = 0
            POA_irradiance_sombra['poa_ground_diffuse'][i] = 0
        else:
            POA.append(POA_irradiance_sombra['poa_global'][i])

    # Añadimos las listas como columnsas a la estructura de datos
    puntosSol['GHI'] = GHI
    puntosSol['POA'] = POA

    # Devolvemos la estructura de datos con GHI y POA para el caso general
    # y con sommbra
    return pd.DataFrame({'GHI': clearsky['ghi'], 'POA':
                         POA_irradiance['poa_global'],
                         'GHI_shadow': clearsky_sombra['ghi'],
                         'POA_shadow': POA_irradiance_sombra['poa_global']})


# Calcula el GHI del cielo despejado para un día entero


def _get_irradiance_day(site_location, date, frec, tilt, surface_azimuth,
                        puntos, puntosSol):
    '''
    ------------------------------------
    --- Irradiancia esperada (W/m^2) ---
    --------------------------------------------------------------------------

    Mediante una función de la librería 'pvlib', obtendremos la irradiancia en 
    W / m^2 en la ubicación y fecha determinada. Obtendremos la irradiancia 
    durante un día en el caso de no haber ninguna sombra y considerando el 
    efecto de las sombras, tanto la Irradiancia Global Horizontal (GHI) como 
    la Irradiancia en un plano inclinado (POA). Se extraeran los valores de 
    GHI y POA de los puntos del camino solar de la estructura de datos 
    introducida. Nos permite ver la irradiancia de un día completo si la 
    empleamos con la función 'de_Este_a_Oeste()'.

    --------------------------------------------------------------------------

    Parámetros
    ----------
    site_location :
        Estructura con los valores de la ubicación, latitud, longitud y 
        zona horaria
    date :
        Fecha y hora del inicio del camino solar
    frec :
        Paso de tiempo entre los puntos del camino solar
    tilt :
        Inclinación de los módulos
    surface_azimuth :
        Orientación de los módulos
    puntos :
        Lista de fechas y horas del camino solar
    puntosSol :
        Estructura de datos con los puntos del camino solar sin sombra

    Devolución
    ----------
    DataFrame
        Estructura de datos con los puntos del camino solar y sus irradiancias

    '''

    # Casting de cadena a int para extracción de frecuencia
    frec = int(frec[0])

    # Ajustamos las iteraciones para obtener un día completo
    iteraciones = (24*60)/frec

    # Crea un espacio de un día mediante intervalos de duración variable
    times = pd.date_range(date, freq=str(frec)+'min', periods=iteraciones,
                          tz=site_location.tz)

    # Genera los datos del cielo despejado empleando el modelo de
    # Ineichen, por defecto
    # El métoodo get_clearsky devuelve una estructura de datos con los
    # valores GHI, DNI y DHI
    clearsky = site_location.get_clearsky(times)

    # Obtenemos el azimuth y zenith solar para usarlo en la función
    # de transposición
    solar_position = site_location.get_solarposition(times=times)

    # Uso de la función get_total_irradiance para trasponer la GHI a POA
    POA_irradiance = irradiance.get_total_irradiance(surface_tilt=tilt,
                                                     surface_azimuth=surface_azimuth, dni=clearsky['dni'],
                                                     ghi=clearsky['ghi'], dhi=clearsky['dhi'],
                                                     solar_zenith=solar_position['apparent_zenith'],
                                                     solar_azimuth=solar_position['azimuth'])

    # Copia de las estructuras de datos obtenidas
    clearsky_sombra = clearsky.copy()
    POA_irradiance_sombra = POA_irradiance.copy()

    # Asignamos un '0' a los valores donde se producen sombras
    # Si los puntos no producen sombra, los incluimos en la lista para la
    # estuctura de datos
    for i in range(len(clearsky_sombra)):
        if clearsky_sombra.index[i] not in puntos:
            clearsky_sombra['ghi'][i] = 0
            clearsky_sombra['dni'][i] = 0
            clearsky_sombra['dhi'][i] = 0

    for i in range(len(POA_irradiance)):
        if POA_irradiance_sombra.index[i] not in puntos:
            POA_irradiance_sombra['poa_global'][i] = 0
            POA_irradiance_sombra['poa_direct'][i] = 0
            POA_irradiance_sombra['poa_diffuse'][i] = 0
            POA_irradiance_sombra['poa_sky_diffuse'][i] = 0
            POA_irradiance_sombra['poa_ground_diffuse'][i] = 0

    # Devolvemos la estructura de datos con GHI y POA para el caso general
    # y con sommbra
    return pd.DataFrame({'GHI': clearsky['ghi'], 'POA':
                         POA_irradiance['poa_global'],
                         'GHI_shadow': clearsky_sombra['ghi'],
                         'POA_shadow': POA_irradiance_sombra['poa_global']})


# Función que representa gráficamente la irradiancia


def representar_Irradiancia(datos):
    '''
    ------------------------------------
    --- Irradiancia esperada (W/m^2) ---
    --------------------------------------------------------------------------

    Representaremos la irradiancia durante un día en el caso de no haber 
    ninguna sombra y considerando el efecto de las sombras, tanto la 
    Irradiancia Global Horizontal (GHI) como la Irradiancia en un plano 
    inclinado (POA).

    --------------------------------------------------------------------------

    Parámetros
    ----------
    datos :
        Estructura de datos del camino solar y sus irradiancias

    '''

    # Convertimios los índices de la estructura de datos a Hora:Minuto para
    # representar más fácilmente
    datos.index = datos.index.strftime("%H:%M")

    # Representación de GHI vs. POA de el día seleccionado
    fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)
    datos['GHI'].plot(ax=ax1, label='GHI')
    datos['POA'].plot(ax=ax1, label='POA')
    datos['GHI_shadow'].plot(ax=ax2, label='GHI')
    datos['POA_shadow'].plot(ax=ax2, label='POA')
    ax1.set_xlabel('Hora del día (Sin sombra)')
    ax2.set_xlabel('Hora del día (Con sombra)')
    ax1.set_ylabel('Irradiancia ($W/m^2$)')
    ax1.legend()
    ax2.legend()
    plt.show()
