# Sense Energy Monitor Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/JoshuaSeidel/hass-sense.svg)](https://github.com/JoshuaSeidel/hass-sense/releases)
[![License](https://img.shields.io/github/license/JoshuaSeidel/hass-sense.svg)](LICENSE)

**The Ultimate Sense Energy Monitor Integration** - Matches the official integration's capabilities while adding groundbreaking AI-powered features!

## 🌟 What Makes This Different?

This isn't just another Sense integration. We've built the **first AI-powered energy monitoring integration** for Home Assistant!

### ✅ Everything the Official Integration Has
- Real-time power monitoring
- Historical energy data
- Device detection
- Smart plug control
- Energy dashboard support

### 🚀 Plus Revolutionary Features
- **🤖 AI-Powered Insights** - Get intelligent explanations of your energy usage
- **📊 Advanced Analytics** - Peak power tracking, anomaly detection, 15-minute averages
- **💰 Bill Forecasting** - AI predicts your monthly bill with explanations
- **☀️ Solar Intelligence** - Real-time optimization advice for solar users
- **⚡ Configurable Updates** - 5 seconds to 5 minutes (official is fixed at 60s)
- **🔮 Predictive Features** - Weekly stories, optimization suggestions, comparative analysis

## Features

### 🔋 Comprehensive Energy Monitoring
- **Real-time Power Sensors**
  - Active power consumption (W)
  - Solar power production (W)
  - Line voltage monitoring (L1 & L2)
  - Grid frequency monitoring (Hz)
  - **Peak power tracking** (new!)
  - **15-minute average power** (new!)
  - **Average power consumption** (new!)

### 📊 Historical Energy Data
- **Daily, Weekly, Monthly, and Yearly Statistics**
  - Energy consumption (kWh)
  - Solar production (kWh)
  - All sensors support long-term statistics

### ☀️ Solar Analytics (New!)
- **Peak solar production tracking**
- **Self-consumption rate** - How much solar you use vs export
- **Solar optimization coaching** via AI

### 🏠 Device Detection
- **Binary Sensors** for each detected device showing on/off state
- **Anomaly Detection Sensor** - Alerts when power usage is unusual
- Automatic discovery of all devices learned by your Sense monitor
- Device attributes including location, tags, manufacturer info

### 🔌 Smart Plug Control
- **Switch entities** for controllable devices
- Integration with TP-Link Kasa and Wemo smart plugs
- Direct device control from Home Assistant

### 🤖 AI-Powered Features (v2.0+)

**7 AI Sensors:**
- `sensor.sense_ai_daily_insights` - Morning summary with recommendations
- `sensor.sense_ai_solar_coach` - Real-time solar optimization advice
- `sensor.sense_ai_bill_forecast` - Predictive monthly bill with explanation
- `sensor.sense_ai_weekly_story` - Engaging narrative about your energy week
- `sensor.sense_ai_optimization_suggestions` - AI-generated automation code
- `sensor.sense_ai_comparative_analysis` - Compare to similar homes
- `sensor.sense_ai_anomaly_explanation` - AI explains unusual power spikes

**7 AI Services:**
- `sense.ask_ai` - Ask questions about your energy in natural language
- `sense.identify_device` - AI helps identify unknown devices
- `sense.explain_anomaly` - Get AI explanation of current anomaly
- `sense.generate_insights` - Generate insights on-demand
- `sense.generate_optimization` - Get optimization suggestions
- `sense.get_privacy_info` - See what data is sent to AI
- `sense.get_cost_estimate` - Estimate AI costs

**AI Provider Options:**
- **Home Assistant Conversation** (Free) - Uses your default agent
- **OpenAI Integration** - Uses your OpenAI conversation integration
- **Anthropic Conversation** - Uses your Anthropic conversation integration

**Token Budget Control:**
- **Low** (~$1-2/month) - Essential features only
- **Medium** (~$3-5/month) - Recommended balance
- **High** (~$8-12/month) - All features, real-time

See **[AI_FEATURES.md](AI_FEATURES.md)** for complete AI documentation!

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

### 🚀 Advanced Features
Ready to take it further? Check out **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** for:
- 💰 Cost tracking & bill projection
- ⚡ Peak power detection
- 📊 Predictive analytics
- 🤖 Smart automations (load shedding, off-peak optimization)
- ☀️ Solar optimization strategies
- 💡 Energy budgets
- 📱 Dashboard examples

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

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for **Sense Energy Monitor**
4. Enter your Sense account credentials:
   - Email address
   - Password
   - Real-time Update Rate (optional, default: 60 seconds)
5. Click **Submit**

### Configure Options (After Setup)

1. Go to **Settings** → **Devices & Services** → **Sense Energy Monitor**
2. Click **Configure**
3. Adjust settings:
   - **Real-time Update Rate** - How often to fetch power data (5s to 300s)
   - **AI Provider** - Select AI provider or "Disabled"
   - **Monthly Token Budget** - Control AI costs (only shown if AI enabled)

### Enable AI Features

1. First, set up a conversation integration (optional but recommended):
   - **OpenAI**: Install "OpenAI Conversation" integration
   - **Anthropic**: Install "Anthropic Conversation" integration
   - **Free**: Use built-in Home Assistant Conversation

2. In Sense integration options:
   - **AI Provider**: Select your provider (or "Disabled")
   - **Monthly Token Budget**: Choose your budget level
   - Click **Submit**

3. Integration will reload and AI sensors will appear!

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

### Analytics Sensors (New!)
| Sensor | Unit | Description |
|--------|------|-------------|
| `sensor.sense_peak_power` | W | Peak power today |
| `sensor.sense_avg_power` | W | Average power consumption |
| `sensor.sense_recent_15min_avg` | W | 15-minute average power |
| `sensor.sense_solar_peak` | W | Peak solar production today |
| `sensor.sense_solar_self_consumption` | % | Solar self-consumption rate |

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
- `binary_sensor.sense_anomaly_detection` - Alerts when power usage is unusual
- Switches for controllable devices (smart plugs)

### AI Sensors (When Enabled)
| Sensor | Update Frequency | Description |
|--------|------------------|-------------|
| `sensor.sense_ai_daily_insights` | Daily at 8 AM | Morning summary with recommendations |
| `sensor.sense_ai_solar_coach` | Every 15 min | Real-time solar optimization |
| `sensor.sense_ai_bill_forecast` | Daily | Predictive monthly bill |
| `sensor.sense_ai_weekly_story` | Weekly | Engaging energy narrative |
| `sensor.sense_ai_optimization_suggestions` | Daily | AI-generated automations |
| `sensor.sense_ai_comparative_analysis` | Weekly | Compare to similar homes |
| `sensor.sense_ai_anomaly_explanation` | On anomaly | Explains unusual spikes |

## Services

### Standard Services

#### Get Device Info
```yaml
service: sense.get_device_info
data:
  device_id: "abc123def456"
```

#### Reset Device
```yaml
service: sense.reset_device
data:
  device_id: "abc123def456"
```

#### Rename Device
```yaml
service: sense.rename_device
data:
  device_id: "abc123def456"
  name: "Living Room Lamp"
```

### AI Services (When Enabled)

#### Ask AI About Energy
```yaml
service: sense.ask_ai
data:
  question: "Why is my power usage higher than usual today?"
```

#### Identify Unknown Device
```yaml
service: sense.identify_device
data:
  device_id: "unknown_device_123"
```

#### Explain Current Anomaly
```yaml
service: sense.explain_anomaly
```

#### Generate Insights On-Demand
```yaml
service: sense.generate_insights
data:
  period: "daily"  # or "weekly", "monthly"
```

#### Get Optimization Suggestions
```yaml
service: sense.generate_optimization
```

#### Check Privacy Info
```yaml
service: sense.get_privacy_info
```

#### Estimate AI Costs
```yaml
service: sense.get_cost_estimate
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

### Anomaly Detection with AI Explanation
```yaml
automation:
  - alias: "Power Anomaly Alert with AI"
    trigger:
      - platform: state
        entity_id: binary_sensor.sense_anomaly_detection
        to: "on"
    action:
      - service: sense.explain_anomaly
      - service: notify.mobile_app
        data:
          message: "⚠️ Power anomaly detected! {{ states('sensor.sense_ai_anomaly_explanation') }}"
```

### Daily AI Insights Notification
```yaml
automation:
  - alias: "Morning Energy Insights"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.mobile_app
        data:
          message: "☀️ {{ states('sensor.sense_ai_daily_insights') }}"
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

### Ask AI About Bill Increases
```yaml
automation:
  - alias: "Explain Bill Increase"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sense_monthly_usage
        above: 800  # kWh
    action:
      - service: sense.ask_ai
        data:
          question: "Why is my monthly usage so high? What can I do to reduce it?"
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
- Check your update rate setting (too fast may hit rate limits)

### Missing Devices
- Wait for Sense to detect and learn devices (can take several days)
- Check the Sense mobile app to see if devices are detected there first
- Some devices may not be detectable due to their power signature

### AI Features Not Working
- Verify you've selected an AI provider (not "Disabled")
- Check that the conversation integration is installed and configured
- Enable debug logging to see AI calls
- Check `sense.get_privacy_info` to verify configuration

### Enable Debug Logging
```yaml
logger:
  default: info
  logs:
    custom_components.sense: debug
```

## Documentation

- **[AI_FEATURES.md](AI_FEATURES.md)** - Complete AI features documentation
- **[ADVANCED_FEATURES.md](ADVANCED_FEATURES.md)** - Advanced usage and automation examples
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and changes
- **[ROADMAP.md](ROADMAP.md)** - Future development plans

## API Information

This integration uses the official Sense API library:
- [sense_energy](https://github.com/scottbonline/sense) Python library (v0.13.8+)
- Sense cloud API endpoints
- WebSocket for real-time data

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
- OpenAI & Anthropic for AI capabilities

## Changelog

See [CHANGELOG.md](CHANGELOG.md) or [RELEASES](https://github.com/JoshuaSeidel/hass-sense/releases) for version history and changes.

---

**Disclaimer:** This integration is not affiliated with, endorsed by, or connected to Sense. All product names, logos, and brands are property of their respective owners.
