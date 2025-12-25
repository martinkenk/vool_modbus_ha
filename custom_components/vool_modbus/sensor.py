"""Sensor platform for VOOL Modbus integration."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CHARGER_STATE_MAP,
)
from .coordinator import VoolModbusCoordinator
from .entity import VoolModbusEntity


@dataclass(frozen=True, kw_only=True)
class VoolSensorEntityDescription(SensorEntityDescription):
    """Describes a VOOL sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None


# =============================================================================
# Charger Sensors (based on registers 100-111, 200-201, 501-502)
# =============================================================================
CHARGER_SENSORS: tuple[VoolSensorEntityDescription, ...] = (
    VoolSensorEntityDescription(
        key="charger_state",
        translation_key="charger_state",
        icon="mdi:ev-station",
        value_fn=lambda data: CHARGER_STATE_MAP.get(data.get("charger_state", 0), "Unknown"),
    ),
    VoolSensorEntityDescription(
        key="active_power",
        translation_key="active_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("active_power"),
    ),
    VoolSensorEntityDescription(
        key="l1_power",
        translation_key="l1_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("l1_power"),
    ),
    VoolSensorEntityDescription(
        key="l2_power",
        translation_key="l2_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("l2_power"),
    ),
    VoolSensorEntityDescription(
        key="l3_power",
        translation_key="l3_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("l3_power"),
    ),
    VoolSensorEntityDescription(
        key="current_l1",
        translation_key="current_l1",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current_l1"),
    ),
    VoolSensorEntityDescription(
        key="current_l2",
        translation_key="current_l2",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current_l2"),
    ),
    VoolSensorEntityDescription(
        key="current_l3",
        translation_key="current_l3",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("current_l3"),
    ),
    VoolSensorEntityDescription(
        key="voltage_l1",
        translation_key="voltage_l1",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voltage_l1"),
    ),
    VoolSensorEntityDescription(
        key="voltage_l2",
        translation_key="voltage_l2",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voltage_l2"),
    ),
    VoolSensorEntityDescription(
        key="voltage_l3",
        translation_key="voltage_l3",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("voltage_l3"),
    ),
    VoolSensorEntityDescription(
        key="energy_imported",
        translation_key="energy_imported",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda data: data.get("energy_imported"),
    ),
    VoolSensorEntityDescription(
        key="external_current_limit",
        translation_key="external_current_limit",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.get("external_current_limit"),
    ),
    VoolSensorEntityDescription(
        key="requested_phases",
        translation_key="requested_phases",
        icon="mdi:sine-wave",
        value_fn=lambda data: data.get("requested_phases"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up VOOL Modbus sensors."""
    coordinator: VoolModbusCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        VoolSensor(coordinator, description)
        for description in CHARGER_SENSORS
    )


class VoolSensor(VoolModbusEntity, SensorEntity):
    """Representation of a VOOL sensor."""

    entity_description: VoolSensorEntityDescription

    def __init__(
        self,
        coordinator: VoolModbusCoordinator,
        description: VoolSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self.coordinator.data)

        return self.coordinator.data.get(self.entity_description.key)
