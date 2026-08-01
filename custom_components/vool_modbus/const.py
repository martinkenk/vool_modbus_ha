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

# Charger states (register 100)
# VOOL Modbus Interface Manual 25.11.2025, firmware v1.9.40.
CHARGER_STATE_UNDEFINED: Final = 0
CHARGER_STATE_AVAILABLE: Final = 1
CHARGER_STATE_PREPARING: Final = 2
CHARGER_STATE_CHARGING: Final = 3
CHARGER_STATE_SUSPENDED_EV: Final = 4
CHARGER_STATE_SUSPENDED_EVSE: Final = 5
CHARGER_STATE_FINISHING: Final = 6
CHARGER_STATE_RESERVED: Final = 7
CHARGER_STATE_UNAVAILABLE: Final = 8
CHARGER_STATE_FAULTED: Final = 9
CHARGER_STATE_STARTING_CHARGING: Final = 10

CHARGER_STATE_MAP: Final[dict[int, str]] = {
    CHARGER_STATE_UNDEFINED: "Undefined",
    CHARGER_STATE_AVAILABLE: "Available",
    CHARGER_STATE_PREPARING: "Preparing",
    CHARGER_STATE_CHARGING: "Charging",
    CHARGER_STATE_SUSPENDED_EV: "Suspended by EV",
    CHARGER_STATE_SUSPENDED_EVSE: "Suspended by EVSE",
    CHARGER_STATE_FINISHING: "Finishing",
    CHARGER_STATE_RESERVED: "Reserved",
    CHARGER_STATE_UNAVAILABLE: "Unavailable",
    CHARGER_STATE_FAULTED: "Faulted",
    CHARGER_STATE_STARTING_CHARGING: "Starting Charging",
}

# These states imply that a charging cable/vehicle is present.
CHARGER_CONNECTED_STATES: Final[frozenset[int]] = frozenset(
    {
        CHARGER_STATE_PREPARING,
        CHARGER_STATE_CHARGING,
        CHARGER_STATE_SUSPENDED_EV,
        CHARGER_STATE_SUSPENDED_EVSE,
        CHARGER_STATE_FINISHING,
        CHARGER_STATE_STARTING_CHARGING,
    }
)
