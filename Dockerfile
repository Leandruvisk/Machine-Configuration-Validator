# Use Python 3.11 slim image
FROM python:3.11-slim

# Install Poetry
RUN pip install poetry

# Set working directory
WORKDIR /app

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-dev

# Copy the application code
COPY app/ .
COPY run_motor_simulator.py .

# Create directories for configs and reports
RUN mkdir -p /app/configs /app/reports

# Copy configs
COPY configs/ /app/configs/

# Expose any ports if needed (none for now)
# EXPOSE 8000

# Run the application
CMD ["python", "main.py"]