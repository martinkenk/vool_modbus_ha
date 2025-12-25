"""Switch platform for VOOL Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    REG_CHARGING_COMMAND,
)
from .coordinator import VoolModbusCoordinator
from .entity import VoolModbusEntity


# Charging command values per spec
CHARGING_CMD_START = 1
CHARGING_CMD_STOP = 2


@dataclass(frozen=True, kw_only=True)
class VoolSwitchEntityDescription(SwitchEntityDescription):
    """Describes a VOOL switch entity."""

    register: int
    data_key: str
    on_value: int = 1
    off_value: int = 0


CHARGER_SWITCHES: tuple[VoolSwitchEntityDescription, ...] = (
    VoolSwitchEntityDescription(
        key="charging_enabled",
        translation_key="charging_enabled",
        icon="mdi:ev-plug-type2",
        register=REG_CHARGING_COMMAND,
        data_key="charging_command",
        on_value=CHARGING_CMD_START,
        off_value=CHARGING_CMD_STOP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VOOL Modbus switches."""
    coordinator: VoolModbusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        VoolSwitch(coordinator, description)
        for description in CHARGER_SWITCHES
    )


class VoolSwitch(VoolModbusEntity, SwitchEntity):
    """Representation of a VOOL switch."""

    entity_description: VoolSwitchEntityDescription

    def __init__(
        self,
        coordinator: VoolModbusCoordinator,
        description: VoolSwitchEntityDescription,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the switch is on (charging started)."""
        if self.coordinator.data is None:
            return None
        
        # Check if charging command was set to START
        cmd_value = self.coordinator.data.get(self.entity_description.data_key)
        if cmd_value is None:
            return None
        return cmd_value == self.entity_description.on_value

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on (start charging)."""
        await self.coordinator.async_write_register(
            self.entity_description.register, self.entity_description.on_value
        )

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off (stop charging)."""
        await self.coordinator.async_write_register(
            self.entity_description.register, self.entity_description.off_value
        )
