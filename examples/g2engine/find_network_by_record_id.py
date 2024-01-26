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

RECORD_LIST_DICT = {
    "RECORDS": [
        {"DATA_SOURCE": "REFERENCE", "RECORD_ID": "2071"},
        {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1069"},
    ]
}
MAX_DEGREE = 5
BUILD_OUT_DEGREE = 2
MAX_ENTITIES = 10


try:
    g2_engine = g2engine.G2Engine(MODULE_NAME, INI_PARAMS_DICT)
    result = g2_engine.find_network_by_record_id(
        RECORD_LIST_DICT, MAX_DEGREE, BUILD_OUT_DEGREE, MAX_ENTITIES
    )
    print(result)
except G2Exception as err:
    print(err)
