#!/usr/bin/env bash
# exit on error
set -o errexit

# Install system dependencies for GeoDjango (required for PostGIS support)
apt-get update -qq
apt-get install -y --no-install-recommends \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libspatialindex-dev \
    gettext

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files (optional, can be done in start command)
python manage.py collectstatic --no-input

