"""The Xiaomi Bluetooth integration."""

from __future__ import annotations

import logging
from typing import cast

from home_assistant_bluetooth import BluetoothServiceInfo
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
from .QingActiveBluetoothProcessorCoordinator import (
    QingActiveBluetoothProcessorCoordinator,
)

# from .coordinator import XiaomiActiveBluetoothProcessorCoordinator
from .QingBluetoothDeviceData import QingBluetoothDeviceData

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.warning("*** async_setup_entry:%s", entry)
    address = entry.unique_id
    assert address is not None

    data = QingBluetoothDeviceData()

    def _needs_poll(
        service_info: BluetoothServiceInfoBleak, last_poll: float | None
    ) -> bool:
        # Only poll if hass is running, we need to poll,
        # and we actually have a way to connect to the device
        return (
            hass.state is CoreState.running
            and data.poll_needed(service_info, last_poll)
            and bool(
                async_ble_device_from_address(
                    hass, service_info.device.address, connectable=True
                )
            )
        )

    async def _async_poll(service_info: BluetoothServiceInfoBleak) -> SensorUpdate:
        # BluetoothServiceInfoBleak is defined in HA, otherwise would just pass it
        # directly to the Xiaomi code
        # Make sure the device we have is one that we can connect with
        # in case its coming from a passive scanner
        if service_info.connectable:
            connectable_device = service_info.device
        elif device := async_ble_device_from_address(
            hass, service_info.device.address, True
        ):
            connectable_device = device
        else:
            # We have no bluetooth controller that is in range of
            # the device to poll it
            raise RuntimeError(
                f"No connectable device found for {service_info.device.address}"
            )
        return await data.async_poll(connectable_device)

    async def _update(service_info: BluetoothServiceInfo) -> SensorUpdate:
        _LOGGER.warning("*** _update:%s", data)
        return SensorUpdate()

    coordinator = hass.data.setdefault(DOMAIN, {})[entry.entry_id] = (
        QingActiveBluetoothProcessorCoordinator(
            hass,
            _LOGGER,
            address=address,
            mode=BluetoothScanningMode.PASSIVE,
            update_method=_update,
            needs_poll_method=_needs_poll,
            device_data=data,
            discovered_event_classes=set(
                entry.data.get(CONF_DISCOVERED_EVENT_CLASSES, [])
            ),
            poll_method=_async_poll,
            # We will take advertisements from non-connectable devices
            # since we will trade the BLEDevice for a connectable one
            # if we need to poll it
            connectable=False,
            entry=entry,
        )
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(
        coordinator.async_start()
    )  # only start after all platforms have had a chance to subscribe
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
