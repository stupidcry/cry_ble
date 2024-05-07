"""Parser for OralB BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/oral_b.py

MIT License applies.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from enum import Enum, auto

from bleak import BleakError, BLEDevice
from bleak_retry_connector import (
    BleakClientWithServiceCache,
    establish_connection,
    retry_bluetooth_connection_error,
)
from bluetooth_data_tools import short_address
from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import SensorDeviceClass, SensorUpdate, Units
from sensor_state_data.enum import StrEnum


_LOGGER = logging.getLogger(__name__)


class RenphoBluetoothDeviceData(BluetoothData):
    """Data for OralB BLE sensors."""

    def __init__(self) -> None:
        _LOGGER.warn("=======RenphoBluetoothDeviceData init")
        super().__init__()

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        """Update from BLE advertisement data."""
        _LOGGER.warn(
            "======_start_update Parsing OralB BLE advertisement data: %s", service_info
        )

    def poll_needed(
        self, service_info: BluetoothServiceInfo, last_poll: float | None
    ) -> bool:
        """
        This is called every time we get a service_info for a device. It means the
        device is working and online.
        """
        _LOGGER.warn("=======poll_needed")
        return True

    @retry_bluetooth_connection_error()
    async def _get_payload(self, client: BleakClientWithServiceCache) -> None:
        """Get the payload from the brush using its gatt_characteristics."""
        _LOGGER.warn(f"_get_payload {client.services}")
        ######## debug
        discovery_info_attributes = dir(client.services)
        for attr_name in discovery_info_attributes:
            attr_value = getattr(client.services, attr_name)
            _LOGGER.warn(f"{attr_name}: {attr_value}")
        ######## debug
        battery_char = client.services.get_characteristic("1A12")
        _LOGGER.warn(f"Successfully read active gatt characters{battery_char}")

    async def async_poll(self, ble_device: BLEDevice) -> SensorUpdate:
        """
        Poll the device to retrieve any values we can't get from passive listening.
        """
        _LOGGER.warn("Polling Renpho device: %s", ble_device.address)
        client = await establish_connection(
            BleakClientWithServiceCache, ble_device, ble_device.address
        )
        try:
            await self._get_payload(client)
        except BleakError as err:
            _LOGGER.warning(f"Reading gatt characters failed with err: {err}")
        finally:
            await client.disconnect()
            _LOGGER.debug("Disconnected from active bluetooth client")
        return self._finish_update()
