from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from bleak.backends.device import BLEDevice
from sensor_state_data import (
    BinarySensorDeviceClass,
    SensorLibrary,
    SensorUpdate,
    Units,
)
from bleak_retry_connector import establish_connection
from bleak import BleakClient
import logging

_LOGGER = logging.getLogger(__name__)


class QingBluetoothDeviceData(BluetoothData):
    def __init__(self, bindkey: bytes | None = None) -> None:
        super().__init__()

    def poll_needed(
        self, service_info: BluetoothServiceInfo, last_poll: float | None
    ) -> bool:
        _LOGGER.warning("*** poll_needed")
        return True

    async def async_poll(self, ble_device: BLEDevice) -> SensorUpdate:
        """
        Poll the device to retrieve any values we can't get from passive listening.
        """
        _LOGGER.warning("*** async_poll")
        # if self.device_id == 0x0098:
        #     client = await establish_connection(
        #         BleakClient, ble_device, ble_device.address
        #     )
        #     try:
        #         battery_char = client.services.get_characteristic(
        #             CHARACTERISTIC_BATTERY
        #         )
        #         payload = await client.read_gatt_char(battery_char)
        #     finally:
        #         await client.disconnect()

        #     self.set_device_sw_version(payload[2:].decode("utf-8"))
        #     self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, payload[0])
        self.set_device_sw_version("123456")
        self.update_predefined_sensor(SensorLibrary.BATTERY__PERCENTAGE, 99)
        return self._finish_update()

    def update(self, data: BluetoothServiceInfo) -> SensorUpdate:
        """Update a device."""
        # Ensure events from previous
        # updates are not carried over
        # as events are transient.
        _LOGGER.warning("*** update")
        self._events_updates.clear()
        self._start_update(data)
        self.update_signal_strength(data.rssi)
        return self._finish_update()
