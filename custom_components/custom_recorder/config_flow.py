"""Config flow for Hello World integration."""
import logging
import voluptuous as vol
from typing import Any, Dict, Optional
from datetime import datetime

import os

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import selector
import homeassistant.helpers.entity_registry

from homeassistant.helpers.device_registry import (
    async_get,
    async_entries_for_config_entry,
)
from homeassistant.helpers import (
    device_registry as dr,
    entity_registry as er,
)

from .const import *

from homeassistant import config_entries, exceptions
from homeassistant.core import callback


_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    data: Optional[Dict[str, Any]]

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self.data = user_input
            return self.async_create_entry(title=user_input[CONF_DEVICE_NAME], data=self.data)

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

    def clear_device_info(self):
        # 밀어넣었던 디바이스에서 제거
        entity_registry = er.async_get(
            self.hass)
        entities = er.async_entries_for_config_entry(
            entity_registry, self.config_entry.entry_id)
        device_ids = set([])
        entities = er.async_entries_for_config_entry(
                entity_registry, self.config_entry.entry_id)
        device_registry = dr.async_get(
            self.hass)
        devices = dr.async_entries_for_config_entry(
            device_registry, self.config_entry.entry_id)

        for e in entities:
            device_ids.add(e.device_id)

        for d in devices:
            if d.id not in device_ids:
                device_registry.async_update_device(
                    d.id, remove_config_entry_id=self.config_entry.entry_id)

    def remove_entity(self, entity_id, conf):
        _LOGGER.debug("delete option")
        er.async_get(self.hass).async_remove(entity_id=entity_id)

        try:
            self.data[CONF_ENTITIES].remove(conf)
        except:
            """"""

    def __init__(self, config_entry):
        self.data = {}
        self.data[CONF_DEVICE_NAME] = config_entry.data.get(CONF_DEVICE_NAME)
        data_dir = DATA_DIR + self.data[CONF_DEVICE_NAME] + "_" + config_entry.entry_id + "/"
        self.data[CONF_DATA_DIR] = data_dir
        self.data[CONF_ENTITIES] = []
        self._bLoadSetting = False

        self._selected_option = {}
        self._selected_entity_id = None

    async def async_step_init(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Manage the options for the custom component."""
        errors: Dict[str, str] = {}

        def _load_setting():
            data_dir = self.data[CONF_DATA_DIR]

            _LOGGER.debug("data_dir : %s", data_dir)
            if os.path.isdir(data_dir) == False:
                os.makedirs(data_dir)

            _LOGGER.debug("call init")
            # 디렉토리에 있는 목록으로 config 대체
            file_list = os.listdir(data_dir)
            #if len(file_list) <= 0:
            #    os.removedirs(data_dir)

            for file in file_list:
                f = open(data_dir + file)
                lines = f.readlines()
                record_limit_count = DEFAULT_LIMIT_COUNT
                move_source_entity_device = False
                parent_device_entity_id_format = False
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
                    isMoveSourceEntityDevice = line.find(FIELD_MOVE_SOURCE_ENTITY_DEVICE)
                    isParentEntityIdFormat = line.find(FIELD_PARENT_DEVICE_ENTITY_ID_FORMAT)
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
                    if isMoveSourceEntityDevice == 0:
                        move_source_entity_device = lines[idx+1].replace("\n", "")
                    if isParentEntityIdFormat == 0:
                        parent_device_entity_id_format = lines[idx+1].replace("\n", "")

                if source_entity != None and record_period != None and offset_unit != None and offset != None and record_period_unit != None and record_limit_count != None and\
                    move_source_entity_device != None:
                    d = {CONF_SOURCE_ENTITY: source_entity,
                        CONF_SOURCE_ENTITY_ATTR: source_entity_attr,
                        CONF_NAME: name, 
                        CONF_RECORD_PERIOD_UNIT: record_period_unit,
                        CONF_RECORD_PERIOD: record_period, 
                        CONF_OFFSET_UNIT: offset_unit, 
                        CONF_OFFSET: offset,
                        CONF_RECORD_LIMIT_COUNT: record_limit_count,
                        CONF_MOVE_SOURCE_ENTITY_DEVICE: move_source_entity_device,
                        CONF_PARENT_DEVICE_ENTITY_ID_FORMAT: parent_device_entity_id_format
                        }

                    self.data[CONF_ENTITIES].append(d)
                f.close()
        if False == self._bLoadSetting:
            await self.hass.async_add_executor_job(_load_setting)
            self._bLoadSetting = True

        if user_input is not None:

            if not errors:
                if user_input.get(CONF_OPTION_SELECT) == CONF_OPTION_MODIFY:
                    if len(self.data[CONF_ENTITIES]) > 0:
                        return await self.async_step_select()
                elif user_input.get(CONF_OPTION_SELECT) == CONF_OPTION_ADD:
                    return await self.async_step_entity()

        options_schema = vol.Schema(
            {
                vol.Optional(CONF_OPTION_SELECT): selector.SelectSelector(selector.SelectSelectorConfig(options=CONF_OPTIONS, mode=selector.SelectSelectorMode.LIST, translation_key=CONF_OPTION_SELECT)),
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )

    async def async_step_select(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Manage the options for the custom component."""
        errors: Dict[str, str] = {}
        if user_input is not None:
            _LOGGER.debug("user input is not None")
            if not errors:
                entity_id = user_input.get(CONF_OPTION_ENTITIES)
                entity = er.async_get(self.hass).async_get(entity_id)
                _LOGGER.debug("entity : " + str(entity))
                conf = {}
                for k in self.data[CONF_ENTITIES]:
                    if entity.original_name == k.get(CONF_NAME):
                        conf = k
                        self._selected_option = conf
                        self._selected_entity_id = entity_id
                        break

                if user_input.get(CONF_OPTION_DELETE):
                    # 삭제
                    self.remove_entity(entity_id, conf)
                    # txt 파일도 삭제해야 함
                    data_dir = self.data.get(CONF_DATA_DIR)
                    os.remove(data_dir + conf.get(CONF_NAME) + ".txt")
                    file_list = os.listdir(data_dir)
                    _LOGGER.debug("file_list size : %d", len(file_list))
                    
                    self.clear_device_info()

                    return self.async_create_entry(title=self.data[CONF_DEVICE_NAME], data=self.data)
                else:
                    # 수정
                    _LOGGER.debug("selected option : " + str(self._selected_option))
                    return await self.async_step_entity()

        option_entities = []
        entities = er.async_entries_for_config_entry(
            er.async_get(self.hass), self.config_entry.entry_id)
        for e in entities:
            option_entities.append(e.entity_id)
        _LOGGER.debug("entities : " + str(entities))
        options_schema = vol.Schema(
            {
                vol.Optional(CONF_OPTION_ENTITIES): selector.EntitySelector(selector.EntitySelectorConfig(include_entities=option_entities)),
                vol.Optional(CONF_OPTION_DELETE): selector.BooleanSelector(selector.BooleanSelectorConfig())
            }
        )

        return self.async_show_form(
            step_id="select", data_schema=options_schema, errors=errors
        )

    async def async_step_entity(self, user_input: Optional[Dict[str, Any]] = None):
        """Second step in config flow to add a repo to watch."""
        errors: Dict[str, str] = {}
        if user_input is not None:

            if not errors:
                if self._selected_option.get(CONF_NAME):
                    self.remove_entity(self._selected_entity_id, self._selected_option)
                    # 파일 명 수정
                    # data_dir = self.data.get(CONF_DATA_DIR)
                    # os.rename(data_dir + self._selected_option.get(CONF_NAME) + ".txt",
                    #           data_dir + user_input.get(CONF_NAME) + ".txt")
                    # file_list = os.listdir(data_dir)
                    # _LOGGER.debug("file_list size : %d", len(file_list))
                    user_input[CONF_NAME] = self._selected_option.get(CONF_NAME)
                    self.clear_device_info()
                # Input is valid, set data.
                self.data[CONF_ENTITIES].append(
                    {
                        CONF_SOURCE_ENTITY: user_input[CONF_SOURCE_ENTITY],
                        CONF_SOURCE_ENTITY_ATTR: user_input.get(CONF_SOURCE_ENTITY_ATTR, "None"),
                        CONF_NAME: user_input.get(CONF_NAME, user_input[CONF_SOURCE_ENTITY]),
                        CONF_RECORD_PERIOD_UNIT: user_input[CONF_RECORD_PERIOD_UNIT],
                        CONF_RECORD_PERIOD: user_input[CONF_RECORD_PERIOD],
                        CONF_OFFSET_UNIT: user_input[CONF_OFFSET_UNIT],
                        CONF_OFFSET: user_input[CONF_OFFSET],
                        CONF_RECORD_LIMIT_COUNT: user_input[CONF_RECORD_LIMIT_COUNT],
                        CONF_MOVE_SOURCE_ENTITY_DEVICE: user_input[CONF_MOVE_SOURCE_ENTITY_DEVICE],
                        CONF_PARENT_DEVICE_ENTITY_ID_FORMAT: user_input[CONF_PARENT_DEVICE_ENTITY_ID_FORMAT],
                    }
                )

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
                            fp.write(FIELD_MOVE_SOURCE_ENTITY_DEVICE)
                            fp.write(str(e[CONF_MOVE_SOURCE_ENTITY_DEVICE]) + "\n")
                            fp.write(FIELD_PARENT_DEVICE_ENTITY_ID_FORMAT)
                            fp.write(str(e[CONF_PARENT_DEVICE_ENTITY_ID_FORMAT]) + "\n")
                            _LOGGER.debug(f"file write end")

                return self.async_create_entry(title=self.data[CONF_DEVICE_NAME], data=self.data)

        _LOGGER.debug("selected option : " + str(self._selected_option))

        if self._selected_option:
            return self.async_show_form(
                step_id="entity",
                data_schema=vol.Schema(
                        {
                            vol.Required(CONF_SOURCE_ENTITY, default=self._selected_option.get(CONF_SOURCE_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig()),
                            vol.Optional(CONF_SOURCE_ENTITY_ATTR, description={"suggested_value": self._selected_option.get(CONF_SOURCE_ENTITY_ATTR, None)}): cv.string,
                            vol.Required(CONF_RECORD_PERIOD_UNIT, default=self._selected_option.get(CONF_RECORD_PERIOD_UNIT, DATE_UNIT[0])): vol.In(DATE_UNIT),
                            vol.Required(CONF_RECORD_PERIOD, default=int(self._selected_option.get(CONF_RECORD_PERIOD, 1))): int,
                            vol.Required(CONF_OFFSET_UNIT, default=self._selected_option.get(CONF_OFFSET_UNIT, DATE_UNIT[0])): vol.In(DATE_UNIT),
                            vol.Required(CONF_OFFSET, default=int(self._selected_option.get(CONF_OFFSET, 0))): int,
                            vol.Required(CONF_RECORD_LIMIT_COUNT, default=int(self._selected_option.get(CONF_RECORD_LIMIT_COUNT, DEFAULT_LIMIT_COUNT))): int,
                            vol.Required(CONF_MOVE_SOURCE_ENTITY_DEVICE, default=False if self._selected_option.get(CONF_MOVE_SOURCE_ENTITY_DEVICE, "False") in ("False", "None") else True): cv.boolean,
                            vol.Required(CONF_PARENT_DEVICE_ENTITY_ID_FORMAT, default=False if self._selected_option.get(CONF_PARENT_DEVICE_ENTITY_ID_FORMAT, "False") in ("False", "None") else True): cv.boolean,
                            #vol.Optional(CONF_ADD_ANODHER): cv.boolean,
                        }
                ), errors=errors
                , description_placeholders={
                    "entity_name": self._selected_option.get(CONF_NAME, "")
                },
            )
        else:
            return self.async_show_form(
                step_id="entity",
                data_schema=vol.Schema(
                        {
                            vol.Optional(CONF_NAME, description={"suggested_value": self._selected_option.get(CONF_NAME, None)}): cv.string,
                            vol.Required(CONF_SOURCE_ENTITY, default=self._selected_option.get(CONF_SOURCE_ENTITY)): selector.EntitySelector(selector.EntitySelectorConfig()),
                            vol.Optional(CONF_SOURCE_ENTITY_ATTR, description={"suggested_value": self._selected_option.get(CONF_SOURCE_ENTITY_ATTR, None)}): cv.string,
                            vol.Required(CONF_RECORD_PERIOD_UNIT, default=self._selected_option.get(CONF_RECORD_PERIOD_UNIT, DATE_UNIT[0])): vol.In(DATE_UNIT),
                            vol.Required(CONF_RECORD_PERIOD, default=int(self._selected_option.get(CONF_RECORD_PERIOD, 1))): int,
                            vol.Required(CONF_OFFSET_UNIT, default=self._selected_option.get(CONF_OFFSET_UNIT, DATE_UNIT[0])): vol.In(DATE_UNIT),
                            vol.Required(CONF_OFFSET, default=int(self._selected_option.get(CONF_OFFSET, 0))): int,
                            vol.Required(CONF_RECORD_LIMIT_COUNT, default=int(self._selected_option.get(CONF_RECORD_LIMIT_COUNT, DEFAULT_LIMIT_COUNT))): int,
                            vol.Required(CONF_MOVE_SOURCE_ENTITY_DEVICE, default=False if self._selected_option.get(CONF_MOVE_SOURCE_ENTITY_DEVICE, "False") in ("False", "None") else True): cv.boolean,
                            vol.Required(CONF_PARENT_DEVICE_ENTITY_ID_FORMAT, default=False if self._selected_option.get(CONF_PARENT_DEVICE_ENTITY_ID_FORMAT, "False") in ("False", "None") else True): cv.boolean,
                            # vol.Optional(CONF_ADD_ANODHER): cv.boolean,
                        }
                ), errors=errors
                , description_placeholders={
                    "entity_name": self._selected_option.get(CONF_NAME, "")
                },
            )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
