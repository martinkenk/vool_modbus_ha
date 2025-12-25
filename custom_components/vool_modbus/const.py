"""Constants for the VOOL Modbus integration."""
from typing import Final

DOMAIN: Final = "vool_modbus"

# Configuration
CONF_DEVICE_TYPE: Final = "device_type"
CONF_MODBUS_PORT: Final = "modbus_port"
CONF_SLAVE_ID: Final = "slave_id"

# Device Types
DEVICE_TYPE_CHARGER: Final = "charger"

# Default values
DEFAULT_MODBUS_PORT: Final = 502
DEFAULT_SLAVE_ID: Final = 1
DEFAULT_SCAN_INTERVAL: Final = 5

# =============================================================================
# Modbus Register Addresses - ALL are Holding Registers (FC03 read, FC06 write)
# Based on official VOOL Modbus Interface Manual
# =============================================================================

# Status Registers (100-111) - Read Only
REG_CHARGER_STATE: Final = 100      # uint, enum, R
REG_REQUESTED_PHASES: Final = 101   # uint, binary, R
REG_CURRENT_L1: Final = 102         # int, A × 0.01, R
REG_CURRENT_L2: Final = 103         # int, A × 0.01, R
REG_CURRENT_L3: Final = 104         # int, A × 0.01, R
REG_VOLTAGE_L1: Final = 105         # int, V × 0.1, R
REG_VOLTAGE_L2: Final = 106         # int, V × 0.1, R
REG_VOLTAGE_L3: Final = 107         # int, V × 0.1, R
REG_ACTIVE_POWER: Final = 108       # int, kW × 0.01, R (total)
REG_ACTIVE_POWER_L1: Final = 109    # int, kW × 0.01, R
REG_ACTIVE_POWER_L2: Final = 110    # int, kW × 0.01, R
REG_ACTIVE_POWER_L3: Final = 111    # int, kW × 0.01, R

# Energy Registers (200-201) - Read Only
REG_ENERGY_IMPORTED: Final = 200    # uint32 (MSB), Wh, R (spans 200-201)

# Control Registers (500-502)
REG_CHARGING_COMMAND: Final = 500   # uint, enum, W only
REG_EXTERNAL_CURRENT_LIMIT: Final = 501  # uint, A × 0.01, R/W
REG_EXTERNAL_ALLOWED_PHASES: Final = 502  # uint, binary, R/W

# Charging Command Values (for register 500)
# Per spec: 1 = Start, 2 = Stop
CHARGING_CMD_START: Final = 1
CHARGING_CMD_STOP: Final = 2

# Phase configuration (binary representation for register 101/502)
# Bit 0 = L1, Bit 1 = L2, Bit 2 = L3
PHASES_L1: Final = 0b001  # 1
PHASES_L1_L2: Final = 0b011  # 3
PHASES_L1_L2_L3: Final = 0b111  # 7

# Charger States (register 100)
# These are example states - actual values may vary based on device firmware
CHARGER_STATE_MAP: Final = {
    0: "Unknown",
    1: "Not Connected",
    2: "Connected",
    3: "Charging",
    4: "Charging Paused",
    5: "Error",
    6: "Charging Complete",
}
