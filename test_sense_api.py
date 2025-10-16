#!/usr/bin/env python3
"""Test script for Sense API connectivity and data retrieval."""
import asyncio
import sys
import logging
from custom_components.sense.sense_api import SenseableAsync

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_sense_api(email: str, password: str):
    """Test the Sense API connection and data retrieval."""
    print(f"\n{'='*60}")
    print("Sense API Connection Test")
    print(f"{'='*60}\n")
    
    gateway = SenseableAsync(email, password, timeout=30)
    
    try:
        # Test 1: Authentication
        print("Test 1: Authentication...")
        await gateway.authenticate()
        print(f"✓ Authentication successful")
        print(f"  - Monitor ID: {gateway.sense_monitor_id}")
        print(f"  - User ID: {gateway.sense_user_id}")
        print(f"  - Access Token: {gateway.sense_access_token[:20]}..." if gateway.sense_access_token else "None")
        
        # Test 2: Real-time data
        print("\nTest 2: Fetching real-time data...")
        await gateway.update_realtime()
        print(f"✓ Real-time data retrieved")
        print(f"  - Active Power: {gateway.active_power}W")
        print(f"  - Solar Power: {gateway.active_solar_power}W")
        print(f"  - Voltage: {gateway.voltage}V")
        print(f"  - Frequency: {gateway.hz}Hz")
        print(f"  - Active Devices: {len(gateway.active_devices)}")
        if gateway.active_devices:
            for device in gateway.active_devices[:5]:
                print(f"    - {device}")
        
        # Test 3: Get all data
        print("\nTest 3: Getting all data...")
        all_data = gateway.get_all_data()
        print(f"✓ All data retrieved")
        print(f"  - Keys in data: {list(all_data.keys())}")
        print(f"  - Active power: {all_data.get('active_power')}")
        print(f"  - Daily usage: {all_data.get('daily_usage')}")
        
        # Test 4: Get devices
        print("\nTest 4: Getting discovered devices...")
        try:
            devices = await gateway.get_discovered_device_data()
            print(f"✓ Discovered devices retrieved")
            print(f"  - Total devices: {len(devices)}")
            if devices:
                for i, device in enumerate(devices[:5], 1):
                    print(f"    {i}. {device.get('name', 'Unknown')} (ID: {device.get('id', 'Unknown')})")
        except Exception as e:
            print(f"✗ Failed to get devices: {e}")
        
        # Test 5: Trend data
        print("\nTest 5: Fetching trend data...")
        try:
            await gateway.update_trend_data()
            print(f"✓ Trend data retrieved (may have warnings)")
            print(f"  - Daily usage: {gateway.daily_usage}kWh")
            print(f"  - Daily production: {gateway.daily_production}kWh")
            print(f"  - Weekly usage: {gateway.weekly_usage}kWh")
            print(f"  - Monthly usage: {gateway.monthly_usage}kWh")
        except Exception as e:
            print(f"⚠ Trend data failed (non-critical): {e}")
        
        print(f"\n{'='*60}")
        print("✓ All tests completed!")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await gateway.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 test_sense_api.py <email> <password>")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    success = asyncio.run(test_sense_api(email, password))
    sys.exit(0 if success else 1)

