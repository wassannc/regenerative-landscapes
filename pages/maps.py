import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os

st.subheader("🌍 Village GIS Map")

# -------- BASE PATH --------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# -------- ULTRA SAFE GEOJSON FIX --------
def load_geojson_safe(path):
    with open(path) as f:
        data = json.load(f)

    safe_features = []

    for f in data.get("features", []):
        try:
            geom = f.get("geometry", {})
            props = f.get("properties", {})

            # ✅ Skip invalid geometry
            if not geom:
                continue

            if geom.get("type") not in ["Point", "Polygon", "MultiPolygon"]:
                continue

            coords = geom.get("coordinates")

            # ✅ Skip bad coordinates
            if coords is None:
                continue

            # ✅ Clean properties (force string)
            clean_props = {}
            for k, v in props.items():
                try:
                    clean_props[k] = "" if v is None else str(v)
                except:
                    clean_props[k] = ""

            # ✅ Rebuild feature safely
            safe_features.append({
                "type": "Feature",
                "geometry": {
                    "type": geom["type"],
                    "coordinates": coords
                },
                "properties": clean_props
            })

        except:
            continue

    return {
        "type": "FeatureCollection",
        "features": safe_features
    }

# -------- LOAD FILES --------
polygons = load_geojson_safe(
    os.path.join(BASE_DIR, "maps", "landuse_polygons.geojson")
)

points = load_geojson_safe(
    os.path.join(BASE_DIR, "maps", "resources_points.geojson")
)

# -------- MAP --------
m = folium.Map(location=[18.15, 82.70], zoom_start=14)

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

# -------- ADD POLYGONS --------
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

# -------- ADD POINTS (SAFE WAY) --------
for feature in points["features"]:
    try:
        coords = feature["geometry"]["coordinates"]

        folium.CircleMarker(
            location=[coords[1], coords[0]],  # lat, lon
            radius=5,
            color="black",
            fill=True,
            fill_color="red",
            fill_opacity=0.9
        ).add_to(m)

    except:
        continue
        
# -------- DISPLAY --------
st_folium(m, width=900)
