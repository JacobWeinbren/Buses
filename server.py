import aiohttp
import asyncio
import numpy as np
import polyline
import time
from aiohttp import TCPConnector
from datetime import datetime
import xml.etree.ElementTree as ET
from io import BytesIO
from zipfile import ZipFile
import ujson
from flask import Flask, send_file
from flask_cors import CORS
import os

# Base URL for GraphHopper routing service
graphhopper_url = os.getenv("GRAPHHOPPER_URL", "http://localhost:8989") + "/route"


# Async request to GraphHopper for routing
async def make_request(session, start, end):
    coordinates = f"point={start[0]},{start[1]}&point={end[0]},{end[1]}"
    request_url = (
        f"{graphhopper_url}?{coordinates}&locale=en&points_encoded=false&profile=car"
    )
    try:
        async with session.get(request_url) as response:
            if response.status == 200:
                data = await response.json()
                # Assuming you want to extract the polyline from the first route
                if data["paths"] and "points" in data["paths"][0]:
                    points = data["paths"][0]["points"]["coordinates"]
                    return points  # Directly return the decoded polyline points
            return None
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
        return None


# Perform batch requests to OSRM
async def batch_request(locations, previous_locations, batch_size=100):
    results = {}
    async with aiohttp.ClientSession(connector=TCPConnector(limit=500)) as session:
        tasks = [
            (bus_id, make_request(session, previous_locations[bus_id], end))
            for bus_id, end in locations.items()
            if bus_id in previous_locations
        ]
        for i in range(0, len(tasks), batch_size):
            batch = asyncio.gather(*(task[1] for task in tasks[i : i + batch_size]))
            batch_results = await batch
            for j, result in enumerate(batch_results):
                if result:
                    bus_id = tasks[i + j][0]
                    # Since make_request now returns the points directly, no need to decode
                    rounded_points = [
                        (round(lat, 5), round(lon, 5)) for lat, lon in result
                    ]
                    results[bus_id] = rounded_points
    return results


# Download and extract coordinates from XML asynchronously
async def download_and_extract_coordinates(url):
    ns = {"ns": "http://www.siri.org.uk/siri"}
    coordinates = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.read()
                with ZipFile(BytesIO(data)) as zip_ref:
                    with zip_ref.open("siri.xml") as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                        for vehicle_activity in root.findall(
                            ".//ns:VehicleActivity", ns
                        ):
                            origin_ref = vehicle_activity.find(".//ns:OriginRef", ns)
                            destination_ref = vehicle_activity.find(
                                ".//ns:DestinationRef", ns
                            )
                            vehicle_ref = vehicle_activity.find(".//ns:VehicleRef", ns)
                            location = vehicle_activity.find(
                                ".//ns:VehicleLocation", ns
                            )
                            if (
                                origin_ref is not None
                                and destination_ref is not None
                                and vehicle_ref is not None
                                and location is not None
                            ):
                                latitude = location.find(".//ns:Latitude", ns)
                                longitude = location.find(".//ns:Longitude", ns)
                                if latitude is not None and longitude is not None:
                                    # Combine OriginRef, DestinationRef, and VehicleRef to form a unique ID
                                    unique_id = f"{origin_ref.text}_{destination_ref.text}_{vehicle_ref.text}"
                                    coordinates[unique_id] = (
                                        float(latitude.text),
                                        float(longitude.text),
                                    )
    return coordinates


# Main async entry point
async def main():
    url = "https://data.bus-data.dft.gov.uk/avl/download/bulk_archive"
    previous_locations = {}
    while True:
        start_time = time.time()
        locations = await download_and_extract_coordinates(url)
        results = await batch_request(locations, previous_locations)
        with open("bus_routes.json", "w") as f:
            ujson.dump(results, f)
        print(
            f"Total time for {len(locations)} requests: {time.time() - start_time} seconds"
        )
        previous_locations = locations
        print("Waiting for next update...")
        await asyncio.sleep(60)


app = Flask(__name__)
CORS(app)


@app.route("/download")
def download_file():
    return send_file("bus_routes.json", as_attachment=True)


if __name__ == "__main__":
    from threading import Thread

    server_thread = Thread(
        target=lambda: app.run(host="0.0.0.0", port=5002, use_reloader=False)
    )
    server_thread.start()
    asyncio.run(main())
