# VOOL Modbus Installation Guide

This guide provides detailed instructions for installing the VOOL Modbus integration for Home Assistant.

## Prerequisites

- Home Assistant 2024.1.0 or newer
- VOOL Charger device with Modbus TCP enabled
- Network connectivity between Home Assistant and your VOOL device
- Knowledge of your VOOL device's IP address

## Installation Methods

### Method 1: HACS (Recommended)

HACS (Home Assistant Community Store) is the recommended way to install custom integrations.

#### Step 1: Install HACS (if not already installed)

1. Visit the [HACS installation page](https://hacs.xyz/docs/setup/prerequisites)
2. Follow the instructions for your Home Assistant installation type
3. Restart Home Assistant after installation

#### Step 2: Add Custom Repository

1. Open Home Assistant
2. Navigate to **HACS** in the sidebar
3. Click on **Integrations**
4. Click the three dots (⋮) in the top right corner
5. Select **Custom repositories**
6. Enter the repository URL:
   ```
   https://github.com/martinkenk/vool-modbus-ha
   ```
7. Select **Integration** as the category
8. Click **Add**

#### Step 3: Install the Integration

1. In HACS Integrations, click **+ Explore & Download Repositories**
2. Search for "VOOL Modbus"
3. Click on the integration
4. Click **Download**
5. Select the latest version
6. Click **Download** again
7. **Restart Home Assistant**

### Method 2: Manual Installation

If you prefer not to use HACS, you can install manually.

#### Step 1: Download the Integration

1. Go to the [releases page](https://github.com/martinkenk/vool-modbus-ha/releases)
2. Download the latest `vool_modbus.zip` file
3. Extract the contents

#### Step 2: Copy Files

1. Locate your Home Assistant configuration directory
   - For Home Assistant OS: `/config/`
   - For Docker: The directory mapped to `/config`
   - For Core: `~/.homeassistant/`

2. Create the custom_components folder if it doesn't exist:
   ```bash
   mkdir -p /config/custom_components
   ```

3. Copy the `vool_modbus` folder to `custom_components`:
   ```bash
   cp -r vool_modbus /config/custom_components/
   ```

4. Your directory structure should look like:
   ```
   config/
   └── custom_components/
       └── vool_modbus/
           ├── __init__.py
           ├── config_flow.py
           ├── const.py
           ├── coordinator.py
           ├── entity.py
           ├── manifest.json
           ├── sensor.py
           ├── binary_sensor.py
           ├── switch.py
           ├── number.py
           ├── select.py
           ├── button.py
           ├── strings.json
           └── translations/
               └── en.json
   ```

#### Step 3: Restart Home Assistant

1. Go to **Settings** → **System** → **Restart**
2. Click **Restart** to restart Home Assistant

## Configuration

### Adding Your First Device

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "VOOL Modbus"
4. Select the integration

### Enter Connection Details

| Field | Description | Default |
|-------|-------------|---------|
| IP Address | The IP address of your VOOL device | Required |
| Modbus TCP Port | The Modbus TCP port | 502 |
| Modbus Slave ID | The Modbus slave ID | 1 |
| Device Name | A friendly name for this device | Auto-generated |

Click **Submit**

The integration will attempt to connect to your device. If successful, the device will be added.

### Adding Multiple Devices

You can add multiple VOOL devices by repeating the configuration process:

1. Go to **Settings** → **Devices & Services**
2. Find the VOOL Modbus integration
3. Click **+ Add Entry**
4. Follow the configuration steps for your additional device

Each device will have its own set of entities with unique names.

## Finding Your Device's IP Address

### From Your Router

1. Log into your router's admin interface
2. Look for connected devices or DHCP clients
3. Find the device named "VOOL" or similar

### From the VOOL App

1. Open the VOOL mobile app
2. Navigate to device settings
3. Look for network information

### Using Network Scanning

```bash
# On Linux/Mac
nmap -sn 192.168.1.0/24 | grep -B2 -i vool

# Or using arp-scan
sudo arp-scan --localnet | grep -i vool
```

## Enabling Modbus on Your VOOL Device

Modbus TCP must be enabled on your VOOL device. Refer to your VOOL device's documentation for instructions on enabling Modbus.

Typical default settings:
- **Port**: 502
- **Slave ID**: 1

## Dashboard Setup

The integration includes sample dashboards. See the [Dashboard Setup Guide](dashboard/README.md) for instructions.

### Recommended Frontend Cards (HACS)

For the best dashboard experience, install these cards from HACS:

1. **Mushroom Cards** - Beautiful, customizable cards
   - HACS → Frontend → Search "Mushroom"
   
2. **Mini Graph Card** - Historical graphs
   - HACS → Frontend → Search "Mini Graph Card"

## Troubleshooting

### Integration Not Found

If "VOOL Modbus" doesn't appear in the integration search:
1. Ensure you restarted Home Assistant after installation
2. Check that files are in the correct location
3. Check the Home Assistant logs for errors

### Cannot Connect

If you see "Failed to connect to the device":
1. Verify the IP address is correct
2. Ping the device: `ping <device-ip>`
3. Check that Modbus TCP is enabled on the device
4. Ensure port 502 is not blocked by firewall
5. Try the connection from another device

### Entities Show "Unavailable"

If entities appear but show "Unavailable":
1. Check the network connection
2. Reload the integration
3. Check Home Assistant logs for Modbus errors

### Getting Logs

To enable debug logging, add to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.vool_modbus: debug
    pymodbus: debug
```

Restart Home Assistant and check **Settings** → **System** → **Logs**.

## Updating the Integration

### Via HACS

1. Go to HACS → Integrations
2. Click on VOOL Modbus
3. Click **Update** if available
4. Restart Home Assistant

### Manual Update

1. Download the new version
2. Replace the files in `custom_components/vool_modbus/`
3. Restart Home Assistant

## Uninstalling

### Via HACS

1. Go to HACS → Integrations
2. Click on VOOL Modbus
3. Click the three dots (⋮)
4. Select **Remove**
5. Restart Home Assistant

### Manual Removal

1. Remove the device from **Settings** → **Devices & Services**
2. Delete the `custom_components/vool_modbus/` directory
3. Restart Home Assistant

## Support

- [Issue Tracker](https://github.com/martinkenk/vool-modbus-ha/issues)
- [Discussions](https://github.com/martinkenk/vool-modbus-ha/discussions)
- [Home Assistant Community Forum](https://community.home-assistant.io/)
