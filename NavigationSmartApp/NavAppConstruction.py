import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import folium
import json
import re
import ast
from shapely.geometry import LineString
from datetime import datetime
from dateutil import parser as dateparser
import API_ZVVZurich

#Loading the data
with open("stzh.poi_vbz_baustelle_view.json", encoding="utf-8") as file:
    data = json.load(file)

records = []
for feature in data["features"]:
    properties = feature["properties"]
    lon, lat = feature["geometry"]["coordinates"]
    # parse start date
    start_date = None
    if properties.get("datum"):
        try:
            start_date = datetime.strptime(properties["datum"], "%Y%m%d%H%M")
        except Exception:
            pass
    # parse end date from bemerkung if present
    end_date = None
    remark = properties.get("bemerkung", "")
    m = re.search(r"(\d{1,2}\.\s*\w+\s*\d{4})", remark)
    if m:
        try:
            end_date = dateparser.parse(m.group(1), dayfirst=True, fuzzy=True)
        except Exception:
            pass
    records.append({
        "id": properties.get("objectid"),
        "name": properties.get("name"),
        "lon": lon,
        "lat": lat,
        "start": start_date,
        "end": end_date,
        "bemerkung": remark
    })

construction_fields = pd.DataFrame(records)
#public_stops = pd.read_csv("ZVV_HALTESTELLEN_P_wgs84.csv")
driving_plan= pd.read_csv("tagtyp.csv", sep=";", encoding="utf-8")
#lon,lat=public_stops[["lon", "lat"]]

#OSM walk and drive routes
M_walk = ox.graph_from_place("Zürich, Switzerland", network_type="walk")
M_drive = ox.graph_from_place("Zürich, Switzerland", network_type="drive")

M_walk = ox.add_edge_speeds(M_walk)
M_walk = ox.add_edge_travel_times(M_walk)
M_drive = ox.add_edge_speeds(M_drive)
M_drive = ox.add_edge_travel_times(M_drive)

#Filter active construction fields (today)
today = pd.Timestamp.today().normalize()
construction_fields["start"] = pd.to_datetime(construction_fields["start"], errors="coerce")
construction_fields["end"] = pd.to_datetime(construction_fields["end"], errors="coerce")
active_construction = construction_fields[
    ((construction_fields["start"].isna()) | (construction_fields["start"] <= today)) &
    ((construction_fields["end"].isna()) | (construction_fields["end"] >= today))
]
print("Active Construction fields count:", len(active_construction))

#Apply a delay due to construction fields for the driving mode
edge_centroids = []
edge_keys = []

for u, v, key, data in M_drive.edges(keys=True, data=True):
    try:
        x1, y1 = M_drive.nodes[u]["x"], M_drive.nodes[u]["y"]
        x2, y2 = M_drive.nodes[v]["x"], M_drive.nodes[v]["y"]
        xm, ym = (x1 + x2) / 2, (y1 + y2) / 2  # midpoint
        edge_centroids.append((ym, xm))  # lat, lon
        edge_keys.append((u, v, key))
    except:
        continue

edge_tree = cKDTree(np.radians(edge_centroids))
# Delay edges within 50m of any active Construction Field
radius_m = 50
earth_radius_m = 6371000  # meters
radius_rad = radius_m / earth_radius_m

affected_edges = set()

for index, construction in active_construction.iterrows():
    try:
        construction_lat = construction["lat"]
        construction_lon = construction["lon"]

        # Convert construction point to radians
        point_rad = np.radians([construction_lat, construction_lon])

        # Find all edges within the radius
        nearby_edge_indices = edge_tree.query_ball_point(point_rad, r=radius_rad)

        for edge_idx in nearby_edge_indices:
            u, v, key = edge_keys[edge_idx]
            if M_drive.has_edge(u, v, key):
                M_drive[u][v][key]["travel_time"] += 3600  # Delay of 1 hour
                affected_edges.add((u, v, key))

    except Exception as error:
        print(f"Failed to apply delay near Construction field at index {index}: {error}")

#KDTree for walk graph nodes
nodes_gdf = ox.graph_to_gdfs(M_walk, edges=False)
node_coords = np.array(list(zip(nodes_gdf["y"], nodes_gdf["x"])))
node_ids = nodes_gdf.index.to_numpy()
kdtree = cKDTree(node_coords)

def nearest_walk_node(lat, lon):
    dist, idx = kdtree.query([lat, lon])
    return node_ids[idx], dist
#Public Transport

# #Public transport graph M_pt
# M_pt = nx.DiGraph()
# M_pt.graph["crs"] = "EPSG:4326"
#
# # Map stop ID to lat-lon
# stop_coords = {}
# for idx, row in public_stops.iterrows():
#     sid = row["NHSTID"]
#     lat = row.get("lat")
#     lon = row.get("lon")
#     stop_coords[sid] = (lat, lon)
#     # Add node to M_pt
#     M_pt.add_node(sid, x=lon, y=lat)
#
#
# # Use column "LINIEN" for line info
# if "LINIEN" in public_stops.columns:
#     unique_lines = public_stops["LINIEN"].unique()
# else:
#     unique_lines = []
#
# # Connect consecutive stops on same line
# for line in unique_lines:
#     sub = public_stops[public_stops["LINIEN"] == line]
#     # Filter those with valid coordinates and create a list of these
#     sub = sub.dropna(subset=["lat", "lon", "NHSTID"])
#     sub = sub.sort_values("NHSTID")
#     stop_ids = sub["NHSTID"].tolist()
#     for i in range(len(stop_ids) - 1):
#         u = stop_ids[i]
#         v = stop_ids[i+1]
#         lat1, lon1 = stop_coords.get(u, (None, None))
#         lat2, lon2 = stop_coords.get(v, (None, None))
#         if lat1 is None or lat2 is None:
#             continue
#         dist = ox.distance.great_circle(lat1, lon1, lat2, lon2)
#         # Choose a reasonable default PT speed (m/s)
#         pt_speed = 4.33  # 25 km/h
#         travel_time = dist / pt_speed
#         M_pt.add_edge(u, v, travel_time=travel_time, line=str(line))

