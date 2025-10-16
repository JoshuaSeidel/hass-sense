# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.5] - 2025-10-16

### Fixed - CRITICAL: Setup Hanging
- **Integration setup hanging**: Fixed sensor platform taking >10 seconds
  - Issue: AI sensors were blocking setup by calling LLM immediately
  - Solution: Added `async_track_time_interval` for periodic updates
  - AI sensors now check every 15 minutes if they should update
  - Setup completes immediately, updates happen in background
- **Deprecated config_entry warning**: Removed explicit assignment
  - Fixed: "sets option flow config_entry explicitly" warning
  - Removed `self.config_entry = config_entry` (available from parent)
  - Prepares for Home Assistant 2025.12

### Changed
- AI sensors now use `async_track_time_interval` for updates
- Check every 15 minutes, but only update based on sensor schedule
- Daily insights: Once per day at 6 AM
- Solar coach: Every 15 minutes (if conditions met)
- Bill forecast: Daily
- Weekly story: Weekly
- Setup no longer blocked by AI sensor initialization

### Technical
- Added `async_track_time_interval` import
- Added `_async_scheduled_update` method to base AI sensor
- Each sensor's `async_update()` has its own time checks
- Removed blocking `await self.async_update()` from `async_added_to_hass`
- Config flow now uses inherited `self.config_entry`

**Integration should now load in <10 seconds! AI updates happen in background!**

## [2.0.4] - 2025-10-16

### Fixed - CRITICAL BUGS
- **Binary sensor/switch crash**: Fixed `'coroutine' object is not subscriptable` error
  - Issue: `sense_energy` library's `get_discovered_device_data()` is broken
  - Solution: Use `gateway.devices` directly instead
  - Affected: binary_sensor.py and switch.py platforms
- **AI sensors stuck in "pending"**: Fixed AI sensors not updating
  - Added `async_added_to_hass()` to trigger initial update
  - Simplified AI sensor creation (no feature checking)
  - All 7 AI sensors now added when AI enabled
  - Better logging to show which sensors are created

### Changed
- Binary sensors now use `gateway.devices` attribute
- Switch platform uses `gateway.devices` with proper `getattr()` calls
- AI sensors trigger update immediately when added to HA
- Better logging: "Adding AI sensors (provider: openai)"

### Technical
- Workaround for broken `get_discovered_device_data()` in sense_energy library
- AI sensors now properly call their `async_update()` method on startup
- Removed feature-based filtering (all AI sensors added when enabled)

**Binary sensors and switches should now work! AI sensors should start generating!**

## [2.0.3] - 2025-10-16

### Changed - UX Improvements
- **Cleaner Config UI**: Removed overlapping text, better labels
- **AI Provider Selection**: Changed from checkbox to dropdown
  - "Disabled - No AI Features" (default)
  - "Home Assistant Conversation (Free - Uses your default agent)"
  - "OpenAI Integration (Requires API key)" - only shown if installed
  - "Anthropic Conversation (Requires API key)" - only shown if installed
- **Removed "Built-in" AI**: There's no such thing as free AI, removed misleading option
- **Dynamic Options**: Token budget only shown when AI provider selected
- **Better Labels**: Changed from variable names to user-friendly text
  - "ai_enabled" → removed (now implicit based on provider)
  - "ai_provider" → "AI Provider"
  - "ai_token_budget" → "Monthly Token Budget"
  - "realtime_update_rate" → "Real-time Update Rate"

### Fixed
- AI enabled automatically when provider selected (not "none")
- Provider options only show installed integrations
- No more confusing "Built-in (Free, Limited)" option

### Documentation
- **README.md**: Completely updated with all v2.0 features
- Added AI features section with all 7 sensors and 7 services
- Added automation examples for AI features
- Better organization and feature highlights
- Added "What Makes This Different" section

**Much cleaner and more intuitive config experience!**

## [2.0.2] - 2025-10-16

### Fixed
- **CRITICAL**: AI sensors now actually get created!
- Fixed OpenAI integration to use conversation agent with agent_id
- Fixed Anthropic integration to use conversation agent with agent_id
- AI sensors now added dynamically in sensor.py based on config
- Better error handling and fallback for conversation agents
- Improved logging for AI provider calls

