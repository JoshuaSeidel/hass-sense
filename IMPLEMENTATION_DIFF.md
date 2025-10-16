# Critical Implementation Differences

## Key Issues Found

### 1. **Authentication Method** ⚠️ CRITICAL

**Official:**
```python
# Stores tokens in config entry
access_token = entry_data.get("access_token", "")
user_id = entry_data.get("user_id", "")
device_id = entry_data.get("device_id", "")
refresh_token = entry_data.get("refresh_token", "")
monitor_id = entry_data.get("monitor_id", "")

# Loads existing auth
gateway.load_auth(access_token, user_id, device_id, refresh_token)
gateway.set_monitor_id(monitor_id)
```

**Ours:**
```python
# Re-authenticates every time
email = entry_data[CONF_EMAIL]
password = entry_data[CONF_PASSWORD]
await gateway.authenticate(email, password)
```

**Problem:** We're authenticating from scratch every restart instead of using stored tokens!

**Fix Needed:** 
- Store tokens in config entry after first auth
- Use `load_auth()` instead of `authenticate()` on subsequent loads
- This will be faster and more reliable

---

### 2. **Executor Job for Initialization** ⚠️ CRITICAL

**Official:**
```python
gateway = await hass.async_add_executor_job(
    partial(
        ASyncSenseable,
        api_timeout=timeout,
        wss_timeout=timeout,
        client_session=client_session,
    )
)
```

**Ours:**
```python
gateway = ASyncSenseable(
    api_timeout=timeout,
    wss_timeout=timeout,
    client_session=client_session
)
```

**Problem:** Creating ASyncSenseable does blocking I/O (SSL cert loading). Should run in executor!

**Fix Needed:** Use `hass.async_add_executor_job()` with `functools.partial`

---

### 3. **Device Fetching** ⚠️ IMPORTANT

**Official:**
```python
await gateway.fetch_devices()  # Fetch devices separately
await gateway.update_realtime()
```

**Ours:**
```python
await gateway.update_realtime()  # Only update realtime
```

**Problem:** We're not fetching the device list properly!

**Fix Needed:** Call `gateway.fetch_devices()` before first realtime update

---

### 4. **Exception Handling** ⚠️ CRITICAL

**Official Uses:**
```python
from sense_energy import (
    SenseAuthenticationException,
    SenseMFARequiredException,
    SenseAPIException,
    SenseAPITimeoutException,
    SenseWebsocketException,
)

SENSE_TIMEOUT_EXCEPTIONS = (TimeoutError, SenseAPITimeoutException)
SENSE_WEBSOCKET_EXCEPTIONS = (socket.gaierror, SenseWebsocketException)
SENSE_CONNECT_EXCEPTIONS = (
    socket.gaierror,
    TimeoutError,
    SenseAPITimeoutException,
    SenseAPIException,
)
```

**Ours Uses:**
```python
SENSE_TIMEOUT_EXCEPTIONS = (asyncio.TimeoutError,)
SENSE_WEBSOCKET_EXCEPTIONS = (ClientError, ConnectionError, OSError)
```

**Problem:** We're not using the library's specific exceptions!

**Fix Needed:** Import and use `sense_energy` exception classes

---

### 5. **Coordinator Structure** ⚠️ CRITICAL

**Official:**
```python
# Separate coordinators
trends_coordinator = SenseTrendCoordinator(hass, entry, gateway)
realtime_coordinator = SenseRealtimeCoordinator(hass, entry, gateway)

# Background tasks
entry.async_create_background_task(
    hass,
    trends_coordinator.async_request_refresh(),
    "sense.trends-coordinator-refresh",
)
```

**Ours:**
```python
# Single coordinator doing everything
coordinator = DataUpdateCoordinator(...)
```

**Problem:** Single coordinator updates everything every 60s (inefficient!)

**Fix Needed:** Split into separate coordinators with different update intervals

---

### 6. **Data Storage** ⚠️ IMPORTANT

