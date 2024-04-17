#! /usr/bin/env python3

from senzing import szengine
from senzing.szexception import SzException

ENTITY_ID = 1
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
    result = sz_engine.get_entity_by_entity_id_return_dict(ENTITY_ID)
    print(result)
except SzException as err:
    print(err)
