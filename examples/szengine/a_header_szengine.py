#! /usr/bin/env python3

from typing import List, Tuple

from senzing_truthset import (
    TRUTHSET_CUSTOMER_RECORDS,
    TRUTHSET_REFERENCE_RECORDS,
    TRUTHSET_WATCHLIST_RECORDS,
)

from senzing import SzEngine, SzEngineFlags

DATA_SOURCES = {
    "CUSTOMERS": TRUTHSET_CUSTOMER_RECORDS,
    "REFERENCE": TRUTHSET_REFERENCE_RECORDS,
    "WATCHLIST": TRUTHSET_WATCHLIST_RECORDS,
}
INSTANCE_NAME = "Example1"
SETTINGS = {
    "PIPELINE": {
        "CONFIGPATH": "/etc/opt/senzing",
        "RESOURCEPATH": "/opt/senzing/g2/resources",
        "SUPPORTPATH": "/opt/senzing/data",
    },
    "SQL": {"CONNECTION": "sqlite3://na:na@/tmp/sqlite/G2C.db"},
}
TEST_RECORDS: List[Tuple[str, str]] = [
    ("CUSTOMERS", "1001"),
    ("CUSTOMERS", "1002"),
    ("CUSTOMERS", "1003"),
    ("CUSTOMERS", "1009"),
]

# -----------------------------------------------------------------------------
# Internal functions
# -----------------------------------------------------------------------------


def add_records(sz_engine: SzEngine, record_id_list: List[Tuple[str, str]]) -> None:
    """Add all of the records in the list."""
    flags = SzEngineFlags.SZ_WITHOUT_INFO
    for record_identification in record_id_list:
        datasource = record_identification[0]
        record_id = record_identification[1]
        record = DATA_SOURCES.get(datasource, {}).get(record_id, {})
        sz_engine.add_record(
            record.get("DataSource", ""),
            record.get("Id", ""),
            record.get("Json", ""),
            flags,
        )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

print("\n---- szengine --------------------------------------------------------\n")

sz_engine = SzEngine(INSTANCE_NAME, SETTINGS)
add_records(sz_engine, TEST_RECORDS)