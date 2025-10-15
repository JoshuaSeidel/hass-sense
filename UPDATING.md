# Updating to v1.0.1

## What's Fixed

The v1.0.1 release fixes the **415 "Unsupported Media Type"** authentication error that prevented the integration from connecting to the Sense API.

## How to Update

### If You're Using Git Clone

```bash
cd /config/custom_components/sense
git pull origin main
```

Then restart Home Assistant.

### If You Installed Manually

1. Download the latest release: https://github.com/JoshuaSeidel/hass-sense/releases/tag/v1.0.1
2. Replace the files in `/config/custom_components/sense/`
3. Restart Home Assistant

### If You're Using HACS

HACS should automatically detect the update. If not:
1. Go to HACS → Integrations
2. Find "Sense Energy Monitor"
3. Click "Update"
4. Restart Home Assistant

## After Updating

If you already tried to configure the integration and got the authentication error:

1. Go to **Settings** → **Devices & Services**
2. Find the **Sense Energy Monitor** integration
3. Click the three dots (⋮) and select **Delete**
4. Click **+ Add Integration**
5. Search for "Sense Energy Monitor"
6. Enter your credentials again

The authentication should now work correctly! ✅

## Verifying the Fix

After reconfiguring:
1. Check that sensors appear in **Developer Tools** → **States**
2. Look for `sensor.sense_active_power` and other Sense sensors
3. Verify they're updating with real data

## Still Having Issues?

If you still encounter problems:
1. Check the logs at **Settings** → **System** → **Logs**
2. Look for any errors from `custom_components.sense`
3. Report issues at: https://github.com/JoshuaSeidel/hass-sense/issues

Include:
- Your Home Assistant version
- The complete error message from logs
- Steps you took before the error occurred

