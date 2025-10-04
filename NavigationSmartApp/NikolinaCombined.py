import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree
import folium
import json
import re
from datetime import datetime
from dateutil import parser as dateparser
import requests


google_api="AIzaSyBzqk782N2-IoGWiK7ZdIt_umTpUlYctRc"
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

driving_plan= pd.read_csv("tagtyp.csv", sep=";", encoding="utf-8")

#OSM walk and drive routes
M_walk = ox.graph_from_place("Zürich, Switzerland", network_type="walk")
M_drive = ox.graph_from_place("Zürich, Switzerland", network_type="drive")

M_walk = ox.add_edge_speeds(M_walk)
M_drive = ox.add_edge_speeds(M_drive)

for u, v, key, data in M_drive.edges(keys=True, data=True):
    if "length" in data and "speed_kph" in data:
        try:
            data["travel_time"] = data["length"] / (data["speed_kph"] * 1000 / 3600)
        except ZeroDivisionError:
            data["travel_time"] = float("inf")  # Avoid issues with zero speed
    else:
        data["travel_time"] = float("inf")  # Set to an arbitrarily high value to indicate unusable edge

for u, v, key, data in M_walk.edges(keys=True, data=True):
    # Check if 'speed_kph' exists and is valid
    if not isinstance(data.get("speed_kph"), (int, float)) or data["speed_kph"] < 1:
        # Assign default walking speed (5 km/h)
        data["speed_kph"] = 5

M_walk = ox.add_edge_travel_times(M_walk)
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
            if "travel_time" in M_drive[u][v][key]:
                M_drive[u][v][key]["travel_time"] += 1800

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
def get_fastest_route_google(origin, destination):
    endpoint = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": origin,
        "destination": destination,
        "mode": "transit",
        "departure_time": "now",
        "key": google_api
    }

    try:
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            route = data["routes"][0]
            legs = route["legs"][0]

            print("Public Transport Schedule (Google):")
            print(f"Departure: {legs['departure_time']['text']}")
            print(f"Arrival: {legs['arrival_time']['text']}")
            print(f"Duration: {legs['duration']['text']}")

            print("\nRoute Details:")
            for step in legs["steps"]:
                if step["travel_mode"] == "TRANSIT":
                    line = step["transit_details"]["line"]
                    vehicle = line["vehicle"]["type"]
                    name = line.get("short_name") or line.get("name")
                    departure_stop = step["transit_details"]["departure_stop"]["name"]
                    arrival_stop = step["transit_details"]["arrival_stop"]["name"]
                    print(f"Take {vehicle} {name} from {departure_stop} to {arrival_stop}")

            # Return duration in seconds for comparison
            return {
                "route": route,
                "duration_sec": legs["duration"]["value"],
                "duration_text": legs["duration"]["text"]
            }

        else:
            print(f"Google API Error: {data['status']}")
            return None

    except Exception as e:
        print(f"Error using Google Directions API: {e}")
        return None
#Time
WALK_SPEED = 1.4      # m/s
DRIVE_SPEED_KMPH = 50
DRIVE_SPEED = (DRIVE_SPEED_KMPH * 1000) / 60

for u, v, data in M_walk.edges(data=True):
    if "length" in data:
        data["travel_time"] = data["length"] / WALK_SPEED

for u, v, data in M_drive.edges(data=True):
    if "length" in data:
        data["travel_time"] = data["length"] / DRIVE_SPEED
# Compute routes for each mode
origin_point = input("Please enter your starting point( latitude,longitude):").strip()
dest_point = input("Please enter your starting point( latitude,longitude):").strip()
origin_point=tuple(map(float,origin_point.split(",")))
dest_point=tuple(map(float,dest_point.split(",")))

orig_walk = ox.distance.nearest_nodes(M_walk, origin_point[1], origin_point[0])
dest_walk = ox.distance.nearest_nodes(M_walk, dest_point[1], dest_point[0])

orig_drive = ox.distance.nearest_nodes(M_drive, origin_point[1], origin_point[0])
dest_drive = ox.distance.nearest_nodes(M_drive, dest_point[1], dest_point[0])
# Get shortest paths
route_walk = nx.shortest_path(M_walk, orig_walk, dest_walk, weight="travel_time")
route_drive = nx.shortest_path(M_drive, orig_drive, dest_drive, weight="travel_time")

# Get travel times in minutes
time_walk = nx.shortest_path_length(M_walk, orig_walk, dest_walk, weight="travel_time") / 60
time_drive = nx.shortest_path_length(M_drive, orig_drive, dest_drive, weight="travel_time") / 60

# Get public transport route
route_pt_result = get_fastest_route_google(
    f"{origin_point[0]},{origin_point[1]}",
    f"{dest_point[0]},{dest_point[1]}"
)

# Convert public transport time to minutes (if available)
pt_time_min = route_pt_result["duration_sec"] / 60 if route_pt_result else None

# Store all modes
modes = {
    "walking": (route_walk, time_walk),
    "driving": (route_drive, time_drive),
    "public_transport": (route_pt_result, pt_time_min)
}

print(f"Route (Public Transport): {route_pt_result}")
print(f"Modes and times (in minutes): {modes}")

# Determine best mode by minimum time
best_mode = min(modes, key=lambda k: modes[k][1] if modes[k][1] is not None else float("inf"))
print(f"Best mode: {best_mode}, Time: {modes[best_mode][1]:.2f} minutes")


# Visualization with Folium
#m = folium.Map(location=[origin_point[0], origin_point[1]], zoom_start=14)




def plot_mode_route(route, graph):
    if not route:
        return []
    return [
        (node["y"], node["x"])
        for n in route
        if (node := graph.nodes.get(n)) and "x" in node and "y" in node
    ]


def add_route_to_map(route, graph, map_object, color, label):
    coords = plot_mode_route(route, graph)
    if coords:
        #transformed_coords = transform_coordinates(coords)
        folium.PolyLine(
            coords, color=color, weight=5, opacity=0.8, tooltip=label
        ).add_to(map_object)


import polyline  # Make sure you have 'polyline' installed: pip install polyline


def add_google_transit_route_to_map(route_result, map_object, color="red"):
    if not route_result or "route" not in route_result:
        print("No public transport route to add.")
        return

    # Access the actual route object directly
    route = route_result["route"]

    try:
        steps = route["legs"][0]["steps"]
        coords = []
        for step in steps:
            if "polyline" in step:
                encoded = step["polyline"]["points"]
                decoded_points = polyline.decode(encoded)  # [(lat, lon), ...]
                coords.extend(decoded_points)

        if coords:
            folium.PolyLine(
                coords,
                color=color,
                weight=5,
                opacity=0.8,
                tooltip="Public Transport"
            ).add_to(map_object)
        else:
            print("No polyline data found in Google transit route.")
    except Exception as e:
        print(f"Error plotting Google transit route: {e}")


map_object = folium.Map(location=[origin_point[0], origin_point[1]], zoom_start=14)
# Add Google public transport route
add_google_transit_route_to_map(route_pt_result, map_object, color="red")


def add_construction_markers(map_object, construction_data):
    for _, row in construction_data.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"<b>Baustelle:</b> {row['name']}<br>{row['bemerkung']}",
            icon=folium.Icon(color="orange", icon="road"),
        ).add_to(map_object)


# Add walking and driving routes
add_route_to_map(route_walk, M_walk, map_object, color="green", label="Walking")
add_route_to_map(route_drive, M_drive, map_object, color="blue", label="Driving")

# Mark active construction sites
add_construction_markers(map_object, active_construction)

# Export the map to an HTML file
map_object.save("all_modes_route.html")
