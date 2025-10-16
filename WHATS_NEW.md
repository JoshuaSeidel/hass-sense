# What's New in v1.3.0 🚀

## TL;DR
**Your Sense integration is now WAY more powerful!** We've added:
- ⚡ **Configurable real-time updates** (as fast as 5 seconds!)
- 🏗️ **Better architecture** (separate coordinators for efficiency)
- ⚙️ **Options flow** (change settings without re-adding)
- 📚 **Advanced features guide** (cost tracking, automations, solar optimization)
- 🤖 **Agent instructions** (better AI assistance for development)

---

## 🎯 The Big Picture

### Before v1.2.2
- Everything worked, but was "one size fits all"
- Fixed 60-second updates
- Single coordinator handled everything
- No way to customize

### After v1.3.0
- **YOU control update speed** (5s to 5min)
- **Smarter architecture** (realtime vs historical data separate)
- **Better performance** (less wasted API calls)
- **More features** (comprehensive guide for power users)

---

## ✨ What Changed

### 1. Configurable Update Rates

**During Setup:**
When you add the integration, you now see:
```
Update Interval: [dropdown]
  - 5 seconds (Very Fast - High API usage)
  - 10 seconds (Fast)
  - 15 seconds
  - 30 seconds (Balanced)
  - 60 seconds (Default) ← Recommended
  - 2 minutes (Slow)
  - 5 minutes (Very Slow)
```

**After Setup:**
1. Go to Settings → Devices & Services → Sense
2. Click "Configure"
3. Change update rate
4. Restart integration

**Why This Matters:**
- **5s updates** = Near real-time power monitoring! 📊
- **60s (default)** = Great balance for most users
- **300s updates** = Minimal API usage for simple monitoring

### 2. Separate Coordinators

**Technical Win:**

**Before:** One coordinator updated everything every 60s
```
Every 60s:
  ✓ Power data (needs frequent updates)
  ✓ Voltage (needs frequent updates)
  ✓ Daily usage (rarely changes)
  ✓ Monthly usage (rarely changes)
```

**After:** Two coordinators, each optimized
```
Realtime Coordinator (your chosen rate):
  ✓ Power consumption
  ✓ Solar production
  ✓ Voltage L1 & L2
  ✓ Grid frequency

Trends Coordinator (every 5 minutes):
  ✓ Daily usage/production
  ✓ Weekly usage/production
  ✓ Monthly usage/production
  ✓ Yearly usage/production
```

**Result:** 
- Faster realtime data when you want it
- Less API load overall
- Better performance

### 3. Advanced Features Guide

**NEW FILE:** `ADVANCED_FEATURES.md`

This comprehensive guide shows you how to:

#### 💰 Track Energy Costs
```yaml
# Instant cost per hour
sensor.energy_cost_per_hour: "$1.20/hr"

# Daily cost
sensor.daily_energy_cost: "$14.32"

# Projected monthly bill
sensor.projected_monthly_bill: "$432.50"
```

#### ⚡ Detect Peak Power
```yaml
# Get alerts when power is high
binary_sensor.high_power_alert: on
  current: 8,500W
  threshold: 5,000W
```

#### 📊 Predict Future Bills
```yaml
# Based on your usage trends
sensor.projected_monthly_usage: "948 kWh"
sensor.energy_budget_status: "105%"  # Over budget!
```

#### 🤖 Smart Automations
- Load shedding (turn off non-essentials during high usage)
- Off-peak scheduling (run appliances during cheap electricity)
- Solar-aware automation (use appliances when sun is out)
- Budget alerts (notify when approaching limit)

#### ☀️ Solar Optimization
```yaml
# Track solar efficiency
sensor.solar_self_consumption: "87%"
sensor.net_power_flow: "-1,250W"  # Exporting to grid

# Get alerts
automation: "Notify When Solar is Wasted"
```

---

## 🎓 How to Use

### For Most Users (Recommended)

