import folium
from streamlit_folium import st_folium
import json
import streamlit as st
import os
import math

st.subheader("🌍 Village GIS Map")

# -------- BASE PATH --------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# -------- CLEAN FUNCTION --------
def load_clean_geojson(path):
    import json
    import math

    with open(path) as f:
        data = json.load(f)

    for feature in data.get("features", []):
        props = feature.get("properties", {})

        clean_props = {}
        for k, v in props.items():
            try:
                if v is None:
                    clean_props[k] = ""
                elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                    clean_props[k] = ""
                else:
                    clean_props[k] = str(v)
            except:
                clean_props[k] = ""

        feature["properties"] = clean_props

    return data

import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

polygons = load_clean_geojson(
    os.path.join(BASE_DIR, "maps", "landuse_polygons.geojson")
)

points = load_clean_geojson(
    os.path.join(BASE_DIR, "maps", "resources_points.geojson")
)

# -------- MAP BASE --------
m = folium.Map(location=[18.15, 82.70], zoom_start=14, tiles="CartoDB positron")

# -------- COLOR FUNCTION --------
def get_color(land_type):
    land_type = land_type.lower()

    if "agriculture" in land_type:
        return "#7CB342"   # light green
    elif "irrigation" in land_type:
        return "#1E88E5"   # strong blue
    elif "water" in land_type:
        return "#00ACC1"   # cyan
    elif "orchard" in land_type:
        return "#2E7D32"   # dark green
    elif "pond" in land_type:
        return "#00897B"
    else:
        return "#BDBDBD"   # grey

# -------- ADD POLYGONS --------
folium.GeoJson(
    polygons,
    name="Land_Use",
    style_function=lambda feature: {
        "color": "black",
        "weight": 1,
        "fillColor": get_color(feature["properties"].get("Land_Use", "")),
        "fillOpacity": 0.6,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["Land_Use"],
        aliases=["Type:"]
    )
).add_to(m)

# -------- ADD POINTS --------
folium.GeoJson(
    points,
    name="Resources",
    point_to_layer=lambda feature, latlng: folium.CircleMarker(
        location=latlng,
        radius=6,
        color="black",
        weight=1,
        fill=True,
        fill_color="red",
        fill_opacity=0.9
    ),
    tooltip=folium.GeoJsonTooltip(
        fields=["Name"],
        aliases=["Type:"]
    )
).add_to(m)

folium.GeoJson(
    polygons,
    name="Boundary",
    style_function=lambda feature: {
        "color": "black",
        "weight": 2,
        "fillOpacity": 0
    }
).add_to(m)

tooltip=folium.GeoJsonTooltip(
    fields=["Land_Use"],
    aliases=["Land Type:"],
    sticky=True
)

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
folium.LayerControl().add_to(m)

# -------- DISPLAY --------
st_folium(m, width=900)
