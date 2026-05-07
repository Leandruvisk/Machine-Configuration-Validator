@echo off
REM Run Aerich migrations for the project
IF NOT EXIST aerich.ini (
  echo aerich.ini not found. Create it in the project root.
  exit /b 1
)

IF NOT EXIST migrations\* (
  echo Initializing Aerich metadata...
  poetry run aerich init
  poetry run aerich init-db
)

poetry run aerich migrate
poetry run aerich upgrade
