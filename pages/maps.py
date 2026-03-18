import folium
from streamlit_folium import st_folium
import json
import streamlit as st

st.subheader("Nereduvalasa Village GIS Map")

# Base map
m = folium.Map(location=[18.15, 82.70], zoom_start=14)

# --- Village Boundary ---
with open("maps/Nereduvalasa.geojson") as f:
    village = json.load(f)

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
with open("maps/Nereduvalasa_epra.geojson") as f:
    epra = json.load(f)

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
with open("maps/Nereduvalasa_proposed_irrigation_area.geojson") as f:
    irrigation = json.load(f)

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
