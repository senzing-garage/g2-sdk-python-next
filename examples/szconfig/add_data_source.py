#! /usr/bin/env python3

from senzing import szconfig, szconfigmanager
from senzing.szexception import SzError

CONFIG_COMMENT = "Added new datasource"
DATA_SOURCE_CODE = "TEST12"
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
    sz_config = szconfig.SzConfig(INSTANCE_NAME, SETTINGS)
    sz_configmgr = szconfigmanager.SzConfigManager(INSTANCE_NAME, SETTINGS)

    current_config_id = sz_configmgr.get_default_config_id()
    current_config = sz_configmgr.get_config(current_config_id)
    config_handle = sz_config.import_config(current_config)

    result = sz_config.add_data_source(config_handle, DATA_SOURCE_CODE)
    new_config = sz_config.export_config(config_handle)
    sz_config.close_config(config_handle)

    new_config_id = sz_configmgr.add_config(new_config, CONFIG_COMMENT)
    sz_configmgr.set_default_config_id(new_config_id)

    print(result)
except SzError as err:
    print(err)
