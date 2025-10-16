# Debugging the Sense Integration

## Quick Test Script

If your integration connects but shows no data, run this test script:

```bash
cd /config/custom_components/sense
python3 test_api.py your_email@example.com your_password
```

This will show you:
- ✅ If authentication works
- ✅ What your Monitor ID is
- ✅ What data the API returns
- ✅ If the issue is with the API or the integration

## Enable Debug Logging

Add to `/config/configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.sense: debug
```

Restart Home Assistant, then check **Settings → System → Logs**.

## What to Look For

### Good Signs (Everything Working):
```
Successfully authenticated with Sense API - Monitor ID: 1000005242
Updated real-time data: 1234W, Solar: 567W, Voltage: [120, 120], Hz: 60
Coordinator data update: active_power=1234, devices=5
```

### Problem Signs (No Data):
```
No data returned from realtime status endpoint
Realtime API response: None
active_power=0
```

## Using Home Assistant Diagnostics

The integration now includes built-in diagnostics:

1. Go to **Settings → Devices & Services**
2. Find **Sense Energy Monitor**
3. Click on it
4. Click **Download Diagnostics**

This will download a JSON file with all the integration state and data.

## Common Issues

### Issue: "No data returned from realtime status endpoint"
**Cause:** The API endpoint structure changed
**Solution:** Run test_api.py to see what data is actually returned

### Issue: Sensors show "unavailable"
**Cause:** Coordinator not updating
**Solution:** Check logs for errors, reload integration

### Issue: Sensors stuck at 0
**Cause:** API returning 0 or wrong data format
**Solution:** Check test_api.py output

## Manual API Test with curl

You can also test manually:

```bash
# Step 1: Authenticate
curl -X POST https://api.sense.com/apiservice/api/v1/authenticate \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=YOUR_EMAIL&password=YOUR_PASSWORD"

# Copy the access_token and monitor_id from response

# Step 2: Get status
curl https://api.sense.com/apiservice/api/v1/app/monitors/MONITOR_ID/status \
  -H "Authorization: Bearer ACCESS_TOKEN"
```

## Reporting Issues

When reporting issues, include:

1. Output from `test_api.py`
2. Relevant logs (with debug enabled)
3. Downloaded diagnostics file
4. Home Assistant version
5. Integration version (from manifest.json)

Post issues at: https://github.com/JoshuaSeidel/hass-sense/issues

