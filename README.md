# OSRM Routing Engine Setup Guide

This guide provides instructions on how to set up your own routing engine using OSRM (Open Source Routing Machine) with Docker for routing in England. OSRM is a C++ implementation of a high-performance routing engine for shortest paths in road networks. Leveraging Docker simplifies the setup process across different environments.

## Prerequisites

-   Docker installed on your system.

## Step 1: Download OpenStreetMap Data for England

First, you need to download the OpenStreetMap (OSM) data for England. This data is used by OSRM to compute routes.

```bash
wget http://download.geofabrik.de/europe/great-britain/england-latest.osm.pbf
```

## Step 2: Pre-process the Data with Docker

OSRM requires the raw OSM data to be pre-processed into a routing graph. This is done in three stages: extraction, partitioning, and customization.

1. **Extract** the OSM data using the car profile:

```bash
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-extract -p /opt/car.lua /data/england-latest.osm.pb
```

2. **Partition** the extracted data:

```bash
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-partition /data/england-latest.osrm
```

3. **Customize** the partitioned data:

```bash
docker run -t -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-customize /data/england-latest.osrm
```

## Step 3: Start the Routing Engine HTTP Server

With the data processed, you can now start the OSRM backend server. This server will listen for routing requests on port 5000.

```bash
docker run -t -i -p 5000:5000 -v "${PWD}:/data" ghcr.io/project-osrm/osrm-backend osrm-routed --algorithm mld /data/england-latest.osrm
```

## Step 4: Make Routing Requests

With the server running, you can make HTTP requests to get routes. For example, to get a route in London:

```bash
curl "http://127.0.0.1:5000/route/v1/driving/-0.127647,51.507321;-0.142555,51.507948?steps=true"
```
