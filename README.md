# CheckServiceStatus

A Python service monitoring tool that checks website availability and publishes results to MQTT.

## Features

- Check HTTP/HTTPS service availability
- Verify expected content is present on websites
- Publish monitoring results to MQTT broker
- Detailed error reporting and response time measurement
- Clean, modular code structure

## Files

- `CheckServiceStatus.py` - Core service checking functionality
- `CheckWebsites.py` - Website monitoring script with MQTT publishing

## Dependencies

- `requests` - For HTTP requests
- `paho-mqtt` - For MQTT publishing

## Installation

```bash
# Install dependencies using uv
uv pip install requests paho-mqtt

# Or using pip
pip install requests paho-mqtt
```

## Usage

### Basic Service Check
```python
from CheckServiceStatus import check_service_status

result = check_service_status("https://example.com", "Expected Title")
print(result)
```

### Website Monitoring with MQTT
```bash
# Run the website monitoring script
python CheckWebsites.py
```

## MQTT Topic Structure

Results are published to: `KTBMES/twix/websites/<website_name>/<method>/result`

Examples:
- `KTBMES/twix/websites/ktbcs/https/result`
- `KTBMES/twix/websites/skinner/http/result`

## Configuration

Edit the MQTT broker settings in `CheckWebsites.py`:

```python
MQTT_BROKER = "localhost"  # Your MQTT broker address
MQTT_PORT = 1883
MQTT_USERNAME = None  # Set if authentication required
MQTT_PASSWORD = None  # Set if authentication required
```

## License

Private repository - All rights reserved.