"""Button platform for VOOL Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    REG_CHARGING_COMMAND,
    CHARGING_CMD_START,
    CHARGING_CMD_STOP,
)
from .coordinator import VoolModbusCoordinator
from .entity import VoolModbusEntity


@dataclass(frozen=True, kw_only=True)
class VoolButtonEntityDescription(ButtonEntityDescription):
    """Describes a VOOL button entity."""

    register: int
    value: int


CHARGER_BUTTONS: tuple[VoolButtonEntityDescription, ...] = (
    VoolButtonEntityDescription(
        key="start_charge",
        translation_key="start_charge",
        icon="mdi:play",
        register=REG_CHARGING_COMMAND,
        value=CHARGING_CMD_START,  # 1 = Start
    ),
    VoolButtonEntityDescription(
        key="stop_charge",
        translation_key="stop_charge",
        icon="mdi:stop",
        register=REG_CHARGING_COMMAND,
        value=CHARGING_CMD_STOP,  # 2 = Stop
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VOOL Modbus buttons."""
    coordinator: VoolModbusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        VoolButton(coordinator, description)
        for description in CHARGER_BUTTONS
    )


class VoolButton(VoolModbusEntity, ButtonEntity):
    """Representation of a VOOL button."""

    entity_description: VoolButtonEntityDescription

    def __init__(
        self,
        coordinator: VoolModbusCoordinator,
        description: VoolButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Press the button."""
        await self.coordinator.async_write_register(
            self.entity_description.register,
            self.entity_description.value,
        )