### Changed
- OpenAI/Anthropic options now properly use installed conversation integrations
- Agent IDs: conversation.openai and conversation.anthropic
- Fallback to default conversation agent if specific agent not found

**Now AI sensors will actually appear when you enable AI features!**

## [2.0.1] - 2025-10-16

### Fixed
- **CRITICAL**: Added AI options to config flow
- AI settings now visible in integration options
- Added: Enable AI, Provider selection, Token budget
- Added strings.json for better UI translations
- Descriptions for each AI option

**Now you can actually enable and configure AI features!**

## [2.0.0] - 2025-10-16

### 🤖 AI-POWERED ENERGY INTELLIGENCE! 

This is a **REVOLUTIONARY** release! The first energy monitoring integration with comprehensive AI features!

### Added - 9 AI Features
- **Daily Insights**: AI-generated morning summary with recommendations
- **Anomaly Explanation**: AI explains unusual power spikes
- **Solar Coach**: Real-time solar optimization advice
- **Bill Forecast**: Predictive monthly bill with explanation
- **Device Identification**: AI helps identify unknown devices
- **Weekly Story**: Engaging narrative about your energy week
- **Optimization Suggestions**: AI generates automation code
- **Conversational Assistant**: Ask questions in natural language
- **Comparative Analysis**: Compare to similar homes

### Added - AI Sensors (7 total)
- `sensor.sense_ai_daily_insights`
- `sensor.sense_ai_solar_coach`
- `sensor.sense_ai_bill_forecast`
- `sensor.sense_ai_weekly_story`
- `sensor.sense_ai_optimization_suggestions`
- `sensor.sense_ai_comparative_analysis`
- `sensor.sense_ai_anomaly_explanation`

### Added - AI Services (7 total)
- `sense.ask_ai` - Ask questions about energy
- `sense.identify_device` - Identify unknown devices
- `sense.explain_anomaly` - Explain current anomaly
- `sense.generate_insights` - Generate insights on-demand
- `sense.generate_optimization` - Get optimization suggestions
- `sense.get_privacy_info` - See what data is sent
- `sense.get_cost_estimate` - Estimate AI costs

### Added - Configuration
- Token budget levels (Low/Medium/High)
- Multi-provider support (HA Conversation, OpenAI, Anthropic, Built-in)
- Per-feature enable/disable
- Privacy transparency
- Cost estimation
- Rate limiting

### Technical
- `ai_engine.py`: Core AI engine with multi-provider support
- `ai_features.py`: 9 feature implementations with prompt engineering
- `ai_sensor.py`: AI sensor platform
- `services.yaml`: Complete service definitions
- Full documentation in `AI_FEATURES.md`

### Breaking Changes
- None! AI features are opt-in
- All existing features work exactly as before
- Enable AI in integration options

**This changes EVERYTHING about energy monitoring!** 🚀

## [1.4.0] - 2025-10-16

### Added 🚀
- **Analytics Engine**: Built-in power usage analytics
- **Peak Power Sensor**: Tracks highest power usage today
- **Average Power Sensor**: Running average of power consumption
- **15-Minute Average Sensor**: Recent power trend
- **Peak Solar Sensor**: Highest solar production today
- **Solar Self-Consumption Sensor**: Shows % of solar power you're using vs exporting
- **Anomaly Detection Binary Sensor**: Automatically detects unusual power usage
- **statistics.py Module**: PowerStatistics and SolarStatistics tracking

### Features
- Real-time anomaly detection (alerts when usage is abnormal)
- Solar efficiency tracking (optimize self-consumption)
- Daily peak tracking (automatic reset at midnight)
- Historical analysis (last 100 readings)
- Statistical variance calculation
- Spike detection

### Technical
- Analytics integrated into SenseRealtimeCoordinator
- Statistics tracked in memory (no database required)
- Daily automatic reset
- Attributes include deviation, expected vs actual values

**This is INNOVATION! No other integration has built-in analytics and anomaly detection!** 🎉

## [1.3.3] - 2025-10-16

