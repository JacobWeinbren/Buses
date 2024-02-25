import aiohttp
import asyncio
import numpy as np
import polyline
import time
from aiohttp import TCPConnector

osrm_url = "http://127.0.0.1:5001/route/v1/driving/"


async def make_request(session, start, end):
    coordinates = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    request_url = f"{osrm_url}{coordinates}?steps=true"
    try:
        async with session.get(request_url) as response:
            return await response.json() if response.status == 200 else None
    except aiohttp.ClientError as e:
        print(f"Request failed: {e}")
        return None


def interpolate_points(points, num_points=10):
    if len(points) <= num_points:
        return points
    return points[np.linspace(0, len(points) - 1, num=num_points, dtype=int)]


async def batch_request(locations, batch_size=100):
    start_time = time.time()
    results = []
    connector = TCPConnector(limit=500)  # Limit the number of simultaneous connections
    async with aiohttp.ClientSession(connector=connector) as session:
        for i in range(0, len(locations), batch_size):
            batch = locations[i : i + batch_size]
            tasks = [make_request(session, start, end) for start, end in batch]
            batch_results = await asyncio.gather(*tasks)
            for result in batch_results:
                if result:
                    decoded_points = polyline.decode(result["routes"][0]["geometry"])
                    interpolated_points = interpolate_points(decoded_points, 10)
                    results.append(interpolated_points)
    print(
        f"Total time for {len(locations)} requests: {time.time() - start_time} seconds"
    )


def generate_random_points(base_lat, base_lon, num_points=18000, distance=500):
    deg_per_meter = 1 / 111320
    lat_offsets = np.random.uniform(-distance, distance, num_points) * deg_per_meter
    lon_offsets = (
        np.random.uniform(-distance, distance, num_points)
        * deg_per_meter
        / np.cos(np.radians(base_lat))
    )
    return np.column_stack((base_lat + lat_offsets, base_lon + lon_offsets))


base_location = (51.507321, -0.127647)
locations = [(start, start) for start in generate_random_points(*base_location)]

asyncio.run(batch_request(locations))
