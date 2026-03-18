import folium
from streamlit_folium import st_folium
import json

st.subheader("Nereduvalasa Village GIS Map")

# create base map
m = folium.Map(location=[18.15, 82.70], zoom_start=14)

# --- Village Boundary ---
with open("maps/nereduvalasa.geojson") as f:
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

# --- EPRA (existing resources) ---
with open("maps/Nereduvalasa_epra.geojson") as f:
    epra = json.load(f)

folium.GeoJson(
    epra,
    name="Existing Resources (EPRA)",
    marker=folium.CircleMarker(radius=5, color="blue")
).add_to(m)

# --- Proposed Irrigation ---
with open("maps/Nereduvalasa_proposed_irrigation.geojson") as f:
    irrigation = json.load(f)

folium.GeoJson(
    irrigation,
    name="Proposed Irrigation",
    style_function=lambda x: {
        "color": "red",
        "weight": 2
    }
).add_to(m)

# layer control
folium.LayerControl().add_to(m)

# display map
st_folium(m, width=900)
