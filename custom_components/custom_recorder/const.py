
import numpy as np
# This is the internal name of the integration, it should also match the directory
# name for the integration.
DOMAIN = "custom_recorder"
NAME = "Custom Recorder"
VERSION = "1.2.0"

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
CONF_RECORD_LIMIT_COUNT = "record_limit_count"
CONF_DATA_DIR = "data_dir"
CONF_MOVE_SOURCE_ENTITY_DEVICE = "move_source_entity_device"
CONF_PARENT_DEVICE_ENTITY_ID_FORMAT = "parent_device_entity_id_format"

CONF_OPTION_SELECT = "option_select"
CONF_OPTION_SELECT = "option_select"
CONF_OPTION_DELETE = "option_delete"
CONF_OPTION_ENTITIES = "option_entities"
CONF_OPTION_MODIFY = "option_modify"
CONF_OPTION_ADD = "option_add"

CONF_OPTIONS = [
    CONF_OPTION_MODIFY,
    CONF_OPTION_ADD
]

DEFAULT_LIMIT_COUNT = 0

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
FIELD_RECORD_LIMIT_COUNT = "[record_limit_count]\n"
FIELD_MOVE_SOURCE_ENTITY_DEVICE = "[move_source_entity_device]\n"
FIELD_PARENT_DEVICE_ENTITY_ID_FORMAT = "[parent_device_entity_id_format]\n"

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
    "quantile_25": np.quantile,
    "quantile_50": np.quantile,
    "quantile_75": np.quantile,
}
