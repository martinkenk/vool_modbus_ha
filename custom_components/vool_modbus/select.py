"""Select platform for VOOL Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    REG_EXTERNAL_ALLOWED_PHASES,
    PHASES_L1,
    PHASES_L1_L2,
    PHASES_L1_L2_L3,
)
from .coordinator import VoolModbusCoordinator
from .entity import VoolModbusEntity


# Phase options mapping (binary representation)
PHASES_MAP: dict[int, str] = {
    PHASES_L1: "1 Phase (L1)",
    PHASES_L1_L2: "2 Phases (L1+L2)",
    PHASES_L1_L2_L3: "3 Phases (L1+L2+L3)",
}

PHASES_REVERSE_MAP: dict[str, int] = {v: k for k, v in PHASES_MAP.items()}


@dataclass(frozen=True, kw_only=True)
class VoolSelectEntityDescription(SelectEntityDescription):
    """Describes a VOOL select entity."""

    register: int
    data_key: str
    options_map: dict[int, str]
    reverse_map: dict[str, int]


CHARGER_SELECTS: tuple[VoolSelectEntityDescription, ...] = (
    VoolSelectEntityDescription(
        key="allowed_phases",
        translation_key="allowed_phases",
        icon="mdi:sine-wave",
        register=REG_EXTERNAL_ALLOWED_PHASES,
        data_key="external_allowed_phases",
        options=list(PHASES_MAP.values()),
        options_map=PHASES_MAP,
        reverse_map=PHASES_REVERSE_MAP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VOOL Modbus selects."""
    coordinator: VoolModbusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        VoolSelect(coordinator, description)
        for description in CHARGER_SELECTS
    )


class VoolSelect(VoolModbusEntity, SelectEntity):
    """Representation of a VOOL select."""

    entity_description: VoolSelectEntityDescription

    def __init__(
        self,
        coordinator: VoolModbusCoordinator,
        description: VoolSelectEntityDescription,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_options = description.options

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.coordinator.data is None:
            return None
        
        value = self.coordinator.data.get(self.entity_description.data_key)
        if value is None:
            return None
        
        return self.entity_description.options_map.get(value)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        # Reverse lookup to get the value
        reverse_map = {v: k for k, v in self.entity_description.options_map.items()}
        value = reverse_map.get(option)
        
        if value is not None:
            await self.coordinator.async_write_register(
                self.entity_description.register, value
            )
