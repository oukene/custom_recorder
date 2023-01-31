"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import decimal
from distutils.command.config import config
import random
import logging
from threading import Timer
import time
from xmlrpc.client import boolean
import homeassistant
from typing import Optional
from homeassistant.const import (
    STATE_UNKNOWN, STATE_UNAVAILABLE, ATTR_UNIT_OF_MEASUREMENT, ATTR_ICON
)

import copy
import os
import asyncio
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

from homeassistant import components
from homeassistant import util
from homeassistant.helpers.entity import Entity

from .const import *
from homeassistant.exceptions import TemplateError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity, generate_entity_id
from homeassistant.helpers.event import async_track_state_change, track_state_change
from homeassistant.components.sensor import SensorEntity

import math

_LOGGER = logging.getLogger(__name__)

# See cover.py for more details.
# Note how both entities for each roller sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.

ENTITY_ID_FORMAT = DOMAIN + ".{}"


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    hass.data[DOMAIN][config_entry.entry_id]["listener"] = []
    
    device = Device(NAME, config_entry)

    new_devices = []

    # 지정된 디렉토리의 모든 파일을 읽는다
    if os.path.isdir(DATA_DIR) == False:
        os.makedirs(DATA_DIR)


    # 디렉토리에 있는 목록으로 config 대체
    file_list = os.listdir(DATA_DIR)
    d = [None, None]
    for file in file_list:
        _LOGGER.debug(f"filename - {file}")
        f = open(DATA_DIR + file)
        lines = f.readlines()
        name = None
        source_entity = None
        record_period = None
        data = {}
        for idx, line in enumerate(lines):
            isName = None
            isSourceEntity = None
            isRecordPeriod = None
            isData = None
            isName = line.find(FIELD_NAME)
            isSourceEntity = line.find(FIELD_SOURCE_ENTITY)
            isRecordPeriodUnit = line.find(FIELD_RECORD_PERIOD_UNIT)
            isRecordPeriod = line.find(FIELD_RECORD_PERIOD)
            isOffsetUnit = line.find(FIELD_OFFSET_UNIT)
            isOffset = line.find(FIELD_OFFSET)
            isData = line.find(FIELD_DATA)
            # _LOGGER.debug(f"isName - {isName}, isOriginEntity - {isOriginEntity}, isRecordPeriod - {isRecordPeriod}")
            if isName == 0:
                name = lines[idx + 1].replace("\n", "")
            if isSourceEntity == 0:
                source_entity = lines[idx + 1].replace("\n", "")
            if isRecordPeriodUnit == 0:
                record_period_unit = lines[idx + 1].replace("\n", "")
            if isRecordPeriod == 0:
                record_period = lines[idx + 1].replace("\n", "")
            if isOffsetUnit == 0:
                offset_unit = lines[idx+1].replace("\n", "")
            if isOffset == 0:
                offset = lines[idx+1].replace("\n", "")
            if isData == 0:
                # 기록된 데이터를 모두 읽은은 후 종료
                d = lines[idx+1].replace("\n", "")
                d = d.split(",")
                #if datetime(d[0]) < datetime.now() - timedelta(days=int(record_period)):
                args = {}
                args[record_period_unit] = int(record_period)
                if datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S.%f') < datetime.now() - relativedelta(**args):
                    continue
                d[0] = d[0]
                d[1] = d[1]
                #d[1] = d[1].replace('\n', '')
                #_LOGGER.debug(f"d - {d[0]}, val - {d[1]}")
                data[str(d[0])] = d[1]

        if name != None and source_entity != None and record_period != None and offset_unit != None and offset != None and record_period_unit != None:
            #d = {'origin_entity': origin_entity,
            #        'name': name, 'record_period': record_period}
            #_LOGGER.debug(f"add entity - {d}")
            new_devices.append(
                CustomRecorder(
                    hass,
                    config_entry.entry_id,
                    device,
                    name,
                    source_entity,
                    record_period_unit,
                    record_period,
                    offset_unit,
                    offset,
                    data,
                    file,
                    d[1],
                ))
            data = sorted(data.items())
            f.close()
            f=open(DATA_DIR + file, "w")
            f.write(FIELD_NAME)
            f.write(name + "\n")
            f.write(FIELD_SOURCE_ENTITY)
            f.write(source_entity + "\n")
            f.write(FIELD_RECORD_PERIOD_UNIT)
            f.write(record_period_unit + "\n")
            f.write(FIELD_RECORD_PERIOD)
            f.write(record_period + "\n")
            f.write(FIELD_OFFSET_UNIT)
            f.write(offset_unit + "\n")
            f.write(FIELD_OFFSET)
            f.write(offset + "\n")

            for d in data:
                f.write(FIELD_DATA)
                f.write(d[0] + "," + d[1] + "\n")

        f.close()

    #if config_entry.options.get(CONF_ENTITIES) != None:
    #    for entity in config_entry.options.get(CONF_ENTITIES):
    #        new_devices.append(
    #            CustomRecorder(
    #                hass,
    #                config_entry.entry_id,
    #                device,
    #                entity[CONF_NAME],
    #                entity[CONF_ORIGIN_ENTITY],
    #                entity[CONF_RECORD_PERIOD],
    #            )
                #        )
    if new_devices:
        async_add_devices(new_devices)

