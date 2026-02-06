import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="RLV Maps", layout="wide")

st.title("🗺️ RLV Spatial Planning Maps")

st.markdown("Visualize village resources, land types and development plans.")

uploaded_file = st.file_uploader("Upload GeoJSON or KML file", type=["geojson","json","kml"])

if uploaded_file is not None:

    if uploaded_file.name.endswith(".kml"):
        gdf = gpd.read_file(uploaded_file, driver='KML')
    else:
        gdf = gpd.read_file(uploaded_file)

    st.success("Map loaded successfully!")

    # Convert CRS to WGS84
    gdf = gdf.to_crs(epsg=4326)

    # Create base map
    m = folium.Map(location=[gdf.geometry.centroid.y.mean(),
                             gdf.geometry.centroid.x.mean()],
                   zoom_start=12)

    folium.GeoJson(
    gdf,
    name="Village Boundaries",
    tooltip=folium.GeoJsonTooltip(
        fields=["village", "mandal", "panchayath"],
        aliases=["Village:", "Mandal:", "Panchayath:"]
    ),
    style_function=lambda x: {
        "fillColor": "#3186cc",
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.6,
    }
).add_to(m)

    st_folium(m, width=1200, height=600)

