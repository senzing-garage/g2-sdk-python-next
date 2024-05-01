#! /usr/bin/env python3

import json

from senzing import SzError, szengine

ENTITY_ID_1 = 1
ENTITY_ID_2 = 6
INSTANCE_NAME = "Example"
SETTINGS = {
    "PIPELINE": {
        "CONFIGPATH": "/etc/opt/senzing",
        "RESOURCEPATH": "/opt/senzing/g2/resources",
        "SUPPORTPATH": "/opt/senzing/data",
    },
    "SQL": {"CONNECTION": "sqlite3://na:na@/tmp/sqlite/G2C.db"},
}

try:
    sz_engine = szengine.SzEngine(INSTANCE_NAME, SETTINGS)
    RESULT = sz_engine.why_entities_return_dict(ENTITY_ID_1, ENTITY_ID_2, 1)
    print(json.dumps(RESULT)[:66], "...")
except SzError as err:
    print(f"\nError:\n{err}\n")
