# Installation Guide

## Quick Start for Testing

### Option 1: Manual Installation (Fastest for Testing)

1. **Download the Integration**
   ```bash
   cd /config
   mkdir -p custom_components
   cd custom_components
   git clone https://github.com/JoshuaSeidel/hass-sense.git sense
   ```

2. **Restart Home Assistant**
   - Go to Settings → System → Restart

3. **Add the Integration**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Sense Energy Monitor"
   - Enter your Sense credentials

### Option 2: HACS Installation

1. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Click on "Integrations"
   - Click the three dots (⋮) in the top right
   - Select "Custom repositories"
   - Add: `https://github.com/JoshuaSeidel/hass-sense`
   - Category: "Integration"
   - Click "Add"

2. **Install the Integration**
   - Search for "Sense Energy Monitor" in HACS
   - Click "Install"
   - Restart Home Assistant

3. **Configure**
   - Go to Settings → Devices & Services
   - Click "+ Add Integration"
   - Search for "Sense Energy Monitor"
   - Enter your credentials

## Configuration

### Required Information
- **Email**: Your Sense account email address
- **Password**: Your Sense account password
- **Timeout** (optional): API timeout in seconds (default: 30)

### What Happens After Setup

Once configured, the integration will automatically:
1. Authenticate with your Sense account
2. Discover your energy monitor
3. Create 14+ sensor entities
4. Create binary sensors for all detected devices
5. Create switches for controllable devices (if any)
6. Start updating data every 60 seconds

## Verifying Installation

### Check the Entities

After installation, you should see:

**Sensors:**
- `sensor.sense_active_power`
- `sensor.sense_solar_power`
- `sensor.sense_voltage_l1`
- `sensor.sense_voltage_l2`
- `sensor.sense_frequency`
- `sensor.sense_daily_usage`
- `sensor.sense_daily_production`
- `sensor.sense_weekly_usage`
- `sensor.sense_weekly_production`
- `sensor.sense_monthly_usage`
- `sensor.sense_monthly_production`
- `sensor.sense_yearly_usage`
- `sensor.sense_yearly_production`

**Binary Sensors:**
- One for each device detected by your Sense monitor
- Example: `binary_sensor.sense_refrigerator`

**Switches:**
- One for each controllable device (smart plugs)
- Example: `switch.sense_living_room_lamp_switch`

### Add to Energy Dashboard

1. Go to Settings → Dashboards → Energy
2. Click "Add Consumption"
3. Select `sensor.sense_daily_usage`
4. If you have solar:
   - Click "Add Solar Production"
   - Select `sensor.sense_daily_production`

## Troubleshooting

### Integration Not Found
- Make sure you've restarted Home Assistant after installation
- Check that the `custom_components/sense` directory exists
- Verify all files are present in the directory

### Authentication Errors
- Verify your Sense credentials in the mobile app
- Make sure your account doesn't have 2FA enabled (not currently supported)
- Check your internet connection

### No Devices Showing
- Wait for Sense to detect and learn devices (can take days/weeks)
- Check the Sense mobile app to verify devices are detected there
- Reload the integration from Settings → Devices & Services

### Enable Debug Logging

Add to your `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.sense: debug
```

Then restart Home Assistant and check the logs.

## Next Steps

- [Create automations](README.md#automation-examples)
- [Use the services](README.md#services)
- [Configure the Energy Dashboard](README.md#energy-dashboard-integration)

## Support

Having issues? Please [open an issue](https://github.com/JoshuaSeidel/hass-sense/issues) on GitHub.

