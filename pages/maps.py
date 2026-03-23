import folium
from streamlit_folium import st_folium
import json
import streamlit as st
import os
import math

st.subheader("Nereduvalasa Village GIS Map")

# -------- BASE PATH --------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# -------- CLEAN GEOJSON FUNCTION --------
def load_clean_geojson(path):
    with open(path) as f:
        data = json.load(f)

    for feature in data.get("features", []):
        props = feature.get("properties", {})

        clean_props = {}
        for k, v in props.items():
            if v is None:
                clean_props[k] = ""
            elif isinstance(v, float) and math.isnan(v):
                clean_props[k] = ""
            else:
                clean_props[k] = str(v)

        feature["properties"] = clean_props

        # fix empty geometry
        if feature.get("geometry") is None:
            feature["geometry"] = {
                "type": "Point",
                "coordinates": [0, 0]
            }

    return data

# -------- LOAD FILES --------
village = load_clean_geojson(
    os.path.join(BASE_DIR, "maps", "nereduvalasa.geojson")
)

epra = load_clean_geojson(
    os.path.join(BASE_DIR, "maps", "Nereduvalasa_epra.geojson")
)

# ⚠️ make sure filename matches EXACTLY in GitHub
irrigation = load_clean_geojson(
    os.path.join(BASE_DIR, "maps", "Nereduvalasa_proposed_irrigation_area.geojson")
)

# -------- CREATE MAP --------
m = folium.Map(location=[18.15, 82.70], zoom_start=14)

# -------- VILLAGE BOUNDARY --------
folium.GeoJson(
    village,
    name="Village Boundary",
    style_function=lambda x: {
        "color": "green",
        "weight": 2,
        "fillOpacity": 0.05
    }
).add_to(m)

# -------- EPRA (POINTS) --------
folium.GeoJson(
    epra,
    name="EPRA Resources",
    marker=folium.CircleMarker(
        radius=5,
        color="blue",
        fill=True
    )
).add_to(m)

# -------- IRRIGATION --------
folium.GeoJson(
    irrigation,
    name="Proposed Irrigation",
    style_function=lambda x: {
        "color": "red",
        "weight": 2
    }
).add_to(m)

# -------- LAYER CONTROL --------
folium.LayerControl().add_to(m)

# -------- DISPLAY --------
st_folium(m, width=900)
