# TODO Check and change the exception type with raises to more specific exception instead of g2exception
# TODO Add tests for flags
# TODO Think about and test how to make the g2helper conversions more robust and possibly raise g2exception
# TODO Test calling delete record again
# TODO Add tests for incorrect ini parms paths and incorrect DB details for constructor
# TODO value/type tests and handling ctype exceptions from g2helpers - needs thought
import json
from typing import Any, Dict
import pytest
from pytest_schema import Or, schema
from senzing_truthset import (
    TRUTHSET_DATASOURCES,
    TRUTHSET_CUSTOMER_RECORDS,
    TRUTHSET_REFERENCE_RECORDS,
    TRUTHSET_WATCHLIST_RECORDS,
)
from senzing import g2config, g2configmgr, g2engine, g2exception

# AC - Temp disables to get changes in for move to senzing garage
# pylint: disable=C0302

# -----------------------------------------------------------------------------
# G2Engine fixtures
# -----------------------------------------------------------------------------


@pytest.fixture(name="g2_engine", scope="module")
def g2engine_fixture(engine_vars):
    """
    Single engine object to use for all tests.
    engine_vars is returned from conftest.py.
    """
    return g2engine.G2Engine(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
    )


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

DATA_SOURCES = {
    "CUSTOMERS": TRUTHSET_CUSTOMER_RECORDS,
    "REFERENCE": TRUTHSET_REFERENCE_RECORDS,
    "WATCHLIST": TRUTHSET_WATCHLIST_RECORDS,
}

RECORD_DICT = {
    "RECORD_TYPE": "PERSON",
    "PRIMARY_NAME_LAST": "Smith",
    "PRIMARY_NAME_FIRST": "Robert",
    "DATE_OF_BIRTH": "12/11/1978",
    "ADDR_TYPE": "MAILING",
    "ADDR_LINE1": "123 Main Street, Las Vegas NV 89132",
    "PHONE_TYPE": "HOME",
    "PHONE_NUMBER": "702-919-1300",
    "EMAIL_ADDRESS": "bsmith@work.com",
    "DATE": "1/2/18",
    "STATUS": "Active",
    "AMOUNT": "100",
}
RECORD_STR = (
    '{"RECORD_TYPE": "PERSON", "PRIMARY_NAME_LAST": "Smith", "PRIMARY_NAME_FIRST":'
    ' "Robert", "DATE_OF_BIRTH": "12/11/1978", "ADDR_TYPE": "MAILING", "ADDR_LINE1":'
    ' "123 Main Street, Las Vegas NV 89132","PHONE_TYPE": "HOME", "PHONE_NUMBER":'
    ' "702-919-1300", "EMAIL_ADDRESS": "bsmith@work.com", "DATE": "1/2/18", "STATUS":'
    ' "Active", "AMOUNT": "100"}'
)

RECORD_STR_BAD = (
    '{"RECORD_TYPE": "PERSON" "PRIMARY_NAME_LAST": "Smith", "PRIMARY_NAME_FIRST":'
    ' "Robert", "DATE_OF_BIRTH": "12/11/1978", "ADDR_TYPE": "MAILING", "ADDR_LINE1":'
    ' "123 Main Street, Las Vegas NV 89132","PHONE_TYPE": "HOME", "PHONE_NUMBER":'
    ' "702-919-1300", "EMAIL_ADDRESS": "bsmith@work.com", "DATE": "1/2/18", "STATUS":'
    ' "Active", "AMOUNT": "100"}'
)

# -----------------------------------------------------------------------------
# G2Engine schemas
# -----------------------------------------------------------------------------

with_info_schema = {
    "DATA_SOURCE": str,
    "RECORD_ID": str,
    "AFFECTED_ENTITIES": [{"ENTITY_ID": int}],
    "INTERESTING_ENTITIES": {"ENTITIES": []},
}

export_json_entity_report_schema = {
    "RESOLVED_ENTITY": {
        "ENTITY_ID": int,
        "ENTITY_NAME": str,
        "FEATURES": {},
        "RECORDS": [
            {
                "DATA_SOURCE": str,
                "RECORD_ID": str,
                "ENTITY_TYPE": str,
                "INTERNAL_ID": int,
                "ENTITY_KEY": str,
                "ENTITY_DESC": str,
                "MATCH_KEY": str,
                "MATCH_LEVEL": int,
                "MATCH_LEVEL_CODE": str,
                "ERRULE_CODE": str,
                "LAST_SEEN_DT": str,
            }
        ],
    },
    "RELATED_ENTITIES": [{}],
}


g2_config_schema = {
    "G2_CONFIG": {
        "CFG_ETYPE": [
            {
                "ETYPE_ID": int,
                "ETYPE_CODE": str,
                "ETYPE_DESC": str,
            },
        ],
        "CFG_DSRC_INTEREST": [],
        "CFG_RCLASS": [
            {
                "RCLASS_ID": int,
                "RCLASS_CODE": str,
                "RCLASS_DESC": str,
                "IS_DISCLOSED": str,
            },
        ],
        "CFG_FTYPE": [
            {
                "FTYPE_ID": int,
                "FTYPE_CODE": Or(str, None),
                "FCLASS_ID": int,
                "FTYPE_FREQ": str,
                "FTYPE_EXCL": str,
                "FTYPE_STAB": str,
                "PERSIST_HISTORY": str,
                "USED_FOR_CAND": str,
                "DERIVED": str,
                "RTYPE_ID": int,
                "ANONYMIZE": str,
                "VERSION": int,
                "SHOW_IN_MATCH_KEY": str,
            },
        ],
        "CFG_FCLASS": [
            {
                "FCLASS_ID": int,
                "FCLASS_CODE": str,
            },
        ],
        "CFG_FBOM": [
            {
                "FTYPE_ID": int,
                "FELEM_ID": int,
                "EXEC_ORDER": int,
                "DISPLAY_LEVEL": int,
                "DISPLAY_DELIM": Or(str, None),
                "DERIVED": str,
            },
        ],
        "CFG_FELEM": [
            {
                "FELEM_ID": int,
                "FELEM_CODE": str,
                "TOKENIZE": str,
                "DATA_TYPE": str,
            },
        ],
        "CFG_DSRC": [
            {
                "DSRC_ID": int,
                "DSRC_CODE": str,
                "DSRC_DESC": str,
                "DSRC_RELY": int,
                "RETENTION_LEVEL": str,
                "CONVERSATIONAL": str,
            },
        ],
        "CFG_EFBOM": [
            {
                "EFCALL_ID": int,
                "FTYPE_ID": int,
                "FELEM_ID": int,
                "EXEC_ORDER": int,
                "FELEM_REQ": str,
            },
        ],
        "CFG_EFUNC": [
            {
                "EFUNC_ID": int,
                "EFUNC_CODE": str,
                "FUNC_LIB": str,
                "FUNC_VER": str,
                "CONNECT_STR": str,
                "LANGUAGE": Or(str, None),
                "JAVA_CLASS_NAME": Or(str, None),
            },
        ],
        "CFG_EFCALL": [
            {
                "EFCALL_ID": int,
                "FTYPE_ID": int,
                "FELEM_ID": int,
                "EFUNC_ID": int,
                "EXEC_ORDER": int,
                "EFEAT_FTYPE_ID": int,
                "IS_VIRTUAL": str,
            },
        ],
        "CFG_SFCALL": [
            {
                "SFCALL_ID": int,
                "FTYPE_ID": int,
                "FELEM_ID": int,
                "SFUNC_ID": int,
                "EXEC_ORDER": int,
            },
        ],
        "CFG_SFUNC": [
            {
                "SFUNC_ID": int,
                "SFUNC_CODE": str,
                "FUNC_LIB": str,
                "FUNC_VER": str,
                "CONNECT_STR": str,
                "LANGUAGE": Or(str, None),
                "JAVA_CLASS_NAME": Or(str, None),
            },
        ],
        "SYS_OOM": [
            {
                "OOM_TYPE": str,
                "OOM_LEVEL": str,
                "FTYPE_ID": int,
                "THRESH1_CNT": int,
                "THRESH1_OOM": int,
                "NEXT_THRESH": int,
            },
        ],
        "CFG_CFUNC": [
            {
                "CFUNC_ID": int,
                "CFUNC_CODE": str,
                "FUNC_LIB": str,
                "FUNC_VER": str,
                "CONNECT_STR": str,
                "ANON_SUPPORT": str,
                "LANGUAGE": Or(str, None),
                "JAVA_CLASS_NAME": Or(str, None),
            },
        ],
        "CFG_CFCALL": [
            {
                "CFCALL_ID": int,
                "FTYPE_ID": int,
                "CFUNC_ID": int,
                "EXEC_ORDER": int,
            },
        ],
        "CFG_GPLAN": [
            {
                "GPLAN_ID": int,
                "GPLAN_CODE": str,
            },
        ],
        "CFG_ERRULE": [
            {
                "ERRULE_ID": int,
                "ERRULE_CODE": str,
                "ERRULE_DESC": str,
                "RESOLVE": str,
                "RELATE": str,
                "REF_SCORE": int,
                "RTYPE_ID": int,
                "QUAL_ERFRAG_CODE": str,
                "DISQ_ERFRAG_CODE": Or(str, None),
                "ERRULE_TIER": Or(int, None),
            },
        ],
        "CFG_ERFRAG": [
            {
                "ERFRAG_ID": int,
                "ERFRAG_CODE": str,
                "ERFRAG_DESC": str,
                "ERFRAG_SOURCE": str,
                "ERFRAG_DEPENDS": Or(str, None),
            },
        ],
        "CFG_CFBOM": [
            {
                "CFCALL_ID": int,
                "FTYPE_ID": int,
                "FELEM_ID": int,
                "EXEC_ORDER": int,
            },
        ],
        "CFG_DFUNC": [
            {
                "DFUNC_ID": int,
                "DFUNC_CODE": str,
                "FUNC_LIB": str,
                "FUNC_VER": str,
                "CONNECT_STR": str,
                "ANON_SUPPORT": str,
                "LANGUAGE": Or(str, None),
                "JAVA_CLASS_NAME": Or(str, None),
            },
        ],
        "CFG_DFCALL": [
            {
                "DFCALL_ID": int,
                "FTYPE_ID": int,
                "DFUNC_ID": int,
                "EXEC_ORDER": int,
            },
        ],
        "CFG_DFBOM": [
            {
                "DFCALL_ID": int,
                "FTYPE_ID": int,
                "FELEM_ID": int,
                "EXEC_ORDER": int,
            },
        ],
        "CFG_CFRTN": [
            {
                "CFRTN_ID": int,
                "CFUNC_ID": int,
                "FTYPE_ID": int,
                "CFUNC_RTNVAL": str,
                "EXEC_ORDER": int,
                "SAME_SCORE": int,
                "CLOSE_SCORE": int,
                "LIKELY_SCORE": int,
                "PLAUSIBLE_SCORE": int,
                "UN_LIKELY_SCORE": int,
            },
        ],
        "CFG_RTYPE": [
            {
                "RTYPE_ID": int,
                "RTYPE_CODE": str,
                "RCLASS_ID": int,
                "REL_STRENGTH": int,
                "BREAK_RES": str,
            },
        ],
        "CFG_GENERIC_THRESHOLD": [
            {
                "GPLAN_ID": int,
                "BEHAVIOR": str,
                "FTYPE_ID": int,
                "CANDIDATE_CAP": int,
                "SCORING_CAP": int,
                "SEND_TO_REDO": str,
            },
        ],
        "CFG_FBOVR": [
            {
                "FTYPE_ID": int,
                "UTYPE_CODE": str,
                "FTYPE_FREQ": str,
                "FTYPE_EXCL": str,
                "FTYPE_STAB": str,
            },
        ],
        "CFG_ATTR": [
            {
                "ATTR_ID": int,
                "ATTR_CODE": str,
                "ATTR_CLASS": str,
                "FTYPE_CODE": Or(str, None),
                "FELEM_CODE": Or(str, None),
                "FELEM_REQ": str,
                "DEFAULT_VALUE": Or(str, None),
                "ADVANCED": str,
                "INTERNAL": str,
            },
        ],
        "CONFIG_BASE_VERSION": {
            "VERSION": str,
            "BUILD_VERSION": str,
            "BUILD_DATE": str,
            "BUILD_NUMBER": str,
            "COMPATIBILITY_VERSION": {
                "CONFIG_VERSION": str,
            },
        },
    },
}

