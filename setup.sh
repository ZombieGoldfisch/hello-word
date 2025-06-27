#!/usr/bin/env bash
# Setup script for the project. Installs required dependencies.
set -e

# Determine python interpreter
PYTHON=${PYTHON:-python3}

if ! command -v "$PYTHON" >/dev/null 2>&1; then
    echo "Python interpreter '$PYTHON' not found. Please install Python 3." >&2
    exit 1
fi

# Upgrade pip and install mandatory requirements
$PYTHON -m pip install --upgrade pip
$PYTHON -m pip install -r requirements.txt

if [ "$1" = "--with-optional" ]; then
    # Install optional packages used for visualization and geocoding
    $PYTHON -m pip install osmnx folium geopy
fi

echo "Setup complete"
