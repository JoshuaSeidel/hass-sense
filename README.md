# Sense Energy Monitor Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/JoshuaSeidel/hass-sense.svg)](https://github.com/JoshuaSeidel/hass-sense/releases)
[![License](https://img.shields.io/github/license/JoshuaSeidel/hass-sense.svg)](LICENSE)

A fully-featured Home Assistant custom integration for the Sense Energy Monitor, providing comprehensive real-time and historical energy monitoring capabilities.

## Features

### 🔋 Comprehensive Energy Monitoring
- **Real-time Power Sensors**
  - Active power consumption (W)
  - Solar power production (W)
  - Line voltage monitoring (L1 & L2)
  - Grid frequency monitoring (Hz)

### 📊 Historical Energy Data
- **Daily, Weekly, Monthly, and Yearly Statistics**
  - Energy consumption (kWh)
  - Solar production (kWh)
  - All sensors support long-term statistics

### 🏠 Device Detection
- **Binary Sensors** for each detected device showing on/off state
- Automatic discovery of all devices learned by your Sense monitor
- Device attributes including:
  - Location
  - Tags
  - Manufacturer and model info

### 🔌 Smart Plug Control
- **Switch entities** for controllable devices
- Integration with TP-Link Kasa and Wemo smart plugs
- Direct device control from Home Assistant

### 🛠️ Advanced Services
- `sense.get_device_info` - Retrieve detailed device information
- `sense.reset_device` - Remove a device from learned devices
- `sense.rename_device` - Rename detected devices

### ⚡ Performance & Real-time Updates
- **Configurable update intervals** from 5 seconds to 5 minutes
- **Separate coordinators** for realtime (power, voltage) vs trends (usage history)
- Default 60-second intervals for realtime, 5-minute intervals for trends
- **Near real-time monitoring** available (5-10s updates) for power tracking
- Efficient API calls to minimize rate limiting
- Automatic reconnection on connection failures
- **Options flow** to change update rate after setup

## Installation

### Method 1: HACS (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations
   - Click the three dots in the top right
   - Select "Custom repositories"
   - Add `https://github.com/JoshuaSeidel/hass-sense` as an Integration
3. Click "Install" on the Sense Energy Monitor integration
4. Restart Home Assistant

### Method 2: Manual Installation

1. Download the latest release from the [releases page](https://github.com/JoshuaSeidel/hass-sense/releases)
2. Extract the files to your Home Assistant config directory:
   ```
   /config/custom_components/sense/
   ```
3. Restart Home Assistant

## Configuration

### UI Configuration (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Sense Energy Monitor**
4. Enter your Sense account credentials:
   - Email address
   - Password
   - Timeout (optional, default: 30 seconds)
5. Click **Submit**

### Configuration.yaml (Legacy)

```yaml
# Not recommended - use UI configuration instead
sense:
  email: your_email@example.com
  password: your_password
  timeout: 30
```

## Sensors

The integration creates the following sensors:

### Real-time Sensors
| Sensor | Unit | Description |
|--------|------|-------------|
| `sensor.sense_active_power` | W | Current power consumption |
| `sensor.sense_solar_power` | W | Current solar production |
| `sensor.sense_voltage_l1` | V | Voltage on line 1 |
| `sensor.sense_voltage_l2` | V | Voltage on line 2 |
| `sensor.sense_frequency` | Hz | Grid frequency |

### Energy Sensors
| Sensor | Unit | Description |
|--------|------|-------------|
| `sensor.sense_daily_usage` | kWh | Energy used today |
| `sensor.sense_daily_production` | kWh | Solar produced today |
| `sensor.sense_weekly_usage` | kWh | Energy used this week |
| `sensor.sense_weekly_production` | kWh | Solar produced this week |
| `sensor.sense_monthly_usage` | kWh | Energy used this month |
| `sensor.sense_monthly_production` | kWh | Solar produced this month |
| `sensor.sense_yearly_usage` | kWh | Energy used this year |
| `sensor.sense_yearly_production` | kWh | Solar produced this year |

### Device Sensors
- Binary sensors for each detected device showing on/off state
- Switches for controllable devices (smart plugs)

## Services

### Get Device Info
```yaml
service: sense.get_device_info
data:
  device_id: "abc123def456"
```

### Reset Device
```yaml
service: sense.reset_device
data:
  device_id: "abc123def456"
```

### Rename Device
```yaml
service: sense.rename_device
data:
  device_id: "abc123def456"
  name: "Living Room Lamp"
```

## Automation Examples

### Alert When High Power Usage Detected
```yaml
automation:
  - alias: "High Power Usage Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sense_active_power
        above: 5000
    action:
      - service: notify.mobile_app
        data:
          message: "High power usage detected: {{ states('sensor.sense_active_power') }}W"
```

### Track Daily Solar Production
```yaml
automation:
  - alias: "Daily Solar Report"
    trigger:
      - platform: time
        at: "21:00:00"
    action:
      - service: notify.mobile_app
        data:
          message: "Today's solar production: {{ states('sensor.sense_daily_production') }} kWh"
```

### Monitor Specific Device
```yaml
automation:
  - alias: "Notify When Dryer Finishes"
    trigger:
      - platform: state
        entity_id: binary_sensor.sense_dryer
        from: "on"
        to: "off"
        for: "00:05:00"
    action:
      - service: notify.mobile_app
        data:
          message: "The dryer has finished!"
```

## Energy Dashboard Integration

This integration fully supports Home Assistant's Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Consumption**
3. Select `sensor.sense_daily_usage`
4. If you have solar, click **Add Solar Production**
5. Select `sensor.sense_daily_production`

## Troubleshooting

### Authentication Errors
- Verify your Sense account credentials
- Check if you can log in to the Sense mobile app
- Ensure your account doesn't have 2FA enabled (not currently supported)

### Sensors Not Updating
- Check the Home Assistant logs for errors
- Verify your internet connection
- Try reloading the integration from Settings → Devices & Services

### Missing Devices
- Wait for Sense to detect and learn devices (can take several days)
- Check the Sense mobile app to see if devices are detected there first
- Some devices may not be detectable due to their power signature

### Enable Debug Logging
```yaml
logger:
  default: info
  logs:
    custom_components.sense: debug
```

## API Information

This integration uses the unofficial Sense API based on:
- [sense_energy](https://github.com/scottbonline/sense) Python library (v0.13.8+)
- Sense cloud API endpoints

**Note:** This is an unofficial integration and is not affiliated with or endorsed by Sense. Use at your own risk.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions:
- [Open an issue](https://github.com/JoshuaSeidel/hass-sense/issues)
- Check existing issues for solutions
- Review the [Home Assistant Community](https://community.home-assistant.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [scottbonline/sense](https://github.com/scottbonline/sense) - Sense API Python library
- [Home Assistant](https://www.home-assistant.io/) - Open source home automation platform
- Sense community contributors

## Changelog

See [RELEASES](https://github.com/JoshuaSeidel/hass-sense/releases) for version history and changes.

---

**Disclaimer:** This integration is not affiliated with, endorsed by, or connected to Sense. All product names, logos, and brands are property of their respective owners.

