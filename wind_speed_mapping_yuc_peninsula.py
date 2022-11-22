# -*- coding: utf-8 -*-
"""Notebook-resuelto.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1D_ZRp8Xw1jdtimIRV3T3RqeQ8wPWW53K

# Introducción - Setup
Se importó todo lo que tenía el Notebook anterior a Google Colab para poder trabajarlo en una nube y no usar recursos propios. Se configuró el documento en Colab para acomodar las librerías utilizadas.
"""

from google.colab import drive
drive.mount('/content/drive')

"""Aquí se importan las librerías y las mediciones que utilizamos para la creación de los mapas. Todas las librerías que utilizamos estaban ya instaladas en la nube de Google excepto Cartopy."""

!pip install cartopy

"""Se cambió la librería shapely porque provocaba conflictos con Cartopy, pues la versión no era compatible."""

!pip uninstall shapely

"""Se instala la antigua versión compatible."""

!pip install shapely --no-binary shapely

import xarray as xr #Manejo de netcdfs
import numpy as np #Manejo de matrices n-dimensionales
import cartopy.crs as ccrs #Sistema de referencia de coordenadas para los mapas
import cartopy.feature as cfeature #Características de los mapas
import matplotlib.pyplot as plt #Gráficos

data = xr.open_dataset("/content/drive/MyDrive/Colab_Notebooks/era_2020.nc") 
data

"""# Ejercicio 3.1
*Utiliza el mismo netcdf, a partir de las componentes horizontales a 10 m obten la rapidez del viento a esa altura. Utiliza la ley de potencias para extrapolar de 10 a 90 m, considera $\alpha=1/7$*
$$U(z)=U(z_r)\left(\frac{z}{z_r}\right)^{1/7}$$
Donde: <br>
z = Altura a la que se desea extrapolar <br>
zr = velocidad de referencia <br>
Uzr = Velocidad del viento a extrapolar a la altura zr <br>
Uz = velocidad estimada a la altura z <br>

###Paso 1
Obtenemos una nueva variable utilizando los datos U10 y V10 llamada WS10. Se segmentó la operación para evitar el operador `**` y se reemplazó por el método *.sqrt* de numpy.
"""

data["ws10"] = data["u10"]*data["u10"]
data["ws10"] += data["v10"]*data["v10"]
data["ws10"] = np.sqrt(data["ws10"])
data

"""###Paso 2
Ahora implementamos la ley de potencias para extrapolar. $$U(z)=U(z_r)\left(\frac{z}{z_r}\right)^{1/7}$$
"""

# z = Altura a la que se desea extrapolar (90)
z = 90
zr = 10
Uzr = data["ws10"]
Uz = np.power(z/zr, (1/7))
Uz = Uz * Uzr
# Se guardaron las velocidades en la variable ws90 del arreglo
data["ws90"] = Uz
data

"""# Ejercicio 3.2
*Realiza dos mapas de las velocidades extrapoladas a 90 m, acota el área de la gráfica únicamente para la Península de Yucatán. El primer mapa será para el promedio mensual de agosto y el segundo mapa será para el promedio mensual de diciembre. Verifica que ambos mapas tengan el mismo intervalo de velocidades para la visualización del colorbar.*

###Paso 1
Elegimos las longitudes y latitudes de la península de Yucatán.
"""

lons_yuc = np.array(data.longitude[128:128+29])
lats_yuc = np.array(data.latitude[48:48+37])
lons_yuc, lats_yuc

"""###Paso 2
Creamos dos arreglos promedidados en el eje del tiempo con las velocidades extrapoladas a 90m en los meses de agosto y diciembre llamados `ws90_mean_08` y `ws90_mean_12` respectivamente.
"""

# Se crean los marcadores que segmentan los datos temporales
# en el dataframe por cada mes para facilitar la recuperación
# de los datos para los otros meses

i_jan = (0,743)
i_feb = (744,1439)
i_mar =(1440,2183)
i_apr = (2184,2903)
i_may = (2904,3647)
i_jun = (3648,4367)
i_jul = (4368,5111)
i_aug = (5112,5855)
i_sep = (5856,6575)
i_oct = (6576,7319)
i_nov = (7320,8039)
i_dic = (8040,8783)

ws90_mean_08 = data["ws90"][i_aug[0]:i_aug[1]+1]
ws90_mean_08 = ws90_mean_08.mean(axis=0)
ws90_mean_08

"""###Paso 3
Seleccionamos las latitudes y longitudes pertenecientes a Yucatán y las guardamos en una nueva variable.
"""

ws90_mean_08_yuc = np.array(ws90_mean_08[48:48+lats_yuc.size, 128:128+lons_yuc.size])
ws90_mean_08_yuc.shape

"""###Paso 4
Con esos datos se proyecta la información al mapa de la península de Yucatán.
"""

