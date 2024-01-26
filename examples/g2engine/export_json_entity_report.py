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
    g2_engine = g2engine.G2Engine(MODULE_NAME, INI_PARAMS_DICT)
    export_handle = g2_engine.export_json_entity_report()

    with open("exportJSONEntityReport.json", "w", encoding="utf-8") as export_out:
        while True:
            export_record = g2_engine.fetch_next(export_handle)
            if not export_record:
                break
            export_out.write(export_record)

    g2_engine.close_export(export_handle)

except G2Exception as err:
    print(err)