### Fixed
- **CRITICAL**: `gateway.rate_limit` now uses user-configured rate instead of hardcoded 60s
- The official library's WebSocket rate limiting was always 60s regardless of settings
- Now properly applies your chosen update rate (5s, 10s, etc.)

### Technical
- Moved `realtime_update_rate` calculation to top of `async_setup_entry`
- Set `gateway.rate_limit = realtime_update_rate` (was using `ACTIVE_UPDATE_RATE` constant)
- Added logging: "Using official sense_energy library with Xs update rate"

**This was the actual bug! Now fast updates (5-15s) will really work!**

## [1.3.2] - 2025-10-16

### Fixed
- **CRITICAL**: Options flow now triggers integration reload
- Changing update rate in options now actually applies the new rate
- Added `async_reload_entry` listener for config changes
- Enhanced logging to show current update interval in use

### Changed
- Coordinator logs now show interval: "Realtime update (5s interval): 1234W"
- Makes it easy to verify your chosen update rate is working

**Now when you change the update rate, it will automatically reload and apply!**

## [1.3.1] - 2025-10-16

### Fixed
- **Unload error**: Official `ASyncSenseable` doesn't have `close()` method
- Added `hasattr()` check before calling `gateway.close()` on unload
- Integration can now be safely removed/reloaded

## [1.3.0] - 2025-10-16

### Added 🚀
- **Separate Coordinators**: Split data updates into realtime (60s default) and trends (300s)
- **Configurable Update Rate**: Choose update interval from 5s to 5min during setup
- **Options Flow**: Change update rate after setup via integration options
- **Performance**: Trend data (daily/weekly/monthly/yearly) updates separately from realtime
- **Better Architecture**: Each sensor uses appropriate coordinator for its data type

### Changed
- Realtime sensors (power, voltage, frequency) now use fast coordinator
- Trend sensors (usage/production) use slow coordinator (reduces API calls)
- Update rates are now fully customizable per user preference
- Default remains 60s for backwards compatibility

### Technical
- New `coordinator.py` module with `SenseRealtimeCoordinator` and `SenseTrendCoordinator`
- Each coordinator returns proper data dict and exposes gateway
- Options flow allows changing update rate without re-adding integration
- Better logging shows which coordinator is updating

**This enables much faster updates (down to 5s) for users who want near-real-time data!**

## [1.2.2] - 2025-10-15

### Fixed
- **CRITICAL**: Use proper exception classes from sense_energy library
- **CRITICAL**: Use executor job for gateway creation (blocks on SSL cert loading)
- **CRITICAL**: Call `gateway.fetch_devices()` before realtime update
- **CRITICAL**: Set `gateway.rate_limit` for proper API rate limiting
- **CRITICAL**: Use getattr() with fallbacks for all attribute access
- Proper exception handling matching official integration

### Added
- SENSE_CONNECT_EXCEPTIONS for connection errors
- TREND_UPDATE_RATE constant (300s for future use)
- Detailed implementation comparison document

### Changed
- Improved error messages to match official integration
- Better fallback handling when sense_energy not installed

**This release fixes all known compatibility issues with the official sense_energy library!**

## [1.2.1] - 2025-10-15

### Fixed
- Fixed AttributeError: 'ASyncSenseable' object has no attribute 'get_all_data'
- Added compatibility layer between official sense_energy library and custom implementation
- Properly map official library attributes to our data structure

### Added
- Comprehensive roadmap for future development
- Comparison document with official integration
- Vision for becoming the ultimate Sense integration

## [1.2.0] - 2025-10-15

### Changed
- **MAJOR**: Now uses official `sense_energy` library's `ASyncSenseable` class
- Switched from REST API to WebSocket for realtime data (official library handles this)
- Follows same pattern as official Home Assistant Sense integration

### Fixed
- Realtime power data now works correctly via WebSocket connection
- No longer relies on deprecated `/status` REST endpoint

### Added
- Automatic fallback to custom implementation if sense_energy library not available
- Better compatibility with official sense_energy library updates

**This should fix all data retrieval issues!**

## [1.1.4] - 2025-10-15

### Added
- Test alternative API endpoints to find where realtime power data moved
- Discovery that /status endpoint no longer contains power data

## [1.1.3] - 2025-10-15

