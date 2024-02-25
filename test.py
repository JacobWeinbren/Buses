import aiohttp
import asyncio
import numpy as np
import polyline
import time
from aiohttp import TCPConnector
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import requests
import os
import zipfile

# Base URL for OSRM routing service
osrm_url = "http://127.0.0.1:5001/route/v1/driving/"


# Async request to OSRM for routing
async def make_request(session, start, end):
    # Format coordinates for URL
    coordinates = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    request_url = f"{osrm_url}{coordinates}?steps=true"
    try:
        # Perform async GET request
        async with session.get(request_url) as response:
            # Return JSON if successful
            return await response.json() if response.status == 200 else None
    except aiohttp.ClientError as e:
        # Handle client errors
        print(f"Request failed: {e}")
        return None


# Reduce points for simplified path
def interpolate_points(points, num_points=10):
    # Select points at intervals
    return points[:: max(1, len(points) // num_points)] + [points[-1]]


# Perform batch requests to OSRM
async def batch_request(locations, batch_size=100):
    start_time = time.time()
    results = []
    # Setup async session with connection limit
    async with aiohttp.ClientSession(connector=TCPConnector(limit=500)) as session:
        # Process locations in batches
        for i in range(0, len(locations), batch_size):
            # Create tasks for batch
            tasks = [
                make_request(session, *pair) for pair in locations[i : i + batch_size]
            ]
            # Await all tasks in the batch
            batch_results = await asyncio.gather(*tasks)
            # Process and store results
            results.extend(
                interpolate_points(polyline.decode(result["routes"][0]["geometry"]), 10)
                for result in batch_results
                if result
            )
    # Print total processing time
    print(
        f"Total time for {len(locations)} requests: {time.time() - start_time} seconds"
    )
    return results


# Download and extract coordinates from XML
def download_and_extract_coordinates(url):
    zip_file_path = "data.zip"
    siri_xml_path = "siri.xml"
    ns = {"ns": "http://www.siri.org.uk/siri"}

    # Stream download to avoid memory overload
    with requests.get(url, stream=True) as r, open(zip_file_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract XML from zip
    with zipfile.ZipFile(zip_file_path) as zip_ref:
        zip_ref.extract(siri_xml_path)

    # Parse XML for coordinates
    tree = ET.parse(siri_xml_path)
    root = tree.getroot()
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    coordinates = []

    # Extract coordinates for yesterday's data
    for vehicle_activity in root.findall(".//ns:VehicleActivity", ns):
        data_frame_ref = vehicle_activity.find(".//ns:DataFrameRef", ns)
        if data_frame_ref is not None and data_frame_ref.text == yesterday_date:
            location = vehicle_activity.find(".//ns:VehicleLocation", ns)
            if location is not None:
                latitude = location.find(".//ns:Latitude", ns)
                longitude = location.find(".//ns:Longitude", ns)
                if latitude is not None and longitude is not None:
                    coordinates.append(
                        (
                            float(latitude.text),
                            float(longitude.text),
                        )
                    )

    # Cleanup downloaded files
    os.remove(zip_file_path)
    os.remove(siri_xml_path)

    return coordinates


# Main async entry point
async def main():
    url = "https://data.bus-data.dft.gov.uk/avl/download/bulk_archive"
    # Extract coordinates from downloaded data
    locations = download_and_extract_coordinates(url)
    # Duplicate locations for routing
    locations = [(loc, loc) for loc in locations]
    # Perform batch routing requests
    await batch_request(locations)


# Entry point guard for script execution
if __name__ == "__main__":
    asyncio.run(main())
