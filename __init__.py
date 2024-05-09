"""The Xiaomi Bluetooth integration."""

from __future__ import annotations

import logging
from typing import cast

from xiaomi_ble import EncryptionScheme, SensorUpdate, XiaomiBluetoothDeviceData

from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    DOMAIN as BLUETOOTH_DOMAIN,
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import CoreState, HomeAssistant
from homeassistant.helpers.device_registry import (
    CONNECTION_BLUETOOTH,
    DeviceRegistry,
    async_get,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    CONF_DISCOVERED_EVENT_CLASSES,
    CONF_SLEEPY_DEVICE,
    DOMAIN,
    XIAOMI_BLE_EVENT,
    XiaomiBleEvent,
)
# from .coordinator import XiaomiActiveBluetoothProcessorCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.EVENT, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.warning("*** async_setup_entry:%s", entry)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
