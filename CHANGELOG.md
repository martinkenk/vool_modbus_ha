# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-11-05

### Added
- Read-only VOOL LMC support for software v6.4.0 and later.
- LMC mains current, voltage, and computed apparent power sensors.
- Device-type selection and configurable polling interval (5-3600 seconds).

### Fixed
- Reload options through Home Assistant's config-entry lifecycle.
- Apply port and slave ID options when reconnecting.
- Report computed LMC apparent power in VA, not active power in W.
- Restore upstream documentation and support links.

## [1.0.0] - 2024-12-25

### Added
- Initial release
- Support for VOOL EV Charger via Modbus TCP
- Support for VOOL LMC (Load Management Controller)
- Full UI configuration through Home Assistant
- Sensors for power, current, voltage, energy, temperature
- Binary sensors for connection and charging status
- Controls: switches, buttons, number inputs, selects
- HACS compatibility
- Sample dashboard configuration