class Device:
    """Dummy roller (device for HA) for Hello World example."""

    def __init__(self, name, config):
        """Init dummy roller."""
        self._id = f"{name}_{config.entry_id}"
        self._name = name
        self._callbacks = set()
        self._loop = asyncio.get_event_loop()
        # Reports if the roller is moving up or down.
        # >0 is up, <0 is down. This very much just for demonstration.

        # Some static information about this device
        self.firmware_version = VERSION
        self.model = NAME
        self.manufacturer = NAME

    @property
    def device_id(self):
        """Return ID for roller."""
        return self._id

    @property
    def name(self):
        return self._name

    def register_callback(self, callback):
        """Register callback, called when Roller changes state."""
        self._callbacks.add(callback)

    def remove_callback(self, callback):
        """Remove previously registered callback."""
        self._callbacks.discard(callback)

    # In a real implementation, this library would call it's call backs when it was
    # notified of any state changeds for the relevant device.
    async def publish_updates(self):
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

    def publish_updates(self):
        """Schedule call all registered callbacks."""
        for callback in self._callbacks:
            callback()

# This base class shows the common properties and methods for a sensor as used in this
# example. See each sensor for further details about properties and methods that
# have been overridden.


class Sensorbase(SensorEntity):
    """Base representation of a Hello World Sensor."""

    should_poll = False

    def __init__(self, device):
        """Initialize the sensor."""
        self._device = device

    # To link this entity to the cover device, this property must return an
    # identifiers value matching that used in the cover, but no other information such
    # as name. If name is returned, this entity will then also become a device in the
    # HA UI.
    @property
    def device_info(self):
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            # If desired, the name for the device could be different to the entity
            "name": self._device.name,
            "sw_version": self._device.firmware_version,
            "model": self._device.model,
            "manufacturer": self._device.manufacturer
        }

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        """Return True if roller and hub is available."""
        return True

    async def async_added_to_hass(self):
        """Run when this Entity has been added to HA."""
        # Sensors should also register callbacks to HA when their state changes
        self._device.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        """Entity being removed from hass."""
        # The opposite of async_added_to_hass. Remove any registered call backs here.
        self._device.remove_callback(self.async_write_ha_state)


