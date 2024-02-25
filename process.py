import xml.etree.ElementTree as ET
import json

# Load and parse the XML file
tree = ET.parse("siri.xml")
root = tree.getroot()

# Prepare a GeoJSON structure
geojson = {"type": "FeatureCollection", "features": []}

# Namespace may be required to access elements, depending on your XML structure
ns = {"": "http://www.siri.org.uk/siri"}

# Iterate through each VehicleActivity in the XML
for va in root.findall(".//VehicleActivity", ns):
    lon = va.find(".//Longitude", ns).text
    lat = va.find(".//Latitude", ns).text
    item_id = va.find(".//ItemIdentifier", ns).text
    # Create a GeoJSON feature for each vehicle
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(lon), float(lat)]},
        "properties": {
            "ItemIdentifier": item_id
            # Add more properties as needed
        },
    }
    geojson["features"].append(feature)

# Save the GeoJSON to a file
with open("vehicles.geojson", "w") as f:
    json.dump(geojson, f)

print("GeoJSON file created.")