how_results_schema = {
    "HOW_RESULTS": {
        "RESOLUTION_STEPS": [{}],
        "FINAL_STATE": {
            "NEED_REEVALUATION": int,
            "VIRTUAL_ENTITIES": [
                {
                    "VIRTUAL_ENTITY_ID": str,
                    "MEMBER_RECORDS": [
                        {
                            "INTERNAL_ID": int,
                            "RECORDS": [{"DATA_SOURCE": str, "RECORD_ID": str}],
                        }
                    ],
                }
            ],
        },
    }
}

interesting_entities_schema: Dict[Any, Any] = {
    "INTERESTING_ENTITIES": {"ENTITIES": []},
}

network_schema = {
    "ENTITY_PATHS": [{"START_ENTITY_ID": int, "END_ENTITY_ID": int, "ENTITIES": []}],
    "ENTITIES": [
        {
            "RESOLVED_ENTITY": {
                "ENTITY_ID": int,
                "ENTITY_NAME": str,
                "RECORD_SUMMARY": [
                    {
                        "DATA_SOURCE": str,
                        "RECORD_COUNT": int,
                        "FIRST_SEEN_DT": str,
                        "LAST_SEEN_DT": str,
                    }
                ],
                "LAST_SEEN_DT": str,
            },
            "RELATED_ENTITIES": [
                {
                    "ENTITY_ID": int,
                    "MATCH_LEVEL": int,
                    "MATCH_LEVEL_CODE": str,
                    "MATCH_KEY": str,
                    "ERRULE_CODE": str,
                    "IS_DISCLOSED": int,
                    "IS_AMBIGUOUS": int,
                }
            ],
        }
    ],
}


path_schema = {
    "ENTITY_PATHS": [{"START_ENTITY_ID": int, "END_ENTITY_ID": int, "ENTITIES": [int]}],
    "ENTITIES": [
        {
            "RESOLVED_ENTITY": {
                "ENTITY_ID": int,
                "ENTITY_NAME": str,
                "RECORD_SUMMARY": [
                    {
                        "DATA_SOURCE": str,
                        "RECORD_COUNT": int,
                        "FIRST_SEEN_DT": str,
                        "LAST_SEEN_DT": str,
                    }
                ],
                "LAST_SEEN_DT": str,
            },
            "RELATED_ENTITIES": [
                {
                    "ENTITY_ID": int,
                    "MATCH_LEVEL": int,
                    "MATCH_LEVEL_CODE": str,
                    "MATCH_KEY": str,
                    "ERRULE_CODE": str,
                    "IS_DISCLOSED": int,
                    "IS_AMBIGUOUS": int,
                }
            ],
        }
    ],
}


process_withinfo_schema = {
    "DATA_SOURCE": str,
    "RECORD_ID": str,
    "AFFECTED_ENTITIES": [{"ENTITY_ID": int}],
    "INTERESTING_ENTITIES": {"ENTITIES": []},
}

record_schema = {"DATA_SOURCE": str, "RECORD_ID": str, "JSON_DATA": {}}

redo_record_schema = {
    "REASON": str,
    "DATA_SOURCE": str,
    "RECORD_ID": str,
    "ENTITY_TYPE": str,
    "DSRC_ACTION": str,
}

resolved_entity_schema = {
    "RESOLVED_ENTITY": {
        "ENTITY_ID": int,
        "ENTITY_NAME": str,
        "FEATURES": {},
        "RECORD_SUMMARY": [
            {
                "DATA_SOURCE": str,
                "RECORD_COUNT": int,
                "FIRST_SEEN_DT": str,
                "LAST_SEEN_DT": str,
            }
        ],
        "LAST_SEEN_DT": str,
        "RECORDS": [
            {
                "DATA_SOURCE": str,
                "RECORD_ID": str,
                "ENTITY_TYPE": str,
                "INTERNAL_ID": int,
                "ENTITY_KEY": str,
                "ENTITY_DESC": str,
                "MATCH_KEY": str,
                "MATCH_LEVEL": int,
                "MATCH_LEVEL_CODE": str,
                "ERRULE_CODE": str,
                "LAST_SEEN_DT": str,
            },
        ],
    },
    "RELATED_ENTITIES": [{}],
}

