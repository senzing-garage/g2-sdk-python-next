#! /usr/bin/env python3

"""
TODO: g2engine_abstract.py
"""

# pylint: disable=C0302
# AC - Temp disables to get changes in for move to senzing garage
# pylint: disable=W0511,W1113


# Import from standard library. https://docs.python.org/3/library/

import json
from abc import ABC, abstractmethod

# TODO Possible "observer" approach for with info
# from dataclasses import dataclass
# from typing import Any, Dict, Protocol, Tuple, Union, cast, runtime_checkable
from typing import Any, Dict, Tuple, cast, Union

from .g2engineflags import G2EngineFlags

# Metadata

# __all__ = ["G2EngineAbstract", "WithInfoResponsesAbstract"]
__all__ = ["G2EngineAbstract"]
__version__ = "0.0.1"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = "2023-10-30"
__updated__ = "2023-10-30"

# -------------------------------------------------------------------------
# Data Classes
# -------------------------------------------------------------------------


# TODO Possible "observer" approach for with info
# @dataclass(slots=True)
# class WithInfoResponsesAbstract(ABC):
#     @abstractmethod
#     def append(self, response: str) -> None:
#         """"""

#     @abstractmethod
#     def get_and_clear(self) -> deque[str]:
#         """"""

#     @abstractmethod
#     def len(self) -> int:
#         """"""

#     @abstractmethod
#     def sizeof(self) -> int:
#         """"""


# -------------------------------------------------------------------------
# Classes
# -------------------------------------------------------------------------