# # Connect PT stops to walking graph nodes
# for sid, (lat, lon) in stop_coords.items():
#     try:
#         nearest_node, dist = nearest_walk_node(lat, lon)
#         walk_time = max(dist / 1.5, 10) #5km/h average walking speed
#
#         # Add PT stop to G_pt
#         if not M_pt.has_node(sid):
#             M_pt.add_node(sid, x=lon, y=lat)
#
#         # Add the nearest walk node to G_pt with coordinates from G_walk
#         if not M_pt.has_node(nearest_node):
#             node_data = M_walk.nodes[nearest_node]
#             M_pt.add_node(nearest_node, x=node_data["x"], y=node_data["y"])
#
#         # Add edges
#         M_pt.add_edge(sid, nearest_node, travel_time=walk_time)
#         M_pt.add_edge(nearest_node, sid, travel_time=walk_time)
#
#     except Exception as e:
#         print(f"Error linking stop {sid} to walk node: {e}")
#
# # Delay public transport edges affected by "Baustellen on Gleise"
# def extract_linien_from_string(s):
#     return re.findall(r"\b\d+\b", s)
#
# affected_pt_lines = set()
# for idx, row in active_construction.iterrows():
#     bm = str(row.get("bemerkung", "")).lower()
#     if "gleis" in bm or "tram" in bm:
#         lines_found = extract_linien_from_string(row.get("bemerkung", ""))
#         for l in lines_found:
#             affected_pt_lines.add(l)
#
# print("Affected PT lines:", affected_pt_lines)
#
# for u, v, data in M_pt.edges(data=True):
#     line = data.get("line")
#     if line is not None and str(line) in affected_pt_lines:
#         data["travel_time"] += 3600  # add 1 hour

# Ensure every edge has travel_time ---
for M in [M_walk, M_drive, M_pt]:
    for u, v, data in M.edges(data=True):
        if "travel_time" not in data:
            length = data.get("length", 1)
            data["travel_time"] = length / 1.5

# Choose origin & destination, find nearest nodes ---
origin_point = (47.3782, 8.5402)
dest_point = (47.38294310727824, 8.53531911167331)

orig_walk = ox.distance.nearest_nodes(M_walk, origin_point[1], origin_point[0])
dest_walk = ox.distance.nearest_nodes(M_walk, dest_point[1], dest_point[0])

orig_drive = ox.distance.nearest_nodes(M_drive, origin_point[1], origin_point[0])
dest_drive = ox.distance.nearest_nodes(M_drive, dest_point[1], dest_point[0])

# orig_pt = ox.distance.nearest_nodes(M_pt, origin_point[1], origin_point[0])
# dest_pt = ox.distance.nearest_nodes(M_pt, dest_point[1], dest_point[0])

#Compute shortest paths
def compute_route(G, orig, dest):
    try:
        route = nx.shortest_path(G, orig, dest, weight="travel_time")
        time = nx.shortest_path_length(G, orig, dest, weight="travel_time")
        return route, time
    except Exception as e:
        return None, float("inf")
route_walk, time_walk = compute_route(M_walk, orig_walk, dest_walk)
route_drive, time_drive = compute_route(M_drive, orig_drive, dest_drive)
route_pt, time_pt = compute_route(M_pt, orig_pt, dest_pt)

print("Walk time (min):", time_walk / 60)
print("Drive time (min):", time_drive / 60)
print("Public transport time (min):", time_pt / 60)

modes = {
    "walking": (route_walk, time_walk),
    "driving": (route_drive, time_drive),
    "public_transport": (route_pt, time_pt)
}
best = min(modes, key=lambda k: modes[k][1])
print("Best mode:", best, "time min:", modes[best][1] / 60)

# Visualization in Folium
m = folium.Map(location=[origin_point[0], origin_point[1]], zoom_start=14)

def plot_mode_route(route, M, color, label):
    if route is None:
        return
    coords = []
    for n in route:
        node = M.nodes[n]
        if "x" in node and "y" in node:
            coords.append((node["y"], node["x"]))
    if coords:
        folium.PolyLine(coords, color=color, weight=5, opacity=0.8, tooltip=label).add_to(m)

plot_mode_route(route_walk, M_walk, "green", "Walking")
plot_mode_route(route_drive, M_drive, "blue", "Driving")
#plot_mode_route(route_pt, M_pt, "red", "Public Transport")

# Mark Baustellen
for idx, row in active_construction.iterrows():
    folium.Marker([row["lat"], row["lon"]],
                  popup=f"Baustelle: {row['name']} — {row['bemerkung']}",
                  icon=folium.Icon(color="orange", icon="road")).add_to(m)

m.save("all_modes_route.html")
print("Saved map to all_modes_route.html")

#Results object for frontend or further logic
results = {
    "walking": {"time_min": time_walk / 60, "route": route_walk},
    "driving": {"time_min": time_drive / 60, "route": route_drive},
    "public_transport": {"time_min": time_pt / 60, "route": route_pt},
    "best_mode": best
}