search_schema = {
    "RESOLVED_ENTITIES": [
        {
            "MATCH_INFO": {
                "MATCH_LEVEL": int,
                "MATCH_LEVEL_CODE": str,
                "MATCH_KEY": str,
                "ERRULE_CODE": str,
                "FEATURE_SCORES": {},
            },
            "ENTITY": {
                "RESOLVED_ENTITY": {
                    "ENTITY_ID": int,
                    "ENTITY_NAME": str,
                    "FEATURES": {},
                    "RECORD_SUMMARY": [
                        {
                            "DATA_SOURCE": str,
                            "RECORD_COUNT": int,
                            "FIRST_SEEN_DT": str,
                            "LAST_SEEN_DT": str,
                        }
                    ],
                    "LAST_SEEN_DT": str,
                }
            },
        }
    ]
}

stats_schema = {
    "workload": {
        "apiVersion": str,
        "loadedRecords": int,
        "addedRecords": int,
        "optimizedOut": int,
        "optimizedOutSkipped": int,
        "newObsEnt": int,
        "obsEntHashSame": int,
        "obsEntHashDiff": int,
        "partiallyResolved": int,
        "deletedRecords": int,
        "changeDeletes": int,
        "reevaluations": int,
        "repairedEntities": int,
        "duration": int,
        "retries": int,
        "candidates": int,
        "actualAmbiguousTest": int,
        "cachedAmbiguousTest": int,
        "libFeatCacheHit": int,
        "libFeatCacheMiss": int,
        "resFeatStatCacheHit": int,
        "resFeatStatCacheMiss": int,
        "libFeatInsert": int,
        "resFeatStatInsert": int,
        "resFeatStatUpdateAttempt": int,
        "resFeatStatUpdateFail": int,
        "unresolveTest": int,
        "abortedUnresolve": int,
        "gnrScorersUsed": int,
        "unresolveTriggers": {},
        "reresolveTriggers": {
            "abortRetry": int,
            "unresolveMovement": int,
            "multipleResolvableCandidates": int,
            "resolveNewFeatures": int,
            "newFeatureFTypes": [],
        },
        "reresolveSkipped": int,
        "filteredObsFeat": int,
        "expressedFeatureCalls": [],
        "expressedFeaturesCreated": [],
        "scoredPairs": [],
        "cacheHit": [],
        "cacheMiss": [],
        "redoTriggers": [],
        "latchContention": [],
        "highContentionFeat": [],
        "highContentionResEnt": [],
        "genericDetect": [],
        "candidateBuilders": [],
        "suppressedCandidateBuilders": [],
        "suppressedScoredFeatureType": [],
        "reducedScoredFeatureType": [],
        "suppressedDisclosedRelationshipDomainCount": int,
        "CorruptEntityTestDiagnosis": {},
        "threadState": {},
        "systemResources": {"initResources": [{}], "currResources": [{}]},
    }
}

virtual_entity_schema = {
    "RESOLVED_ENTITY": {
        "ENTITY_ID": int,
        "ENTITY_NAME": str,
        "FEATURES": {},
        "RECORD_SUMMARY": [
            {
                "DATA_SOURCE": str,
                "RECORD_COUNT": int,
                "FIRST_SEEN_DT": str,
                "LAST_SEEN_DT": str,
            }
        ],
        "LAST_SEEN_DT": str,
        "RECORDS": [
            {
                "DATA_SOURCE": str,
                "RECORD_ID": str,
                "ENTITY_TYPE": str,
                "INTERNAL_ID": int,
                "ENTITY_KEY": str,
                "ENTITY_DESC": str,
                "LAST_SEEN_DT": str,
                "FEATURES": [{"LIB_FEAT_ID": int}],
            },
        ],
    },
}

why_entities_results_schema = {
    "WHY_RESULTS": [
        {
            "ENTITY_ID": int,
            "ENTITY_ID_2": int,
            "MATCH_INFO": {},
        }
    ],
    "ENTITIES": [
        {
            "RESOLVED_ENTITY": {
                "ENTITY_ID": int,
                "ENTITY_NAME": str,
                "FEATURES": {},
                "RECORD_SUMMARY": [{}],
                "LAST_SEEN_DT": str,
                "RECORDS": [
                    {
                        "DATA_SOURCE": str,
                        "RECORD_ID": str,
                        "ENTITY_TYPE": str,
                        "INTERNAL_ID": int,
                        "ENTITY_KEY": str,
                        "ENTITY_DESC": str,
                        "MATCH_KEY": str,
                        "MATCH_LEVEL": int,
                        "MATCH_LEVEL_CODE": str,
                        "ERRULE_CODE": str,
                        "LAST_SEEN_DT": str,
                        "FEATURES": [{}],
                    }
                ],
            },
            "RELATED_ENTITIES": [{}],
        }
    ],
}


why_entity_results_schema = {
    "WHY_RESULTS": [
        {
            "INTERNAL_ID": int,
            "ENTITY_ID": int,
            "FOCUS_RECORDS": [{}],
            "MATCH_INFO": {
                "WHY_KEY": str,
                "WHY_ERRULE_CODE": str,
                "MATCH_LEVEL_CODE": str,
                "CANDIDATE_KEYS": {},
                "FEATURE_SCORES": {},
            },
        }
    ],
    "ENTITIES": [
        {
            "RESOLVED_ENTITY": {
                "ENTITY_ID": int,
                "ENTITY_NAME": str,
                "FEATURES": {},
                "RECORD_SUMMARY": [{}],
                "LAST_SEEN_DT": str,
                "RECORDS": [
                    {
                        "DATA_SOURCE": str,
                        "RECORD_ID": str,
                        "ENTITY_TYPE": str,
                        "INTERNAL_ID": int,
                        "ENTITY_KEY": str,
                        "ENTITY_DESC": str,
                        "MATCH_KEY": str,
                        "MATCH_LEVEL": int,
                        "MATCH_LEVEL_CODE": str,
                        "ERRULE_CODE": str,
                        "LAST_SEEN_DT": str,
                        "FEATURES": [{}],
                    }
                ],
            },
            "RELATED_ENTITIES": [{}],
        }
    ],
}

# -----------------------------------------------------------------------------
# G2Engine pre tests & setup
# -----------------------------------------------------------------------------


def test_add_truthset_datasources(engine_vars) -> None:
    """Add needed datasources for tests."""
    g2_config = g2config.G2Config(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
        engine_vars["VERBOSE_LOGGING"],
    )
    g2_configmgr = g2configmgr.G2ConfigMgr(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
        engine_vars["VERBOSE_LOGGING"],
    )
    g2_engine = g2engine.G2Engine(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
        engine_vars["VERBOSE_LOGGING"],
    )
    config_handle = g2_config.create()
    for _, value in TRUTHSET_DATASOURCES.items():
        g2_config.add_data_source(config_handle, value.get("Json", ""))
    json_config = g2_config.save(config_handle)
    new_config_id = g2_configmgr.add_config(json_config, "Test")
    g2_configmgr.set_default_config_id(new_config_id)
    g2_engine.reinit(new_config_id)


def test_add_truthset_data(engine_vars):
    """Add truthset data for tests"""
    g2_engine = g2engine.G2Engine(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
        engine_vars["VERBOSE_LOGGING"],
    )
    add_records_truthset(g2_engine)


# -----------------------------------------------------------------------------
# G2Engine testcases
# -----------------------------------------------------------------------------


def test_exception(g2_engine):
    """Test exceptions."""
    actual = g2_engine.new_exception(0)
    assert isinstance(actual, Exception)


def test_constructor(engine_vars):
    """Test constructor."""
    actual = g2engine.G2Engine(
        engine_vars["MODULE_NAME"],
        engine_vars["INI_PARAMS"],
        engine_vars["VERBOSE_LOGGING"],
    )
    assert isinstance(actual, g2engine.G2Engine)


def test_constructor_bad_module_name(engine_vars):
    """Test constructor."""
    bad_module_name = ""
    with pytest.raises(g2exception.G2Exception):
        g2engine.G2Engine(
            bad_module_name,
            engine_vars["INI_PARAMS"],
        )


def test_constructor_bad_ini_params(engine_vars):
    """Test constructor."""
    bad_ini_params = ""
    with pytest.raises(g2exception.G2Exception):
        g2engine.G2Engine(
            engine_vars["MODULE_NAME"],
            bad_ini_params,
        )


# TODO Was having issues with the as_c_ini in init
# def test_constructor_bad_verbose_logging(engine_vars):
#     """Test constructor."""


def test_add_record_dict(g2_engine):
    """Test add_record where the record is a dict."""
    data_source_code = "TEST"
    record_id = "1"
    json_data = RECORD_DICT
    g2_engine.add_record(data_source_code, record_id, json_data)


def test_add_record_str(g2_engine):
    """Test add_record where the record is a JSON string."""
    data_source_code = "TEST"
    record_id = "1"
    json_data = RECORD_STR
    g2_engine.add_record(data_source_code, record_id, json_data)


