#! /usr/bin/env python3

from senzing import SzError, szconfig

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
    sz_config = szconfig.SzConfig(INSTANCE_NAME, SETTINGS)
    config_handle = sz_config.create_config()
    RESULT = sz_config.get_data_sources(config_handle)
    sz_config.close_config(config_handle)
    print(RESULT[:66], "...")
except SzError as err:
    print(f"\nError:\n{err}\n")
