# OSRM Routing Engine with Docker Compose Setup Guide

This guide outlines the steps to set up your own routing engine using the Open Source Routing Machine (OSRM) with Docker Compose, focusing on routing in England. OSRM is a high-performance routing engine designed for shortest paths in road networks.

## Prerequisites

-   Docker and Docker Compose installed on your system. Docker Compose is included with Docker Desktop for Windows and Mac. For Linux, Docker Compose might need to be installed separately.

## Setup Instructions

### 1. Prepare the Data Directory

Ensure you have a `data` directory in the same location as your `docker-compose.yml` file. This directory should contain the OpenStreetMap (OSM) data file for England.

If you haven't downloaded the data file yet, you can do so with the following command:

```bash
curl http://download.geofabrik.de/europe/great-britain/england-latest.osm.pbf -o ./data/england-latest.osm.pbf
```

### 2. Building the Map with OSRM

Before using the OSRM routing engine, you need to process the raw OSM data. This involves extracting, partitioning, and customizing the data to be used by OSRM. A bash script named `build-map.sh` is provided for this purpose.

To build the map, run the following commands:

```bash
chmod +x build-map.sh
./build-map.sh
```

### 3. Running Docker Compose

Navigate to your project directory where the `docker-compose.yml` file is located and run the following command to start all services:

```bash
docker-compose up
```

To run the services in the background, add the `-d` flag:

```bash
docker-compose up -d
```

### 4. Shutting Down

To stop and remove all the services started by Docker Compose, use:

```bash
docker-compose down
```

To also remove the volumes and networks created by Docker Compose, add the `-v` flag:

```bash
docker-compose down -v
```
