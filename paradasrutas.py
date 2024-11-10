import geopandas as gpd
import folium

# Cargar el archivo de paradas
paradas = gpd.read_file("data/paradas.geojson")
# Cargar el archivo de rutas
rutas = gpd.read_file("data/rutas.geojson")

# Crear un mapa centrado en el área de las paradas
centro_mapa = [paradas.geometry.y.mean(), paradas.geometry.x.mean()]
mapa = folium.Map(location=centro_mapa, zoom_start=12)

# Agregar cada parada como CircleMarker en el mapa con tamaño y color ajustados
for _, row in paradas.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,  # Tamaño pequeño del marcador
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.8,
        popup=f"Parada: {row['stop_name']}"
    ).add_to(mapa)

# Agregar las rutas como capas de líneas
for _, route in rutas.iterrows():
    folium.GeoJson(
        route.geometry,
        name=f"Ruta {route['route_short_name']}",
        tooltip=route['route_long_name'],
        style_function=lambda x: {'color': 'blue', 'weight': 2}  # Color y grosor de la línea
    ).add_to(mapa)

# Guardar el mapa como archivo HTML
mapa.save("mapas/mapa_paradas_rutas.html")
