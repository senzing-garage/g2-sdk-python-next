#! /usr/bin/env python3

import json

from senzing import g2config
from senzing.g2exception import G2Exception

ini_params_dict = {
    "PIPELINE": {
        "CONFIGPATH": "/etc/opt/senzing",
        "RESOURCEPATH": "/opt/senzing/g2/resources",
        "SUPPORTPATH": "/opt/senzing/data",
    },
    "SQL": {"CONNECTION": "sqlite3://na:na@/tmp/sqlite/G2C.db"},
}
MODULE_NAME = "Example"

try:
    g2_config = g2config.G2Config(MODULE_NAME, json.dumps(ini_params_dict))
    CONFIG_HANDLE = g2_config.create()

    # Do work.

    g2_config.close(CONFIG_HANDLE)
except G2Exception as err:
    print(err)