# TODO Modify as_c_char_p to convert int to str? More robust and allows mistakes to continue
def test_add_record_bad_data_source_code_type(g2_engine):
    """Test add_record with incorrect data source code type."""
    data_source_code = 1
    record_id = "1"
    json_data = RECORD_DICT
    with pytest.raises(TypeError):
        g2_engine.add_record(data_source_code, record_id, json_data)


def test_add_record_bad_data_source_code_value(g2_engine):
    """Test add_record with non-existent data source code."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1"
    json_data = RECORD_DICT
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record(data_source_code, record_id, json_data)


def test_add_record_bad_record(g2_engine):
    """Test add_record with bad JSON string."""
    data_source_code = "TEST"
    record_id = "1"
    json_data = RECORD_STR_BAD
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record(data_source_code, record_id, json_data)


def test_add_record_bad_record_id_type(g2_engine):
    """Test add_record with incorrect record id type."""
    data_source_code = "TEST"
    record_id = 1
    json_data = RECORD_DICT
    with pytest.raises(TypeError):
        g2_engine.add_record(data_source_code, record_id, json_data)


def test_add_record_data_source_code_empty(g2_engine):
    """Test add_record with empty data source code."""
    data_source_code = ""
    record_id = "1"
    json_data = RECORD_DICT
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record(data_source_code, record_id, json_data)


def test_add_record_record_str_empty(g2_engine):
    """Test add_record with empty record as a string"""
    data_source_code = "TEST"
    record_id = "1"
    json_data = ""
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record(data_source_code, record_id, json_data)


# NOTE This doesn't throw an exception because json dumps results in a valid json str '{}'
# def test_add_record_record_dict_empty(g2_engine):
#     """Test add_record with empty record as a dictionary"""
#     with pytest.raises(g2exception.G2Exception):
#         g2_engine.add_record(data_source_code, record_id, {})


def test_add_record_with_info_dict(g2_engine):
    """Test add_record_with_info where the record is a dict."""
    data_source_code = "TEST"
    record_id = "1"
    json_data = RECORD_DICT
    actual = g2_engine.add_record_with_info(data_source_code, record_id, json_data)
    actual_dict = json.loads(actual)
    assert schema(with_info_schema) == actual_dict


def test_add_record_with_info_str(g2_engine):
    """Test add_record_with_info where the record is a JSON string."""
    data_source_code = "TEST"
    record_id = "1"
    json_data = RECORD_STR
    actual = g2_engine.add_record_with_info(data_source_code, record_id, json_data)
    actual_dict = json.loads(actual)
    assert schema(with_info_schema) == actual_dict


# TODO Modify as_c_char_p to convert int to str? More robust and allows mistakes to continue
def test_add_record_with_info_bad_data_source_code_type(g2_engine):
    """Test add_record_with_info with incorrect data source code type."""
    data_source_code = 1
    record_id = "1"
    json_data = RECORD_DICT
    with pytest.raises(TypeError):
        g2_engine.add_record_with_info(data_source_code, record_id, json_data)


def test_add_record_with_info_bad_data_source_code_value(g2_engine):
    """Test add_record_with_info with non-existent data source code."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1"
    json_data = RECORD_DICT
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record_with_info(data_source_code, record_id, json_data)


def test_add_record_with_info_bad_record(g2_engine):
    """Test add_record with bad JSON string."""
    data_source_code = "TEST"
    record_id = "1"
    json_data = RECORD_STR_BAD
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record_with_info(data_source_code, record_id, json_data)


def test_add_record_with_info_bad_record_id_type(g2_engine):
    """Test add_record with incorrect record id type."""
    data_source_code = "TEST"
    record_id = 1
    json_data = RECORD_DICT
    with pytest.raises(TypeError):
        g2_engine.add_record_with_info(data_source_code, record_id, json_data)


def test_add_record_with_info_data_source_code_empty(g2_engine):
    """Test add_record with empty data source code."""
    data_source_code = ""
    record_id = "1"
    json_data = RECORD_DICT
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record_with_info(data_source_code, record_id, json_data)


def test_add_record_with_info_record_str_empty(g2_engine):
    """Test add_record_with_info with empty record as a string"""
    data_source_code = "TEST"
    record_id = "1"
    json_data = ""
    with pytest.raises(g2exception.G2Exception):
        g2_engine.add_record(data_source_code, record_id, json_data)


# TODO Close export


def test_count_redo_records(g2_engine):
    """Test count_redo_records"""
    actual = g2_engine.count_redo_records()
    assert actual == 0


def test_delete_record(g2_engine):
    """Test delete_record."""
    data_source_code = "TEST"
    record_id = "1"
    g2_engine.delete_record(data_source_code, record_id)


def test_delete_record_bad_data_source_code_type(g2_engine):
    """Test delete_record with incorrect data source code type."""
    data_source_code = 1
    record_id = "1"
    with pytest.raises(TypeError):
        g2_engine.add_record(data_source_code, record_id)


def test_delete_record_bad_data_source_code_value(g2_engine):
    """Test delete_record with non-existent data source code."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.delete_record(data_source_code, record_id)


def test_delete_record_data_source_code_empty(g2_engine):
    """Test delete_record with empty data source code."""
    data_source_code = ""
    record_id = "1"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.delete_record_with_info(data_source_code, record_id)


def test_delete_record_with_info(g2_engine):
    """Test delete_record_with_info."""
    data_source_code = "TEST"
    record_id = "1"
    json_data = RECORD_DICT
    g2_engine.add_record(data_source_code, record_id, json_data)
    actual = g2_engine.delete_record_with_info(data_source_code, record_id)
    actual_dict = json.loads(actual)
    assert schema(with_info_schema) == actual_dict


def test_delete_record_with_info_bad_data_source_code_type(g2_engine):
    """Test delete_record_with_info with incorrect data source code type."""
    data_source_code = 1
    record_id = "1"
    with pytest.raises(TypeError):
        g2_engine.delete_record_with_info(data_source_code, record_id)


def test_delete_record_with_info_bad_data_source_code_value(g2_engine):
    """Test delete_record_with_info with non-existent data source code."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.delete_record_with_info(data_source_code, record_id)


def test_delete_record_with_info_data_source_code_empty(g2_engine):
    """Test delete_record with empty data source code."""
    data_source_code = ""
    record_id = "1"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.delete_record_with_info(data_source_code, record_id)


# TODO Do destroy if using constructor?


def test_export_config(g2_engine) -> None:
    """Test export_config."""
    actual = g2_engine.export_config()
    actual_dict = json.loads(actual)
    assert schema(g2_config_schema) == actual_dict


def test_export_config_and_config_id(g2_engine) -> None:
    """Test export_config_and_config_id."""
    actual, actual_id = g2_engine.export_config_and_config_id()
    actual_dict = json.loads(actual)
    assert actual_id > 0
    assert schema(g2_config_schema) == actual_dict


def test_export_csv_entity_report(g2_engine) -> None:
    """Test export_csv_entity_report."""
    csv_headers = "RESOLVED_ENTITY_ID,RESOLVED_ENTITY_NAME,RELATED_ENTITY_ID,MATCH_LEVEL,MATCH_KEY,IS_DISCLOSED,IS_AMBIGUOUS,DATA_SOURCE,RECORD_ID,JSON_DATA,LAST_SEEN_DT,NAME_DATA,ATTRIBUTE_DATA,IDENTIFIER_DATA,ADDRESS_DATA,PHONE_DATA,RELATIONSHIP_DATA,ENTITY_DATA,OTHER_DATA"
    handle = g2_engine.export_csv_entity_report(csv_headers)
    actual = ""
    while True:
        fragment = g2_engine.fetch_next(handle)
        if not fragment:
            break
        actual += fragment
    g2_engine.close_export(handle)
    assert len(actual) > 0


def test_export_csv_entity_report_bad_header(g2_engine) -> None:
    """Test export_csv_entity_report with incorrect header value."""
    csv_headers = "RESOLVED_ENTITY_,RESOLVED_ENTITY_NAME,RELATED_ENTITY_ID,MATCH_LEVEL,MATCH_KEY,IS_DISCLOSED,IS_AMBIGUOUS,DATA_SOURCE,RECORD_ID,JSON_DATA,LAST_SEEN_DT,NAME_DATA,ATTRIBUTE_DATA,IDENTIFIER_DATA,ADDRESS_DATA,PHONE_DATA,RELATIONSHIP_DATA,ENTITY_DATA,OTHER_DATA"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.export_csv_entity_report(csv_headers)


