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
# -------- VILLAGE DROPDOWN --------
village_list = list(set(
    [f["properties"].get("Village", "") for f in polygons["features"]]
))

selected_village = st.selectbox(
    "Select Village",
    sorted(village_list)
)

# -------- FILTER BY VILLAGE --------
filtered_polygons = {
    "type": "FeatureCollection",
    "features": [
        f for f in polygons["features"]
        if str(f["properties"].get("Village", "")).strip().lower()
        == selected_village.strip().lower()
    ]
}
filtered_points = [
    f for f in points["features"]
    if str(f["properties"].get("Village", "")).strip().lower()
    == selected_village.strip().lower()
]
# ===============================
# 📊 VILLAGE STATS (ADD HERE)
# ===============================

st.markdown("### 📊 Village Summary")

# Counts
# -------- AREA CALCULATION --------
total_area = 0

for f in filtered_polygons["features"]:
    try:
        area_val = float(f["properties"].get("area", 0))
        total_area += area_val
    except:
        continue
total_points = len(filtered_points)
# Display
col1, col2 = st.columns(2)
col1.metric("Total Area (Acres)", round(total_area, 2))
col2.metric("Proposed Works", total_points)

from collections import Counter

land_use_list = [
    f["properties"].get("Land_Use", "Unknown")
    for f in filtered_polygons["features"]
]

land_use_counts = Counter(land_use_list)

from collections import defaultdict

land_use_area = defaultdict(float)

for f in filtered_polygons["features"]:
    try:
        land_type = f["properties"].get("Land_Use", "Unknown")
        area_val = float(f["properties"].get("area", 0))

        land_use_area[land_type] += area_val
    except:
        continue
# Breakdown
import pandas as pd

st.markdown("### 🌱 Land Use Distribution (Acres)")

df = pd.DataFrame([
    {"Land Use": k, "Area (Acres)": round(v, 2)}
    for k, v in land_use_area.items()
])

st.dataframe(df, use_container_width=True)
    
# -------- CREATE MAP --------
m = folium.Map(location=[18.15, 82.70], zoom_start=14)

# -------- AUTO ZOOM --------
if filtered_polygons["features"]:
    coords_list = []

    for f in filtered_polygons["features"]:
        geom = f["geometry"]

        if geom["type"] == "Polygon":
            coords_list.extend(geom["coordinates"][0])

        elif geom["type"] == "MultiPolygon":
            for poly in geom["coordinates"]:
                coords_list.extend(poly[0])

    if coords_list:
        lat = sum([c[1] for c in coords_list]) / len(coords_list)
        lon = sum([c[0] for c in coords_list]) / len(coords_list)

        m.location = [lat, lon]
        m.zoom_start = 15

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
    elif "coffee" in val:
        return "#6D4C41"   # brown
    elif "grazing" in val:
        return "#C0CA33"   # yellow-green
    elif "nregs" in val:
        return "#F4511E"   # orange
    else:
        return "#BDBDBD"

for f in filtered_polygons["features"]:
    props = f.get("properties", {})
    if "Land_Use" not in props or props["Land_Use"] is None:
        props["Land_Use"] = "Unknown"

# -------- POLYGON LAYER --------
land_layer = folium.FeatureGroup(name="Land Use", show=True)

folium.GeoJson(
    filtered_polygons,
    style_function=lambda f: {
        "color": "black",
        "weight": 1,
        "fillColor": get_color(f["properties"].get("Land_Use", "")),
        "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["Land_Use"],
        aliases=["Type:"],
        sticky=True,
        labels=True
    )
).add_to(land_layer)

land_layer.add_to(m)

# -------- POINTS (SAFE LOOP) --------
points_layer = folium.FeatureGroup(name="Proposed Works", show=True)

for feature in filtered_points:
    try:
        coords = feature["geometry"]["coordinates"]
        props = feature.get("properties", {})

        # ✅ PLACE IT HERE
        label = props.get("Name", "Work")

        folium.CircleMarker(
            location=[coords[1], coords[0]],
            radius=5,
            color="black",
            fill=True,
            fill_color="red",
            fill_opacity=0.9,
            tooltip=label,
            popup=label
        ).add_to(points_layer)

    except:
        continue

points_layer.add_to(m)

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

<div><span style="background:#7CB342;width:12px;height:12px;display:inline-block;"></span> Agriculture</div>
<div><span style="background:#1E88E5;width:12px;height:12px;display:inline-block;"></span> Irrigation</div>
<div><span style="background:#00ACC1;width:12px;height:12px;display:inline-block;"></span> Water bodies</div>
<div><span style="background:#2E7D32;width:12px;height:12px;display:inline-block;"></span> Orchard</div>
<div><span style="background:#00897B;width:12px;height:12px;display:inline-block;"></span> Farm Pond</div>
<div><span style="background:red;width:12px;height:12px;display:inline-block;"></span> Proposed Works</div>
<div><span style="background:#6D4C41;width:12px;height:12px;display:inline-block;"></span> Coffee</div>
<div><span style="background:#C0CA33;width:12px;height:12px;display:inline-block;"></span> Grazing Land</div>
<div><span style="background:#F4511E;width:12px;height:12px;display:inline-block;"></span> NREGS Works</div>

</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# -------- LAYER CONTROL --------
folium.LayerControl(collapsed=False).add_to(m)

# -------- DISPLAY --------
st_folium(m, width=900)
