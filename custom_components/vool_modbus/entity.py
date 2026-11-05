"""Base entity for VOOL Modbus integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_SLAVE_ID, DEFAULT_SLAVE_ID, DEVICE_TYPE_CHARGER, DOMAIN
from .coordinator import VoolModbusCoordinator


class VoolModbusEntity(CoordinatorEntity[VoolModbusCoordinator]):
    """Base class for VOOL Modbus entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: VoolModbusCoordinator,
        entity_key: str,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._entity_key = entity_key
        # Connection options must not change existing device or entity identities.
        original_slave_id = int(coordinator.entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))
        self._device_identifier = f"{coordinator.host}_{original_slave_id}"
        self._attr_unique_id = f"{self._device_identifier}_{entity_key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_identifier)},
            name=self.coordinator.entry.title,
            manufacturer="VOOL",
            model="Charger" if self.coordinator.device_type == DEVICE_TYPE_CHARGER else "LMC",
            configuration_url=f"http://{self.coordinator.host}",
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.coordinator.last_update_success