class G2EngineAbstract(ABC):
    """
    G2 engine module access library
    """

    # -------------------------------------------------------------------------
    # Messages
    # -------------------------------------------------------------------------

    # TODO: Change to f-strings
    # TODO Remove all _V2 for V4
    # Change to be same as g2Product: G2Engine_<method_name()>
    PREFIX = "g2engine."
    """ :meta private: """

    # TODO Reorder and sort - some APIs are going away and search was added to end temporarily
    # TODO Removed all the _V2 versions
    # TODO It doesn't make sense to have G2_, that isn't the method name
    ID_MESSAGES = {
        4001: PREFIX + "G2_addRecord({0}, {1}, {2}, {3}) failed. Return code: {4}",
        4002: (
            PREFIX
            + "G2_addRecordWithInfo({0}, {1}, {2}, {3}, {4}) failed. Return code: {5}"
        ),
        # NOTE These are being removed for V4
        # 4003: (
        #     PREFIX
        #     + "G2_addRecordWithInfoWithReturnedRecordID({0}, {1}, {2}, {3}) failed."
        #     " Return code: {4}"
        # ),
        # 4004: (
        #     PREFIX
        #     + "G2_addRecordWithReturnedRecordID({0}, {1}, {2}) failed. Return code: {3}"
        # ),
        # NOTE Is checkRecord being removed?
        4005: PREFIX + "G2_checkRecord({0}, {1}) failed. Return code: {2}",
        4006: PREFIX + "G2_closeExport({0}) failed. Return code: {1}",
        4007: PREFIX + "G2_countRedoRecords failed. Return code: {0}",
        4008: PREFIX + "G2_deleteRecord({0}, {1}, {2}) failed. Return code: {3}",
        4009: (
            PREFIX
            + "G2_deleteRecordWithInfo({0}, {1}, {2}, {3}) failed. Return code: {4}"
        ),
        4010: PREFIX + "G2_destroy() failed. Return code: {0}",
        4011: PREFIX + "G2_exportConfigAndConfigID() failed. Return code: {0}",
        4012: PREFIX + "G2_exportConfig() failed. Return code: {0}",
        4013: PREFIX + "G2_exportCSVEntityReport({0}, {1}) failed. Return code: {2}",
        4014: PREFIX + "G2_exportJSONEntityReport({0}) failed. Return code: {1}",
        4015: PREFIX + "G2_fetchNext({0}) failed. Return code: {1}",
        4016: (
            PREFIX
            + "G2_findInterestingEntitiesByEntityID({0}, {1}) failed. Return code: {2}"
        ),
        4017: (
            PREFIX
            + "G2_findInterestingEntitiesByRecordID({0}, {1}, {2}) failed. Return"
            " code: {3}"
        ),
        4018: (
            PREFIX
            + "G2_findNetworkByEntityID({0}, {1}, {2}, {3}) failed. Return code: {4}"
        ),
        4019: (
            PREFIX
            + "G2_findNetworkByEntityID_V2({0}, {1}, {2}, {3}, {4}) failed. Return"
            " code: {5}"
        ),
        4020: (
            PREFIX
            + "G2_findNetworkByRecordID({0}, {1}, {2}, {3}) failed. Return code: {4}"
        ),
        4021: (
            PREFIX
            + "G2_findNetworkByRecordID_V2({0}, {1}, {2}, {3}, {4}) failed. Return"
            " code: {5}"
        ),
        4022: PREFIX + "G2_findPathByEntityID({0}, {1}, {2}) failed. Return code: {3}",
        4023: (
            PREFIX
            + "G2_findPathByEntityID_V2({0}, {1}, {2}, {3}) failed. Return code: {4}"
        ),
        4024: (
            PREFIX
            + "G2_findPathByRecordID({0}, {1}, {2}, {3}, {4}) failed. Return code: {5}"
        ),
        4025: (
            PREFIX
            + "G2_findPathByRecordID_V2({0}, {1}, {2}, {3}, {4}, {5}) failed. Return"
            " code: {0}"
        ),
        4026: (
            PREFIX
            + "G2_findPathExcludingByEntityID({0}, {1}, {2}, {3}) failed. Return"
            " code: {4}"
        ),
        4027: (
            PREFIX
            + "G2_findPathExcludingByEntityID_V2({0}, {1}, {2}, {3}, {4}) failed."
            " Return code: {5}"
        ),
        4028: (
            PREFIX
            + "G2_findPathExcludingByRecordID({0}, {1}, {2}, {3} {4}, {5}) failed."
            " Return code: {6}"
        ),
        4029: (
            PREFIX
            + "G2_findPathExcludingByRecordID_V2({0}, {1}, {2}, {3} {4}, {5}, {6})"
            " failed. Return code: {7}"
        ),
        4030: (
            PREFIX
            + "G2_findPathIncludingSourceByEntityID({0}, {1}, {2}, {3}, {4}) failed."
            " Return code: {5}"
        ),
        4031: (
            PREFIX
            + "G2_findPathIncludingSourceByEntityID_V2({0}, {1}, {2}, {3}, {4}, {5})"
            " failed. Return code: {6}"
        ),
        4032: (
            PREFIX
            + "G2_findPathIncludingSourceByRecordID({0}, {1}, {2}, {3} {4}, {5}, {6})"
            " failed. Return code: {7}"
        ),
        4033: (
            PREFIX
            + "G2_findPathIncludingSourceByRecordID_V2({0}, {1}, {2}, {3} {4}, {5},"
            " {6}, {7}) failed. Return code: {8}"
        ),
        4034: PREFIX + "G2_getActiveConfigID() failed. Return code: {0}",
        # TODO Modified to reflect V4
        # 4034: PREFIX + "G2_getEntityByEntityID({0}) failed. Return code: {1}",
        4035: PREFIX + "G2_getEntityByEntityID({0}, {1}) failed. Return code: {2}",
        4036: PREFIX + "G2_getEntityByEntityID_V2({0}, {1}) failed. Return code: {2}",
        4037: PREFIX + "G2_getEntityByRecordID({0}, {1}) failed. Return code: {2}",
        4038: (
            PREFIX + "G2_getEntityByRecordID_V2({0}, {1}, {2}) failed. Return code: {3}"
        ),
        4039: PREFIX + "G2_getLastException() failed. Return code: {0}",
        4040: PREFIX + "G2_getRecord({0}, {1}) failed. Return code: {2}",
        4041: PREFIX + "G2_getRecord_V2({0}, {1}, {2}) failed. Return code: {3}",
        4042: PREFIX + "G2_getRedoRecord() failed. Return code: {0}",
        4043: PREFIX + "G2_getRepositoryLastModifiedTime() failed. Return code: {0}",
        4044: PREFIX + "G2_getVirtualEntityByRecordID({0}) failed. Return code: {1}",
        4045: (
            PREFIX
            + "G2_getVirtualEntityByRecordID_V2({0}, {1}) failed. Return code: {2}"
        ),
        4046: PREFIX + "G2_howEntityByEntityID({0}) failed. Return code: {1}",
        4047: PREFIX + "G2_howEntityByEntityID_V2({0}, {1}) failed. Return code: {2}",
        4048: PREFIX + "G2_init({0}, {1}, {2}) failed. Return code: {3}",
        4049: (
            PREFIX + "G2_initWithConfigID({0}, {1}, {2}, {3}) failed. Return code: {4}"
        ),
        4050: PREFIX + "G2_primeEngine() failed. Return code: {0}",
        4051: PREFIX + "G2_process({0}) failed. Return code: {1}",
        4052: PREFIX + "G2_processRedoRecord() failed. Return code: {0}",
        4053: PREFIX + "G2_processRedoRecordWithInfo({0}) failed. Return code: {0}",
        4054: PREFIX + "G2_processWithInfo({0}, {1}) failed. Return code: {2}",
        4055: PREFIX + "G2_processWithResponse({0}) failed. Return code: {1}",
        4056: PREFIX + "G2_processWithResponseResize({0}) failed. Return code: {1}",
        4057: PREFIX + "G2_purgeRepository() failed. Return code: {0}",
        4058: PREFIX + "G2_reevaluateEntity({0}, {1}) failed. Return code: {2}",
        4059: PREFIX + "G2_reevaluateEntityWithInfo({0}, {1}) failed. Return code: {2}",
        4060: PREFIX + "G2_reevaluateRecord({0}, {1}, {2}) failed. Return code: {3}",
        4061: (
            PREFIX
            + "G2_reevaluateRecordWithInfo({0}, {1}, {2}) failed. Return code: {3}"
        ),
        4062: PREFIX + "G2_reinit({0}) failed. Return code: {1}",
        4063: PREFIX + "G2_replaceRecord({0}, {1}, {2}, {3}) failed. Return code: {4}",
        4064: (
            PREFIX
            + "G2_replaceRecordWithInfo({0}, {1}, {2}, {3}, {4}) failed. Return"
            " code: {5}"
        ),
        # TODO This needs fixing, wrong number of fields
        4065: PREFIX + "G2_searchByAttributes({0}) failed. Return code: {1}",
        4066: PREFIX + "G2_searchByAttributes_V2({0}, {1}) failed. Return code: {2}",
        4067: PREFIX + "G2_stats() failed. Return code: {0}",
        4068: PREFIX + "G2_whyEntities({0}, {1}) failed. Return code: {2}",
        4069: PREFIX + "G2_whyEntities_V2({0}, {1}, {2}) failed. Return code: {3}",
        4070: PREFIX + "G2_whyEntityByEntityID({0}) failed. Return code: {1}",
        4071: PREFIX + "G2_whyEntityByEntityID_V2({0}, {1}) failed. Return code: {2}",
        4072: PREFIX + "G2_whyEntityByRecordID({0}, {1}) failed. Return code: {2}",
        4073: (
            PREFIX + "G2_whyEntityByRecordID_V2({0}, {1}, {2}) failed. Return code: {3}"
        ),
        4074: PREFIX + "G2_whyRecords({0}, {1}, {2}, {3}) failed. Return code: {4}",
        4075: (
            PREFIX
            + "G2_whyRecords_V2({0}, {1}, {2}, {3}, {4}) failed. Return code: {5}"
        ),
        # TODO This text doesn't make sense without specifying there are 2 ways to init
        4076: (
            PREFIX
            + "G2Engine{0}, {1}) failed. module_name and ini_params must both be set or"
            " both be empty"
        ),
        # TODO Reorder this for V4
        4077: (
            PREFIX + "G2_searchByAttributes_V3({0}, {1}, {2}) failed. Return code: {3}"
        ),
    }
    """ :meta private: """

    # -------------------------------------------------------------------------
    # Interface definition
    # -------------------------------------------------------------------------

    @abstractmethod
    def add_record(
        self,
        data_source_code: str,
        record_id: str,
        # json_data: str,
        json_data: Union[str, Dict[Any, Any]],
        # FIXME load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        The `add_record` method adds a record into the Senzing repository.
        Can be called as many times as desired and from multiple threads at the same time.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            json_data (str | Dict): A JSON document containing the record to be added to the Senzing repository.
            load_id (str, optional): An identifier used to distinguish different load batches/sessions. An empty string is acceptable. Defaults to "".

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/add_record.py
                :linenos:
                :language: python
        """

    # TODO Possible "observer" approach for with info
    # @abstractmethod
    # def add_record(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     json_data: str,
    #     # FIXME load_id is no longer used, being removed from V4 C api?
    #     load_id: str = "",
    #     # with_info: bool = False,
    #     # with_info_obj: object = None,
    #     # with_info_obj: Union[Type[WithInfoObserve], None] = None,
    #     # with_info_obj: Optional[list[str]] = field(default=None),
    #     # with_info_obj: Optional[Union[type[WithInfoObserve], None]] = None,
    #     with_info_obj: Optional[Union[WithInfoResponsesAbstract, None]] = None,
    #     flags: int = 0,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> Union[None, str]:
    #     # TODO: Add in with info details
    #     """
    #     The `add_record` method adds a record into the Senzing repository.
    #     Can be called as many times as desired and from multiple threads at the same time.

    #     Args:
    #         data_source_code (str): Identifies the provenance of the data.
    #         record_id (str): The unique identifier within the records of the same data source.
    #         json_data (str): A JSON document containing the record to be added to the Senzing repository.
    #         load_id (str, optional): An identifier used to distinguish different load batches/sessions. An empty string is acceptable. Defaults to "".

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/add_record.py
    #             :linenos:
    #             :language: python
    #     """

    @abstractmethod
    def add_record_with_info(
        self,
        data_source_code: str,
        record_id: str,
        # json_data: str,
        json_data: Union[str, Dict[Any, Any]],
        # TODO: load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        flags: int = 0,
        **kwargs: Any,
    ) -> str:
        """
        The `add_record_with_info` method adds a record into the Senzing repository
        and returns information on the affected entities.
        Can be called as many times as desired and from multiple threads at the same time.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            json_data (str): A JSON document containing the record to be added to the Senzing repository.
            load_id (str, optional): An identifier used to distinguish different load batches/sessions. An empty string is acceptable. Defaults to "".
            flags (int, optional): Flags used to control information returned. Defaults to 0.

        Returns:
            str: A JSON document containing the ENTITY_ID values of the affected entities.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/add_record_with_info.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/add_record_with_info.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def close_export(self, response_handle: int, **kwargs: Any) -> None:
        """
        The `close_export` method closes the exported document created by `export_json_entity_report`.
        It is part of the `export_json_entity_report`, `fetch_next`, `close_export`
        lifecycle of a list of sized entities.

        Args:
            response_handle (int): A handle created by `export_json_entity_report` or `export_csv_entity_report`.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/export_json_fetch_close.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/export_json_fetch_close.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def count_redo_records(self, **kwargs: Any) -> int:
        """
        The `count_redo_records` method returns the number of records in need of redo-ing.

        Returns:
            int: The number of redo records in Senzing's redo queue.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/count_redo_records.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def delete_record(
        self,
        data_source_code: str,
        record_id: str,
        # TODO: load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        **kwargs: Any,
    ) -> None:
        """
        The `delete_record` method deletes a record from the Senzing repository.
        Can be called as many times as desired and from multiple threads at the same time.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            load_id (str, optional): An identifier used to distinguish different load batches/sessions. An empty string is acceptable. Defaults to "".

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/delete_record.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def delete_record_with_info(
        self,
        data_source_code: str,
        record_id: str,
        # TODO: load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        flags: int = 0,
        **kwargs: Any,
    ) -> str:
        """
        The `delete_record_with_info` method deletes a record from the Senzing repository
        and returns a JSON document containing the IDs of the affected entities.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            load_id (str, optional): An identifier used to distinguish different load batches/sessions. An empty string is acceptable. Defaults to "".
            flags (int, optional): Flags used to control information returned. Defaults to 0.

        Returns:
            str: Flags used to control information returned.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/delete_record_with_info.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/delete_record_with_info.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def destroy(self, **kwargs: Any) -> None:
        """
        The `destroy` method releases resources and performs cleanup for the G2Engine object and any in-memory configurations.
        It should be called after all other calls are complete.

        **Note:** If the `G2Engine` constructor was called with parameters,
        the destructor will automatically call the destroy() method.
        In this case, a separate call to `destroy()` is not needed.

        Example:

        .. code-block:: python

            g2_engine = g2engine.G2Engine(module_name, ini_params)

        Raises:
            g2exception.G2Exception:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/g2engine_init_and_destroy.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def export_config(self, **kwargs: Any) -> str:
        """
        The `export_config` method returns the current Senzing engine configuration.

        Returns:
            str: A JSON document containing the current Senzing Engine configuration.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/export_config.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/export_config.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def export_config_and_config_id(self, **kwargs: Any) -> Tuple[str, int]:
        """
        Similar to `export_config`, the `export_config_and_config_id` method returns the current Senzing engine configuration and it's identifier.

        Returns:
            Tuple[str, int]: [A JSON document containing the current Senzing Engine configuration, The unique identifier of the Senzing Engine configuration]

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/export_config_and_config_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/export_config_and_config_id.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def export_csv_entity_report(
        self,
        csv_column_list: str,
        flags: int = G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> int:
        """
        **Warning:** `export_csv_entity_report` is not recommended for large systems as it does not scale.
        It is recommended larger systems implement real-time replication to a data warehouse.

        The `export_csv_entity_report` method initializes a cursor over a document of exported entities.
        It is part of the `export_csv_entity_report`, `fetch_next`, `close_export`
        lifecycle of a list of entities to export.

        Args:
            csv_column_list (str): A comma-separated list of column names for the CSV export.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS.

        Returns:
            int: A handle that identifies the document to be scrolled through using `fetch_next`.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/export_csv_fetch_close.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/export_csv_fetch_close.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def export_json_entity_report(
        self, flags: int = G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS, **kwargs: Any
    ) -> int:
        """
        **Warning:** `export_json_entity_report` is not recommended for large systems as it does not scale.
        It is recommended larger systems implement real-time replication to a data warehouse.

        The `export_json_entity_report` method initializes a cursor over a document of exported entities.
        It is part of the `export_json_entity_report`, `fetch_next`, `close_export`
        lifecycle of a list of entities to export.

        Args:
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS.

        Returns:
            int: A handle that identifies the document to be scrolled through using `fetch_next`.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/export_json_fetch_close.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/export_json_fetch_close.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def fetch_next(self, response_handle: int, **kwargs: Any) -> str:
        """
        The `fetch_next` method is used to scroll through an exported document one entity at a time.
        Successive calls of `fetch_next` will export successive rows of entity data until there is no more.
        It is part of the `export_json_entity_report` or `export_json_entity_report`, `fetch_next`, `close_export`
        lifecycle of a list of exported entities.

        Args:
            response_handle (int): A handle created by `export_json_entity_report` or `export_json_entity_report`.

        Returns:
            str: TODO:

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/export_json_fetch_close.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/export_json_fetch_close.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def find_interesting_entities_by_entity_id(
        self, entity_id: int, flags: int = 0, **kwargs: Any
    ) -> str:
        """The `find_interesting_entities_by_entity_id` method... TODO:

        Args:
            entity_id (int): The unique identifier of an entity.
            flags (int, optional): Flags used to control information returned. Defaults to 0.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_interesting_entities_by_entity_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_interesting_entities_by_entity_id.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def find_interesting_entities_by_record_id(
        self, data_source_code: str, record_id: str, flags: int = 0, **kwargs: Any
    ) -> str:
        """
        The `find_interesting_entities_by_record_id` method... TODO:

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            flags (int, optional): Flags used to control information returned. Defaults to 0.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_interesting_entities_by_record_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_interesting_entities_by_record_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def find_network_by_entity_id_v2(
    #     self,
    #     entity_list: str,
    #     max_degree: int,
    #     build_out_degree: int,
    #     max_entities: int,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `find_network_by_entity_id_v2` method finds all entities surrounding a requested set of entities.
    #     This includes the requested entities, paths between them, and relations to other nearby entities.
    #     It extends `find_network_by_entity_id` by adding output control flags.

    #     Args:
    #         entity_list (str): A JSON document listing entities.
    #         max_degree (int): The maximum number of degrees in paths between search entities.
    #         build_out_degree (int): The number of degrees of relationships to show around each search entity.
    #         max_entities (int): The maximum number of entities to return in the discovered network.
    #         flags (int, optional): The maximum number of entities to return in the discovered network.. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/find_network_by_entity_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/find_network_by_entity_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def find_network_by_entity_id(
        self,
        # entity_list: str,
        entity_list: Union[str, Dict[Any, Any]],
        max_degree: int,
        build_out_degree: int,
        max_entities: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_network_by_entity_id` method finds all entities surrounding a requested set of entities.
        This includes the requested entities, paths between them, and relations to other nearby entities.
        Returns a JSON document that identifies the path between the each set of search entities (if the path exists),
        and the information for the entities in the path.

        To control output, use `find_network_by_entity_id_v2` instead.

        Args:
            entity_list (str): A JSON document listing entities.
            max_degree (int): The maximum number of degrees in paths between search entities.
            build_out_degree (int): The number of degrees of relationships to show around each search entity.
            max_entities (int): The maximum number of entities to return in the discovered network.
            flags (int, optional): The maximum number of entities to return in the discovered network. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_network_by_entity_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_network_by_entity_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    @abstractmethod
    def find_network_by_record_id(
        self,
        record_list: str,
        max_degree: int,
        build_out_degree: int,
        max_entities: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_network_by_record_id` method finds all entities surrounding a requested set of entities by their RECORD_ID values.
        This includes the requested entities, paths between them, and relations to other nearby entities.
        Returns a JSON document that identifies the path between the each set of search entities (if the path exists),
        and the information for the entities in the path.

        To control output, use `find_network_by_record_id_v2` instead.

        Args:
            record_list (str): A JSON document listing records.
            max_degree (int): The maximum number of degrees in paths between search entities.
            build_out_degree (int): The number of degrees of relationships to show around each search entity.
            max_entities (int): The maximum number of entities to return in the discovered network.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_network_by_record_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_network_by_record_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def find_path_by_entity_id_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     max_degree: int,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `find_path_by_entity_id_v2` method finds single relationship paths between two entities.
    #     Paths are found using known relationships with other entities.
    #     It extends `find_path_by_entity_id` by adding output control flags.

    #     Args:
    #         entity_id_1 (int): The entity ID for the starting entity of the search path.
    #         entity_id_2 (int): The entity ID for the ending entity of the search path.
    #         max_degree (int): The maximum number of degrees in paths between search entities.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/find_path_by_entity_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/find_path_by_entity_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def find_path_by_entity_id(
        self,
        entity_id_1: int,
        entity_id_2: int,
        max_degree: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_path_by_entity_id` method finds the most efficient relationship between two entities path based on the parameters
        and returns a JSON document with an ENTITY_PATHS section that details the path between the entities.
        The ENTITIES sections details information on the entities. Paths are found using known relationships with other entities.
        Paths are found using known relationships with other entities.
        To control output, use `find_path_by_entity_id_v2` instead.

        Args:
            entity_id_1 (int): The entity ID for the starting entity of the search path.
            entity_id_2 (int): The entity ID for the ending entity of the search path.
            max_degree (int): The maximum number of degrees in paths between search entities.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str: A JSON document with an ENTITY_PATHS section that details the path between the entities.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_path_by_entity_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_path_by_entity_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def find_path_by_record_id_v2(
    #     self,
    #     data_source_code_1: str,
    #     record_id_1: str,
    #     data_source_code_2: str,
    #     record_id_2: str,
    #     max_degree: int,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `find_path_by_record_id_v2` method finds all entities surrounding a requested set of entities identified by record identifiers.
    #     This includes the requested entities, paths between them, and relations to other nearby entities.
    #     It extends `find_path_by_record_id` by adding output control flags.

    #     Args:
    #         data_source_code_1 (str): Identifies the provenance of the record for the starting entity of the search path.
    #         record_id_1 (str): The unique identifier within the records of the same data source for the starting entity of the search path.
    #         data_source_code_2 (str): Identifies the provenance of the record for the ending entity of the search path.
    #         record_id_2 (str): The unique identifier within the records of the same data source for the ending entity of the search path.
    #         max_degree (int): The maximum number of degrees in paths between search entities.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/find_path_by_record_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/find_path_by_record_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def find_path_by_record_id(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        max_degree: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_path_by_record_id` method finds the most efficient relationship between
        two entities path based on the parameters by RECORD_ID values
        and returns a JSON document with an ENTITY_PATHS section that details the path between the entities.
        The ENTITIES sections details information on the entities.
        Paths are found using known relationships with other entities.
        The entities are identified by starting and ending records.
        To control output, use `find_path_by_record_id_v2` instead.

        Args:
            data_source_code_1 (str): Identifies the provenance of the record for the starting entity of the search path.
            record_id_1 (str): The unique identifier within the records of the same data source for the starting entity of the search path.
            data_source_code_2 (str): Identifies the provenance of the record for the ending entity of the search path.
            record_id_2 (str): The unique identifier within the records of the same data source for the ending entity of the search path.
            max_degree (int): The maximum number of degrees in paths between search entities.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_path_by_record_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_path_by_record_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def find_path_excluding_by_entity_id_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     max_degree: int,
    #     excluded_entities: str,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `find_path_excluding_by_entity_id_v2` method finds single relationship paths between two entities.
    #     Paths are found using known relationships with other entities.
    #     In addition, it will find paths that exclude certain entities from being on the path.
    #     It extends `find_path_excluding_by_entity_id` by adding output control flags.

    #     Args:
    #         entity_id_1 (int): The entity ID for the starting entity of the search path.
    #         entity_id_2 (int): The entity ID for the ending entity of the search path.
    #         max_degree (int): The maximum number of degrees in paths between search entities.
    #         excluded_entities (str): A JSON document listing entities that should be avoided on the path.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_entity_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_entity_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def find_path_excluding_by_entity_id(
        self,
        entity_id_1: int,
        entity_id_2: int,
        max_degree: int,
        # excluded_entities: str,
        excluded_entities: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_path_excluding_by_entity_id` method finds the most efficient relationship between
        two entities path based on the parameters while preferentially excluding specific ENTITY_IDs,
        and returns a JSON document with an ENTITY_PATHS section that details the path between the entities.
        The ENTITIES sections details information on the entities.
        Paths are found using known relationships with other entities.
        To control output, use `find_path_excluding_by_entity_id_v2` instead.

        By default, any excluded entities are strictly excluded.
        The G2_FIND_PATH_PREFER_EXCLUDE flag sets the exclusion to preferred instead of strict exclusion.
        Preferred exclusion means that if an excluded entity is the only one in the path, it will be used,
        but strict will never include excluded entities in the path.

        Args:
            entity_id_1 (int): The entity ID for the starting entity of the search path.
            entity_id_2 (int): The entity ID for the ending entity of the search path.
            max_degree (int): The maximum number of degrees in paths between search entities.
            excluded_entities (str): A JSON document listing entities that should be avoided on the path.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_entity_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_entity_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def find_path_excluding_by_record_id_v2(
    #     self,
    #     data_source_code_1: str,
    #     record_id_1: str,
    #     data_source_code_2: str,
    #     record_id_2: str,
    #     max_degree: int,
    #     excluded_records: str,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `find_path_excluding_by_record_id_v2` method finds single relationship paths between two entities.
    #     Paths are found using known relationships with other entities.
    #     In addition, it will find paths that exclude certain entities from being on the path.
    #     It extends `find_path_excluding_by_record_id` by adding output control flags.

    #     When excluding entities, the user may choose to either strictly exclude the entities,
    #     or prefer to exclude the entities but still include them if no other path is found.
    #     By default, entities will be strictly excluded.
    #     A "preferred exclude" may be done by specifying the G2_FIND_PATH_PREFER_EXCLUDE control flag.

    #     Args:
    #         data_source_code_1 (str): Identifies the provenance of the record for the starting entity of the search path.
    #         record_id_1 (str): The unique identifier within the records of the same data source for the starting entity of the search path.
    #         data_source_code_2 (str): Identifies the provenance of the record for the ending entity of the search path.
    #         record_id_2 (str): The unique identifier within the records of the same data source for the ending entity of the search path.
    #         max_degree (int): The maximum number of degrees in paths between search entities.
    #         excluded_records (str): A JSON document listing entities that should be avoided on the path.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_record_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_record_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def find_path_excluding_by_record_id(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        max_degree: int,
        # excluded_records: str,
        excluded_records: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_path_excluding_by_record_id` method finds the most efficient relationship between two entities
        path based on the parameters by RECORD_IDs while preferentially excluding specific ENTITY_IDs
        and returns a JSON document with an ENTITY_PATHS section that details the path between the entities.
        The ENTITIES sections details information on the entities.
        Paths are found using known relationships with other entities.
        To control output, use `find_path_excluding_by_record_id_v2` instead.

        By default, any excluded entities are strictly excluded.
        The G2_FIND_PATH_PREFER_EXCLUDE flag sets the exclusion to preferred instead of strict exclusion.
        Preferred exclusion means that if an excluded entity is the only one in the path, it will be used,
        but strict will never include excluded entities in the path.

        Args:
            data_source_code_1 (str): Identifies the provenance of the record for the starting entity of the search path.
            record_id_1 (str): The unique identifier within the records of the same data source for the starting entity of the search path.
            data_source_code_2 (str): Identifies the provenance of the record for the ending entity of the search path.
            record_id_2 (str): The unique identifier within the records of the same data source for the ending entity of the search path.
            max_degree (int): The maximum number of degrees in paths between search entities.
            excluded_records (str): A JSON document listing entities that should be avoided on the path.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str:  A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_record_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_path_excluding_by_record_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def find_path_including_source_by_entity_id_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     max_degree: int,
    #     excluded_entities: str,
    #     required_dsrcs: str,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `find_path_including_source_by_entity_id_v2` method finds single relationship paths between two entities.
    #     In addition, one of the entities along the path must include a specified data source.
    #     Specific entities may also be excluded,
    #     using the same methodology as the `find_path_excluding_by_entity_id_v2` and `find_path_excluding_by_record_id`.
    #     It extends `find_path_including_source_by_entity_id` by adding output control flags.

    #     Args:
    #         entity_id_1 (int): The entity ID for the starting entity of the search path.
    #         entity_id_2 (int): The entity ID for the ending entity of the search path.
    #         max_degree (int): The maximum number of degrees in paths between search entities.
    #         excluded_entities (str): A JSON document listing entities that should be avoided on the path.
    #         required_dsrcs (str): A JSON document listing data sources that should be included on the path.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_entity_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_entity_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def find_path_including_source_by_entity_id(
        self,
        entity_id_1: int,
        entity_id_2: int,
        max_degree: int,
        # excluded_entities: str,
        # required_dsrcs: str,
        excluded_entities: Union[str, Dict[Any, Any]],
        required_dsrcs: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_path_including_source_by_entity_id` method finds the most efficient relationship between two entities
        path based on the parameters, requiring a path entity to include a RECORD_ID from specified data source.
        Specific ENTITY_IDs to exclude can optionally be listed.

        Returns a JSON document with an ENTITY_PATHS section that details the path between the entities.
        The ENTITIES sections details information on the entities. Paths are found using known relationships with other entities.

        By default, any excluded entities are strictly excluded.
        The G2_FIND_PATH_PREFER_EXCLUDE flag sets the exclusion to preferred instead of strict exclusion.
        Preferred exclusion means that if an excluded entity is the only one in the path, it will be used,
        but strict will never include excluded entities in the path.

        To control output, use `find_path_including_source_by_entity_id_v2` instead.

        Args:
            entity_id_1 (int): The entity ID for the starting entity of the search path.
            entity_id_2 (int): The entity ID for the ending entity of the search path.
            max_degree (int): The maximum number of degrees in paths between search entities.
            excluded_entities (str): A JSON document listing entities that should be avoided on the path.
            required_dsrcs (str): A JSON document listing data sources that should be included on the path.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_entity_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_entity_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def find_path_including_source_by_record_id_v2(
    #     self,
    #     data_source_code_1: str,
    #     record_id_1: str,
    #     data_source_code_2: str,
    #     record_id_2: str,
    #     max_degree: int,
    #     excluded_records: str,
    #     required_dsrcs: str,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `find_path_including_source_by_record_id_v2` method finds single relationship paths between two entities.
    #     In addition, one of the entities along the path must include a specified data source.
    #     Specific entities may also be excluded,
    #     using the same methodology as the `find_path_excluding_by_entity_id_v2` and `find_path_excluding_by_record_id_v2`.
    #     It extends `find_path_including_source_by_record_id` by adding output control flags.

    #     Args:
    #         data_source_code_1 (str): Identifies the provenance of the record for the starting entity of the search path.
    #         record_id_1 (str): The unique identifier within the records of the same data source for the starting entity of the search path.
    #         data_source_code_2 (str): Identifies the provenance of the record for the ending entity of the search path.
    #         record_id_2 (str): The unique identifier within the records of the same data source for the ending entity of the search path.
    #         max_degree (int): The maximum number of degrees in paths between search entities.
    #         excluded_records (str): A JSON document listing entities that should be avoided on the path.
    #         required_dsrcs (str):  A JSON document listing data sources that should be included on the path.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_record_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_record_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def find_path_including_source_by_record_id(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        max_degree: int,
        # excluded_records: str,
        # required_dsrcs: str,
        excluded_records: Union[str, Dict[Any, Any]],
        required_dsrcs: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `find_path_including_source_by_record_id` method finds the most efficient relationship between two entities
        path based on the parameters by RECORD_IDs, requiring a path entity to include a RECORD_ID from specified data source.
        Specific ENTITY_IDs to exclude can optionally be listed.

        Returns a JSON document with an ENTITY_PATHS section that details the path between the entities.
        The ENTITIES sections details information on the entities.
        Paths are found using known relationships with other entities.

        By default, any excluded entities are strictly excluded.
        The G2_FIND_PATH_PREFER_EXCLUDE flag sets the exclusion to preferred instead of strict exclusion.
        Preferred exclusion means that if an excluded entity is the only one in the path, it will be used,
        but strict will never include excluded entities in the path.

        To control output, use `find_path_including_source_by_record_id_v2` instead.

        Args:
            data_source_code_1 (str): Identifies the provenance of the record for the starting entity of the search path.
            record_id_1 (str): The unique identifier within the records of the same data source for the starting entity of the search path.
            data_source_code_2 (str): Identifies the provenance of the record for the ending entity of the search path.
            record_id_2 (str): The unique identifier within the records of the same data source for the ending entity of the search path.
            max_degree (int): The maximum number of degrees in paths between search entities.
            excluded_records (str): A JSON document listing entities that should be avoided on the path.
            required_dsrcs (str): A JSON document listing data sources that should be included on the path.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_record_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/find_path_including_source_by_record_id.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def get_active_config_id(self, **kwargs: Any) -> int:
        """
        The `get_active_config_id` method returns the identifier of the currently active Senzing engine configuration.

        Returns:
            int: The identifier of the active Senzing Engine configuration.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/get_active_config_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/get_active_config_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def get_entity_by_entity_id_v2(
    #     self,
    #     entity_id: int,
    #     flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `get_entity_by_entity_id_v2` method returns entity data based on the ID of a resolved identity.
    #     It extends `get_entity_by_entity_id` by adding output control flags.

    #     Args:
    #         entity_id (int): The unique identifier of an entity.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/get_entity_by_entity_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/get_entity_by_entity_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def get_entity_by_entity_id(
        self,
        entity_id: int,
        flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `get_entity_by_entity_id` method returns entity data based on the ID of a resolved identity.
        To control output, use `get_entity_by_entity_id_v2` instead.

        Args:
            entity_id (int): The unique identifier of an entity.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/get_entity_by_entity_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/get_entity_by_entity_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def get_entity_by_record_id_v2(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `get_entity_by_record_id_v2` method returns entity data based on the ID of a record which is a member of the entity.
    #     It extends `get_entity_by_record_id` by adding output control flags.

    #     Args:
    #         data_source_code (str): Identifies the provenance of the data.
    #         record_id (str): The unique identifier within the records of the same data source.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/get_entity_by_record_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/get_entity_by_record_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def get_entity_by_record_id(
        self,
        data_source_code: str,
        record_id: str,
        flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `get_entity_by_record_id` method returns entity data based on the ID of a record which is a member of the entity.
        To control output, use `get_entity_by_record_id_v2` instead.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/get_entity_by_record_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/get_entity_by_record_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def get_record_v2(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_RECORD_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `get_record_v2` method returns a JSON document of a single record from the Senzing repository.
    #     It extends `get_record` by adding output control flags.
    #     Can be called as many times as desired and from multiple threads at the same time.

    #     Args:
    #         data_source_code (str): Identifies the provenance of the data.
    #         record_id (str): The unique identifier within the records of the same data source.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_RECORD_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/get_record_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/get_record_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def get_record(
        self,
        data_source_code: str,
        record_id: str,
        flags: int = G2EngineFlags.G2_RECORD_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `get_record` method returns a JSON document of a single record from the Senzing repository.
        To control output, use `get_record_v2` instead.
        Can be called as many times as desired and from multiple threads at the same time.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_RECORD_DEFAULT_FLAGS.

        Returns:
            str: A JSON document of a single record.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/get_record.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/get_record.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def get_redo_record(self, **kwargs: Any) -> str:
        """
        The `get_redo_record` method returns the next internally queued redo record from the Senzing repository.
        Usually, the `process_redo_record` or `process_redo_record_with_info` method is called to process the redo record
        retrieved by `get_redo_record`.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/get_redo_record.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/get_redo_record.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def get_repository_last_modified_time(self, **kwargs: Any) -> int:
        """
        The `get_repository_last_modified_time` method retrieves the last modified time of the Senzing repository,
        measured in the number of seconds between the last modified time and January 1, 1970 12:00am GMT (epoch time).

        Returns:
            int: A Unix Timestamp.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/get_repository_last_modified_time.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/get_repository_last_modified_time.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def get_virtual_entity_by_record_id_v2(
    #     self,
    #     record_list: str,
    #     flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     TODO: The `get_virtual_entity_by_record_id_v2` method...
    #     It extends `get_virtual_entity_by_record_id` by adding output control flags.

    #     Args:
    #         record_list (str): A JSON document of one or more records by DATA_SOURCE and RECORD_ID pairs, formatted as `{"RECORDS":[{"DATA_SOURCE":"DS1","RECORD_ID":"R1"},{"DATA_SOURCE":"DS2","RECORD_ID":"R2"}]}`.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/get_virtual_entity_by_record_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/get_virtual_entity_by_record_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def get_virtual_entity_by_record_id(
        self,
        # record_list: str,
        record_list: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `get_virtual_entity_by_record_id` method creates a view of a virtual entity
        using a list of existing loaded records.
        The virtual entity is composed of only those records and their features.
        Entity resolution is not performed.
        To control output, use `get_virtual_entity_by_record_id_v2` instead.

        Args:
            record_list (str): A JSON document of one or more records by DATA_SOURCE and RECORD_ID pairs, formatted as `{"RECORDS":[{"DATA_SOURCE":"DS1","RECORD_ID":"R1"},{"DATA_SOURCE":"DS2","RECORD_ID":"R2"}]}`.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS.

        Returns:
            str:  A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/get_virtual_entity_by_record_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/get_virtual_entity_by_record_id.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def how_entity_by_entity_id_v2(
    #     self,
    #     entity_id: int,
    #     flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     TODO: The `how_entity_by_entity_id_v2` method...
    #     It extends `how_entity_by_entity_id` by adding output control flags.

    #     Args:
    #         entity_id (int): The unique identifier of an entity.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str:  A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/how_entity_by_entity_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/how_entity_by_entity_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def how_entity_by_entity_id(
        self,
        entity_id: int,
        flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        TODO: The `how_entity_by_entity_id` method determines and details steps-by-step *how* records resolved to an ENTITY_ID.

        In most cases, *how* provides more detailed information than *why* as the resolution is detailed step-by-step.

        To control output, use `how_entity_by_entity_id_v2` instead.

        Args:
            entity_id (int): The unique identifier of an entity.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/how_entity_by_entity_id.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/how_entity_by_entity_id.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def init(
        # self, module_name: str, ini_params: str, verbose_logging: int = 0, **kwargs: Any
        self,
        module_name: str,
        ini_params: Union[str, Dict[Any, Any]],
        verbose_logging: int = 0,
        **kwargs: Any,
    ) -> None:
        """
        The `init` method initializes the Senzing G2Engine object.
        It must be called prior to any other calls.

        **Note:** If the G2Engine constructor is called with parameters,
        the constructor will automatically call the `init()` method.
        In this case, a separate call to `init()` is not needed.

        Example:

        .. code-block:: python

            g2_engine = g2engine.G2Engine(module_name, ini_params)

        Args:
            module_name (str): A short name given to this instance of the G2Engine object, to help identify it within system logs.
            ini_params (str): A JSON string containing configuration parameters.
            verbose_logging (int): `Optional:` A flag to enable deeper logging of the G2 processing. 0 for no Senzing logging; 1 for logging. Default: 0

        Raises:
            TypeError: Incorrect datatype of input parameter.

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/g2engine_init_and_destroy.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def init_with_config_id(
        self,
        module_name: str,
        # ini_params: str,
        ini_params: Union[str, Dict[Any, Any]],
        init_config_id: int,
        verbose_logging: int = 0,
        **kwargs: Any,
    ) -> None:
        """
        The `init_with_config_id` method initializes the Senzing G2Engine object with a non-default configuration ID.
        It must be called prior to any other calls.

        **Note:** If the G2Engine constructor is called with parameters,
        the constructor will automatically call the `init()` method.
        In this case, a separate call to `init()` is not needed.

        Example:

        .. code-block:: python

            g2_engine = g2engine.G2Engine(module_name, ini_params, init_config_id)

        Args:
            module_name (str): A short name given to this instance of the G2Engine object, to help identify it within system logs.
            ini_params (str): A JSON string containing configuration parameters.
            init_config_id (int): The configuration ID used for the initialization.
            verbose_logging (int): `Optional:` A flag to enable deeper logging of the G2 processing. 0 for no Senzing logging; 1 for logging. Default: 0

        Raises:
            TypeError: Incorrect datatype of input parameter.
            g2exception.G2Exception:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/g2engine_init_with_config_id.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def prime_engine(self, **kwargs: Any) -> None:
        """
        The `prime_engine` method Initializes high resource consumption components of Senzing
        used in some functions. If this call is not made, these resources are initialized the
        first time they are needed and can cause unusually long processing times the first time
        a function is called that requires these resources.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/prime_engine.py
                :linenos:
                :language: python
        """

    @abstractmethod
    # def process(self, record: str, **kwargs: Any) -> None:
    def process(self, record: Union[str, Dict[Any, Any]], **kwargs: Any) -> None:
        """
        The `process` method processes the redo record.
        Usually the redo record is retrieved with `get_redo_record`.

        Args:
            record (str):  A JSON document containing the redo record to be processed.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/process.py
                :linenos:
                :language: python
        """

    @abstractmethod
    # def process_with_info(self, record: str, flags: int, **kwargs: Any) -> str:
    def process_with_info(
        self, record: Union[str, Dict[Any, Any]], flags: int, **kwargs: Any
    ) -> str:
        """_summary_
        The `process_with_info` method processes the redo record
        and returns a JSON document containing the ENTITY_ID values of the affected entities.

        Args:
            record (str): A JSON document containing the record to be added to the Senzing repository.
            flags (int): Flags used to control information returned.

        Returns:
            str:  A JSON document containing the ENTITY_ID values of the affected entities.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/process_with_info.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/process_with_info.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def purge_repository(self, **kwargs: Any) -> None:
        """
        **Warning:**
        The `purge_repository` method removes every record in the Senzing repository.

        Before calling `purge_repository` all other instances of the Senzing API
        MUST be destroyed or shutdown.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/purge_repository.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def reevaluate_entity(self, entity_id: int, flags: int = 0, **kwargs: Any) -> None:
        """
        The `reevaluate_entity` method reevaluates the specified entity.

        Args:
            entity_id (int): The unique identifier of an entity.
            flags (int, optional): Flags used to control information returned. Defaults to 0.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/reevaluate_entity.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def reevaluate_entity_with_info(
        self, entity_id: int, flags: int = 0, **kwargs: Any
    ) -> str:
        """
        TODO: The `reevaluate_entity_with_info` method reevaluates the specified entity.
        and returns a JSON document containing the ENTITY_ID values of the affected entities.

        Args:
            entity_id (int): The unique identifier of an entity.
            flags (int, optional): Flags used to control information returned. Defaults to 0.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/reevaluate_entity_with_info.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/reevaluate_entity_with_info.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def reevaluate_record(
        self, data_source_code: str, record_id: str, flags: int = 0, **kwargs: Any
    ) -> None:
        """
        The `reevaluate_record` method reevaluates a specific record.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            flags (int, optional):  Flags used to control information returned. Defaults to 0.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/reevaluate_entity.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def reevaluate_record_with_info(
        self, data_source_code: str, record_id: str, flags: int = 0, **kwargs: Any
    ) -> str:
        """
        The `reevaluate_record_with_info` reevaluates a specific record
        and returns a JSON document containing the ENTITY_ID values of the affected entities.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            flags (int, optional):  Flags used to control information returned. Defaults to 0.

        Returns:
            str: A JSON document containing the ENTITY_ID values of the affected entities.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/reevaluate_record_with_info.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/reevaluate_record_with_info.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def reinit(self, init_config_id: int, **kwargs: Any) -> None:
        """
        The `reinit` method re-initializes the Senzing G2Engine object using a specific configuration
        identifier. A list of available configuration identifiers can be retrieved using
        `g2configmgr.get_config_list`.

        Args:
            init_config_id (int): The configuration ID used for the initialization

        Raises:
            TypeError: Incorrect datatype of input parameter.
            g2exception.G2Exception: init_config_id does not exist.

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/g2engine_reinit.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def replace_record(
        self,
        data_source_code: str,
        record_id: str,
        # json_data: str,
        json_data: Union[str, Dict[Any, Any]],
        # TODO: load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        **kwargs: Any,
    ) -> None:
        """
        The `replace_record` method updates/replaces a record in the Senzing repository.
        If record doesn't exist, a new record is added to the data repository.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            json_data (str): A JSON document containing the record to be added to the Senzing repository.
            load_id (str, optional): An identifier used to distinguish different load batches/sessions. An empty string is acceptable. Defaults to "".

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/replace_record.py
                :linenos:
                :language: python
        """

    @abstractmethod
    def replace_record_with_info(
        self,
        data_source_code: str,
        record_id: str,
        # json_data: str,
        json_data: Union[str, Dict[Any, Any]],
        # TODO: load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        flags: int = 0,
        **kwargs: Any,
    ) -> str:
        """
        The `replace_record_with_info` method updates/replaces a record in the Senzing repository
        and returns information on the affected entities.
        If record doesn't exist, a new record is added to the data repository.

        Args:
            data_source_code (str): Identifies the provenance of the data.
            record_id (str): The unique identifier within the records of the same data source.
            json_data (str): A JSON document containing the record to be added to the Senzing repository.
            load_id (str, optional): An identifier used to distinguish different load batches/sessions. An empty string is acceptable. Defaults to "".
            flags (int, optional): Flags used to control information returned. Defaults to 0.

        Returns:
            str:  A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/replace_record_with_info.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/replace_record_with_info.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def search_by_attributes_v2(
    #     self,
    #     json_data: str,
    #     flags: int = G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `search_by_attributes_v2` method retrieves entity data based on a user-specified set of entity attributes.
    #     It extends `search_by_attributes` by adding output control flags.

    #     Args:
    #         json_data (str): TODO:
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/search_by_attributes_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/search_by_attributes_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def search_by_attributes_v3(
    #     self,
    #     json_data: str,
    #     search_profile: str,
    #     flags: int = G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `search_by_attributes_v3` method retrieves entity data based on a user-specified set of entity attributes.
    #     It extends `search_by_attributes` by adding output control flags and supporting a `search_profile`.

    #     Args:
    #         json_data (str): TODO:
    #         search_profile (str): TODO:
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/search_by_attributes_v3.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/search_by_attributes_v3.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def search_by_attributes(
        self,
        # json_data: str,
        json_data: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `search_by_attributes` method retrieves entity data based on a user-specified set of entity attributes.
        To control output, use `search_by_attributes_v2` instead.
        To specify a search profile, use `search_by_attributes_v3` instead.

        Args:
            json_data (str):  A JSON document with the attribute data to search for.
            flags (int, optional): _description_. Defaults to G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/search_by_attributes.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/search_by_attributes.txt
                :linenos:
                :language: json
        """

    @abstractmethod
    def stats(self, **kwargs: Any) -> str:
        """
        The `stats` method retrieves workload statistics for the current process.
        These statistics will automatically reset after retrieval.

        Returns:
            str:  A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/stats.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/stats.txt
                :linenos:
                :language: json
        """

    # @abstractmethod
    # def why_entities_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `why_entities_v2` method explains why records belong to their resolved entities.
    #     `why_entities_v2` will compare the record data within an entity
    #     against the rest of the entity data and show why they are connected.
    #     This is calculated based on the features that record data represents.
    #     It extends `why_entities` by adding output control flags.

    #     Args:
    #         entity_id_1 (int): The entity ID for the starting entity of the search path.
    #         entity_id_2 (int): The entity ID for the ending entity of the search path.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/why_entities_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/why_entities_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def why_entities(
        self,
        entity_id_1: int,
        entity_id_2: int,
        flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `why_entities` method determines why entities did not resolve or why they do relate.

        To control output, use `why_entities_v2` instead.

        Args:
            entity_id_1 (int): The entity ID for the starting entity of the search path.
            entity_id_2 (int): The entity ID for the ending entity of the search path.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/why_entities.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/why_entities.txt
                :linenos:
                :language: json
        """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def why_entity_by_entity_id_v2(
    #     self,
    #     entity_id: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `why_entity_by_entity_id_v2` method explains why records belong to their resolved entities.
    #     It extends `why_entity_by_entity_id` by adding output control flags.

    #     Args:
    #         entity_id (str): The unique identifier of an entity for the starting entity of the search path.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_entity_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_entity_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    # NOTE Being removed in V4
    # @abstractmethod
    # def why_entity_by_entity_id(
    #     self,
    #     entity_id: int,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `why_entity_by_entity_id` method determines *why* records resolved to an ENTITY_ID.
    #     Returns a JSON document that gives the results of the record analysis.

    #     It has a “WHY_KEY”, which is similar to a match key, in defining the relevant connected data.
    #     It shows candidate keys for features that initially cause the records to be analyzed for a relationship,
    #     plus a series of feature scores that show how similar the feature data was.

    #     The response JSON document also contains a separate ENTITIES section,
    #     with the full information about the resolved entity.

    #     The recommended composite flag is G2_WHY_ENTITY_DEFAULT_FLAGS.
    #     Additional recommended flags are G2_ENTITY_OPTION_INCLUDE_INTERNAL_FEATURES and G2_ENTITY_OPTION_INCLUDE_FEATURE_STATS,
    #     which provide detailed feature data that is useful for understanding the WHY_RESULTS data.

    #     To control output, use `why_entity_by_entity_id_v2` instead.

    #     Args:
    #         entity_id (int): The unique identifier of an entity for the starting entity of the search path.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_entity_id.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_entity_id.txt
    #             :linenos:
    #             :language: json
    #     """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def why_entity_by_record_id_v2(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `why_entity_by_record_id_v2` method explains why records belong to their resolved entities.
    #     It extends `why_entity_by_record_id` by adding output control flags.

    #     Args:
    #         data_source_code (str): Identifies the provenance of the data.
    #         record_id (str): The unique identifier within the records of the same data source.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_record_id_v2.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_record_id_v2.txt
    #             :linenos:
    #             :language: json
    #     """

    # NOTE Being removed in V4
    # @abstractmethod
    # def why_entity_by_record_id(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `why_entity_by_record_id` method determines *why* records resolved to an ENTITY_ID by a RECORD_ID.
    #     Returns a JSON document that gives the results of the record analysis.

    #     It has a “WHY_KEY”, which is similar to a match key, in defining the relevant connected data.
    #     It shows candidate keys for features that initially cause the records to be analyzed for a relationship,
    #     plus a series of feature scores that show how similar the feature data was.

    #     The response JSON document also contains a separate ENTITIES section,
    #     with the full information about the resolved entity.

    #     The recommended composite flag is G2_WHY_ENTITY_DEFAULT_FLAGS.
    #     Additional recommended flags are G2_ENTITY_OPTION_INCLUDE_INTERNAL_FEATURES and G2_ENTITY_OPTION_INCLUDE_FEATURE_STATS,
    #     which provide detailed feature data that is useful for understanding the WHY_RESULTS data.

    #     To control output, use `why_entity_by_record_id_v2` instead.

    #     Args:
    #         data_source_code (str): Identifies the provenance of the data.
    #         record_id (str): The unique identifier within the records of the same data source.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_record_id.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_record_id.txt
    #             :linenos:
    #             :language: json
    #     """

    # TODO: This should be going away in V4?
    # @abstractmethod
    # def why_records_v2(
    #     self,
    #     data_source_code_1: str,
    #     record_id_1: str,
    #     data_source_code_2: str,
    #     record_id_2: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     **kwargs: Any,
    # ) -> str:
    #     """
    #     The `why_records_v2` determines if any two records can or cannot resolve together, or if they relate.
    #     It extends `why_records` by adding output control flags.

    #     Args:
    #         data_source_code_1 (str): Identifies the provenance of the data.
    #         record_id_1 (str): The unique identifier within the records of the same data source.
    #         data_source_code_2 (str): Identifies the provenance of the data.
    #         record_id_2 (str): The unique identifier within the records of the same data source.
    #         flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

    #     Returns:
    #         str: A JSON document.

    #     Raises:

    #     .. collapse:: Example:

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_record_id.py
    #             :linenos:
    #             :language: python

    #         **Output:**

    #         .. literalinclude:: ../../examples/g2engine/why_entity_by_record_id.txt
    #             :linenos:
    #             :language: json
    #     """

    @abstractmethod
    def why_records(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> str:
        """
        The `why_records` determines if any two records can or cannot resolve together, or if they relate.

        To control output, use `why_records_v2` instead.

        Args:
            data_source_code_1 (str): Identifies the provenance of the data.
            record_id_1 (str): The unique identifier within the records of the same data source.
            data_source_code_2 (str): Identifies the provenance of the data.
            record_id_2 (str): The unique identifier within the records of the same data source.
            flags (int, optional): Flags used to control information returned. Defaults to G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS.

        Returns:
            str: A JSON document.

        Raises:

        .. collapse:: Example:

            .. literalinclude:: ../../examples/g2engine/why_records.py
                :linenos:
                :language: python

            **Output:**

            .. literalinclude:: ../../examples/g2engine/why_records.txt
                :linenos:
                :language: json
        """

    # TODO: Is why_record_in_entity missing?
    # TODO: MJD: Mistake on my part.  Need to add it.

    # -------------------------------------------------------------------------
    # Convenience methods
    # -------------------------------------------------------------------------

    def get_record_as_dict(
        # self, data_source_code: str, record_id: str, **kwargs: Any
        self,
        data_source_code: str,
        record_id: str,
        flags: int = G2EngineFlags.G2_RECORD_DEFAULT_FLAGS,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """TODO: document"""
        return cast(
            Dict[str, Any],
            json.loads(self.get_record(data_source_code, record_id, flags, **kwargs)),
        )
