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

ENTITY_LIST_DICT = {"ENTITIES": [{"ENTITY_ID": "100008"}, {"ENTITY_ID": "55"}]}
MAX_DEGREE = 5
BUILD_OUT_DEGREE = 2
MAX_ENTITIES = 10


try:
    g2_engine = g2engine.G2Engine(MODULE_NAME, INI_PARAMS_DICT)
    result = g2_engine.find_network_by_entity_id(
        ENTITY_LIST_DICT, MAX_DEGREE, BUILD_OUT_DEGREE, MAX_ENTITIES
    )
    print(result)
except G2Exception as err:
    print(err)
