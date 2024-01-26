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

DATA_SOURCE_CODE_1 = "CUSTOMERS"
RECORD_ID_1 = "1009"
DATA_SOURCE_CODE_2 = "WATCHLIST"
RECORD_ID_2 = "1014"

try:
    g2_engine = g2engine.G2Engine(MODULE_NAME, INI_PARAMS_DICT)
    result = g2_engine.why_records(
        DATA_SOURCE_CODE_1, RECORD_ID_1, DATA_SOURCE_CODE_2, RECORD_ID_2
    )
    print(result)
except G2Exception as err:
    print(err)
