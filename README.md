# VOOL Modbus Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/martinkenk/vool_modbus_ha.svg)](https://github.com/martinkenk/vool_modbus_ha/releases)
[![License](https://img.shields.io/github/license/martinkenk/vool_modbus_ha.svg)](LICENSE)

A Home Assistant custom integration for VOOL EV Chargers and the VOOL LMC (Load Management Controller)
via Modbus TCP. LMC support requires software v6.4.0 or later and is read-only.

## Features

- **Real-time monitoring**: Power, current, voltage (per phase), energy consumption
- **Status monitoring**: Charger state, requested phases, vehicle connection status
- **Full control**: Start/stop charging, set external current limits, configure allowed phases
- **LMC support (read-only)**: Per-phase mains current, voltage, and computed apparent power

## Installation

### HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations → ⋮ (menu) → Custom repositories
3. Add this repository URL: `https://github.com/martinkenk/vool_modbus_ha`
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

### LMC Sensors (read-only)
| Entity | Description | Unit |
|--------|-------------|------|
| Mains Current L1/L2/L3 | Per-phase mains current | A |
| Mains Voltage L1/L2/L3 | Per-phase mains voltage | V |
| Mains Apparent Power L1/L2/L3 | Per-phase apparent power, computed as V × I | VA |
| Mains Apparent Power Total | Sum of the three phases' apparent power | VA |

The LMC's Modbus interface exposes no active power, power factor, or energy register. Apparent power
is computed client-side rather than read from the device. LMC writes (current limit, load management mode,
and commands) are not implemented. Keep Modbus write access disabled; it is not needed by this integration.

## Dashboard

A sample dashboard configuration is included in the `dashboard/` folder. See [Dashboard Setup](dashboard/README.md) for instructions.

## LMC Measurements and the Energy Dashboard

The LMC sensors report apparent power in VA, not active power in W. Integrating apparent power over time
does not yield active energy in kWh, so these sensors are not suitable for deriving Energy dashboard
consumption. Use a meter that reports active energy or measured active power instead.

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
- Published releases include `vool_modbus.zip`, which HACS downloads using the `zip_release` setting.
- Check that you are using `martinkenk/vool_modbus_ha` and that the selected release contains this asset.

## Contributing

See the [Contributing Guidelines](CONTRIBUTING.md) to submit an issue or pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with or endorsed by VOOL. Use at your own risk.

## Support

- [Issue Tracker](https://github.com/martinkenk/vool_modbus_ha/issues)
