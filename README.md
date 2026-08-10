# VOOL Modbus Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License](https://img.shields.io/github/license/Mactomik/vool_modbus_ha.svg)](LICENSE)

A Home Assistant custom integration for VOOL EV Chargers via Modbus TCP.

> **This is a fork** of [martinkenk/vool_modbus_ha](https://github.com/martinkenk/vool_modbus_ha), which only
> supports the individual VOOL charger. This fork adds support for the **VOOL LMC (Load Management
> Controller)**, a different product with its own Modbus register map. See
> [Changes in this fork](#changes-in-this-fork) below for details.

![VOOL Logo](images/logo.png)

## Features

- **Real-time monitoring**: Power, current, voltage (per phase), energy consumption
- **Status monitoring**: Charger state, requested phases, vehicle connection status
- **Full control**: Start/stop charging, set external current limits, configure allowed phases
- **LMC support (this fork, read-only)**: Per-phase mains current, voltage, and computed power

## Installation

### HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations → ⋮ (menu) → Custom repositories
3. Add this repository URL: `https://github.com/Mactomik/vool_modbus_ha`
4. Select category: **Integration**
5. Click **Add**
6. Search for "VOOL Modbus" in HACS and install it
7. Restart Home Assistant

### Manual Installation

1. Clone or download this repository
2. Copy the `custom_components/vool_modbus` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "VOOL Modbus"
4. Select the **Device Type**: Charger or LMC
5. Enter the connection details:
   - **IP Address**: The IP address of your VOOL device
   - **Port**: Modbus TCP port (default: 502)
   - **Slave ID**: Modbus slave ID (default: 1, ignored by the LMC — it's addressed by IP)
   - **Name**: A friendly name for the device
6. Click **Submit**

### Multiple Devices

You can add multiple VOOL devices by repeating the configuration process. Each device will appear as a separate integration entry with its own entities.

### Options (scan interval, port, slave ID)

After adding a device, click **Configure** on its entry under Settings → Devices & Services to change the poll rate (5-3600 seconds, default 5s) or connection details without removing and re-adding it.

## Entities

### Sensors
| Entity | Description | Unit |
|--------|-------------|------|
| Charger State | Current state of the charger | - |
| Active Power | Current charging power | kW |
| L1/L2/L3 Power | Per-phase power | kW |
| Current L1/L2/L3 | Per-phase current | A |
| Voltage L1/L2/L3 | Per-phase voltage | V |
| Energy Imported | Total energy delivered | kWh |
| Requested Phases | Phases requested by vehicle | - |
| External Current Limit | Configured current limit | A |

### Binary Sensors
| Entity | Description |
|--------|-------------|
| Vehicle Connected | Whether a vehicle is plugged in |
| Charging | Whether actively charging |
| Error | Whether an error condition exists |

### Controls
| Entity | Type | Description |
|--------|------|-------------|
| Charging Enabled | Switch | Start/stop charging |
| External Current Limit | Number | Set external current limit (6-32A) |
| Allowed Phases | Select | Configure allowed phases (1/2/3) |
| Start Charging | Button | Start a charging session |
| Stop Charging | Button | Stop a charging session |

Charger entities above do not appear for LMC devices — the LMC exposes a different register map (see below).

### LMC Sensors (this fork, read-only)
| Entity | Description | Unit |
|--------|-------------|------|
| Mains Current L1/L2/L3 | Per-phase mains current | A |
| Mains Voltage L1/L2/L3 | Per-phase mains voltage | V |
| Mains Power L1/L2/L3 | Per-phase power, computed as V × I (unity power factor assumed) | W |
| Mains Power Total | Sum of the three phases | W |

The LMC's Modbus interface has no power or energy register — only current and voltage per phase — so power
is computed client-side by this integration rather than read from the device. There is currently no write
support for the LMC (current limit, load management mode, commands); see
[Changes in this fork](#changes-in-this-fork) for why.

## Dashboard

A sample dashboard configuration is included in the `dashboard/` folder. See [Dashboard Setup](dashboard/README.md) for instructions.

## Using LMC Power in the Energy Dashboard

The Home Assistant Energy dashboard needs a cumulative kWh sensor, not an instantaneous power reading, so
`Mains Power Total` (W) can't be added to it directly. Derive an energy sensor from it with a built-in helper:

1. **Settings** → **Devices & Services** → **Helpers** → **+ Add Helper**
2. Choose **Integration - Riemann sum integral**
3. **Input sensor**: `Mains Power Total`
4. **Metric prefix**: `k` (kilo), so the result is in kWh
5. **Integration method**: `Left Riemann sum`
6. Save, then add the resulting sensor to the Energy dashboard as an individual device (or as a grid source, depending on what it should represent for you)

## Troubleshooting

### Cannot connect to device
- Verify the IP address is correct
- Ensure Modbus TCP is enabled on your VOOL device
- Check that port 502 is not blocked by a firewall
- Verify the device is on the same network as Home Assistant

### Values not updating
- Check the network connection to the device
- Try reloading the integration
- Check the Home Assistant logs for errors

### Error: "Failed to read from Modbus device"
- Verify the Modbus slave ID is correct (default: 1; ignored by the LMC)
- Ensure no other application is using the Modbus connection

### Error: "Failed to read from charger/lmc at address ..."
- Double check you picked the right **Device Type** during setup — Charger and LMC use completely different
  register maps, and reading a charger address against an LMC (or vice versa) returns a Modbus exception, not
  a network error.
- For the LMC specifically, confirm Modbus TCP is actually enabled on the device (parameter 750 in its local
  web interface — it's disabled by default and can only be turned on from there, not over Modbus itself).

### HACS download fails / "Could not download"
- If you're on a fork with no published GitHub Release, make sure `hacs.json` does **not** set
  `"zip_release": true` — that tells HACS to fetch a prebuilt ZIP asset from a release, which fails with no
  matching release, even for the unmodified upstream commit.

## Changes in this fork

Relative to [martinkenk/vool_modbus_ha](https://github.com/martinkenk/vool_modbus_ha):

- **Added VOOL LMC (Load Management Controller) support**, read-only: mains current/voltage per phase and
  computed power (`const.py`, `coordinator.py`, `sensor.py`). The LMC is a different product with its own
  register map (float32 pairs addressed as `register = param# * 2`, per VOOL's official "LMC — Modbus TCP
  Register Map" doc, rev 1.0, July 2026) — it does **not** share register addresses with the single charger,
  despite a comment in the original `config_flow.py` claiming otherwise. Reading register 100 (charger state)
  against an LMC falls outside every documented region and returns a Modbus exception, which is what sent us
  down this path in the first place.
- **Wired up the device-type selector** in `config_flow.py` — the strings for a "VOOL Device Type" step
  already existed in `strings.json`/`translations/en.json`, but `async_step_user` never actually showed the
  form and hardcoded the charger type.
- Charger-only entity platforms (`number`, `binary_sensor`, `button`, `select`, `switch`) now skip entity
  creation for LMC devices instead of creating dead entities against registers that don't exist on that
  product.
- LMC write support (current limit, load management mode, factory reset/reboot commands) is intentionally
  **not** implemented — the LMC spec requires enabling a separate "write enabled" parameter on the device and
  warns that any host with write access can trigger a reboot or factory reset, so it was left out of this
  read-only-focused pass.
- **Made the polling scan interval configurable** via the options flow (5-3600s, was hardcoded to 5s).
- **Fixed `hacs.json`** (`zip_release: true` pointed HACS at a GitHub Release asset that was never published,
  so downloads failed even for the unmodified upstream commit) and corrected repo URLs throughout that
  referenced a nonexistent `martinkenk/vool-modbus-ha` (hyphenated) instead of the actual
  `martinkenk/vool_modbus_ha`.

## Contributing

This fork is maintained for personal use and isn't actively seeking contributions, but the original project's
[Contributing Guidelines](CONTRIBUTING.md) still apply if you'd like to send a PR.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with or endorsed by VOOL. Use at your own risk.

## Support

This is a personal fork; for the original charger-only integration, see
[martinkenk/vool_modbus_ha](https://github.com/martinkenk/vool_modbus_ha). For issues specific to the LMC
support added here:

- [Issue Tracker](https://github.com/Mactomik/vool_modbus_ha/issues)
