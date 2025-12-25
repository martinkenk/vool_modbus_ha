# VOOL Modbus Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/martinkenk/vool-modbus-ha.svg)](https://github.com/martinkenk/vool-modbus-ha/releases)
[![License](https://img.shields.io/github/license/martinkenk/vool-modbus-ha.svg)](LICENSE)

A Home Assistant custom integration for VOOL EV Chargers via Modbus TCP.

![VOOL Logo](images/logo.png)

## Features

- **Real-time monitoring**: Power, current, voltage (per phase), energy consumption
- **Status monitoring**: Charger state, requested phases, vehicle connection status
- **Full control**: Start/stop charging, set external current limits, configure allowed phases

## Installation

### HACS (Recommended)

1. Ensure you have [HACS](https://hacs.xyz/) installed
2. Go to HACS → Integrations → ⋮ (menu) → Custom repositories
3. Add this repository URL: `https://github.com/martinkenk/vool-modbus-ha`
4. Select category: **Integration**
5. Click **Add**
6. Search for "VOOL Modbus" in HACS and install it
7. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/martinkenk/vool-modbus-ha/releases)
2. Extract the `custom_components/vool_modbus` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

### Adding the Integration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "VOOL Modbus"
4. Enter the connection details:
   - **IP Address**: The IP address of your VOOL device
   - **Port**: Modbus TCP port (default: 502)
   - **Slave ID**: Modbus slave ID (default: 1)
   - **Name**: A friendly name for the device
5. Click **Submit**

### Multiple Devices

You can add multiple VOOL devices by repeating the configuration process. Each device will appear as a separate integration entry with its own entities.

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

## Dashboard

A sample dashboard configuration is included in the `dashboard/` folder. See [Dashboard Setup](dashboard/README.md) for instructions.

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
- Verify the Modbus slave ID is correct (default: 1)
- Ensure no other application is using the Modbus connection

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This integration is not officially affiliated with or endorsed by VOOL. Use at your own risk.

## Support

- [Issue Tracker](https://github.com/martinkenk/vool-modbus-ha/issues)
- [Discussions](https://github.com/martinkenk/vool-modbus-ha/discussions)
