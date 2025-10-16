# Advanced Features & Use Cases

This document shows how to leverage the Sense integration for advanced monitoring, automation, and cost tracking.

## 🎯 Quick Links
- [Cost Tracking](#-cost-tracking)
- [Peak Detection](#-peak-power-detection)
- [Predictive Analytics](#-predictive-analytics)
- [Smart Automations](#-smart-automations)
- [Solar Optimization](#-solar-optimization)
- [Energy Budgets](#-energy-budgets)

---

## 💰 Cost Tracking

### Template Sensors for Cost Calculation

Add these to your `configuration.yaml` to track costs:

```yaml
template:
  - sensor:
      # Current cost per hour
      - name: "Energy Cost Per Hour"
        unique_id: sense_cost_per_hour
        unit_of_measurement: "$/hr"
        state: >
          {{ (states('sensor.sense_active_power') | float / 1000 * 0.12) | round(3) }}
        attributes:
          rate: 0.12  # Your electricity rate per kWh
          
      # Daily energy cost
      - name: "Daily Energy Cost"
        unique_id: sense_daily_cost
        unit_of_measurement: "$"
        state: >
          {{ (states('sensor.sense_daily_usage') | float * 0.12) | round(2) }}
          
      # Daily solar savings
      - name: "Daily Solar Savings"
        unique_id: sense_daily_solar_savings
        unit_of_measurement: "$"
        state: >
          {{ (states('sensor.sense_daily_production') | float * 0.10) | round(2) }}
          
      # Net daily cost (usage - solar)
      - name: "Net Daily Energy Cost"
        unique_id: sense_net_daily_cost
        unit_of_measurement: "$"
        state: >
          {% set usage = states('sensor.sense_daily_usage') | float %}
          {% set production = states('sensor.sense_daily_production') | float %}
          {{ ((usage * 0.12) - (production * 0.10)) | round(2) }}
          
      # Projected monthly bill
      - name: "Projected Monthly Bill"
        unique_id: sense_projected_monthly_bill
        unit_of_measurement: "$"
        state: >
          {% set daily_cost = states('sensor.net_daily_energy_cost') | float %}
          {% set fixed_charges = 15.00 %}  # Your fixed monthly charges
          {{ (daily_cost * 30 + fixed_charges) | round(2) }}
```

### Time-of-Use (TOU) Rates

For utilities with time-of-use pricing:

```yaml
template:
  - sensor:
      - name: "Current Energy Rate"
        unique_id: sense_current_rate
        unit_of_measurement: "$/kWh"
        state: >
          {% set hour = now().hour %}
          {% if hour >= 16 and hour < 21 %}
            0.20  # Peak rate (4pm-9pm)
          {% elif hour >= 0 and hour < 6 %}
            0.08  # Super off-peak (midnight-6am)
          {% elif hour >= 21 or hour < 7 %}
            0.10  # Off-peak
          {% else %}
            0.12  # Standard
          {% endif %}
          
      - name: "Smart Energy Cost Per Hour"
        unique_id: sense_smart_cost_per_hour
        unit_of_measurement: "$/hr"
        state: >
          {% set power_kw = states('sensor.sense_active_power') | float / 1000 %}
          {% set rate = states('sensor.current_energy_rate') | float %}
          {{ (power_kw * rate) | round(3) }}
```

---

## ⚡ Peak Power Detection

### Detect and Alert on High Power Events

```yaml
template:
  - binary_sensor:
      - name: "High Power Alert"
        unique_id: sense_high_power_alert
        state: >
          {{ states('sensor.sense_active_power') | float > 5000 }}
        attributes:
          threshold: 5000
          current_power: "{{ states('sensor.sense_active_power') }}"
          
  - sensor:
      - name: "Peak Power Today"
        unique_id: sense_peak_power_today
        unit_of_measurement: "W"
        state: >
          {{ state_attr('sensor.sense_active_power', 'max_value') | default(0) }}

automation:
  - alias: "Alert on Peak Power"
    trigger:
      - platform: state
        entity_id: binary_sensor.high_power_alert
        to: 'on'
    action:
      - service: notify.mobile_app
        data:
          title: "High Power Usage!"
          message: >
            Current usage: {{ states('sensor.sense_active_power') }}W
            Cost per hour: ${{ states('sensor.energy_cost_per_hour') }}
```

### Track Peak Power Statistics

```yaml
# In configuration.yaml
recorder:
  exclude:
    entities:
      # ... exclude other sensors ...
  
sensor:
  - platform: statistics
    name: "Power Statistics Today"
    entity_id: sensor.sense_active_power
    state_characteristic: mean
    max_age:
      hours: 24
      
  - platform: statistics
    name: "Peak Power Today"
    entity_id: sensor.sense_active_power
    state_characteristic: value_max
    max_age:
      hours: 24
```

---

## 📊 Predictive Analytics

### Project Future Bills

```yaml
template:
  - sensor:
      # 7-day rolling average
      - name: "Average Daily Usage 7d"
        unique_id: sense_avg_daily_7d
        unit_of_measurement: "kWh"
        state: >
          {% set days = 7 %}
          {{ (states('sensor.sense_weekly_usage') | float / days) | round(2) }}
          
      # Projected monthly usage
      - name: "Projected Monthly Usage"
        unique_id: sense_projected_monthly
        unit_of_measurement: "kWh"
        state: >
          {% set daily_avg = states('sensor.average_daily_usage_7d') | float %}
          {% set days_in_month = 30 %}
          {{ (daily_avg * days_in_month) | round(1) }}
          
      # Projected vs Budget
      - name: "Energy Budget Status"
        unique_id: sense_budget_status
        unit_of_measurement: "%"
        state: >
          {% set projected = states('sensor.projected_monthly_usage') | float %}
          {% set budget = 900 %}  # Your monthly budget in kWh
          {{ ((projected / budget) * 100) | round(0) }}
        attributes:
          projected_kwh: "{{ states('sensor.projected_monthly_usage') }}"
          budget_kwh: 900
          over_budget: "{{ states('sensor.projected_monthly_usage') | float > 900 }}"
```

### Anomaly Detection

```yaml
automation:
  - alias: "Detect Unusual Energy Usage"
    trigger:
      - platform: state
        entity_id: sensor.sense_active_power
    condition:
      - condition: template
        value_template: >
          {% set current = trigger.to_state.state | float %}
          {% set avg = state_attr('sensor.power_statistics_today', 'mean') | float %}
          {{ current > (avg * 2) }}  # More than 2x average
    action:
      - service: notify.mobile_app
        data:
          title: "Unusual Energy Usage Detected"
          message: >
            Current: {{ states('sensor.sense_active_power') }}W
            Average: {{ state_attr('sensor.power_statistics_today', 'mean') | round(0) }}W
```

---

## 🤖 Smart Automations

### Off-Peak Charging/Running

Automate high-power devices to run during cheap electricity hours:

```yaml
automation:
  - alias: "Start EV Charging During Off-Peak"
    trigger:
      - platform: time
        at: "22:00:00"  # Off-peak starts
    condition:
      - condition: numeric_state
        entity_id: sensor.ev_battery
        below: 80
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
          
  - alias: "Stop EV Charging Before Peak"
    trigger:
      - platform: time
        at: "15:45:00"  # Before peak starts at 4pm
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

### Load Shedding

Automatically reduce power during high usage:

```yaml
automation:
  - alias: "Load Shedding - High Power"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sense_active_power
        above: 8000  # Your main breaker limit minus safety margin
    action:
      # Turn off non-essential loads
      - service: switch.turn_off
        target:
          entity_id:
            - switch.pool_pump
            - switch.water_heater
      - service: climate.set_temperature
        target:
          entity_id: climate.hvac
        data:
          temperature: 76  # Reduce AC load
      - service: notify.mobile_app
        data:
          title: "Load Shedding Active"
          message: "Power usage high, reducing non-essential loads"
```

### Solar-Aware Automation

Run appliances when solar is producing:

```yaml
automation:
  - alias: "Run Dishwasher During Solar Production"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sense_active_solar_power
        above: 2000  # 2kW solar production
        for:
          minutes: 5
    condition:
      - condition: time
        after: "10:00:00"
        before: "15:00:00"
      - condition: state
        entity_id: input_boolean.dishwasher_ready
        state: 'on'
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.dishwasher
      - service: input_boolean.turn_off
        target:
          entity_id: input_boolean.dishwasher_ready
```

---

## ☀️ Solar Optimization

### Track Solar Efficiency

```yaml
template:
  - sensor:
      # Solar self-consumption rate
      - name: "Solar Self-Consumption"
        unique_id: sense_solar_self_consumption
        unit_of_measurement: "%"
        state: >
          {% set production = states('sensor.sense_active_solar_power') | float %}
          {% set usage = states('sensor.sense_active_power') | float %}
          {% if production > 0 %}
            {{ (min(usage, production) / production * 100) | round(0) }}
          {% else %}
            0
          {% endif %}
          
      # Net power (negative = exporting to grid)
      - name: "Net Power Flow"
        unique_id: sense_net_power
        unit_of_measurement: "W"
        state: >
          {% set usage = states('sensor.sense_active_power') | float %}
          {% set production = states('sensor.sense_active_solar_power') | float %}
          {{ (usage - production) | round(0) }}
        attributes:
          status: >
            {% set net = (states('sensor.sense_active_power') | float - 
                         states('sensor.sense_active_solar_power') | float) %}
            {% if net < -100 %}
              Exporting to Grid
            {% elif net < 100 %}
              Zero Net
            {% else %}
              Drawing from Grid
            {% endif %}
```

### Maximize Solar Usage

```yaml
automation:
  - alias: "Notify When Solar is Wasted"
    trigger:
      - platform: numeric_state
        entity_id: sensor.net_power_flow
        below: -1000  # Exporting more than 1kW
        for:
          minutes: 10
    action:
      - service: notify.mobile_app
        data:
          title: "Excess Solar Production"
          message: >
            Exporting {{ states('sensor.net_power_flow') | abs }}W to grid.
            Consider running appliances now!
          data:
            actions:
              - action: START_LAUNDRY
                title: "Start Laundry"
              - action: START_DRYER
                title: "Start Dryer"
```

---

## 💡 Energy Budgets

### Track Budget Compliance

```yaml
input_number:
  monthly_energy_budget:
    name: Monthly Energy Budget
    initial: 900
    min: 0
    max: 2000
    step: 10
    unit_of_measurement: "kWh"
    
template:
  - sensor:
      - name: "Energy Budget Remaining"
        unique_id: sense_budget_remaining
        unit_of_measurement: "kWh"
        state: >
          {% set budget = states('input_number.monthly_energy_budget') | float %}
          {% set used = states('sensor.sense_monthly_usage') | float %}
          {{ (budget - used) | round(1) }}
          
      - name: "Days Until Budget Reset"
        unique_id: sense_days_until_reset
        unit_of_measurement: "days"
        state: >
          {% set today = now().day %}
          {% set days_in_month = (now().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1) %}
          {{ days_in_month.day - today }}
          
      - name: "Recommended Daily Usage"
        unique_id: sense_recommended_daily
        unit_of_measurement: "kWh"
        state: >
          {% set remaining = states('sensor.energy_budget_remaining') | float %}
          {% set days_left = states('sensor.days_until_budget_reset') | int %}
          {% if days_left > 0 %}
            {{ (remaining / days_left) | round(1) }}
          {% else %}
            0
          {% endif %}

automation:
  - alias: "Budget Warning - 80% Used"
    trigger:
      - platform: template
        value_template: >
          {% set budget = states('input_number.monthly_energy_budget') | float %}
          {% set used = states('sensor.sense_monthly_usage') | float %}
          {{ (used / budget) > 0.8 }}
    action:
      - service: notify.mobile_app
        data:
          title: "Energy Budget Warning"
          message: "80% of monthly energy budget used!"
```

---

## 📱 Dashboard Examples

### Energy Overview Card

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.sense_active_power
    name: Current Power
    min: 0
    max: 10000
    severity:
      green: 0
      yellow: 5000
      red: 8000
      
  - type: entities
    entities:
      - entity: sensor.energy_cost_per_hour
        name: Cost Per Hour
      - entity: sensor.net_daily_energy_cost
        name: Today's Cost
      - entity: sensor.projected_monthly_bill
        name: Projected Bill
        
  - type: history-graph
    entities:
      - entity: sensor.sense_active_power
        name: Power Usage
      - entity: sensor.sense_active_solar_power
        name: Solar Production
    hours_to_show: 24
```

### Solar Dashboard

```yaml
type: vertical-stack
cards:
  - type: gauge
    entity: sensor.solar_self_consumption
    name: Solar Self-Consumption
    min: 0
    max: 100
    
  - type: entities
    entities:
      - entity: sensor.net_power_flow
        name: Net Power
      - entity: sensor.daily_solar_savings
        name: Today's Savings
      - entity: sensor.sense_daily_production
        name: Today's Production
```

---

## 🎓 Pro Tips

1. **Use Statistics Platform**: Track min/max/mean over time
2. **Create Input Helpers**: Store rates, budgets, goals
3. **Leverage Recorder**: Exclude high-frequency sensors to save DB space
4. **Use Conditional Cards**: Show different info based on state
5. **Set Up Notifications**: Get alerts for anomalies and budgets
6. **Create Scenes**: Auto-respond to high usage events
7. **Use Grafana**: For advanced visualization and analytics

---

## 🚀 Coming Soon

Future versions will add built-in support for:
- Native cost tracking sensors
- ML-based anomaly detection
- Predictive bill estimation
- Per-device cost attribution
- Solar ROI calculator
- Energy efficiency scores

Want a feature? [Open an issue](https://github.com/JoshuaSeidel/hass-sense/issues)!