**Official:**
```python
@dataclass(kw_only=True, slots=True)
class SenseData:
    data: ASyncSenseable
    trends: SenseTrendCoordinator
    rt: SenseRealtimeCoordinator

entry.runtime_data = SenseData(
    data=gateway,
    trends=trends_coordinator,
    rt=realtime_coordinator,
)
```

**Ours:**
```python
hass.data[DOMAIN][entry.entry_id] = {
    "coordinator": coordinator,
    "gateway": gateway,
}
```

**Problem:** Not using type-safe dataclass storage

**Fix Needed:** Create SenseData dataclass

---

### 7. **Rate Limiting** ⚠️ IMPORTANT

**Official:**
```python
gateway.rate_limit = ACTIVE_UPDATE_RATE  # Set rate limit on gateway
```

**Ours:**
```python
# Rate limit only in coordinator update_interval
```

**Problem:** Gateway itself should have rate limit set

**Fix Needed:** Set `gateway.rate_limit = ACTIVE_UPDATE_RATE`

---

### 8. **Trend Update Rate** ⚠️ IMPORTANT

**Official:**
```python
ACTIVE_UPDATE_RATE = 60    # Realtime: every 60s
TREND_UPDATE_RATE = 300    # Trends: every 5 minutes
```

**Ours:**
```python
ACTIVE_UPDATE_RATE = 60    # Everything: every 60s
```

**Problem:** Updating trends every 60s wastes API calls!

**Fix Needed:** Update trends only every 5 minutes

---

## Implementation Checklist

### Phase 1: Critical Fixes (v1.2.2)
- [ ] Use executor job for gateway creation
- [ ] Import proper exception classes from sense_energy
- [ ] Update exception handling to use library exceptions
- [ ] Call `gateway.fetch_devices()` before realtime update
- [ ] Set `gateway.rate_limit = ACTIVE_UPDATE_RATE`
- [ ] Fix attribute mapping (use getattr with proper names)

### Phase 2: Auth Improvements (v1.3.0)
- [ ] Store tokens in config entry after auth
- [ ] Use `load_auth()` instead of re-authenticating
- [ ] Implement token refresh logic
- [ ] Add device_id to stored auth data

### Phase 3: Architecture (v1.4.0)
- [ ] Split into separate coordinators
- [ ] Create SenseData dataclass
- [ ] Implement TREND_UPDATE_RATE (300s)
- [ ] Use runtime_data instead of hass.data dict

### Phase 4: Complete Parity (v1.5.0)
- [ ] Match all official sensors
- [ ] Add missing constants
- [ ] Implement proper unload
- [ ] Add icon mappings from MDI_ICONS

---

## Quick Fixes for v1.2.2

```python
# 1. Import proper exceptions
from sense_energy import (
    ASyncSenseable,
    SenseAuthenticationException,
    SenseMFARequiredException,
    SenseAPIException,
    SenseAPITimeoutException,
    SenseWebsocketException,
)
import socket

# 2. Update exception tuples
SENSE_TIMEOUT_EXCEPTIONS = (TimeoutError, SenseAPITimeoutException)
SENSE_WEBSOCKET_EXCEPTIONS = (socket.gaierror, SenseWebsocketException)

# 3. Use executor for gateway creation
from functools import partial

gateway = await hass.async_add_executor_job(
    partial(
        ASyncSenseable,
        api_timeout=timeout,
        wss_timeout=timeout,
        client_session=client_session,
    )
)

# 4. Set rate limit
gateway.rate_limit = ACTIVE_UPDATE_RATE

# 5. Fetch devices before realtime
await gateway.fetch_devices()
await gateway.update_realtime()
```

---

## Most Critical Issue

**The re-authentication problem:** We're calling `authenticate(email, password)` every time HA restarts instead of using stored tokens. This is:
1. Slower
2. Less reliable
3. May trigger rate limiting
4. Doesn't match how the official integration works

**Must fix this first!**

