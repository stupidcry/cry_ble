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

from bleak import BleakError, BLEDevice, BleakGATTCharacteristic
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

import dataclasses
from bleak import BleakClient, BleakError
import asyncio
from logging import Logger
from typing import Any, Callable, Tuple, TypeVar, cast
import random
import time

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class RenphoDevice:
    """Response data with information about the RenphoDevice"""

    hw_version: str = ""
    sw_version: str = ""
    name: str = ""
    identifier: str = ""
    address: str = ""
    sensors: dict[str, str | float | None] = dataclasses.field(
        default_factory=lambda: {}
    )


class RenphoBluetoothDeviceData(BluetoothData):
    """Data for RD200 BLE sensors."""

    _event: asyncio.Event | None
    _command_data: bytearray | None

    def __init__(self, logger: Logger):
        super().__init__()
        self.logger = logger
        self._command_data = None
        self._event = None

    def notification_handler(self, _: Any, data: bytearray) -> None:
        """Helper for command events"""
        self._command_data = data

        if self._event is None:
            return
        self._event.set()

    async def _get_renpho_data(
        self, client: BleakClient, device: RenphoDevice
    ) -> RenphoDevice:
        self._event = asyncio.Event()
        self.logger.info("=== _get_renpho_data")
        try:
            await client.start_notify(
                "00001a12-0000-1000-8000-00805f9b34fb", self.notification_handler
            )
        except:
            self.logger.warn("_get_radon_uptime Bleak error 1")

        try:
            await asyncio.wait_for(self._event.wait(), 5)
        except asyncio.TimeoutError:
            self.logger.warn("Timeout getting command data.")
        except:
            self.logger.warn("_get_radon_uptime Bleak error 2")

        await client.stop_notify("00001a12-0000-1000-8000-00805f9b34fb")
        self.logger.info(f"=== _get_renpho_data: {self._command_data}")
        device.sensors["weight"] = random.randint(1, 100)
        self._command_data = None
        return device

    async def update_device(self, ble_device: BLEDevice) -> RenphoDevice:
        """Connects to the device through BLE and retrieves relevant data"""
        start = time.time()
        client = await establish_connection(BleakClient, ble_device, ble_device.address)
        _LOGGER.warn(f"=== establish_connection{time.time()-start}")  # noqa: G004
        device = RenphoDevice()
        device.name = ble_device.name
        device.address = ble_device.address

        device = await self._get_renpho_data(client, device)
        await client.disconnect()
        _LOGGER.warn(f"=== update_device disconnect: {time.time()-start}")  # noqa: G004
        return device

    def poll_needed(
        self, service_info: BluetoothServiceInfo, last_poll: float | None
    ) -> bool:
        if last_poll is None:
            return True
        return True

    async def async_poll(self, ble_device: BLEDevice) -> SensorUpdate:
        _LOGGER.debug("Polling Oral-B device: %s", ble_device.address)
        client = await establish_connection(
            BleakClientWithServiceCache, ble_device, ble_device.address
        )
        try:
            # await self._get_payload(client)
            _LOGGER.warning(f"======= get payload....")
        except BleakError as err:
            _LOGGER.warning(f"Reading gatt characters failed with err: {err}")
        finally:
            await client.disconnect()
            _LOGGER.debug("Disconnected from active bluetooth client")
        return self._finish_update()
