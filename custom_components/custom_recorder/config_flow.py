"""Config flow for Hello World integration."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional
from datetime import datetime

import os

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import selector
import homeassistant.helpers.entity_registry

from homeassistant.helpers.device_registry import (
    async_get,
    async_entries_for_config_entry
)

from .const import *

from homeassistant import config_entries, exceptions
from homeassistant.core import callback
from homeassistant.config import CONF_NAME


_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy hub will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            # if user_input[CONF_NETWORK_SEARCH] == True:
            #    return self.async_create_entry(title=user_input[CONF_AREA_NAME], data=user_input)
            # else:
            self.data = user_input
            #self.data[CONF_NAME] = NAME
            #self.data[CONF_SWITCHES] = []
            # self.devices = await get_available_device()
            # return await self.async_step_hosts()
            return self.async_create_entry(title=user_input[CONF_DEVICE_NAME], data=self.data)

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema(
                {
                    vol.Required(CONF_DEVICE_NAME, default=""): cv.string
                }), errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Handle a option flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.data = {}
        self.data[CONF_DEVICE_NAME] = config_entry.data.get(CONF_DEVICE_NAME)
        data_dir = DATA_DIR + self.data[CONF_DEVICE_NAME] + "_" + config_entry.entry_id + "/"
        self.data[CONF_DATA_DIR] = data_dir
        self.data[CONF_ENTITIES] = []

        _LOGGER.debug("data_dir : %s", data_dir)
        if os.path.isdir(data_dir) == False:
            os.makedirs(data_dir)

        _LOGGER.debug("call init")
        _LOGGER.debug(f"options - {config_entry.options}")
        _LOGGER.debug("config entry_id : " + config_entry.entry_id)
        # 디렉토리에 있는 목록으로 config 대체
        file_list = os.listdir(data_dir)
        if len(file_list) <= 0:
            os.removedirs(data_dir)

        for file in file_list:
            f = open(data_dir + file)
            lines = f.readlines()
            record_limit_count = DEFAULT_LIMIT_COUNT
            for idx, line in enumerate(lines):
                #_LOGGER.debug(f"idx - {idx}, line = {line}")
                isName = line.find(FIELD_NAME)
                isSourceEntity = line.find(FIELD_SOURCE_ENTITY)
                isSourceEntityAttr = line.find(FIELD_SOURCE_ENTITY_ATTR)
                isRecordPeriodUnit = line.find(FIELD_RECORD_PERIOD_UNIT)
                isRecordPeriod = line.find(FIELD_RECORD_PERIOD)
                isOffsetUnit = line.find(FIELD_OFFSET_UNIT)
                isOffset = line.find(FIELD_OFFSET)
                isRecordLimitCount = line.find(FIELD_RECORD_LIMIT_COUNT)
                #_LOGGER.debug(f"isName - {isName}, isOriginEntity - {isOriginEntity}, isRecordPeriod - {isRecordPeriod}")

                if isName == 0:
                    name = lines[idx + 1].replace("\n", "")
                if isSourceEntity == 0:
                    source_entity = lines[idx + 1].replace("\n", "")
                if isSourceEntityAttr == 0:
                    source_entity_attr = lines[idx+1].replace("\n", "")
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

            if source_entity != None and record_period != None and offset_unit != None and offset != None and record_period_unit != None and record_limit_count != None:
                d = {CONF_SOURCE_ENTITY: source_entity,
                     CONF_SOURCE_ENTITY_ATTR: source_entity_attr,
                     CONF_NAME: name, 
                     CONF_RECORD_PERIOD_UNIT: record_period_unit,
                     CONF_RECORD_PERIOD: record_period, 
                     CONF_OFFSET_UNIT: offset_unit, 
                     CONF_OFFSET: offset,
                     CONF_RECORD_LIMIT_COUNT: record_limit_count
                     }
                self.data[CONF_ENTITIES].append(d)
            f.close()

        #self.data[CONF_ENTITIES] = [
        #    {'origin_entity': 'input_number.power', 'name': 'test', 'record_period': 30}]
        _LOGGER.debug(f"data - {self.data[CONF_ENTITIES]}")


        #self.data = {}
        #if CONF_ENTITIES in config_entry.options:
        #    self.data[CONF_ENTITIES] = config_entry.options[CONF_ENTITIES]
        # else:
        #   self.data[CONF_ENTITIES] = []

    async def async_step_init(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Manage the options for the custom component."""
        errors: Dict[str, str] = {}
        # Grab all configured repos from the entity registry so we can populate the
        # multi-select dropdown that will allow a user to remove a repo.
        # entity_registry = await async_get_registry(self.hass)

        # entries = async_entries_for_config_entry(
        #    entity_registry, self.config_entry.entry_id
        # )
        # for e in entries:
        #    _LOGGER.debug("entries : " + e.entity_id)
        # Default value for our multi-select.
        #entity_map = {e.entity_id : e for e in entries}
        all_entities = {}
        all_entities_by_id = {}

        entity_registry = homeassistant.helpers.entity_registry.async_get(self.hass)
        entities = homeassistant.helpers.entity_registry.async_entries_for_config_entry(entity_registry, self.config_entry.entry_id)

        device_registry = async_get(self.hass)
        devices = async_entries_for_config_entry(device_registry, self.config_entry.entry_id)

        #for e in entities:
        #    _LOGGER.debug("entity id : %s, name : %s",e.entity_id, e.original_name)

        # Default value for our multi-select.

        for host in self.data[CONF_ENTITIES]:
            for e in entities:
                if e.original_name == host[CONF_NAME]:
                    name = e.original_name

                    all_entities[e.entity_id] = '{} - {}'.format(
                        name, host[CONF_SOURCE_ENTITY])

                    all_entities_by_id[(
                                        host[CONF_SOURCE_ENTITY],
                                        host[CONF_SOURCE_ENTITY_ATTR],
                                        host[CONF_NAME],
                                        host[CONF_RECORD_PERIOD_UNIT],
                                        host[CONF_RECORD_PERIOD],
                                        host[CONF_OFFSET_UNIT],
                                        host[CONF_OFFSET],
                                        host[CONF_RECORD_LIMIT_COUNT]
                    )] = e.entity_id

        if user_input is not None:
            if not errors:
                _LOGGER.debug(f"userinput - {user_input}")
                # If user ticked the box show this form again so they can add an
                # additional repo.
                # remove devices
                self.data[CONF_ENTITIES].clear()
                remove_entities = {}

                for key in all_entities_by_id:
                    _LOGGER.debug(
                        f"all entities by id key - {all_entities_by_id[key]}")
                    if all_entities_by_id[key] not in user_input[CONF_ENTITIES]:
                        _LOGGER.debug("remove entity : %s", all_entities_by_id[key])
                        remove_entities[all_entities_by_id[key]] = key[2]
                        #self.config_entry.data[CONF_DEVICES].remove( { host[CONF_HOST], [e.name for e in devices if e.id == all_devices_by_host[host[CONF_HOST]]] })
                    else:
                        _LOGGER.debug("append entity : %s", key[0])
                        self.data[CONF_ENTITIES].append(
                            {
                                CONF_SOURCE_ENTITY: key[0],
                                CONF_SOURCE_ENTITY_ATTR: key[1],
                                CONF_NAME: key[2],
                                CONF_RECORD_PERIOD_UNIT: key[3],
                                CONF_RECORD_PERIOD: key[4],
                                CONF_OFFSET_UNIT: key[5],
                                CONF_OFFSET: key[6],
                                CONF_RECORD_LIMIT_COUNT: key[7]
                            }
                        )
                        
                for key in remove_entities:
                    _LOGGER.debug(f"remove entity : {key}, size - {remove_entities}")
                    # 여기에서 파일 삭제
                    data_dir = self.data.get(CONF_DATA_DIR)
                    os.remove(data_dir + remove_entities[key] + ".txt")
                    file_list = os.listdir(data_dir)
                    _LOGGER.debug("file_list size : %d", len(file_list))
                    #if len(file_list) <= 0:
                    #    _LOGGER.debug("remove dir : %s", data_dir)
                    #    os.removedirs(data_dir)

                    entity_registry.async_remove(key)

                if user_input.get(CONF_ADD_ANODHER, False):
                    # if len(self.devices) <= 0:
                    #    return self.async_create_entry(title=self.cnfig_entry.data[CONF_AREA_NAME], data=self.config_entry.data)
                    # else:
                    return await self.async_step_entity()

                if len(self.data[CONF_ENTITIES]) <= 0:
                    for d in devices:
                        device_registry.async_remove_device(d.id)

                # User is done adding repos, create the config entry.
                self.data["modifydatetime"] = datetime.now()
                return self.async_create_entry(title=self.data[CONF_DEVICE_NAME], data=self.data)

        options_schema = vol.Schema(
            {
                vol.Optional(CONF_ENTITIES, default=list(all_entities)): cv.multi_select(all_entities),
                vol.Optional(CONF_ADD_ANODHER): cv.boolean,

                #vol.Optional(CONF_USE_SETUP_MODE, False, cv.boolean),
                #vol.Optional(CONF_ADD_GROUP_DEVICE, False, cv.boolean),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )

    async def async_step_entity(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        errors: Dict[str, str] = {}
        if user_input is not None:

            if not errors:
                # Input is valid, set data.
                self.data[CONF_ENTITIES].append(
                    {
                        CONF_SOURCE_ENTITY: user_input[CONF_SOURCE_ENTITY],
                        CONF_SOURCE_ENTITY_ATTR: user_input.get("", user_input[CONF_SOURCE_ENTITY_ATTR]),
                        CONF_NAME: user_input.get(CONF_NAME, user_input[CONF_SOURCE_ENTITY]),
                        CONF_RECORD_PERIOD_UNIT: user_input[CONF_RECORD_PERIOD_UNIT],
                        CONF_RECORD_PERIOD: user_input[CONF_RECORD_PERIOD],
                        CONF_OFFSET_UNIT: user_input[CONF_OFFSET_UNIT],
                        CONF_OFFSET: user_input[CONF_OFFSET],
                        CONF_RECORD_LIMIT_COUNT: user_input[CONF_RECORD_LIMIT_COUNT]
                    }
                )

                # If user ticked the box show this form again so they can add an
                # additional repo.
                if user_input.get(CONF_ADD_ANODHER, False):
                    # self.devices.remove(user_input[CONF_SWITCH_ENTITY])
                    # if len(self.devices) <= 0:
                    #    return self.async_create_entry(title=NAME, data=self.data)
                    # else:
                    return await self.async_step_entity()
                # User is done adding repos, create the config entry.
                _LOGGER.debug("call async_create_entry")
                self.data["modifydatetime"] = datetime.now()

                # 여기에서 파일 생성, 존재하지 않는 파일들은 생성해 줌
                data_dir = self.data.get(CONF_DATA_DIR)
                if os.path.isdir(data_dir) == False:
                    os.makedirs(data_dir)
                file_list = os.listdir(data_dir)
                for e in self.data[CONF_ENTITIES]:
                    if e[CONF_NAME] + ".txt" not in file_list:
                        # 파일 생성
                        with open(data_dir + e[CONF_NAME] + ".txt", "w") as fp:
                            # 파일 형식에 맞게 데이터 셋팅                        
                            fp.write(FIELD_NAME)
                            fp.write(e[CONF_NAME] + "\n")
                            fp.write(FIELD_SOURCE_ENTITY)
                            fp.write(e[CONF_SOURCE_ENTITY] + "\n")
                            fp.write(FIELD_SOURCE_ENTITY_ATTR)
                            fp.write(e[CONF_SOURCE_ENTITY_ATTR] + "\n")
                            fp.write(FIELD_RECORD_PERIOD_UNIT)
                            fp.write(e[CONF_RECORD_PERIOD_UNIT] + "\n")
                            fp.write(FIELD_RECORD_PERIOD)
                            fp.write(str(e[CONF_RECORD_PERIOD]) + "\n")
                            fp.write(FIELD_OFFSET_UNIT)
                            fp.write(e[CONF_OFFSET_UNIT] + "\n")
                            fp.write(FIELD_OFFSET)
                            fp.write(str(e[CONF_OFFSET]) + "\n")
                            fp.write(FIELD_RECORD_LIMIT_COUNT)
                            fp.write(str(e[CONF_RECORD_LIMIT_COUNT]) + "\n")
                            _LOGGER.debug(f"file write end")

                return self.async_create_entry(title=self.data[CONF_DEVICE_NAME], data=self.data)

        return self.async_show_form(
            step_id="entity",
            data_schema=vol.Schema(
                    {
                        vol.Required(CONF_SOURCE_ENTITY, default=None): selector({"entity": {}}),
                        vol.Optional(CONF_SOURCE_ENTITY_ATTR, default="None"): cv.string,
                        vol.Optional(CONF_NAME): cv.string,
                        vol.Required(CONF_RECORD_PERIOD_UNIT, default=DATE_UNIT[0]): vol.In(DATE_UNIT),
                        vol.Required(CONF_RECORD_PERIOD, default=1): int,
                        vol.Required(CONF_OFFSET_UNIT, default=DATE_UNIT[0]): vol.In(DATE_UNIT),
                        vol.Required(CONF_OFFSET, default=0): int,
                        vol.Required(CONF_RECORD_LIMIT_COUNT, default=DEFAULT_LIMIT_COUNT): int,
                        vol.Optional(CONF_ADD_ANODHER): cv.boolean,
                    }
            ), errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
