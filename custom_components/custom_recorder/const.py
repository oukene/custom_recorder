"""Constants for the Detailed Hello World Push integration."""
from typing import DefaultDict
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "custom_recorder"
NAME = "Custom Recorder"
VERSION = "1.0.0"

CONF_DEVICE_NAME = "device_name"
CONF_SOURCE_ENTITY = "source_entity"
CONF_RECORD_INTERVAL = "record_interval"
CONF_ENTITIES = "entities"
CONF_ADD_ANODHER = "add_another"
CONF_NAME = "name"
CONF_RECORD_PERIOD = "record_period"
CONF_RECORD_TYPE = "record_type"

DIR_PATH = "custom_recorder/"
DATA_PATH = "test/"

DATA_DIR = DIR_PATH + DATA_PATH

FIELD_NAME = "[name]\n"
FIELD_SOURCE_ENTITY = "[source_entity]\n"
FIELD_RECORD_PERIOD = "[record_period]\n"
FIELD_DATA = "[data]\n"

OPTIONS = [
    (CONF_SOURCE_ENTITY, "", cv.string),
    (CONF_RECORD_INTERVAL, "0.5", vol.All(vol.Coerce(float), vol.Range(0, 1))),
]
