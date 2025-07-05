#!/usr/bin/env python3
"""
Simple test script for the Computer Use Agent API
"""

import requests
import json
import time
import base64
from PIL import Image
import io

API_BASE_URL = "http://localhost:8000"


def test_api():
    """Test the API endpoints"""

    print("Testing Computer Use Agent API...")
    print("=" * 50)

    # Test 1: Check status
    print("\n1. Testing /status endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✓ Status: {status}")
        else:
            print(f"✗ Status check failed: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API server. Make sure it's running on port 8000")
        print("  Run: poetry run api")
        return

    # Test 2: Get screenshot
    print("\n2. Testing /screenshot endpoint...")
    try:
        response = requests.get(f"{API_BASE_URL}/screenshot")
        if response.status_code == 200:
            screenshot_data = response.json()
            print(f"✓ Screenshot captured at: {screenshot_data['timestamp']}")

            # Optionally save screenshot to file
            screenshot_bytes = base64.b64decode(screenshot_data["screenshot"])
            with open("test_screenshot.png", "wb") as f:
                f.write(screenshot_bytes)
            print("✓ Screenshot saved as test_screenshot.png")
        else:
            print(f"✗ Screenshot failed: {response.status_code}")
    except Exception as e:
        print(f"✗ Screenshot error: {e}")

    # Test 3: Execute simple action
    print("\n3. Testing /act endpoint (single step)...")
    try:
        action_request = {
            "instruction": "Take a screenshot and describe what you see",
            "single_step": True,
        }
        response = requests.post(f"{API_BASE_URL}/act", json=action_request)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Action executed: {result['success']}")
            print(f"  Message: {result['message']}")
            if result["actions"]:
                print(f"  Actions taken: {len(result['actions'])}")
                for action in result["actions"]:
                    print(f"    - {action['action']}: {action.get('result', 'N/A')}")
        else:
            print(f"✗ Action failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Action error: {e}")

    # Test 4: Test click endpoint
    print("\n4. Testing /click endpoint...")
    try:
        form_data = {"query": "desktop"}
        response = requests.post(f"{API_BASE_URL}/click", data=form_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Click executed: {result['success']}")
            print(f"  Message: {result['message']}")
        else:
            print(f"✗ Click failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Click error: {e}")

    # Test 5: Test command endpoint
    print("\n5. Testing /command endpoint...")
    try:
        form_data = {"command": "echo 'Hello from API'"}
        response = requests.post(f"{API_BASE_URL}/command", data=form_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Command executed: {result['success']}")
            print(f"  Result: {result['message']}")
        else:
            print(f"✗ Command failed: {response.status_code}")
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"✗ Command error: {e}")

    print("\n" + "=" * 50)
    print("API testing completed!")


if __name__ == "__main__":
    test_api()
