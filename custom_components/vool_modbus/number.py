"""Number platform for VOOL Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    REG_EXTERNAL_CURRENT_LIMIT,
)
from .coordinator import VoolModbusCoordinator
from .entity import VoolModbusEntity


@dataclass(frozen=True, kw_only=True)
class VoolNumberEntityDescription(NumberEntityDescription):
    """Describes a VOOL number entity."""

    register: int
    data_key: str
    multiplier: float = 1.0


CHARGER_NUMBERS: tuple[VoolNumberEntityDescription, ...] = (
    VoolNumberEntityDescription(
        key="external_current_limit",
        translation_key="external_current_limit",
        device_class=NumberDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        native_min_value=6,
        native_max_value=32,
        native_step=0.01,
        mode=NumberMode.SLIDER,
        icon="mdi:current-ac",
        register=REG_EXTERNAL_CURRENT_LIMIT,
        data_key="external_current_limit",
        multiplier=100,  # Register stores A × 0.01, so we multiply by 100
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VOOL Modbus numbers."""
    coordinator: VoolModbusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        VoolNumber(coordinator, description)
        for description in CHARGER_NUMBERS
    )


class VoolNumber(VoolModbusEntity, NumberEntity):
    """Representation of a VOOL number."""

    entity_description: VoolNumberEntityDescription

    def __init__(
        self,
        coordinator: VoolModbusCoordinator,
        description: VoolNumberEntityDescription,
    ) -> None:
        """Initialize the number."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        
        return self.coordinator.data.get(self.entity_description.data_key)

    async def async_set_native_value(self, value: float) -> None:
        """Set a new value."""
        register_value = int(value * self.entity_description.multiplier)
        await self.coordinator.async_write_register(
            self.entity_description.register, register_value
        )
