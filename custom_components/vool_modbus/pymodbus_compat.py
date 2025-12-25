"""pymodbus API compatibility helpers.

Home Assistant may end up running different pymodbus 3.x versions depending on the core
version and dependency resolver. pymodbus has changed the Modbus unit/slave argument
name and whether it is keyword-only across releases.

These helpers try the common call patterns and fall back to calls without an explicit
unit id if the installed pymodbus version doesn't support passing it.
"""

from __future__ import annotations

import logging
from typing import Any, Awaitable, Callable

_LOGGER = logging.getLogger(__name__)


class VoolPymodbusCompatError(TypeError):
    """Raised when no compatible pymodbus call signature is found."""


async def _try_calls(awaitables: list[Callable[[], Awaitable[Any]]], context: str) -> Any:
    last_error: Exception | None = None

    for factory in awaitables:
        try:
            return await factory()
        except TypeError as err:
            last_error = err

    raise VoolPymodbusCompatError(f"No compatible pymodbus call signature for {context}: {last_error}")


async def async_read_input_registers(client: Any, address: int, count: int, unit_id: int) -> Any:
    """Read input registers with best-effort unit/slave handling."""

    address = int(address)
    count = int(count)
    unit_id = int(unit_id)

    async def call_address_count_slave() -> Any:
        return await client.read_input_registers(address=address, count=count, slave=unit_id)

    async def call_address_count_unit() -> Any:
        return await client.read_input_registers(address=address, count=count, unit=unit_id)

    async def call_address_count_slave_id() -> Any:
        return await client.read_input_registers(address=address, count=count, slave_id=unit_id)

    async def call_address_count_device_id() -> Any:
        return await client.read_input_registers(address=address, count=count, device_id=unit_id)

    async def call_address_count() -> Any:
        return await client.read_input_registers(address=address, count=count)

    async def call_positional_address_count_slave() -> Any:
        return await client.read_input_registers(address, count, unit_id)

    async def call_positional_address_count() -> Any:
        return await client.read_input_registers(address, count)

    try:
        return await _try_calls(
            [
                call_address_count_slave,
                call_address_count_unit,
                call_address_count_slave_id,
                call_address_count_device_id,
                call_address_count,
                call_positional_address_count_slave,
                call_positional_address_count,
            ],
            context="read_input_registers",
        )
    except VoolPymodbusCompatError:
        _LOGGER.warning(
            "pymodbus does not accept unit/slave id for read_input_registers; falling back to default unit id"
        )
        return await client.read_input_registers(address=address, count=count)


async def async_read_holding_registers(client: Any, address: int, count: int, unit_id: int) -> Any:
    """Read holding registers with best-effort unit/slave handling."""

    address = int(address)
    count = int(count)
    unit_id = int(unit_id)

    async def call_address_count_slave() -> Any:
        return await client.read_holding_registers(address=address, count=count, slave=unit_id)

    async def call_address_count_unit() -> Any:
        return await client.read_holding_registers(address=address, count=count, unit=unit_id)

    async def call_address_count_slave_id() -> Any:
        return await client.read_holding_registers(address=address, count=count, slave_id=unit_id)

    async def call_address_count_device_id() -> Any:
        return await client.read_holding_registers(address=address, count=count, device_id=unit_id)

    async def call_address_count() -> Any:
        return await client.read_holding_registers(address=address, count=count)

    async def call_positional_address_count_slave() -> Any:
        return await client.read_holding_registers(address, count, unit_id)

    async def call_positional_address_count() -> Any:
        return await client.read_holding_registers(address, count)

    try:
        return await _try_calls(
            [
                call_address_count_slave,
                call_address_count_unit,
                call_address_count_slave_id,
                call_address_count_device_id,
                call_address_count,
                call_positional_address_count_slave,
                call_positional_address_count,
            ],
            context="read_holding_registers",
        )
    except VoolPymodbusCompatError:
        _LOGGER.warning(
            "pymodbus does not accept unit/slave id for read_holding_registers; falling back to default unit id"
        )
        return await client.read_holding_registers(address=address, count=count)


async def async_write_register(client: Any, address: int, value: int, unit_id: int) -> Any:
    """Write a single holding register with best-effort unit/slave handling."""

    address = int(address)
    value = int(value)
    unit_id = int(unit_id)

    async def call_address_value_slave() -> Any:
        return await client.write_register(address=address, value=value, slave=unit_id)

    async def call_address_value_unit() -> Any:
        return await client.write_register(address=address, value=value, unit=unit_id)

    async def call_address_value_slave_id() -> Any:
        return await client.write_register(address=address, value=value, slave_id=unit_id)

    async def call_address_value_device_id() -> Any:
        return await client.write_register(address=address, value=value, device_id=unit_id)

    async def call_address_value() -> Any:
        return await client.write_register(address=address, value=value)

    async def call_positional_address_value_slave() -> Any:
        return await client.write_register(address, value, unit_id)

    async def call_positional_address_value() -> Any:
        return await client.write_register(address, value)

    try:
        return await _try_calls(
            [
                call_address_value_slave,
                call_address_value_unit,
                call_address_value_slave_id,
                call_address_value_device_id,
                call_address_value,
                call_positional_address_value_slave,
                call_positional_address_value,
            ],
            context="write_register",
        )
    except VoolPymodbusCompatError:
        _LOGGER.warning(
            "pymodbus does not accept unit/slave id for write_register; falling back to default unit id"
        )
        return await client.write_register(address=address, value=value)
