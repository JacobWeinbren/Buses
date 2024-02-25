# OSRM Routing Engine with Docker Compose Setup Guide

This guide outlines the steps to set up your own routing engine using the Open Source Routing Machine (OSRM) with Docker Compose, focusing on routing in England. OSRM is a high-performance routing engine designed for shortest paths in road networks.

## Prerequisites

-   Docker and Docker Compose installed on your system. Docker Compose is included with Docker Desktop for Windows and Mac. For Linux, Docker Compose might need to be installed separately.

## Setup Instructions

### 1. Prepare the Data Directory

Ensure you have a `data` directory in the same location as your `docker-compose.yml` file. This directory should contain the OpenStreetMap (OSM) data file for England.

If you haven't downloaded the data file yet, you can do so with the following command:

```bash
curl -O https://repo1.maven.org/maven2/com/graphhopper/graphhopper-web/8.0/graphhopper-web-8.0.jar -O https://raw.githubusercontent.com/graphhopper/graphhopper/8.x/config-example.yml -O http://download.geofabrik.de/europe/great-britain/england-latest.osm.pbf
java -D"dw.graphhopper.datareader.file=england-latest.osm.pbf" -jar graphhopper*.jar server config-example.yml
```

```bash
python server.py
```
