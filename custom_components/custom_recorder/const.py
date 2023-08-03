
import numpy as np
# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "custom_recorder"
NAME = "Custom Recorder"
VERSION = "1.0.6"

CONF_DEVICE_NAME = "device_name"
CONF_SOURCE_ENTITY = "source_entity"
CONF_SOURCE_ENTITY_ATTR = "source_entity_attr"
CONF_ENTITIES = "entities"
CONF_ADD_ANODHER = "add_another"
CONF_NAME = "name"
CONF_RECORD_PERIOD_UNIT = "record_period_unit"
CONF_RECORD_PERIOD = "record_period"
CONF_OFFSET_UNIT = "offset_unit"
CONF_OFFSET = "offset"

DIR_PATH = "custom_recorder/"
DATA_PATH = "data/"

DATA_DIR = DIR_PATH + DATA_PATH

FIELD_NAME = "[name]\n"
FIELD_SOURCE_ENTITY = "[source_entity]\n"
FIELD_SOURCE_ENTITY_ATTR = "[source_entity_attr]\n"
FIELD_RECORD_PERIOD_UNIT = "[record_period_unit]\n"
FIELD_RECORD_PERIOD = "[record_period]\n"
FIELD_OFFSET_UNIT = "[offset_unit]\n"
FIELD_OFFSET = "[offset]\n"
FIELD_DATA = "[data]\n"

DATE_UNIT = [
    'years', 
    'months', 
    'weeks', 
    'days', 
    'hours', 
    'minutes', 
    'seconds', 
    'microseconds',
]

STATISTICS_TYPE = {
    "min": np.min,
    "max": np.max,
    "mean": np.mean,
    "median": np.median,
    "sum": np.sum,
    "std": np.std,
    "var": np.var,
}
