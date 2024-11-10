import geopandas as gpd
import folium
import branca.colormap as cm

# Cargar los archivos GeoJSON
areas_censales = gpd.read_file('censo-2020-filtrado.geojson')
paradas = gpd.read_file('data/paradas.geojson')

# Limitar los datos a una región específica (ajusta según tu región de interés)
lat_min, lat_max = 20.7, 21.3
lon_min, lon_max = -90.0, -88.5
areas_censales = areas_censales.cx[lon_min:lon_max, lat_min:lat_max]
paradas = paradas.cx[lon_min:lon_max, lat_min:lat_max]

# Crear un mapa centrado en el área de interés
centro_mapa = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
mapa = folium.Map(location=centro_mapa, zoom_start=12)

# Crear un mapa de colores basado en la densidad poblacional
columna_densidad = 'POBTOT'  # Cambia esta columna si es otra en tu archivo
min_densidad = areas_censales[columna_densidad].min()
max_densidad = areas_censales[columna_densidad].max()
colormap = cm.LinearColormap(colors=['green', 'yellow', 'red'], vmin=min_densidad, vmax=max_densidad, caption="Densidad Poblacional")

# Agregar áreas censales al mapa con color según la densidad poblacional
for _, row in areas_censales.iterrows():
    densidad = row[columna_densidad]
    color = colormap(densidad)
    
    # Convertir la geometría en formato JSON y agregar al mapa como GeoJson
    folium.GeoJson(
        row['geometry'],
        style_function=lambda feature, color=color: {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.5
        }
    ).add_to(mapa)

# Agregar la leyenda del mapa de colores
colormap.add_to(mapa)

# Agregar cada parada como marcador en el mapa
for _, row in paradas.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.8,
        popup=f"Parada: {row['stop_name']}"
    ).add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save("mapa_interactivo_densidad.html")
