"""Binary sensor platform for VOOL Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import VoolModbusCoordinator
from .entity import VoolModbusEntity


@dataclass(frozen=True, kw_only=True)
class VoolBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a VOOL binary sensor entity."""

    value_fn: Callable[[dict[str, Any]], bool | None]


# Charger states based on register 100:
# The exact state values may need adjustment based on actual device behavior
# Common states: 1=NotConnected, 2=Connected, 3=Charging, 4=Paused, 5=Error
CHARGER_BINARY_SENSORS: tuple[VoolBinarySensorEntityDescription, ...] = (
    VoolBinarySensorEntityDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.PLUG,
        # Connected when state >= 2 (anything except "Not Connected")
        value_fn=lambda data: data.get("charger_state", 0) >= 2,
    ),
    VoolBinarySensorEntityDescription(
        key="charging",
        translation_key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        # Charging when state == 3
        value_fn=lambda data: data.get("charger_state", 0) == 3,
    ),
    VoolBinarySensorEntityDescription(
        key="error",
        translation_key="error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        # Error when state == 5
        value_fn=lambda data: data.get("charger_state", 0) == 5,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VOOL Modbus binary sensors."""
    coordinator: VoolModbusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        VoolBinarySensor(coordinator, description)
        for description in CHARGER_BINARY_SENSORS
    )


class VoolBinarySensor(VoolModbusEntity, BinarySensorEntity):
    """Representation of a VOOL binary sensor."""

    entity_description: VoolBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: VoolModbusCoordinator,
        description: VoolBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        if self.coordinator.data is None:
            return None
        
        return self.entity_description.value_fn(self.coordinator.data)
