import json

# Load the JSON data from the file
file_path = "bus_routes.json"
with open(file_path, "r") as file:
    data = json.load(file)

# Prepare the GeoJSON structure
geojson = {"type": "FeatureCollection", "features": []}

# Convert each bus route to a GeoJSON LineString feature
for route_id, coordinates in data.items():
    feature = {
        "type": "Feature",
        "properties": {"route_id": route_id},
        "geometry": {"type": "LineString", "coordinates": coordinates},
    }
    geojson["features"].append(feature)

# Save the GeoJSON to a new file
output_file_path = "bus_routes_geojson.json"
with open(output_file_path, "w") as file:
    json.dump(geojson, file, indent=4)

print(f"GeoJSON saved to {output_file_path}")
