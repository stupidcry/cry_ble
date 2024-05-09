"""Parser for OralB BLE advertisements.

This file is shamelessly copied from the following repository:
https://github.com/Ernst79/bleparser/blob/c42ae922e1abed2720c7fac993777e1bd59c0c93/package/bleparser/oral_b.py

MIT License applies.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
import logging
import time

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
        super().__init__()

    def _start_update(self, service_info: BluetoothServiceInfo) -> None:
        _LOGGER.waring("===*** _start_update")

    def poll_needed(
        self, service_info: BluetoothServiceInfo, last_poll: float | None
    ) -> bool:
        _LOGGER.waring("=== poll_needed")
        return True

    @retry_bluetooth_connection_error()
    async def _get_payload(self, client: BleakClientWithServiceCache) -> None:
        _LOGGER.waring("=== _get_payload")

    async def async_poll(self, ble_device: BLEDevice) -> SensorUpdate:
        _LOGGER.waring("=== Polling device: %s", ble_device.address)
        client = await establish_connection(
            BleakClientWithServiceCache, ble_device, ble_device.address
        )
        try:
            await self._get_payload(client)
        except BleakError as err:
            _LOGGER.waring(f"Reading gatt characters failed with err: {err}")
        finally:
            await client.disconnect()
            _LOGGER.debug("Disconnected from active bluetooth client")
        return self._finish_update()
