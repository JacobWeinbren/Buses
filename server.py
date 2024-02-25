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
import os

# Base URL for OSRM routing service
osrm_url = os.getenv("OSRM_URL", "http://127.0.0.1:5001") + "/route/v1/driving/"


# Async request to OSRM for routing
async def make_request(session, start, end):
    coordinates = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    request_url = f"{osrm_url}{coordinates}?steps=true"
    try:
        async with session.get(request_url) as response:
            return await response.json() if response.status == 200 else None
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
        return None


# Interpolate points for simplified path using numpy for efficiency
def interpolate_points(points, num_points=5):
    points_array = np.array(points)
    original_length = len(points)

    if original_length == num_points:
        return np.round(points_array, 5).tolist()
    elif original_length > num_points:
        indices = np.round(np.linspace(0, original_length - 1, num_points)).astype(int)
        return np.round(points_array[indices], 5).tolist()
    else:
        new_points = np.zeros((num_points, 2))
        for i in range(2):
            new_points[:, i] = np.interp(
                np.linspace(0, original_length - 1, num_points),
                np.arange(original_length),
                points_array[:, i],
            )
        return np.round(new_points, 5).tolist()


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
                    points = polyline.decode(result["routes"][0]["geometry"])
                    results[bus_id] = interpolate_points(points, 10)
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
                            vehicle_ref = vehicle_activity.find(".//ns:VehicleRef", ns)
                            location = vehicle_activity.find(
                                ".//ns:VehicleLocation", ns
                            )
                            if vehicle_ref is not None and location is not None:
                                latitude = location.find(".//ns:Latitude", ns)
                                longitude = location.find(".//ns:Longitude", ns)
                                if latitude is not None and longitude is not None:
                                    coordinates[vehicle_ref.text] = (
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
        await asyncio.sleep(10)


app = Flask(__name__)


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
