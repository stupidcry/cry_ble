"""The OralB integration."""

from __future__ import annotations

import logging

from oralb_ble import OralBBluetoothDeviceData, SensorUpdate

from homeassistant.components.bluetooth import (
    BluetoothScanningMode,
    BluetoothServiceInfoBleak,
    async_ble_device_from_address,
)
from homeassistant.components.bluetooth.active_update_processor import (
    ActiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import CoreState, HomeAssistant

from .const import DOMAIN
from .RenphoBluetoothDeviceData import RenphoBluetoothDeviceData

from homeassistant.components import bluetooth
from bleak_retry_connector import close_stale_connections_by_address
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from datetime import timedelta
import time


PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Renpho BLE device from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    address = entry.unique_id
    assert address is not None
    await close_stale_connections_by_address(address)

    ble_device = bluetooth.async_ble_device_from_address(hass, address)
    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find RD200 device with address {address}")

    # async def _async_update_method() -> RenphoBluetoothDeviceData:
    #     """Get data from RD200 BLE."""
    #     start = time.time()
    #     ble_device = bluetooth.async_ble_device_from_address(hass, address)
    #     renpho = RenphoBluetoothDeviceData(_LOGGER)
    #     try:
    #         data = await renpho.update_device(ble_device)
    #     except Exception as err:
    #         raise UpdateFailed(f"Unable to fetch data: {err}") from err
    #     _LOGGER.warn(f"=== _async_update_method time:{time.time()-start}")  # noqa: G004
    #     return data

    # coordinator = DataUpdateCoordinator(
    #     hass,
    #     _LOGGER,
    #     name=DOMAIN,
    #     update_method=_async_update_method,
    #     update_interval=timedelta(seconds=1),
    # )
    renpho = RenphoBluetoothDeviceData(_LOGGER)

    def _needs_poll(
        service_info: BluetoothServiceInfoBleak, last_poll: float | None
    ) -> bool:
        return (
            hass.state is CoreState.running
            and renpho.poll_needed(service_info, last_poll)
            and bool(
                async_ble_device_from_address(
                    hass, service_info.device.address, connectable=True
                )
            )
        )

    async def _async_poll(service_info: BluetoothServiceInfoBleak) -> SensorUpdate:
        _LOGGER.warning("============== start poll:%s", service_info.connectable)
        if service_info.connectable:
            connectable_device = service_info.device
        elif device := async_ble_device_from_address(
            hass, service_info.device.address, True
        ):
            connectable_device = device
        else:
            raise RuntimeError(
                f"No connectable device found for {service_info.device.address}"
            )
        _LOGGER.warning("============== start poll:%s", connectable_device)
        return await renpho.async_poll(connectable_device)

    coordinator = ActiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=renpho.update,
        needs_poll_method=_needs_poll,
        poll_method=_async_poll,
        # We will take advertisements from non-connectable devices
        # since we will trade the BLEDevice for a connectable one
        # if we need to poll it
        connectable=False,
    )

    await coordinator.async_config_entry_first_refresh()
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

    # data = RenphoBluetoothDeviceData()

    # def _needs_poll(
    #     service_info: BluetoothServiceInfoBleak, last_poll: float | None
    # ) -> bool:
    #     # Only poll if hass is running, we need to poll,
    #     # and we actually have a way to connect to the device
    #     _LOGGER.warn(f"need pool: {hass.state} {data.poll_needed(service_info, last_poll)} {async_ble_device_from_address(
    #                 hass, service_info.device.address, connectable=True
    #             )}  {(
    #         hass.state is CoreState.running
    #         and data.poll_needed(service_info, last_poll)
    #         and bool(
    #             async_ble_device_from_address(
    #                 hass, service_info.device.address, connectable=True
    #             )
    #         )
    #     )}")
    #     return (
    #         hass.state is CoreState.running
    #         and data.poll_needed(service_info, last_poll)
    #         and bool(
    #             async_ble_device_from_address(
    #                 hass, service_info.device.address, connectable=True
    #             )
    #         )
    #     )

    # async def _async_poll(service_info: BluetoothServiceInfoBleak) -> SensorUpdate:
    #     # BluetoothServiceInfoBleak is defined in HA, otherwise would just pass it
    #     # directly to the oralb code
    #     # Make sure the device we have is one that we can connect with
    #     # in case its coming from a passive scanner
    #     _LOGGER.warn(f"============== start poll:{service_info.connectable}")
    #     if service_info.connectable:
    #         connectable_device = service_info.device
    #     elif device := async_ble_device_from_address(
    #         hass, service_info.device.address, True
    #     ):
    #         connectable_device = device
    #     else:
    #         # We have no bluetooth controller that is in range of
    #         # the device to poll it
    #         raise RuntimeError(
    #             f"No connectable device found for {service_info.device.address}"
    #         )
    #     _LOGGER.warn(f"============== start poll:{connectable_device}")
    #     return await data.async_poll(connectable_device)

    # coordinator = hass.data.setdefault(DOMAIN, {})[entry.entry_id] = (
    #     ActiveBluetoothProcessorCoordinator(
    #         hass,
    #         _LOGGER,
    #         address=address,
    #         mode=BluetoothScanningMode.PASSIVE,
    #         update_method=data.update,
    #         needs_poll_method=_needs_poll,
    #         poll_method=_async_poll,
    #         # We will take advertisements from non-connectable devices
    #         # since we will trade the BLEDevice for a connectable one
    #         # if we need to poll it
    #         connectable=False,
    #     )
    # )
    # _LOGGER.warn("==========before forward")
    # await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # entry.async_on_unload(
    #     coordinator.async_start()
    # )  # only start after all platforms have had a chance to subscribe
    # return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.warn(f"=== async_unload_entry:{entry}")  # noqa: G004
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
