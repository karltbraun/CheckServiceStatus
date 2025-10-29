import json
import time

import paho.mqtt.client as mqtt

from CheckServiceStatus import check_service_status


def publish_to_mqtt(
    client,
    website_name,
    method,
    result_value,
    broker_host,
    broker_port=1883,
):
    """
    Publish the check result to MQTT broker.

    Args:
        client: MQTT client instance
        website_name: Name/tag for the website
        method: HTTP or HTTPS method
        result_value: Boolean result from check_service_status
        broker_host: MQTT broker hostname
        broker_port: MQTT broker port (default: 1883)
    """
    topic = f"KTBMES/Twix/websites/{website_name}/{method.lower()}/result"
    payload = str(
        result_value
    ).lower()  # Convert boolean to lowercase string

    try:
        client.publish(topic, payload, qos=1, retain=True)
        print(f"Published to MQTT - Topic: {topic}, Payload: {payload}")
    except Exception as e:
        print(f"Failed to publish to MQTT: {e}")


def main():
    # MQTT broker configuration
    MQTT_BROKER = "vultr2"  # Change to your MQTT broker address
    MQTT_PORT = 1883
    MQTT_USERNAME = None  # Set if authentication is required
    MQTT_PASSWORD = None  # Set if authentication is required

    expect_string_ktbcs: str = (
        "<title>KTBCS - Professional Technology Consulting</title>"
    )
    expect_string_skinner: str = (
        "<title>Skinner Editorial Portfolio</title>"
    )

    # Modified check_targets to include website names
    check_targets = [
        ["ktbcs", "http://ktbcs.xyz", expect_string_ktbcs],
        ["ktbcs", "https://ktbcs.xyz", expect_string_ktbcs],
        ["skinner", "http://skinnereditorial.com", expect_string_skinner],
        ["skinner", "https://skinnereditorial.com", expect_string_skinner],
    ]

    # Initialize MQTT client
    client = mqtt.Client()

    # Set credentials if provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        # Connect to MQTT broker
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()  # Start the loop to handle network operations
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")

        # Check each target and publish results
        for website_name, url, expected_string in check_targets:
            result = check_service_status(url, expected_string)

            # Print results (keeping existing functionality)
            print("Service Status Check Results:")
            for key, value in result.items():
                print(f"{key}: {value}")

            # Publish to MQTT
            method = result.get("method", "unknown")
            is_active = result.get("is_active", False)
            contains_expected = result.get(
                "contains_expected_string", False
            )

            # Publish the overall result (active AND contains expected string)
            overall_result = is_active and contains_expected
            publish_to_mqtt(
                client,
                website_name,
                method,
                overall_result,
                MQTT_BROKER,
                MQTT_PORT,
            )

            print()  # Add a blank line between results for readability

            # Small delay between checks to avoid overwhelming the broker
            time.sleep(0.5)

    except Exception as e:
        print(f"MQTT connection failed: {e}")
        print("Continuing with checks but without MQTT publishing...")

        # Fallback: run checks without MQTT
        for website_name, url, expected_string in check_targets:
            result = check_service_status(url, expected_string)
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


if __name__ == "__main__":
    main()
