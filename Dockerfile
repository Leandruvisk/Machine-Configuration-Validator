# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY app/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app/ .

# Create directories for configs and reports
RUN mkdir -p /app/configs /app/reports

# Copy configs
COPY configs/ /app/configs/

# Expose any ports if needed (none for now)
# EXPOSE 8000

# Run the application
CMD ["python", "main.py"]