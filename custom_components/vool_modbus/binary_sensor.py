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

from .const import (
    CHARGER_CONNECTED_STATES,
    CHARGER_STATE_AVAILABLE,
    CHARGER_STATE_CHARGING,
    CHARGER_STATE_FAULTED,
    DOMAIN,
)
from .coordinator import VoolModbusCoordinator
from .entity import VoolModbusEntity


@dataclass(frozen=True, kw_only=True)
class VoolBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describes a VOOL binary sensor entity."""

    value_fn: Callable[[dict[str, Any]], bool | None]


def _vehicle_connected(data: dict[str, Any]) -> bool | None:
    """Return whether the charger state confirms vehicle presence."""
    charger_state = data.get("charger_state")

    if charger_state in CHARGER_CONNECTED_STATES:
        return True

    if charger_state == CHARGER_STATE_AVAILABLE:
        return False

    # Undefined, Reserved, Unavailable and Faulted do not reliably indicate
    # whether a vehicle is physically connected.
    return None


def _charger_state_is(
    data: dict[str, Any],
    expected_state: int,
) -> bool | None:
    """Return whether the charger is in the expected state."""
    charger_state = data.get("charger_state")
    if charger_state is None:
        return None

    return charger_state == expected_state


CHARGER_BINARY_SENSORS: tuple[VoolBinarySensorEntityDescription, ...] = (
    VoolBinarySensorEntityDescription(
        key="connected",
        translation_key="connected",
        device_class=BinarySensorDeviceClass.PLUG,
        value_fn=_vehicle_connected,
    ),
    VoolBinarySensorEntityDescription(
        key="charging",
        translation_key="charging",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        value_fn=lambda data: _charger_state_is(
            data,
            CHARGER_STATE_CHARGING,
        ),
    ),
    VoolBinarySensorEntityDescription(
        key="error",
        translation_key="error",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda data: _charger_state_is(
            data,
            CHARGER_STATE_FAULTED,
        ),
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
