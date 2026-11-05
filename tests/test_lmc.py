"""Regression tests for read-only LMC measurements and options reload."""

import struct
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.vool_modbus.const import (
    CONF_DEVICE_TYPE,
    CONF_SLAVE_ID,
    DEVICE_TYPE_LMC,
    DOMAIN,
)
from custom_components.vool_modbus.coordinator import VoolModbusCoordinator

pytestmark = pytest.mark.usefixtures("enable_custom_integrations")


@pytest.fixture
def lmc_client():
    """Provide one measurement block with reserved gaps."""
    registers = [0] * 26
    for offset, value in ((0, 2.5), (2, 4.0), (4, 1.0), (20, 230.0), (22, 240.0), (24, 235.0)):
        registers[offset:offset + 2] = struct.unpack(">HH", struct.pack(">f", value))
    client = MagicMock(connected=True)
    client.connect = AsyncMock(return_value=True)
    client.read_holding_registers = AsyncMock(
        return_value=SimpleNamespace(registers=registers, isError=lambda: False)
    )
    with patch(
        "custom_components.vool_modbus.coordinator.AsyncModbusTcpClient",
        return_value=client,
    ):
        yield client


@pytest.fixture
def lmc_entry(hass):
    """Add an LMC config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="LMC Test",
        data={CONF_HOST: "192.0.2.1", CONF_DEVICE_TYPE: DEVICE_TYPE_LMC},
    )
    entry.add_to_hass(hass)
    return entry


async def test_lmc_measurements_and_apparent_power(hass, lmc_entry, lmc_client):
    """Decode the documented region and publish VA, never active watts."""
    assert await hass.config_entries.async_setup(lmc_entry.entry_id)
    await hass.async_block_till_done()

    data = hass.data[DOMAIN][lmc_entry.entry_id].data
    assert [data[f"mains_current_l{i}"] for i in (1, 2, 3)] == [2.5, 4.0, 1.0]
    assert [data[f"mains_voltage_l{i}"] for i in (1, 2, 3)] == [230.0, 240.0, 235.0]
    assert data["mains_power_total"] == 1770.0
    lmc_client.read_holding_registers.assert_awaited_once_with(
        address=600, count=26, slave=1
    )

    sensors = hass.states.async_all("sensor")
    assert len(sensors) == 10
    apparent_power = [
        state for state in sensors if state.attributes.get("device_class") == "apparent_power"
    ]
    assert len(apparent_power) == 4
    assert all(state.attributes["unit_of_measurement"] == "VA" for state in apparent_power)
    assert not hass.states.async_all("button")
    assert not hass.states.async_all("switch")
    assert not hass.states.async_all("number")
    assert not hass.states.async_all("select")
    assert not hass.states.async_all("binary_sensor")


async def test_options_reload_keeps_lmc_available(hass, lmc_entry, lmc_client):
    """Use HA's setup lifecycle and apply all connection and polling options."""
    assert await hass.config_entries.async_setup(lmc_entry.entry_id)
    await hass.async_block_till_done()
    original = hass.data[DOMAIN][lmc_entry.entry_id]
    original_entity_ids = {state.entity_id for state in hass.states.async_all("sensor")}

    hass.config_entries.async_update_entry(
        lmc_entry,
        options={CONF_SCAN_INTERVAL: 15, CONF_PORT: 1502, CONF_SLAVE_ID: 7},
    )
    await hass.async_block_till_done()

    coordinator = hass.data[DOMAIN][lmc_entry.entry_id]
    assert coordinator is not original
    assert lmc_entry.state is ConfigEntryState.LOADED
    assert coordinator.update_interval == timedelta(seconds=15)
    assert coordinator.port == 1502
    assert coordinator.slave_id == 7
    assert {state.entity_id for state in hass.states.async_all("sensor")} == original_entity_ids
    assert all(state.state != "unavailable" for state in hass.states.async_all("sensor"))
    assert lmc_client.read_holding_registers.await_args.kwargs == {
        "address": 600, "count": 26, "slave": 7
    }


async def test_lmc_modbus_exception_fails_update(hass, lmc_entry, lmc_client):
    """Do not publish measurements when the device rejects a read."""
    lmc_client.read_holding_registers.return_value = SimpleNamespace(isError=lambda: True)
    coordinator = VoolModbusCoordinator(hass, lmc_entry)

    with pytest.raises(UpdateFailed, match="Error reading LMC measurements"):
        await coordinator._async_update_data()
