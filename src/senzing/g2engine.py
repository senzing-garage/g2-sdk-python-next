"""
The g2engine package is used to insert, update, delete and query records and entities in the Senzing product.
It is a wrapper over Senzing's G2Engine C binding.
It conforms to the interface specified in
`g2engine_abstract.py <https://github.com/Senzing/g2-sdk-python-next/blob/main/src/senzing/g2engine_abstract.py>`_

# TODO: Also pythonpath and engine vars?
To use g2engine,
the **LD_LIBRARY_PATH** environment variable must include a path to Senzing's libraries.

Example:

.. code-block:: bash

    export LD_LIBRARY_PATH=/opt/senzing/g2/lib
"""

# pylint: disable=R0903,C0302,R0915
# AC - Temp disables to get changes in for move to senzing garage
# pylint: disable=W0511,W1113,W0613
# NOTE Used for ctypes type hinting - https://stackoverflow.com/questions/77619149/python-ctypes-pointer-type-hinting
from __future__ import annotations
import os

from ctypes import (
    _Pointer,
    POINTER,
    Structure,
    c_char,
    c_char_p,
    c_int,
    c_longlong,
    c_size_t,
    c_uint,
    c_void_p,
    cdll,
    CDLL,
)
from types import TracebackType
from typing import Any, Dict, Optional, Tuple, Type, Union

# TODO Possible "observer" approach for with info
# from .g2engine_abstract import G2EngineAbstract, WithInfoResponsesAbstract
from .g2engine_abstract import G2EngineAbstract
from .g2engineflags import G2EngineFlags
from .g2exception import G2Exception, new_g2exception
from .g2helpers import (
    as_c_char_p,
    as_c_int,
    as_python_int,
    as_python_str,
    as_str,
    as_uintptr_t,
    find_file_in_path,
)

from .g2version import is_supported_senzingapi_version


# Metadata

# TODO Possible "observer" approach for with info
# __all__ = ["G2Engine", "WithInfoResponses"]
__all__ = ["G2Engine"]
__version__ = "0.0.1"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = "2023-10-30"
__updated__ = "2023-11-15"

SENZING_PRODUCT_ID = (  # See https://github.com/Senzing/knowledge-base/blob/main/lists/senzing-component-ids.md
    "5043"
)
CALLER_SKIP = 6  # Number of stack frames to skip when reporting location in Exception.

# -----------------------------------------------------------------------------
# Context Manager Classes
# -----------------------------------------------------------------------------


class FreeCResources:
    """Free C resources"""

    # TODO Is this correct for type hinting?
    def __init__(self, handle: CDLL, resource: _Pointer[c_char]) -> None:
        self.handle = handle
        self.resource = resource

    def __enter__(self) -> None:
        pass

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.handle.G2GoHelper_free(self.resource)


# -----------------------------------------------------------------------------
# Data Classes used for with info
# -----------------------------------------------------------------------------


# TODO Possible "observer" approach for with info
# @dataclass(slots=True)
# class WithInfoResponses(WithInfoResponsesAbstract):
#     """ """

#     _responses: deque[str] = field(default_factory=deque)
#     _lock = Lock()

#     def append(self, response: str) -> None:
#         self._responses.append(response)

#     def get_and_clear(self) -> deque[str]:
#         # NOTE Use lock to block and return a copy of the responses so can clear the current responses in a thread safe manner
#         with self._lock:
#             _responses_copy = self._responses.copy()
#             self._responses.clear()
#         return _responses_copy

#     def len(self) -> int:
#         return len(self._responses)

#     def sizeof(self) -> int:
#         return sys.getsizeof(self._responses)


# -----------------------------------------------------------------------------
# Classes that are result structures from calls to Senzing
# -----------------------------------------------------------------------------


class G2ResponseReturnCodeResult(Structure):
    """Simple response, return_code structure"""

    _fields_ = [
        ("response", POINTER(c_char)),
        ("return_code", c_longlong),
    ]


class G2AddRecordWithInfoResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_addRecordWithInfo_result"""


class G2DeleteRecordWithInfoResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_deleteRecordWithInfo_result"""


class G2ExportConfigAndConfigIDResult(Structure):
    """In golang_helpers.h G2_exportConfigAndConfigID_result"""

    _fields_ = [
        ("config_id", c_longlong),
        ("config", POINTER(c_char)),
        ("return_code", c_longlong),
    ]


class G2ExportConfigResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_exportConfig_result"""


class G2ExportCSVEntityReportResult(Structure):
    """In golang_helpers.h G2_exportCSVEntityReport_result"""

    _fields_ = [
        ("export_handle", c_void_p),
        ("return_code", c_longlong),
    ]


class G2ExportJSONEntityReportResult(Structure):
    """In golang_helpers.h G2_exportJSONEntityReport_result"""

    _fields_ = [
        ("export_handle", c_void_p),
        ("return_code", c_longlong),
    ]


class G2FetchNextResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_fetchNext_result"""


class G2FindInterestingEntitiesByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findInterestingEntitiesByEntityID_result"""


class G2FindInterestingEntitiesByRecordIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findInterestingEntitiesByRecordID_result"""


class G2FindNetworkByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findNetworkByEntityID_result"""


class G2FindNetworkByEntityIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findNetworkByEntityID_V2_result"""


class G2FindNetworkByRecordIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findNetworkByRecordID_result"""


class G2FindNetworkByRecordIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findNetworkByRecordID_V2_result"""


class G2FindPathByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathByEntityID_result"""


class G2FindPathByEntityIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathByEntityID_V2_result"""


class G2FindPathByRecordIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathByRecordID_result"""


class G2FindPathByRecordIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathByRecordID_V2_result"""


class G2FindPathExcludingByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathExcludingByEntityID_result"""


class G2FindPathExcludingByEntityIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathExcludingByEntityID_V2_result"""


class G2FindPathExcludingByRecordIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathExcludingByRecordID_result"""


class G2FindPathExcludingByRecordIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathExcludingByRecordID_V2_result"""


class G2FindPathIncludingSourceByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathIncludingSourceByEntityID_result"""


class G2FindPathIncludingSourceByEntityIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathIncludingSourceByEntityID_V2_result"""


class G2FindPathIncludingSourceByRecordIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathIncludingSourceByRecordID_result"""


class G2FindPathIncludingSourceByRecordIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_findPathIncludingSourceByRecordID_V2_result"""


class G2GetActiveConfigIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getActiveConfigID_result"""


class G2GetEntityByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getEntityByEntityID_result"""


class G2GetEntityByEntityIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getEntityByEntityID_V2_result"""


class G2GetEntityByRecordIDResult(Structure):
    """In golang_helpers.h G2_getEntityByRecordID_result"""


class G2GetEntityByRecordIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getEntityByRecordID_V2_result"""


class G2GetRecordResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getRecord_result"""


class G2GetRecordV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getRecord_V2_result"""


class G2GetRedoRecordResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getRedoRecord_result"""


class G2GetRepositoryLastModifiedTimeResult(Structure):
    """In golang_helpers.h G2_getRepositoryLastModifiedTime_result"""

    _fields_ = [
        ("time", c_longlong),
        ("return_code", c_longlong),
    ]


class G2GetVirtualEntityByRecordIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getVirtualEntityByRecordID_result"""


class G2GetVirtualEntityByRecordIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_getVirtualEntityByRecordID_V2_result"""


class G2HowEntityByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_howEntityByEntityID_result"""


class G2HowEntityByEntityIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_howEntityByEntityID_V2_result"""


class G2ProcessWithInfoResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_processWithInfo_result"""


class G2ReevaluateEntityWithInfoResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_reevaluateEntityWithInfo_result"""


class G2ReevaluateRecordWithInfoResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_reevaluateRecordWithInfo_result"""


class G2ReplaceRecordWithInfoResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_replaceRecordWithInfo_result"""


class G2SearchByAttributesResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_searchByAttributes_result"""


class G2SearchByAttributesV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_searchByAttributes_V2_result"""


class G2SearchByAttributesV3Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_searchByAttributes_V2_result"""


class G2StatsResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_stats_result"""


class G2WhyEntitiesResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyEntities_result"""


class G2WhyEntitiesV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyEntities_V2_result"""


class G2WhyEntityByEntityIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyEntityByEntityID_result"""


class G2WhyEntityByEntityIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyEntityByEntityID_V2_result"""


class G2WhyEntityByRecordIDResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyEntityByRecordID_result"""


class G2WhyEntityByRecordIDV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyEntityByRecordID_V2_result"""


class G2WhyRecordsResult(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyRecords_result"""


class G2WhyRecordsV2Result(G2ResponseReturnCodeResult):
    """In golang_helpers.h G2_whyRecords_V2_result"""


# -----------------------------------------------------------------------------
# G2Engine class
# -----------------------------------------------------------------------------


