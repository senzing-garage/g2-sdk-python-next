#! /usr/bin/env python3

from senzing import g2engine
from senzing.g2exception import G2Exception

INI_PARAMS_DICT = {
    "PIPELINE": {
        "CONFIGPATH": "/etc/opt/senzing",
        "RESOURCEPATH": "/opt/senzing/g2/resources",
        "SUPPORTPATH": "/opt/senzing/data",
    },
    "SQL": {"CONNECTION": "sqlite3://na:na@/tmp/sqlite/G2C.db"},
}
MODULE_NAME = "Example"

START_DATA_SOURCE_CODE = "CUSTOMERS"
START_RECORD_ID = "1001"
END_DATA_SOURCE_CODE = "WATCHLIST"
END_RECORD_ID = "1007"
MAX_DEGREE = 3
EXCLUDED_ENTITIES_DICT = {"ENTITIES": [{"ENTITY_ID": "5"}]}
REQUIRED_DSRCS_DICT = {"DATA_SOURCES": ["WATCHLIST"]}

try:
    g2_engine = g2engine.G2Engine(MODULE_NAME, INI_PARAMS_DICT)
    result = g2_engine.find_path_including_source_by_record_id(
        START_DATA_SOURCE_CODE,
        START_RECORD_ID,
        END_DATA_SOURCE_CODE,
        END_RECORD_ID,
        MAX_DEGREE,
        EXCLUDED_ENTITIES_DICT,
        REQUIRED_DSRCS_DICT,
    )
    print(result)
except G2Exception as err:
    print(err)