def test_export_json_entity_report(g2_engine) -> None:
    """Test export_json_entity_report."""
    handle = g2_engine.export_json_entity_report()
    actual = g2_engine.fetch_next(handle)
    g2_engine.close_export(handle)
    actual_dict = json.loads(actual)
    assert schema(export_json_entity_report_schema) == actual_dict


# TODO fetch_next?

# TODO find_interesting_entities? It needs a config and is early adopter only


def test_find_network_by_entity_id_list_as_dict(g2_engine) -> None:
    """Test find_network_by_entity_id with entity_list as a dict"""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1027")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1069")
    entity_list = {
        "ENTITIES": [
            {"ENTITY_ID": entity_id_1},
            {"ENTITY_ID": entity_id_2},
        ]
    }
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    actual = g2_engine.find_network_by_entity_id(
        entity_list, max_degree, build_out_degree, max_entities
    )
    actual_dict = json.loads(actual)
    assert schema(network_schema) == actual_dict


def test_find_network_by_entity_id_list_as_str(g2_engine) -> None:
    """Test find_network_by_entity_id with entity_list as a string."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1027")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1069")
    entity_list = (
        f'{{"ENTITIES": [{{"ENTITY_ID": {entity_id_1}}}, {{"ENTITY_ID":'
        f" {entity_id_2}}}]}}"
    )
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    actual = g2_engine.find_network_by_entity_id(
        entity_list, max_degree, build_out_degree, max_entities
    )
    actual_dict = json.loads(actual)
    assert schema(network_schema) == actual_dict


def test_find_network_by_entity_id_bad_entity_ids(g2_engine) -> None:
    """Test find_network_by_entity_id with non-existent entities."""
    entity_list = {
        "ENTITIES": [
            {"ENTITY_ID": 99999999999998},
            {"ENTITY_ID": 99999999999999},
        ]
    }
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_network_by_entity_id(
            entity_list, max_degree, build_out_degree, max_entities
        )


def test_find_network_by_entity_id_empty_entity_list(g2_engine) -> None:
    """Test find_network_by_entity_id with empty list."""
    entity_list = {}
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    actual = g2_engine.find_network_by_entity_id(
        entity_list, max_degree, build_out_degree, max_entities
    )
    actual_dict = json.loads(actual)
    assert schema(network_schema) == actual_dict


def test_find_network_by_record_id_list_as_dict(g2_engine) -> None:
    """Test find_network_by_record_id with record_list as a dict."""
    record_list = {
        "RECORDS": [
            {"DATA_SOURCE": "WATCHLIST", "RECORD_ID": "1027"},
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1069"},
        ]
    }
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    actual = g2_engine.find_network_by_record_id(
        record_list, max_degree, build_out_degree, max_entities
    )
    actual_dict = json.loads(actual)
    assert schema(network_schema) == actual_dict


def test_find_network_by_record_id_list_as_str(g2_engine) -> None:
    """Test find_network_by_record_id with record_list as a string."""
    record_list = (
        '{"RECORDS": [{"DATA_SOURCE": "WATCHLIST", "RECORD_ID": "1027"},'
        ' {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1069"}]}'
    )
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    actual = g2_engine.find_network_by_record_id(
        record_list, max_degree, build_out_degree, max_entities
    )
    actual_dict = json.loads(actual)
    assert schema(network_schema) == actual_dict


def test_find_network_by_record_id_bad_data_source_code(g2_engine) -> None:
    """Test find_network_by_record_id with non-existent data source."""
    record_list = {
        "RECORDS": [
            {"DATA_SOURCE": "DOESN'T EXIST", "RECORD_ID": "1027"},
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1069"},
        ]
    }
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_network_by_record_id(
            record_list, max_degree, build_out_degree, max_entities
        )


def test_find_network_by_record_id_bad_record_ids(g2_engine) -> None:
    """Test find_network_by_record_id with non-existent record id."""
    record_list = {
        "RECORDS": [
            {"DATA_SOURCE": "WATCHLIST", "RECORD_ID": "9999999999999999"},
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1069"},
        ]
    }
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_network_by_record_id(
            record_list, max_degree, build_out_degree, max_entities
        )


def test_find_network_by_record_id_empty_record_list(g2_engine) -> None:
    """Test find_network_by_record_id with empty list."""
    record_list = {}
    max_degree = 5
    build_out_degree = 2
    max_entities = 10
    actual = g2_engine.find_network_by_record_id(
        record_list, max_degree, build_out_degree, max_entities
    )
    actual_dict = json.loads(actual)
    assert schema(network_schema) == actual_dict


def test_find_path_by_entity_id(g2_engine) -> None:
    """Test find_path_by_entity_id."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "2082")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "REFERENCE", "2131")
    max_degree = 5
    actual = g2_engine.find_path_by_entity_id(entity_id_1, entity_id_2, max_degree)
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_by_entity_id_bad_entity_ids(g2_engine) -> None:
    """Test find_path_by_entity_id with non-existent entities."""
    entity_id_1 = 99999999999998
    entity_id_2 = 99999999999999
    max_degree = 5
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_by_entity_id(entity_id_1, entity_id_2, max_degree)


