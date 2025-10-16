#!/usr/bin/env python3
"""Standalone test script for Sense API - Can be run from terminal."""
import asyncio
import sys
import aiohttp

API_URL = "https://api.sense.com/apiservice/api/v1"


async def test_sense_connection(email: str, password: str):
    """Test Sense API connection and data retrieval."""
    print("\n" + "=" * 70)
    print("SENSE API CONNECTION TEST")
    print("=" * 70 + "\n")

    async with aiohttp.ClientSession() as session:
        # Step 1: Authentication
        print("Step 1: Testing Authentication...")
        print("-" * 70)
        
        auth_data = {
            "email": email,
            "password": password,
        }
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Home-Assistant-Sense/1.0.0",
        }
        
        try:
            async with session.post(
                f"{API_URL}/authenticate",
                data=auth_data,
                headers=headers,
            ) as response:
                if response.status != 200:
                    print(f"❌ Authentication failed with status: {response.status}")
                    print(f"   Response: {await response.text()}")
                    return False
                
                auth_result = await response.json()
                
                access_token = auth_result.get("access_token")
                user_id = auth_result.get("user_id")
                monitors = auth_result.get("monitors", [])
                
                if not access_token:
                    print("❌ No access token in response")
                    return False
                
                if not monitors:
                    print("❌ No monitors found in account")
                    return False
                
                monitor_id = monitors[0]["id"]
                
                print("✅ Authentication successful!")
                print(f"   User ID: {user_id}")
                print(f"   Monitor ID: {monitor_id}")
                print(f"   Access Token: {access_token[:20]}...")
                print(f"   Number of monitors: {len(monitors)}")
                
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 2: Get Realtime Status
        print("\nStep 2: Testing Realtime Data Endpoint...")
        print("-" * 70)
        
        headers["Authorization"] = f"Bearer {access_token}"
        
        try:
            async with session.get(
                f"{API_URL}/app/monitors/{monitor_id}/status",
                headers=headers,
            ) as response:
                if response.status != 200:
                    print(f"❌ Status endpoint failed with status: {response.status}")
                    print(f"   Response: {await response.text()}")
                    return False
                
                status_data = await response.json()
                
                print("✅ Realtime data retrieved!")
                
                # Check for new API format (nested under 'signals')
                if "signals" in status_data:
                    print("   [Using NEW API format with 'signals' key]")
                    signals = status_data["signals"]
                    
                    # DEBUG: Show what's in signals
                    print(f"\n   DEBUG - Signals structure:")
                    if isinstance(signals, dict):
                        print(f"   Signals keys: {list(signals.keys())}")
                        print(f"   Signals type: dict")
                        # Try to find the actual data
                        for key in ['channels', 'progress', 'c', '0', '1']:
                            if key in signals:
                                print(f"   Found key '{key}': {signals[key]}")
                    elif isinstance(signals, list):
                        print(f"   Signals type: list with {len(signals)} items")
                        if signals:
                            print(f"   First item: {signals[0]}")
                    else:
                        print(f"   Signals type: {type(signals)}")
                        print(f"   Signals value: {signals}")
                    
                    print(f"\n   Attempting to extract values:")
                    print(f"   Active Power: {signals.get('w', 'N/A')} W")
                    print(f"   Solar Power: {signals.get('solar_w', 'N/A')} W")
                    print(f"   Voltage: {signals.get('voltage', 'N/A')} V")
                    print(f"   Frequency: {signals.get('hz', 'N/A')} Hz")
                    
                    # Get devices from device_detection
                    device_detection = status_data.get("device_detection", {})
                    detected = device_detection.get("in_progress", [])
                    print(f"   Active Devices: {len(detected)}")
                    if detected:
                        print("   Active device names:")
                        for device in detected[:5]:
                            print(f"      - {device.get('name', 'Unknown')}")
                else:
                    print("   [Using OLD API format]")
                    print(f"   Active Power: {status_data.get('w', 'N/A')} W")
                    print(f"   Solar Power: {status_data.get('solar_w', 'N/A')} W")
                    print(f"   Voltage: {status_data.get('voltage', 'N/A')} V")
                    print(f"   Frequency: {status_data.get('hz', 'N/A')} Hz")
                    
                    devices = status_data.get("devices", [])
                    active_devices = [d for d in devices if d.get("state") == "on"]
                    print(f"   Active Devices: {len(active_devices)}")
                    
                    if active_devices:
                        print("   Active device names:")
                        for device in active_devices[:5]:
                            print(f"      - {device.get('name', 'Unknown')}")
                
                # Show raw response for debugging
                print(f"\n   Raw response keys: {list(status_data.keys())}")
                
        except Exception as e:
            print(f"❌ Status endpoint error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Step 3: Get Devices
        print("\nStep 3: Testing Devices Endpoint...")
        print("-" * 70)
        
        try:
            async with session.get(
                f"{API_URL}/app/monitors/{monitor_id}/devices",
                headers=headers,
            ) as response:
                if response.status != 200:
                    print(f"⚠️  Devices endpoint returned status: {response.status}")
                    print(f"   (This is optional, may not work for all accounts)")
                else:
                    devices_data = await response.json()
                    
                    if isinstance(devices_data, list):
                        print(f"✅ Devices retrieved: {len(devices_data)} total")
                        if devices_data:
                            print("   First 5 devices:")
                            for device in devices_data[:5]:
                                name = device.get("name", "Unknown")
                                dev_id = device.get("id", "N/A")
                                print(f"      - {name} (ID: {dev_id})")
                    else:
                        print(f"   Response: {devices_data}")
                
        except Exception as e:
            print(f"⚠️  Devices endpoint error (non-critical): {e}")
        
        # Step 4: Test Trend Data
        print("\nStep 4: Testing Trend Data Endpoint...")
        print("-" * 70)
        
        try:
            async with session.get(
                f"{API_URL}/app/history/trends?monitor_id={monitor_id}&scale=DAY",
                headers=headers,
            ) as response:
                if response.status != 200:
                    print(f"⚠️  Trend data returned status: {response.status}")
                    print(f"   (This is optional, may not work)")
                else:
                    trend_data = await response.json()
                    
                    if "consumption" in trend_data:
                        consumption = trend_data["consumption"].get("total", 0)
                        production = trend_data.get("production", {}).get("total", 0)
                        print(f"✅ Trend data retrieved:")
                        print(f"   Daily consumption: {consumption} kWh")
                        print(f"   Daily production: {production} kWh")
                    else:
                        print(f"   Response keys: {list(trend_data.keys())}")
                
        except Exception as e:
            print(f"⚠️  Trend data endpoint error (non-critical): {e}")
        
        print("\n" + "=" * 70)
        print("✅ TEST COMPLETE - API Connection Working!")
        print("=" * 70 + "\n")
        
        return True


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("\n❌ Usage: python3 test_api.py <email> <password>\n")
        print("Example:")
        print("  python3 test_api.py user@example.com mypassword\n")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    try:
        success = asyncio.run(test_sense_connection(email, password))
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

