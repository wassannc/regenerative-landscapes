import folium
from streamlit_folium import st_folium
import json
import streamlit as st

st.subheader("Nereduvalasa Village GIS Map")

# Base map
m = folium.Map(location=[18.15, 82.70], zoom_start=14)

# --- Village Boundary ---
import json

def load_clean_geojson(path):
    with open(path) as f:
        data = json.load(f)

    for feature in data.get("features", []):
        props = feature.get("properties", {})

        # convert all values to safe string
        clean_props = {}
        for k, v in props.items():
            if v is None:
                clean_props[k] = ""
            else:
                clean_props[k] = str(v)

        feature["properties"] = clean_props

    return data

folium.GeoJson(
    village,
    name="Village Boundary",
    style_function=lambda x: {
        "color": "green",
        "weight": 2,
        "fillOpacity": 0.05
    }
).add_to(m)

# --- EPRA Resources ---
epra = load_clean_geojson("maps/Nereduvalasa_epra.geojson")

folium.GeoJson(
    epra,
    name="EPRA Resources",
    point_to_layer=lambda feature, latlng: folium.CircleMarker(
        location=latlng,
        radius=5,
        color="blue",
        fill=True
    )
).add_to(m)

# --- Proposed Irrigation ---
irrigation = load_clean_geojson("maps/Nereduvalasa_proposed_irrigation_area.geojson")

folium.GeoJson(
    irrigation,
    name="Proposed Irrigation",
    style_function=lambda x: {
        "color": "red",
        "weight": 2
    }
).add_to(m)

# Layer control
folium.LayerControl().add_to(m)

# Show map
st_folium(m, width=900)