class CustomRecorder(Sensorbase):
    """Representation of a Thermal Comfort Sensor."""

    def __init__(self, hass, entry_id, device, entity_name, source_entity, record_period_unit, record_period, offset_unit, offset, data, file, last_data):
        """Initialize the sensor."""
        super().__init__(device)

        self.hass = hass
        self.entry_id = entry_id
        self._source_entity = source_entity
        _LOGGER.debug(
            f"data file - {DATA_DIR + file}, last_date - {last_data}")
        
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, "{}_{}".format(NAME, entity_name), hass=hass)
        self._name = "{}".format(entity_name)
        # self._name = "{} {}".format(device.device_id, SENSOR_TYPES[sensor_type][1])
        self._unit_of_measurement = None
        self._state = last_data
        self._offset_unit = offset_unit
        self._offset = offset
        self._attributes = {}
        self._attributes["source entity id"] = source_entity
        self._attributes["record period unit"] = record_period_unit
        self._attributes["record period"] = record_period
        self._attributes["offset unit"] = offset_unit
        self._attributes["offset"] = offset
        self._attributes["data file"] = file
        self._attributes["data"] = data
        self._icon = None
        self._record_period = record_period
        self._loop = asyncio.get_event_loop()

        self._unique_id = self.entity_id
        self._device = device
        self._setup = False

        self._device.publish_updates()

        self.setup()
        #self._loop.create_task(self.setup())

    def setup(self):
        self.hass.data[DOMAIN][self.entry_id]["listener"].append(async_track_state_change(
            self.hass, self._source_entity, self.entity_listener))

        
        state = self.hass.states.get(self._source_entity)
        old_state = self.hass.states.get(self.entity_id)
        if _is_valid_state(state):
            self._loop.create_task(self.entity_listener(
                self._source_entity, old_state, state))
        #self._state = state.state

        #self._state = self.hass.states.get(self._switch_entity).state

    def entity_listener(self, entity, old_state, new_state):
        #try:
            _LOGGER.debug("call entity listener")
            if _is_valid_state(new_state):
                if self._setup == False:
                    self._unit_of_measurement = new_state.attributes.get(
                        ATTR_UNIT_OF_MEASUREMENT)
                    self._icon = new_state.attributes.get(
                        ATTR_ICON)
                    self._setup = True

                # 데이터를 파일에 저장
                # 데이터가 하나도 기록된 게 없다면 첫 데이터이므로 저장하고 아닐때는 값이 바뀔때만 저장
                _LOGGER.debug(f"old_state - {old_state}, new_state - {new_state}")
                #if (_is_valid_state(old_state) and old_state.state != new_state.state) or (len(self._attributes["data"]) <= 0 or self._state != new_state.state):
                if (len(self._attributes["data"]) <= 0 or self._state != new_state.state):
                    self._state = new_state.state
                    self.schedule_update_ha_state(True)
                    args = {}
                    args[self._offset_unit] = int(self._offset)
                    #_LOGGER.debug(f"offset unit : {self._offset_unit}, offset : {self._offset}")
                    now = datetime.now() + relativedelta(**args)
                    str_now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
                    self._attributes["data"][str_now] = self._state
                    data = "[data]\n" + str_now + ',' + self._state + "\n"
                    #_LOGGER.debug(f"data - {data}")
                    fp = open(DATA_DIR + self._attributes["data file"], "a")
                    fp.write(data)
                    fp.close()
                #_LOGGER.debug("call switch_entity_listener, old state : %s, new_state : %s",
                #          old_state, new_state.state)  

        #except Exception as e:
        #    _LOGGER.error(f"catch error - {e}")

    """Sensor Properties"""
    @property
    def has_entity_name(self) -> bool:
        return True

    @property
    def unit_of_measurement(self):
        """Return the unit_of_measurement of the device."""
        return self._unit_of_measurement
    
    @property
    def icon(self) -> str | None:
        return self._icon

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        return self._attributes

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        # return self._state
        return self._state

    # @property
    # def device_class(self) -> Optional[str]:
    #    """Return the device class of the sensor."""
    #    return self._device_class
    # @property
    # def entity_picture(self):
    #    """Return the entity_picture to use in the frontend, if any."""
    #    return self._entity_picture
    # @property
    # def unit_of_measurement(self):
    #    """Return the unit_of_measurement of the device."""
    #    return self._unit_of_measurement
    # @property
    # def should_poll(self):
    #    """No polling needed."""
    #    return False
    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        if self._unique_id is not None:
            return self._unique_id

    def update(self):
        """Update the state."""


def _is_valid_state(state) -> bool:
    return state and state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE
