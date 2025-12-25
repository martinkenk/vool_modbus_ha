# VOOL Modbus Integration

A Home Assistant custom integration for VOOL EV Chargers via Modbus TCP.

## Features

- Real-time monitoring: Power, current, voltage (per phase), energy consumption
- Status monitoring: Charger state, requested phases, vehicle connection status  
- Full control: Start/stop charging, set external current limits, configure allowed phases

## Configuration

After installation, add the integration via Settings → Devices & Services → Add Integration → VOOL Modbus.

You'll need:
- IP address of your VOOL device
- Modbus TCP port (default: 502)
- Modbus slave ID (default: 1)

## More Information

See the [README](https://github.com/martinkenk/vool_modbus_ha) for full documentation.
