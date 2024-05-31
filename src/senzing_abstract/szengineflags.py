"""
TODO: szengineflags.py
"""

from enum import IntFlag
from typing import Any, List

# Metadata

__all__ = ["SzEngineFlags"]
__version__ = "0.0.1"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = "2023-10-30"
__updated__ = "2023-10-30"

# -----------------------------------------------------------------------------
# SzEngineFlags class
# -----------------------------------------------------------------------------


class SzEngineFlags(IntFlag):
    """Engine Flags ..."""

    @classmethod
    def combine_flags(
        cls, list_of_strings: List[str], *args: Any, **kwargs: Any
    ) -> int:
        """OR together all strings in list_of_strings"""
        # pylint: disable=unused-argument

        result = 0
        for string in list_of_strings:
            result = result | SzEngineFlags[string]
        return result

    @classmethod
    def get_flag_int(cls, flag: IntFlag) -> int:
        """# TODO"""
        return flag.value

    # Flags for exporting entity data.

    SZ_EXPORT_INCLUDE_MULTI_RECORD_ENTITIES = 1 << 0
    SZ_EXPORT_INCLUDE_POSSIBLY_SAME = 1 << 1
    SZ_EXPORT_INCLUDE_POSSIBLY_RELATED = 1 << 2
    SZ_EXPORT_INCLUDE_NAME_ONLY = 1 << 3
    SZ_EXPORT_INCLUDE_DISCLOSED = 1 << 4
    SZ_EXPORT_INCLUDE_SINGLE_RECORD_ENTITIES = 1 << 5
    SZ_EXPORT_INCLUDE_ALL_ENTITIES = (
        SZ_EXPORT_INCLUDE_MULTI_RECORD_ENTITIES
        | SZ_EXPORT_INCLUDE_SINGLE_RECORD_ENTITIES
    )
    SZ_EXPORT_INCLUDE_ALL_HAVING_RELATIONSHIPS = (
        SZ_EXPORT_INCLUDE_POSSIBLY_SAME
        | SZ_EXPORT_INCLUDE_POSSIBLY_RELATED
        | SZ_EXPORT_INCLUDE_NAME_ONLY
        | SZ_EXPORT_INCLUDE_DISCLOSED
    )

    # Flags for outputting entity relation data.

    SZ_ENTITY_INCLUDE_POSSIBLY_SAME_RELATIONS = 1 << 6
    SZ_ENTITY_INCLUDE_POSSIBLY_RELATED_RELATIONS = 1 << 7
    SZ_ENTITY_INCLUDE_NAME_ONLY_RELATIONS = 1 << 8
    SZ_ENTITY_INCLUDE_DISCLOSED_RELATIONS = 1 << 9
    SZ_ENTITY_INCLUDE_ALL_RELATIONS = (
        SZ_ENTITY_INCLUDE_POSSIBLY_SAME_RELATIONS
        | SZ_ENTITY_INCLUDE_POSSIBLY_RELATED_RELATIONS
        | SZ_ENTITY_INCLUDE_NAME_ONLY_RELATIONS
        | SZ_ENTITY_INCLUDE_DISCLOSED_RELATIONS
    )

    # Flags for outputting entity feature data.

    SZ_ENTITY_INCLUDE_ALL_FEATURES = 1 << 10
    SZ_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES = 1 << 11

    # Flags for getting extra information about an entity.

    SZ_ENTITY_INCLUDE_ENTITY_NAME = 1 << 12
    SZ_ENTITY_INCLUDE_RECORD_SUMMARY = 1 << 13
    SZ_ENTITY_INCLUDE_RECORD_TYPES = 1 << 28
    SZ_ENTITY_INCLUDE_RECORD_DATA = 1 << 14
    SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO = 1 << 15
    SZ_ENTITY_INCLUDE_RECORD_JSON_DATA = 1 << 16
    SZ_ENTITY_INCLUDE_RECORD_UNMAPPED_DATA = 1 << 31
    SZ_ENTITY_INCLUDE_RECORD_FEATURE_IDS = 1 << 18
    SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME = 1 << 19
    SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO = 1 << 20
    SZ_ENTITY_INCLUDE_RELATED_RECORD_SUMMARY = 1 << 21
    SZ_ENTITY_INCLUDE_RELATED_RECORD_DATA = 1 << 22

    # Flags for extra feature data.

    SZ_ENTITY_INCLUDE_INTERNAL_FEATURES = 1 << 23
    SZ_ENTITY_INCLUDE_FEATURE_STATS = 1 << 24
    SZ_ENTITY_INCLUDE_FEATURE_ELEMENTS = 1 << 32

    # Flags for extra matching data.

    SZ_INCLUDE_MATCH_KEY_DETAILS = 1 << 34

    # Flags for finding entity path & network data.

    SZ_FIND_PATH_PREFER_EXCLUDE = 1 << 25
    SZ_FIND_PATH_INCLUDE_MATCHING_INFO = 1 << 30
    SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO = 1 << 33

    # Flags for including search result information.

    SZ_INCLUDE_FEATURE_SCORES = 1 << 26
    SZ_SEARCH_INCLUDE_STATS = 1 << 27

    # Flag for returning with info responses.
    SZ_WITH_INFO = 1 << 62

    # Flags for exporting entity data.

    SZ_SEARCH_INCLUDE_RESOLVED = SZ_EXPORT_INCLUDE_MULTI_RECORD_ENTITIES
    SZ_SEARCH_INCLUDE_POSSIBLY_SAME = SZ_EXPORT_INCLUDE_POSSIBLY_SAME
    SZ_SEARCH_INCLUDE_POSSIBLY_RELATED = SZ_EXPORT_INCLUDE_POSSIBLY_RELATED
    SZ_SEARCH_INCLUDE_NAME_ONLY = SZ_EXPORT_INCLUDE_NAME_ONLY
    SZ_SEARCH_INCLUDE_ALL_ENTITIES = (
        SZ_SEARCH_INCLUDE_RESOLVED
        | SZ_SEARCH_INCLUDE_POSSIBLY_SAME
        | SZ_SEARCH_INCLUDE_POSSIBLY_RELATED
        | SZ_SEARCH_INCLUDE_NAME_ONLY
    )

    # Recommended settings.

    SZ_RECORD_DEFAULT_FLAGS = SZ_ENTITY_INCLUDE_RECORD_JSON_DATA

    SZ_ENTITY_DEFAULT_FLAGS = (
        SZ_ENTITY_INCLUDE_ALL_RELATIONS
        | SZ_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES
        | SZ_ENTITY_INCLUDE_ENTITY_NAME
        | SZ_ENTITY_INCLUDE_RECORD_SUMMARY
        | SZ_ENTITY_INCLUDE_RECORD_DATA
        | SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO
        | SZ_ENTITY_INCLUDE_RELATED_ENTITY_NAME
        | SZ_ENTITY_INCLUDE_RELATED_RECORD_SUMMARY
        | SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
    )

    SZ_ENTITY_BRIEF_DEFAULT_FLAGS = (
        SZ_ENTITY_INCLUDE_RECORD_MATCHING_INFO
        | SZ_ENTITY_INCLUDE_ALL_RELATIONS
        | SZ_ENTITY_INCLUDE_RELATED_MATCHING_INFO
    )

    SZ_EXPORT_DEFAULT_FLAGS = (
        SZ_EXPORT_INCLUDE_ALL_ENTITIES
        # NOTE Check, was removed in 4.0.0.24095 - 2024_04_04__00_00
        # NOTE There are changes in V4 to output messages and Jae is likely still working on them
        # | SZ_EXPORT_INCLUDE_ALL_HAVING_RELATIONSHIPS
        | SZ_ENTITY_DEFAULT_FLAGS
    )

    SZ_FIND_PATH_DEFAULT_FLAGS = (
        SZ_FIND_PATH_INCLUDE_MATCHING_INFO
        | SZ_ENTITY_INCLUDE_ENTITY_NAME
        | SZ_ENTITY_INCLUDE_RECORD_SUMMARY
    )

    SZ_FIND_NETWORK_DEFAULT_FLAGS = (
        SZ_FIND_NETWORK_INCLUDE_MATCHING_INFO
        | SZ_ENTITY_INCLUDE_ENTITY_NAME
        | SZ_ENTITY_INCLUDE_RECORD_SUMMARY
    )

    SZ_WHY_ENTITIES_DEFAULT_FLAGS = (
        SZ_ENTITY_DEFAULT_FLAGS
        | SZ_ENTITY_INCLUDE_INTERNAL_FEATURES
        | SZ_ENTITY_INCLUDE_FEATURE_STATS
        | SZ_INCLUDE_FEATURE_SCORES
    )

    SZ_WHY_RECORDS_DEFAULT_FLAGS = (
        SZ_ENTITY_DEFAULT_FLAGS
        | SZ_ENTITY_INCLUDE_INTERNAL_FEATURES
        | SZ_ENTITY_INCLUDE_FEATURE_STATS
        | SZ_INCLUDE_FEATURE_SCORES
    )

    SZ_WHY_RECORD_IN_ENTITY_DEFAULT_FLAGS = (
        SZ_ENTITY_DEFAULT_FLAGS
        | SZ_ENTITY_INCLUDE_INTERNAL_FEATURES
        | SZ_ENTITY_INCLUDE_FEATURE_STATS
        | SZ_INCLUDE_FEATURE_SCORES
    )

    SZ_HOW_ENTITY_DEFAULT_FLAGS = SZ_INCLUDE_FEATURE_SCORES

    SZ_VIRTUAL_ENTITY_DEFAULT_FLAGS = SZ_ENTITY_DEFAULT_FLAGS

    SZ_SEARCH_BY_ATTRIBUTES_ALL = (
        SZ_SEARCH_INCLUDE_ALL_ENTITIES
        | SZ_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES
        | SZ_ENTITY_INCLUDE_ENTITY_NAME
        | SZ_ENTITY_INCLUDE_RECORD_SUMMARY
        | SZ_INCLUDE_FEATURE_SCORES
    )

    SZ_SEARCH_BY_ATTRIBUTES_STRONG = (
        SZ_SEARCH_INCLUDE_RESOLVED
        | SZ_SEARCH_INCLUDE_POSSIBLY_SAME
        | SZ_ENTITY_INCLUDE_REPRESENTATIVE_FEATURES
        | SZ_ENTITY_INCLUDE_ENTITY_NAME
        | SZ_ENTITY_INCLUDE_RECORD_SUMMARY
        | SZ_INCLUDE_FEATURE_SCORES
    )

    SZ_SEARCH_BY_ATTRIBUTES_MINIMAL_ALL = SZ_SEARCH_INCLUDE_ALL_ENTITIES

    SZ_SEARCH_BY_ATTRIBUTES_MINIMAL_STRONG = (
        SZ_SEARCH_INCLUDE_RESOLVED | SZ_SEARCH_INCLUDE_POSSIBLY_SAME
    )

    SZ_SEARCH_BY_ATTRIBUTES_DEFAULT_FLAGS = SZ_SEARCH_BY_ATTRIBUTES_ALL

    # -----------------------------------------------------------------------------
    # non-SzEngineFlags flags
    # -----------------------------------------------------------------------------

    SZ_INITIALIZE_WITH_DEFAULT_CONFIGURATION = 0
    SZ_NO_FLAGS = 0
    SZ_NO_LOGGING = 0
    SZ_VERBOSE_LOGGING = 1
    SZ_WITHOUT_INFO = 0


# -----------------------------------------------------------------------------
# Additional default values
# TODO:  Not sure if these values belong in this file.
# -----------------------------------------------------------------------------

SZ_NO_ATTRIBUTES = ""
SZ_NO_EXCLUSIONS = ""
SZ_NO_REQUIRED_DATASOURCES = ""
SZ_NO_SEARCH_PROFILE = ""
