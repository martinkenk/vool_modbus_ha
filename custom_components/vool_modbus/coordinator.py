"""Data coordinator for VOOL Modbus integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_DEVICE_TYPE,
    CONF_SLAVE_ID,
    DEVICE_TYPE_CHARGER,
    DEFAULT_MODBUS_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    # Status registers (100-111)
    REG_CHARGER_STATE,
    REG_REQUESTED_PHASES,
    REG_CURRENT_L1,
    REG_CURRENT_L2,
    REG_CURRENT_L3,
    REG_VOLTAGE_L1,
    REG_VOLTAGE_L2,
    REG_VOLTAGE_L3,
    REG_ACTIVE_POWER,
    REG_ACTIVE_POWER_L1,
    REG_ACTIVE_POWER_L2,
    REG_ACTIVE_POWER_L3,
    # Energy registers
    REG_ENERGY_IMPORTED,
    # Control registers
    REG_CHARGING_COMMAND,
)

from .pymodbus_compat import (
    async_read_holding_registers,
    async_write_register,
)

_LOGGER = logging.getLogger(__name__)


def _signed16(value: int) -> int:
    """Convert unsigned 16-bit value to signed 16-bit value."""
    if value >= 0x8000:
        return value - 0x10000
    return value


class VoolModbusCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to manage data updates from VOOL device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.host = entry.data[CONF_HOST]
        self.port = int(entry.data.get(CONF_PORT, DEFAULT_MODBUS_PORT))
        self.slave_id = int(entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))
        self.device_type = entry.data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_CHARGER)
        self._client: AsyncModbusTcpClient | None = None
        self._connected = False

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _ensure_connected(self) -> bool:
        """Ensure we are connected to the Modbus device."""
        if self._client is None or not self._connected:
            self._client = AsyncModbusTcpClient(
                host=self.host,
                port=self.port,
                timeout=10,
            )
            self._connected = await self._client.connect()
        return self._connected

    async def async_close(self) -> None:
        """Close the Modbus connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
            self._connected = False

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the VOOL device."""
        try:
            if not await self._ensure_connected():
                raise UpdateFailed("Failed to connect to Modbus device")

            data: dict[str, Any] = {}
            data = await self._read_charger_data()
            data.update(await self._read_charger_holding_registers())

            return data

        except ModbusException as err:
            self._connected = False
            raise UpdateFailed(f"Modbus error: {err}") from err
        except Exception as err:
            self._connected = False
            raise UpdateFailed(f"Error communicating with device: {err}") from err

    async def _read_charger_data(self) -> dict[str, Any]:
        """Read charger status registers (100-111) - all are holding registers."""
        data: dict[str, Any] = {}

        # Read status registers 100-111 (12 registers) using FC03 (holding registers)
        result = await async_read_holding_registers(
            self._client, REG_CHARGER_STATE, 12, self.slave_id
        )

        if result.isError():
            raise UpdateFailed(f"Error reading charger data: {result}")

        regs = result.registers
        base = REG_CHARGER_STATE

        # Debug logging to help diagnose issues
        _LOGGER.debug(
            "Raw registers 100-111: %s",
            [regs[i] for i in range(12)]
        )

        data["charger_state"] = regs[REG_CHARGER_STATE - base]
        data["requested_phases"] = regs[REG_REQUESTED_PHASES - base]
        # Current registers are signed int16, A × 0.01
        data["current_l1"] = _signed16(regs[REG_CURRENT_L1 - base]) * 0.01
        data["current_l2"] = _signed16(regs[REG_CURRENT_L2 - base]) * 0.01
        data["current_l3"] = _signed16(regs[REG_CURRENT_L3 - base]) * 0.01
        # Voltage registers are signed int16, V × 0.1
        data["voltage_l1"] = _signed16(regs[REG_VOLTAGE_L1 - base]) * 0.1
        data["voltage_l2"] = _signed16(regs[REG_VOLTAGE_L2 - base]) * 0.1
        data["voltage_l3"] = _signed16(regs[REG_VOLTAGE_L3 - base]) * 0.1
        # Power registers are signed int16, kW × 0.01
        data["active_power"] = _signed16(regs[REG_ACTIVE_POWER - base]) * 0.01
        data["l1_power"] = _signed16(regs[REG_ACTIVE_POWER_L1 - base]) * 0.01
        data["l2_power"] = _signed16(regs[REG_ACTIVE_POWER_L2 - base]) * 0.01
        data["l3_power"] = _signed16(regs[REG_ACTIVE_POWER_L3 - base]) * 0.01

        # Read energy imported (registers 200-201, uint32)
        energy_result = await async_read_holding_registers(
            self._client, REG_ENERGY_IMPORTED, 2, self.slave_id
        )

        if not energy_result.isError():
            energy_regs = energy_result.registers
            # uint32: MSB at 200, LSB at 201
            data["energy_imported"] = (
                (energy_regs[0] << 16) | energy_regs[1]
            ) / 1000.0  # Wh to kWh

        return data

    async def _read_charger_holding_registers(self) -> dict[str, Any]:
        """Read charger control registers (500-502)."""
        data: dict[str, Any] = {}

        # Read control registers 500-502 (charging command, current limit, and phases)
        result = await async_read_holding_registers(
            self._client, REG_CHARGING_COMMAND, 3, self.slave_id
        )

        if result.isError():
            _LOGGER.warning("Error reading control registers: %s", result)
            return data

        regs = result.registers

        data["charging_command"] = regs[0]  # 1=Start, 2=Stop
        data["external_current_limit"] = regs[1] * 0.01  # A × 0.01
        data["external_allowed_phases"] = regs[2]

        return data

    async def async_write_register(self, address: int, value: int) -> bool:
        """Write a value to a holding register."""
        try:
            if not await self._ensure_connected():
                raise UpdateFailed("Failed to connect to Modbus device")

            result = await async_write_register(self._client, address, value, self.slave_id)
            
            if result.isError():
                _LOGGER.error("Error writing register %s: %s", address, result)
                return False
            
            # Trigger a data refresh
            await self.async_request_refresh()
            return True

        except Exception as err:
            _LOGGER.error("Error writing to Modbus device: %s", err)
            return False

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, f"{self.host}_{self.slave_id}")},
            "name": self.entry.title,
            "manufacturer": "VOOL",
            "model": "Charger",
            "configuration_url": f"http://{self.host}",
        }
