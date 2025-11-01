# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (if needed for paho-mqtt or requests)
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY CheckServiceStatus.py .
COPY CheckWebsites.py .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Set environment variables with defaults
ENV MQTT_BROKER=vultr2
ENV MQTT_PORT=1883
ENV MQTT_USERNAME=""
ENV MQTT_PASSWORD=""
ENV CHECK_INTERVAL_MS=60000

# Run the application
CMD ["python", "CheckWebsites.py"]