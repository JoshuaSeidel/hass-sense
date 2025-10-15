# Testing Guide

## Quick Test Installation

### Step 1: Install the Integration

**Option A: Direct Git Clone (Fastest)**
```bash
# SSH into your Home Assistant instance or use the Terminal add-on

cd /config/custom_components
git clone https://github.com/JoshuaSeidel/hass-sense.git sense

# Restart Home Assistant
```

**Option B: Manual Download**
1. Download the latest release from: https://github.com/JoshuaSeidel/hass-sense/releases/tag/v1.0.0
2. Extract the `custom_components/sense` folder to your Home Assistant config
3. Restart Home Assistant

### Step 2: Configure the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration** (bottom right)
3. Search for "**Sense Energy Monitor**"
4. Enter your credentials:
   - **Email**: Your Sense account email
   - **Password**: Your Sense account password
   - **Timeout**: 30 (default)
5. Click **Submit**

### Step 3: Verify Installation

#### Check the Device
1. Go to **Settings** → **Devices & Services** → **Sense Energy Monitor**
2. You should see your Sense Energy Monitor device
3. Click on it to see all entities

#### Check the Sensors

Navigate to **Developer Tools** → **States** and search for `sense`:

**Expected Sensors:**
- ✅ `sensor.sense_active_power` - Current power usage (W)
- ✅ `sensor.sense_solar_power` - Current solar production (W)
- ✅ `sensor.sense_voltage_l1` - Line 1 voltage (V)
- ✅ `sensor.sense_voltage_l2` - Line 2 voltage (V)
- ✅ `sensor.sense_frequency` - Grid frequency (Hz)
- ✅ `sensor.sense_daily_usage` - Today's energy usage (kWh)
- ✅ `sensor.sense_daily_production` - Today's solar production (kWh)
- ✅ `sensor.sense_weekly_usage` - This week's energy usage (kWh)
- ✅ `sensor.sense_weekly_production` - This week's solar production (kWh)
- ✅ `sensor.sense_monthly_usage` - This month's energy usage (kWh)
- ✅ `sensor.sense_monthly_production` - This month's solar production (kWh)
- ✅ `sensor.sense_yearly_usage` - This year's energy usage (kWh)
- ✅ `sensor.sense_yearly_production` - This year's solar production (kWh)

**Expected Binary Sensors:**
- ✅ `binary_sensor.sense_[device_name]` - One for each detected device

**Expected Switches:**
- ✅ `switch.sense_[device_name]_switch` - One for each controllable device

### Step 4: Test Core Functionality

#### Test 1: Real-time Data
1. Open **Developer Tools** → **States**
2. Find `sensor.sense_active_power`
3. Verify it shows your current power usage
4. Turn on a high-power device (microwave, hair dryer, etc.)
5. Wait 60 seconds and refresh
6. Verify the power reading increased

#### Test 2: Device Detection
1. Check your Sense mobile app for detected devices
2. In Home Assistant, go to **Developer Tools** → **States**
3. Search for binary sensors: `binary_sensor.sense_`
4. Verify you see sensors for your detected devices
5. Turn a device on/off and wait 60 seconds
6. Verify the binary sensor state changes

#### Test 3: Energy Statistics
1. Go to **Developer Tools** → **States**
2. Find `sensor.sense_daily_usage`
3. Verify it shows a reasonable kWh value
4. Note the value
5. Wait a few hours
6. Check again - it should have increased

#### Test 4: Services
Test the device information service:
1. Go to **Developer Tools** → **Services**
2. Select `sense.get_device_info`
3. Enter a device ID (find from device attributes)
4. Click "Call Service"
5. Check the logs or listen for the `sense_device_info` event

### Step 5: Energy Dashboard Integration

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click **Add Consumption**
3. Select `sensor.sense_daily_usage`
4. Save

If you have solar:
1. Click **Add Solar Production**
2. Select `sensor.sense_daily_production`
3. Save

Wait a few hours for data to populate, then check the Energy Dashboard.

### Step 6: Create a Test Automation

```yaml
alias: "Test Sense High Power Alert"
description: "Alert when power usage exceeds 3000W"
trigger:
  - platform: numeric_state
    entity_id: sensor.sense_active_power
    above: 3000
action:
  - service: persistent_notification.create
    data:
      title: "High Power Usage"
      message: "Power usage is {{ states('sensor.sense_active_power') }}W"
mode: single
```

1. Create this automation in **Settings** → **Automations & Scenes**
2. Turn on several high-power devices
3. Verify you get the notification when power exceeds 3000W

## Troubleshooting Tests

### Test Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.sense: debug
```

Restart Home Assistant and check **Settings** → **System** → **Logs**

Look for entries like:
- `Successfully authenticated with Sense API`
- `Updated real-time data: XXXW, Solar: XXXW`
- `Updated trend data`

### Test Reload

1. Go to **Settings** → **Devices & Services**
2. Find **Sense Energy Monitor**
3. Click the three dots (⋮)
4. Select **Reload**
5. Verify all sensors come back online

### Test Error Handling

Test with wrong credentials:
1. Go to **Settings** → **Devices & Services**
2. Add a new Sense integration
3. Enter incorrect password
4. Verify you get an appropriate error message

## Performance Testing

### Check Update Frequency

1. Go to **Developer Tools** → **States**
2. Find `sensor.sense_active_power`
3. Note the "Last Updated" timestamp
4. Refresh the page every 30 seconds
5. Verify updates occur approximately every 60 seconds

### Check API Calls

Enable debug logging and monitor logs for:
- Authentication calls (should be infrequent)
- Real-time updates (every 60 seconds)
- Trend data updates (every 5 minutes or as configured)

## Success Criteria

✅ **Basic Functionality**
- [ ] Integration installs without errors
- [ ] Configuration flow completes successfully
- [ ] All 14+ sensors are created
- [ ] Sensors update every ~60 seconds
- [ ] Values are accurate and reasonable

✅ **Device Detection**
- [ ] Binary sensors created for detected devices
- [ ] Device states update correctly
- [ ] Device attributes are populated

✅ **Energy Dashboard**
- [ ] Can add consumption sensor
- [ ] Can add production sensor (if solar)
- [ ] Data appears in Energy Dashboard

✅ **Services**
- [ ] Services are registered
- [ ] Services can be called without errors

✅ **Stability**
- [ ] No errors in logs during normal operation
- [ ] Survives Home Assistant restart
- [ ] Reconnects after network issues

## Known Limitations

1. **Update Frequency**: 60-second updates (API limitation)
2. **Device Control**: Limited to TP-Link Kasa and Wemo smart plugs
3. **Authentication**: No 2FA support (API limitation)
4. **WebSocket**: Not implemented in this version (uses polling)

## Reporting Issues

If you find issues during testing, please report them with:

1. **Home Assistant version**
2. **Integration version** (1.0.0)
3. **Error messages** from logs
4. **Steps to reproduce**
5. **Expected vs actual behavior**

Open an issue at: https://github.com/JoshuaSeidel/hass-sense/issues

## Next Steps

After successful testing:
- ⭐ Star the repository if you find it useful
- 📝 Provide feedback on missing features
- 🐛 Report any bugs you encounter
- 🤝 Contribute improvements via Pull Requests

Happy testing! 🎉

