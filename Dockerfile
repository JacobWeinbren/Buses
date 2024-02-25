# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install system dependencies for GDAL and set environment variables to help Python packages find GDAL
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    build-essential \ 
    && rm -rf /var/lib/apt/lists/* \
    && echo "GDAL_VERSION=$(gdal-config --version)" >> /etc/environment \
    && echo "GDAL_CONFIG=/usr/bin/gdal-config" >> /etc/environment \
    && echo "CPLUS_INCLUDE_PATH=/usr/include/gdal" >> /etc/environment \
    && echo "C_INCLUDE_PATH=/usr/include/gdal" >> /etc/environment

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5002 available to the world outside this container
EXPOSE 5002

# Run app.py when the container launches
CMD ["python", "./server.py"]