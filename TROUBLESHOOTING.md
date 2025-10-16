# Troubleshooting Guide

## Issue: Integration Connects But No Data Appears

If your Sense integration authenticates successfully but sensors show no data or remain at 0, follow these steps:

### Step 1: Enable Debug Logging

Add to your `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.sense: debug
```

Restart Home Assistant and wait 2-3 minutes for updates to occur.

### Step 2: Check the Logs

Go to **Settings** → **System** → **Logs** and look for:

**✓ Good signs:**
```
Successfully authenticated with Sense API - Monitor ID: XXXXX, User ID: XXXXX
Updated real-time data: XXXW, Solar: XXXW, Voltage: [XXX, XXX], Hz: XX
Coordinator data update: active_power=XXX, devices=X
```

**✗ Problem indicators:**
```
No data returned from realtime status endpoint
Error updating realtime data
Realtime API response: None
```

### Step 3: Test the API Directly

Run the test script to verify API connectivity:

**Recommended (bash script - no dependencies):**
```bash
cd /config/custom_components/sense
chmod +x test_api.sh
./test_api.sh your_email@example.com your_password
```

**Alternative (Python script):**
```bash
cd /config/custom_components/sense
python3 test_api.py your_email@example.com your_password
```

This will show you exactly what data is being returned from the Sense API.

### Step 4: Common Issues and Solutions

#### Issue A: Authentication succeeds but status endpoint returns no data

**Symptoms:**
- Logs show "Successfully authenticated"
- Logs show "No data returned from realtime status endpoint"

**Solution:**
The `/status` endpoint may have changed. Check the logs from the test script to see what data structure is returned.

#### Issue B: Sensors exist but show "unavailable"

**Symptoms:**
- Sensors appear in Developer Tools → States
- All sensors show "unavailable" or "unknown"

**Solution:**
1. Check if coordinator is updating:
   ```
   Look for: "Coordinator data update: active_power=XXX"
   ```
2. If no coordinator updates, the API calls are failing
3. Check for error messages in logs

#### Issue C: Only some sensors work

**Symptoms:**
- Real-time power sensors work
- Historical sensors (daily/weekly/monthly) show 0

**Expected:**
This is normal if the trend data endpoints are unavailable. Real-time monitoring should still work.

#### Issue D: Data was working, now stopped

**Symptoms:**
- Integration worked before
- Now sensors show stale data or unavailable

**Solution:**
1. **Reload the integration:**
   - Settings → Devices & Services
   - Click the three dots on Sense integration
   - Select "Reload"

2. **Check API rate limiting:**
   - Sense may rate-limit if too many requests
   - Wait 15 minutes and try again

3. **Re-authenticate:**
   - Delete the integration
   - Restart Home Assistant
   - Add the integration again

### Step 5: Verify Sensor Entities

Check that sensors are created:

1. Go to **Developer Tools** → **States**
2. Filter by "sense"
3. You should see:
   - `sensor.sense_active_power`
   - `sensor.sense_solar_power`
   - `sensor.sense_voltage_l1`
   - `sensor.sense_voltage_l2`
   - `sensor.sense_frequency`
   - And more...

If sensors don't exist, the platforms didn't load correctly.

### Step 6: Check Sensor Values

1. Find `sensor.sense_active_power` in Developer Tools → States
2. Click on it to see details:
   - **State**: Should show a number (watts)
   - **Last Updated**: Should update every ~60 seconds
   - **Attributes**: Should show device info

If the state is "unavailable" or "unknown":
- The coordinator isn't providing data
- Check coordinator logs

### Step 7: Manual API Test

If the Python test script doesn't work, try the Sense mobile app:

1. Open the Sense mobile app
2. Verify you can see real-time power data
3. If the app doesn't show data, the issue is with your Sense monitor, not the integration

### Step 8: Check Home Assistant Version

Ensure you're running Home Assistant 2024.1.0 or newer:

1. Go to **Settings** → **System** → **About**
2. Check "Version"
3. If older, update Home Assistant first

### Step 9: Verify Network Connectivity

The integration requires internet access to reach api.sense.com:

```bash
# Test from Home Assistant host
curl -I https://api.sense.com/apiservice/api/v1/
```

Should return HTTP 200 or similar (not connection refused).

### Step 10: Check for Breaking API Changes

The Sense API is unofficial and can change:

1. Check the [GitHub issues](https://github.com/JoshuaSeidel/hass-sense/issues)
2. Look for recent reports of similar problems
3. Check if there's an updated version available

## Collecting Diagnostic Information

If you need to report an issue, collect this information:

1. **Home Assistant Version:**
   ```
   Settings → System → About → Version
   ```

2. **Integration Version:**
   ```
   Check custom_components/sense/manifest.json version field
   ```

3. **Relevant Logs:**
   ```
   Settings → System → Logs
   Filter by "sense"
   Copy the last 50-100 lines
   ```

4. **Test Script Output:**
   ```bash
   python3 test_sense_api.py your_email your_password > sense_test.log 2>&1
   ```

5. **Sensor States:**
   ```
   Developer Tools → States
   Export state of sensor.sense_active_power
   ```

## Quick Fixes Checklist

Try these in order:

- [ ] Reload the integration
- [ ] Restart Home Assistant
- [ ] Delete and re-add the integration
- [ ] Enable debug logging and check logs
- [ ] Run the test script
- [ ] Check Sense mobile app for data
- [ ] Verify internet connectivity
- [ ] Check for integration updates
- [ ] Report issue on GitHub with diagnostics

## Getting Help

If you've tried all the above and still have issues:

1. **GitHub Issues:** https://github.com/JoshuaSeidel/hass-sense/issues
2. **Home Assistant Community:** https://community.home-assistant.io/
3. **Include:**
   - Your troubleshooting steps
   - Diagnostic information
   - Log excerpts
   - Test script output

## Known Limitations

Current known issues:

1. **Historical trend data** may not work due to API changes
2. **Smart plug control** is limited to specific brands
3. **No WebSocket support** - uses polling (60s updates)
4. **No 2FA support** - accounts with 2FA won't work
5. **Single monitor** - multi-monitor setups not supported

These are API limitations, not integration bugs.

