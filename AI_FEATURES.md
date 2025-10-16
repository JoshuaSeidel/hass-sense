# AI-Powered Energy Intelligence

## Overview

The Sense integration now includes **9 AI-powered features** that provide intelligent insights, predictions, and recommendations for your energy usage.

## 🎯 Features

### 1. Daily Insights
**Sensor:** `sensor.sense_ai_daily_insights`
- **What:** AI-generated summary of yesterday's energy usage
- **When:** Updates once per day (morning)
- **Includes:**
  - Usage summary with specific numbers
  - Top 3 actionable recommendations
  - Notable patterns or concerns
  - Comparison to previous days

**Example:**
> "Yesterday you used 42 kWh ($5.04), 15% higher than usual. Your AC ran 18 hours due to heat - consider pre-cooling during solar production hours (11am-2pm) to save $1.50/day. Peak usage was 6:30 PM (8,200W) when cooking, AC, and EV charging overlapped. Recommendation: Delay EV charging to 9 PM to avoid peak rates."

---

### 2. Anomaly Explanation
**Binary Sensor:** `binary_sensor.power_usage_anomaly`
**Sensor:** `sensor.sense_ai_anomaly_explanation`
- **What:** AI explains unusual power spikes when detected
- **When:** On-demand when anomaly occurs
- **Includes:**
  - Most likely cause(s)
  - Which devices to check
  - Severity assessment
  - Recommended actions

**Example:**
> "Your power spiked to 8,500W at 3:42 PM (3.2x average). This coincides with HVAC (3,200W) + water heater (4,500W) + unknown device (2,000W). Likely causes: 1) Electric oven in use, 2) EV charging started early, 3) Pool heater malfunction. Check these devices first. This is unusual but not necessarily concerning if intentional."

---

### 3. Solar Coach
**Sensor:** `sensor.sense_ai_solar_coach`
- **What:** Real-time advice on when to run appliances for max solar usage
- **When:** Updates hourly (or real-time on high budget)
- **Includes:**
  - Current solar status
  - Best action right now
  - Timing recommendations

**Example:**
> "☀️ Perfect time to run dishwasher! Solar producing 3.2kW, home using 1.8kW. You have 1.4kW excess going to grid. Also good time for: laundry, pool pump, EV charging. Solar will peak for next 2 hours."

---

### 4. Bill Forecast
**Sensor:** `sensor.sense_ai_bill_forecast`
- **What:** AI predicts monthly bill with explanation
- **When:** Updates weekly (or daily on high budget)
- **Includes:**
  - Projected total cost
  - Comparison to last month
  - Factors driving the cost
  - Actions to reduce bill
  - Savings estimates

**Example:**
> "Projected bill: $432 (high confidence). This is $45 higher than last month due to: 1) AC usage up 50% from heatwave (+$28), 2) EV charging during peak hours 8x (+$12), 3) Pool pump schedule changed to daytime (+$5). Recommendations: 1) Move EV charging to after 9pm (save $12), 2) Reset pool pump to midnight-6am (save $8), 3) Raise AC temp by 2°F (save $15). Total potential savings: $35/month."

---

### 5. Device Identification
**Service:** `sense.identify_device`
- **What:** AI helps identify "Unknown Device" detections
- **When:** On-demand service call
- **Includes:**
  - Most likely device type
  - Confidence level
  - Reasoning
  - How to confirm

**Example:**
> "Unknown Device #3 is likely your **dishwasher** (85% confidence). Reasoning: 1) Power draw matches typical dishwasher (1200-1500W), 2) Runs for 90-120 minutes, 3) Always activates after dinner (7-9 PM), 4) Has distinct heating cycles. Alternative: Could be clothes washer if you do evening laundry. To confirm: Run dishwasher alone and watch for device activation."

---

### 6. Weekly Story
**Sensor:** `sensor.sense_ai_weekly_story`
- **What:** Engaging narrative about your week's energy usage
- **When:** Updates weekly (Sunday morning)
- **Includes:**
  - Week summary
  - Day-by-day highlights
  - Notable achievements
  - Comparison to last week
  - Recommendations

