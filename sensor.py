"""Support for OralB sensors."""

from __future__ import annotations

from oralb_ble import OralBSensor, SensorUpdate

from homeassistant import config_entries
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothProcessorCoordinator,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from .const import DOMAIN

SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    OralBSensor.TIME: SensorEntityDescription(
        key=OralBSensor.TIME,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfTime.SECONDS,
    ),
    OralBSensor.SECTOR: SensorEntityDescription(
        key=OralBSensor.SECTOR,
        translation_key="sector",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OralBSensor.NUMBER_OF_SECTORS: SensorEntityDescription(
        key=OralBSensor.NUMBER_OF_SECTORS,
        translation_key="number_of_sectors",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OralBSensor.SECTOR_TIMER: SensorEntityDescription(
        key=OralBSensor.SECTOR_TIMER,
        translation_key="sector_timer",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    OralBSensor.TOOTHBRUSH_STATE: SensorEntityDescription(
        key=OralBSensor.TOOTHBRUSH_STATE,
        name=None,
    ),
    OralBSensor.PRESSURE: SensorEntityDescription(
        key=OralBSensor.PRESSURE,
        translation_key="pressure",
    ),
    OralBSensor.MODE: SensorEntityDescription(
        key=OralBSensor.MODE,
        translation_key="mode",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    OralBSensor.SIGNAL_STRENGTH: SensorEntityDescription(
        key=OralBSensor.SIGNAL_STRENGTH,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=False,
    ),
    OralBSensor.BATTERY_PERCENT: SensorEntityDescription(
        key=OralBSensor.BATTERY_PERCENT,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
}

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the OralB BLE sensors."""
    coordinator: PassiveBluetoothProcessorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    _LOGGER.warn("============sensor async_setup_entry")


class OralBBluetoothSensorEntity(
    PassiveBluetoothProcessorEntity[PassiveBluetoothDataProcessor[str | int | None]],
    SensorEntity,
):
    """Representation of a OralB sensor."""

    @property
    def native_value(self) -> str | int | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)

    @property
    def available(self) -> bool:
        """Return True if entity is available.

        The sensor is only created when the device is seen.

        Since these are sleepy devices which stop broadcasting
        when not in use, we can't rely on the last update time
        so once we have seen the device we always return True.
        """
        return True

    @property
    def assumed_state(self) -> bool:
        """Return True if the device is no longer broadcasting."""
        return not self.processor.available
