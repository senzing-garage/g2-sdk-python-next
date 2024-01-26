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

try:
    g2_engine = g2engine.G2Engine()
    g2_engine.init(MODULE_NAME, INI_PARAMS_DICT)
    # Using get_active_config_id for demonstrations purposes
    active_config_id = g2_engine.get_active_config_id()
    g2_engine.destroy()

    # TODO How is this working if destroy called? del?
    g2_engine.init_with_config_id(MODULE_NAME, INI_PARAMS_DICT, 0)
    g2_engine.destroy()
except G2Exception as err:
    print(err)