**Just upgrade and enjoy!**
- Default 60s updates work great
- Everything else is automatic
- No configuration needed

### For Power Monitoring Enthusiasts

**Want near-real-time data?**
1. Go to Integration Options
2. Change update rate to 10s or 15s
3. Restart integration
4. Watch your dashboard update in near-real-time!

**Want to save API calls?**
1. Go to Integration Options
2. Change update rate to 120s or 300s
3. Restart integration
4. Still get all the data, just less frequently

### For Advanced Users

**Unlock the full potential:**
1. Read `ADVANCED_FEATURES.md`
2. Add template sensors for costs
3. Set up automations
4. Create custom dashboards
5. Track budgets and goals

---

## 📊 Comparison

### This Integration vs Official

| Feature | Official | Us (v1.3.0) |
|---------|----------|-------------|
| Basic Sensors | ✅ | ✅ |
| Binary Sensors | ✅ | ✅ |
| Device Detection | ✅ | ✅ |
| **Switch Control** | ❌ | ✅ Unique! |
| **Custom Services** | ❌ | ✅ Unique! |
| Update Rate | Fixed 60s | **5s to 5min** |
| Options Flow | ❌ | ✅ |
| Separate Coordinators | ✅ | ✅ |
| **Advanced Features Guide** | ❌ | ✅ 50+ examples! |
| **Cost Tracking** | ❌ | ✅ Via templates |
| **Real-time (5s)** | ❌ | ✅ |

### Real-World Examples

**Scenario 1: Home Power Monitoring**
- **Setting:** 60s updates (default)
- **Result:** Perfect balance, works like official but with more features

**Scenario 2: EV Charging Monitoring**
- **Setting:** 10s updates
- **Result:** See power draw change in real-time as car charges
- **Use Case:** Verify charger is working, track exact start/stop

**Scenario 3: Solar Production Tracking**
- **Setting:** 15s updates
- **Result:** Watch solar production respond to cloud cover
- **Use Case:** Optimize appliance usage based on solar

**Scenario 4: Simple Monthly Tracking**
- **Setting:** 5min updates (300s)
- **Result:** Minimal API usage, still get daily/monthly totals
- **Use Case:** Just want to see monthly bills, don't need live data

---

## 🔮 What's Next

### v1.4.0 (Coming Soon)
- **Native cost sensors** (no template needed)
- **Per-device energy tracking**
- **Peak power sensors**
- **Grid flow sensors**
- **Carbon footprint estimation**

### v2.0.0 (Future)
- **ML anomaly detection** (auto-detect unusual usage)
- **Predictive maintenance** (predict appliance issues)
- **Energy advisor** (AI suggestions for savings)
- **Gamification** (energy saving challenges)

---

## 💡 Pro Tips

1. **Start with defaults** - 60s works great for most
2. **Use advanced features guide** - Tons of free value
3. **Set up cost tracking** - See real money impact
4. **Create automations** - Save money automatically
5. **Monitor your solar** - Maximize self-consumption
6. **Track budgets** - Stay under monthly limits
7. **Join the community** - Share your setups!

---

## 🙏 Thank You!

v1.3.0 represents a **huge leap forward**:
- More flexible
- Better performance
- Advanced features
- Future-proof architecture

Your feedback drives development. Got ideas? [Open an issue](https://github.com/JoshuaSeidel/hass-sense/issues)!

---

## 📚 Documentation

- **README.md** - Installation & basics
- **ADVANCED_FEATURES.md** - Power user guide (NEW!)
- **CHANGELOG.md** - All changes
- **ROADMAP.md** - Future plans
- **TROUBLESHOOTING.md** - Fix issues
- **.cursorrules** - Development guide

---

## 🚀 Get Started

**Already using it?**
```bash
# Via HACS:
Just click "Update" on the integration

# Manually:
cd /config/custom_components/sense
git pull origin main
```

**New user?**
Check out [README.md](README.md) for installation instructions!

---

**Enjoy your supercharged Sense integration!** ⚡️

