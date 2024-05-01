#! /usr/bin/env python3

from senzing import SzEngineFlags, SzError, szengine

DATA_SOURCE_CODE = "CUSTOMERS"
FLAGS = SzEngineFlags.SZ_WHY_RECORDS_DEFAULT_FLAGS
INSTANCE_NAME = "Example"
RECORD_ID = "1001"
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
    RESULT = sz_engine.why_record_in_entity(
        DATA_SOURCE_CODE,
        RECORD_ID,
        FLAGS,
    )
    print(RESULT[:66], "...")
except SzError as err:
    print(f"\nError:\n{err}\n")
