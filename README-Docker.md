# Website Monitor - Docker Deployment

This application monitors websites and publishes status updates to MQTT.

## Quick Start with Docker Compose

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Portainer Deployment

### Option 1: Using Docker Compose in Portainer

1. In Portainer, go to "Stacks"
2. Create new stack
3. Copy the contents of `docker-compose.yml`
4. Modify environment variables as needed
5. Deploy

### Option 2: Using Container in Portainer

1. Go to "Containers" → "Add Container"
2. Use image name (after building): `website-monitor:latest`
3. Set environment variables:
   - `MQTT_BROKER=your-broker-hostname`
   - `MQTT_PORT=1883`
   - `MQTT_USERNAME=your-username` (optional)
   - `MQTT_PASSWORD=your-password` (optional)
   - `CHECK_INTERVAL_MS=60000`
4. Set restart policy to "Unless stopped"
5. Deploy

## Environment Variables

| Variable            | Default   | Description                    |
| ------------------- | --------- | ------------------------------ |
| `MQTT_BROKER`       | `vultr2`  | MQTT broker hostname           |
| `MQTT_PORT`         | `1883`    | MQTT broker port               |
| `MQTT_USERNAME`     | _(empty)_ | MQTT username (optional)       |
| `MQTT_PASSWORD`     | _(empty)_ | MQTT password (optional)       |
| `CHECK_INTERVAL_MS` | `60000`   | Check interval in milliseconds |

## Building the Image

```bash
# Build locally
docker build -t website-monitor .

# Or with specific tag
docker build -t website-monitor:v1.0 .
```

## MQTT Topics

The application publishes to these topics:

- `KTBMES/Twix/websites/{site_name}/{protocol}/result` - `"true"` or `"false"`
- `KTBMES/Twix/websites/{site_name}/{protocol}/last_published` - Timestamp

Example:

- `KTBMES/Twix/websites/ktbcs/https/result`
- `KTBMES/Twix/websites/ktbcs/https/last_published`

## Monitored Sites

Currently monitors:

- ktbcs.xyz (HTTP + HTTPS)
- skinnereditorial.com (HTTP + HTTPS)  
- NAS system (HTTP only)

To modify monitored sites, edit the `targets` list in `CheckWebsites.py` and rebuild the image.

## Logs

The container logs all check results and MQTT publications. Use:

```bash
docker logs -f website-monitor
```

## Troubleshooting

### Container won't start

- Check environment variables
- Verify MQTT broker is accessible
- Check container logs

### No MQTT messages

- Verify MQTT broker settings
- Check network connectivity
- Ensure MQTT broker allows connections from container

### High resource usage

- Increase `CHECK_INTERVAL_MS` for less frequent checks
- Monitor container resources in Portainer