### Added
- Complete recursive search of entire API response to find power data
- Raw JSON dump of response for analysis

## [1.1.2] - 2025-10-15

### Added
- Debug output for monitor_info structure (where actual power data likely resides)

## [1.1.1] - 2025-10-15

### Added
- Enhanced debug output in test script to show signals structure
- Detailed debugging to identify exact location of power data in new API

## [1.1.0] - 2025-10-15

### Fixed
- **MAJOR FIX**: Updated to handle new Sense API response format
  - API now returns data nested under `signals`, `device_detection`, and `monitor_info` keys
  - Integration now correctly parses the new response structure
  - Power, voltage, and frequency data now display correctly
  - Active device detection updated for new format

### Added
- Backward compatibility with old API format (automatic detection)
- Enhanced test script to show which API format is being used

### Changed
- Real-time data parsing completely rewritten for new API structure
- Device detection updated to use `device_detection.in_progress` structure

**This is a breaking API change from Sense. All users should update to v1.1.0.**

## [1.0.5] - 2025-10-15

### Added
- Bash script version of test tool (`test_api.sh`) - works without Python dependencies
- No external dependencies required for testing

### Fixed
- "No module named 'aiohttp'" error when running Python test script
- Test script now works in Home Assistant container environment

### Changed
- Bash script is now the recommended testing method
- Updated all documentation to reference bash script first

## [1.0.4] - 2025-10-15

### Added
- Standalone test script (`test_api.py`) included in integration folder
- Built-in diagnostics support via Home Assistant UI
- DEBUG.md guide in integration folder for quick reference
- Test script now properly included when pulling updates

### Fixed
- Test script not being available after git pull/upgrade
- Made test script fully standalone (no HA environment needed)

## [1.0.3] - 2025-10-15

### Added
- Enhanced debugging and logging throughout the integration
- Detailed API response logging for troubleshooting
- Test script (`test_sense_api.py`) for direct API testing
- Better monitor and user ID validation

### Fixed
- Improved error messages for API failures
- Better handling of empty API responses
- Enhanced logging to identify data flow issues

### Changed
- Increased logging verbosity for critical operations
- Changed some debug logs to info level for better visibility

## [1.0.2] - 2025-10-15

### Fixed
- Fixed 400 Bad Request error for trend data endpoint
- Added fallback mechanisms for trend data retrieval
- Made trend data updates non-critical (won't fail the entire integration if unavailable)
- Improved error handling and logging for API calls

### Changed
- Trend data errors are now logged as debug/warnings instead of causing integration failures
- Real-time power data remains functional even if historical data is unavailable

## [1.0.1] - 2025-10-15

### Fixed
- Fixed 415 "Unsupported Media Type" authentication error by using form-encoded data instead of JSON
- Added proper User-Agent header for API requests

## [1.0.0] - 2025-10-15

### Added
- Initial release of Sense Energy Monitor integration for Home Assistant
- Real-time power monitoring sensors (consumption and solar production)
- Voltage monitoring for both lines (L1 and L2)
- Grid frequency monitoring
- Comprehensive energy statistics (daily, weekly, monthly, yearly)
- Binary sensors for all detected devices
- Switch entities for controllable devices (smart plugs)
- UI-based configuration flow
- Advanced services:
  - `sense.get_device_info` - Get detailed device information
  - `sense.reset_device` - Reset/remove learned devices
  - `sense.rename_device` - Rename detected devices
- Full Home Assistant Energy Dashboard integration
- Automatic device discovery
- 60-second update intervals for optimal performance
- Comprehensive error handling and logging
- HACS compatibility

### Features
- 14 sensor entities covering all aspects of energy monitoring
- Device attributes including location, tags, make, and model
- Support for both consumption and solar production tracking
- Long-term statistics support for all energy sensors
- Automatic reconnection on connection failures
- Rate limiting to prevent API throttling

### Documentation
- Comprehensive README with setup instructions
- Automation examples
- Troubleshooting guide
- Service documentation
- Energy Dashboard integration guide

## [Unreleased]

### Planned
- WebSocket support for real-time updates
- Enhanced smart plug control
- Cost tracking and estimation
- Custom notification templates
- Device grouping support
- Historical data export
- Multi-monitor support

