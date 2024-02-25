#!/bin/bash

# Define the data directory and ensure it exists
DATA_DIR="./data"
mkdir -p ${DATA_DIR}

# Step 1: osrm-extract
echo "Running osrm-extract..."
docker run --rm -v ${PWD}/data:/data ghcr.io/project-osrm/osrm-backend \
    osrm-extract -p /opt/car.lua /data/england-latest.osm.pbf 

# Check if osrm-extract was successful
if [ $? -ne 0 ]; then
    echo "osrm-extract failed, exiting..."
    exit 1
fi

# Step 2: osrm-partition
echo "Running osrm-partition..."
docker run --rm -v ${PWD}/data:/data ghcr.io/project-osrm/osrm-backend \
    osrm-partition /data/england-latest.osrm 

# Check if osrm-partition was successful
if [ $? -ne 0 ]; then
    echo "osrm-partition failed, exiting..."
    exit 1
fi

# Step 3: osrm-customize
echo "Running osrm-customize..."
docker run --rm -v ${PWD}/data:/data ghcr.io/project-osrm/osrm-backend \
    osrm-customize /data/england-latest.osrm 

# Check if osrm-customize was successful
if [ $? -ne 0 ]; then
    echo "osrm-customize failed, exiting..."
    exit 1
fi

echo "All steps completed successfully."