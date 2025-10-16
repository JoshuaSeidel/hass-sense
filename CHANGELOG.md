# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

