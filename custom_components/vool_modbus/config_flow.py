"""Config flow for VOOL Modbus integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_DEVICE_TYPE,
    CONF_SLAVE_ID,
    DEVICE_TYPE_CHARGER,
    DEVICE_TYPE_LMC,
    DEVICE_TYPES,
    DEFAULT_MODBUS_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_SCAN_INTERVAL,
    REG_CHARGER_STATE,
    REG_LMC_MEASUREMENTS_BASE,
)

from .pymodbus_compat import async_read_holding_registers

_LOGGER = logging.getLogger(__name__)


async def validate_connection(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    from pymodbus.client import AsyncModbusTcpClient
    
    host = data[CONF_HOST]
    port = int(data.get(CONF_PORT, DEFAULT_MODBUS_PORT))
    slave_id = int(data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID))
    device_type = data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_CHARGER)
    
    client = AsyncModbusTcpClient(
        host=host,
        port=port,
        timeout=5,
    )
    
    try:
        connected = await client.connect()
        if not connected:
            raise CannotConnect("Failed to connect to Modbus device")

        # Charger and LMC use different register maps (see const.py) -- validate
        # against a region that's actually documented for the selected device type.
        if device_type == DEVICE_TYPE_LMC:
            validation_address = REG_LMC_MEASUREMENTS_BASE
            result = await async_read_holding_registers(client, validation_address, 2, slave_id)
        else:
            validation_address = REG_CHARGER_STATE
            result = await async_read_holding_registers(client, validation_address, 1, slave_id)

        if result.isError():
            raise CannotConnect(f"Failed to read from {device_type} at address {validation_address}")

    except Exception as err:
        _LOGGER.error("Connection error: %s", err)
        raise CannotConnect(f"Connection failed: {err}") from err
    finally:
        client.close()
    
    return {"title": data.get(CONF_NAME, f"VOOL {data[CONF_DEVICE_TYPE].title()}")}


class VoolModbusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for VOOL Modbus."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - ask which VOOL device type this is."""
        if user_input is not None:
            self._data[CONF_DEVICE_TYPE] = user_input[CONF_DEVICE_TYPE]
            return await self.async_step_connection()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_DEVICE_TYPE, default=DEVICE_TYPE_CHARGER
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=DEVICE_TYPES,
                            translation_key=CONF_DEVICE_TYPE,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        ),
                    ),
                }
            ),
        )

    async def async_step_connection(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the connection configuration step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cleaned = dict(user_input)
            if CONF_PORT in cleaned and cleaned[CONF_PORT] is not None:
                cleaned[CONF_PORT] = int(cleaned[CONF_PORT])
            if CONF_SLAVE_ID in cleaned and cleaned[CONF_SLAVE_ID] is not None:
                cleaned[CONF_SLAVE_ID] = int(cleaned[CONF_SLAVE_ID])
            self._data.update(cleaned)
            
            # Check if device is already configured
            await self.async_set_unique_id(
                f"{self._data[CONF_HOST]}_{self._data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)}"
            )
            self._abort_if_unique_id_configured()

            try:
                info = await validate_connection(self.hass, self._data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Use custom name if provided, otherwise use default
                title = self._data.get(CONF_NAME) or info["title"]
                return self.async_create_entry(title=title, data=self._data)

        device_type = self._data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_CHARGER)
        default_name = f"VOOL {device_type.title()}"

        return self.async_show_form(
            step_id="connection",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
                    ),
                    vol.Optional(CONF_PORT, default=DEFAULT_MODBUS_PORT): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=247,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(CONF_NAME, default=default_name): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "device_type": self._data.get(CONF_DEVICE_TYPE, DEVICE_TYPE_CHARGER).title(),
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return VoolModbusOptionsFlowHandler()


class VoolModbusOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for VOOL Modbus."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            cleaned = dict(user_input)
            if CONF_PORT in cleaned and cleaned[CONF_PORT] is not None:
                cleaned[CONF_PORT] = int(cleaned[CONF_PORT])
            if CONF_SLAVE_ID in cleaned and cleaned[CONF_SLAVE_ID] is not None:
                cleaned[CONF_SLAVE_ID] = int(cleaned[CONF_SLAVE_ID])
            if CONF_SCAN_INTERVAL in cleaned and cleaned[CONF_SCAN_INTERVAL] is not None:
                cleaned[CONF_SCAN_INTERVAL] = int(cleaned[CONF_SCAN_INTERVAL])
            return self.async_create_entry(title="", data=cleaned)

        current_port = self.config_entry.data.get(CONF_PORT, DEFAULT_MODBUS_PORT)
        current_slave_id = self.config_entry.data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
        current_scan_interval = self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_PORT,
                        default=self.config_entry.options.get(CONF_PORT, current_port),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=65535,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_SLAVE_ID,
                        default=self.config_entry.options.get(CONF_SLAVE_ID, current_slave_id),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1,
                            max=247,
                            mode=selector.NumberSelectorMode.BOX,
                        ),
                    ),
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=5,
                            max=3600,
                            mode=selector.NumberSelectorMode.BOX,
                            unit_of_measurement="s",
                        ),
                    ),
                }
            ),
            errors=errors,
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