**Example:**
> "What a week! Monday started normal at 38 kWh, but Tuesday's heatwave pushed you to 52 kWh - your highest day this month. You adapted brilliantly on Wednesday, pre-cooling in the morning and saving $4. Thursday's mystery device (2,200W for 3 hours at 2 AM) is concerning - possibly a malfunctioning appliance. Your EV charging improved: 80% off-peak vs 60% last week. Weekend usage was perfect - great solar self-consumption on Saturday (92%!). Overall: $127 this week, on track for $520 monthly. Next week: Watch that mystery device and keep up the off-peak charging!"

---

### 7. Optimization Suggestions
**Sensor:** `sensor.sense_ai_optimization_suggestions`
- **What:** AI-generated automation suggestions with YAML code
- **When:** Updates weekly
- **Includes:**
  - Top 3 opportunities
  - Savings estimates
  - Working HA automation code
  - Implementation instructions

**Example:**
```yaml
Suggestion 1: Off-Peak EV Charging
Savings: $25/month
Reason: You charge during peak hours 60% of the time, costing $0.20/kWh vs $0.08 off-peak.

automation:
  - alias: "Smart EV Charging"
    trigger:
      - platform: time
        at: "21:00:00"
    condition:
      - condition: numeric_state
        entity_id: sensor.ev_battery
        below: 80
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

---

### 8. Conversational Assistant
**Service:** `sense.ask_ai`
- **What:** Ask questions about your energy usage in natural language
- **When:** On-demand service call
- **Includes:**
  - Direct answer with data
  - Context and explanation
  - Actionable recommendations

**Example Questions:**
- "Why is my bill higher this month?"
- "When should I run my dishwasher?"
- "What's using the most power right now?"
- "How can I save $50/month?"
- "Is my solar system working well?"

**Example Response:**
> Q: "Why is my bill higher this month?"
> 
> A: "Your bill is $45 higher primarily because of three factors: 1) **AC usage** increased 50% due to the heatwave (18 hours/day vs 12 average), costing an extra $28. 2) **EV charging** happened during peak hours 8 times instead of off-peak, adding $12. 3) **Pool pump** schedule changed to run during the day instead of overnight, adding $5. The good news: these are all fixable. Move EV charging to after 9pm and pool pump to midnight-6am to save $20/month immediately."

---

### 9. Comparative Analysis
**Sensor:** `sensor.sense_ai_comparative_analysis`
- **What:** Compare your usage to similar homes
- **When:** Updates monthly
- **Includes:**
  - Percentile ranking
  - What you're doing well
  - Areas for improvement
  - Specific recommendations

**Example:**
> "You're in the **85th percentile** - better than 85% of similar 3-bedroom homes with solar in your area! Your solar self-consumption (87%) is excellent - top 15% of solar homes. You're also doing great with off-peak usage shifting. However, your peak hour usage (4-9 PM) is higher than average, suggesting room for improvement with time-shifting appliances. Your HVAC efficiency is average - consider a smart thermostat or AC maintenance. Overall: You're a high performer with a few opportunities to reach the top 10%."

---

## 🔧 Configuration

### Token Budget Levels

#### Low Budget (~$1-2/month)
- Daily insights: ✅ Daily
- Anomaly explanation: ✅ On-demand
- Solar coach: ❌
- Bill forecast: ✅ Weekly
- Device ID: ❌
- Weekly story: ✅ Weekly
- Conversational: ❌
- Optimization: ✅ Weekly
- Comparative: ❌

#### Medium Budget (~$3-5/month) **[Default]**
- Daily insights: ✅ Daily
- Anomaly explanation: ✅ On-demand
- Solar coach: ✅ Hourly
- Bill forecast: ✅ Weekly
- Device ID: ✅ On-demand
- Weekly story: ✅ Weekly
- Conversational: ✅ On-demand
- Optimization: ✅ Weekly
- Comparative: ❌

#### High Budget (~$8-12/month)
- Daily insights: ✅ Daily (detailed)
- Anomaly explanation: ✅ On-demand
- Solar coach: ✅ Real-time (5min)
- Bill forecast: ✅ Daily
- Device ID: ✅ On-demand
- Weekly story: ✅ Weekly (detailed)
- Conversational: ✅ On-demand
- Optimization: ✅ Daily
- Comparative: ✅ Monthly

### AI Provider Options

1. **Home Assistant Conversation** (Recommended)
   - Uses your configured HA conversation agent
   - Supports OpenAI, Anthropic, local LLMs, etc.
   - Most flexible
   - Setup: Configure conversation integration first

2. **OpenAI Direct**
   - Direct OpenAI API calls
   - Requires API key
   - Good for GPT-4 Turbo

3. **Anthropic Direct**
   - Direct Anthropic API calls
   - Requires API key
   - Good for Claude 3 Sonnet/Opus

4. **Built-in (Fallback)**
   - Rule-based responses
   - No API costs
   - Limited intelligence
   - Good for testing

### Privacy & Data

**Data Sent to AI:**
- ✅ Energy usage statistics (kWh, watts)
- ✅ Peak power times and values
- ✅ Device names and states
- ✅ Solar production data
- ✅ Cost calculations (no account numbers)
- ✅ Time-of-day patterns
- ✅ Historical trends (aggregated)

**Data NOT Sent:**
- ❌ Your name or address
- ❌ Account numbers or payment info
- ❌ Specific device locations
- ❌ Video or images
- ❌ Personal schedules
- ❌ Other smart home data

**Retention:**
- Responses cached locally in HA
- Not stored by AI provider (per their policies)
- Can be disabled anytime

---

## 📱 Usage Examples

### Automation: Daily Insights Notification
```yaml
automation:
  - alias: "Morning Energy Insights"
    trigger:
      - platform: state
        entity_id: sensor.sense_ai_daily_insights
    action:
      - service: notify.mobile_app
        data:
          title: "☀️ Your Energy Report"
          message: "{{ states('sensor.sense_ai_daily_insights') }}"
