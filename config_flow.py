"""Config flow for oralb ble integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class RenphoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for oralb."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, str] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick discovered device."""
        _LOGGER.warning("===1 async_step_user")
        if user_input is not None:
            _LOGGER.warning("=== user input:%s", user_input)
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=self._discovered_devices[address], data={}
            )

        current_addresses = self._async_current_ids()
        for discovery_info in async_discovered_service_info(self.hass, False):
            address = discovery_info.address
            _LOGGER.warning("=== address:%s, %s, %s", address,discovery_info.name,discovery_info.advertisement.local_name)
            if address in current_addresses or address in self._discovered_devices:
                continue
            if "100" in discovery_info.name:
                self._discovered_devices[address] = discovery_info.name
                _LOGGER.warning("Found My Device")
                _LOGGER.warning("=== Discovery address: %s", address)
                _LOGGER.warning("=== Man Data: %s", discovery_info.manufacturer_data)
                _LOGGER.warning("=== advertisement: %s", discovery_info.advertisement)
                _LOGGER.warning("=== device: %s", discovery_info.device)
                _LOGGER.warning("=== service data: %s", discovery_info.service_data)
                _LOGGER.warning("=== service uuids: %s", discovery_info.service_uuids)
                _LOGGER.warning("=== rssi: %s", discovery_info.rssi)
                _LOGGER.warning(
                    "=== advertisement: %s", discovery_info.advertisement.local_name
                )
        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {vol.Required(CONF_ADDRESS): vol.In(self._discovered_devices)}
            ),
        )
