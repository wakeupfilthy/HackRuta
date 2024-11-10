import geopandas as gpd
import folium
import branca.colormap as cm
import pandas as pd

# Cargar los archivos GeoJSON
areas_censales = gpd.read_file('censo-2020-filtrado.geojson')
paradas = gpd.read_file('data/paradas.geojson')
rutas = gpd.read_file('data/rutas.geojson')  # Cargar las rutas de transporte
aforo = gpd.read_file("aforo-filtrado.geojson")  # Archivo de aforo

# Filtrar el GeoDataFrame de aforo para solo incluir los registros de los días lunes
aforo = aforo[aforo["dia"] == "lunes"]

# Agrupar los datos de aforo por CVE_AGEB para obtener la suma de up_net en cada AGEB los lunes
aforo_agg = aforo.groupby("CVE_AGEB")["up_net"].sum().reset_index()

# Unir el DataFrame de aforo con el GeoDataFrame de las áreas censales por el ID de AGEB
areas_censales = areas_censales.merge(aforo_agg, left_on="CVE_AGEB", right_on="CVE_AGEB", how="left")

# Limitar los datos a una región específica
lat_min, lat_max = 20.7, 21.3
lon_min, lon_max = -90.0, -88.5
areas_censales = areas_censales.cx[lon_min:lon_max, lat_min:lat_max]
paradas = paradas.cx[lon_min:lon_max, lat_min:lat_max]
rutas = rutas.cx[lon_min:lon_max, lat_min:lat_max]

# Crear un mapa centrado en el área de interés
centro_mapa = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
mapa = folium.Map(location=centro_mapa, zoom_start=12)

# Crear colormap para la densidad poblacional
columna_densidad = 'POBTOT'
min_densidad = areas_censales[columna_densidad].min()
max_densidad = areas_censales[columna_densidad].max()
colormap_densidad = cm.LinearColormap(colors=['green', 'yellow', 'red'], vmin=min_densidad, vmax=max_densidad, caption="Densidad Poblacional")

# Crear colormap para ascenso de pasajeros (up_net)
min_up_net = areas_censales["up_net"].min()
max_up_net = areas_censales["up_net"].max()
colormap_up_net = cm.LinearColormap(colors=['blue', 'purple', 'red'], vmin=min_up_net, vmax=max_up_net, caption="Ascenso de Pasajeros (up_net) los Lunes")

# Capa para visualizar densidad poblacional
densidad_layer = folium.FeatureGroup(name="Densidad Poblacional")
for _, row in areas_censales.iterrows():
    densidad = row[columna_densidad]
    color = colormap_densidad(densidad)
    folium.GeoJson(
        row['geometry'],
        style_function=lambda feature, color=color: {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.5
        }
    ).add_to(densidad_layer)
densidad_layer.add_to(mapa)

# Capa para visualizar el ascenso de pasajeros (up_net)
up_net_layer = folium.FeatureGroup(name="Ascenso de Pasajeros (up_net) los Lunes")
for _, row in areas_censales.iterrows():
    up_net = row["up_net"]
    color = colormap_up_net(up_net) if pd.notna(up_net) else "#808080"  # Gris si no hay datos
    folium.GeoJson(
        row['geometry'],
        style_function=lambda feature, color=color: {
            'fillColor': color,
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.5
        }
    ).add_to(up_net_layer)
up_net_layer.add_to(mapa)

# Capa para paradas de transporte
paradas_layer = folium.FeatureGroup(name="Paradas de Transporte")
for _, row in paradas.iterrows():
    folium.CircleMarker(
        location=[row.geometry.y, row.geometry.x],
        radius=3,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.8,
        popup=f"Parada: {row['stop_name']}"
    ).add_to(paradas_layer)
paradas_layer.add_to(mapa)

# Capa para las rutas de transporte
rutas_layer = folium.FeatureGroup(name="Rutas de Transporte")
for _, route in rutas.iterrows():
    folium.GeoJson(
        route.geometry,
        name=f"Ruta {route['route_short_name']}",
        tooltip=route['route_long_name'],
        style_function=lambda x: {'color': 'blue', 'weight': 2}
    ).add_to(rutas_layer)
rutas_layer.add_to(mapa)

# Agregar las leyendas de cada capa
colormap_densidad.add_to(mapa)
colormap_up_net.add_to(mapa)

# Agregar control de capas al mapa
folium.LayerControl().add_to(mapa)

# Guardar el mapa en un archivo HTML
mapa.save("mapas/mapa_combined_con_rutas.html")