# TODO init_config_id ?
# TODO Optional on Parameters needs to be explained for different init methods
# TODO Raises could be more granular
class G2Engine(G2EngineAbstract):
    """
    The `init` method initializes the Senzing G2Engine object.
    It must be called prior to any other calls.

    **Note:** If the G2Engine constructor is called with parameters,
    the constructor will automatically call the `init()` method.

    Example:

    .. code-block:: python

        g2_engine = g2engine.G2Engine(module_name, ini_params)


    If the G2Engine constructor is called without parameters,
    the `init()` method must be called to initialize the use of G2Engine.

    Example:

    .. code-block:: python

        g2_engine = g2engine.G2Engine()
        g2_engine.init(module_name, ini_params, verbose_logging)

    Either `module_name` and `ini_params` must both be specified or neither must be specified.
    Just specifying one or the other results in a **G2Exception**.

    Parameters:
        module_name:
            `Optional:` A name for the auditing node, to help identify it within system logs. Default: ""
        ini_params:
            `Optional:` A JSON string containing configuration parameters. Default: ""
        init_config_id:
            `Optional:` Specify the ID of a specific Senzing configuration. Default: 0 - Use default Senzing configuration
        verbose_logging:
            `Optional:` A flag to enable deeper logging of the G2 processing. 0 for no Senzing logging; 1 for logging. Default: 0

    Raises:
        G2Exception: Raised when input parameters are incorrect.

    .. collapse:: Example:

        .. literalinclude:: ../../examples/g2engine/g2engine_constructor.py
            :linenos:
            :language: python
    """

    # -------------------------------------------------------------------------
    # Python dunder/magic methods
    # -------------------------------------------------------------------------

    def __init__(
        self,
        module_name: str = "",
        # ini_params: str = "",
        ini_params: Union[str, Dict[Any, Any]] = "",
        verbose_logging: int = 0,
        init_config_id: int = 0,
        **kwargs: Any,
    ) -> None:
        """
        Constructor

        For return value of -> None, see https://peps.python.org/pep-0484/#the-meaning-of-annotations
        """
        # pylint: disable=W0613

        # Verify parameters.

        self.auto_init = False
        self.ini_params = as_str(ini_params)
        self.init_config_id = init_config_id
        self.module_name = module_name
        self.noop = ""
        self.verbose_logging = verbose_logging

        # Determine if Senzing API version is acceptable.

        is_supported_senzingapi_version()

        # Load binary library.

        try:
            if os.name == "nt":
                self.library_handle = cdll.LoadLibrary(find_file_in_path("G2.dll"))
            else:
                self.library_handle = cdll.LoadLibrary("libG2.so")
        except OSError as err:
            # TODO Additional explanation e.g. is LD_LIBRARY_PATH set
            raise G2Exception("Failed to load the G2 library") from err

        # Initialize C function input parameters and results.
        # Must be synchronized with g2/sdk/c/libg2engine.h

        self.library_handle.G2_addRecord.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
        ]
        self.library_handle.G2_addRecord.restype = c_int
        # self.library_handle.G2_addRecordWithInfo.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_addRecordWithInfo_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_addRecordWithInfo_helper.restype = (
            G2AddRecordWithInfoResult
        )
        # self.library_handle.G2_addRecordWithInfoWithReturnedRecordID.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_char_p, c_size_t, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def3]
        # self.library_handle.G2_addRecordWithInfoWithReturnedRecordID.restype = c_int
        # self.library_handle.G2_addRecordWithReturnedRecordID.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_size_t]
        # self.library_handle.G2_checkRecord.argtypes = [ c_char_p, c_char_p, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_clearLastException.argtypes = []
        self.library_handle.G2_clearLastException.restype = None
        # self.library_handle.G2_closeExport.argtypes = [c_void_p]
        # self.library_handle.G2_closeExport.restype = c_int
        self.library_handle.G2_closeExport_helper.argtypes = [
            POINTER(c_uint),
        ]
        self.library_handle.G2_closeExport_helper.restype = c_longlong
        # NOTE Added
        self.library_handle.G2_countRedoRecords.argtypes = []
        self.library_handle.G2_countRedoRecords.restype = c_longlong
        self.library_handle.G2_deleteRecord.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
        ]
        self.library_handle.G2_deleteRecord.restype = c_int
        self.library_handle.G2_deleteRecordWithInfo_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_deleteRecordWithInfo_helper.restype = (
            G2DeleteRecordWithInfoResult
        )
        self.library_handle.G2_destroy.argtypes = []
        self.library_handle.G2_destroy.restype = c_longlong
        # self.library_handle.G2_exportConfig.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_exportConfig_helper.argtypes = []
        self.library_handle.G2_exportConfig_helper.restype = G2ExportConfigResult
        self.library_handle.G2_exportConfigAndConfigID_helper.argtypes = []
        self.library_handle.G2_exportConfigAndConfigID_helper.restype = (
            G2ExportConfigAndConfigIDResult
        )
        # self.library_handle.G2_exportCSVEntityReport.argtypes = [c_char_p, c_longlong, POINTER(c_void_p)]
        # self.library_handle.G2_exportCSVEntityReport.restype = c_int
        self.library_handle.G2_exportCSVEntityReport_helper.argtypes = [
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_exportCSVEntityReport_helper.restype = (
            G2ExportCSVEntityReportResult
        )
        # self.library_handle.G2_exportJSONEntityReport.argtypes = [c_longlong, POINTER(c_void_p)]
        # self.library_handle.G2_exportJSONEntityReport.restype = c_int
        self.library_handle.G2_exportJSONEntityReport_helper.argtypes = [c_longlong]
        self.library_handle.G2_exportJSONEntityReport_helper.restype = (
            G2ExportJSONEntityReportResult
        )
        # self.library_handle.G2_fetchNext.argtypes = [c_void_p, c_char_p, c_size_t]
        # self.library_handle.G2_fetchNext.restype = c_int
        self.library_handle.G2_fetchNext_helper.argtypes = [
            POINTER(c_uint),
        ]
        self.library_handle.G2_fetchNext_helper.restype = G2FetchNextResult
        # self.library_handle.G2_findInterestingEntitiesByEntityID.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findInterestingEntitiesByEntityID.restype = c_int
        self.library_handle.G2_findInterestingEntitiesByEntityID_helper.argtypes = [
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findInterestingEntitiesByEntityID_helper.restype = (
            G2FindInterestingEntitiesByEntityIDResult
        )
        # self.library_handle.G2_findInterestingEntitiesByRecordID.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findInterestingEntitiesByRecordID.restype = c_int
        self.library_handle.G2_findInterestingEntitiesByRecordID_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_findInterestingEntitiesByRecordID_helper.restype = (
            G2FindInterestingEntitiesByRecordIDResult
        )
        self.library_handle.G2_findNetworkByEntityID_helper.argtypes = [
            c_char_p,
            c_longlong,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findNetworkByEntityID_helper.restype = (
            G2FindNetworkByEntityIDResult
        )
        # self.library_handle.G2_findNetworkByEntityID_V2.argtypes = [c_char_p, c_int, c_int, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findNetworkByEntityID_V2.restype = c_int
        self.library_handle.G2_findNetworkByEntityID_V2_helper.argtypes = [
            c_char_p,
            c_longlong,
            c_longlong,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findNetworkByEntityID_V2_helper.restype = (
            G2FindNetworkByEntityIDV2Result
        )
        self.library_handle.G2_findNetworkByRecordID_helper.argtypes = [
            c_char_p,
            c_longlong,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findNetworkByRecordID_helper.restype = (
            G2FindNetworkByRecordIDResult
        )
        # self.library_handle.G2_findNetworkByRecordID_V2.argtypes = [c_char_p, c_int, c_int, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findNetworkByRecordID_V2.restype = c_int
        self.library_handle.G2_findNetworkByRecordID_V2_helper.argtypes = [
            c_char_p,
            c_longlong,
            c_longlong,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findNetworkByRecordID_V2_helper.restype = (
            G2FindNetworkByRecordIDV2Result
        )
        self.library_handle.G2_findPathByEntityID_helper.argtypes = [
            c_longlong,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findPathByEntityID_helper.restype = (
            G2FindPathByEntityIDResult
        )
        # self.library_handle.G2_findPathByEntityID_V2.argtypes = [c_longlong, c_longlong, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findPathByEntityID_V2.restype = c_int
        self.library_handle.G2_findPathByEntityID_V2_helper.argtypes = [
            c_longlong,
            c_longlong,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findPathByEntityID_V2_helper.restype = (
            G2FindPathByEntityIDV2Result
        )
        self.library_handle.G2_findPathByRecordID_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_findPathByRecordID_helper.restype = (
            G2FindPathByRecordIDResult
        )
        # self.library_handle.G2_findPathByRecordID_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findPathByRecordID_V2.restype = c_int
        self.library_handle.G2_findPathByRecordID_V2_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_findPathByRecordID_V2_helper.restype = (
            G2FindPathByRecordIDV2Result
        )
        self.library_handle.G2_findPathExcludingByEntityID_helper.argtypes = [
            c_longlong,
            c_longlong,
            c_longlong,
            c_char_p,
        ]
        self.library_handle.G2_findPathExcludingByEntityID_helper.restype = (
            G2FindPathExcludingByEntityIDResult
        )
        # self.library_handle.G2_findPathExcludingByEntityID_V2.argtypes = [c_longlong, c_longlong, c_int, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findPathExcludingByEntityID_V2.restype = c_int
        self.library_handle.G2_findPathExcludingByEntityID_V2_helper.argtypes = [
            c_longlong,
            c_longlong,
            c_longlong,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_findPathExcludingByEntityID_V2_helper.restype = (
            G2FindPathExcludingByEntityIDV2Result
        )
        self.library_handle.G2_findPathExcludingByRecordID_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
            c_char_p,
        ]
        self.library_handle.G2_findPathExcludingByRecordID_helper.restype = (
            G2FindPathExcludingByRecordIDResult
        )
        # self.library_handle.G2_findPathExcludingByRecordID_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findPathExcludingByRecordID_V2.restype = c_int
        self.library_handle.G2_findPathExcludingByRecordID_V2_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_findPathExcludingByRecordID_V2_helper.restype = (
            G2FindPathExcludingByRecordIDV2Result
        )
        self.library_handle.G2_findPathIncludingSourceByEntityID_helper.argtypes = [
            c_longlong,
            c_longlong,
            c_longlong,
            c_char_p,
            c_char_p,
        ]
        self.library_handle.G2_findPathIncludingSourceByEntityID_helper.restype = (
            G2FindPathIncludingSourceByEntityIDResult
        )
        # self.library_handle.G2_findPathIncludingSourceByEntityID_V2.argtypes = [c_longlong, c_longlong, c_int, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findPathIncludingSourceByEntityID_V2.restype = c_int
        self.library_handle.G2_findPathIncludingSourceByEntityID_V2_helper.argtypes = [
            c_longlong,
            c_longlong,
            c_longlong,
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_findPathIncludingSourceByEntityID_V2_helper.restype = (
            G2FindPathIncludingSourceByEntityIDV2Result
        )
        self.library_handle.G2_findPathIncludingSourceByRecordID_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
            c_char_p,
            c_char_p,
        ]
        self.library_handle.G2_findPathIncludingSourceByRecordID_helper.restype = (
            G2FindPathIncludingSourceByRecordIDResult
        )
        # self.library_handle.G2_findPathIncludingSourceByRecordID_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_int, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_findPathIncludingSourceByRecordID_V2.restype = c_int
        self.library_handle.G2_findPathIncludingSourceByRecordID_V2_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_findPathIncludingSourceByRecordID_V2_helper.restype = (
            G2FindPathIncludingSourceByRecordIDV2Result
        )
        # self.library_handle.G2_getActiveConfigID.argtypes = [POINTER(c_longlong)]
        self.library_handle.G2_getActiveConfigID_helper.argtypes = []
        self.library_handle.G2_getActiveConfigID_helper.restype = (
            G2GetActiveConfigIDResult
        )
        self.library_handle.G2_getEntityByEntityID_helper.argtypes = [
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_getEntityByEntityID_helper.restype = (
            G2GetEntityByEntityIDResult
        )
        # self.library_handle.G2_getEntityByEntityID_V2.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_getEntityByEntityID_V2.restype = c_int
        self.library_handle.G2_getEntityByEntityID_V2_helper.argtypes = [
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_getEntityByEntityID_V2_helper.restype = (
            G2GetEntityByEntityIDV2Result
        )
        self.library_handle.G2_getEntityByRecordID_helper.argtypes = [
            c_char_p,
            c_char_p,
        ]
        self.library_handle.G2_getEntityByRecordID_helper.restype = (
            G2GetEntityByRecordIDResult
        )
        # self.library_handle.G2_getEntityByRecordID_V2.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_getEntityByRecordID_V2.restype = c_int
        self.library_handle.G2_getEntityByRecordID_V2_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_getEntityByRecordID_V2_helper.restype = (
            G2GetEntityByRecordIDV2Result
        )
        self.library_handle.G2_getLastException.argtypes = [
            POINTER(c_char),
            c_size_t,
        ]
        self.library_handle.G2_getLastException.restype = c_longlong
        self.library_handle.G2_getLastExceptionCode.argtypes = []
        self.library_handle.G2_getLastExceptionCode.restype = c_int
        self.library_handle.G2_getRecord_helper.argtypes = [c_char_p, c_char_p]
        self.library_handle.G2_getRecord_helper.restype = G2GetRecordResult
        # self.library_handle.G2_getRecord_V2.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_getRecord_V2.restype = c_int
        self.library_handle.G2_getRecord_V2_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_getRecord_V2_helper.restype = G2GetRecordV2Result
        # self.library_handle.G2_getRedoRecord.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_getRedoRecord.restype = c_int
        self.library_handle.G2_getRedoRecord_helper.argtypes = []
        self.library_handle.G2_getRedoRecord_helper.restype = G2GetRedoRecordResult
        # self.library_handle.G2_getRepositoryLastModifiedTime.argtypes = [POINTER(c_longlong)]
        self.library_handle.G2_getRepositoryLastModifiedTime_helper.argtypes = []
        self.library_handle.G2_getRepositoryLastModifiedTime_helper.restype = (
            G2GetRepositoryLastModifiedTimeResult
        )
        self.library_handle.G2_getVirtualEntityByRecordID_helper.argtypes = [c_char_p]
        self.library_handle.G2_getVirtualEntityByRecordID_helper.restype = (
            G2GetVirtualEntityByRecordIDResult
        )
        # self.library_handle.G2_getVirtualEntityByRecordID_V2.argtypes = [c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_getVirtualEntityByRecordID_V2.restype = c_int
        self.library_handle.G2_getVirtualEntityByRecordID_V2_helper.argtypes = [
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_getVirtualEntityByRecordID_V2_helper.restype = (
            G2GetVirtualEntityByRecordIDV2Result
        )
        self.library_handle.G2_howEntityByEntityID_helper.argtypes = [c_longlong]
        self.library_handle.G2_howEntityByEntityID_helper.restype = (
            G2HowEntityByEntityIDResult
        )
        # self.library_handle.G2_howEntityByEntityID_V2.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_howEntityByEntityID_V2.restype = c_int
        self.library_handle.G2_howEntityByEntityID_V2_helper.argtypes = [
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_howEntityByEntityID_V2_helper.restype = (
            G2HowEntityByEntityIDV2Result
        )
        self.library_handle.G2_init.argtypes = [c_char_p, c_char_p, c_int]
        self.library_handle.G2_initWithConfigID.argtypes = [
            c_char_p,
            c_char_p,
            c_longlong,
            c_int,
        ]
        self.library_handle.G2_process.argtypes = [c_char_p]
        self.library_handle.G2_process.restype = c_int
        # self.library_handle.G2_processRedoRecord.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_processRedoRecord.restype = c_int
        # self.library_handle.G2_processWithInfo.argtypes = [c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_processWithInfo_helper.argtypes = [c_char_p, c_longlong]
        self.library_handle.G2_processWithInfo_helper.restype = G2ProcessWithInfoResult
        # self.library_handle.G2_processWithResponseResize.argtypes = [c_char_p, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_reevaluateEntity.argtypes = [c_longlong, c_longlong]
        # self.library_handle.G2_reevaluateEntityWithInfo.argtypes = [c_int, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_reevaluateEntityWithInfo_helper.argtypes = [
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_reevaluateEntityWithInfo_helper.restype = (
            G2ReevaluateEntityWithInfoResult
        )
        self.library_handle.G2_reevaluateRecord.argtypes = [
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_reevaluateRecord.restype = c_int
        # self.library_handle.G2_reevaluateRecordWithInfo.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_reevaluateRecordWithInfo_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_reevaluateRecordWithInfo_helper.restype = (
            G2ReevaluateRecordWithInfoResult
        )
        self.library_handle.G2_reinit.argtypes = [c_longlong]
        # self.library_handle.G2_replaceRecordWithInfo.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_replaceRecordWithInfo_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_replaceRecordWithInfo_helper.restype = (
            G2ReplaceRecordWithInfoResult
        )
        self.library_handle.G2_searchByAttributes_helper.argtypes = [c_char_p]
        self.library_handle.G2_searchByAttributes_helper.restype = (
            G2SearchByAttributesResult
        )
        # self.library_handle.G2_searchByAttributes_V2.argtypes = [c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_searchByAttributes_V2_helper.argtypes = [
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_searchByAttributes_V2_helper.restype = (
            G2SearchByAttributesV2Result
        )
        # TODO Waiting on https://senzing.atlassian.net/browse/GDEV-3716?atlOrigin=eyJpIjoiYjU0NjU0NDM5Yzg4NGRiZjg4ZWYwMGZhMjQ2N2M1ODMiLCJwIjoiaiJ9
        # self.library_handle.G2_searchByAttributes_V3_helper.argtypes = [
        #     c_char_p,
        #     c_char_p,
        #     c_longlong,
        # ]
        # self.library_handle.G2_searchByAttributes_V3_helper.restype = (
        #     G2SearchByAttributesV3Result
        # )
        # self.library_handle.G2_searchByAttributes_V3.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_stats.argtypes = [POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        self.library_handle.G2_stats_helper.argtypes = []
        self.library_handle.G2_stats_helper.restype = G2StatsResult
        self.library_handle.G2_whyEntities_helper.argtypes = [c_longlong, c_longlong]
        self.library_handle.G2_whyEntities_helper.restype = G2WhyEntitiesResult
        # self.library_handle.G2_whyEntities_V2.argtypes = [c_longlong, c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_whyEntities_V2.restype = c_int
        self.library_handle.G2_whyEntities_V2_helper.argtypes = [
            c_longlong,
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_whyEntities_V2_helper.restype = G2WhyEntitiesV2Result
        self.library_handle.G2_whyEntityByEntityID_helper.argtypes = [c_longlong]
        self.library_handle.G2_whyEntityByEntityID_helper.restype = (
            G2WhyEntityByEntityIDResult
        )
        # self.library_handle.G2_whyEntityByEntityID_V2.argtypes = [c_longlong, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_whyEntityByEntityID_V2.restype = c_int
        self.library_handle.G2_whyEntityByEntityID_V2_helper.argtypes = [
            c_longlong,
            c_longlong,
        ]
        self.library_handle.G2_whyEntityByEntityID_V2_helper.restype = (
            G2WhyEntityByEntityIDV2Result
        )
        self.library_handle.G2_whyEntityByRecordID_helper.argtypes = [
            c_char_p,
            c_char_p,
        ]
        self.library_handle.G2_whyEntityByRecordID_helper.restype = (
            G2WhyEntityByRecordIDResult
        )
        # self.library_handle.G2_whyEntityByRecordID_V2.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_whyEntityByRecordID_V2.restype = c_int
        self.library_handle.G2_whyEntityByRecordID_V2_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_whyEntityByRecordID_V2_helper.restype = (
            G2WhyEntityByRecordIDV2Result
        )
        # self.library_handle.G2_whyRecordInEntity_V2.argtypes = [c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_whyRecordInEntity_V2.restype = c_int
        self.library_handle.G2_whyRecords_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
        ]
        self.library_handle.G2_whyRecords_helper.restype = G2WhyRecordsResult
        # self.library_handle.G2_whyRecords_V2.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p, c_longlong, POINTER(c_char_p), POINTER(c_size_t), self._resize_func_def]
        # self.library_handle.G2_whyRecords_V2.restype = c_int
        self.library_handle.G2_whyRecords_V2_helper.argtypes = [
            c_char_p,
            c_char_p,
            c_char_p,
            c_char_p,
            c_longlong,
        ]
        self.library_handle.G2_whyRecords_V2_helper.restype = G2WhyRecordsV2Result
        self.library_handle.G2GoHelper_free.argtypes = [c_char_p]

        # Optionally, initialize Senzing engine.
        if (len(self.module_name) == 0) or (len(self.ini_params) == 0):
            if len(self.module_name) + len(self.ini_params) != 0:
                raise self.new_exception(4076, self.module_name, self.ini_params)
        if len(self.module_name) > 0:
            self.auto_init = True
            self.init(self.module_name, self.ini_params, self.verbose_logging)

    def __del__(self) -> None:
        """Destructor"""
        if self.auto_init:
            self.destroy()

    # -------------------------------------------------------------------------
    # Development methods - to be removed after initial development
    # -------------------------------------------------------------------------

    def fake_g2engine(self, *args: Any, **kwargs: Any) -> None:
        """
        TODO: Remove once SDK methods have been implemented.

        :meta private:
        """
        if len(args) + len(kwargs) > 2000:
            print(self.noop)

    # -------------------------------------------------------------------------
    # Exception helpers
    # -------------------------------------------------------------------------

    # TODO Modify in g2exception and abstract module to handle flags in messages from the args
    def new_exception(self, error_id: int, *args: Any) -> Exception:
        """
        Generate a new exception based on the error_id.

        :meta private:
        """
        return new_g2exception(
            self.library_handle.G2_getLastException,
            self.library_handle.G2_clearLastException,
            SENZING_PRODUCT_ID,
            error_id,
            self.ID_MESSAGES,
            CALLER_SKIP,
            *args,
        )

    # -------------------------------------------------------------------------
    # G2Engine methods
    # -------------------------------------------------------------------------

    def add_record(
        self,
        data_source_code: str,
        record_id: str,
        json_data: Union[str, Dict[Any, Any]],
        # FIXME load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        # TODO Code smell and pylint reports it. Investigate how to improve
        *args: Any,
        **kwargs: Any,
    ) -> None:
        result = self.library_handle.G2_addRecord(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_char_p(as_str(json_data)),
            as_c_char_p(load_id),
        )
        if result != 0:
            raise self.new_exception(
                4001,
                data_source_code,
                record_id,
                json_data,
                load_id,
                result,
            )

    # TODO Possible "observer" approach for with info
    # def add_record(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     json_data: str,
    #     # FIXME load_id is no longer used, being removed from V4 C api?
    #     load_id: str = "",
    #     with_info_obj: Optional[Union[WithInfoResponsesAbstract, None]] = None,
    #     flags: int = 0,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> None:
    #     if not with_info_obj:
    #         result = self.library_handle.G2_addRecord(
    #             as_c_char_p(data_source_code),
    #             as_c_char_p(record_id),
    #             as_c_char_p(json_data),
    #             as_c_char_p(load_id),
    #         )
    #         if result != 0:
    #             raise self.new_exception(
    #                 4001,
    #                 data_source_code,
    #                 record_id,
    #                 json_data,
    #                 # load_id,
    #                 result.return_code,
    #             )
    #         return None

    #     else:
    #         result = self.library_handle.G2_addRecordWithInfo_helper(
    #             as_c_char_p(data_source_code),
    #             as_c_char_p(record_id),
    #             as_c_char_p(json_data),
    #             as_c_char_p(load_id),
    #             as_c_int(flags),
    #         )

    #         try:
    #             if result.return_code != 0:
    #                 raise self.new_exception(
    #                     4002,
    #                     data_source_code,
    #                     record_id,
    #                     json_data,
    #                     # load_id,
    #                     flags,
    #                     result.return_code,
    #                 )
    #             result_response = as_python_str(result.response)
    #             # TODO Catch exceptions fpr the with info object? What if it's not what we expect?
    #             with_info_obj.append(result_response)
    #         finally:
    #             self.library_handle.G2GoHelper_free(result.response)
    #         return None

    def add_record_with_info(
        self,
        data_source_code: str,
        record_id: str,
        json_data: Union[str, Dict[Any, Any]],
        # FIXME load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        flags: int = 0,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_addRecordWithInfo_helper(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_char_p(as_str(json_data)),
            as_c_char_p(load_id),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4002,
                    data_source_code,
                    record_id,
                    json_data,
                    load_id,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE add_record_with_retruned_record_id and addRecordWithInfoWithReturnedRecordID are going away in V4 and not included

    # TODO Is checkRecord being removed?

    def close_export(self, response_handle: int, *args: Any, **kwargs: Any) -> None:
        result = self.library_handle.G2_closeExport(as_uintptr_t(response_handle))
        if result != 0:
            raise self.new_exception(4006, response_handle, result)

    def count_redo_records(self, *args: Any, **kwargs: Any) -> int:
        result = self.library_handle.G2_countRedoRecords()
        # NOTE If result >= 0 call was successful
        if result < 0:
            raise self.new_exception(4007, result.return_code)
        return as_python_int(result)

    def delete_record(
        self,
        data_source_code: str,
        record_id: str,
        # FIXME load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        **kwargs: Any,
    ) -> None:
        result = self.library_handle.G2_deleteRecord(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_char_p(load_id),
        )
        if result != 0:
            raise self.new_exception(
                4008,
                data_source_code,
                record_id,
                load_id,
                result,
            )

    def delete_record_with_info(
        self,
        data_source_code: str,
        record_id: str,
        # FIXME load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        flags: int = 0,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_deleteRecordWithInfo_helper(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_char_p(load_id),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4009,
                    data_source_code,
                    record_id,
                    load_id,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    def destroy(self, *args: Any, **kwargs: Any) -> None:
        result = self.library_handle.G2_destroy()
        if result != 0:
            raise self.new_exception(4010, result)

    def export_config(self, *args: Any, **kwargs: Any) -> str:
        result = self.library_handle.G2_exportConfig_helper()

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(4012, result.return_code)
            return as_python_str(result.response)

    def export_config_and_config_id(self, *args: Any, **kwargs: Any) -> Tuple[str, int]:
        result = self.library_handle.G2_exportConfigAndConfigID_helper()

        with FreeCResources(self.library_handle, result.config):
            if result.return_code != 0:
                raise self.new_exception(4010, result.return_code)
            # TODO Does config_id need as_python_int, cytpe is compatible?
            return as_python_str(result.config), result.config_id

    def export_csv_entity_report(
        self,
        # TODO add default col list?
        csv_column_list: str,
        flags: int = G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> int:
        result = self.library_handle.G2_exportCSVEntityReport_helper(
            as_c_char_p(csv_column_list), as_c_int(flags)
        )
        if result.return_code != 0:
            raise self.new_exception(4013, csv_column_list, flags, result.return_code)
        return as_python_int(result.export_handle)

    def export_json_entity_report(
        self,
        flags: int = G2EngineFlags.G2_EXPORT_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> int:
        result = self.library_handle.G2_exportJSONEntityReport_helper(as_c_int(flags))
        if result.return_code != 0:
            raise self.new_exception(4014, flags, result.return_code)
        return as_python_int(result.export_handle)

    def fetch_next(self, response_handle: int, *args: Any, **kwargs: Any) -> str:
        result = self.library_handle.G2_fetchNext_helper(as_uintptr_t(response_handle))
        if result.return_code != 0:
            raise self.new_exception(4015, response_handle, result.return_code)
        return as_python_str(result.response)

    # NOTE No examples of this, early adopter function and needs manual additions to Sz config to work
    def find_interesting_entities_by_entity_id(
        self, entity_id: int, flags: int = 0, *args: Any, **kwargs: Any
    ) -> str:
        result = self.library_handle.G2_findInterestingEntitiesByEntityID_helper(
            as_c_int(entity_id)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(4016, entity_id, result.return_code)
            return as_python_str(result.response)

    # NOTE No examples of this, early adopter function and needs manual additions to Sz config to work
    def find_interesting_entities_by_record_id(
        self,
        data_source_code: str,
        record_id: str,
        flags: int = 0,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_findInterestingEntitiesByRecordID_helper(
            as_c_char_p(data_source_code), as_c_char_p(record_id), as_c_int(flags)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4017, data_source_code, record_id, result.return_code
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def find_network_by_entity_id_v2(
    #     self,
    #     entity_list: str,
    #     max_degree: int,
    #     build_out_degree: int,
    #     max_entities: int,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         entity_list, max_degree, build_out_degree, max_entities, flags
    #     )
    #     return "string"

    def find_network_by_entity_id(
        self,
        entity_list: Union[str, Dict[Any, Any]],
        max_degree: int,
        build_out_degree: int,
        max_entities: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findNetworkByEntityID_V2_helper(
            # as_c_char_p(entity_list),
            as_c_char_p(as_str(entity_list)),
            as_c_int(max_degree),
            as_c_int(build_out_degree),
            as_c_int(max_entities),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4018,
                    entity_list,
                    max_degree,
                    build_out_degree,
                    max_entities,
                    # flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def find_network_by_record_id_v2(
    #     self,
    #     record_list: str,
    #     max_degree: int,
    #     build_out_degree: int,
    #     max_entities: int,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         record_list, max_degree, build_out_degree, max_entities, flags
    #     )
    #     return "string"

    def find_network_by_record_id(
        self,
        record_list: Union[str, Dict[Any, Any]],
        max_degree: int,
        build_out_degree: int,
        max_entities: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findNetworkByRecordID_V2_helper(
            as_c_char_p(as_str(record_list)),
            as_c_int(max_degree),
            as_c_int(build_out_degree),
            as_c_int(max_entities),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4020,
                    record_list,
                    max_degree,
                    build_out_degree,
                    max_entities,
                    # flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def find_path_by_entity_id_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     max_degree: int,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(entity_id_1, entity_id_2, max_degree, flags)
    #     return "string"

    def find_path_by_entity_id(
        self,
        entity_id_1: int,
        entity_id_2: int,
        max_degree: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findPathByEntityID_V2_helper(
            as_c_int(entity_id_1),
            as_c_int(entity_id_2),
            as_c_int(max_degree),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4022,
                    entity_id_1,
                    entity_id_2,
                    max_degree,
                    # flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def find_path_by_record_id_v2(
    #     self,
    #     data_source_code_1: str,
    #     record_id_1: str,
    #     data_source_code_2: str,
    #     record_id_2: str,
    #     max_degree: int,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         data_source_code_1,
    #         record_id_1,
    #         data_source_code_2,
    #         record_id_2,
    #         max_degree,
    #         flags,
    #     )
    #     return "string"

    def find_path_by_record_id(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        max_degree: int,
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findPathByRecordID_V2_helper(
            as_c_char_p(data_source_code_1),
            as_c_char_p(record_id_1),
            as_c_char_p(data_source_code_2),
            as_c_char_p(record_id_2),
            as_c_int(max_degree),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4024,
                    data_source_code_1,
                    record_id_1,
                    data_source_code_2,
                    record_id_2,
                    # TODO Account for max_degree in new_exception as per flags
                    # max_degree,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def find_path_excluding_by_entity_id_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     max_degree: int,
    #     excluded_entities: str,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         entity_id_1, entity_id_2, max_degree, excluded_entities, flags
    #     )
    #     return "string"

    def find_path_excluding_by_entity_id(
        self,
        entity_id_1: int,
        entity_id_2: int,
        max_degree: int,
        excluded_entities: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findPathExcludingByEntityID_V2_helper(
            as_c_int(entity_id_1),
            as_c_int(entity_id_2),
            as_c_int(max_degree),
            as_c_char_p(as_str(excluded_entities)),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4026,
                    entity_id_1,
                    entity_id_2,
                    max_degree,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def find_path_excluding_by_record_id_v2(
    #     self,
    #     data_source_code_1: str,
    #     record_id_1: str,
    #     data_source_code_2: str,
    #     record_id_2: str,
    #     max_degree: int,
    #     excluded_records: str,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         data_source_code_1,
    #         record_id_1,
    #         data_source_code_2,
    #         record_id_2,
    #         max_degree,
    #         excluded_records,
    #         flags,
    #     )
    #     return "string"

    # TODO On all methods that take args like excluded_records make the default {} if not specified? The engine accepts {} but does this make sense to provide a default?
    def find_path_excluding_by_record_id(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        max_degree: int,
        # TODO Jira to discuss excluded_entities and excluded_records
        excluded_records: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findPathExcludingByRecordID_V2_helper(
            as_c_char_p(data_source_code_1),
            as_c_char_p(record_id_1),
            as_c_char_p(data_source_code_2),
            as_c_char_p(record_id_2),
            as_c_int(max_degree),
            as_c_char_p(as_str(excluded_records)),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4028,
                    data_source_code_1,
                    record_id_1,
                    data_source_code_2,
                    record_id_2,
                    # max_degree,
                    excluded_records,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def find_path_including_source_by_entity_id_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     max_degree: int,
    #     excluded_entities: str,
    #     required_dsrcs: str,
    #     flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         entity_id_1,
    #         entity_id_2,
    #         max_degree,
    #         excluded_entities,
    #         required_dsrcs,
    #         flags,
    #     )
    #     return "string"

    def find_path_including_source_by_entity_id(
        self,
        entity_id_1: int,
        entity_id_2: int,
        max_degree: int,
        excluded_entities: Union[str, Dict[Any, Any]],
        required_dsrcs: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findPathIncludingSourceByEntityID_V2_helper(
            as_c_int(entity_id_1),
            as_c_int(entity_id_2),
            as_c_int(max_degree),
            as_c_char_p(as_str(excluded_entities)),
            as_c_char_p(as_str(required_dsrcs)),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4030,
                    entity_id_1,
                    entity_id_2,
                    max_degree,
                    excluded_entities,
                    required_dsrcs,
                    # flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
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
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         data_source_code_1,
    #         record_id_1,
    #         data_source_code_2,
    #         record_id_2,
    #         max_degree,
    #         excluded_records,
    #         required_dsrcs,
    #         flags,
    #     )
    #     return "string"

    def find_path_including_source_by_record_id(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        max_degree: int,
        excluded_records: Union[str, Dict[Any, Any]],
        required_dsrcs: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_FIND_PATH_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_findPathIncludingSourceByRecordID_V2_helper(
            as_c_char_p(data_source_code_1),
            as_c_char_p(record_id_1),
            as_c_char_p(data_source_code_2),
            as_c_char_p(record_id_2),
            as_c_int(max_degree),
            as_c_char_p(as_str(excluded_records)),
            as_c_char_p(as_str(required_dsrcs)),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4032,
                    data_source_code_1,
                    record_id_1,
                    data_source_code_2,
                    record_id_2,
                    # max_degree,
                    excluded_records,
                    required_dsrcs,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    def get_active_config_id(self, *args: Any, **kwargs: Any) -> int:
        result = self.library_handle.G2_getActiveConfigID_helper()
        if result.return_code != 0:
            raise self.new_exception(4034, result.return_code)
        return as_python_int(result.response)

    # NOTE This should be going away in V4?
    # def get_entity_by_entity_id_v2(
    #     self,
    #     entity_id: int,
    #     flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(entity_id, flags)
    #     return "string"

    def get_entity_by_entity_id(
        self,
        entity_id: int,
        flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_getEntityByEntityID_V2_helper(
            as_c_int(entity_id), as_c_int(flags)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(4035, entity_id, flags, result.return_code)
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def get_entity_by_record_id_v2(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(data_source_code, record_id, flags)
    #     return "string"

    def get_entity_by_record_id(
        self,
        data_source_code: str,
        record_id: str,
        flags: int = G2EngineFlags.G2_ENTITY_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_getEntityByRecordID_V2_helper(
            as_c_char_p(data_source_code), as_c_char_p(record_id), as_c_int(flags)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4037, data_source_code, record_id, result.return_code
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def get_record_v2(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_RECORD_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(data_source_code, record_id, flags)
    #     return "string"

    def get_record(
        self,
        data_source_code: str,
        record_id: str,
        flags: int = G2EngineFlags.G2_RECORD_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Remove V2 for V4
        result = self.library_handle.G2_getRecord_V2_helper(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    # 4040, data_source_code, record_id, flags, result.return_code
                    4040,
                    data_source_code,
                    record_id,
                    result.return_code,
                )
            return as_python_str(result.response)

    def get_redo_record(self, *args: Any, **kwargs: Any) -> str:
        result = self.library_handle.G2_getRedoRecord_helper()

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(4042, result.return_code)
            return as_python_str(result.response)

    def get_repository_last_modified_time(self, *args: Any, **kwargs: Any) -> int:
        result = self.library_handle.G2_getRepositoryLastModifiedTime_helper()
        if result.return_code != 0:
            raise self.new_exception(4043, result.return_code)
        return as_python_int(result.time)

    # NOTE This should be going away in V4?
    # def get_virtual_entity_by_record_id_v2(
    #     self,
    #     record_list: str,
    #     flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(record_list, flags)
    #     return "string"

    def get_virtual_entity_by_record_id(
        self,
        record_list: Union[str, Dict[Any, Any]],
        flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_getVirtualEntityByRecordID_V2_helper(
            as_c_char_p(as_str(record_list)), as_c_int(flags)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                # raise self.new_exception(4044, record_list, flags, result.return_code)
                raise self.new_exception(4044, record_list, result.return_code)
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def how_entity_by_entity_id_v2(
    #     self,
    #     entity_id: int,
    #     flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(entity_id, flags)
    #     return "string"

    def how_entity_by_entity_id(
        self,
        entity_id: int,
        flags: int = G2EngineFlags.G2_HOW_ENTITY_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_howEntityByEntityID_V2_helper(
            as_c_int(entity_id), as_c_int(flags)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(4046, flags, result.return_code)
            return as_python_str(result.response)

    def init(
        self,
        module_name: str,
        ini_params: Union[str, Dict[Any, Any]],
        verbose_logging: int = 0,
        **kwargs: Any,
    ) -> None:
        result = self.library_handle.G2_init(
            as_c_char_p(module_name),
            as_c_char_p(as_str(ini_params)),
            as_c_int(verbose_logging),
        )
        if result < 0:
            raise self.new_exception(
                4048, module_name, ini_params, verbose_logging, result
            )

    def init_with_config_id(
        self,
        module_name: str,
        ini_params: Union[str, Dict[Any, Any]],
        init_config_id: int,
        verbose_logging: int = 0,
        **kwargs: Any,
    ) -> None:
        result = self.library_handle.G2_initWithConfigID(
            as_c_char_p(module_name),
            as_c_char_p(as_str(ini_params)),
            as_c_int(init_config_id),
            as_c_int(verbose_logging),
        )
        if result < 0:
            raise self.new_exception(
                4049,
                module_name,
                ini_params,
                init_config_id,
                verbose_logging,
                result,
            )

    def prime_engine(self, *args: Any, **kwargs: Any) -> None:
        result = self.library_handle.G2_primeEngine()
        if result < 0:
            raise self.new_exception(4050, result)

    # TODO Going away in V4? Will be get_redo_record + process_redo_record
    def process(
        self, record: Union[str, Dict[Any, Any]], *args: Any, **kwargs: Any
    ) -> None:
        result = self.library_handle.G2_process(
            as_c_char_p(as_str(record)),
        )
        if result < 0:
            raise self.new_exception(4051, record, result)

    # TODO Going away in V4? Will be get_redo_record + process_redo_record
    def process_with_info(
        self,
        record: Union[str, Dict[Any, Any]],
        flags: int = 0,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_processWithInfo_helper(
            as_c_char_p(as_str(record)),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4054,
                    record,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    def purge_repository(self, *args: Any, **kwargs: Any) -> None:
        result = self.library_handle.G2_purgeRepository()
        if result < 0:
            raise self.new_exception(4057, result)

    def reevaluate_entity(
        self, entity_id: int, flags: int = 0, *args: Any, **kwargs: Any
    ) -> None:
        result = self.library_handle.G2_reevaluateEntity(
            as_c_int(entity_id), as_c_int(flags)
        )
        if result < 0:
            raise self.new_exception(4058, result)

    def reevaluate_entity_with_info(
        self, entity_id: int, flags: int = 0, *args: Any, **kwargs: Any
    ) -> str:
        result = self.library_handle.G2_reevaluateEntityWithInfo_helper(
            as_c_int(entity_id),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4059,
                    entity_id,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    def reevaluate_record(
        self,
        data_source_code: str,
        record_id: str,
        flags: int = 0,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        result = self.library_handle.G2_reevaluateRecord(
            as_c_char_p(data_source_code), as_c_char_p(record_id), as_c_int(flags)
        )
        if result < 0:
            raise self.new_exception(4060, data_source_code, record_id, flags, result)

    def reevaluate_record_with_info(
        self,
        data_source_code: str,
        record_id: str,
        flags: int = 0,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_reevaluateRecordWithInfo_helper(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4061,
                    data_source_code,
                    record_id,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    def reinit(self, init_config_id: int, *args: Any, **kwargs: Any) -> None:
        result = self.library_handle.G2_reinit(as_c_int(init_config_id))
        if result < 0:
            raise self.new_exception(4062, init_config_id, result)

    def replace_record(
        self,
        data_source_code: str,
        record_id: str,
        json_data: Union[str, Dict[Any, Any]],
        # FIXME load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        *args: Any,
        **kwargs: Any,
    ) -> None:
        result = self.library_handle.G2_replaceRecord(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_char_p(as_str(json_data)),
            as_c_char_p(load_id),
        )
        if result < 0:
            raise self.new_exception(
                4063, data_source_code, record_id, json_data, load_id, result
            )

    def replace_record_with_info(
        self,
        data_source_code: str,
        record_id: str,
        json_data: Union[str, Dict[Any, Any]],
        # FIXME load_id is no longer used, being removed from V4 C api?
        load_id: str = "",
        flags: int = 0,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        result = self.library_handle.G2_replaceRecordWithInfo_helper(
            as_c_char_p(data_source_code),
            as_c_char_p(record_id),
            as_c_char_p(as_str(json_data)),
            as_c_char_p(load_id),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4002,
                    data_source_code,
                    record_id,
                    json_data,
                    load_id,
                    flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def search_by_attributes_v2(
    #     self,
    #     json_data: str,
    #     flags: int = G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(json_data, flags)
    #     return "string"

    # NOTE This should be going away in V4?
    # def search_by_attributes_v3(
    #     self,
    #     json_data: str,
    #     search_profile: str,
    #     # TODO Does the abstract signature also need any defaults?
    #     flags: int = G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(json_data, search_profile, flags)
    #     return "string"

    # TODO Change to incorporate search_profile from search_by_attributes_v3
    #      https://senzing.atlassian.net/browse/GDEV-3716?atlOrigin=eyJpIjoiYjU0NjU0NDM5Yzg4NGRiZjg4ZWYwMGZhMjQ2N2M1ODMiLCJwIjoiaiJ9
    def search_by_attributes(
        self,
        json_data: Union[str, Dict[Any, Any]],
        # search_profile: str = "SEARCH",
        flags: int = G2EngineFlags.G2_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Change to no V3 for V4
        # result = self.library_handle.G2_searchByAttributes_V3_helper(
        result = self.library_handle.G2_searchByAttributes_V2_helper(
            as_c_char_p(as_str(json_data)), as_c_int(flags)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                # TODO 4076 needs to be reordered in engine_abstract for a V4 build
                raise self.new_exception(
                    # 4076, json_data, search_profile, flags, result.return_code
                    4065,
                    json_data,
                    # flags,
                    result.return_code,
                )
            return as_python_str(result.response)

    def stats(self, *args: Any, **kwargs: Any) -> str:
        result = self.library_handle.G2_stats_helper()

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(4067, result.return_code)
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def why_entities_v2(
    #     self,
    #     entity_id_1: int,
    #     entity_id_2: int,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(entity_id_1, entity_id_2, flags)
    #     return "string"

    # TODO Remove V2 for V4
    def why_entities(
        self,
        entity_id_1: int,
        entity_id_2: int,
        flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Is as_ needed? Sending in a string int value the call still works without as_c_int?
        result = self.library_handle.G2_whyEntities_V2_helper(
            as_c_int(entity_id_1), as_c_int(entity_id_2), as_c_int(flags)
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4068, entity_id_1, entity_id_2, result.return_code
                )
            return as_python_str(result.response)

    # NOTE This should be going away in V4?
    # def why_entity_by_entity_id_v2(
    #     self,
    #     entity_id: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(entity_id, flags)
    #     return "string"

    # NOTE Being removed in V4
    # def why_entity_by_entity_id(
    #     self,
    #     entity_id: int,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     result = self.library_handle.G2_whyEntityByEntityID_V2_helper(
    #         as_c_int(entity_id), as_c_int(flags)
    #     )
    #     try:
    #         if result.return_code != 0:
    #             raise self.new_exception(4070, entity_id, flags, result.return_code)
    #         result_response = as_python_str(result.response)
    #     finally:
    #         self.library_handle.G2GoHelper_free(result.response)
    #     return result_response

    # NOTE This should be going away in V4?
    # def why_entity_by_record_id_v2(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(data_source_code, record_id, flags)
    #     return "string"

    # NOTE Being removed in V4
    # def why_entity_by_record_id(
    #     self,
    #     data_source_code: str,
    #     record_id: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     # TODO Is as_ needed? Sending in a string int value the call still works without as_c_int?
    #     result = self.library_handle.G2_whyEntityByRecordID_V2_helper(
    #         as_c_char_p(data_source_code), as_c_char_p(record_id), as_c_int(flags)
    #     )
    #     try:
    #         if result.return_code != 0:
    #             raise self.new_exception(
    #                 4072, data_source_code, record_id, flags, result.return_code
    #             )
    #         result_response = as_python_str(result.response)
    #     finally:
    #         self.library_handle.G2GoHelper_free(result.response)
    #     return result_response

    # NOTE This should be going away in V4?
    # def why_records_v2(
    #     self,
    #     data_source_code_1: str,
    #     record_id_1: str,
    #     data_source_code_2: str,
    #     record_id_2: str,
    #     flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
    #     *args: Any,
    #     **kwargs: Any,
    # ) -> str:
    #     self.fake_g2engine(
    #         data_source_code_1, record_id_1, data_source_code_2, record_id_2, flags
    #     )
    #     return "string"

    # TODO Remove V2 for V4
    def why_records(
        self,
        data_source_code_1: str,
        record_id_1: str,
        data_source_code_2: str,
        record_id_2: str,
        flags: int = G2EngineFlags.G2_WHY_ENTITY_DEFAULT_FLAGS,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        # TODO Is as_c_int needed? Sending in a string int value the call still works without as_c_int?
        result = self.library_handle.G2_whyRecords_V2_helper(
            as_c_char_p(data_source_code_1),
            as_c_char_p(record_id_1),
            as_c_char_p(data_source_code_2),
            as_c_char_p(record_id_2),
            as_c_int(flags),
        )

        with FreeCResources(self.library_handle, result.response):
            if result.return_code != 0:
                raise self.new_exception(
                    4074,
                    data_source_code_1,
                    record_id_1,
                    data_source_code_2,
                    record_id_2,
                    # flags,
                    result.return_code,
                )
            return as_python_str(result.response)
