#!/bin/bash
set -e

# Initialize Aerich migration directory if missing
if [ ! -f aerich.ini ]; then
  echo "aerich.ini not found. Create it in the project root."
  exit 1
fi

if [ ! -d migrations ] || [ -z "$(ls -A migrations)" ]; then
  echo "Initializing Aerich metadata..."
  poetry run aerich init
  poetry run aerich init-db
fi

poetry run aerich migrate
poetry run aerich upgrade