```

### Automation: Anomaly Alert
```yaml
automation:
  - alias: "Power Anomaly Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.power_usage_anomaly
        to: 'on'
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Unusual Power Usage"
          message: "{{ states('sensor.sense_ai_anomaly_explanation') }}"
          data:
            priority: high
```

### Automation: Solar Coach Notification
```yaml
automation:
  - alias: "Solar Opportunity Alert"
    trigger:
      - platform: state
        entity_id: sensor.sense_ai_solar_coach
        attribute: status
        to: 'optimal'
    action:
      - service: notify.mobile_app
        data:
          message: "{{ states('sensor.sense_ai_solar_coach') }}"
```

### Script: Ask AI Question
```yaml
script:
  ask_energy_question:
    sequence:
      - service: sense.ask_ai
        data:
          question: "{{ question }}"
        response_variable: answer
      - service: notify.mobile_app
        data:
          message: "{{ answer.answer }}"
```

### Dashboard Card
```yaml
type: markdown
content: |
  ## 🤖 AI Energy Insights
  
  ### Today's Summary
  {{ states('sensor.sense_ai_daily_insights') }}
  
  ### Solar Coach
  {{ states('sensor.sense_ai_solar_coach') }}
  
  ### Bill Forecast
  {{ states('sensor.sense_ai_bill_forecast') }}
```

---

## 🎓 Tips

1. **Start with Medium budget** - Good balance of features and cost
2. **Enable daily insights first** - Most valuable feature
3. **Use anomaly detection** - Catch issues early
4. **Ask questions** - The conversational assistant is powerful
5. **Review weekly stories** - Great for understanding patterns
6. **Implement suggested automations** - AI generates working code!
7. **Check comparative analysis** - See how you stack up

---

## 🔮 Coming Soon

- **Learning mode**: AI learns your preferences over time
- **Predictive maintenance**: Detect failing appliances early
- **Energy challenges**: Gamified savings goals
- **Voice integration**: "Hey Google, ask Sense about my energy"
- **Multi-home comparison**: Compare your properties
- **Carbon footprint tracking**: Environmental impact insights

---

## 💰 Cost Transparency

All costs are estimates based on typical usage:

| Budget | Monthly Cost | Features | Best For |
|--------|-------------|----------|----------|
| Low | $1-2 | Essential insights | Budget-conscious users |
| Medium | $3-5 | Most features | Most users (recommended) |
| High | $8-12 | All features, real-time | Power users, solar owners |

**Note:** Actual costs depend on:
- Your AI provider (OpenAI, Anthropic, local LLM)
- How often you use on-demand features
- Token prices (subject to change)

**Free option:** Use built-in fallback (no AI provider needed)

---

## 🚀 Getting Started

1. **Enable AI features** in integration options
2. **Choose token budget** (start with Medium)
3. **Select AI provider** (HA Conversation recommended)
4. **Review privacy info** and confirm
5. **Wait for first insights** (next morning)
6. **Set up notifications** for daily insights
7. **Explore features** and ask questions!

---

**This is the future of energy monitoring!** 🎯

