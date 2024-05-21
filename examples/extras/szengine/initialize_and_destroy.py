#! /usr/bin/env python3

from senzing import SzEngine, SzError

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
    sz_engine = SzEngine()
    # sz_engine.initialize(INSTANCE_NAME, SETTINGS)
    sz_engine.initialize(INSTANCE_NAME, SETTINGS, 2264094302, 1)
    # Do Work
    sz_engine.destroy()
except SzError as err:
    print(err)