import time
from datetime import datetime

import requests


def check_service_status(
    url: str, expected_string: str, timeout: int = 10
) -> dict:
    """
    Check service status with detailed information.

    Args:
        url (str): The URL to check
        expected_string (str): The string to search for in the response
        timeout (int): Timeout in seconds for the request (default: 10)

    Returns:
        dict: Detailed status information including:
            - url: The checked URL
            - is_active: Whether the URL is active
            - contains_expected_string: Whether response contains expected string
            - status_code: HTTP status code (if available)
            - response_time: Response time in seconds
            - error_message: Error message if any
            - timestamp: When the check was performed (local timezone)
    """
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = {
        "url": url,
        "method": "",
        "expected_string": expected_string,
        "is_active": False,
        "contains_expected_string": False,
        "status_code": None,
        "response_time": None,
        "error_message": None,
        "timestamp": timestamp,
    }

    if "https:" in url.lower():
        result["method"] = "HTTPS"
    elif "http:" in url.lower():
        result["method"] = "HTTP"

    try:
        response = requests.get(url, timeout=timeout)
        response_time = time.time() - start_time

        result["status_code"] = response.status_code
        result["response_time"] = round(response_time, 3)
        result["is_active"] = response.status_code == 200

        if result["is_active"]:
            response_text = response.text.lower()
            expected_string_lower = expected_string.lower()
            result["contains_expected_string"] = (
                expected_string_lower in response_text
            )

    except requests.exceptions.Timeout:
        result["response_time"] = round(time.time() - start_time, 3)
        result["error_message"] = (
            f"Request timed out after {timeout} seconds"
        )
    except requests.exceptions.ConnectionError:
        result["response_time"] = round(time.time() - start_time, 3)
        result["error_message"] = (
            "Connection error - unable to reach the URL"
        )
    except requests.exceptions.RequestException as e:
        result["response_time"] = round(time.time() - start_time, 3)
        result["error_message"] = f"Request error: {str(e)}"
    except Exception as e:
        result["response_time"] = round(time.time() - start_time, 3)
        result["error_message"] = f"Unexpected error: {str(e)}"

    return result


# Example usage
if __name__ == "__main__":
    expect_string_ktbcs: str = (
        "<title>KTBCS - Professional Technology Consulting</title>"
    )
    expect_string_skinner: str = (
        "<title>Skinner Editorial Portfolio</title>"
    )

    check_targets = [
        ["http://ktbcs.xyz", expect_string_ktbcs],
        ["https://ktbcs.xyz", expect_string_ktbcs],
        ["http://skinnereditorial.com", expect_string_skinner],
        ["https://skinnereditorial.com", expect_string_skinner],
    ]

    # Usage example
    for url, expected_string in check_targets:
        result = check_service_status(url, expected_string)
        print("Service Status Check Results:")
        for key, value in result.items():
            print(f"{key}: {value}")
        print()  # Add a blank line between results for readability
