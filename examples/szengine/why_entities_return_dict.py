#! /usr/bin/env python3

from senzing import szengine
from senzing.szexception import SzError

ENTITY_ID_1 = 1
ENTITY_ID_2 = 6
INSTANCE_NAME = "Example"
SETTINGS = {
    "PIPELINE": {
        "CONFIGPATH": "/etc/opt/senzing",
        "RESOURCEPATH": "/opt/senzing/g2/resources",
        "SUPPORTPATH": "/opt/senzing/data",
    },
    "SQL": {"CONNECTION": "sqlite3://na:na@/var/opt/senzing/G2C.db"},
}

try:
    sz_engine = szengine.SzEngine(INSTANCE_NAME, SETTINGS)
    result = sz_engine.why_entities_return_dict(ENTITY_ID_1, ENTITY_ID_2, 1)
    print(result)
except SzError as err:
    print(err)
