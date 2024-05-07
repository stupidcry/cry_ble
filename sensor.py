"""Support for rd200 ble sensors."""

from __future__ import annotations

import logging
import dataclasses

from .RenphoBluetoothDeviceData import RenphoDevice

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_BILLION,
    CONCENTRATION_PARTS_PER_MILLION,
    LIGHT_LUX,
    PERCENTAGE,
    UnitOfPressure,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util.unit_system import METRIC_SYSTEM

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSORS_MAPPING_TEMPLATE: dict[str, SensorEntityDescription] = {
    "weight": SensorEntityDescription(
        key="weight",
        device_class=SensorDeviceClass.WEIGHT,
        native_unit_of_measurement="g",
        name="Weight",
    )
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Renpho BLE sensors."""

    coordinator: DataUpdateCoordinator[RenphoDevice] = hass.data[DOMAIN][entry.entry_id]

    # we need to change some units
    sensors_mapping = SENSORS_MAPPING_TEMPLATE.copy()

    entities = []
    _LOGGER.info("=== got sensors: %s", coordinator.data.sensors)
    for sensor_type, sensor_value in coordinator.data.sensors.items():
        if sensor_type not in sensors_mapping:
            _LOGGER.debug(
                "Unknown sensor type detected: %s, %s",
                sensor_type,
                sensor_value,
            )
            continue
        entities.append(
            WeightSensor(coordinator, coordinator.data, sensors_mapping[sensor_type])
        )

    async_add_entities(entities)


class WeightSensor(
    CoordinatorEntity[DataUpdateCoordinator[RenphoDevice]], SensorEntity
):
    """RD200 BLE sensors for the device."""

    ## Setting the Device State to None fixes Uptime String, Appears to override line: https://github.com/Makr91/rd200v2/blob/3d87d6e005f5efb7c143ff32256153c517ccade9/custom_components/rd200_ble/sensor.py#L78
    # Had to comment this line out to avoid it setting all state_class to none
    # _attr_state_class = None
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        rd200_device: RenphoDevice,
        entity_description: SensorEntityDescription,
    ) -> None:
        """Populate the rd200 entity with relevant data."""
        super().__init__(coordinator)
        self.entity_description = entity_description

        name = f"{rd200_device.name} {rd200_device.identifier}"
        _LOGGER.info(f"=== name:{name}")

        self._attr_unique_id = f"{name}_{entity_description.key}"

        self._id = rd200_device.address
        self._attr_device_info = DeviceInfo(
            connections={
                (
                    CONNECTION_BLUETOOTH,
                    rd200_device.address,
                )
            },
            name=name,
            manufacturer="CRY Co., LTD.",
            model="PG-XXX",
            hw_version=rd200_device.hw_version,
            sw_version=rd200_device.sw_version,
        )

    @property
    def native_value(self) -> StateType:
        """Return the value reported by the sensor."""
        try:
            return self.coordinator.data.sensors[self.entity_description.key]
        except KeyError:
            return None
