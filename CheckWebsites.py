import asyncio
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from zoneinfo import ZoneInfo

import paho.mqtt.client as mqtt

from CheckServiceStatus import check_service_status


@dataclass
class MQTTConfig:
    broker: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class WebsiteTarget:
    name: str
    url: str
    expected_string: str


def publish_to_mqtt(
    client,
    website_name,
    method,
    result_value,
    broker_host,
    broker_port=1883,
):
    """
    Publish the check result and timestamp to MQTT broker.

    Topics are constructed as: {PUB_ROOT}/{PUB_SOURCE}/{website_name}/{method}/result
    and: {PUB_ROOT}/{PUB_SOURCE}/{website_name}/{method}/last_published

    Args:
        client: MQTT client instance
        website_name: Name/tag for the website
        method: HTTP or HTTPS method
        result_value: Boolean result from check_service_status
        broker_host: MQTT broker hostname
        broker_port: MQTT broker port (default: 1883)
    """
    # Get MQTT topic configuration from environment variables
    pub_root = os.getenv("PUB_ROOT", "MISSING_ROOT")  # Default fallback
    pub_source = os.getenv(
        "PUB_SOURCE", "MISSING_SOURCE"
    )  # Default fallback

    # Define MQTT topics (consolidated for easy maintenance)
    base_topic = (
        f"{pub_root}/{pub_source}/websites/{website_name}/{method.lower()}"
    )
    result_topic = f"{base_topic}/result"
    timestamp_topic = f"{base_topic}/last_published"

    # Prepare payload
    result_payload = str(
        result_value
    ).lower()  # Convert boolean to lowercase string

    try:
        # Publish the result
        client.publish(result_topic, result_payload, qos=1, retain=True)
        print(
            f"Published to MQTT - Topic: {result_topic}, Payload: {result_payload}"
        )

        # Publish the timestamp with explicit timezone
        # Get timezone from environment or default to Pacific timezone
        timezone_name = os.getenv(
            "TZ", "America/Los_Angeles"
        )  # Pacific Time Zone default
        try:
            local_tz = ZoneInfo(timezone_name)
            current_time = datetime.now(local_tz).strftime(
                "%Y-%m-%d %H:%M"
            )
        except Exception:
            # Fallback to UTC if timezone not available
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M UTC")

        client.publish(timestamp_topic, current_time, qos=1, retain=True)
        print(
            f"Published to MQTT - Topic: {timestamp_topic}, Payload: {current_time}"
        )

    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")


def CheckWebsite(
    target: WebsiteTarget, mqtt_config: MQTTConfig, client: mqtt.Client
) -> bool:
    """
    Check a single website and publish results to MQTT.

    Args:
        target: WebsiteTarget containing name, url, and expected_string
        mqtt_config: MQTTConfig containing broker details
        client: MQTT client instance

    Returns:
        bool: True if website is active and contains expected string
    """
    result = check_service_status(target.url, target.expected_string)

    # Print results (keeping existing functionality)
    print("Service Status Check Results:")
    for key, value in result.items():
        print(f"{key}: {value}")

    # Extract results
    method = result.get("method", "unknown")
    is_active = result.get("is_active", False)
    contains_expected = result.get("contains_expected_string", False)

    # Calculate overall result (active AND contains expected string)
    overall_result = is_active and contains_expected

    # Publish to MQTT
    publish_to_mqtt(
        client,
        target.name,
        method,
        overall_result,
        mqtt_config.broker,
        mqtt_config.port,
    )

    print()  # Add a blank line between results for readability

    return overall_result


def CheckWebsites(targets: List[WebsiteTarget], mqtt_config: MQTTConfig):
    """
    Check multiple websites using the provided configuration.

    Args:
        targets: List of WebsiteTarget objects to check
        mqtt_config: MQTTConfig containing broker details
    """
    # Initialize MQTT client
    client = mqtt.Client()

    # Set credentials if provided
    if mqtt_config.username and mqtt_config.password:
        client.username_pw_set(mqtt_config.username, mqtt_config.password)

    try:
        # Connect to MQTT broker
        client.connect(mqtt_config.broker, mqtt_config.port, 60)
        client.loop_start()  # Start the loop to handle network operations
        print(
            f"Connected to MQTT broker at {mqtt_config.broker}:{mqtt_config.port}"
        )

        # Check each target
        for target in targets:
            CheckWebsite(target, mqtt_config, client)

            # Small delay between checks to avoid overwhelming the broker
            time.sleep(0.5)

    except Exception as e:
        print(f"MQTT connection failed: {e}")
        print("Continuing with checks but without MQTT publishing...")

        # Fallback: run checks without MQTT
        for target in targets:
            result = check_service_status(
                target.url, target.expected_string
            )
            print("Service Status Check Results:")
            for key, value in result.items():
                print(f"{key}: {value}")
            print()

    finally:
        # Clean up MQTT connection
        try:
            client.loop_stop()
            client.disconnect()
            print("Disconnected from MQTT broker")
        except Exception:
            pass


async def main():
    # Get configuration from environment variables with defaults
    time_between_checks_ms = int(
        os.getenv("CHECK_INTERVAL_MS", "60000")
    )  # 60 seconds default
    mqtt_broker = os.getenv("MQTT_BROKER", "vultr2")
    mqtt_port = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username = os.getenv("MQTT_USERNAME") or None
    mqtt_password = os.getenv("MQTT_PASSWORD") or None

    # Define expected strings
    expect_string_ktbcs: str = (
        "<title>KTBCS - Professional Technology Consulting</title>"
    )
    expect_string_skinner: str = (
        "<title>Skinner Editorial Portfolio</title>"
    )
    expect_string_nas: str = (
        "<title>KTBMES-NAS-01"  # Partial string match within title tag
    )

    # Create MQTT configuration
    mqtt_config = MQTTConfig(
        broker=mqtt_broker,
        port=mqtt_port,
        username=mqtt_username,
        password=mqtt_password,
    )

    # Create website targets
    targets = [
        WebsiteTarget("ktbcs", "http://ktbcs.xyz", expect_string_ktbcs),
        WebsiteTarget("ktbcs", "https://ktbcs.xyz", expect_string_ktbcs),
        WebsiteTarget(
            "skinner", "http://skinnereditorial.com", expect_string_skinner
        ),
        WebsiteTarget(
            "skinner",
            "https://skinnereditorial.com",
            expect_string_skinner,
        ),
        # HTTP-only website (no HTTPS variant)
        WebsiteTarget(
            "nas",
            "http://100.114.180.102:5000/#/sign",
            expect_string_nas,
        ),
    ]

    # Convert milliseconds to seconds for asyncio.sleep()
    time_between_checks_seconds = time_between_checks_ms / 1000.0

    print("=== Website Monitor Starting ===")
    print(f"MQTT Broker: {mqtt_broker}:{mqtt_port}")
    print(f"MQTT Auth: {'Yes' if mqtt_username else 'No'}")
    print(
        f"Check Interval: {time_between_checks_ms}ms ({time_between_checks_seconds}s)"
    )
    print(f"Monitoring {len(targets)} targets")
    print("Press Ctrl+C to stop")
    print("=" * 40)

    try:
        while True:
            print(
                f"\n*** Starting website checks at {time.strftime('%Y-%m-%d %H:%M:%S')} ***"
            )
            CheckWebsites(targets, mqtt_config)
            print(
                f"*** Completed checks, waiting {time_between_checks_seconds}s until next run ***"
            )
            await asyncio.sleep(time_between_checks_seconds)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Monitoring stopped")


if __name__ == "__main__":
    asyncio.run(main())
