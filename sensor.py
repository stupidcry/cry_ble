"""Support for xiaomi ble sensors."""

from __future__ import annotations

import logging

from sensor_state_data import (
    DeviceClass,
    DeviceKey,
    SensorDescription,
    SensorDeviceInfo,
    SensorUpdate,
    SensorValue,
    Units,
)

from homeassistant import config_entries
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_MILLIGRAMS_PER_CUBIC_METER,
    CONDUCTIVITY,
    LIGHT_LUX,
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfMass,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from .const import DOMAIN
from .device import device_key_to_bluetooth_entity_key
from .QingActiveBluetoothProcessorCoordinator import (
    QingActiveBluetoothProcessorCoordinator,
    QingPassiveBluetoothDataProcessor,
)

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS = {
    (DeviceClass.BATTERY, Units.PERCENTAGE): SensorEntityDescription(
        key=f"{DeviceClass.BATTERY}_{Units.PERCENTAGE}",
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    (DeviceClass.HUMIDITY, Units.PERCENTAGE): SensorEntityDescription(
        key=f"{DeviceClass.HUMIDITY}_{Units.PERCENTAGE}",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (DeviceClass.TEMPERATURE, Units.TEMP_CELSIUS): SensorEntityDescription(
        key=f"{DeviceClass.TEMPERATURE}_{Units.TEMP_CELSIUS}",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
}


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""
    _LOGGER.warning("***+++ sensor_update_to_bluetooth_data_update:%s", sensor_update)

    return PassiveBluetoothDataUpdate(
        # (title=None, anufacturer=None, sw_version='123456', hw_version=None)},
        # devices={None: SensorDeviceInfo(name=None, model=None, manufacturer=None, sw_version='123456', hw_version=None)}
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        # entity_descriptions={DeviceKey(key='battery', device_id=None): SensorDescription(device_key=DeviceKey(key='battery', device_id=None), device_class=<SensorDeviceClass.BATTERY: 'battery'>, native_unit_of_measurement=<Units.PERCENTAGE: '%'>)},
        entity_descriptions={
            device_key_to_bluetooth_entity_key(device_key): SENSOR_DESCRIPTIONS[
                (description.device_class, description.native_unit_of_measurement)
            ]
            for device_key, description in sensor_update.entity_descriptions.items()
            if description.device_class
        },
        entity_data={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
        # entity_values={DeviceKey(key='battery', device_id=None): SensorValue(device_key=DeviceKey(key='battery', device_id=None), name='Battery', native_value=99)}
        entity_names={
            device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
        # devices={
        #     device_id: sensor_device_info_to_hass_device_info(device_info)
        #     for device_id, device_info in sensor_update.devices.items()
        # },
        # entity_descriptions={
        #     device_key_to_bluetooth_entity_key(device_key): SENSOR_DESCRIPTIONS[
        #         (description.device_class, description.native_unit_of_measurement)
        #     ]
        #     for device_key, description in sensor_update.entity_descriptions.items()
        #     if description.device_class
        # },
        # entity_data={
        #     device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
        #     for device_key, sensor_values in sensor_update.entity_values.items()
        # },
        # entity_names={
        #     device_key_to_bluetooth_entity_key(device_key): sensor_values.name
        #     for device_key, sensor_values in sensor_update.entity_values.items()
        # },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Xiaomi BLE sensors."""
    _LOGGER.warning("*** sensor async_setup_entry:%s", entry)
    coordinator: QingActiveBluetoothProcessorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    processor = QingPassiveBluetoothDataProcessor(
        sensor_update_to_bluetooth_data_update
    )
    entry.async_on_unload(
        processor.async_add_entities_listener(
            QingBluetoothSensorEntity, async_add_entities
        )
    )
    entry.async_on_unload(
        coordinator.async_register_processor(processor, SensorEntityDescription)
    )


class QingBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[QingPassiveBluetoothDataProcessor],
    SensorEntity,
):
    """Representation of a xiaomi ble sensor."""

    @property
    def native_value(self) -> int | float | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self.processor.coordinator.sleepy_device or super().available