plt.figure(figsize=(12,6))
ax = plt.axes(projection=ccrs.PlateCarree()) #Proyección del mapa 
##https://scitools.org.uk/cartopy/docs/v0.15/crs/projections.html

ax.set_extent([267,274,23,14]) #Límites del mapa [longitudes, latitudes]
ax.coastlines(resolution="10m")
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.STATES.with_scale("10m"))# Límites de los países
ax.set_title(f"Velocidad promediada a 90m - agosto ({lons_yuc[0]}-{lons_yuc[-1]}  ,  {lats_yuc[0]}-{lats_yuc[-1]})")

#Malla de los datos, utilizando vmax para modificar la barra de colores
p = ax.pcolormesh(lons_yuc, lats_yuc, ws90_mean_08_yuc, cmap='jet', transform=ccrs.PlateCarree(), vmax=11, vmin=0) 
plt.colorbar(p, shrink=0.8) #Barra de colores

"""Se repiten los pasos para el mes de diciembre."""

ws90_mean_12 = data["ws90"][i_dic[0]:i_dic[1]+1]
ws90_mean_12 = ws90_mean_12.mean(axis=0)
ws90_mean_12_yuc = np.array(ws90_mean_12[48:48+lats_yuc.size,128:128+lons_yuc.size])
plt.figure(figsize=(12,6))
ax = plt.axes(projection =ccrs.PlateCarree())
ax.set_extent([267,274,23,14])
ax.coastlines(resolution="10m")
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.STATES.with_scale("10m"))
ax.set_title(f"Velocidad promediada a 90m - diciembre ({lons_yuc[0]}-{lons_yuc[-1]}  ,  {lats_yuc[0]}-{lats_yuc[-1]})")
p = ax.pcolormesh(lons_yuc, lats_yuc, ws90_mean_12_yuc, cmap="jet", transform =ccrs.PlateCarree(),vmax=11, vmin=0)
plt.colorbar(p, shrink=0.8)

"""#Ejercicio 3.3
*Selecciona un punto al norte de Yucatán dentro del océano. Realiza un mapa del promedio anual de las velocidades y muestra el punto que seleccionaste.*

###Paso 1
Se define el punto elegido al norte de Yucatán (272.00, 21.75).
"""

plt.figure(figsize=(12,6))
ax = plt.axes(projection =ccrs.PlateCarree())
ax.set_extent([267,274,23,14])
ax.coastlines(resolution="10m")
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.STATES.with_scale("10m"))
ax.set_title("Punto a evaluar        (272.00, 21.75)")
ax.plot(272, 21.75, marker='.', transform=cartopy.crs.PlateCarree(), markersize=10, color='blue')

"""##Paso 2
Se divide el dataframe a la región a analizar.
"""

ws90_mean_punto = data.sel(dict(latitude=slice(22.5,21.5), longitude = slice(271, 273)))
lons_yuc_punto = np.array(ws90_mean_punto.longitude)
lats_yuc_punto = np.array(ws90_mean_punto.latitude)
ws90_mean_punto = ws90_mean_punto["ws90"]
ws90_mean_punto = ws90_mean_punto.mean(axis=0)
ws90_mean_punto.shape

"""##Paso 3

Se superponen las medidas sobre el mapa definido.
"""

plt.figure(figsize=(12,6))
ax = plt.axes(projection =ccrs.PlateCarree())
ax.set_extent([271, 273, 22.5, 21.5])
ax.coastlines(resolution="10m")
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.STATES.with_scale("10m"))
ax.set_title(f"Velocidad anual promediada a 90m                         ({lons_yuc_punto[0]}-{lons_yuc_punto[-1]}  ,  {lats_yuc_punto[0]}-{lats_yuc_punto[-1]})")
p = ax.pcolormesh(lons_yuc_punto, lats_yuc_punto, ws90_mean_punto, cmap="jet", transform =ccrs.PlateCarree(),vmax=11, vmin=0)
ax.plot(272, 21.75, marker='o', transform=cartopy.crs.PlateCarree(), markersize=15, color='blue')
plt.colorbar(p, shrink=0.8)

"""#Ejercicio 3.4
*Para el punto que seleccionaste interpola la velocidad a 90 metros. Grafica la serie temporal.*

###Paso 1
Se elige la variable interpolada del dataframe y se guarda en una nueva variable. Se eliminan las columnas que se mantienen constantes (`latitude, longitude`).
"""

punto = data.interp(latitude=21.75, longitude=272)
punto_ws90 = punto.ws90.to_dataframe()
punto_ws90.drop(labels=["latitude", "longitude"], axis=1, inplace=True)
punto_ws90

"""##Paso 2
Finalmente se grafica la serie temporal.
"""

fig, ax = plt.subplots(figsize=(15,5))
ax.plot(punto_ws90)
ax.set_xlabel("Tiempo")
ax.set_ylabel("Velocidad [m s$^{-1}$]")
