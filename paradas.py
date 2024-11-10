import geopandas as gpd
import folium

# Cargar el archivo de paradas
paradas = gpd.read_file("data/paradas.geojson")

# Crear un mapa centrado en el área de las paradas
centro_mapa = [paradas.geometry.y.mean(), paradas.geometry.x.mean()]
mapa = folium.Map(location=centro_mapa, zoom_start=12)

# Agregar cada parada como marcador en el mapa
for _, row in paradas.iterrows():
    folium.Marker(
        location=[row.geometry.y, row.geometry.x],
        popup=f"Parada: {row['stop_name']}",
        icon=folium.Icon(color="blue")
    ).add_to(mapa)

# Guardar el mapa como archivo HTML
mapa.save("mapas/mapa_paradas.html")
