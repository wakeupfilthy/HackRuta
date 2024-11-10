import geopandas as gpd
import pandas as pd
import folium
import branca.colormap as cm

# Cargar los archivos GeoJSON
areas_censales = gpd.read_file('censo-2020-filtrado.geojson')
aforo = gpd.read_file("aforo-filtrado.geojson")  # Cargar el archivo de aforo como un GeoDataFrame

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

# Crear un mapa centrado en el área de interés
centro_mapa = [(lat_min + lat_max) / 2, (lon_min + lon_max) / 2]
mapa = folium.Map(location=centro_mapa, zoom_start=12)

# Crear un mapa de colores basado en el valor de up_net
min_up_net = areas_censales["up_net"].min()
max_up_net = areas_censales["up_net"].max()
colormap = cm.LinearColormap(colors=['blue', 'purple', 'red'], vmin=min_up_net, vmax=max_up_net, caption="Ascenso de Pasajeros (up_net) los Lunes")

# Agregar áreas censales al mapa con color según el valor de up_net
for _, row in areas_censales.iterrows():
    up_net = row["up_net"]
    color = colormap(up_net) if pd.notna(up_net) else "#808080"  # Color gris si no hay datos
    
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

# Guardar el mapa en un archivo HTML
mapa.save("mapa_up_net_lunes.html")
