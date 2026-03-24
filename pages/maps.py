import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os

st.subheader("🌍 Village GIS Map")

# -------- BASE PATH --------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# -------- SAFE GEOJSON LOADER --------
def load_geojson_safe(path):
    with open(path) as f:
        data = json.load(f)

    safe_features = []

    for f in data.get("features", []):
        try:
            geom = f.get("geometry", {})
            props = f.get("properties", {})

            # skip invalid geometry
            if not geom or "type" not in geom or "coordinates" not in geom:
                continue

            # clean properties
            clean_props = {}
            for k, v in props.items():
                clean_props[k] = "" if v is None else str(v)

            safe_features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": clean_props
            })

        except:
            continue

    return {
        "type": "FeatureCollection",
        "features": safe_features
    }

# -------- LOAD DATA --------
polygons = load_geojson_safe(
    os.path.join(BASE_DIR, "maps", "landuse_polygons.geojson")
)

points = load_geojson_safe(
    os.path.join(BASE_DIR, "maps", "resources_points.geojson")
)

# -------- CREATE MAP --------
m = folium.Map(location=[18.15, 82.70], zoom_start=14)

# -------- BASE LAYERS --------
folium.TileLayer(
    "OpenStreetMap",
    name="Street Map"
).add_to(m)

folium.TileLayer(
    tiles="https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
    attr="Google",
    name="Satellite",
    subdomains=["mt0", "mt1", "mt2", "mt3"],
    max_zoom=20
).add_to(m)

# -------- COLOR FUNCTION --------
def get_color(val):
    val = val.lower()

    if "agriculture" in val:
        return "#7CB342"
    elif "irrigation" in val:
        return "#1E88E5"
    elif "water" in val:
        return "#00ACC1"
    elif "orchard" in val:
        return "#2E7D32"
    elif "pond" in val:
        return "#00897B"
    else:
        return "#BDBDBD"

# -------- POLYGON LAYER --------
folium.GeoJson(
    polygons,
    name="Land Use",
    style_function=lambda f: {
        "color": "black",
        "weight": 1,
        "fillColor": get_color(f["properties"].get("Land_Use", "")),
        "fillOpacity": 0.6,
    }
).add_to(m)

# -------- POINTS (SAFE LOOP) --------
for feature in points["features"]:
    try:
        coords = feature["geometry"]["coordinates"]

        folium.CircleMarker(
            location=[coords[1], coords[0]],
            radius=5,
            color="black",
            fill=True,
            fill_color="red",
            fill_opacity=0.9
        ).add_to(m)

    except:
        continue

# -------- LEGEND --------
legend_html = """
<div style="
position: fixed; 
bottom: 40px; left: 40px; width: 230px;
background-color: white;
border:2px solid grey;
z-index:9999;
font-size:14px;
padding: 10px;
border-radius:8px;
">
<b>Legend</b><br><br>
<span style="color:#7CB342;">⬛</span> Agriculture<br>
<span style="color:#1E88E5;">⬛</span> Irrigation<br>
<span style="color:#00ACC1;">⬛</span> Water bodies<br>
<span style="color:#2E7D32;">⬛</span> Orchard<br>
<span style="color:#00897B;">⬛</span> Farm Pond<br>
<span style="color:red;">⬤</span> Proposed Works
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# -------- LAYER CONTROL --------
folium.LayerControl(collapsed=False).add_to(m)

# -------- DISPLAY --------
st_folium(m, width=900)
