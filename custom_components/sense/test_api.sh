#!/bin/bash
# Simple bash script to test Sense API without Python dependencies

if [ "$#" -ne 2 ]; then
    echo ""
    echo "Usage: ./test_api.sh <email> <password>"
    echo ""
    echo "Example:"
    echo "  ./test_api.sh user@example.com mypassword"
    echo ""
    exit 1
fi

EMAIL="$1"
PASSWORD="$2"
API_URL="https://api.sense.com/apiservice/api/v1"

echo ""
echo "======================================================================"
echo "SENSE API CONNECTION TEST"
echo "======================================================================"
echo ""

# Step 1: Authentication
echo "Step 1: Testing Authentication..."
echo "----------------------------------------------------------------------"

AUTH_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST "${API_URL}/authenticate" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: Home-Assistant-Sense/1.0.0" \
  -d "email=${EMAIL}&password=${PASSWORD}")

HTTP_CODE=$(echo "$AUTH_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
AUTH_DATA=$(echo "$AUTH_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Authentication failed with HTTP status: $HTTP_CODE"
    echo "   Response: $AUTH_DATA"
    exit 1
fi

echo "✅ Authentication successful!"

# Extract data using grep and sed (works without jq)
ACCESS_TOKEN=$(echo "$AUTH_DATA" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
USER_ID=$(echo "$AUTH_DATA" | grep -o '"user_id":[0-9]*' | cut -d: -f2)
MONITOR_ID=$(echo "$AUTH_DATA" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)

if [ -z "$ACCESS_TOKEN" ]; then
    echo "❌ No access token in response"
    echo "   Response: $AUTH_DATA"
    exit 1
fi

if [ -z "$MONITOR_ID" ]; then
    echo "❌ No monitor found in account"
    echo "   Response: $AUTH_DATA"
    exit 1
fi

echo "   User ID: $USER_ID"
echo "   Monitor ID: $MONITOR_ID"
echo "   Access Token: ${ACCESS_TOKEN:0:20}..."

# Step 2: Get Realtime Status
echo ""
echo "Step 2: Testing Realtime Data Endpoint..."
echo "----------------------------------------------------------------------"

STATUS_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  "${API_URL}/app/monitors/${MONITOR_ID}/status" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "User-Agent: Home-Assistant-Sense/1.0.0")

HTTP_CODE=$(echo "$STATUS_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
STATUS_DATA=$(echo "$STATUS_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Status endpoint failed with HTTP status: $HTTP_CODE"
    echo "   Response: $STATUS_DATA"
    exit 1
fi

echo "✅ Realtime data retrieved!"

# Extract power data
ACTIVE_POWER=$(echo "$STATUS_DATA" | grep -o '"w":[0-9.]*' | head -1 | cut -d: -f2)
SOLAR_POWER=$(echo "$STATUS_DATA" | grep -o '"solar_w":[-0-9.]*' | head -1 | cut -d: -f2)
FREQUENCY=$(echo "$STATUS_DATA" | grep -o '"hz":[0-9.]*' | head -1 | cut -d: -f2)

echo "   Active Power: ${ACTIVE_POWER:-N/A} W"
echo "   Solar Power: ${SOLAR_POWER:-N/A} W"
echo "   Frequency: ${FREQUENCY:-N/A} Hz"

# Check if we got data
if [ -z "$ACTIVE_POWER" ] && [ -z "$SOLAR_POWER" ]; then
    echo ""
    echo "⚠️  WARNING: No power data found in response!"
    echo "   This means the API endpoint returned data but in an unexpected format."
    echo ""
    echo "   Raw response (first 500 chars):"
    echo "   ${STATUS_DATA:0:500}"
else
    echo ""
    echo "   ✓ Power data is being returned from API"
fi

# Step 3: Get Devices
echo ""
echo "Step 3: Testing Devices Endpoint..."
echo "----------------------------------------------------------------------"

DEVICES_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" \
  "${API_URL}/app/monitors/${MONITOR_ID}/devices" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "User-Agent: Home-Assistant-Sense/1.0.0")

HTTP_CODE=$(echo "$DEVICES_RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
DEVICES_DATA=$(echo "$DEVICES_RESPONSE" | sed '/HTTP_CODE:/d')

if [ "$HTTP_CODE" != "200" ]; then
    echo "⚠️  Devices endpoint returned HTTP status: $HTTP_CODE"
    echo "   (This is optional, may not work for all accounts)"
else
    echo "✅ Devices endpoint accessible"
    DEVICE_COUNT=$(echo "$DEVICES_DATA" | grep -o '"name"' | wc -l | tr -d ' ')
    echo "   Found ~$DEVICE_COUNT devices in response"
fi

echo ""
echo "======================================================================"
echo "✅ TEST COMPLETE"
echo "======================================================================"
echo ""
echo "Summary:"
echo "  - Authentication: ✅ Working"
echo "  - Monitor ID: $MONITOR_ID"
echo "  - Realtime Data: $([ ! -z "$ACTIVE_POWER" ] && echo "✅ Working" || echo "⚠️  No data")"
echo "  - Active Power: ${ACTIVE_POWER:-N/A} W"
echo ""

if [ -z "$ACTIVE_POWER" ] && [ -z "$SOLAR_POWER" ]; then
    echo "⚠️  ISSUE DETECTED: API returns data but power values are missing"
    echo ""
    echo "Next steps:"
    echo "  1. Check if your Sense monitor is online in the mobile app"
    echo "  2. Save the raw response above and report it"
    echo "  3. The API format may have changed"
    echo ""
    exit 1
else
    echo "✅ Everything looks good! Data is flowing from the API."
    echo ""
    echo "If Home Assistant sensors still show no data:"
    echo "  1. Enable debug logging in configuration.yaml"
    echo "  2. Check Home Assistant logs for parsing errors"
    echo "  3. Try reloading the integration"
    echo ""
fi