def test_find_path_by_record_id(g2_engine) -> None:
    """Test find_path_by_record_id."""
    data_source_code_1 = "REFERENCE"
    record_id_1 = "2081"
    data_source_code_2 = "REFERENCE"
    record_id_2 = "2132"
    max_degree = 5
    actual = g2_engine.find_path_by_record_id(
        data_source_code_1, record_id_1, data_source_code_2, record_id_2, max_degree
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_by_record_id_bad_data_source_code(g2_engine) -> None:
    """Test find_path_by_record_id with non-existent data source."""
    data_source_code_1 = "DOESN'T EXIST"
    record_id_1 = "2081"
    data_source_code_2 = "REFERENCE"
    record_id_2 = "2132"
    max_degree = 5
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_by_record_id(
            data_source_code_1, record_id_1, data_source_code_2, record_id_2, max_degree
        )


def test_find_path_by_record_id_bad_record_ids(g2_engine) -> None:
    """Test find_path_by_record_id with non-existent record id."""
    data_source_code_1 = "REFERENCE"
    record_id_1 = "9999999999999999"
    data_source_code_2 = "REFERENCE"
    record_id_2 = "2132"
    max_degree = 5
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_by_record_id(
            data_source_code_1, record_id_1, data_source_code_2, record_id_2, max_degree
        )


def test_find_path_excluding_by_entity_id_dict(g2_engine) -> None:
    """Test find_path_excluding_by_entity_id where excluded entities is a dict."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1019")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1021")
    entity_id_3 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1009")
    max_degree = 5
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": entity_id_3}]}
    actual = g2_engine.find_path_excluding_by_entity_id(
        entity_id_1, entity_id_2, max_degree, excluded_entities
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_excluding_by_entity_id_str(g2_engine) -> None:
    """Test find_path_excluding_by_entity_id where excluded entities is a str."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1019")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1021")
    entity_id_3 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1009")
    max_degree = 5
    excluded_entities = f'{{"ENTITIES": [{{"ENTITY_ID": {entity_id_3}}}]}}'
    actual = g2_engine.find_path_excluding_by_entity_id(
        entity_id_1, entity_id_2, max_degree, excluded_entities
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_excluding_by_entity_id_bad_entity_ids(g2_engine) -> None:
    """Test find_path_excluding_by_entity_id with non-existent entities."""
    entity_id_1 = 9999999999999999
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1021")
    entity_id_3 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1009")
    max_degree = 5
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": entity_id_3}]}
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_excluding_by_entity_id(
            entity_id_1, entity_id_2, max_degree, excluded_entities
        )


# TODO excluded_records_dict = {"RECORDS": [{"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1009"}]}
# TODO Jira to look into / improve this in the engine
def test_find_path_excluding_by_record_id_dict(g2_engine) -> None:
    """Test find_path_excluding_by_record_id where the excluded entities is a dict."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1019"
    data_source_code_2 = "CUSTOMERS"
    record_id_2 = "1020"
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": "6"}]}
    actual = g2_engine.find_path_excluding_by_record_id(
        data_source_code_1,
        record_id_1,
        data_source_code_2,
        record_id_2,
        max_degree,
        excluded_entities,
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_excluding_by_record_id_str(g2_engine) -> None:
    """Test find_path_excluding_by_record_id where the excluded entities is a string."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1019"
    data_source_code_2 = "CUSTOMERS"
    record_id_2 = "1020"
    max_degree = 3
    # TODO Change to get the entity by record id?
    excluded_entities = '{"ENTITIES": [{"ENTITY_ID": "6"}]}'
    actual = g2_engine.find_path_excluding_by_record_id(
        data_source_code_1,
        record_id_1,
        data_source_code_2,
        record_id_2,
        max_degree,
        excluded_entities,
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_excluding_by_record_id_bad_data_source_code(g2_engine) -> None:
    """Test find_path_excluding_by_record_id with non-existent data source."""
    data_source_code_1 = "DOESN'T EXIST"
    record_id_1 = "1019"
    data_source_code_2 = "CUSTOMERS"
    record_id_2 = "1020"
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": "6"}]}
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_excluding_by_record_id(
            data_source_code_1,
            record_id_1,
            data_source_code_2,
            record_id_2,
            max_degree,
            excluded_entities,
        )


def test_find_path_excluding_by_record_id_bad_record_ids(g2_engine) -> None:
    """Test find_path_excluding_by_record_id with non-existent record id."""
    data_source_code_1 = "REFERENCE"
    record_id_1 = "9999999999999999"
    data_source_code_2 = "REFERENCE"
    record_id_2 = "2132"
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": "6"}]}
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_excluding_by_record_id(
            data_source_code_1,
            record_id_1,
            data_source_code_2,
            record_id_2,
            max_degree,
            excluded_entities,
        )


def test_find_path_excluding_by_record_id_excluded_entities_empty(g2_engine) -> None:
    """Test find_path_excluding_by_record_id where the excluded entities is empty."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1019"
    data_source_code_2 = "CUSTOMERS"
    record_id_2 = "1020"
    max_degree = 3
    excluded_entities = {}
    actual = g2_engine.find_path_excluding_by_record_id(
        data_source_code_1,
        record_id_1,
        data_source_code_2,
        record_id_2,
        max_degree,
        excluded_entities,
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


# TODO Can excluded use records like find path? Jira to discuss and recommend
def test_find_path_including_source_by_entity_id_dict(g2_engine) -> None:
    """Test find_path_including_source_by_entity_id where excluded/required args are dicts."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1004")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1007")
    entity_id_3 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1005")
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": entity_id_3}]}
    required_dsrcs = {"DATA_SOURCES": ["WATCHLIST"]}
    actual = g2_engine.find_path_including_source_by_entity_id(
        entity_id_1, entity_id_2, max_degree, excluded_entities, required_dsrcs
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_including_source_by_entity_id_str(g2_engine) -> None:
    """Test find_path_including_source_by_entity_id where excluded/required args are strings."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1004")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1007")
    entity_id_3 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1005")
    max_degree = 3
    excluded_entities = f'{{"ENTITIES": [{{"ENTITY_ID": {entity_id_3}}}]}}'
    required_dsrcs = '{"DATA_SOURCES": ["WATCHLIST"]}'
    actual = g2_engine.find_path_including_source_by_entity_id(
        entity_id_1, entity_id_2, max_degree, excluded_entities, required_dsrcs
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_including_source_by_entity_id_bad_entity_ids(g2_engine) -> None:
    """Test find_path_including_source_by_entity_id with non-existent entities."""
    entity_id_1 = 9999999999999999
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1007")
    entity_id_3 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1005")
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": entity_id_3}]}
    required_dsrcs = {"DATA_SOURCES": ["WATCHLIST"]}
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_including_source_by_entity_id(
            entity_id_1, entity_id_2, max_degree, excluded_entities, required_dsrcs
        )


def test_find_path_including_source_by_entity_id_excluded_entities_empty(
    g2_engine,
) -> None:
    """Test find_path_including_source_by_entity_id where the excluded entities is empty."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1004")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1007")
    max_degree = 3
    excluded_entities = {}
    required_dsrcs = {"DATA_SOURCES": ["WATCHLIST"]}
    actual = g2_engine.find_path_including_source_by_entity_id(
        entity_id_1, entity_id_2, max_degree, excluded_entities, required_dsrcs
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_including_source_by_entity_id_required_dsrcs_empty(
    g2_engine,
) -> None:
    """Test find_path_including_source_by_entity_id where the required data sources is empty."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1004")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "WATCHLIST", "1007")
    entity_id_3 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1005")
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": entity_id_3}]}
    required_dsrcs = {}
    actual = g2_engine.find_path_including_source_by_entity_id(
        entity_id_1, entity_id_2, max_degree, excluded_entities, required_dsrcs
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_including_source_by_record_id_dict(g2_engine) -> None:
    """Test find_path_including_source_by_record_id excluded/required args are dicts."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1001"
    data_source_code_2 = "WATCHLIST"
    record_id_2 = "1007"
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": "5"}]}
    required_dsrcs = {"DATA_SOURCES": ["WATCHLIST"]}
    actual = g2_engine.find_path_including_source_by_record_id(
        data_source_code_1,
        record_id_1,
        data_source_code_2,
        record_id_2,
        max_degree,
        excluded_entities,
        required_dsrcs,
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_including_source_by_record_id_str(g2_engine) -> None:
    """Test find_path_including_source_by_record_id excluded/required args are strings."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1001"
    data_source_code_2 = "WATCHLIST"
    record_id_2 = "1007"
    max_degree = 3
    # TODO Change these in all methods to get by record id
    excluded_entities = '{"ENTITIES": [{"ENTITY_ID": "5"}]}'
    required_dsrcs = '{"DATA_SOURCES": ["WATCHLIST"]}'
    actual = g2_engine.find_path_including_source_by_record_id(
        data_source_code_1,
        record_id_1,
        data_source_code_2,
        record_id_2,
        max_degree,
        excluded_entities,
        required_dsrcs,
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_including_source_by_record_id_bad_data_source_code(
    g2_engine,
) -> None:
    """Test find_path_including_source_by_record_id with non-existent data source."""
    data_source_code_1 = "DOESN'T EXIST"
    record_id_1 = "1001"
    data_source_code_2 = "WATCHLIST"
    record_id_2 = "1007"
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": "6"}]}
    required_dsrcs = {"DATA_SOURCES": ["WATCHLIST"]}
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_including_source_by_record_id(
            data_source_code_1,
            record_id_1,
            data_source_code_2,
            record_id_2,
            max_degree,
            excluded_entities,
            required_dsrcs,
        )


def test_find_path_including_source_by_record_id_bad_record_ids(g2_engine) -> None:
    """Test find_path_including_source_by_record_id with non-existent record id."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "9999999999999999"
    data_source_code_2 = "WATCHLIST"
    record_id_2 = "1007"
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": "6"}]}
    required_dsrcs = {"DATA_SOURCES": ["WATCHLIST"]}
    with pytest.raises(g2exception.G2Exception):
        g2_engine.find_path_including_source_by_record_id(
            data_source_code_1,
            record_id_1,
            data_source_code_2,
            record_id_2,
            max_degree,
            excluded_entities,
            required_dsrcs,
        )


def test_find_path_including_source_by_record_id_excluded_entities_empty(
    g2_engine,
) -> None:
    """Test find_path_including_source_by_record_id where the excluded entities is empty."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1001"
    data_source_code_2 = "WATCHLIST"
    record_id_2 = "1007"
    max_degree = 3
    excluded_entities = {}
    required_dsrcs = '{"DATA_SOURCES": ["WATCHLIST"]}'
    actual = g2_engine.find_path_including_source_by_record_id(
        data_source_code_1,
        record_id_1,
        data_source_code_2,
        record_id_2,
        max_degree,
        excluded_entities,
        required_dsrcs,
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_find_path_including_source_by_record_id_required_dsrcs_empty(
    g2_engine,
) -> None:
    """Test find_path_including_source_by_record_id where the required data sources is empty."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1001"
    data_source_code_2 = "WATCHLIST"
    record_id_2 = "1007"
    max_degree = 3
    excluded_entities = {"ENTITIES": [{"ENTITY_ID": "6"}]}
    required_dsrcs = {}
    actual = g2_engine.find_path_including_source_by_record_id(
        data_source_code_1,
        record_id_1,
        data_source_code_2,
        record_id_2,
        max_degree,
        excluded_entities,
        required_dsrcs,
    )
    actual_dict = json.loads(actual)
    assert schema(path_schema) == actual_dict


def test_get_active_config_id(g2_engine):
    """Test get_active_config_id"""
    actual = g2_engine.get_active_config_id()
    assert actual >= 0


def test_get_entity_by_entity_id(
    g2_engine,
) -> None:
    """Test get_entity_by_entity_id."""
    entity_id = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1001")
    actual = g2_engine.get_entity_by_entity_id(entity_id)
    actual_dict = json.loads(actual)
    assert schema(resolved_entity_schema) == actual_dict


def test_get_entity_by_entity_id_bad_entity_ids(g2_engine) -> None:
    """Test get_entity_by_entity_id with non-existent entities."""
    entity_id = 9999999999999999
    with pytest.raises(g2exception.G2Exception):
        g2_engine.get_entity_by_entity_id(entity_id)


def test_get_entity_by_record_id(g2_engine) -> None:
    """Test get_entity_by_record_id."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    actual = g2_engine.get_entity_by_record_id(data_source_code, record_id)
    actual_dict = json.loads(actual)
    assert schema(resolved_entity_schema) == actual_dict


def test_get_entity_by_record_id_bad_data_source_code(g2_engine) -> None:
    """Test get_entity_by_record_id with non-existent data source."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1001"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.get_entity_by_record_id(data_source_code, record_id)


def test_get_entity_by_record_id_bad_record_id(g2_engine) -> None:
    """Test get_entity_by_record_id with non-existent record id."""
    data_source_code = "CUSTOMERS"
    record_id = "9999999999999999"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.get_entity_by_record_id(data_source_code, record_id)


def test_get_record(g2_engine) -> None:
    """Test get_record."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    actual = g2_engine.get_record(data_source_code, record_id)
    actual_dict = json.loads(actual)
    assert schema(record_schema) == actual_dict


def test_get_record_bad_data_source_code(g2_engine) -> None:
    """Test get_record with non-existent data source."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1001"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.get_record(data_source_code, record_id)


def test_get_record_bad_record_id(g2_engine) -> None:
    """Test get_record with non-existent record id."""
    data_source_code = "CUSTOMERS"
    record_id = "9999999999999999"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.get_record(data_source_code, record_id)


def test_get_redo_record(g2_engine):
    """Test get_redo_record."""
    g2_engine.purge_repository()
    add_records_truthset(g2_engine, do_redo=False)
    actual = g2_engine.get_redo_record()
    actual_dict = json.loads(actual)
    add_records_truthset(g2_engine)
    assert schema(redo_record_schema) == actual_dict


def test_get_repository_last_modified_time(g2_engine):
    """Test get_repository_last_modified_time"""
    actual = g2_engine.get_repository_last_modified_time()
    assert actual >= 0


def test_get_virtual_entity_by_record_id_as_dict(
    g2_engine,
) -> None:
    """Test get_virtual_entity_by_record_id with record_list as a dict."""
    record_list = {
        "RECORDS": [
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1001"},
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1022"},
        ]
    }
    actual = g2_engine.get_virtual_entity_by_record_id(record_list)
    actual_dict = json.loads(actual)
    assert schema(virtual_entity_schema) == actual_dict


def test_get_virtual_entity_by_record_id_as_str(
    g2_engine,
) -> None:
    """Test get_virtual_entity_by_record_id with record_list as a string."""
    record_list = (
        '{"RECORDS": [{"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1001"},'
        ' {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1022"}]}'
    )
    actual = g2_engine.get_virtual_entity_by_record_id(record_list)
    actual_dict = json.loads(actual)
    assert schema(virtual_entity_schema) == actual_dict


def test_get_virtual_entity_by_record_id_bad_data_source_code(
    g2_engine,
) -> None:
    """Test get_virtual_entity_by_record_id with non-existent data source."""
    record_list = {
        "RECORDS": [
            {"DATA_SOURCE": "DOESN'T EXIST", "RECORD_ID": "1001"},
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1022"},
        ]
    }
    with pytest.raises(g2exception.G2Exception):
        g2_engine.get_virtual_entity_by_record_id(record_list)


def test_get_virtual_entity_by_record_id_bad_record_id(
    g2_engine,
) -> None:
    """Test get_virtual_entity_by_record_id with non-existent record id."""
    record_list = {
        "RECORDS": [
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "9999999999999999"},
            {"DATA_SOURCE": "CUSTOMERS", "RECORD_ID": "1022"},
        ]
    }
    with pytest.raises(g2exception.G2Exception):
        g2_engine.get_virtual_entity_by_record_id(record_list)


def test_how_entity_by_entity_id(g2_engine) -> None:
    """Test how_entity_by_entity_id."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    entity_id = get_entity_id_from_record_id(g2_engine, data_source_code, record_id)
    actual = g2_engine.how_entity_by_entity_id(entity_id)
    actual_dict = json.loads(actual)
    assert schema(how_results_schema) == actual_dict


def test_how_entity_by_entity_id_bad_entity_id(g2_engine) -> None:
    """Test how_entity_by_entity_id with non-existent entity."""
    entity_id = "9999999999999999"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.how_entity_by_entity_id(entity_id)


# TODO Add testing bad args
def test_init_and_destroy(engine_vars) -> None:
    """Test init and destroy."""
    module_name = "Test"
    ini_params = engine_vars["INI_PARAMS"]
    g2_engine_init_destroy = g2engine.G2Engine()
    g2_engine_init_destroy.init(module_name, ini_params)
    g2_engine_init_destroy.destroy()


# TODO Add test for constructor to take init_config_id when modified g2engine.py
def test_init_with_config_id(engine_vars) -> None:
    """Test init_with_config_id."""
    module_name = "Test"
    ini_params = engine_vars["INI_PARAMS"]
    g2_engine_2 = g2engine.G2Engine()
    g2_engine_2.init(module_name, ini_params)
    init_config_id = g2_engine_2.get_active_config_id()
    g2_engine_2.destroy()
    g2_engine_2 = g2engine.G2Engine()
    g2_engine_2.init_with_config_id(module_name, ini_params, init_config_id)


# NOTE Having issues with this, coming back to...
# def test_init_with_config_id_bad_config_id(engine_vars) -> None:
#     """Test init_with_config_id with non-existent config id."""
#     module_name = "Test"
#     ini_params = engine_vars["INI_PARAMS"]
#     init_config_id = 0
#     g2_engine_with_id = g2engine.G2Engine()
#     with pytest.raises(g2exception.G2Exception):
#         g2_engine_with_id.init_with_config_id(module_name, ini_params, init_config_id)


def test_prime_engine(g2_engine) -> None:
    """Test prime_engine."""
    g2_engine.prime_engine()


# NOTE process and process_with_info are going away in V4, not adding tests for them
# TODO Add tests for process_redo_record / _with_info when available in V4


def test_purge_repository(g2_engine) -> None:
    """Test purge_repository."""
    g2_engine.purge_repository()
    add_records_truthset(g2_engine)


# NOTE Don't need to test a non-existent entity, if not found it is ignored by the engine similar to delete_record
def test_reevaluate_entity(g2_engine) -> None:
    """Test reevaluate_entity."""
    entity_id = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1001")
    g2_engine.reevaluate_entity(entity_id)


def test_reevaluate_entity_with_info(g2_engine) -> None:
    """Test reevaluate_entity_with_info."""
    entity_id = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1001")
    actual = g2_engine.reevaluate_entity_with_info(entity_id)
    actual_dict = json.loads(actual)
    assert schema(with_info_schema) == actual_dict


def test_reevaluate_record(g2_engine) -> None:
    """Test reevaluate_record."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    g2_engine.reevaluate_record(data_source_code, record_id)


def test_reevaluate_record_bad_data_source_code(g2_engine) -> None:
    """Test reevaluate_record with non-existent data source code."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1001"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.reevaluate_record(data_source_code, record_id)


def test_reevaluate_record_bad_record_id(g2_engine) -> None:
    """Test reevaluate_record with non-existent record id."""
    data_source_code = "CUSTOMERS"
    record_id = "9999999999999999"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.reevaluate_record(data_source_code, record_id)


def test_reevaluate_record_with_info(g2_engine) -> None:
    """Test reevaluate_record_with_info."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    actual = g2_engine.reevaluate_record_with_info(data_source_code, record_id)
    actual_dict = json.loads(actual)
    assert schema(with_info_schema) == actual_dict


def test_reevaluate_record_with_info_bad_data_source_code(g2_engine) -> None:
    """Test reevaluate_record_with_info with non-existent data source code."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1001"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.reevaluate_record_with_info(data_source_code, record_id)


def test_reevaluate_record_with_info_bad_record_id(g2_engine) -> None:
    """Test reevaluate_record_with_info with non-existent record id."""
    data_source_code = "CUSTOMERS"
    record_id = "9999999999999999"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.reevaluate_record_with_info(data_source_code, record_id)


def test_reinit(g2_engine) -> None:
    """Test reinit."""
    config_id = g2_engine.get_active_config_id()
    g2_engine.reinit(config_id)


def test_reinit_bad_config_id(g2_engine) -> None:
    """Test reinit with bad config id."""
    active_config_id = g2_engine.get_active_config_id()
    config_id = 0
    try:
        with pytest.raises(g2exception.G2Exception):
            g2_engine.reinit(config_id)
    finally:
        g2_engine.reinit(active_config_id)


def test_replace_record(g2_engine) -> None:
    """Test replace_record."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    current_record = g2_engine.get_record(data_source_code, record_id)
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    new_json_record = current_json_data
    new_json_record["ADDR_LINE1"] = "123 Main Street, Las Vegas NV 99999"
    g2_engine.replace_record(data_source_code, record_id, new_json_record)
    g2_engine.replace_record(data_source_code, record_id, current_json_data)


def test_replace_record_bad_data_source_code(g2_engine) -> None:
    """Test replace_record with non-existent data source."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1001"
    current_record = g2_engine.get_record("CUSTOMERS", record_id)
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    try:
        with pytest.raises(g2exception.G2Exception):
            g2_engine.replace_record(data_source_code, record_id, current_json_data)
    finally:
        g2_engine.replace_record("CUSTOMERS", record_id, current_json_data)


def test_replace_record_bad_record_id(g2_engine) -> None:
    """Test replace_record with non-existent record id."""
    data_source_code = "CUSTOMERS"
    record_id = "9999999999999999"
    current_record = g2_engine.get_record(data_source_code, "1001")
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    try:
        with pytest.raises(g2exception.G2Exception):
            g2_engine.replace_record(data_source_code, record_id, current_json_data)
    finally:
        g2_engine.replace_record(data_source_code, "1001", current_json_data)


def test_replace_record_bad_record(g2_engine) -> None:
    """Test replace_record with bad JSON string."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    current_record = g2_engine.get_record(data_source_code, record_id)
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    try:
        with pytest.raises(g2exception.G2Exception):
            g2_engine.replace_record(data_source_code, record_id, RECORD_STR_BAD)
    finally:
        g2_engine.replace_record(data_source_code, record_id, current_json_data)


def test_replace_record_with_info(g2_engine) -> None:
    """Test replace_record_with_info."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    current_record = g2_engine.get_record(data_source_code, record_id)
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    new_json_record = current_json_data
    new_json_record["ADDR_LINE1"] = "123 Main Street, Las Vegas NV 99999"
    actual = g2_engine.replace_record_with_info(
        data_source_code, record_id, new_json_record
    )
    actual_dict = json.loads(actual)
    assert schema(with_info_schema) == actual_dict
    g2_engine.replace_record(data_source_code, record_id, current_json_data)


def test_replace_record_with_info_bad_data_source_code(g2_engine) -> None:
    """Test replace_record_with_info with non-existent data source."""
    data_source_code = "DOESN'T EXIST"
    record_id = "1001"
    current_record = g2_engine.get_record("CUSTOMERS", record_id)
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    try:
        with pytest.raises(g2exception.G2Exception):
            g2_engine.replace_record_with_info(
                data_source_code, record_id, current_json_data
            )
    finally:
        g2_engine.replace_record("CUSTOMERS", record_id, current_json_data)


def test_replace_record_with_info_bad_record_id(g2_engine) -> None:
    """Test replace_record_with_info with non-existent record id."""
    data_source_code = "CUSTOMERS"
    record_id = "9999999999999999"
    current_record = g2_engine.get_record(data_source_code, "1001")
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    try:
        with pytest.raises(g2exception.G2Exception):
            g2_engine.replace_record_with_info(
                data_source_code, record_id, current_json_data
            )
    finally:
        g2_engine.replace_record(data_source_code, "1001", current_json_data)


def test_replace_record_with_info_bad_record(g2_engine) -> None:
    """Test replace_record_with_info with bad JSON string."""
    data_source_code = "CUSTOMERS"
    record_id = "1001"
    current_record = g2_engine.get_record(data_source_code, record_id)
    data = json.loads(current_record)
    current_json_data = data["JSON_DATA"]
    try:
        with pytest.raises(g2exception.G2Exception):
            g2_engine.replace_record_with_info(
                data_source_code, record_id, RECORD_STR_BAD
            )
    finally:
        g2_engine.replace_record(data_source_code, record_id, current_json_data)


def test_search_by_attributes(g2_engine) -> None:
    """Test search_by_attributes."""
    json_data = {"NAME_FULL": "robert smith", "DATE_OF_BIRTH": "12/11/1978"}
    actual = g2_engine.search_by_attributes(json_data)
    actual_dict = json.loads(actual)
    assert schema(search_schema) == actual_dict


def test_search_by_attributes_bad_json_data(g2_engine) -> None:
    """Test search_by_attributes with bad JSON string."""
    json_data = '{"NAME_FULL" "robert smith", "DATE_OF_BIRTH": "12/11/1978"}'
    with pytest.raises(g2exception.G2Exception):
        g2_engine.search_by_attributes(json_data)


# NOTE Having issues with this, coming back to...
# def test_stats(engine_vars) -> None:
#     """Test stats."""
#     # Use a fresh engine so stats are mostly blank to align to stats_schema
#     g2_engine_stats = g2engine.G2Engine(
#         engine_vars["MODULE_NAME"], engine_vars["INI_PARAMS"]
#     )
#     actual = g2_engine_stats.stats()
#     actual_dict = json.loads(actual)
#     assert schema(stats_schema) == actual_dict


# NOTE Following are going away in V4
# why_entity_by_entity_id
# why_entity_by_record_id


def test_why_entities(g2_engine) -> None:
    """Test why_entities."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1001")
    entity_id_2 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1002")
    actual = g2_engine.why_entities(entity_id_1, entity_id_2)
    actual_dict = json.loads(actual)
    assert schema(why_entities_results_schema) == actual_dict


def test_why_entities_bad_entity_id(g2_engine) -> None:
    """Test why_entities with non-existent entity."""
    entity_id_1 = get_entity_id_from_record_id(g2_engine, "CUSTOMERS", "1001")
    entity_id_2 = 9999999999999999
    with pytest.raises(g2exception.G2Exception):
        g2_engine.why_entities(entity_id_1, entity_id_2)


def test_why_records(g2_engine) -> None:
    """Test why_records."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "1001"
    data_source_code_2 = "CUSTOMERS"
    record_id_2 = "1002"
    actual = g2_engine.why_records(
        data_source_code_1, record_id_1, data_source_code_2, record_id_2
    )
    actual_dict = json.loads(actual)
    assert schema(why_entity_results_schema) == actual_dict


def test_why_records_bad_data_source_code(g2_engine) -> None:
    """Test why_records with non-existent data source."""
    data_source_code_1 = "DOESN'T EXIST"
    record_id_1 = "1001"
    data_source_code_2 = "CUSTOMERS"
    record_id_2 = "1002"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.why_records(
            data_source_code_1, record_id_1, data_source_code_2, record_id_2
        )


def test_why_records_bad_record_id(g2_engine) -> None:
    """Test why_records with non-existent record id."""
    data_source_code_1 = "CUSTOMERS"
    record_id_1 = "9999999999999999"
    data_source_code_2 = "CUSTOMERS"
    record_id_2 = "1002"
    with pytest.raises(g2exception.G2Exception):
        g2_engine.why_records(
            data_source_code_1, record_id_1, data_source_code_2, record_id_2
        )


# -----------------------------------------------------------------------------
# Utilities
# -----------------------------------------------------------------------------


def add_records_truthset(g2_engine, do_redo=True) -> None:
    """Add all truth-set the records."""
    for record_set in DATA_SOURCES.values():
        for record in record_set.values():
            g2_engine.add_record(
                record.get("DataSource"), record.get("Id"), record.get("Json")
            )
    if do_redo:
        while g2_engine.count_redo_records() > 0:
            record = g2_engine.get_redo_record()
            g2_engine.process(record)


# TODO add type for other g2_engines
def get_entity_id_from_record_id(
    g2_engine: g2engine.G2Engine, data_source_code: str, record_id: str
) -> int:
    """Given a datasource and record_id return the entity ID."""
    entity_json = g2_engine.get_entity_by_record_id(
        data_source_code,
        record_id,
    )
    entity = json.loads(entity_json)
    return int(entity.get("RESOLVED_ENTITY", {}).get("ENTITY_ID", 0))
