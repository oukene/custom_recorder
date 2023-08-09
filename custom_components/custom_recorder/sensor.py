"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import logging
from homeassistant.const import (
    STATE_UNKNOWN, STATE_UNAVAILABLE, ATTR_UNIT_OF_MEASUREMENT, ATTR_ICON
)

import time
import numpy
import os
import asyncio
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from .const import *
from homeassistant.helpers.entity import generate_entity_id
from homeassistant.helpers.event import async_track_state_change
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

# See cover.py for more details.
# Note how both entities for each roller sensor (battry and illuminance) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.

ENTITY_ID_FORMAT = DOMAIN + ".{}"

def isNumber(s):
    try:
        if s != None:
            float(s)
            return True
        else:
            return False
    except ValueError:
        return False


async def async_setup_entry(hass, config_entry, async_add_devices):
    """Add sensors for passed config_entry in HA."""

    hass.data[DOMAIN][config_entry.entry_id]["listener"] = []
    
    device = Device(NAME, config_entry)

    new_devices = []
    tmp_devices = []

    # 지정된 디렉토리의 모든 파일을 읽는다
    if os.path.isdir(DATA_DIR) == False:
        os.makedirs(DATA_DIR)

    
    # 디렉토리에 있는 목록으로 config 대체
    file_list = os.listdir(DATA_DIR)
    for file in file_list:
        d = [None, None]
        _LOGGER.debug(f"filename - {file}")
        with open(DATA_DIR + file) as fp:
            lines = fp.readlines()
            _LOGGER.debug("lines : %s", lines)
            name = None
            source_entity = None
            source_entity_attr = None
            record_period = None
            data = {}
            record_limit_count = DEFAULT_LIMIT_COUNT
            for idx, line in enumerate(lines):
                isName = None
                isSourceEntity = None
                isRecordPeriod = None
                isData = None
                isName = line.find(FIELD_NAME)
                isSourceEntity = line.find(FIELD_SOURCE_ENTITY)
                isSourceEntityAttr = line.find(FIELD_SOURCE_ENTITY_ATTR)
                isRecordPeriodUnit = line.find(FIELD_RECORD_PERIOD_UNIT)
                isRecordPeriod = line.find(FIELD_RECORD_PERIOD)
                isOffsetUnit = line.find(FIELD_OFFSET_UNIT)
                isOffset = line.find(FIELD_OFFSET)
                isData = line.find(FIELD_DATA)
                isRecordLimitCount = line.find(FIELD_RECORD_LIMIT_COUNT)
                # _LOGGER.debug(f"isName - {isName}, isOriginEntity - {isOriginEntity}, isRecordPeriod - {isRecordPeriod}")
                if isName == 0:
                    name = lines[idx + 1].replace("\n", "")
                if isSourceEntity == 0:
                    source_entity = lines[idx + 1].replace("\n", "")
                if isSourceEntityAttr == 0:
                    source_entity_attr = lines[idx + 1].replace("\n", "")
                    if source_entity_attr == "None":
                        source_entity_attr = None
                if isRecordPeriodUnit == 0:
                    record_period_unit = lines[idx + 1].replace("\n", "")
                if isRecordPeriod == 0:
                    record_period = lines[idx + 1].replace("\n", "")
                if isOffsetUnit == 0:
                    offset_unit = lines[idx+1].replace("\n", "")
                if isOffset == 0:
                    offset = lines[idx+1].replace("\n", "")
                if isRecordLimitCount == 0:
                    record_limit_count = lines[idx+1].replace("\n", "")
                if isData == 0:
                    # 기록된 데이터를 모두 읽은 후 종료
                    d = lines[idx+1].replace("\n", "")
                    d = d.split(",")
                    #if datetime(d[0]) < datetime.now() - timedelta(days=int(record_period)):
                    args = {}
                    offset_args = {}
                    args[record_period_unit] = int(record_period)
                    # offset 설정만큼 보정
                    offset_args[offset_unit] = int(offset)
                    if datetime.strptime(d[0], '%Y-%m-%d %H:%M:%S.%f') < datetime.now() - relativedelta(**args) - relativedelta(**offset_args):
                        continue
                    #d[0] = d[0]
                    d[1] = float(d[1]) if isNumber(d[1]) else d[1]
                    #d[1] = d[1].replace('\n', '')
                    #_LOGGER.debug(f"d - {d[0]}, val - {d[1]}")
                    _LOGGER.debug("데이터 추가 : " + str(d))
                    data[str(d[0])] = d[1]

            tmp = {}
            # record limit count 체크
            _LOGGER.debug("data size : %d", len(data))
            for key in sorted(data.keys(), reverse=True):
                _LOGGER.debug("len : %d, limitCount : %d", len(tmp), int(record_limit_count))
                if len(tmp) <= int(record_limit_count) - 1:
                    tmp[key] = data[key]
                else:
                    break

            data = dict(sorted(tmp.items()))

            _LOGGER.debug("데이터 사이즈 : %d", len(data))
            if source_entity != None and record_period != None and offset_unit != None and offset != None and record_period_unit != None and record_limit_count != None:
                #d = {'origin_entity': origin_entity,
                #        'name': name, 'record_period': record_period}
                #_LOGGER.debug(f"add entity - {d}")

                tmp_devices.append(
                    (
                        hass,
                        config_entry.entry_id,
                        device,
                        name,
                        source_entity,
                        source_entity_attr,
                        record_period_unit,
                        record_period,
                        offset_unit,
                        offset,
                        record_limit_count,
                        data,
                        file,
                        [d[0], d[1]],
                    ))
                #data = sorted(data.items())
                #f1.close()
                with open(DATA_DIR + file, "w") as fp2:
                    fp2.write(FIELD_NAME)
                    fp2.write(str(name) + "\n")
                    fp2.write(FIELD_SOURCE_ENTITY)
                    fp2.write(source_entity + "\n")
                    fp2.write(FIELD_SOURCE_ENTITY_ATTR)
                    fp2.write(str(source_entity_attr) + "\n")
                    fp2.write(FIELD_RECORD_PERIOD_UNIT)
                    fp2.write(record_period_unit + "\n")
                    fp2.write(FIELD_RECORD_PERIOD)
                    fp2.write(record_period + "\n")
                    fp2.write(FIELD_OFFSET_UNIT)
                    fp2.write(offset_unit + "\n")
                    fp2.write(FIELD_OFFSET)
                    fp2.write(offset + "\n")
                    fp2.write(FIELD_RECORD_LIMIT_COUNT)
                    fp2.write(str(record_limit_count) + "\n")

                    for d in data.keys():
                        fp2.write(FIELD_DATA)
                        fp2.write(d + "," + str(data[d]) + "\n")

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
    for device in tmp_devices:
        new_devices.append(
            CustomRecorder(
                device[0],
                device[1],
                device[2],
                device[3],
                device[4],
                device[5],
                device[6],
                device[7],
                device[8],
                device[9],
                device[10],
                device[11],
                device[12],
                device[13],
            ))
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

    def __init__(self, hass, entry_id, device, entity_name, source_entity, source_entity_attr, record_period_unit, record_period, offset_unit, offset, record_limit_count, data, file, last_data):
        """Initialize the sensor."""
        super().__init__(device)

        self.hass = hass
        self.entry_id = entry_id
        self._source_entity = source_entity
        self._source_entity_attr = source_entity_attr
        _LOGGER.debug(
            f"data file - {DATA_DIR + file}, last_date - {last_data}")
        
        self.entity_id = generate_entity_id(
            ENTITY_ID_FORMAT, "{}_{}".format(NAME, entity_name), hass=hass)
        self._name = "{}".format(entity_name)
        # self._name = "{} {}".format(device.device_id, SENSOR_TYPES[sensor_type][1])
        self._unit_of_measurement = None
        self._state = last_data[1]
        self._offset_unit = offset_unit
        self._offset = offset
        self._attributes = {}
        self._attributes[CONF_SOURCE_ENTITY] = source_entity
        self._attributes[CONF_SOURCE_ENTITY_ATTR] = source_entity_attr
        self._attributes[CONF_RECORD_PERIOD_UNIT] = record_period_unit
        self._attributes[CONF_RECORD_PERIOD] = record_period
        self._attributes[CONF_OFFSET_UNIT] = offset_unit
        self._attributes[CONF_OFFSET] = offset
        self._attributes[CONF_RECORD_LIMIT_COUNT] = record_limit_count
        self._attributes["data_file"] = file
        #for key in STATISTICS_TYPE:
        #    self._attributes[key] = None
        self.calc_statistics(data)
        self._attributes["last_update_time"] = last_data[0]
        self._attributes["data"] = data
        self._icon = None
        self._record_period_unit = record_period_unit
        self._record_period = record_period
        self._loop = asyncio.get_event_loop()

        self._unique_id = self.entity_id
        self._device = device
        self._setup = False

        self._device.publish_updates()

        self.setup()
        #self._loop.create_task(self.setup())

    #async def async_added_to_hass(self):
    #    old_state = await self.async_get_last_sensor_data()
    #    if old_state != None:
    #        self._state = old_state.native_value
    #        _LOGGER.debug(f"old_state.state - {old_state.native_value}")
    #
    #    self._device.register_callback(self.async_write_ha_state)


    def calc_statistics(self, data):
        # 통계 계산
        if isNumber(self._state) and len(data) > 0:
            for key in STATISTICS_TYPE:
                if key == "quantile_25":
                    self._attributes[key] = STATISTICS_TYPE[key](list(data.values()), 0.25)
                elif key == "quantile_50":
                    self._attributes[key] = STATISTICS_TYPE[key](list(data.values()), 0.5)
                elif key == "quantile_75":
                    self._attributes[key] = STATISTICS_TYPE[key](list(data.values()), 0.75)
                else:
                    self._attributes[key] = STATISTICS_TYPE[key](list(data.values()))

    def setup(self):
        self.hass.data[DOMAIN][self.entry_id]["listener"].append(async_track_state_change(
            self.hass, self._source_entity, self.entity_listener))

        
        state = self.hass.states.get(self._source_entity)
        _LOGGER.debug("entity id : %s", self.entity_id)
        old_state = self.hass.states.get(self.entity_id)
        if _is_valid_state(state):
            self.entity_listener(self._source_entity, old_state, state)
        #self._state = state.state

        #self._state = self.hass.states.get(self._switch_entity).state

    def entity_listener(self, entity, old_state, new_state):
        #try:
        _LOGGER.debug("call entity listener")
        if _is_valid_state(new_state):
            self._unit_of_measurement = new_state.attributes.get(
                ATTR_UNIT_OF_MEASUREMENT)
            self._icon = new_state.attributes.get(
                ATTR_ICON)
            
            _LOGGER.debug(f"source entity attr - {self._source_entity_attr}")

            # 데이터를 파일에 저장
            # 데이터가 하나도 기록된 게 없다면 첫 데이터이므로 저장하고 아닐때는 값이 바뀔때만 저장
            _LOGGER.debug(f"old_state - {old_state}, new_state - {new_state}")
            #if (_is_valid_state(old_state) and old_state.state != new_state.state) or (len(self._attributes["data"]) <= 0 or self._state != new_state.state):

            data = dict(sorted(self._attributes["data"].items(), reverse=True))
            _LOGGER.debug(f"data : " + str(data) + ", length : " + str(len(data)))
            if (len(data) <= 0 or 
                (self._source_entity_attr == None and str(self._state) != str(new_state.state)) or
                (self._source_entity_attr != None and str(self._state) != str(new_state.attributes.get(self._source_entity_attr)))
                ):
                if self._source_entity_attr != None:
                    self._state = new_state.attributes.get(self._source_entity_attr)
                else:
                    self._state = new_state.state

                args = {}
                offset_args = {}
                args[self._record_period_unit] = int(self._record_period)
                # offset 설정만큼 보정
                offset_args[self._offset_unit] = int(self._offset)
                #data = sorted(data.items())
                # 기간 지난것들 체크

                tmp = {}
                for key in data.keys():
                    # 여유시간 1분 추가
                    if datetime.strptime(key, '%Y-%m-%d %H:%M:%S.%f') > datetime.now() - relativedelta(**args) - relativedelta(**offset_args) + timedelta(minutes=1):
                        if len(tmp) < int(self._attributes[CONF_RECORD_LIMIT_COUNT]) - 1:
                            tmp[key] = data[key]
                        else:
                            break
                
                data = dict(sorted(tmp.items()))
                #_LOGGER.debug(f"offset unit : {self._offset_unit}, offset : {self._offset}")
                now = datetime.now()
                self._attributes["last_update_time"] = now
                now = now + relativedelta(**offset_args)
                str_now = now.strftime('%Y-%m-%d %H:%M:%S.%f')
                data[str_now] = float(self._state) if isNumber(self._state) else self._state
                _LOGGER.debug(f"self._state - {self._state}")
                d = "[data]\n" + str_now + ',' + str(self._state) + "\n"
                #_LOGGER.debug(f"data - {data}")
                with open(DATA_DIR + self._attributes["data_file"], "a") as fp:
                    fp.write(d)

                self._attributes["data"] = data
                self.calc_statistics(data)

            #_LOGGER.debug("call switch_entity_listener, old state : %s, new_state : %s",
            #          old_state, new_state.state)  
            self.schedule_update_ha_state(True)

        #except Exception as e:
        #    _LOGGER.error(f"catch error - {e}")

    """Sensor Properties"""
    @property
    def has_entity_name(self) -> bool:
        return True

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
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
    return state and state.state != STATE_UNKNOWN and state.state != STATE_UNAVAILABLE and state.state != None
