# VOOL Dashboard Setup

This folder contains sample dashboard configurations for your VOOL Charger.

## Quick Setup

### Option 1: Import Dashboard

1. Go to **Settings** → **Dashboards**
2. Click **Add Dashboard**
3. Select **New dashboard from scratch**
4. Name it "EV Charging"
5. Click **Create**
6. Open the new dashboard
7. Click the three dots (⋮) → **Edit Dashboard**
8. Click the three dots (⋮) → **Raw configuration editor**
9. Replace the content with the YAML from the appropriate file below
10. Click **Save**

### Option 2: Add Cards to Existing Dashboard

Copy individual card configurations from the YAML files and add them to your existing dashboards.

## Dashboard Files

- `charger_dashboard.yaml` - Full dashboard for VOOL Charger
- `charger_cards.yaml` - Individual cards for the charger

## Customization

Replace entity IDs in the YAML files to match your setup. Entity IDs depend on the name you gave the device in the config flow, so the easiest approach is to copy the entity IDs from Home Assistant (Developer Tools → States) and update the YAML.

- Sensors: `sensor.<your_device_name>_<sensor_name>`
- Binary Sensors: `binary_sensor.<your_device_name>_<sensor_name>`
- Switches: `switch.<your_device_name>_<switch_name>`
- Numbers: `number.<your_device_name>_<number_name>`
- Selects: `select.<your_device_name>_<select_name>`
- Buttons: `button.<your_device_name>_<button_name>`

## Screenshots

*(Add screenshots of your dashboard here)*
