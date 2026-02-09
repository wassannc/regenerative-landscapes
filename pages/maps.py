import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import json

st.set_page_config(page_title="RLV Maps", layout="wide")
st.markdown("""
<style>
[data-testid="stSidebarNav"] {display: none;}

.topnav {
    background: linear-gradient(90deg, #0f2b46, #123e63);
    padding: 12px 30px;
    border-radius: 0 0 12px 12px;
    margin-bottom: 10px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
.topnav a {
    color: white;
    margin-right: 40px;
    font-size: 18px;
    font-weight: 600;
    text-decoration: none;
}
.topnav a:hover {
    color: #ffd166;
}
</style>

<div class="topnav">
    <a href="/">Dashboard</a>
    <a href="/maps">Maps</a>
    <a href="/planning">Planning</a>
</div>
""", unsafe_allow_html=True)

st.title("🗺️ RLV Resource Mapping")

uploaded_file = st.file_uploader(
    "Upload a KML or GeoJSON file",
    type=["geojson", "json", "kml"]
)

if uploaded_file:

    # ---------- READ FILE ----------
    if uploaded_file.name.endswith(".kml"):
        gdf = gpd.read_file(uploaded_file, driver="KML")
    else:
        gdf = gpd.read_file(uploaded_file)

    # Ensure WGS84 CRS
    gdf = gdf.to_crs(epsg=4326)

    # Remove problematic columns (timestamps, objects etc.)
    for col in gdf.columns:
        if gdf[col].dtype not in ["int64", "float64", "object"]:
            gdf[col] = gdf[col].astype(str)

    # Convert to GeoJSON safely
    # ---------- FIX GEOMETRY ISSUES ----------
gdf = gdf[gdf.geometry.notnull()]          # Remove empty geometries
gdf = gdf[gdf.is_valid]                   # Remove invalid shapes
gdf["geometry"] = gdf["geometry"].buffer(0)  # Fix minor geometry errors

# Convert all non-geometry columns to safe types
for col in gdf.columns:
    if col != "geometry":
        gdf[col] = gdf[col].astype(str)

# Convert to GeoJSON safely
geojson_data = json.loads(gdf.to_json())

    st.success(f"Loaded {len(gdf)} map features")

    # ---------- CREATE MAP ----------
    m = folium.Map(location=[17.5, 82.6], zoom_start=9)

    folium.GeoJson(
        geojson_data,
        name="Resource Map",
        style_function=lambda x: {
            "color": "green",
            "weight": 2,
            "fillOpacity": 0.3
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[col for col in gdf.columns if col != "geometry"]
        )
    ).add_to(m)

    folium.LayerControl().add_to(m)

    st_folium(m, width=1200, height=600)

else:
    st.info("Upload a GeoJSON or KML file to view the map.")


