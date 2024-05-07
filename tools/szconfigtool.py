#! /usr/bin/env python3

import argparse
import cmd
import glob
import json
import os
import re
import subprocess
import sys
import textwrap
import traceback
from collections import OrderedDict
from contextlib import suppress

try:
    import prettytable
except (ImportError, ModuleNotFoundError):
    prettytable = None

# TODO Add back in when consolidated modules into a helper module
# import G2Paths
# from G2IniParams import G2IniParams
# from senzing import G2Config, G2ConfigMgr, SzError
from senzing import szconfig, szconfigmanager
from senzing.szerror import SzError

try:
    import atexit
    import readline
except ImportError:
    readline = None

try:
    from pygments import formatters, highlight, lexers

    pygments_installed = True
except ImportError:
    pygments_installed = False

# ===== supporting classes =====


# ==============================
class Colors:

    @classmethod
    def apply(cls, in_string, color_list=None):
        """apply list of colors to a string"""
        if color_list:
            prefix = "".join(
                [getattr(cls, i.strip().upper()) for i in color_list.split(",")]
            )
            suffix = cls.RESET
            return f"{prefix}{in_string}{suffix}"
        return in_string

    @classmethod
    def set_theme(cls, theme):
        # best for dark backgrounds
        if theme.upper() == "DEFAULT":
            cls.TABLE_TITLE = cls.FG_GREY42
            cls.ROW_TITLE = cls.FG_GREY42
            cls.COLUMN_HEADER = cls.FG_GREY42
            cls.ENTITY_COLOR = cls.FG_MEDIUMORCHID1
            cls.DSRC_COLOR = cls.FG_ORANGERED1
            cls.ATTR_COLOR = cls.FG_CORNFLOWERBLUE
            cls.GOOD = cls.FG_CHARTREUSE3
            cls.BAD = cls.FG_RED3
            cls.CAUTION = cls.FG_GOLD3
            cls.HIGHLIGHT1 = cls.FG_DEEPPINK4
            cls.HIGHLIGHT2 = cls.FG_DEEPSKYBLUE1
        elif theme.upper() == "LIGHT":
            cls.TABLE_TITLE = cls.FG_LIGHTBLACK
            cls.ROW_TITLE = cls.FG_LIGHTBLACK
            cls.COLUMN_HEADER = cls.FG_LIGHTBLACK  # + cls.ITALICS
            cls.ENTITY_COLOR = cls.FG_LIGHTMAGENTA + cls.BOLD
            cls.DSRC_COLOR = cls.FG_LIGHTYELLOW + cls.BOLD
            cls.ATTR_COLOR = cls.FG_LIGHTCYAN + cls.BOLD
            cls.GOOD = cls.FG_LIGHTGREEN
            cls.BAD = cls.FG_LIGHTRED
            cls.CAUTION = cls.FG_LIGHTYELLOW
            cls.HIGHLIGHT1 = cls.FG_LIGHTMAGENTA
            cls.HIGHLIGHT2 = cls.FG_LIGHTCYAN
        elif theme.upper() == "DARK":
            cls.TABLE_TITLE = cls.FG_LIGHTBLACK
            cls.ROW_TITLE = cls.FG_LIGHTBLACK
            cls.COLUMN_HEADER = cls.FG_LIGHTBLACK  # + cls.ITALICS
            cls.ENTITY_COLOR = cls.FG_MAGENTA + cls.BOLD
            cls.DSRC_COLOR = cls.FG_YELLOW + cls.BOLD
            cls.ATTR_COLOR = cls.FG_CYAN + cls.BOLD
            cls.GOOD = cls.FG_GREEN
            cls.BAD = cls.FG_RED
            cls.CAUTION = cls.FG_YELLOW
            cls.HIGHLIGHT1 = cls.FG_MAGENTA
            cls.HIGHLIGHT2 = cls.FG_CYAN

    # styles
    RESET = "\033[0m"
    BOLD = "\033[01m"
    DIM = "\033[02m"
    ITALICS = "\033[03m"
    UNDERLINE = "\033[04m"
    BLINK = "\033[05m"
    REVERSE = "\033[07m"
    STRIKETHROUGH = "\033[09m"
    INVISIBLE = "\033[08m"
    # foregrounds
    FG_BLACK = "\033[30m"
    FG_WHITE = "\033[97m"
    FG_BLUE = "\033[34m"
    FG_MAGENTA = "\033[35m"
    FG_CYAN = "\033[36m"
    FG_YELLOW = "\033[33m"
    FG_GREEN = "\033[32m"
    FG_RED = "\033[31m"
    FG_LIGHTBLACK = "\033[90m"
    FG_LIGHTWHITE = "\033[37m"
    FG_LIGHTBLUE = "\033[94m"
    FG_LIGHTMAGENTA = "\033[95m"
    FG_LIGHTCYAN = "\033[96m"
    FG_LIGHTYELLOW = "\033[93m"
    FG_LIGHTGREEN = "\033[92m"
    FG_LIGHTRED = "\033[91m"
    # backgrounds
    BG_BLACK = "\033[40m"
    BG_WHITE = "\033[107m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_YELLOW = "\033[43m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"
    BG_LIGHTBLACK = "\033[100m"
    BG_LIGHTWHITE = "\033[47m"
    BG_LIGHTBLUE = "\033[104m"
    BG_LIGHTMAGENTA = "\033[105m"
    BG_LIGHTCYAN = "\033[106m"
    BG_LIGHTYELLOW = "\033[103m"
    BG_LIGHTGREEN = "\033[102m"
    BG_LIGHTRED = "\033[101m"
    # extended
    FG_DARKORANGE = "\033[38;5;208m"
    FG_SYSTEMBLUE = "\033[38;5;12m"  # darker
    FG_DODGERBLUE2 = "\033[38;5;27m"  # lighter
    FG_PURPLE = "\033[38;5;93m"
    FG_DARKVIOLET = "\033[38;5;128m"
    FG_MAGENTA3 = "\033[38;5;164m"
    FG_GOLD3 = "\033[38;5;178m"
    FG_YELLOW1 = "\033[38;5;226m"
    FG_SKYBLUE1 = "\033[38;5;117m"
    FG_SKYBLUE2 = "\033[38;5;111m"
    FG_ROYALBLUE1 = "\033[38;5;63m"
    FG_CORNFLOWERBLUE = "\033[38;5;69m"
    FG_HOTPINK = "\033[38;5;206m"
    FG_DEEPPINK4 = "\033[38;5;89m"
    FG_MAGENTA3 = "\033[38;5;164m"
    FG_SALMON = "\033[38;5;209m"
    FG_MEDIUMORCHID1 = "\033[38;5;207m"
    FG_NAVAJOWHITE3 = "\033[38;5;144m"
    FG_DARKGOLDENROD = "\033[38;5;136m"
    FG_STEELBLUE1 = "\033[38;5;81m"
    FG_GREY42 = "\033[38;5;242m"
    FG_INDIANRED = "\033[38;5;131m"
    FG_DEEPSKYBLUE1 = "\033[38;5;39m"
    FG_ORANGE3 = "\033[38;5;172m"
    FG_RED3 = "\033[38;5;124m"
    FG_SEAGREEN2 = "\033[38;5;83m"
    FG_YELLOW3 = "\033[38;5;184m"
    FG_CYAN3 = "\033[38;5;43m"
    FG_CHARTREUSE3 = "\033[38;5;70m"
    FG_ORANGERED1 = "\033[38;5;202m"


def colorize(in_string, color_list="None"):
    return Colors.apply(in_string, color_list)


def colorize_msg(msg_text, msg_type_or_color=""):
    if msg_type_or_color.upper() == "ERROR":
        msg_color = "bad"
    elif msg_type_or_color.upper() == "WARNING":
        msg_color = "caution,italics"
    elif msg_type_or_color.upper() == "INFO":
        msg_color = "highlight2"
    elif msg_type_or_color.upper() == "SUCCESS":
        msg_color = "good"
    else:
        msg_color = msg_type_or_color
    print(f"\n{Colors.apply(msg_text, msg_color)}\n")


def colorize_json(json_str):
    for token in set(re.findall(r'"(.*?)"', json_str)):
        tag = f'"{token}":'
        if tag in json_str:
            json_str = json_str.replace(tag, colorize(tag, "attr_color"))
        else:
            tag = f'"{token}"'
            if tag in json_str:
                json_str = json_str.replace(tag, colorize(tag, "dim"))
    return json_str


# ===== main class =====


class SzCmdShell(cmd.Cmd, object):

    def __init__(self, engine_settings, hist_disable, force_mode, file_to_process):
        cmd.Cmd.__init__(self)

        # Cmd Module settings
        self.intro = ""
        self.prompt = "(szcfg) "
        self.ruler = "-"
        self.doc_header = "Configuration Command List"
        self.misc_header = "Help Topics (help <topic>)"
        self.undoc_header = "Misc Commands"
        self.__hidden_methods = (
            "do_EOF",
            "do_help",
            "do_addStandardizeFunc",
            "do_addExpressionFunc",
            "do_addComparisonFunc",
            "do_addComparisonFuncReturnCode",
            "do_addFeatureComparison",
            "do_deleteFeatureComparison",
            "do_addFeatureComparisonElement",
            "do_deleteFeatureComparisonElement",
            "do_addFeatureDistinctCallElement",
            "do_setFeatureElementDerived",
            "do_setFeatureElementDisplayLevel",
            "do_addEntityScore",
            "do_addToNameSSNLast4hash",
            "do_deleteFromSSNLast4hash",
            "do_updateAttributeAdvanced",
            "do_updateAttributeAdvanced",
            "do_updateFeatureVersion",
        )

        # self.sz_configmgr = G2ConfigMgr()
        # self.sz_config = G2Config()
        self.sz_configmgr = szconfigmanager.SzConfigManager()
        self.sz_config = szconfig.SzConfig()

        # Set flag to know if running an interactive command shell or reading from file
        self.is_interactive = True

        # Config variables and setup
        self.config_updated = False
        self.engine_settings = engine_settings

        # Processing input file
        self.force_mode = force_mode
        self.file_to_process = file_to_process

        self.attribute_class_list = (
            "NAME",
            "ATTRIBUTE",
            "IDENTIFIER",
            "ADDRESS",
            "PHONE",
            "RELATIONSHIP",
            "OTHER",
        )
        self.locked_feature_list = (
            "NAME",
            "ADDRESS",
            "PHONE",
            "DOB",
            "REL_LINK",
            "REL_ANCHOR",
            "REL_POINTER",
        )
        self.valid_behavior_codes = [
            "NAME",
            "A1",
            "A1E",
            "A1ES",
            "F1",
            "F1E",
            "F1ES",
            "FF",
            "FFE",
            "FFES",
            "FM",
            "FME",
            "FMES",
            "FVM",
            "FVME",
            "FVMES",
            "NONE",
        ]

        # TODO Have these changed?
        self.json_attr_types = {
            "ID": "integer",
            "EXECORDER": "integer",
            "DATASOURCE": "string|255",
            "FEATURE": "string|255",
            "ELEMENT": "string|255",
            "ATTRIBUTE": "string|255",
            "FRAGMENT": "string|255",
            "RULE": "string|255",
            "TIER": "integer",
            "RTYPEID": "integer",
            "REF_SCORE": "integer",
            "FUNCTION": "string|255",
            "SECTION": "string|255",
            "FIELD": "string|255",
        }

        # Setup for pretty printing
        Colors.set_theme("DEFAULT")
        # TODO Set this during import
        self.pygments_installed = True if "pygments" in sys.modules else False
        # self.current_output_format = 'table' if prettytable else 'jsonl'
        self.current_output_format_list = "table" if prettytable else "jsonl"
        self.current_output_format_record = "json"

        # Readline and history
        self.readline_available = True if "readline" in sys.modules else False
        self.hist_disable = hist_disable
        self.hist_check()

        self.parser = argparse.ArgumentParser(prog="", add_help=False)
        self.subparsers = self.parser.add_subparsers()

        getConfig_parser = self.subparsers.add_parser(
            "getConfig", usage=argparse.SUPPRESS
        )
        getConfig_parser.add_argument("configID", type=int)

    # ===== custom help section =====

    def do_help(self, help_topic):
        """"""
        if not help_topic:
            self.help_overview()
            return

        if help_topic not in self.get_names(include_hidden=True):
            help_topic = "do_" + help_topic
            if help_topic not in self.get_names(include_hidden=True):
                cmd.Cmd.do_help(self, help_topic[3:])
                return

        topic_docstring = getattr(self, help_topic).__doc__
        if not topic_docstring:
            colorize_msg(f"No help found for {help_topic}", "warning")
            return

        help_text = current_section = ""
        headers = [
            "Syntax:",
            "Examples:",
            "Example:",
            "Notes:",
            "Caution:",
            "Arguments:",
        ]
        help_lines = textwrap.dedent(topic_docstring).split("\n")

        for line in help_lines:
            line_color = ""
            if line:
                if line in headers:
                    line_color = "highlight2"
                    current_section = line

                if current_section == "Caution:":
                    line_color = "caution, italics"
                elif current_section not in (
                    "Syntax:",
                    "Examples:",
                    "Example:",
                    "Notes:",
                    "Arguments:",
                ):
                    line_color = ""

            if re.match(rf"^\s*{help_topic[3:]}", line) and not line_color:
                sep_column = line.find(help_topic[3:]) + len(help_topic[3:])
                help_text += (
                    line[0:sep_column] + colorize(line[sep_column:], "dim") + "\n"
                )
            else:
                help_text += colorize(line, line_color) + "\n"

        print(help_text)

    def help_all(self):
        args = ("",)
        cmd.Cmd.do_help(self, *args)

    def help_overview(self):
        print(
            textwrap.dedent(
                f"""
        {colorize('This utility allows you to configure a Senzing instance.', '')}

        {colorize('Senzing compares records within and across data sources.  Records consist of features and features have attributes.', '')}
        {colorize('For instance, the NAME feature has attributes such as NAME_FIRST and NAME_LAST for a person and NAME_ORG for an', '')}
        {colorize('organization.', '')}

        {colorize('Features are standardized and expressed in various ways to create candidate keys, and when candidates are found all', '')}
        {colorize('of their features are compared to the features of the incoming record to see how close they actually are.', '')}

        {colorize('Finally, a set of rules or "principles" are applied to the feature scores of each candidate to see if the incoming', '')}
        {colorize('record should resolve to an existing entity or become a new one. In either case, the rules are also used to create', '')}
        {colorize('relationships between entities.', '')}

        {colorize('Additional help:', 'highlight2')}
            help basic      {colorize('<- for commonly used commands', 'dim')}
            help features   {colorize('<- to be used only with the guidance of Senzing support', 'dim')}
            help principles {colorize('<- to be used only with the guidance of Senzing support', 'dim')}
            help all        {colorize('<- to show all configuration commands', 'dim')}

        {colorize('To understand more about configuring Senzing, please review:', '')}
            {colorize('https://senzing.com/wp-content/uploads/Entity-Resolution-Processes-021320.pdf', 'highlight1, underline')}
            {colorize('https://senzing.com/wp-content/uploads/Principle-Based-Entity-Resolution-092519.pdf', 'highlight1, underline')}
            {colorize('https://senzing.zendesk.com/hc/en-us/articles/231925448-Generic-Entity-Specification-JSON-CSV-Mapping', 'highlight1, underline')}

        """
            )
        )

    def help_basic(self):
        print(
            textwrap.dedent(
                f"""
        {colorize('Senzing comes pre-configured with all the settings needed to resolve persons and organizations.  Usually all that is required', '')}
        {colorize('is for you to register your data sources and start loading data based on the Generic Entity Specification.', '')}

        {colorize('Data source commands:', 'highlight2')}
            addDataSource           {colorize('<- to register a new data source', 'dim')}
            deleteDataSource        {colorize('<- to remove a data source created by error', 'dim')}
            listDataSources         {colorize('<- to see all the registered data sources', 'dim')}

        {colorize('When you see a how or a why screen output in Senzing, you see the actual entity counts and scores of a match. The list functions', 'dim,italics')}
        {colorize('below show you what those thresholds and scores are currently configured to.', 'dim,italics')}

        {colorize('Features and attribute settings:', 'highlight2')}
            listFeatures            {colorize('<- to see all features, whether they are used for candidates, and how they are scored', 'dim')}
            listAttributes          {colorize('<- to see all the attributes you can map to', 'dim')}

        {colorize('Principles (rules, scores, and thresholds):', 'highlight2')}
            listFunctions           {colorize('<- to see all the standardize, expression and comparison functions possible', 'dim')}
            listGenericThresholds   {colorize('<- to see all the thresholds for when feature values go generic for candidates or scoring', 'dim')}
            listRules               {colorize('<- to see all the principles in the order they are evaluated', 'dim')}
            listFragments           {colorize('<- to see all the fragments of rules are configured, such as what is considered close_name', 'dim')}

        {colorize('CAUTION:', 'caution, italics')}
            {colorize('While adding or updating features, expressions, scoring thresholds and rules are discouraged without the guidance of Senzing support,', 'caution, italics')}
            {colorize('knowing how they are configured and what their thresholds are can help you understand why records resolved or not, leading to the', 'caution, italics')}
            {colorize('proper course of action when working with Senzing Support.', 'caution, italics')}

        """
            )
        )

    def help_features(self):
        print(
            textwrap.dedent(
                f"""
        {colorize('New features and their attributes are rarely needed.  But when they are they are usually industry specific', '')}
        {colorize('identifiers (F1s) like medicare_provider_id init_enginesor swift_code for a bank.  If you want some other kind of attribute like a grouping (FF)', '')}
        {colorize('or a physical attribute (FME, FMES), it is best to clone an existing feature by doing a getFeature, then modifying the json payload to', '')}
        {colorize('use it in an addFeature.', '')}

        {colorize('Commands to add or update features:', 'highlight2')}
            listFeatures            {colorize('<- to list all the features in the system', 'dim')}
            getFeature              {colorize('<- get the json configuration for an existing feature', 'dim')}
            addFeature              {colorize('<- add a new feature from a json configuration', 'dim')}
            setFeature              {colorize('<- to change a setting on an existing feature', 'dim')}
            deleteFeature           {colorize('<- to delete a feature added by mistake', 'dim')}

        {colorize('Attributes are what you map your source data to.  If you add a new feature, you will also need to add attributes for it. Be sure to', '')}
        {colorize('use a unique ID for attributes and to classify them as either an ATTRIBUTE or an IDENTIFIER.', '')}

        {colorize('Commands to add or update attributes:', 'highlight2')}
            listAttributes          {colorize('<- to see all the attributes you can map to', 'dim')}
            getAttribute            {colorize('<- get the json configuration for an existing attribute', 'dim')}
            addAttribute            {colorize('<- add a new attribute from a json configuration', 'dim')}
            deleteAttribute         {colorize('<- to delete an attribute added by mistake', 'dim')}

        {colorize('Some templates have been created to help you add new identifiers if needed. A template adds a feature and its required', '')}
        {colorize('attributes with one command.', '')}

        {colorize('Commands for using templates:', 'highlight2')}
            templateAdd             {colorize('<- add an identifier (F1) feature and attributes based on a template', 'dim')}
            templateAdd list        {colorize('<- to see the list of available templates', 'dim')}
        """
            )
        )

    def help_principles(self):
        print(
            textwrap.dedent(
                f"""
        {colorize('Before the principles are applied, the features and expressions created for an incoming record are used to find candidates.', '')}
        {colorize('An example of an expression is name and DOB and there is an expression call on the feature "name" to automatically create it', '')}
        {colorize('if both a name and DOB are present on the incoming record.  Features and expressions used for candidates are also referred', '')}
        {colorize('to as candidate builders or candidate keys.', '')}

        {colorize('Commands that help with configuring candidate keys:', 'highlight2')}
            listFeatures            {colorize('<- to see what features are used for candidates', 'dim')}
            setFeature              {colorize('<- to toggle whether or not a feature is used for candidates', 'dim')}
            listExpressionCalls     {colorize('<- to see what expressions are currently being created', 'dim')}
            addToNamehash           {colorize('<- to add an element from another feature to the list of composite name keys', 'dim')}
            addExpressionCall       {colorize('<- to add a new expression call, aka candidate key', 'dim')}
            listGenericThresholds   {colorize('<- to see when candidate keys will become generic and are no longer used to find candidates', 'dim')}
            setGenericThreshold     {colorize('<- to change when features with certain behaviors become generic', 'dim')}

        {colorize('CAUTION:', 'caution, italics')}
            {colorize('The cost of raising generic thresholds is speed. It is always best to keep generic thresholds low and to add new', 'caution, italics')}
            {colorize('new expressions instead.  You can extend composite key expressions with the addToNameHash command above, or add ', 'caution, italics')}
            {colorize('new expressions by using the addExpressionCall command above.', 'caution, italics')}

        {colorize('Once the candidate matches have been found, scoring and rule evaluation takes place.  Scores are rolled up by behavior.', '')}
        {colorize('For instance, both addresses and phones have the behavior FF (Frequency Few). If they both score above their scoring', '')}
        {colorize('function''s close threshold, there would be two CLOSE_FFs (a fragment) which can be used in a rule such as NAME+CLOSE_FF.', '')}

        {colorize('Commands that help with configuring principles (rules) and scoring:', 'highlight2')}
            listRules               {colorize('<- these are the principles that are applied top down', 'dim')}
            listFragments           {colorize('<- rules are combinations of fragments like close_name or same_name', 'dim')}
            listFunctions           {colorize('<- the comparison functions show you what is considered same, close, likely, etc.', 'dim')}
            setRule                 {colorize('<- to change whether an existing rule resolves or relates', 'dim')}
        """
            )
        )

    def help_support(self):
        print(
            textwrap.dedent(
                f"""
        {colorize('Senzing Knowledge Center:', 'dim')} {colorize('https://senzing.zendesk.com/hc/en-us', 'highlight1,underline')}

        {colorize('Senzing Support Request:', 'dim')} {colorize('https://senzing.zendesk.com/hc/en-us/requests/new', 'highlight1,underline')}
        """
            )
        )

    # ===== Auto completion section =====

    def get_names(self, include_hidden=False):
        """Override base method to return methods for autocomplete and help"""
        if not include_hidden:
            return [n for n in dir(self.__class__) if n not in self.__hidden_methods]
        return list(dir(self.__class__))

    def completenames(self, text, *ignored):
        """Override function from cmd module to make command completion case insensitive"""
        dotext = "do_" + text
        return [a[3:] for a in self.get_names() if a.lower().startswith(dotext.lower())]

    def complete_exportToFile(self, text, line, begidx, endidx):
        if re.match("exportToFile +", line):
            return self.pathCompletes(text, line, begidx, endidx, "exportToFile")

    def complete_importFromFile(self, text, line, begidx, endidx):
        if re.match("importFromFile +", line):
            return self.pathCompletes(text, line, begidx, endidx, "importFromFile")

    def pathCompletes(self, text, line, begidx, endidx, callingcmd):
        """Auto complete paths for commands that have a complete_ function"""

        completes = []

        pathComp = line[len(callingcmd) + 1 : endidx]
        fixed = line[len(callingcmd) + 1 : begidx]

        for path in glob.glob(f"{pathComp}*"):
            path = (
                path + os.sep
                if path and os.path.isdir(path) and path[-1] != os.sep
                else path
            )
            completes.append(path.replace(fixed, "", 1))

        return completes

    def complete_getAttribute(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_ATTR", "ATTR_CODE", text)

    def complete_getFeature(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_FTYPE", "FTYPE_CODE", text)

    def complete_getElement(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_FELEM", "FELEM_CODE", text)

    def complete_getFragment(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_ERFRAG", "ERFRAG_CODE", text)

    def complete_getRule(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_ERRULE", "ERRULE_CODE", text)

    def complete_deleteAttribute(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_ATTR", "ATTR_CODE", text)

    def complete_deleteDataSource(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_DSRC", "DSRC_CODE", text)

    def complete_deleteElement(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_FELEM", "FELEM_CODE", text)

    def complete_deleteEntityType(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_ETYPE", "ETYPE_CODE", text)

    def complete_deleteFeature(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_FTYPE", "FTYPE_CODE", text)

    def complete_deleteFeatureComparison(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_FTYPE", "FTYPE_CODE", text)

    def complete_deleteFeatureDistinctCall(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_FTYPE", "FTYPE_CODE", text)

    def complete_deleteFragment(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_ERFRAG", "ERFRAG_CODE", text)

    def complete_deleteRule(self, text, line, begidx, endidx):
        return self.codes_completes("CFG_ERRULE", "ERRULE_CODE", text)

    def codes_completes(self, table, field, arg):
        # Build list each time to have latest even after an add*, delete*
        return [
            code
            for code in self.get_recordCodes(table, field)
            if code.lower().startswith(arg.lower())
        ]

    def get_recordCodes(self, table, field):
        code_list = []
        for i in range(len(self.config_data["G2_CONFIG"][table])):
            code_list.append(self.config_data["G2_CONFIG"][table][i][field])
        return code_list

    def complete_getConfigSection(self, text, line, begidx, endidx):
        return [
            section
            for section in self.config_data["G2_CONFIG"].keys()
            if section.lower().startswith(text.lower())
        ]

    # ===== command history section =====

    def hist_check(self):

        self.histFileName = None
        self.histFileError = None
        self.histAvail = False

        if not self.hist_disable:

            if readline:
                tmpHist = "." + os.path.basename(
                    sys.argv[0].lower().replace(".py", "_history")
                )
                self.histFileName = os.path.join(os.path.expanduser("~"), tmpHist)

                # Try and open history in users home first for longevity
                try:
                    open(self.histFileName, "a").close()
                except IOError as e:
                    self.histFileError = f"{e} - Couldn't use home, trying /tmp/..."

                # Can't use users home, try using /tmp/ for history useful at least in the session
                if self.histFileError:

                    self.histFileName = f"/tmp/{tmpHist}"
                    try:
                        open(self.histFileName, "a").close()
                    except IOError as e:
                        self.histFileError = f"{e} - User home dir and /tmp/ failed"
                        return

                hist_size = 2000
                readline.read_history_file(self.histFileName)
                readline.set_history_length(hist_size)
                atexit.register(readline.set_history_length, hist_size)
                atexit.register(readline.write_history_file, self.histFileName)

                self.histFileName = self.histFileName
                self.histFileError = None
                self.histAvail = True

    def do_histDedupe(self, arg):
        """
        Deduplicates the command history

        Syntax:
            histDedupe
        """
        if self.histAvail:
            if (
                input(
                    "\nAre you sure you want to de-duplicate the session history? (y/n) "
                )
                .upper()
                .startwith("Y")
            ):

                with open(self.histFileName) as hf:
                    linesIn = (line.rstrip() for line in hf)
                    uniqLines = OrderedDict.fromkeys(line for line in linesIn if line)

                    readline.clear_history()
                    for ul in uniqLines:
                        readline.add_history(ul)

                colorize_msg(
                    "Session history and history file both deduplicated", "success"
                )
            else:
                print()
        else:
            colorize_msg("History is not available in this session", "warning")

    def do_histClear(self, arg):
        """
        Clears the command history

        Syntax:
            histClear
        """
        if self.histAvail:
            if (
                input("\nAre you sure you want to clear the session history? (y/n) ")
                .upper()
                .startwith("Y")
            ):
                readline.clear_history()
                readline.write_history_file(self.histFileName)
                colorize_msg("Session history and history file both cleared", "success")
            else:
                print()
        else:
            colorize_msg("History is not available in this session", "warning")

    def do_history(self, arg):
        """
        Displays the command history

        Syntax:
            history
        """
        if self.histAvail:
            print()
            for i in range(readline.get_current_history_length()):
                print(readline.get_history_item(i + 1))
            print()
        else:
            colorize_msg("History is not available in this session.", "warning")

    # ===== command loop section =====

    # def init_engines(self, init_msg=False):
    def init_engines(self):

        # if init_msg:
        #     colorize_msg('Initializing Senzing engines ...')

        try:
            # TODO Change instance name in all tools
            self.sz_configmgr.initialize("szG2ConfigMgr", self.engine_settings)
            self.sz_config.initialize("szG2Config", self.engine_settings)
        # TODO Change all ex to err
        except SzError as err:
            colorize_msg(err, "error")
            self.destroy_engines()
            sys.exit(1)

        # Re-read config after a save
        if self.config_updated:
            self.load_config()

    def destroy_engines(self):
        with suppress(Exception):
            self.sz_configmgr.destroy()
            self.sz_config.destroy()

    def load_config(self, default_config_id=None):
        # Get the current configuration from the Senzing database
        if not default_config_id:
            # default_config_id = bytearray()
            # self.sz_configmgr.getDefaultConfigID(default_config_id)
            default_config_id = self.sz_configmgr.get_default_config_id()

        # TODO Why is this being tested twice?
        # If a default config isn't found, create a new default configuration
        if not default_config_id:
            colorize_msg("Adding default config to new database", "warning")
            config_handle = self.sz_config.create_config()
            # config_default = bytearray()
            # self.sz_config.save(config_handle, config_default)
            default_config = self.sz_config.export_config(config_handle)
            # config_string = config_default.decode()

            # Persist new default config to Senzing Repository
            try:
                # addconfig_id = bytearray()
                # self.sz_configmgr.addConfig(config_string, 'New default configuration added by G2ConfigTool.',
                # addconfig_id)
                config_id = self.sz_configmgr.add_config(
                    default_config, "New default configuration added by G2ConfigTool."
                )
                # self.sz_configmgr.setDefaultConfigID(addconfig_id)
                self.sz_configmgr.set_default_config_id(config_id)
            except SzError:
                # TODO How do this look with SzError json string?
                raise

            colorize_msg("Default config added!", "success")
            self.destroy_engines()
            # self.init_engines(init_msg=(True if self.is_interactive else False))
            self.init_engines()
            # default_config_id = bytearray()
            # self.sz_configmgr.getDefaultConfigID(default_config_id)
            default_config_id = self.sz_configmgr.get_default_config_id()

        # config_current = bytearray()
        # self.sz_configmgr.getConfig(default_config_id, config_current)
        current_config = self.sz_configmgr.get_config(default_config_id)
        # self.config_data = json.loads(config_current.decode())
        self.config_data = json.loads(current_config)
        self.config_updated = False

    def preloop(self):
        self.init_engines()
        self.load_config()
        colorize_msg(
            "Welcome to the Senzing configuration tool. Type help or ? for help",
            "highlight2",
        )

    def cmdloop(self):
        while True:
            try:
                cmd.Cmd.cmdloop(self)
                break
            except KeyboardInterrupt:
                if self.config_updated:
                    if (
                        input(
                            "\n\nThere are unsaved changes, would you like to save first? (y/n) "
                        )
                        .upper()
                        .startswith("Y")
                    ):
                        self.do_save(self)
                        break
                if (
                    input("\nAre you sure you want to exit? (y/n) ")
                    .upper()
                    .startswith("Y")
                ):
                    break
                else:
                    print()
            except TypeError as err:
                colorize_msg(err, "error")
                type_, value_, traceback_ = sys.exc_info()
                for item in traceback.format_tb(traceback_):
                    print(item)

    def postloop(self):
        self.destroy_engines()

    def emptyline(self):
        return

    def default(self, line):
        # TODO szcommand uses self.print_error
        colorize_msg("Unknown command, type help or ?", "warning")
        return

    def fileloop(self):
        # Get initial config
        # self.init_engines(init_msg=False)
        self.init_engines()
        self.load_config()

        # Set flag to know running an interactive command shell or not
        self.is_interactive = False
        save_detected = False

        with open(self.file_to_process) as data_in:
            for line in data_in:
                line = line.strip()
                if len(line) > 0 and line[0:1] not in ("#", "-", "/"):
                    # *args allows for empty list if there are no args
                    (read_cmd, *args) = line.split()
                    process_cmd = f"do_{read_cmd}"
                    print(colorize(f"----- {read_cmd} -----", "dim"))
                    print(line)

                    if process_cmd == "do_save" and not save_detected:
                        save_detected = True

                    if process_cmd not in dir(self):
                        colorize_msg(f"Command {read_cmd} not found", "error")
                    else:
                        exec_cmd = f"self.{process_cmd}('{' '.join(args)}')"
                        exec(exec_cmd)

                    if not self.force_mode:
                        if (
                            input("\nPress enter to continue or (Q)uit... ")
                            .upper()
                            .startswith("Q")
                        ):
                            break

        if not save_detected and self.config_updated:
            if not self.force_mode:
                if (
                    input(
                        "\nNo save command was issued would you like to save now? (y/n) "
                    )
                    .upper()
                    .startswith("Y")
                ):
                    self.do_save(self)
                    print()
                    return

            colorize_msg("Configuration changes were not saved!", "warning")

    def do_quit(self, arg):
        if self.config_updated:
            if (
                input(
                    "\nThere are unsaved changes, would you like to save first? (y/n) "
                )
                .upper()
                .startswith("Y")
            ):
                self.do_save(self)
            else:
                colorize_msg("Configuration changes were not saved!", "warning")
        # print()
        return True

    def do_exit(self, arg):
        self.do_quit(self)
        return True

    def do_save(self, args):
        if self.config_updated:
            # If not accepting file commands without prompts and not using older style config file
            if not self.force_mode:
                if (
                    not input(
                        "\nAre you certain you wish to proceed and save changes? (y/n) "
                    )
                    .upper()
                    .startswith("Y")
                ):
                    colorize_msg("Configuration changes have not been saved", "warning")
                    return

            try:
                # new_config_id = bytearray()
                # self.sz_configmgr.addConfig(
                #     json.dumps(self.config_data), "Updated by G2ConfigTool", new_config_id
                # )
                new_config_id = self.sz_configmgr.add_config(
                    json.dumps(self.config_data), "Updated by G2ConfigTool"
                )
                self.sz_configmgr.set_default_config_id(new_config_id)
            except SzError as err:
                # TODO szcommand print_error
                colorize_msg(err, "error")
            else:
                colorize_msg("Configuration changes saved!", "success")
                # Reinit engines to pick up changes. This is good practice and will be needed when rewritten to fully use cfg APIs
                # Don't display init msg if not interactive (fileloop)
                if sys._getframe().f_back.f_code.co_name == "onecmd":
                    self.destroy_engines()
                    # self.init_engines(init_msg=(True if self.is_interactive else False))
                    self.init_engines()
                    self.config_updated = False

        else:
            colorize_msg("There were no changes to save", "warning")

    # TODO Showing up in commands
    def do_shell(self, line):
        output = os.popen(line).read()
        print(f"\n{output}\n")

    # ===== json configuration file section =====

    def do_getDefaultConfigID(self, arg):
        """
        Returns the current configuration ID

        Syntax:
            getDefaultConfigID
        """
        # response = bytearray()
        try:
            config_id = self.sz_configmgr.get_default_config_id()
            colorize_msg(config_id, "success")
        except SzError as err:
            colorize_msg(err, "error")

    def do_getConfigList(self, arg):
        """
        Returns the list of all known configurations

        Syntax:
            getConfigList [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        try:
            # response = bytearray()
            config_list = self.sz_configmgr.get_config_list()
            self.print_json_record(json.loads(config_list)["CONFIGS"])
        except SzError as err:
            colorize_msg(err, "error")

    def do_reload_config(self, arg):
        """
        Reload the configuration, abandoning any changes

        Syntax:
            configReload
        """
        if self.config_updated:
            if (
                not input(
                    "\nYou have unsaved changes, are you sure you want to discard them? (y/n) "
                )
                .upper()
                .startswith("Y")
            ):
                colorize_msg("Your changes have not been overwritten", "info")
                return
            self.load_config()
            self.config_updated = False
            colorize_msg("Config has been reloaded", "success")
        else:
            colorize_msg("Config has not been updated", "warning")

    def do_exportToFile(self, arg):
        """
        Export the current configuration data to a file

        Examples:
            exportToFile [fileName] [optional_config_id]

        Notes:
            You can export any prior config_id from the getConfigList command by specifying it after the fileName
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        arg_list = arg.split()
        fileName = arg_list[0]

        if len(arg_list) == 1:
            json_data = self.config_data
        else:
            config_id = arg_list[1]
            try:
                response = bytearray()
                self.sz_configmgr.getConfig(config_id, response)
                json_data = json.loads(response.decode())
            except SzError as err:
                colorize_msg(err, "error")
                return
        try:
            with open(fileName, "w") as fp:
                json.dump(json_data, fp, indent=4, sort_keys=True)
        except OSError as err:
            colorize_msg(err, "error")
        else:
            colorize_msg("Successfully exported!", "success")

    def do_importFromFile(self, arg):
        """
        Import the config from a file

        Examples:
            importFromFile [fileName]
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        if self.config_updated:
            if (
                not input(
                    "\nYou have unsaved changes, are you sure you want to discard them? (y/n) "
                )
                .upper()
                .startswith("Y")
            ):
                return
        try:
            self.config_data = json.load(open(arg, encoding="utf-8"))
        except ValueError as err:
            colorize_msg(err, "error")
        else:
            self.config_updated = True
            colorize_msg("Successfully imported!", "success")

    # ===== settings section =====

    def do_setTheme(self, arg):
        """
        Switch terminal ANSI colors between default, light and dark

        Syntax:
            setTheme {default|light|dark}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        theme = arg.upper()
        theme, message = self.validateDomain(
            "Theme", theme, ["DEFAULT", "DARK", "LIGHT"]
        )
        if not theme:
            colorize_msg(message, "error")
            return

        Colors.set_theme(theme)

    def check_arg_for_output_format(self, output_type, arg):

        if not arg:
            return arg
        new_arg = []
        for token in arg.split():
            if token.lower() == "table" and not prettytable:
                colorize_msg(
                    "\nOutput to table ignored as prettytable not installed (pip3 install prettytable)\n",
                    "warning",
                )
                arg = arg.replace(token, "")
            elif token.lower() in ("table", "json", "jsonl"):
                if output_type == "list":
                    self.current_output_format_list = token.lower()
                else:
                    self.current_output_format_record = token.lower()
                arg = arg.replace(token, "")
            else:
                new_arg.append(token)
        return " ".join(new_arg)

    # ===== code lookups and validations =====

    def get_record(self, table, field, value):
        # turn even single values into list to simplify code
        if not isinstance(field, list):
            field = [field]
            value = [value]

        recordList = []
        for record in self.config_data["G2_CONFIG"][table]:
            matched = True
            for i in range(len(field)):
                if record[field[i]] != value[i]:
                    matched = False
                    break
            if matched:
                recordList.append(record)
        if recordList:
            if len(recordList) > 1:
                colorize_msg(
                    f"get_record call for {table}, {field},{value} returned multiple rows!",
                    "warning",
                )
                for record in recordList:
                    print(record)
                print()
            return recordList[0]
        return None

    def get_record_list(self, table, field=None, value=None):
        recordList = []
        for record in self.config_data["G2_CONFIG"][table]:
            if field and value:
                if record[field] == value:
                    recordList.append(record)
            else:
                recordList.append(record)
        return recordList

    def getDesiredValueOrNext(self, table, field, value, **kwargs):

        # turn even single values into list to simplify code
        # be sure to make last item in list the ID or order to be tested/incremented!
        if isinstance(field, list):
            if len(field) > 1:
                senior_field = field[0:-1]
                senior_value = value[0:-1]
            field = field[-1]
            value = value[-1]
        else:
            senior_field = []
            senior_value = []

        desired_id = value
        id_taken = False
        last_id = kwargs.get("seed_order", 0)
        for record in self.config_data["G2_CONFIG"][table]:
            senior_key_match = True
            for i in range(len(senior_field)):
                if record[senior_field[i]] != senior_value[i]:
                    senior_key_match = False
                    break
            if senior_key_match:
                matched = record[field] == value
                if matched:
                    id_taken = True
                if record[field] > last_id:
                    last_id = record[field]
        return desired_id if desired_id > 0 and not id_taken else last_id + 1

    def lookupDatasource(self, dataSource):
        dsrc_record = self.get_record("CFG_DSRC", "DSRC_CODE", dataSource)
        if dsrc_record:
            return dsrc_record, f'Data source "{dataSource}" already exists'
        return None, f'Data source "{dataSource}" not found'

    def lookupFeature(self, feature):
        ftype_record = self.get_record("CFG_FTYPE", "FTYPE_CODE", feature)
        if ftype_record:
            return ftype_record, f'Feature "{feature}" already exists'
        return None, f'Feature "{feature}" not found'

    def lookupElement(self, element):
        felem_record = self.get_record("CFG_FELEM", "FELEM_CODE", element)
        if felem_record:
            return felem_record, f'Element "{element}" already exists'
        return None, f'Element "{element}" not found'

    def lookupFeatureElement(self, feature, element):
        ftype_record, error_text = self.lookupFeature(feature)
        if not ftype_record:
            return None, error_text
        else:
            felem_record = self.get_record("CFG_FELEM", "FELEM_CODE", element)
            if felem_record:
                fbom_record = self.get_record(
                    "CFG_FBOM",
                    ["FTYPE_ID", "FELEM_ID"],
                    [ftype_record["FTYPE_ID"], felem_record["FELEM_ID"]],
                )
                if fbom_record:
                    return (
                        fbom_record,
                        f'"{element}" is already an element of feature "{feature}"',
                    )
            return (
                None,
                f'{element} is not an element of {feature} (use command "getFeature {feature}" to see its elements)',
            )

    def lookupFeatureClass(self, featureClass):
        fclass_record = self.get_record("CFG_FCLASS", "FCLASS_CODE", featureClass)
        if fclass_record:
            return fclass_record, f'Feature class "{featureClass}" exists"'
        else:
            return (
                False,
                f'Feature class "{featureClass}" not found (use command "listReferenceCodes featureClass" to see the list)',
            )

    def lookupBehaviorCode(self, behaviorCode):
        if behaviorCode in self.valid_behavior_codes:
            return (
                parseFeatureBehavior(behaviorCode),
                f'Behavior code "{behaviorCode}" exists"',
            )
        else:
            return (
                False,
                f'Behavior code "{behaviorCode}" not found (use command "listReferenceCodes behaviorCodes" to see the list)',
            )

    def lookupStandardizeFunction(self, standardizeFunction):
        func_record = self.get_record("CFG_SFUNC", "SFUNC_CODE", standardizeFunction)
        if func_record:
            return func_record, f'Standardize function "{standardizeFunction}" exists"'
        else:
            return (
                False,
                f'Standardize function "{standardizeFunction}" not found (use command "listStandardizeFunctions" to see the list)',
            )

    def lookupExpressionFunction(self, expressionFunction):
        func_record = self.get_record("CFG_EFUNC", "EFUNC_CODE", expressionFunction)
        if func_record:
            return func_record, f'Expression function "{expressionFunction}" exists"'
        else:
            return (
                False,
                f'Expression function "{expressionFunction}" not found (use command "listExpressionFunctions" to see the list)',
            )

    def lookupComparisonFunction(self, comparisonFunction):
        func_record = self.get_record("CFG_CFUNC", "CFUNC_CODE", comparisonFunction)
        if func_record:
            return func_record, f'Comparison function "{comparisonFunction}" exists"'
        else:
            return (
                False,
                f'Comparison function "{comparisonFunction}" not found (use command "listComparisonFunctions" to see the list)',
            )

    def lookupDistinctFunction(self, distinctFunction):
        func_record = self.get_record("CFG_DFUNC", "DFUNC_CODE", distinctFunction)
        if func_record:
            return func_record, f'Distinct function "{distinctFunction}" exists"'
        else:
            return (
                False,
                f'Distinct function "{distinctFunction}" not found (use command "listDistinctFunctions" to see the list)',
            )

    def validateDomain(self, attr, value, domain_list):
        if not value:
            return domain_list[0], f"{attr} defaulted to {domain_list[0]}"
        if value in domain_list:
            return value, f"{attr} value is valid!"
        else:
            return False, f"{attr} value must be in {json.dumps(domain_list)}"

    def lookupAttribute(self, attribute):
        attr_record = self.get_record("CFG_ATTR", "ATTR_CODE", attribute)
        if attr_record:
            return attr_record, f'Attribute "{attribute}" already exists!'
        return None, f'Attribute "{attribute}" not found!'

    def lookupFragment(self, lookup_value):
        if isinstance(lookup_value, int):
            erfragRecord = self.get_record("CFG_ERFRAG", "ERFRAG_ID", lookup_value)
        else:
            erfragRecord = self.get_record("CFG_ERFRAG", "ERFRAG_CODE", lookup_value)
        if erfragRecord:
            return erfragRecord, f'Fragment "{lookup_value}" already exists!'
        return None, f'Fragment "{lookup_value}" not found!'

    def lookupRule(self, lookup_value):
        if isinstance(lookup_value, int):
            errule_record = self.get_record("CFG_ERRULE", "ERRULE_ID", lookup_value)
        else:
            errule_record = self.get_record("CFG_ERRULE", "ERRULE_CODE", lookup_value)
        if errule_record:
            return errule_record, f"Rule {lookup_value} already exists!"
        return None, f"Rule {lookup_value} not found!"

    def lookupGenericPlan(self, plan):
        gplan_record = self.get_record("CFG_GPLAN", "GPLAN_CODE", plan)
        if gplan_record:
            return gplan_record, f'Plan "{plan}" already exists'
        return None, f'Plan "{plan}" not found'

    def validate_parms(self, parm_dict, required_list):
        for attr_name in parm_dict:
            attr_value = parm_dict[attr_name]
            if attr_value and self.json_attr_types.get(attr_name):
                data_type = self.json_attr_types.get(attr_name).split("|")[0]
                max_width = (
                    int(self.json_attr_types.get(attr_name).split("|")[1])
                    if "|" in self.json_attr_types.get(attr_name)
                    else 0
                )
                if data_type == "integer":
                    if not isinstance(attr_value, int):
                        if attr_value.isdigit():
                            parm_dict[attr_name] = int(parm_dict[attr_name])
                        else:
                            raise ValueError(f"{attr_name} must be an integer")
                else:
                    if not isinstance(attr_value, str):
                        raise ValueError(f"{attr_name} must be a string")
                    if max_width and len(attr_value) > max_width:
                        raise ValueError(
                            f"{attr_name} must be less than {max_width} characters"
                        )

        missing_list = []
        for attr in required_list:
            if attr not in parm_dict:
                missing_list.append(attr)
        if missing_list:
            raise ValueError(
                f"{', '.join(missing_list)} {'is' if len(missing_list) == 1 else 'are'} required"
            )

    def settable_parms(self, old_parm_data, set_parm_data, settable_parm_list):
        new_parm_data = dict(old_parm_data)
        errors = []
        update_cnt = 0
        for parm in set_parm_data:
            if parm not in old_parm_data:
                errors.append(f"{parm} is not valid for this record")
            elif set_parm_data[parm] != new_parm_data[parm]:
                if parm.upper() not in settable_parm_list:
                    errors.append(f"{parm} cannot be changed here")
                else:
                    new_parm_data[parm] = set_parm_data[parm]
                    update_cnt += 1
        new_parm_data["update_cnt"] = update_cnt
        if errors:
            new_parm_data["errors"] = (
                "The following errors were detected:\n- " + "\n- ".join(errors)
            )
        return new_parm_data

    def id_or_code_parm(self, arg_str, int_tag, str_tag, int_field, str_field):
        if arg_str.startswith("{"):
            json_parm = dict_keys_upper(json.loads(arg_str))
        elif arg_str.isdigit():
            json_parm = {int_tag: arg_str}
        else:
            json_parm = {str_tag: arg_str}

        if json_parm.get(int_tag):
            return int(json_parm.get(int_tag)), int_field
        if json_parm.get(str_tag):
            return json_parm.get(str_tag).upper(), str_field

        raise ValueError(f"Either {int_tag} or {str_tag} must be provided")

    def update_if_different(
        self, target_record, target_counter, target_field, new_value
    ):
        if target_record[target_field] != new_value:
            target_record[target_field] = new_value
            return target_record, target_counter + 1
        return target_record, target_counter

    # ===== data Source commands =====

    def do_addDataSource(self, arg):
        """
        Register a new data source

        Syntax:
            addDataSource dataSourceCode

        Examples:
            addDataSource CUSTOMER

        Caution:
            dataSource codes will automatically be converted to upper case
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = (
                dict_keys_upper(json.loads(arg))
                if arg.startswith("{")
                else {"DATASOURCE": arg}
            )
            self.validate_parms(parm_data, ["DATASOURCE"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["DATASOURCE"] = parm_data["DATASOURCE"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        dsrc_record, message = self.lookupDatasource(parm_data["DATASOURCE"])
        if dsrc_record:
            colorize_msg(message, "warning")
            return

        next_id = self.getDesiredValueOrNext(
            "CFG_DSRC", "DSRC_ID", parm_data.get("ID"), seed_order=1000
        )
        if parm_data.get("ID") and next_id != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return
        else:
            parm_data["ID"] = next_id

        parm_data["RETENTIONLEVEL"], message = self.validateDomain(
            "Retention level",
            parm_data.get("RETENTIONLEVEL", "Remember"),
            ["Remember", "Forget"],
        )
        if not parm_data["RETENTIONLEVEL"]:
            colorize_msg(message, "error")
            return

        parm_data["CONVERSATIONAL"], message = self.validateDomain(
            "Coversational", parm_data.get("CONVERSATIONAL", "No"), ["Yes", "No"]
        )
        if not parm_data["CONVERSATIONAL"]:
            colorize_msg(message, "error")
            return

        newRecord = {}
        newRecord["DSRC_ID"] = parm_data["ID"]
        newRecord["DSRC_CODE"] = parm_data["DATASOURCE"]
        newRecord["DSRC_DESC"] = parm_data["DATASOURCE"]
        newRecord["DSRC_RELY"] = parm_data.get("RELIABILITY", 1)
        newRecord["RETENTION_LEVEL"] = parm_data["RETENTIONLEVEL"]
        newRecord["CONVERSATIONAL"] = parm_data["CONVERSATIONAL"]
        self.config_data["G2_CONFIG"]["CFG_DSRC"].append(newRecord)
        self.config_updated = True
        colorize_msg("Data source successfully added!", "success")

    def do_listDataSources(self, arg):
        """
        Returns the list of registered data sources

        Syntax:
            listDataSources [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for dsrc_record in sorted(
            self.get_record_list("CFG_DSRC"), key=lambda k: k["DSRC_ID"]
        ):
            if arg and arg.lower() not in str(dsrc_record).lower():
                continue
            json_lines.append(
                {"id": dsrc_record["DSRC_ID"], "dataSource": dsrc_record["DSRC_CODE"]}
            )

        self.print_json_lines(json_lines)

    # TODO auto complete doesn't work if there is a - in dsrc
    def do_deleteDataSource(self, arg):
        """
        Delete an existing data source

        Syntax:
            deleteDataSource [code or id]

        Caution:
            Deleting a data source does not delete its data and you will be prevented from saving if it has data loaded!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "DATASOURCE", "DSRC_ID", "DSRC_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        dsrc_record = self.get_record("CFG_DSRC", search_field, search_value)
        if not dsrc_record:
            colorize_msg("Data source not found", "warning")
            return
        if dsrc_record["DSRC_ID"] <= 2:
            colorize_msg(
                f"The {dsrc_record['DSRC_CODE']} data source cannot be deleted", "error"
            )
            return

        self.config_data["G2_CONFIG"]["CFG_DSRC"].remove(dsrc_record)
        colorize_msg("Data source successfully deleted!", "success")
        self.config_updated = True

    # ===== feature commands =====

    def format_feature_json(self, ftype_record):

        fclass_record = self.get_record(
            "CFG_FCLASS", "FCLASS_ID", ftype_record["FCLASS_ID"]
        )

        sfcall_record_list = self.get_record_list(
            "CFG_SFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        )
        efcall_record_list = self.get_record_list(
            "CFG_EFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        )
        cfcall_record_list = self.get_record_list(
            "CFG_CFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        )
        dfcall_record_list = self.get_record_list(
            "CFG_DFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        )

        # while rare, there can be multiple comparison, the first one can be added with the feature,
        #    the second must be added with addStandardizeCall, addExpressionCall, addComparisonCall
        sfcall_record = (
            sorted(sfcall_record_list, key=lambda k: k["EXEC_ORDER"])[0]
            if sfcall_record_list
            else {}
        )
        efcall_record = (
            sorted(efcall_record_list, key=lambda k: k["EXEC_ORDER"])[0]
            if efcall_record_list
            else {}
        )
        cfcall_record = (
            # sorted(cfcall_record_list, key=lambda k: k["EXEC_ORDER"])[0]
            sorted(cfcall_record_list, key=lambda k: k["CFCALL_ID"])[0]
            if cfcall_record_list
            else {}
        )
        dfcall_record = (
            # sorted(dfcall_record_list, key=lambda k: k["EXEC_ORDER"])[0]
            sorted(dfcall_record_list, key=lambda k: k["DFCALL_ID"])[0]
            if dfcall_record_list
            else {}
        )

        sfunc_record = (
            self.get_record("CFG_SFUNC", "SFUNC_ID", sfcall_record["SFUNC_ID"])
            if sfcall_record
            else {}
        )
        efunc_record = (
            self.get_record("CFG_EFUNC", "EFUNC_ID", efcall_record["EFUNC_ID"])
            if efcall_record
            else {}
        )
        cfunc_record = (
            self.get_record("CFG_CFUNC", "CFUNC_ID", cfcall_record["CFUNC_ID"])
            if cfcall_record
            else {}
        )
        dfunc_record = (
            self.get_record("CFG_DFUNC", "DFUNC_ID", dfcall_record["DFUNC_ID"])
            if dfcall_record
            else {}
        )

        ftype_data = {
            "id": ftype_record["FTYPE_ID"],
            "feature": ftype_record["FTYPE_CODE"],
            "class": fclass_record["FCLASS_CODE"] if fclass_record else "OTHER",
            "behavior": getFeatureBehavior(ftype_record),
            "anonymize": ftype_record["ANONYMIZE"],
            "candidates": ftype_record["USED_FOR_CAND"],
            "standardize": sfunc_record["SFUNC_CODE"] if sfunc_record else "",
            "expression": efunc_record["EFUNC_CODE"] if efunc_record else "",
            "comparison": cfunc_record["CFUNC_CODE"] if cfunc_record else "",
            # "distinct": dfunc_record['DFUNC_CODE'] if dfunc_record else '', (HIDDEN TO REDUCE CONFUSION, engineers use listDistinctCalls)
            "matchKey": ftype_record["SHOW_IN_MATCH_KEY"],
            "version": ftype_record["VERSION"],
        }
        element_list = []
        fbom_record_list = self.get_record_list(
            "CFG_FBOM", "FTYPE_ID", ftype_record["FTYPE_ID"]
        )
        for fbom_record in sorted(fbom_record_list, key=lambda k: k["EXEC_ORDER"]):
            felem_record = self.get_record(
                "CFG_FELEM", "FELEM_ID", fbom_record["FELEM_ID"]
            )
            if not felem_record:
                element_list.append("ERROR: FELEM_ID %s" % fbom_record["FELEM_ID"])
                break
            else:
                efbom_record = efcall_record and self.get_record(
                    "CFG_EFBOM",
                    ["EFCALL_ID", "FTYPE_ID", "FELEM_ID"],
                    [
                        efcall_record["EFCALL_ID"],
                        fbom_record["FTYPE_ID"],
                        fbom_record["FELEM_ID"],
                    ],
                )
                cfbom_record = cfcall_record and self.get_record(
                    "CFG_CFBOM",
                    ["CFCALL_ID", "FTYPE_ID", "FELEM_ID"],
                    [
                        cfcall_record["CFCALL_ID"],
                        fbom_record["FTYPE_ID"],
                        fbom_record["FELEM_ID"],
                    ],
                )
                element_record = {}
                element_record["element"] = felem_record["FELEM_CODE"]
                element_record["expressed"] = (
                    "No" if not efcall_record or not efbom_record else "Yes"
                )
                element_record["compared"] = (
                    "No" if not cfcall_record or not cfbom_record else "Yes"
                )
                element_record["derived"] = fbom_record["DERIVED"]
                element_record["display"] = (
                    "No" if fbom_record["DISPLAY_LEVEL"] == 0 else "Yes"
                )
                element_list.append(element_record)

        ftype_data["element_list"] = element_list

        return ftype_data

    def do_addFeature(self, arg):
        """
        Add an new feature to be used for resolution

        Syntax:
            addFeature {json_configuration}

        Examples:
            see listFeatures or getFeature for examples of json configurations

        Notes:
            The best way to add a feature is via templateAdd as it adds both the feature and its attributes.
            If you add a feature manually, you will also have to manually add attributes for it!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            if (
                "ELEMENTLIST" not in parm_data
                or len(parm_data["ELEMENTLIST"]) == 0
                or not isinstance(parm_data["ELEMENTLIST"], list)
            ):
                raise ValueError("element_list is required")
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
        if ftype_record:
            colorize_msg(message, "warning")
            return

        next_id = self.getDesiredValueOrNext(
            "CFG_FTYPE", "FTYPE_ID", parm_data.get("ID"), seed_order=1000
        )
        if parm_data.get("ID") and next_id != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return
        else:
            parm_data["ID"] = next_id

        ftype_id = parm_data["ID"]
        parm_data["CLASS"] = parm_data.get("CLASS", "OTHER").upper()
        parm_data["BEHAVIOR"] = parm_data.get("BEHAVIOR", "FM").upper()

        parm_data["CANDIDATES"], message = self.validateDomain(
            "Candidates", parm_data.get("CANDIDATES", "No"), ["Yes", "No"]
        )
        if not parm_data["CANDIDATES"]:
            colorize_msg(message, "error")
            return

        parm_data["ANONYMIZE"], message = self.validateDomain(
            "Anonymize", parm_data.get("ANONYMIZE", "No"), ["Yes", "No"]
        )
        if not parm_data["ANONYMIZE"]:
            colorize_msg(message, "error")
            return

        parm_data["DERIVED"], message = self.validateDomain(
            "Derived", parm_data.get("DERIVED", "No"), ["Yes", "No"]
        )
        if not parm_data["DERIVED"]:
            colorize_msg(message, "error")
            return

        parm_data["HISTORY"], message = self.validateDomain(
            "History", parm_data.get("HISTORY", "Yes"), ["Yes", "No"]
        )
        if not parm_data["HISTORY"]:
            colorize_msg(message, "error")
            return

        matchKeyDefault = "Yes" if parm_data.get("COMPARISON") else "No"
        parm_data["MATCHKEY"], message = self.validateDomain(
            "MatchKey",
            parm_data.get("MATCHKEY", matchKeyDefault),
            ["Yes", "No", "Confirm", "Denial"],
        )
        if not parm_data["MATCHKEY"]:
            colorize_msg(message, "error")
            return

        behaviorData, message = self.lookupBehaviorCode(parm_data["BEHAVIOR"])
        if not behaviorData:
            colorize_msg(message, "error")
            return

        fclass_record, message = self.lookupFeatureClass(parm_data["CLASS"])
        if not fclass_record:
            colorize_msg(message, "error")
            return
        fclassID = fclass_record["FCLASS_ID"]

        sfuncID = 0
        if parm_data.get("STANDARDIZE"):
            sfunc_record, message = self.lookupStandardizeFunction(
                parm_data["STANDARDIZE"]
            )
            if not sfunc_record:
                colorize_msg(message, "error")
                return
            sfuncID = sfunc_record["SFUNC_ID"]

        efuncID = 0
        if parm_data.get("EXPRESSION"):
            efunc_record, message = self.lookupExpressionFunction(
                parm_data["EXPRESSION"]
            )
            if not efunc_record:
                colorize_msg(message, "error")
                return
            efuncID = efunc_record["EFUNC_ID"]

        cfuncID = 0
        if parm_data.get("COMPARISON"):
            cfunc_record, message = self.lookupComparisonFunction(
                parm_data["COMPARISON"]
            )
            if not cfunc_record:
                colorize_msg(message, "error")
                return
            cfuncID = cfunc_record["CFUNC_ID"]

        # ensure elements going to express or compare routines
        if efuncID > 0 or cfuncID > 0:
            expressedCnt = comparedCnt = 0
            for element in parm_data["ELEMENTLIST"]:
                if type(element) == dict:
                    element = dict_keys_upper(element)
                    if "EXPRESSED" in element and element["EXPRESSED"].upper() == "YES":
                        expressedCnt += 1
                    if "COMPARED" in element and element["COMPARED"].upper() == "YES":
                        comparedCnt += 1
            if efuncID > 0 and expressedCnt == 0:
                colorize_msg(
                    'No elements marked "expressed" for expression routine', "error"
                )
                return
            if cfuncID > 0 and comparedCnt == 0:
                colorize_msg(
                    'No elements marked "compared" for comparison routine', "error"
                )
                return

        # insert the feature
        newRecord = {}
        newRecord["FTYPE_ID"] = int(ftype_id)
        newRecord["FTYPE_CODE"] = parm_data["FEATURE"]
        newRecord["FTYPE_DESC"] = parm_data["FEATURE"]
        newRecord["FCLASS_ID"] = fclassID
        newRecord["FTYPE_FREQ"] = behaviorData["FREQUENCY"]
        newRecord["FTYPE_EXCL"] = behaviorData["EXCLUSIVITY"]
        newRecord["FTYPE_STAB"] = behaviorData["STABILITY"]
        newRecord["ANONYMIZE"] = parm_data["ANONYMIZE"]
        newRecord["DERIVED"] = parm_data["DERIVED"]
        newRecord["USED_FOR_CAND"] = parm_data["CANDIDATES"]
        newRecord["SHOW_IN_MATCH_KEY"] = parm_data.get("MATCHKEY", "Yes")
        # somewhat hidden fields in case an engineer wants to specify them
        newRecord["PERSIST_HISTORY"] = parm_data.get("HISTORY", "Yes")
        newRecord["DERIVATION"] = parm_data.get("DERIVATION")
        newRecord["VERSION"] = parm_data.get("VERSION", 1)
        newRecord["RTYPE_ID"] = parm_data.get("RTYPEID", 0)

        self.config_data["G2_CONFIG"]["CFG_FTYPE"].append(newRecord)

        # add the standardize call
        sfcallID = 0
        if sfuncID > 0:
            sfcallID = self.getDesiredValueOrNext(
                "CFG_SFCALL", "SFCALL_ID", 0, seed_order=1000
            )
            newRecord = {}
            newRecord["SFCALL_ID"] = sfcallID
            newRecord["SFUNC_ID"] = sfuncID
            newRecord["EXEC_ORDER"] = 1
            newRecord["FTYPE_ID"] = ftype_id
            newRecord["FELEM_ID"] = -1
            self.config_data["G2_CONFIG"]["CFG_SFCALL"].append(newRecord)

        # add the distinct value call (NOT SUPPORTED THROUGH HERE YET)
        dfcall_id = 0
        dfuncID = 0
        if dfuncID > 0:
            dfcall_id = self.getDesiredValueOrNext(
                "CFG_DFCALL", "DFCALL_ID", 0, seed_order=1000
            )
            newRecord = {}
            newRecord["DFCALL_ID"] = dfcall_id
            newRecord["DFUNC_ID"] = dfuncID
            newRecord["EXEC_ORDER"] = 1
            newRecord["FTYPE_ID"] = ftype_id
            self.config_data["G2_CONFIG"]["CFG_DFCALL"].append(newRecord)

        # add the expression call
        efcall_id = 0
        if efuncID > 0:
            efcall_id = self.getDesiredValueOrNext(
                "CFG_EFCALL", "EFCALL_ID", 0, seed_order=1000
            )
            newRecord = {}
            newRecord["EFCALL_ID"] = efcall_id
            newRecord["EFUNC_ID"] = efuncID
            newRecord["EXEC_ORDER"] = 1
            newRecord["FTYPE_ID"] = ftype_id
            newRecord["FELEM_ID"] = -1
            newRecord["EFEAT_FTYPE_ID"] = -1
            newRecord["IS_VIRTUAL"] = "No"
            self.config_data["G2_CONFIG"]["CFG_EFCALL"].append(newRecord)

        # add the comparison call
        cfcall_id = 0
        if cfuncID > 0:
            cfcall_id = self.getDesiredValueOrNext(
                "CFG_CFCALL", "CFCALL_ID", 0, seed_order=1000
            )
            newRecord = {}
            newRecord["CFCALL_ID"] = cfcall_id
            newRecord["CFUNC_ID"] = cfuncID
            newRecord["EXEC_ORDER"] = 1
            newRecord["FTYPE_ID"] = ftype_id
            self.config_data["G2_CONFIG"]["CFG_CFCALL"].append(newRecord)

        fbomOrder = 0
        for element in parm_data["ELEMENTLIST"]:
            fbomOrder += 1

            if type(element) == dict:
                element_record = dict_keys_upper(element)
                element_record["ELEMENT"] = element_record["ELEMENT"].upper()
            else:
                element_record = {}
                element_record["ELEMENT"] = element.upper()
            if "EXPRESSED" not in element_record:
                element_record["EXPRESSED"] = "No"
            if "COMPARED" not in element_record:
                element_record["COMPARED"] = "No"

            felem_record, message = self.lookupElement(element_record["ELEMENT"])
            if felem_record:
                felemID = felem_record["FELEM_ID"]
            else:
                felemID = self.getDesiredValueOrNext(
                    "CFG_FELEM", "FELEM_ID", 0, seed_order=1000
                )
                newRecord = {}
                newRecord["FELEM_ID"] = felemID
                newRecord["FELEM_CODE"] = element_record["ELEMENT"]
                newRecord["FELEM_DESC"] = element_record["ELEMENT"]
                newRecord["DATA_TYPE"] = "string"
                newRecord["TOKENIZE"] = "No"
                self.config_data["G2_CONFIG"]["CFG_FELEM"].append(newRecord)

            # add all elements to distinct bom if specified
            if dfcall_id > 0:
                newRecord = {}
                newRecord["DFCALL_ID"] = dfcall_id
                newRecord["EXEC_ORDER"] = fbomOrder
                newRecord["FTYPE_ID"] = ftype_id
                newRecord["FELEM_ID"] = felemID
                self.config_data["G2_CONFIG"]["CFG_DFBOM"].append(newRecord)

            # add to expression bom if directed to
            if efcall_id > 0 and element_record["EXPRESSED"].upper() == "YES":
                newRecord = {}
                newRecord["EFCALL_ID"] = efcall_id
                newRecord["EXEC_ORDER"] = fbomOrder
                newRecord["FTYPE_ID"] = ftype_id
                newRecord["FELEM_ID"] = felemID
                newRecord["FELEM_REQ"] = "Yes"
                self.config_data["G2_CONFIG"]["CFG_EFBOM"].append(newRecord)

            # add to comparison bom if directed to
            if cfcall_id > 0 and element_record["COMPARED"].upper() == "YES":
                newRecord = {}
                newRecord["CFCALL_ID"] = cfcall_id
                newRecord["EXEC_ORDER"] = fbomOrder
                newRecord["FTYPE_ID"] = ftype_id
                newRecord["FELEM_ID"] = felemID
                self.config_data["G2_CONFIG"]["CFG_CFBOM"].append(newRecord)

            # standardize display_level to just display while maintaining backwards compatibility
            if "DISPLAY" in element_record:
                element_record["DISPLAY_LEVEL"] = (
                    1 if element_record["DISPLAY"].upper() == "YES" else 0
                )

            if "DERIVED" in element_record:
                element_record["DERIVED"] = (
                    "Yes" if element_record["DERIVED"].upper() == "YES" else "No"
                )

            # add to feature bom always
            newRecord = {}
            newRecord["FTYPE_ID"] = ftype_id
            newRecord["FELEM_ID"] = felemID
            newRecord["EXEC_ORDER"] = fbomOrder
            newRecord["DISPLAY_LEVEL"] = element_record.get("DISPLAY_LEVEL", 1)
            newRecord["DISPLAY_DELIM"] = element_record.get("DISPLAY_DELIM")
            newRecord["DERIVED"] = element_record.get("DERIVED", "No")

            self.config_data["G2_CONFIG"]["CFG_FBOM"].append(newRecord)

        self.config_updated = True
        colorize_msg("Feature successfully added!", "success")

    def do_setFeature(self, arg):
        """
        Sets configuration parameters for an existing feature

        Syntax:
            setFeature {partial_json_configuration}

        Examples:
            setFeature {"feature": "NAME", "candidates": "Yes"}

        Caution:
            - Not everything about a feature can be set here. Some changes will require a delete and re-add of the
              feature. For instance, you cannot change a feature's ID or its list of elements.
            - Standardize, expression and comparison routines cannot be changed here.  However, you can
              use their call commands to make changes. e.g, deleteExpressionCall, addExpressionCall, etc.
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE"])
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        old_ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
        if not old_ftype_record:
            colorize_msg(message, "warning")
            return

        ftype_record = dict(old_ftype_record)  # must use dict to create a new instance
        update_cnt = 0
        error_cnt = 0
        for parmCode in parm_data:
            if parmCode == "FEATURE":
                continue
            if parmCode == "CANDIDATES":
                parm_data["CANDIDATES"], message = self.validateDomain(
                    "Candidates", parm_data.get("CANDIDATES", "No"), ["Yes", "No"]
                )
                if not parm_data["CANDIDATES"]:
                    colorize_msg(message, "error")
                    error_cnt += 1
                else:
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record,
                        update_cnt,
                        "USED_FOR_CAND",
                        parm_data["CANDIDATES"],
                    )

            elif parmCode == "ANONYMIZE":
                parm_data["ANONYMIZE"], message = self.validateDomain(
                    "Anonymize", parm_data.get("ANONYMIZE", "No"), ["Yes", "No"]
                )
                if not parm_data["ANONYMIZE"]:
                    colorize_msg(message, "error")
                    error_cnt += 1
                else:
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record, update_cnt, "ANONYMIZE", parm_data["ANONYMIZE"]
                    )

            elif parmCode == "DERIVED":
                parm_data["DERIVED"], message = self.validateDomain(
                    "Derived", parm_data.get("DERIVED", "No"), ["Yes", "No"]
                )
                if not parm_data["DERIVED"]:
                    colorize_msg(message, "error")
                    error_cnt += 1
                else:
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record, update_cnt, "DERIVED", parm_data["DERIVED"]
                    )

            elif parmCode == "HISTORY":
                parm_data["HISTORY"], message = self.validateDomain(
                    "History", parm_data.get("HISTORY", "Yes"), ["Yes", "No"]
                )
                if not parm_data["HISTORY"]:
                    colorize_msg(message, "error")
                    error_cnt += 1
                else:
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record, update_cnt, "HISTORY", parm_data["HISTORY"]
                    )

            elif parmCode == "MATCHKEY":
                matchKeyDefault = "Yes" if parm_data.get("COMPARISON") else "No"
                parm_data["MATCHKEY"], message = self.validateDomain(
                    "MatchKey",
                    parm_data.get("MATCHKEY", matchKeyDefault),
                    ["Yes", "No", "Confirm", "Denial"],
                )
                if not parm_data["MATCHKEY"]:
                    colorize_msg(message, "error")
                    error_cnt += 1
                else:
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record,
                        update_cnt,
                        "SHOW_IN_MATCH_KEY",
                        parm_data["MATCHKEY"],
                    )

            elif parmCode == "BEHAVIOR":
                behaviorData, message = self.lookupBehaviorCode(parm_data["BEHAVIOR"])
                if not behaviorData:
                    colorize_msg(message, "error")
                    error_cnt += 1
                else:
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record,
                        update_cnt,
                        "FTYPE_FREQ",
                        behaviorData["FREQUENCY"],
                    )
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record,
                        update_cnt,
                        "FTYPE_EXCL",
                        behaviorData["EXCLUSIVITY"],
                    )
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record,
                        update_cnt,
                        "FTYPE_STAB",
                        behaviorData["STABILITY"],
                    )

            elif parmCode == "CLASS":
                fclass_record, message = self.lookupFeatureClass(parm_data["CLASS"])
                if not fclass_record:
                    colorize_msg(message, "error")
                    error_cnt += 1
                else:
                    ftype_record, update_cnt = self.update_if_different(
                        ftype_record,
                        update_cnt,
                        "FCLASS_ID",
                        fclass_record["FCLASS_ID"],
                    )

            elif parmCode == "DERIVATION":
                ftype_record, update_cnt = self.update_if_different(
                    ftype_record, update_cnt, "DERIVATION", parm_data["DERIVATION"]
                )

            elif parmCode == "VERSION":
                ftype_record, update_cnt = self.update_if_different(
                    ftype_record, update_cnt, "VERSION", parm_data["VERSION"]
                )

            elif parmCode == "RTYPEID":
                ftype_record, update_cnt = self.update_if_different(
                    ftype_record, update_cnt, "RTYPE_ID", parm_data["RTYPEID"]
                )

            elif parmCode == "ID":
                if parm_data["ID"] != ftype_record["FTYPE_ID"]:
                    colorize_msg("Cannot change ID on features", "error")
                    error_cnt += 1
            else:
                if parm_data[parmCode] != ftype_record.get(parmCode, ""):
                    colorize_msg(
                        f"Cannot {'set' if parm_data[parmCode] else 'unset'} {parmCode} on features",
                        "error",
                    )
                    error_cnt += 1
        if error_cnt > 0:
            colorize_msg("Errors encountered, feature not updated", "error")
        elif update_cnt < 1:
            colorize_msg("No changes detected", "warning")
        else:
            self.config_data["G2_CONFIG"]["CFG_FTYPE"].remove(old_ftype_record)
            self.config_data["G2_CONFIG"]["CFG_FTYPE"].append(ftype_record)
            colorize_msg("Feature successfully updated!", "success")
            self.config_updated = True

    def do_listFeatures(self, arg):
        """
        Returns the list of registered features

        Syntax:
            listFeatures [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for ftype_record in sorted(
            self.get_record_list("CFG_FTYPE"), key=lambda k: k["FTYPE_ID"]
        ):
            feature_json = self.format_feature_json(ftype_record)
            if arg and arg.lower() not in str(feature_json.lower()):
                continue
            json_lines.append(feature_json)

        self.print_json_lines(json_lines)

    def do_getFeature(self, arg):
        """
        Returns a specific feature's json configuration

        Syntax:
            getFeature [code or id] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "FEATURE", "FTYPE_ID", "FTYPE_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        ftype_record = self.get_record("CFG_FTYPE", search_field, search_value)
        if ftype_record:
            self.print_json_record(self.format_feature_json(ftype_record))
        else:
            colorize_msg("Feature not found", "error")

    def do_deleteFeature(self, arg):
        """
        Deletes a feature and its attributes

        Syntax:
            deleteFeature [code or id]

        Caution:
            Deleting a feature does not delete its data and you will be prevented from saving if it has data loaded!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "FEATURE", "FTYPE_ID", "FTYPE_CODE"
            )
        except Exception as err:
            colorize_msg(err, "error")
            return

        ftype_record = self.get_record("CFG_FTYPE", search_field, search_value)
        if not ftype_record:
            colorize_msg("Feature not found", "error")
            return

        if ftype_record["FTYPE_CODE"] in self.locked_feature_list:
            colorize_msg(
                f"The feature {ftype_record['FTYPE_CODE']} cannot be deleted", "error"
            )
            return

        # also delete all supporting tables
        for fbom_record in self.get_record_list(
            "CFG_FBOM", "FTYPE_ID", ftype_record["FTYPE_ID"]
        ):
            self.config_data["G2_CONFIG"]["CFG_FBOM"].remove(fbom_record)

        for attr_record in self.get_record_list(
            "CFG_ATTR", "FTYPE_CODE", ftype_record["FTYPE_CODE"]
        ):
            self.config_data["G2_CONFIG"]["CFG_ATTR"].remove(attr_record)

        for sfcall_record in self.get_record_list(
            "CFG_SFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        ):
            self.config_data["G2_CONFIG"]["CFG_SFCALL"].remove(sfcall_record)

        for efcall_record in self.get_record_list(
            "CFG_EFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        ):
            for efbom_record in self.get_record_list(
                "CFG_EFBOM", "EFCALL_ID", efcall_record["EFCALL_ID"]
            ):
                self.config_data["G2_CONFIG"]["CFG_EFBOM"].remove(efbom_record)
            self.config_data["G2_CONFIG"]["CFG_EFCALL"].remove(efcall_record)

        for cfcall_record in self.get_record_list(
            "CFG_CFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        ):
            for cfbom_record in self.get_record_list(
                "CFG_CFBOM", "CFCALL_ID", cfcall_record["CFCALL_ID"]
            ):
                self.config_data["G2_CONFIG"]["CFG_CFBOM"].remove(cfbom_record)
            self.config_data["G2_CONFIG"]["CFG_CFCALL"].remove(cfcall_record)

        for dfcall_record in self.get_record_list(
            "CFG_DFCALL", "FTYPE_ID", ftype_record["FTYPE_ID"]
        ):
            for dfbom_record in self.get_record_list(
                "CFG_DFBOM", "DFCALL_ID", dfcall_record["DFCALL_ID"]
            ):
                self.config_data["G2_CONFIG"]["CFG_DFBOM"].remove(dfbom_record)
            self.config_data["G2_CONFIG"]["CFG_DFCALL"].remove(dfcall_record)

        self.config_data["G2_CONFIG"]["CFG_FTYPE"].remove(ftype_record)
        colorize_msg("Feature successfully deleted!", "success")
        self.config_updated = True

    # ===== feature element commands =====

    def format_element_json(self, element_record):
        element_data = {
            "id": element_record["FELEM_ID"],
            "element": element_record["FELEM_CODE"],
            "datatype": element_record["DATA_TYPE"],
            # "tokenize": element_record["TOKENIZE"],
        }
        return element_data

    def do_addElement(self, arg):
        """
        Adds a new element

        Syntax:
            addElement {json_configuration}

        Examples:
            see listElements for examples of json_configurations
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ELEMENT"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if self.get_record("CFG_FELEM", "FELEM_CODE", parm_data["ELEMENT"]):
            colorize_msg("Element already exists", "warning")
            return

        parm_data["DATATYPE"], message = self.validateDomain(
            "DataType",
            parm_data.get("DATATYPE", "string"),
            ["string", "number", "date", "datetime", "json"],
        )
        if not parm_data["DATATYPE"]:
            colorize_msg(message, "error")
            return

        parm_data["TOKENIZE"], message = self.validateDomain(
            "Tokenize", parm_data.get("TOKENIZE", "No"), ["Yes", "No"]
        )
        if not parm_data["TOKENIZE"]:
            colorize_msg(message, "error")
            return

        felemID = self.getDesiredValueOrNext(
            "CFG_FELEM", "FELEM_ID", parm_data.get("ID"), seed_order=1000
        )
        if parm_data.get("ID") and felemID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        newRecord = {}
        newRecord["FELEM_ID"] = felemID
        newRecord["FELEM_CODE"] = parm_data["ELEMENT"]
        newRecord["FELEM_DESC"] = parm_data["ELEMENT"]
        newRecord["TOKENIZE"] = parm_data["TOKENIZE"]
        newRecord["DATA_TYPE"] = parm_data["DATATYPE"]
        self.config_data["G2_CONFIG"]["CFG_FELEM"].append(newRecord)
        self.config_updated = True
        colorize_msg("Element successfully added!", "success")

    def do_listElements(self, arg):
        """
        Returns the list of elements.

        Syntax:
            listElements [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for element_record in sorted(
            self.get_record_list("CFG_FELEM"), key=lambda k: k["FELEM_CODE"]
        ):
            elementJson = self.format_element_json(element_record)
            if arg and arg.lower() not in str(elementJson).lower():
                continue
            json_lines.append(elementJson)

        self.print_json_lines(json_lines)

    def do_getElement(self, arg):
        """
        Returns a single element

        Syntax:
            getElement [code or id] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "ELEMENT", "FELEM_ID", "FELEM_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        element_record = self.get_record("CFG_FELEM", search_field, search_value)
        if not element_record:
            colorize_msg("Element does not exist", "warning")
            return
        self.print_json_record(self.format_element_json(element_record))

    def do_deleteElement(self, arg):
        """
        Deletes an element

        Syntax:
            deleteElement [code or id]
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "ELEMENT", "FELEM_ID", "FELEM_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        element_record = self.get_record("CFG_FELEM", search_field, search_value)
        if not element_record:
            colorize_msg("Element does not exist", "warning")
            return

        fbom_record_list = self.get_record_list(
            "CFG_FBOM", "FELEM_ID", element_record["FELEM_ID"]
        )
        if fbom_record_list:
            feature_list = ",".join(
                (
                    self.get_record("CFG_FTYPE", "FTYPE_ID", x["FTYPE_ID"])[
                        "FTYPE_CODE"
                    ]
                    for x in fbom_record_list
                )
            )
            colorize_msg(
                f"Element linked to the following feature(s): {feature_list}", "error"
            )
            return

        self.config_data["G2_CONFIG"]["CFG_FELEM"].remove(element_record)
        colorize_msg("Element successfully deleted!", "success")
        self.config_updated = True

    def do_addElementToFeature(self, arg):
        """
        Add an element to an existing feature

        Syntax:
            addElementToFeature {json_configuration}

        Example:
            addElementToFeature {"feature": "PASSPORT", "element": "STATUS", "derived": "No", "display": "Yes"}

        Notes:
            This command appends an additional element to an existing feature. The element will be added if it does not exist.
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE", "ELEMENT"])
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        ftype_record, message = self.lookupFeature(parm_data["FEATURE"].upper())
        if not ftype_record:
            colorize_msg(message, "error")
            return
        ftype_id = ftype_record["FTYPE_ID"]

        if not self.get_record("CFG_FELEM", "FELEM_CODE", parm_data["ELEMENT"]):
            self.do_addElement(json.dumps(parm_data))

        felem_record, message = self.lookupElement(parm_data["ELEMENT"])
        if (
            not felem_record
        ):  # this should not happen as we added if not exists just above
            colorize_msg(message, "error")
            return
        felemID = felem_record["FELEM_ID"]

        fbom_record, message = self.lookupFeatureElement(
            parm_data["FEATURE"], parm_data["ELEMENT"]
        )
        if fbom_record:
            colorize_msg(message, "warning")
            return

        parm_data["DERIVED"], message = self.validateDomain(
            "Derived", parm_data.get("DERIVED", "No"), ["Yes", "No"]
        )
        if not parm_data["DERIVED"]:
            colorize_msg(message, "error")
            return

        if "DISPLAY_LEVEL" in parm_data:
            parm_data["DISPLAY"] = parm_data["DISPLAY_LEVEL"]
        parm_data["DISPLAY"], message = self.validateDomain(
            "Display", parm_data.get("DISPLAY", "No"), ["Yes", "No"]
        )
        if not parm_data["DISPLAY"]:
            colorize_msg(message, "error")
            return

        execOrder = self.getDesiredValueOrNext(
            "CFG_FBOM", "EXEC_ORDER", parm_data.get("EXECORDER", 0)
        )
        if parm_data.get("EXECORDER") and execOrder != parm_data["EXECORDER"]:
            colorize_msg(
                "The specified execution order is already taken  (remove it to assign the next available)",
                "error",
            )
            return
        else:
            parm_data["EXECORDER"] = execOrder

        newRecord = {}
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["FELEM_ID"] = felemID
        newRecord["EXEC_ORDER"] = parm_data["EXECORDER"]
        newRecord["DISPLAY_LEVEL"] = 0 if parm_data["DISPLAY"] == "No" else "Yes"
        newRecord["DISPLAY_DELIM"] = parm_data.get("DISPLAY_DELIM")
        newRecord["DERIVED"] = parm_data["DERIVED"]
        self.config_data["G2_CONFIG"]["CFG_FBOM"].append(newRecord)
        self.config_updated = True
        colorize_msg("Element successfully added to feature!", "success")

    def do_setFeatureElement(self, arg):
        """
        Sets a feature element's attributes

        Syntax:
            setFeatureElement {json_configuration}

        Example:
            setFeatureElement {"feature": "ACCT_NUM", "element": "ACCT_DOMAIN", "display": "No"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE", "ELEMENT"])
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        old_record, message = self.lookupFeatureElement(
            parm_data["FEATURE"], parm_data["ELEMENT"]
        )
        if not old_record:
            colorize_msg(message, "warning")
            return

        oldParmData = {
            "DERIVED": old_record["DERIVED"],
            "DISPLAY": "No" if old_record["DISPLAY_LEVEL"] == 0 else "Yes",
        }

        newRecord = dict(old_record)  # must use dict to create a new instance
        if parm_data.get("DERIVED"):
            parm_data["DERIVED"], message = self.validateDomain(
                "Derived", parm_data.get("DERIVED", "No"), ["Yes", "No"]
            )
            if not parm_data["DERIVED"]:
                colorize_msg(message, "error")
                return
            newRecord["DERIVED"] = parm_data["DERIVED"]

        if "DISPLAY" in parm_data:
            if parm_data["DISPLAY"] == 1:
                parm_data["DISPLAY"] = "Yes"
            elif parm_data["DISPLAY"] == 0:
                parm_data["DISPLAY"] = "No"
            parm_data["DISPLAY"], message = self.validateDomain(
                "Display", parm_data.get("DISPLAY", "No"), ["Yes", "No"]
            )
            if not parm_data["DISPLAY"]:
                colorize_msg(message, "error")
                return
            newRecord["DISPLAY_LEVEL"] = 0 if parm_data["DISPLAY"] == "No" else 1

        if parm_data.get("DISPLAY_DELIM"):
            newRecord["DISPLAY_DELIM"] = parm_data["DISPLAY_DELIM"]

        self.config_data["G2_CONFIG"]["CFG_FBOM"].remove(old_record)
        self.config_data["G2_CONFIG"]["CFG_FBOM"].append(newRecord)
        colorize_msg("Feature element successfully updated!", "success")
        self.config_updated = True

    def do_deleteElementFromFeature(self, arg):
        """
        Delete an element from a feature

        Syntax:
            deleteElementFromFeature {json_configuration}

        Example:
            deleteElementFromFeature {"feature": "PASSPORT", "element": "STATUS"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE", "ELEMENT"])
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        fbom_record, message = self.lookupFeatureElement(
            parm_data["FEATURE"], parm_data["ELEMENT"]
        )
        if not fbom_record:
            colorize_msg(message, "warning")
            return

        self.config_data["G2_CONFIG"]["CFG_FBOM"].remove(fbom_record)
        colorize_msg("Element successfully deleted from feature!", "success")
        self.config_updated = True

    # ===== attribute commands =====

    def format_attribute_json(self, attribute_record):
        return {
            "id": attribute_record["ATTR_ID"],
            "attribute": attribute_record["ATTR_CODE"],
            "class": attribute_record["ATTR_CLASS"],
            "feature": attribute_record["FTYPE_CODE"],
            "element": attribute_record["FELEM_CODE"],
            "required": attribute_record["FELEM_REQ"],
            "default": attribute_record["DEFAULT_VALUE"],
            "internal": attribute_record["INTERNAL"],
        }
        # "advanced": attribute_record["ADVANCED"],

    def do_addAttribute(self, arg):
        """
        Adds a new attribute and maps it to a feature element

        Syntax:
            addAttribute {json_configuration}

        Examples:
            see listAttributes or getAttribute for examples of json configurations

        Notes:
            - The best way to add an attribute is via templateAdd as it adds both the feature and its attributes.
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ATTRIBUTE", "FEATURE", "ELEMENT"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["ATTRIBUTE"] = parm_data["ATTRIBUTE"].upper()
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        attr_record, message = self.lookupAttribute(parm_data["ATTRIBUTE"])
        if attr_record:
            colorize_msg(message, "warning")
            return

        next_id = self.getDesiredValueOrNext("CFG_ATTR", "ATTR_ID", parm_data.get("ID"))
        if parm_data.get("ID") and next_id != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken  (remove it to assign the next available)",
                "error",
            )
            return
        else:
            parm_data["ID"] = next_id

        parm_data["CLASS"], message = self.validateDomain(
            "Attribute class",
            parm_data.get("CLASS", "OTHER"),
            self.attribute_class_list,
        )
        if not parm_data["CLASS"]:
            colorize_msg(message, "error")
            return

        if parm_data["ELEMENT"] in (
            "<PREHASHED>",
            "USED_FROM_DT",
            "USED_THRU_DT",
            "USAGE_TYPE",
        ):
            featRecord, message = self.lookupFeature(parm_data["FEATURE"])
            if not featRecord:
                colorize_msg(message, "error")
                return
        else:
            fbom_record, message = self.lookupFeatureElement(
                parm_data["FEATURE"], parm_data["ELEMENT"]
            )
            if not fbom_record:
                colorize_msg(message, "error")
                return

        parm_data["REQUIRED"], message = self.validateDomain(
            "Required", parm_data.get("REQUIRED", "No"), ["Yes", "No", "Any", "Desired"]
        )
        if not parm_data["REQUIRED"]:
            colorize_msg(message, "error")
            return

        parm_data["ADVANCED"], message = self.validateDomain(
            "Advanced", parm_data.get("ADVANCED", "No"), ["Yes", "No"]
        )
        if not parm_data["ADVANCED"]:
            colorize_msg(message, "error")
            return

        parm_data["INTERNAL"], message = self.validateDomain(
            "Internal", parm_data.get("INTERNAL", "No"), ["Yes", "No"]
        )
        if not parm_data["INTERNAL"]:
            colorize_msg(message, "error")
            return

        newRecord = {}
        newRecord["ATTR_ID"] = int(parm_data["ID"])
        newRecord["ATTR_CODE"] = parm_data["ATTRIBUTE"]
        newRecord["ATTR_CLASS"] = parm_data["CLASS"]
        newRecord["FTYPE_CODE"] = parm_data["FEATURE"]
        newRecord["FELEM_CODE"] = parm_data["ELEMENT"]
        newRecord["FELEM_REQ"] = parm_data["REQUIRED"]
        newRecord["DEFAULT_VALUE"] = parm_data.get("DEFAULT")
        newRecord["ADVANCED"] = parm_data["ADVANCED"]
        newRecord["INTERNAL"] = parm_data["INTERNAL"]
        self.config_data["G2_CONFIG"]["CFG_ATTR"].append(newRecord)
        self.config_updated = True
        colorize_msg("Attribute successfully added!", "success")

    def do_setAttribute(self, arg):
        """
        Sets existing attribute settings

        Syntax:
            setAttribute {json_configuration}

        Example:
            setAttribute {"attribute": "ACCOUNT_NUMBER", "Advanced": "Yes"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ATTRIBUTE"])
            parm_data["ATTRIBUTE"] = parm_data["ATTRIBUTE"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        old_record, message = self.lookupAttribute(parm_data["ATTRIBUTE"])
        if not old_record:
            colorize_msg(message, "warning")
            return

        oldParmData = dict_keys_upper(self.format_attribute_json(old_record))
        newParmData = self.settable_parms(
            oldParmData, parm_data, ("REQUIRED", "ADVANCED", "INTERNAL")
        )
        if newParmData.get("errors"):
            colorize_msg(newParmData["errors"], "error")
            return
        if newParmData["update_cnt"] == 0:
            colorize_msg("No changes detected", "warning")
            return

        newRecord = dict(old_record)  # must use dict to create a new instance
        if parm_data.get("REQUIRED"):
            parm_data["REQUIRED"], message = self.validateDomain(
                "Required", parm_data.get("REQUIRED", "No"), ["Yes", "No"]
            )
            if not parm_data["REQUIRED"]:
                colorize_msg(message, "error")
                return
            newRecord["FELEM_REQ"] = parm_data["REQUIRED"]

        if parm_data.get("ADVANCED"):
            parm_data["ADVANCED"], message = self.validateDomain(
                "Advanced", parm_data.get("ADVANCED", "No"), ["Yes", "No"]
            )
            if not parm_data["ADVANCED"]:
                colorize_msg(message, "error")
                return
            newRecord["ADVANCED"] = parm_data["ADVANCED"]

        if parm_data.get("INTERNAL"):
            parm_data["INTERNAL"], message = self.validateDomain(
                "Internal", parm_data.get("INTERNAL", "No"), ["Yes", "No"]
            )
            if not parm_data["INTERNAL"]:
                colorize_msg(message, "error")
                return
            newRecord["INTERNAL"] = parm_data["INTERNAL"]

        self.config_data["G2_CONFIG"]["CFG_ATTR"].remove(old_record)
        self.config_data["G2_CONFIG"]["CFG_ATTR"].append(newRecord)
        colorize_msg("Attribute successfully updated!", "success")
        self.config_updated = True

    def do_listAttributes(self, arg):
        # TODO Add Examples to all help, what is a filter_expression?
        """
        Returns the list of registered attributes

        Syntax:
            listAttributes [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for attr_record in sorted(
            self.get_record_list("CFG_ATTR"), key=lambda k: k["ATTR_ID"]
        ):
            if arg and arg.lower() not in str(attr_record).lower():
                continue
            json_lines.append(self.format_attribute_json(attr_record))

        self.print_json_lines(json_lines)

    def do_getAttribute(self, arg):
        """
        Returns a specific attribute's json configuration

        Syntax:
            getAttribute [code or id] [table|json|jsonl]

        Notes:
            If you specify a valid feature, all of its attributes will be displayed
                try: getAttribute PASSPORT
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "ATTRIBUTE", "ATTR_ID", "ATTR_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        attr_record = self.get_record("CFG_ATTR", search_field, search_value)
        if attr_record:
            self.print_json_record(self.format_attribute_json(attr_record))

        # hack to see if they entered a valid feature
        elif self.get_record_list("CFG_ATTR", "FTYPE_CODE", search_value):
            self.print_json_lines(
                self.get_record_list("CFG_ATTR", "FTYPE_CODE", search_value)
            )
        else:
            colorize_msg("Attribute not found", "error")

    def do_deleteAttribute(self, arg):
        """
        Deletes an attribute

        Syntax:
            deleteAttribute [code or id]
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "ATTRIBUTE", "ATTR_ID", "ATTR_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        attr_record = self.get_record("CFG_ATTR", search_field, search_value)
        if not attr_record:
            colorize_msg("Attribute not found", "warning")
            return

        self.config_data["G2_CONFIG"]["CFG_ATTR"].remove(attr_record)
        colorize_msg("Attribute successfully deleted!", "success")
        self.config_updated = True

    # ===== template commands =====

    def do_templateAdd(self, arg):
        """
        Adds a feature and its attributes based on a template

        Syntax:
            templateAdd {"feature": "feature_name", "template": "template_code", "behavior": "optional-override", "comparison": "optional-override"}

        Examples:
            templateAdd {"feature": "customer_number", "template": "global_id"}
            templateAdd {"feature": "customer_number", "template": "global_id", "behavior": "F1E"}
            templateAdd {"feature": "customer_number", "template": "global_id", "behavior": "F1E", "comparison": "exact_comp"}

        Notes:
            Type "templateAdd List" to get a list of valid templates.\n
        """
        validTemplates = {}
        validTemplates["GLOBAL_ID"] = {
            "DESCRIPTION": "globally unique identifier (like an ssn, a credit card, or a medicare_id)",
            "BEHAVIOR": ["F1", "F1E", "F1ES", "A1", "A1E", "A1ES"],
            "CANDIDATES": ["No"],
            "STANDARDIZE": ["PARSE_ID"],
            "EXPRESSION": ["EXPRESS_ID"],
            "COMPARISON": ["ID_COMP", "EXACT_COMP"],
            "FEATURE_CLASS": "ISSUED_ID",
            "ATTRIBUTE_CLASS": "IDENTIFIER",
            "ELEMENTS": [
                {
                    "element": "ID_NUM",
                    "expressed": "No",
                    "compared": "no",
                    "display": "Yes",
                },
                {
                    "element": "ID_NUM_STD",
                    "expressed": "Yes",
                    "compared": "yes",
                    "display": "No",
                },
            ],
            "ATTRIBUTES": [
                {"attribute": "<feature>", "element": "ID_NUM", "required": "Yes"}
            ],
        }

        validTemplates["STATE_ID"] = {
            "DESCRIPTION": "state issued identifier (like a drivers license)",
            "BEHAVIOR": ["F1", "F1E", "F1ES", "A1", "A1E", "A1ES"],
            "CANDIDATES": ["No"],
            "STANDARDIZE": ["PARSE_ID"],
            "EXPRESSION": ["EXPRESS_ID"],
            "COMPARISON": ["ID_COMP"],
            "FEATURE_CLASS": "ISSUED_ID",
            "ATTRIBUTE_CLASS": "IDENTIFIER",
            "ELEMENTS": [
                {
                    "element": "ID_NUM",
                    "expressed": "No",
                    "compared": "no",
                    "display": "Yes",
                },
                {
                    "element": "STATE",
                    "expressed": "No",
                    "compared": "yes",
                    "display": "Yes",
                },
                {
                    "element": "ID_NUM_STD",
                    "expressed": "Yes",
                    "compared": "yes",
                    "display": "No",
                },
            ],
            "ATTRIBUTES": [
                {
                    "attribute": "<feature>_NUMBER",
                    "element": "ID_NUM",
                    "required": "Yes",
                },
                {"attribute": "<feature>_STATE", "element": "STATE", "required": "No"},
            ],
        }

        validTemplates["COUNTRY_ID"] = {
            "DESCRIPTION": "country issued identifier (like a passport)",
            "BEHAVIOR": ["F1", "F1E", "F1ES", "A1", "A1E", "A1ES"],
            "CANDIDATES": ["No"],
            "STANDARDIZE": ["PARSE_ID"],
            "EXPRESSION": ["EXPRESS_ID"],
            "COMPARISON": ["ID_COMP"],
            "FEATURE_CLASS": "ISSUED_ID",
            "ATTRIBUTE_CLASS": "IDENTIFIER",
            "ELEMENTS": [
                {
                    "element": "ID_NUM",
                    "expressed": "No",
                    "compared": "no",
                    "display": "Yes",
                },
                {
                    "element": "COUNTRY",
                    "expressed": "No",
                    "compared": "yes",
                    "display": "Yes",
                },
                {
                    "element": "ID_NUM_STD",
                    "expressed": "Yes",
                    "compared": "yes",
                    "display": "No",
                },
            ],
            "ATTRIBUTES": [
                {
                    "attribute": "<feature>_NUMBER",
                    "element": "ID_NUM",
                    "required": "Yes",
                },
                {
                    "attribute": "<feature>_COUNTRY",
                    "element": "COUNTRY",
                    "required": "No",
                },
            ],
        }

        if arg and arg.upper() == "LIST":
            print()
            for template in validTemplates:
                print("\t", template, "-", validTemplates[template]["DESCRIPTION"])
                print("\t\tbehaviors:", validTemplates[template]["BEHAVIOR"])
                print("\t\tcomparisons:", validTemplates[template]["COMPARISON"])
                print()
            return

        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        feature = parm_data["FEATURE"].upper() if "FEATURE" in parm_data else None
        template = parm_data["TEMPLATE"].upper() if "TEMPLATE" in parm_data else None
        behavior = parm_data["BEHAVIOR"].upper() if "BEHAVIOR" in parm_data else None
        comparison = (
            parm_data["COMPARISON"].upper() if "COMPARISON" in parm_data else None
        )

        standardize = (
            parm_data["STANDARDIZE"].upper() if "STANDARDIZE" in parm_data else None
        )
        expression = (
            parm_data["EXPRESSION"].upper() if "EXPRESSION" in parm_data else None
        )
        candidates = (
            parm_data["CANDIDATES"].upper() if "CANDIDATES" in parm_data else None
        )

        if not feature:
            colorize_msg("A new feature name is required", "error")
            return
        if self.get_record("CFG_FTYPE", "FTYPE_CODE", feature):
            colorize_msg("Feature already exists", "warning")
            return

        if not template:
            colorize_msg("A valid template name is required", "error")
            return
        if template not in validTemplates:
            colorize_msg("template name supplied is not valid", "error")
            return

        if not behavior:
            behavior = validTemplates[template]["BEHAVIOR"][0]
        if behavior not in validTemplates[template]["BEHAVIOR"]:
            colorize_msg("behavior code supplied is not valid for template", "error")
            return

        if not comparison:
            comparison = validTemplates[template]["COMPARISON"][0]
        if comparison not in validTemplates[template]["COMPARISON"]:
            colorize_msg("comparison code supplied is not valid for template", "error")
            return

        if not standardize:
            standardize = validTemplates[template]["STANDARDIZE"][0]
        if standardize not in validTemplates[template]["STANDARDIZE"]:
            colorize_msg("standardize code supplied is not valid for template", "error")
            return

        if not expression:
            expression = validTemplates[template]["EXPRESSION"][0]
        if expression not in validTemplates[template]["EXPRESSION"]:
            colorize_msg("expression code supplied is not valid for template", "error")
            return

        if not candidates:
            candidates = validTemplates[template]["CANDIDATES"][0]
        if candidates not in validTemplates[template]["CANDIDATES"]:
            colorize_msg(
                "candidates setting supplied is not valid for template", "error"
            )
            return

        # values that can't be overridden
        featureClass = validTemplates[template]["FEATURE_CLASS"]
        attributeClass = validTemplates[template]["ATTRIBUTE_CLASS"]

        # exact comp corrections
        if comparison == "EXACT_COMP":
            standardize = ""
            expression = ""
            candidates = "Yes"

        # build the feature
        featureData = {
            "feature": feature,
            "behavior": behavior,
            "class": featureClass,
            "candidates": candidates,
            "standardize": standardize,
            "expression": expression,
            "comparison": comparison,
            "element_list": [],
        }
        for elementDict in validTemplates[template]["ELEMENTS"]:
            if not expression:
                elementDict["expressed"] = "No"
            if not standardize:
                if elementDict["display"] == "Yes":
                    elementDict["compared"] = "Yes"
                else:
                    elementDict["compared"] = "No"
            featureData["element_list"].append(elementDict)

        featureParm = json.dumps(featureData)
        colorize_msg(f"addFeature {featureParm}", "dim")
        self.do_addFeature(featureParm)

        # build the attributes
        for attributeDict in validTemplates[template]["ATTRIBUTES"]:
            attributeDict["attribute"] = attributeDict["attribute"].replace(
                "<feature>", feature
            )

            attributeData = {
                "attribute": attributeDict["attribute"].upper(),
                "class": attributeClass,
                "feature": feature,
                "element": attributeDict["element"].upper(),
                "required": attributeDict["required"],
            }

            attributeParm = json.dumps(attributeData)
            colorize_msg(f"addAttribute {attributeParm}", "dim")
            self.do_addAttribute(attributeParm)

        return

    # ===== call command support functions =====

    def setCallTypeTables(self, call_type):
        if call_type == "expression":
            call_table = "CFG_EFCALL"
            bom_table = "CFG_EFBOM"
            call_id_field = "EFCALL_ID"
            func_table = "CFG_EFUNC"
            func_code_field = "EFUNC_CODE"
            func_id_field = "EFUNC_ID"
        elif call_type == "comparison":
            call_table = "CFG_CFCALL"
            bom_table = "CFG_CFBOM"
            call_id_field = "CFCALL_ID"
            func_table = "CFG_CFUNC"
            func_code_field = "CFUNC_CODE"
            func_id_field = "CFUNC_ID"
        elif call_type == "distinct":
            call_table = "CFG_DFCALL"
            bom_table = "CFG_DFBOM"
            call_id_field = "DFCALL_ID"
            func_table = "CFG_DFUNC"
            func_code_field = "DFUNC_CODE"
            func_id_field = "DFUNC_ID"
        elif call_type == "standardize":
            call_table = "CFG_SFCALL"
            bom_table = None
            call_id_field = "SFCALL_ID"
            func_table = "CFG_SFUNC"
            func_code_field = "SFUNC_CODE"
            func_id_field = "SFUNC_ID"
        return (
            call_table,
            bom_table,
            call_id_field,
            func_table,
            func_code_field,
            func_id_field,
        )

    def getCallID(self, feature, call_type, function=None):
        (
            call_table,
            bom_table,
            call_id_field,
            func_table,
            func_code_field,
            func_id_field,
        ) = self.setCallTypeTables(call_type)
        ftype_record, message = self.lookupFeature(feature.upper())
        if not ftype_record:
            return 0, "Feature not found"
        if function:
            func_id = self.get_record(func_table, func_code_field, function)[
                func_id_field
            ]
            if not func_id:
                return 0, function + " not found"
            call_record = self.get_record(
                call_table,
                ["FTYPE_ID", func_id_field],
                [ftype_record["FTYPE_ID"], func_id],
            )
        else:
            call_recordList = self.get_record_list(
                call_table, "FTYPE_ID", ftype_record["FTYPE_ID"]
            )
            if len(call_recordList) == 1:
                call_record = call_recordList[0]
            elif len(call_recordList) > 1:
                return 0, "Multiple call records found for feature"
            else:
                return 0, "Call record not found"

        if not call_record:
            return 0, "Call record not found"

        return call_record[call_id_field], "success"

    def prep_call_record(self, call_type, arg):

        try:
            parm_data = (
                dict_keys_upper(json.loads(arg))
                if arg.startswith("{")
                else {
                    "ID" if arg.isdigit() else "FEATURE": (
                        int(arg) if arg.isdigit() else arg
                    )
                }
            )
        except Exception as err:
            return None, f"Command error: {err}"

        (
            call_table,
            bom_table,
            call_id_field,
            func_table,
            func_code_field,
            func_id_field,
        ) = self.setCallTypeTables(call_type)

        possible_message = "A feature name or call ID is required"
        if parm_data.get("FEATURE") and not parm_data.get("ID"):
            call_id, possible_message = self.getCallID(
                parm_data["FEATURE"].upper(), call_type
            )
            if call_id:
                parm_data["ID"] = call_id
        if not parm_data.get("ID"):
            return None, possible_message

        call_record = self.get_record(call_table, call_id_field, parm_data["ID"])
        if not call_record:
            return None, f"{call_type} call ID {parm_data['ID']} does not exist"
        return call_record, "success"

    def prepCallElement(self, arg):
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["CALLTYPE", "ELEMENT"])
        except Exception as err:
            return {"error": err}

        parm_data["CALLTYPE"], message = self.validateDomain(
            "Call type",
            parm_data.get("CALLTYPE"),
            ["expression", "comparison", "distinct"],
        )
        if not parm_data["CALLTYPE"]:
            return {"error": message}
        (
            call_table,
            bom_table,
            call_id_field,
            func_table,
            func_code_field,
            func_id_field,
        ) = self.setCallTypeTables(parm_data["CALLTYPE"])

        if parm_data.get("FEATURE") and not parm_data.get("ID"):
            call_id, possible_message = self.getCallID(
                parm_data["FEATURE"].upper(), parm_data["CALLTYPE"]
            )
            if call_id:
                parm_data["ID"] = call_id
        else:
            possible_message = "The call_id must be specified"

        if not parm_data.get("ID"):
            # return {'error': f"The call ID number must be specified - see list{parm_data['CALLTYPE'][0:1].upper() + parm_data['CALLTYPE'][1:].lower()}Calls to determine"}
            return {"error": possible_message}

        call_record = self.get_record(call_table, call_id_field, parm_data["ID"])
        if not call_record:
            return {"error": f"Call ID {parm_data['ID']} does not exist"}

        ftype_id = -1
        if parm_data.get("FEATURE"):
            ftype_record, message = self.lookupFeature(parm_data["FEATURE"].upper())
            if not ftype_record:
                return {"error": message}
            else:
                ftype_id = ftype_record["FTYPE_ID"]

        if ftype_id < 0:
            felem_record, message = self.lookupElement(parm_data["ELEMENT"])
            if not felem_record:
                return {"error": message}
            else:
                felemID = felem_record["FELEM_ID"]
        else:
            fbom_record, message = self.lookupFeatureElement(
                parm_data["FEATURE"], parm_data["ELEMENT"]
            )
            if not fbom_record:
                return {"error": message}
            else:
                felemID = fbom_record["FELEM_ID"]

        required, message = self.validateDomain(
            "Required", parm_data.get("REQUIRED", "No"), ["Yes", "No"]
        )
        if not required:
            return {"error": message}

        bomRecord = self.get_record(
            bom_table,
            [call_id_field, "FTYPE_ID", "FELEM_ID"],
            [parm_data["ID"], ftype_id, felemID],
        )
        callElementData = {
            "call_type": parm_data["CALLTYPE"],
            "call_table": call_table,
            "bom_table": bom_table,
            "call_id_field": call_id_field,
            "call_id": parm_data["ID"],
            "ftype_id": ftype_id,
            "felemID": felemID,
            "exec_order": parm_data.get("EXECORDER", 0),
            "required": required,
            "bomRecord": bomRecord,
        }
        return callElementData

    def addCallElement(self, arg):
        callElementData = self.prepCallElement(arg)
        if callElementData.get("error"):
            colorize_msg(callElementData["error"], "error")
            return
        if callElementData["bomRecord"]:
            colorize_msg("Feature/element already exists for call", "warning")
            return

        execOrder = self.getDesiredValueOrNext(
            callElementData["bom_table"],
            [callElementData["call_id_field"], "EXEC_ORDER"],
            [callElementData["call_id"], callElementData.get("exec_order", 0)],
        )
        if (
            callElementData.get("exec_order")
            and execOrder != callElementData["exec_order"]
        ):
            colorize_msg(
                "The specified order is already taken (remove it to assign the next available)",
                "error",
            )
            return

        newRecord = {}
        newRecord[callElementData["call_id_field"]] = callElementData["call_id"]
        newRecord["EXEC_ORDER"] = execOrder
        newRecord["FTYPE_ID"] = callElementData["ftype_id"]
        newRecord["FELEM_ID"] = callElementData["felemID"]
        if callElementData["bom_table"] == "CFG_EFBOM":
            newRecord["FELEM_REQ"] = callElementData["required"]

        self.config_data["G2_CONFIG"][callElementData["bom_table"]].append(newRecord)
        self.config_updated = True
        colorize_msg(
            f"{callElementData['call_type']} call element successfully added!",
            "success",
        )

    def delete_call_element(self, arg):
        callElementData = self.prepCallElement(arg)
        if callElementData.get("error"):
            colorize_msg(callElementData["error"], "error")
            return
        if not callElementData["bomRecord"]:
            colorize_msg("Feature/element not found for call", "warning")
            return

        self.config_data["G2_CONFIG"][callElementData["bom_table"]].remove(
            callElementData["bomRecord"]
        )
        colorize_msg(
            f"{callElementData['call_type']} call element successfully deleted!",
            "success",
        )
        self.config_updated = True

    # ===== standardize call commands =====

    def format_standarize_call_json(self, sfcall_record):
        sfcallID = sfcall_record["SFCALL_ID"]

        ftype_record1 = self.get_record(
            "CFG_FTYPE", "FTYPE_ID", sfcall_record["FTYPE_ID"]
        )
        felem_record1 = self.get_record(
            "CFG_FELEM", "FELEM_ID", sfcall_record["FELEM_ID"]
        )
        sfunc_record = self.get_record(
            "CFG_SFUNC", "SFUNC_ID", sfcall_record["SFUNC_ID"]
        )

        sfcall_data = {}
        sfcall_data["id"] = sfcallID

        if ftype_record1:
            sfcall_data["feature"] = ftype_record1["FTYPE_CODE"]
        else:
            sfcall_data["feature"] = "all"

        if felem_record1:
            sfcall_data["element"] = felem_record1["FELEM_CODE"]
        else:
            sfcall_data["element"] = "n/a"

        sfcall_data["execOrder"] = sfcall_record["EXEC_ORDER"]
        sfcall_data["function"] = sfunc_record["SFUNC_CODE"]

        return sfcall_data

    def do_addStandardizeCall(self, arg):
        """
        Add a new standardize call

        Syntax:
            addStandardizeCall {json_configuration}

        Examples:
            see listStandardizeCalls or getStandardizeCall for examples of json_configurations
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            if not parm_data.get("FUNCTION") and parm_data.get("STANDARDIZE"):
                parm_data["FUNCTION"] = parm_data["STANDARDIZE"]
            self.validate_parms(parm_data, ["FUNCTION"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["EXECORDER"] = parm_data.get("EXECORDER", 0)
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        sfcallID = self.getDesiredValueOrNext(
            "CFG_SFCALL", "SFCALL_ID", parm_data.get("ID"), seed_order=1000
        )
        if parm_data.get("ID") and sfcallID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        ftype_id = -1
        if parm_data.get("FEATURE") and parm_data.get("FEATURE").upper() != "ALL":
            ftype_record, message = self.lookupFeature(parm_data["FEATURE"].upper())
            if not ftype_record:
                colorize_msg(message, "error")
                return
            ftype_id = ftype_record["FTYPE_ID"]

        felemID = -1
        if parm_data.get("ELEMENT") and parm_data.get("ELEMENT").upper() != "N/A":
            felem_record, message = self.lookupElement(parm_data["ELEMENT"].upper())
            if not felem_record:
                colorize_msg(message, "error")
                return
            felemID = felem_record["FELEM_ID"]

        if (ftype_id > 0 and felemID > 0) or (ftype_id < 0 and felemID < 0):
            colorize_msg(
                "Either a feature or an element must be specified, but not both",
                "error",
            )
            return

        sfcallOrder = self.getDesiredValueOrNext(
            "CFG_SFCALL",
            ["FTYPE_ID", "FELEM_ID", "EXEC_ORDER"],
            [ftype_id, felemID, parm_data.get("EXECORDER")],
        )
        if parm_data["EXECORDER"] and sfcallOrder != parm_data["EXECORDER"]:
            colorize_msg(
                "The specified execution order for the feature/element is already taken",
                "error",
            )
            return

        sfunc_record, message = self.lookupStandardizeFunction(parm_data["FUNCTION"])
        if not sfunc_record:
            colorize_msg(message, "warning")
            return
        sfuncID = sfunc_record["SFUNC_ID"]

        newRecord = {}
        newRecord["SFCALL_ID"] = sfcallID
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["FELEM_ID"] = felemID
        newRecord["SFUNC_ID"] = sfuncID
        newRecord["EXEC_ORDER"] = sfcallOrder
        self.config_data["G2_CONFIG"]["CFG_SFCALL"].append(newRecord)
        self.config_updated = True
        colorize_msg("Standardize call successfully added!", "success")

    def do_listStandardizeCalls(self, arg):
        """
        Returns the list of standardize calls.

        Syntax:
            listStandardizeCalls [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for sfcall_record in sorted(
            self.get_record_list("CFG_SFCALL"),
            key=lambda k: (k["FTYPE_ID"], k["EXEC_ORDER"]),
        ):
            sfcall_json = self.format_standarize_call_json(sfcall_record)
            if arg and arg.lower() not in str(sfcall_json).lower():
                continue
            json_lines.append(sfcall_json)

        self.print_json_lines(json_lines)

    def do_getStandardizeCall(self, arg):
        """
        Returns a single standarization call

        Syntax:
            getStandardizeCall id or feature [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("standardize", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        self.print_json_record(self.format_standarize_call_json(call_record))

    def do_deleteStandardizeCall(self, arg):
        """
        Deletes a standardize call

        Syntax:
            deleteStandardizeCall id or feature
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("standardize", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        self.config_data["G2_CONFIG"]["CFG_SFCALL"].remove(call_record)
        colorize_msg("Standardize call successfully deleted!", "success")
        self.config_updated = True

    # ===== expression call commands =====

    def format_expression_call_json(self, efcall_record):
        efcall_id = efcall_record["EFCALL_ID"]

        ftype_record1 = self.get_record(
            "CFG_FTYPE", "FTYPE_ID", efcall_record["FTYPE_ID"]
        )
        felem_record1 = self.get_record(
            "CFG_FELEM", "FELEM_ID", efcall_record["FELEM_ID"]
        )

        efunc_record = self.get_record(
            "CFG_EFUNC", "EFUNC_ID", efcall_record["EFUNC_ID"]
        )
        efcall_data = {}
        efcall_data["id"] = efcall_id

        if ftype_record1:
            efcall_data["feature"] = ftype_record1["FTYPE_CODE"]
        else:
            efcall_data["feature"] = "all"

        if felem_record1:
            efcall_data["element"] = felem_record1["FELEM_CODE"]
        else:
            efcall_data["element"] = "n/a"

        efcall_data["execOrder"] = efcall_record["EXEC_ORDER"]
        efcall_data["function"] = efunc_record["EFUNC_CODE"]
        efcall_data["isVirtual"] = efcall_record["IS_VIRTUAL"]

        ftype_record2 = self.get_record(
            "CFG_FTYPE", "FTYPE_ID", efcall_record["EFEAT_FTYPE_ID"]
        )
        if ftype_record2:
            efcall_data["expressionFeature"] = ftype_record2["FTYPE_CODE"]
        else:
            efcall_data["expressionFeature"] = "n/a"

        efbom_list = []
        for efbom_record in sorted(
            self.get_record_list("CFG_EFBOM", "EFCALL_ID", efcall_id),
            key=lambda k: k["EXEC_ORDER"],
        ):
            ftype_record3 = self.get_record(
                "CFG_FTYPE", "FTYPE_ID", efbom_record["FTYPE_ID"]
            )
            felem_record3 = self.get_record(
                "CFG_FELEM", "FELEM_ID", efbom_record["FELEM_ID"]
            )

            efbom_data = {}
            efbom_data["order"] = efbom_record["EXEC_ORDER"]
            if efbom_record["FTYPE_ID"] == 0:
                efbom_data["featureLink"] = "parent"
            elif ftype_record3:
                efbom_data["feature"] = ftype_record3["FTYPE_CODE"]
            if felem_record3:
                efbom_data["element"] = felem_record3["FELEM_CODE"]
            else:
                efbom_data["element"] = str(efbom_record["FELEM_ID"])
            efbom_data["required"] = efbom_record["FELEM_REQ"]
            efbom_list.append(efbom_data)
        efcall_data["element_list"] = efbom_list

        return efcall_data

    def do_addExpressionCall(self, arg):
        """
        Add a new expression call

        Syntax:
            addExpressionCall {json_configuration}

        Examples:
            see listExpressionCalls or getExpressionCall for examples of json_configurations
        """

        # uncommon examples for testing ...
        # addExpressionCall {"element":"COUNTRY_CODE", "function":"FEAT_BUILDER", "execOrder":100, "expressionFeature":"COUNTRY_OF_ASSOCIATION", "virtual":"No","element_list": [{"element":"COUNTRY", "featureLink":"parent", "required":"No"}]}
        # addExpressionCall {"element":"COUNTRY_CODE", "function":"FEAT_BUILDER", "execOrder":101, "expressionFeature":"COUNTRY_OF_ASSOCIATION", "virtual":"No","element_list": [{"element":"COUNTRY", "feature":"ADDRESS", "required":"No"}]}

        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            if not parm_data.get("FUNCTION") and parm_data.get("EXPRESSION"):
                parm_data["FUNCTION"] = parm_data["EXPRESSION"]
            self.validate_parms(parm_data, ["FUNCTION", "ELEMENTLIST"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["EXECORDER"] = parm_data.get("EXECORDER", 0)
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        efcall_id = self.getDesiredValueOrNext(
            "CFG_EFCALL", "EFCALL_ID", parm_data.get("ID"), seed_order=1000
        )
        if parm_data.get("ID") and efcall_id != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        ftype_id = -1
        if parm_data.get("FEATURE") and parm_data.get("FEATURE").upper() != "ALL":
            ftype_record, message = self.lookupFeature(parm_data["FEATURE"].upper())
            if not ftype_record:
                colorize_msg(message, "error")
                return
            ftype_id = ftype_record["FTYPE_ID"]

        felemID = -1
        if parm_data.get("ELEMENT") and parm_data.get("ELEMENT").upper() != "N/A":
            felem_record, message = self.lookupElement(parm_data["ELEMENT"].upper())
            if not felem_record:
                colorize_msg(message, "error")
                return
            felemID = felem_record["FELEM_ID"]

        if (ftype_id > 0 and felemID > 0) or (ftype_id < 0 and felemID < 0):
            colorize_msg(
                "Either a feature or an element must be specified, but not both",
                "error",
            )
            return

        efcallOrder = self.getDesiredValueOrNext(
            "CFG_EFCALL",
            ["FTYPE_ID", "FELEM_ID", "EXEC_ORDER"],
            [ftype_id, felemID, parm_data.get("EXECORDER")],
        )
        if parm_data["EXECORDER"] and efcallOrder != parm_data["EXECORDER"]:
            colorize_msg(
                "The specified execution order for the feature/element is already taken",
                "error",
            )
            return

        efunc_record, message = self.lookupExpressionFunction(parm_data["FUNCTION"])
        if not efunc_record:
            colorize_msg(message, "warning")
            return
        efuncID = efunc_record["EFUNC_ID"]

        efeatFTypeID = -1
        if (
            parm_data.get("EXPRESSIONFEATURE")
            and parm_data.get("EXPRESSIONFEATURE").upper() != "N/A"
        ):
            ftype_record2, message = self.lookupFeature(
                parm_data["EXPRESSIONFEATURE"].upper()
            )
            if not ftype_record2:
                colorize_msg(message, "warning")
                return
            efeatFTypeID = ftype_record2["FTYPE_ID"]

        parm_data["ISVIRTUAL"], message = self.validateDomain(
            "Is virtual",
            parm_data.get("ISVIRTUAL", "No"),
            ["Yes", "No", "Any", "Desired"],
        )
        if not parm_data["ISVIRTUAL"]:
            colorize_msg(message, "error")
            return

        # ensure we have valid elements
        efbom_record_list = []
        execOrder = 0
        for element_data in parm_data["ELEMENTLIST"]:
            element_data = dict_keys_upper(element_data)
            execOrder += 1

            if element_data.get("FEATURELINK") == "parent":
                bom_ftype_id = 0
            else:
                bom_ftype_id = -1
                if (
                    element_data.get("FEATURE")
                    and element_data.get("FEATURE").upper() != "PARENT"
                ):
                    bom_ftype_record, message = self.lookupFeature(
                        element_data["FEATURE"].upper()
                    )
                    if not bom_ftype_record:
                        colorize_msg(message, "error")
                        return
                    else:
                        bom_ftype_id = bom_ftype_record["FTYPE_ID"]

            bom_felemID = -1
            if (
                element_data.get("ELEMENT")
                and element_data.get("ELEMENT").upper() != "N/A"
            ):
                if bom_ftype_id > 0:
                    bom_felem_record, message = self.lookupFeatureElement(
                        element_data.get("FEATURE").upper(),
                        element_data["ELEMENT"].upper(),
                    )
                else:
                    bom_felem_record, message = self.lookupElement(
                        element_data["ELEMENT"].upper()
                    )
                if not bom_felem_record:
                    colorize_msg(message, "error")
                    return
                else:
                    bom_felemID = bom_felem_record["FELEM_ID"]
            else:
                colorize_msg(
                    f"Element required in item {execOrder} on the element list", "error"
                )
                return

            element_data["REQUIRED"], message = self.validateDomain(
                "Element required", element_data.get("REQUIRED", "No"), ["Yes", "No"]
            )
            if not element_data["REQUIRED"]:
                colorize_msg(message, "error")
                return

            efbom_record = {}
            efbom_record["EFCALL_ID"] = efcall_id
            efbom_record["FTYPE_ID"] = bom_ftype_id
            efbom_record["FELEM_ID"] = bom_felemID
            efbom_record["EXEC_ORDER"] = execOrder
            efbom_record["FELEM_REQ"] = element_data["REQUIRED"]
            efbom_record_list.append(efbom_record)

        if len(efbom_record_list) == 0:
            colorize_msg("No elements were found in the element_list", "error")
            return

        newRecord = {}
        newRecord["EFCALL_ID"] = efcall_id
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["FELEM_ID"] = felemID
        newRecord["EFUNC_ID"] = efuncID
        newRecord["EXEC_ORDER"] = efcallOrder
        newRecord["EFEAT_FTYPE_ID"] = efeatFTypeID
        newRecord["IS_VIRTUAL"] = parm_data["ISVIRTUAL"]
        self.config_data["G2_CONFIG"]["CFG_EFCALL"].append(newRecord)
        self.config_data["G2_CONFIG"]["CFG_EFBOM"].extend(efbom_record_list)
        self.config_updated = True
        colorize_msg("Expression call successfully added!", "success")

    def do_listExpressionCalls(self, arg):
        """
        Returns the list of expression calls

        Syntax:
            listExpressionCalls [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for efcall_record in sorted(
            self.get_record_list("CFG_EFCALL"),
            key=lambda k: (k["FTYPE_ID"], k["FELEM_ID"], k["EXEC_ORDER"]),
        ):
            efcallJson = self.format_expression_call_json(efcall_record)
            if arg and arg.lower() not in str(efcallJson).lower():
                continue
            json_lines.append(efcallJson)

        self.print_json_lines(json_lines)

    def do_getExpressionCall(self, arg):
        """
        Returns a single expression call

        Syntax:
            getExpressionCall id or feature [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("expression", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        self.print_json_record(self.format_expression_call_json(call_record))

    def do_deleteExpressionCall(self, arg):
        """
        Deletes an expression call

        Syntax:
            deleteExpressionCall id
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("expression", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        for efbom_record in self.get_record_list(
            "CFG_EFBOM", "EFCALL_ID", call_record["EFCALL_ID"]
        ):
            self.config_data["G2_CONFIG"]["CFG_EFBOM"].remove(efbom_record)
        self.config_data["G2_CONFIG"]["CFG_EFCALL"].remove(call_record)
        colorize_msg("Expression call successfully deleted!", "success")
        self.config_updated = True

    def do_addExpressionCallElement(self, arg):
        """
        Add an additional feature/element to an existing expression call

        Syntax:
            addExpressionCallElement {json_configuration}

        Examples:
            addExpressionCallElement {"id": 14, "feature": "ACCT_NUM", "element": "ACCT_DOMAIN", "required": "Yes"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        self.addCallElement(add_attributes_to_arg(arg, add={"callType": "expression"}))

    # TODO Test this, didn't seem to work
    def do_deleteExpressionCallElement(self, arg):
        """
        Delete a feature/element from an existing expression call

        Syntax:
            deleteExpressionCallElement {json_configuration}

        Examples:
            deleteExpressionCallElement {"id": 14, "feature": "ACCT_NUM", "element": "ACCT_DOMAIN"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        self.delete_call_element(
            add_attributes_to_arg(arg, add={"callType": "expression"})
        )

    # ===== comparison call commands =====

    def format_comparison_calls_json(self, cfcall_record):
        cfcall_id = cfcall_record["CFCALL_ID"]
        ftype_record1 = self.get_record(
            "CFG_FTYPE", "FTYPE_ID", cfcall_record["FTYPE_ID"]
        )
        cfunc_record = self.get_record(
            "CFG_CFUNC", "CFUNC_ID", cfcall_record["CFUNC_ID"]
        )

        cfcall_data = {}
        cfcall_data["id"] = cfcall_id
        cfcall_data["feature"] = (
            ftype_record1["FTYPE_CODE"] if ftype_record1 else "error"
        )
        # cfcall_data['execOrder'] = cfcall_record['EXEC_ORDER']
        cfcall_data["function"] = (
            cfunc_record["CFUNC_CODE"] if cfunc_record else "error"
        )

        cfbom_list = []
        for cfbom_record in sorted(
            self.get_record_list("CFG_CFBOM", "CFCALL_ID", cfcall_id),
            key=lambda k: k["EXEC_ORDER"],
        ):
            # TODO Not used
            ftype_record3 = self.get_record(
                "CFG_FTYPE", "FTYPE_ID", cfbom_record["FTYPE_ID"]
            )
            felem_record3 = self.get_record(
                "CFG_FELEM", "FELEM_ID", cfbom_record["FELEM_ID"]
            )
            cfbom_data = {}
            cfbom_data["order"] = cfbom_record["EXEC_ORDER"]
            cfbom_data["element"] = (
                felem_record3["FELEM_CODE"] if felem_record3 else "error"
            )
            cfbom_list.append(cfbom_data)
        cfcall_data["element_list"] = cfbom_list

        return cfcall_data

    def do_addComparisonCall(self, arg):
        """
        Add a new comparison call

        Syntax:
            addComparisonCall {json_configuration}

        Examples:
            see listComparisonCalls or getComparisonCall for examples of json_configurations
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            if not parm_data.get("FUNCTION") and parm_data.get("COMPARISON"):
                parm_data["FUNCTION"] = parm_data["COMPARISON"]
            self.validate_parms(parm_data, ["FEATURE", "FUNCTION", "ELEMENTLIST"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        cfcall_id = self.getDesiredValueOrNext(
            "CFG_CFCALL", "CFCALL_ID", parm_data.get("ID"), seed_order=1000
        )
        if parm_data.get("ID") and cfcall_id != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
        if not ftype_record:
            colorize_msg(message, "error")
            return
        ftype_id = ftype_record["FTYPE_ID"]

        parm_data["EXECORDER"] = 1
        cfcall_record = self.get_record("CFG_CFCALL", "FTYPE_ID", ftype_id)
        if cfcall_record:
            colorize_msg(
                f"Comparison call for function {parm_data['FEATURE']} already set",
                "warning",
            )
            return

        cfunc_record, message = self.lookupComparisonFunction(parm_data["FUNCTION"])
        if not cfunc_record:
            colorize_msg(message, "warning")
            return
        cfuncID = cfunc_record["CFUNC_ID"]

        # ensure we have valid elements
        cfbom_record_list = []
        execOrder = 0
        for element_data in parm_data["ELEMENTLIST"]:
            element_data = dict_keys_upper(element_data)
            execOrder += 1

            bom_ftype_id = (
                ftype_id  # currently elements must belong to the calling feature
            )
            bom_felemID = -1
            if element_data.get("ELEMENT"):
                bom_felem_record, message = self.lookupFeatureElement(
                    parm_data["FEATURE"], element_data["ELEMENT"].upper()
                )
                if not bom_felem_record:
                    colorize_msg(message, "error")
                    return
                else:
                    bom_felemID = bom_felem_record["FELEM_ID"]
            else:
                colorize_msg(
                    f"Element required in item {execOrder} on the element list", "error"
                )
                return

            cfbom_record = {}
            cfbom_record["CFCALL_ID"] = cfcall_id
            cfbom_record["FTYPE_ID"] = bom_ftype_id
            cfbom_record["FELEM_ID"] = bom_felemID
            cfbom_record["EXEC_ORDER"] = execOrder
            cfbom_record_list.append(cfbom_record)

        if len(cfbom_record_list) == 0:
            colorize_msg("No elements were found in the element_list", "error")
            return

        newRecord = {}
        newRecord["CFCALL_ID"] = cfcall_id
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["CFUNC_ID"] = cfuncID
        newRecord["EXEC_ORDER"] = parm_data["EXECORDER"]
        self.config_data["G2_CONFIG"]["CFG_CFCALL"].append(newRecord)
        self.config_data["G2_CONFIG"]["CFG_CFBOM"].extend(cfbom_record_list)
        self.config_updated = True
        colorize_msg("Comparison call successfully added!", "success")

    def do_listComparisonCalls(self, arg):
        """
        Returns the list of comparison calls

        Syntax:
            listComparisonCalls [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        print(self.get_record_list("CFG_CFCALL"))
        for cfcall_record in sorted(
            self.get_record_list("CFG_CFCALL"),
            # key=lambda k: (k["FTYPE_ID"], k["EXEC_ORDER"]),
            # TODO Check order
            key=lambda k: (k["FTYPE_ID"], k["CFCALL_ID"]),
        ):
            cfcall_json = self.format_comparison_calls_json(cfcall_record)
            if arg and arg.lower() not in str(cfcall_json).lower():
                continue
            json_lines.append(cfcall_json)

        self.print_json_lines(json_lines)

    def do_getComparisonCall(self, arg):
        """
        Returns a single comparison call

        Syntax:
            getComparisonCall id or feature [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("comparison", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        self.print_json_record(self.format_comparison_calls_json(call_record))

    def do_deleteComparisonCall(self, arg):
        """
        Deletes a comparison call

        Syntax:
            deleteComparisonCall id
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("comparison", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        for cfbom_record in self.get_record_list(
            "CFG_CFBOM", "CFCALL_ID", call_record["CFCALL_ID"]
        ):
            self.config_data["G2_CONFIG"]["CFG_CFBOM"].remove(cfbom_record)
        self.config_data["G2_CONFIG"]["CFG_CFCALL"].remove(call_record)
        colorize_msg("Comparison call successfully deleted!", "success")
        self.config_updated = True

    def do_addComparisonCallElement(self, arg):
        """
        Add an additional feature/element to an existing comparison call

        Syntax:
            addComparisonCallElement {json_configuration}

        Examples:
            addComparisonCallElement {"id": 16, "feature": "ACCT_NUM", "element": "ACCT_DOMAIN"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        self.addCallElement(add_attributes_to_arg(arg, add={"callType": "comparison"}))

    def do_deleteComparisonCallElement(self, arg):
        """
        Delete a feature/element from an existing comparison call

        Syntax:
            deleteComparisonCallElement {json_configuration}

        Examples:
            deleteComparisonCallElement {"id": 16, "feature": "ACCT_NUM", "element": "ACCT_DOMAIN"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        self.delete_call_element(
            add_attributes_to_arg(arg, add={"callType": "comparison"})
        )

    # ===== distinct call commands =====

    def format_distinct_call_json(self, dfcall_record):
        dfcall_id = dfcall_record["DFCALL_ID"]
        ftype_record1 = self.get_record(
            "CFG_FTYPE", "FTYPE_ID", dfcall_record["FTYPE_ID"]
        )
        dfunc_record = self.get_record(
            "CFG_DFUNC", "DFUNC_ID", dfcall_record["DFUNC_ID"]
        )

        dfcall_data = {}
        dfcall_data["id"] = dfcall_id
        dfcall_data["feature"] = (
            ftype_record1["FTYPE_CODE"] if ftype_record1 else "error"
        )
        # dfcall_data['execOrder'] = dfcall_record['EXEC_ORDER']
        dfcall_data["function"] = (
            dfunc_record["DFUNC_CODE"] if dfunc_record else "error"
        )

        dfbom_list = []
        for dfbom_record in sorted(
            self.get_record_list("CFG_DFBOM", "DFCALL_ID", dfcall_id),
            key=lambda k: k["EXEC_ORDER"],
        ):
            # TODO Not used?
            ftype_record3 = self.get_record(
                "CFG_FTYPE", "FTYPE_ID", dfbom_record["FTYPE_ID"]
            )
            felem_record3 = self.get_record(
                "CFG_FELEM", "FELEM_ID", dfbom_record["FELEM_ID"]
            )
            cfbom_data = {}
            cfbom_data["order"] = dfbom_record["EXEC_ORDER"]
            cfbom_data["element"] = (
                felem_record3["FELEM_CODE"] if felem_record3 else "error"
            )
            dfbom_list.append(cfbom_data)
        dfcall_data["element_list"] = dfbom_list

        return dfcall_data

    def do_addDistinctCall(self, arg):
        """
        Add a new distinct call

        Syntax:
            addDistinctCall {json_configuration}

        Examples:
            see listDistinctCalls or getDistinctCall for examples of json_configurations
        """

        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE", "FUNCTION", "ELEMENTLIST"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        dfcall_id = self.getDesiredValueOrNext(
            "CFG_DFCALL", "DFCALL_ID", parm_data.get("ID"), seed_order=1000
        )
        if parm_data.get("ID") and dfcall_id != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
        if not ftype_record:
            colorize_msg(message, "error")
            return
        ftype_id = ftype_record["FTYPE_ID"]

        parm_data["EXECORDER"] = 1
        dfcall_record = self.get_record("CFG_DFCALL", "FTYPE_ID", ftype_id)
        if dfcall_record:
            colorize_msg(
                f"Distinct call for function {parm_data['FEATURE']} already set",
                "warning",
            )
            return

        dfunc_record, message = self.lookupDistinctFunction(parm_data["FUNCTION"])
        if not dfunc_record:
            colorize_msg(message, "warning")
            return
        dfuncID = dfunc_record["DFUNC_ID"]

        # ensure we have valid elements
        dfbom_record_list = []
        execOrder = 0
        for element_data in parm_data["ELEMENTLIST"]:
            element_data = dict_keys_upper(element_data)
            execOrder += 1

            bom_ftype_id = (
                ftype_id  # currently elements must belong to the calling feature
            )
            bom_felemID = -1
            if element_data.get("ELEMENT"):
                bom_felem_record, message = self.lookupFeatureElement(
                    parm_data["FEATURE"], element_data["ELEMENT"].upper()
                )
                if not bom_felem_record:
                    colorize_msg(message, "error")
                    return
                else:
                    bom_felemID = bom_felem_record["FELEM_ID"]
            else:
                colorize_msg(
                    f"Element required in item {execOrder} on the element list", "error"
                )
                return

            dfbom_record = {}
            dfbom_record["DFCALL_ID"] = dfcall_id
            dfbom_record["FTYPE_ID"] = bom_ftype_id
            dfbom_record["FELEM_ID"] = bom_felemID
            dfbom_record["EXEC_ORDER"] = execOrder
            dfbom_record_list.append(dfbom_record)

        if len(dfbom_record_list) == 0:
            colorize_msg("No elements were found in the element_list", "error")
            return

        newRecord = {}
        newRecord["DFCALL_ID"] = dfcall_id
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["DFUNC_ID"] = dfuncID
        newRecord["EXEC_ORDER"] = parm_data["EXECORDER"]
        self.config_data["G2_CONFIG"]["CFG_DFCALL"].append(newRecord)
        self.config_data["G2_CONFIG"]["CFG_DFBOM"].extend(dfbom_record_list)
        self.config_updated = True
        colorize_msg("Distinct call successfully added!", "success")

    def do_listDistinctCalls(self, arg):
        """
        Returns the list of distinct calls

        Syntax:
            listDistinctCalls [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for dfcall_record in sorted(
            self.get_record_list("CFG_DFCALL"),
            # key=lambda k: (k["FTYPE_ID"], k["EXEC_ORDER"]),
            # TODO Order ok?
            key=lambda k: (k["FTYPE_ID"], k["DFCALL_ID"]),
        ):
            dfcallJson = self.format_distinct_call_json(dfcall_record)
            if arg and arg.lower() not in str(dfcallJson).lower():
                continue
            json_lines.append(dfcallJson)

        self.print_json_lines(json_lines)

    def do_getDistinctCall(self, arg):
        """
        Returns a single distinct call

        Syntax:
            getDistinctCall id or feature [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("distinct", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        self.print_json_record(self.format_distinct_call_json(call_record))

    def do_deleteDistinctCall(self, arg):
        """
        Deletes a distintness call

        Syntax:
            deleteDistinctCall id
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        call_record, message = self.prep_call_record("distinct", arg)
        if not call_record:
            colorize_msg(message, "error")
            return

        for dfbom_record in self.get_record_list(
            "CFG_DFBOM", "DFCALL_ID", call_record["DFCALL_ID"]
        ):
            self.config_data["G2_CONFIG"]["CFG_DFBOM"].remove(dfbom_record)
        self.config_data["G2_CONFIG"]["CFG_DFCALL"].remove(call_record)
        colorize_msg("Distinct call successfully deleted!", "success")
        self.config_updated = True

    def do_addDistinctCallElement(self, arg):
        """
        Add an additional feature/element to an existing distinct call

        Syntax:
            addDistinctCallElement {json_configuration}

        Examples:
            addDistinctCallElement {"id": 16, "feature": "ACCT_NUM", "element": "ACCT_DOMAIN"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        self.addCallElement(add_attributes_to_arg(arg, add={"callType": "distinct"}))

    def do_deleteDistinctCallElement(self, arg):
        """
        Delete a feature/element from an existing distinct call

        Syntax:
            deleteDistinctCallElement {json_configuration}

        Examples:
            deleteDistinctCallElement {"id": 16, "feature": "ACCT_NUM", "element": "ACCT_DOMAIN"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        self.delete_call_element(
            add_attributes_to_arg(arg, add={"callType": "distinct"})
        )

    # ===== convenience call functions =====

    def do_addToNamehash(self, arg):
        """
        Add an additional feature/element to the list composite name keys

        Example:
            addToNamehash {"feature": "ADDRESS", "element": "STR_NUM"}

        Notes:
            This command appends an additional feature and element to the name hasher function.
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ELEMENT"])
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        parm_data["CALLTYPE"] = "expression"
        call_id, message = self.getCallID("NAME", parm_data["CALLTYPE"], "NAME_HASHER")
        if not call_id:
            colorize_msg(message, "error")
            return

        parm_data["ID"] = call_id
        self.addCallElement(json.dumps(parm_data))

    # TODO Check this
    def do_deleteFromNamehash(self, arg):
        """
        Delete a feature element from the list composite name keys

        Example:
            deleteFromNamehash {"feature": "ADDRESS", "element": "STR_NUM"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ELEMENT"])
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        parm_data["CALLTYPE"] = "expression"
        call_id, message = self.getCallID("NAME", parm_data["CALLTYPE"], "NAME_HASHER")
        if not call_id:
            colorize_msg(message, "error")
            return

        parm_data["ID"] = call_id
        self.delete_call_element(json.dumps(parm_data))

    # ===== feature behavior overrides =====

    def formatBehaviorOverrideJson(self, behavior_record):
        ftype_code = self.get_record(
            "CFG_FTYPE", "FTYPE_ID", behavior_record["FTYPE_ID"]
        )["FTYPE_CODE"]

        return {
            "feature": ftype_code,
            "usageType": behavior_record["UTYPE_CODE"],
            "behavior": getFeatureBehavior(behavior_record),
        }

    def do_listBehaviorOverrides(self, arg):
        """
        Returns the list of feature behavior overrides

        Syntax:
            listBehaviorOverrides [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for behavior_record in sorted(
            self.get_record_list("CFG_FBOVR"),
            key=lambda k: (k["FTYPE_ID"], k["UTYPE_CODE"]),
        ):
            behaviorJson = self.formatBehaviorOverrideJson(behavior_record)
            if arg and arg.lower() not in str(behaviorJson).lower():
                continue
            json_lines.append(behaviorJson)

        self.print_json_lines(json_lines)

    def do_addBehaviorOverride(self, arg):
        """
        Add a new behavior override

        Syntax:
            addBehaviorOverride {json_configuration}

        Examples:
            see listBehaviorOverrides for examples of json_configurations
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE", "USAGETYPE", "BEHAVIOR"])
            parm_data["FEATURE"] = parm_data["FEATURE"].upper()
            parm_data["USAGETYPE"] = parm_data["USAGETYPE"].upper()
            parm_data["BEHAVIOR"] = parm_data["BEHAVIOR"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
        if not ftype_record:
            colorize_msg(message, "error")
            return
        ftype_id = ftype_record["FTYPE_ID"]

        behaviorData, message = self.lookupBehaviorCode(parm_data["BEHAVIOR"])
        if not behaviorData:
            colorize_msg(message, "error")
            return

        if self.get_record(
            "CFG_FBOVR", ["FTYPE_ID", "UTYPE_CODE"], [ftype_id, parm_data["USAGETYPE"]]
        ):
            colorize_msg("Behavior override already exists", "warning")
            return

        newRecord = {}
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["ECLASS_ID"] = 0
        newRecord["UTYPE_CODE"] = parm_data["USAGETYPE"]
        newRecord["FTYPE_FREQ"] = behaviorData["FREQUENCY"]
        newRecord["FTYPE_EXCL"] = behaviorData["EXCLUSIVITY"]
        newRecord["FTYPE_STAB"] = behaviorData["STABILITY"]

        self.config_data["G2_CONFIG"]["CFG_FBOVR"].append(newRecord)
        colorize_msg("Behavior override successfully added!", "success")
        self.config_updated = True

    def do_deleteBehaviorOverride(self, arg):
        """
        Deletes a behavior override

        Example:
            deleteBehaviorOverride {"feature": "PHONE", "usageType": "MOBILE"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FEATURE", "USAGETYPE"])
            parm_data["USAGETYPE"] = parm_data["USAGETYPE"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
        if not ftype_record:
            colorize_msg(message, "error")
            return
        ftype_id = ftype_record["FTYPE_ID"]

        behavior_record = self.get_record(
            "CFG_FBOVR", ["FTYPE_ID", "UTYPE_CODE"], [ftype_id, parm_data["USAGETYPE"]]
        )
        if not behavior_record:
            colorize_msg("Behavior override does not exist", "warning")
            return

        self.config_data["G2_CONFIG"]["CFG_FBOVR"].remove(behavior_record)
        colorize_msg("Behavior override successfully deleted!", "success")
        self.config_updated = True

    # ===== generic plan commands =====

    def do_listGenericPlans(self, arg):
        """
        Returns the list of generic threshold plans

        Syntax:
            listGenericPlans [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for plan_record in sorted(
            self.get_record_list("CFG_GPLAN"), key=lambda k: k["GPLAN_ID"]
        ):
            if arg and arg.lower() not in str(plan_record).lower():
                continue
            json_lines.append(
                {
                    "id": plan_record["GPLAN_ID"],
                    "plan": plan_record["GPLAN_CODE"],
                    "description": plan_record["GPLAN_DESC"],
                }
            )

        self.print_json_lines(json_lines)

    def do_cloneGenericPlan(self, arg):
        """
        Create a new generic plan based on an existing one

        Examples:
            cloneGenericPlan {"existingPlan": "SEARCH", "newPlan": "SEARCH-EXHAUSTIVE", "description": "Exhaustive search"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["EXISTINGPLAN", "NEWPLAN"])
            parm_data["EXISTINGPLAN"] = parm_data["EXISTINGPLAN"].upper()
            parm_data["NEWPLAN"] = parm_data["NEWPLAN"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        plan_record1, message = self.lookupGenericPlan(parm_data["EXISTINGPLAN"])
        if not plan_record1:
            colorize_msg(message, "warning")
            return

        plan_record2, message = self.lookupGenericPlan(parm_data["NEWPLAN"])
        if plan_record2:
            colorize_msg(message, "warning")
            return

        next_id = self.getDesiredValueOrNext("CFG_GPLAN", "GPLAN_ID", 0)

        newRecord = {}
        newRecord["GPLAN_ID"] = next_id
        newRecord["GPLAN_CODE"] = parm_data["NEWPLAN"]
        newRecord["GPLAN_DESC"] = parm_data.get("DESCRIPTION", parm_data["NEWPLAN"])

        self.config_data["G2_CONFIG"]["CFG_GPLAN"].append(newRecord)
        for threshold_record in self.get_record_list(
            "CFG_GENERIC_THRESHOLD", "GPLAN_ID", plan_record1["GPLAN_ID"]
        ):
            newRecord = dict(threshold_record)
            newRecord["GPLAN_ID"] = next_id
            self.config_data["G2_CONFIG"]["CFG_GENERIC_THRESHOLD"].append(newRecord)
        self.config_updated = True
        colorize_msg("Generic plan successfully added!", "success")

    def do_deleteGenericPlan(self, arg):
        """
        Delete an existing generic threshold plan

        Syntax:
            deleteGenericPlan [code or id]

        Caution:
            Plan IDs 1 and 2 are required by the system and cannot be deleted!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "PLAN", "GPLAN_ID", "GPLAN_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        plan_record = self.get_record("CFG_GPLAN", search_field, search_value)
        if not plan_record:
            colorize_msg("Generic plan not found", "warning")
            return
        if plan_record["GPLAN_ID"] <= 2:
            colorize_msg(
                f"The {plan_record['GPLAN_CODE']} plan cannot be deleted", "error"
            )
            return

        self.config_data["G2_CONFIG"]["CFG_GPLAN"].remove(plan_record)
        for threshold_record in self.get_record_list(
            "CFG_GENERIC_THRESHOLD", "GPLAN_ID", plan_record["GPLAN_ID"]
        ):
            self.config_data["G2_CONFIG"]["CFG_GENERIC_THRESHOLD"].remove(
                threshold_record
            )
        colorize_msg("Generic plan successfully deleted!", "success")
        self.config_updated = True

    # ===== generic threshold commands =====

    def format_generic_threshold_json(self, threshold_record):
        gplanCode = self.get_record(
            "CFG_GPLAN", "GPLAN_ID", threshold_record["GPLAN_ID"]
        )["GPLAN_CODE"]
        if threshold_record.get("FTYPE_ID", 0) != 0:
            ftype_code = self.get_record(
                "CFG_FTYPE", "FTYPE_ID", threshold_record["FTYPE_ID"]
            )["FTYPE_CODE"]
        else:
            ftype_code = "all"

        return {
            "plan": gplanCode,
            "behavior": threshold_record["BEHAVIOR"],
            "feature": ftype_code,
            "candidateCap": threshold_record["CANDIDATE_CAP"],
            "scoringCap": threshold_record["SCORING_CAP"],
            "sendToRedo": threshold_record["SEND_TO_REDO"],
        }

    def do_listGenericThresholds(self, arg):
        """
        Returns the list of generic thresholds

        Syntax:
            listGenericThresholds [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for threshold_record in sorted(
            self.get_record_list("CFG_GENERIC_THRESHOLD"),
            key=lambda k: (
                k["GPLAN_ID"],
                self.valid_behavior_codes.index(k["BEHAVIOR"]),
            ),
        ):
            threshold_json = self.format_generic_threshold_json(threshold_record)
            if arg and arg.lower() not in str(threshold_json).lower():
                continue
            json_lines.append(threshold_json)

        self.print_json_lines(json_lines)

    def validateGenericThreshold(self, record):
        errorList = []

        behaviorData, message = self.lookupBehaviorCode(record["BEHAVIOR"])
        if not behaviorData:
            errorList.append(message)

        record["SENDTOREDO"], message = self.validateDomain(
            "sendToRedo", record.get("SEND_TO_REDO"), ["Yes", "No"]
        )
        if not record["SENDTOREDO"]:
            errorList.append(message)

        if not isinstance(record["CANDIDATE_CAP"], int):
            errorList.append("candidateCap must be an integer")

        if not isinstance(record["SCORING_CAP"], int):
            errorList.append("scoringCap must be an integer")

        if errorList:
            print(colorize("\nThe following errors were detected:", "bad"))
            for message in errorList:
                print(colorize(f"- {message}", "bad"))
            record = None

        return record

    def do_addGenericThreshold(self, arg):
        """
        Add a new generic threshold

        Syntax:
            addGenericThreshold {json_configuration}

        Examples:
            see listGenericThresholds for examples of json_configurations
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(
                parm_data,
                ["PLAN", "BEHAVIOR", "SCORINGCAP", "CANDIDATECAP", "SENDTOREDO"],
            )
            parm_data["PLAN"] = parm_data["PLAN"].upper()
            parm_data["BEHAVIOR"] = parm_data["BEHAVIOR"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        gplan_record, message = self.lookupGenericPlan(parm_data["PLAN"])
        if not gplan_record:
            colorize_msg(message, "error")
            return
        gplan_id = gplan_record["GPLAN_ID"]

        ftype_id = 0
        if parm_data.get("FEATURE") and parm_data.get("FEATURE") != "all":
            ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
            if not ftype_record:
                colorize_msg(message, "error")
                return
            ftype_id = ftype_record["FTYPE_ID"]

        if self.get_record(
            "CFG_GENERIC_THRESHOLD",
            ["GPLAN_ID", "BEHAVIOR", "FTYPE_ID"],
            [gplan_id, parm_data["BEHAVIOR"], ftype_id],
        ):
            colorize_msg("Generic threshold already exists", "warning")
            return

        newRecord = {}
        newRecord["GPLAN_ID"] = gplan_id
        newRecord["BEHAVIOR"] = parm_data["BEHAVIOR"]
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["CANDIDATE_CAP"] = parm_data["CANDIDATECAP"]
        newRecord["SCORING_CAP"] = parm_data["SCORINGCAP"]
        newRecord["SEND_TO_REDO"] = parm_data["SENDTOREDO"]
        newRecord = self.validateGenericThreshold(newRecord)
        if not newRecord:
            return

        self.config_data["G2_CONFIG"]["CFG_GENERIC_THRESHOLD"].append(newRecord)
        colorize_msg("Generic threshold successfully added!", "success")
        self.config_updated = True

    def do_setGenericThreshold(self, arg):
        """
        Sets the comparison thresholds for a particular comparison threshold ID

        Syntax:
            setGenericThreshold {partial_json_configuration}

        Example:
            setGenericThreshold {"plan": "SEARCH", "feature": "all", "behavior": "NAME", "candidateCap": 500}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["PLAN", "BEHAVIOR"])
            parm_data["PLAN"] = parm_data["PLAN"].upper()
            parm_data["BEHAVIOR"] = parm_data["BEHAVIOR"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        gplan_record, message = self.lookupGenericPlan(parm_data["PLAN"])
        if not gplan_record:
            colorize_msg(message, "error")
            return
        gplan_id = gplan_record["GPLAN_ID"]

        ftype_id = 0
        if parm_data.get("FEATURE") and parm_data.get("FEATURE") != "all":
            ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
            if not ftype_record:
                colorize_msg(message, "error")
                return
            ftype_id = ftype_record["FTYPE_ID"]

        old_record = self.get_record(
            "CFG_GENERIC_THRESHOLD",
            ["GPLAN_ID", "BEHAVIOR", "FTYPE_ID"],
            [gplan_id, parm_data["BEHAVIOR"], ftype_id],
        )
        if not old_record:
            colorize_msg("Generic threshold not found", "warning")
            return

        oldParmData = dict_keys_upper(self.format_generic_threshold_json(old_record))
        newParmData = self.settable_parms(
            oldParmData, parm_data, ("SENDTOREDO", "CANDIDATECAP", "SCORINGCAP")
        )
        if newParmData.get("errors"):
            colorize_msg(newParmData["errors"], "error")
            return
        if newParmData["update_cnt"] == 0:
            colorize_msg("No changes detected", "warning")
            return

        print(newParmData)
        newRecord = dict(old_record)
        newRecord["CANDIDATE_CAP"] = newParmData.get(
            "CANDIDATECAP", newRecord["CANDIDATE_CAP"]
        )
        newRecord["SCORING_CAP"] = newParmData.get(
            "SCORINGCAP", newRecord["SCORING_CAP"]
        )
        newRecord["SEND_TO_REDO"] = newParmData.get(
            "SENDTOREDO", newRecord["SEND_TO_REDO"]
        )
        newRecord = self.validateGenericThreshold(newRecord)
        if not newRecord:
            return

        self.config_data["G2_CONFIG"]["CFG_GENERIC_THRESHOLD"].remove(old_record)
        self.config_data["G2_CONFIG"]["CFG_GENERIC_THRESHOLD"].append(newRecord)
        colorize_msg("Generic threshold successfully updated!", "success")
        self.config_updated = True

    # TODO Chexk this
    def do_deleteGenericThreshold(self, arg):
        """
        Deletes a generic threshold record

        Example:
            deleteGenericThreshold {"plan": "search", "feature": "all", "behavior": "NAME"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["PLAN", "BEHAVIOR"])
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        gplan_record, message = self.lookupGenericPlan(parm_data["PLAN"])
        if not gplan_record:
            colorize_msg(message, "error")
            return
        gplan_id = gplan_record["GPLAN_ID"]

        ftype_id = 0
        if parm_data.get("FEATURE") and parm_data.get("FEATURE") != "all":
            ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
            if not ftype_record:
                colorize_msg(message, "error")
                return
            ftype_id = ftype_record["FTYPE_ID"]

        old_record = self.get_record(
            "CFG_GENERIC_THRESHOLD",
            ["GPLAN_ID", "BEHAVIOR", "FTYPE_ID"],
            [gplan_id, parm_data["BEHAVIOR"], ftype_id],
        )
        if not old_record:
            colorize_msg("Generic threshold not found", "warning")
            return

        self.config_data["G2_CONFIG"]["CFG_GENERIC_THRESHOLD"].remove(old_record)
        colorize_msg("Generic threshold successfully deleted!", "success")
        self.config_updated = True

    # ===== fragment commands =====

    def format_fragment_json(self, record):
        return {
            "id": record["ERFRAG_ID"],
            "fragment": record["ERFRAG_CODE"],
            "source": record["ERFRAG_SOURCE"],
            "depends": record["ERFRAG_DEPENDS"],
        }

    def validateFragmentSource(self, sourceString):
        # compute dependencies from source
        # example: './FRAGMENT[./SAME_NAME>0 and ./SAME_STAB>0] or ./FRAGMENT[./SAME_NAME1>0 and ./SAME_STAB1>0]'
        dependencyList = []
        startPos = sourceString.find("FRAGMENT[")
        while startPos > 0:
            fragmentString = sourceString[
                startPos : sourceString.find("]", startPos) + 1
            ]
            sourceString = sourceString.replace(fragmentString, "")
            # parse the fragment string
            currentFrag = "eof"
            fragmentChars = list(fragmentString)
            potentialErrorString = ""
            for thisChar in fragmentChars:
                potentialErrorString += thisChar
                if thisChar == "/":
                    currentFrag = ""
                elif currentFrag != "eof":
                    if thisChar in "| =><)":
                        # lookup the fragment code
                        fragRecord = self.get_record(
                            "CFG_ERFRAG", "ERFRAG_CODE", currentFrag
                        )
                        if not fragRecord:
                            return [], f"Invalid fragment reference: {currentFrag}"
                        else:
                            dependencyList.append(str(fragRecord["ERFRAG_ID"]))
                        currentFrag = "eof"
                    else:
                        currentFrag += thisChar
            # next list of fragments
            startPos = sourceString.find("FRAGMENT[")
        return dependencyList, ""

    def do_addFragment(self, arg):
        """
        Adds a new rule fragment

        Syntax:
            addFragment {json_configuration}

        Examples:
            see listFragments or getFragment for examples of json configurations
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FRAGMENT", "SOURCE"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FRAGMENT"] = parm_data["FRAGMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if self.get_record("CFG_ERFRAG", "ERFRAG_CODE", parm_data["FRAGMENT"]):
            colorize_msg("Fragment already exists", "warning")
            return

        erfragID = self.getDesiredValueOrNext(
            "CFG_ERFRAG", "ERFRAG_ID", parm_data.get("ID")
        )
        if parm_data.get("ID") and erfragID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        if parm_data.get("DEPENDS"):
            colorize_msg(
                "Depends setting ignored as it is calculated by the system", "warning"
            )

        dependencyList, error_message = self.validateFragmentSource(parm_data["SOURCE"])
        if error_message:
            colorize_msg(error_message, "error")
            return

        newRecord = {}
        newRecord["ERFRAG_ID"] = erfragID
        newRecord["ERFRAG_CODE"] = parm_data["FRAGMENT"]
        newRecord["ERFRAG_DESC"] = parm_data["FRAGMENT"]
        newRecord["ERFRAG_SOURCE"] = parm_data["SOURCE"]
        newRecord["ERFRAG_DEPENDS"] = (
            ",".join(dependencyList) if dependencyList else None
        )
        self.config_data["G2_CONFIG"]["CFG_ERFRAG"].append(newRecord)
        self.config_updated = True
        colorize_msg("Fragment successfully added!", "success")

    def do_setFragment(self, arg):
        """
        Sets configuration parameters for an existing feature

        Syntax:
            setFragment {partial_json_configuration}

        Examples:
            setFragment {"fragment": "GNR_ORG_NAME", "source": "./SCORES/NAME[./GNR_ON>=90]"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            if not parm_data.get("ID") and not parm_data.get("FRAGMENT"):
                raise ValueError("Either ID or FRAGMENT must be supplied")
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        old_record, message = self.lookupFragment(
            parm_data["ID"] if parm_data.get("ID") else parm_data["FRAGMENT"].upper()
        )
        if not old_record:
            colorize_msg(message, "warning")
            return

        oldParmData = dict_keys_upper(self.format_fragment_json(old_record))
        settable_parm_list = "SOURCE"
        newParmData = self.settable_parms(oldParmData, parm_data, settable_parm_list)
        if newParmData.get("errors"):
            colorize_msg(newParmData["errors"], "error")
            return
        if newParmData["update_cnt"] == 0:
            colorize_msg("No changes detected", "warning")
            return

        newRecord = dict(old_record)  # must use dict to create a new instance
        dependencyList, error_message = self.validateFragmentSource(parm_data["SOURCE"])
        if error_message:
            colorize_msg(error_message, "error")
            return

        newRecord["ERFRAG_SOURCE"] = parm_data["SOURCE"]
        newRecord["ERFRAG_DEPENDS"] = (
            ",".join(dependencyList) if dependencyList else None
        )
        self.config_data["G2_CONFIG"]["CFG_ERFRAG"].remove(old_record)
        self.config_data["G2_CONFIG"]["CFG_ERFRAG"].append(newRecord)
        colorize_msg("Fragment successfully updated!", "success")
        self.config_updated = True

    def do_listFragments(self, arg):
        """
        Returns the list of rule fragments.

        Syntax:
            listFragments [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for fragment_record in sorted(
            self.get_record_list("CFG_ERFRAG"), key=lambda k: k["ERFRAG_ID"]
        ):
            fragmentJson = self.format_fragment_json(fragment_record)
            if arg and arg.lower() not in str(fragmentJson).lower():
                continue
            json_lines.append(fragmentJson)

        self.print_json_lines(json_lines)

    def do_getFragment(self, arg):
        """
        Returns a single rule fragment

        Syntax:
            getFragment [code or id] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "FRAGMENT", "ERFRAG_ID", "ERFRAG_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        fragment_record = self.get_record("CFG_ERFRAG", search_field, search_value)
        if not fragment_record:
            colorize_msg("Fragment does not exist", "warning")
            return
        self.print_json_record(self.format_fragment_json(fragment_record))

    def do_deleteFragment(self, arg):
        """
        Deletes a rule fragment

        Syntax:
            deleteFragment [code or id]
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "FRAGMENT", "ERFRAG_ID", "ERFRAG_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        fragment_record = self.get_record("CFG_ERFRAG", search_field, search_value)
        if not fragment_record:
            colorize_msg("Fragment does not exist", "warning")
            return

        self.config_data["G2_CONFIG"]["CFG_ERFRAG"].remove(fragment_record)
        colorize_msg("Fragment successfully deleted!", "success")
        self.config_updated = True

    # ===== rule commands =====

    def format_rule_json(self, record):
        print(record)
        return {
            "id": record["ERRULE_ID"],
            "rule": record["ERRULE_CODE"],
            # "desc": record["ERRULE_DESC"],
            "resolve": record["RESOLVE"],
            "relate": record["RELATE"],
            # "ref_score": record["REF_SCORE"],
            "rtype_id": record["RTYPE_ID"],
            "fragment": record["QUAL_ERFRAG_CODE"],
            "disqualifier": record["DISQ_ERFRAG_CODE"],
            "tier": record["ERRULE_TIER"] if record["RESOLVE"] == "Yes" else None,
        }

    def validateRule(self, record):

        erfragRecord, message = self.lookupFragment(record["QUAL_ERFRAG_CODE"])
        if not erfragRecord:
            colorize_msg(message, "error")
            return None

        if record.get("DISQ_ERFRAG_CODE"):
            dqfragRecord, message = self.lookupFragment(record["DISQ_ERFRAG_CODE"])
            if not dqfragRecord:
                colorize_msg(message, "error")
                return None

        record["RESOLVE"], message = self.validateDomain(
            "resolve", record.get("RESOLVE", "No"), ["Yes", "No"]
        )
        if not record["RESOLVE"]:
            colorize_msg(message, "error")
            return None

        record["RELATE"], message = self.validateDomain(
            "relate", record.get("RELATE", "No"), ["Yes", "No"]
        )
        if not record["RELATE"]:
            colorize_msg(message, "error")
            return None

        if record["RESOLVE"] == "Yes" and record["RELATE"] == "Yes":
            colorize_msg(
                "A rule must either resolve or relate, please set the other to No",
                "error",
            )
            return None

        tier = record.get("ERRULE_TIER")
        rtypeID = record.get("RTYPE_ID")

        if record["RESOLVE"] == "Yes":
            if not tier:
                colorize_msg(
                    "A tier matching other rules that could be considered ambiguous to this one must be specified",
                    "error",
                )
                return None

            if rtypeID != 1:
                # just do it without making them wonder
                # colorize_msg('Relationship type (RTYPE_ID) was forced to 1 for resolve rule', 'warning')
                record["RTYPE_ID"] = 1

        if record["RELATE"] == "Yes":
            # leave tier as is as they may change back to resolve and don't want to lose its original setting
            # if tier:
            #     colorize_msg('A tier is not required for relate rules', 'error')
            if rtypeID not in (2, 3, 4):
                colorize_msg(
                    "Relationship type (RTYPE_ID) must be set to either 2=Possible match or 3=Possibly related",
                    "error",
                )
                return None
        return record

    def do_addRule(self, arg):
        """
        Adds a new rule (aka principle)

        Syntax:
            addRule {json_configuration}

        Examples:
            see listRules or getRule for examples of json configurations
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(
                parm_data, ["ID", "RULE", "FRAGMENT", "RESOLVE", "RELATE", "RTYPE_ID"]
            )
            parm_data["RULE"] = parm_data["RULE"].upper()
            parm_data["FRAGMENT"] = parm_data["FRAGMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if self.get_record("CFG_ERRULE", "ERRULE_CODE", parm_data["RULE"]):
            colorize_msg("Rule already exists", "warning")
            return

        erruleID = self.getDesiredValueOrNext(
            "CFG_ERRULE", "ERRULE_ID", parm_data.get("ID")
        )
        if parm_data.get("ID") and erruleID != parm_data["ID"]:
            colorize_msg("The specified ID is already taken", "error")
            return

        newRecord = {}
        newRecord["ERRULE_ID"] = parm_data["ID"]
        newRecord["ERRULE_CODE"] = parm_data["RULE"]
        newRecord["ERRULE_DESC"] = parm_data.get("DESC", parm_data["RULE"])
        newRecord["RESOLVE"] = parm_data["RESOLVE"]
        newRecord["RELATE"] = parm_data["RELATE"]
        newRecord["REF_SCORE"] = parm_data.get("REF_SCORE", 0)
        newRecord["RTYPE_ID"] = parm_data["RTYPE_ID"]
        newRecord["QUAL_ERFRAG_CODE"] = parm_data["FRAGMENT"]
        newRecord["DISQ_ERFRAG_CODE"] = parm_data.get("DISQUALIFIER")
        newRecord["ERRULE_TIER"] = parm_data.get("TIER")

        newRecord = self.validateRule(newRecord)
        if not newRecord:
            # colorize_msg('Rule not added', 'error')
            return

        self.config_data["G2_CONFIG"]["CFG_ERRULE"].append(newRecord)
        self.config_updated = True
        colorize_msg("Rule successfully added!", "success")

    def do_setRule(self, arg):
        """
        Syntax:
            setRule {partial json configuration}

        Examples:
            setRule {"id": 111, "resolve": "No"}
            setRule {"id": 111, "relate": "Yes", "rtype_id": 2}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ID"])
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        old_record, message = self.lookupRule(parm_data["ID"])
        if not old_record:
            colorize_msg(message, "warning")
            return

        oldParmData = dict_keys_upper(self.format_rule_json(old_record))
        settable_parm_list = (
            "RULE",
            "DESC",
            "RESOLVE",
            "RELATE",
            "REF_SCORE",
            "RTYPE_ID",
            "FRAGMENT",
            "DISQUALIFIER",
            "TIER",
        )
        newParmData = self.settable_parms(oldParmData, parm_data, settable_parm_list)
        if newParmData.get("errors"):
            colorize_msg(newParmData["errors"], "error")
            return
        if newParmData["update_cnt"] == 0:
            colorize_msg("No changes detected", "warning")
            return

        newRecord = dict(old_record)  # must use dict to create a new instance
        newRecord["ERRULE_CODE"] = parm_data.get("RULE", newRecord["ERRULE_CODE"])
        newRecord["ERRULE_DESC"] = parm_data.get("DESC", newRecord["ERRULE_DESC"])
        newRecord["RESOLVE"] = parm_data.get("RESOLVE", newRecord["RESOLVE"])
        newRecord["RELATE"] = parm_data.get("RELATE", newRecord["RELATE"])
        newRecord["REF_SCORE"] = parm_data.get("REF_SCORE", newRecord["REF_SCORE"])
        newRecord["RTYPE_ID"] = parm_data.get("RTYPE_ID", newRecord["RTYPE_ID"])
        newRecord["QUAL_ERFRAG_CODE"] = parm_data.get(
            "FRAGMENT", newRecord["QUAL_ERFRAG_CODE"]
        )
        newRecord["DISQ_ERFRAG_CODE"] = parm_data.get(
            "DISQUALIFIER", newRecord["DISQ_ERFRAG_CODE"]
        )
        newRecord["ERRULE_TIER"] = parm_data.get("TIER", newRecord["ERRULE_TIER"])

        newRecord = self.validateRule(newRecord)
        if not newRecord:
            # colorize_msg('Rule not updated', 'error')
            return

        self.config_data["G2_CONFIG"]["CFG_ERRULE"].remove(old_record)
        self.config_data["G2_CONFIG"]["CFG_ERRULE"].append(newRecord)
        colorize_msg("Rule successfully updated!", "success")
        self.config_updated = True

    def do_listRules(self, arg):
        """
        Returns the list of rules (aka principles)

        Syntax:
            listRules [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)

        json_lines = []
        for rule_record in sorted(
            self.get_record_list("CFG_ERRULE"), key=lambda k: k["ERRULE_ID"]
        ):
            rules_json = self.format_rule_json(rule_record)
            if arg and arg.lower() not in str(rules_json).lower():
                continue
            json_lines.append(rules_json)

        self.print_json_lines(json_lines)

    def do_getRule(self, arg):
        """
        Returns a single rule (aka principle)

        Syntax:
            getRule [code or id] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("record", arg)
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "RULE", "ERRULE_ID", "ERRULE_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        rule_record = self.get_record("CFG_ERRULE", search_field, search_value)
        if not rule_record:
            colorize_msg("Rule does not exist", "warning")
            return
        self.print_json_record(self.format_rule_json(rule_record))

    def do_deleteRule(self, arg):
        """
        Deletes a rule (aka principle)

        Syntax:
            deleteRule [code or id]
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            search_value, search_field = self.id_or_code_parm(
                arg, "ID", "RULE", "ERRULE_ID", "ERRULE_CODE"
            )
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        rule_record = self.get_record("CFG_ERRULE", search_field, search_value)
        if not rule_record:
            colorize_msg("Rule does not exist", "warning")
            return

        self.config_data["G2_CONFIG"]["CFG_ERRULE"].remove(rule_record)
        colorize_msg("Rule successfully deleted!", "success")
        self.config_updated = True

    # ===== supporting codes =====

    def do_listReferenceCodes(self, arg):
        # TODO are the notes still correct?
        """
        Returns the list of internal reference codes

        Syntax:
            listReferenceCodes [code_type] [table|json|jsonl]

        Notes:
            reference code types include:
                matchLevels
                behaviorCodes
                featureClasses
                attributeClasses
        """
        arg = self.check_arg_for_output_format("list", arg)
        if arg:
            arg = arg.upper()

        if not arg or arg in "MATCHLEVELS":
            json_lines = []
            for rtype_record in sorted(
                self.get_record_list("CFG_RTYPE"), key=lambda k: k["RTYPE_ID"]
            ):
                if arg and arg.lower() not in str(rtype_record).lower():
                    continue
                json_lines.append(
                    {
                        "level": rtype_record["RTYPE_ID"],
                        "code": rtype_record["RTYPE_CODE"],
                        "class": self.get_record(
                            "CFG_RCLASS", "RCLASS_ID", rtype_record["RCLASS_ID"]
                        )["RCLASS_DESC"],
                    }
                )
            self.print_json_lines(json_lines, "Match Levels")

        if not arg or arg in "BEHAVIORCODES":
            json_lines = []
            for code in self.valid_behavior_codes:
                if code == "NAME":
                    desc = "Controlled behavior used only for names"
                elif code == "NONE":
                    desc = "No behavior"
                else:
                    if code.startswith("A1"):
                        desc = "Absolutely 1"
                    elif code.startswith("F1"):
                        desc = "Frequency 1"
                    elif code.startswith("FF"):
                        desc = "Frequency 1"
                    elif code.startswith("FM"):
                        desc = "Frequency many"
                    elif code.startswith("FVM"):
                        desc = "Frequency very many"
                    else:
                        desc = "unknown"
                    if "E" in code:
                        desc += ", exclusive"
                    if "S" in code:
                        desc += " and stable"
                json_lines.append({"behaviorCode": code, "behaviorDescription": desc})
            self.print_json_lines(json_lines, "Behavior Codes")

        if not arg or arg in "FEATURECLASS":
            json_lines = []
            for fclass_record in sorted(
                self.get_record_list("CFG_FCLASS"), key=lambda k: k["FCLASS_ID"]
            ):
                json_lines.append(
                    {
                        "class": fclass_record["FCLASS_CODE"],
                        "id": fclass_record["FCLASS_ID"],
                    }
                )
            self.print_json_lines(json_lines, "Feature Classes")

        if not arg or arg in "ATTRIBUTECLASS":
            json_lines = []
            for attr_class in self.attribute_class_list:
                json_lines.append({"attributeClass": attr_class})
            self.print_json_lines(json_lines, "Attribute Classes")

    # standardize functions

    def do_addStandardizeFunction(self, arg):
        """
        Adds a new standardize function

        Syntax:
            addStandardizeFunction {json_configuration}

        Examples:
            see listStandardizeFunctions for examples of json_configurations

        Caution:
            Adding a new function requires a plugin to be programmed!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FUNCTION"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if self.get_record("CFG_SFUNC", "SFUNC_CODE", parm_data["FUNCTION"]):
            colorize_msg("Function already exists", "warning")
            return

        sfuncID = self.getDesiredValueOrNext(
            "CFG_SFUNC", "SFUNC_ID", parm_data.get("ID")
        )
        if parm_data.get("ID") and sfuncID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        parm_data["FUNCLIB"] = parm_data.get("FUNCLIB", "g2func_lib")
        parm_data["VERSION"] = parm_data.get("VERSION", 1)
        parm_data["CONNECTSTR"] = parm_data.get("CONNECTSTR", None)
        parm_data["LANGUAGE"] = parm_data.get("LANGUAGE", None)
        parm_data["JAVACLASSNAME"] = parm_data.get("JAVACLASSNAME", None)

        newRecord = {}
        newRecord["SFUNC_ID"] = sfuncID
        newRecord["SFUNC_CODE"] = parm_data["FUNCTION"]
        newRecord["SFUNC_DESC"] = parm_data["FUNCTION"]
        newRecord["FUNC_LIB"] = parm_data["FUNCLIB"]
        newRecord["FUNC_VER"] = parm_data["VERSION"]
        newRecord["CONNECT_STR"] = parm_data["CONNECTSTR"]
        newRecord["LANGUAGE"] = parm_data["LANGUAGE"]
        newRecord["JAVA_CLASS_NAME"] = parm_data["JAVACLASSNAME"]
        self.config_data["G2_CONFIG"]["CFG_SFUNC"].append(newRecord)
        self.config_updated = True
        colorize_msg("Standardize function successfully added!", "success")

    def do_listStandardizeFunctions(self, arg):
        """
        Returns the list of standardize functions

        Syntax:
            listStandardizeFunctions [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for func_record in sorted(
            self.get_record_list("CFG_SFUNC"), key=lambda k: k["SFUNC_ID"]
        ):
            if arg and arg.lower() not in str(func_record).lower():
                continue
            json_lines.append(
                {
                    "id": func_record["SFUNC_ID"],
                    "function": func_record["SFUNC_CODE"],
                    "connectStr": func_record["CONNECT_STR"],
                    "language": func_record["LANGUAGE"],
                    "javaClassName": func_record["JAVA_CLASS_NAME"],
                }
            )

        if json_lines:
            self.print_json_lines(json_lines)

    # expression functions

    def do_addExpressionFunction(self, arg):
        """
        Adds a new expression function

        Syntax:
            addExpressionFunction {json_configuration}

        Examples:
            see listExpressionFunctions for examples of json_configurations

        Caution:
            Adding a new function requires a plugin to be programmed!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FUNCTION"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if self.get_record("CFG_EFUNC", "EFUNC_CODE", parm_data["FUNCTION"]):
            colorize_msg("Function already exists", "warning")
            return

        efuncID = self.getDesiredValueOrNext(
            "CFG_EFUNC", "EFUNC_ID", parm_data.get("ID")
        )
        if parm_data.get("ID") and efuncID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        parm_data["FUNCLIB"] = parm_data.get("FUNCLIB", "g2func_lib")
        parm_data["VERSION"] = parm_data.get("VERSION", 1)
        parm_data["CONNECTSTR"] = parm_data.get("CONNECTSTR", None)
        parm_data["LANGUAGE"] = parm_data.get("LANGUAGE", None)
        parm_data["JAVACLASSNAME"] = parm_data.get("JAVACLASSNAME", None)

        newRecord = {}
        newRecord["EFUNC_ID"] = efuncID
        newRecord["EFUNC_CODE"] = parm_data["FUNCTION"]
        newRecord["EFUNC_DESC"] = parm_data["FUNCTION"]
        newRecord["FUNC_LIB"] = parm_data["FUNCLIB"]
        newRecord["FUNC_VER"] = parm_data["VERSION"]
        newRecord["CONNECT_STR"] = parm_data["CONNECTSTR"]
        newRecord["LANGUAGE"] = parm_data["LANGUAGE"]
        newRecord["JAVA_CLASS_NAME"] = parm_data["JAVACLASSNAME"]

        self.config_data["G2_CONFIG"]["CFG_EFUNC"].append(newRecord)
        self.config_updated = True
        colorize_msg("Expression function successfully added!", "success")

    def do_listExpressionFunctions(self, arg):
        """
        Returns the list of expression functions

        Syntax:
            listExpressionFuncstions [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for func_record in sorted(
            self.get_record_list("CFG_EFUNC"), key=lambda k: k["EFUNC_ID"]
        ):
            if arg and arg.lower() not in str(func_record).lower():
                continue
            json_lines.append(
                {
                    "id": func_record["EFUNC_ID"],
                    "function": func_record["EFUNC_CODE"],
                    # "version": func_record["FUNC_VER"],
                    "connectStr": func_record["CONNECT_STR"],
                    "language": func_record["LANGUAGE"],
                    "javaClassName": func_record["JAVA_CLASS_NAME"],
                }
            )

        if json_lines:
            self.print_json_lines(json_lines)

        return

    # comparison functions

    def do_addComparisonFunction(self, arg):
        """
        Adds a new comparison function

        Syntax:
            addComparisonFunction {json_configuration}

        Examples:
            see listComparisonFunctions for examples of json_configurations

        Caution:
            Adding a new function requires a plugin to be programmed!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FUNCTION"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if self.get_record("CFG_CFUNC", "CFUNC_CODE", parm_data["FUNCTION"]):
            colorize_msg("Function already exists", "warning")
            return

        cfuncID = self.getDesiredValueOrNext(
            "CFG_CFUNC", "CFUNC_ID", parm_data.get("ID")
        )
        if parm_data.get("ID") and cfuncID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        parm_data["FUNCLIB"] = parm_data.get("FUNCLIB", "g2func_lib")
        parm_data["VERSION"] = parm_data.get("VERSION", 1)
        parm_data["ANONSUPPORT"] = parm_data.get("ANONSUPPORT", "No")
        parm_data["CONNECTSTR"] = parm_data.get("CONNECTSTR", None)
        parm_data["LANGUAGE"] = parm_data.get("LANGUAGE", None)
        parm_data["JAVACLASSNAME"] = parm_data.get("JAVACLASSNAME", None)

        newRecord = {}
        newRecord["CFUNC_ID"] = cfuncID
        newRecord["CFUNC_CODE"] = parm_data["FUNCTION"]
        newRecord["CFUNC_DESC"] = parm_data["FUNCTION"]
        newRecord["FUNC_LIB"] = parm_data["FUNCLIB"]
        newRecord["FUNC_VER"] = parm_data["VERSION"]
        newRecord["CONNECT_STR"] = parm_data["CONNECTSTR"]
        newRecord["ANON_SUPPORT"] = parm_data["ANONSUPPORT"]
        newRecord["LANGUAGE"] = parm_data["LANGUAGE"]
        newRecord["JAVA_CLASS_NAME"] = parm_data["JAVACLASSNAME"]
        self.config_data["G2_CONFIG"]["CFG_CFUNC"].append(newRecord)
        self.config_updated = True
        colorize_msg("Comparison function successfully added!", "success")

    def do_listComparisonFunctions(self, arg):
        """
        Returns the list of comparison functions

        Syntax:
            listComparisonFunctions [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for func_record in sorted(
            self.get_record_list("CFG_CFUNC"), key=lambda k: k["CFUNC_ID"]
        ):
            if arg and arg.lower() not in str(func_record).lower():
                continue
            json_lines.append(
                {
                    "id": func_record["CFUNC_ID"],
                    "function": func_record["CFUNC_CODE"],
                    "connectStr": func_record["CONNECT_STR"],
                    "anonSupport": func_record["ANON_SUPPORT"],
                    "language": func_record["LANGUAGE"],
                    "javaClassName": func_record["JAVA_CLASS_NAME"],
                }
            )
        if json_lines:
            self.print_json_lines(json_lines)

        return

    # comparison thresholds

    def format_comparison_threshold_json(self, cfrtn_record):

        func_record = self.get_record("CFG_CFUNC", "CFUNC_ID", cfrtn_record["CFUNC_ID"])
        if cfrtn_record.get("FTYPE_ID", 0) != 0:
            ftype_code = self.get_record(
                "CFG_FTYPE", "FTYPE_ID", cfrtn_record["FTYPE_ID"]
            )["FTYPE_CODE"]
        else:
            ftype_code = "all"
        return {
            "id": cfrtn_record["CFRTN_ID"],
            "function": func_record["CFUNC_CODE"],
            "returnOrder": cfrtn_record["EXEC_ORDER"],
            "scoreName": cfrtn_record["CFUNC_RTNVAL"],
            "feature": ftype_code,
            "sameScore": cfrtn_record["SAME_SCORE"],
            "closeScore": cfrtn_record["CLOSE_SCORE"],
            "likelyScore": cfrtn_record["LIKELY_SCORE"],
            "plausibleScore": cfrtn_record["PLAUSIBLE_SCORE"],
            "unlikelyScore": cfrtn_record["UN_LIKELY_SCORE"],
        }

    def do_addComparisonThreshold(self, arg):
        """
        Adds a new comparison function threshold setting

        Syntax:
            addComparisonThreshold {json_configuration}

        Notes:
            You can override the comparison thresholds for specific features by specifying the feature instead of all.
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FUNCTION", "SCORENAME"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FEATURE"] = parm_data.get("FEATURE", "ALL")
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
            parm_data["SCORENAME"] = parm_data["SCORENAME"].upper()
            parm_data["SAMESCORE"] = int(parm_data.get("SAMESCORE", 100))
            parm_data["CLOSESCORE"] = int(parm_data.get("CLOSESCORE", 90))
            parm_data["LIKELYSCORE"] = int(parm_data.get("LIKELYSCORE", 80))
            parm_data["PLAUSIBLESCORE"] = int(parm_data.get("PLAUSIBLESCORE", 70))
            parm_data["UNLIKELYSCORE"] = int(parm_data.get("UNLIKELYSCORE", 60))
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        cfrtnID = self.getDesiredValueOrNext(
            "CFG_CFRTN", "CFRTN_ID", parm_data.get("ID")
        )
        if parm_data.get("ID") and cfrtnID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        cfunc_record, message = self.lookupComparisonFunction(parm_data["FUNCTION"])
        if not cfunc_record:
            colorize_msg(message, "warning")
            return
        cfuncID = cfunc_record["CFUNC_ID"]

        ftype_id = 0
        if "FEATURE" in parm_data and parm_data["FEATURE"].upper() != "ALL":
            ftype_record, message = self.lookupFeature(parm_data["FEATURE"])
            if not ftype_record:
                colorize_msg(message, "error")
                return
            ftype_id = ftype_record["FTYPE_ID"]

        cfcall_record = self.get_record(
            "CFG_CFRTN",
            ["CFUNC_ID", "CFUNC_RTNVAL", "FTYPE_ID"],
            [cfuncID, parm_data["SCORENAME"], ftype_id],
        )
        if cfcall_record:
            colorize_msg(
                f"Comparison threshold function: {parm_data['FUNCTION']}, return code: {parm_data['SCORENAME']} for feature {parm_data['FEATURE']} already set",
                "warning",
            )
            return

        # see if the return value already has an exec order and use it! must be in the expected order
        cfcall_record = self.get_record(
            "CFG_CFRTN",
            ["CFUNC_ID", "CFUNC_RTNVAL", "FTYPE_ID"],
            [cfuncID, parm_data["SCORENAME"], 0],
        )
        if cfcall_record:
            execOrder = cfcall_record["EXEC_ORDER"]
        elif parm_data.get("EXECORDER"):
            execOrder = parm_data.get("EXECORDER")
        else:
            execOrder = self.getDesiredValueOrNext(
                "CFG_CFRTN", ["CFUNC_ID", "FTYPE_ID", "EXEC_ORDER"], [cfuncID, 0, 0]
            )

        newRecord = {}
        newRecord["CFRTN_ID"] = cfrtnID
        newRecord["CFUNC_ID"] = cfuncID
        newRecord["FTYPE_ID"] = ftype_id
        newRecord["CFUNC_RTNVAL"] = parm_data["SCORENAME"]
        newRecord["EXEC_ORDER"] = execOrder
        newRecord["SAME_SCORE"] = parm_data["SAMESCORE"]
        newRecord["CLOSE_SCORE"] = parm_data["CLOSESCORE"]
        newRecord["LIKELY_SCORE"] = parm_data["LIKELYSCORE"]
        newRecord["PLAUSIBLE_SCORE"] = parm_data["PLAUSIBLESCORE"]
        newRecord["UN_LIKELY_SCORE"] = parm_data["UNLIKELYSCORE"]
        self.config_data["G2_CONFIG"]["CFG_CFRTN"].append(newRecord)
        self.config_updated = True
        colorize_msg("Comparison threshold successfully added!", "success")

    def do_setComparisonThreshold(self, arg):
        """
        Sets the comparison thresholds for a particular comparison threshold ID

        Syntax:
            setComparisonThreshold {partial_json_configuration}

        Example:
            setComparisonThreshold {"id": 9, "sameScore": 100, "closeScore": 92, "likelyScore": 90, "plausibleScore": 85, "unlikelyScore": 75}

        Notes:
            Only the scores can be changed here.
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ID"])
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        old_record = self.get_record("CFG_CFRTN", "CFRTN_ID", parm_data["ID"])
        if not old_record:
            colorize_msg("Comparison threshold ID not found", "error")
            return

        oldParmData = dict_keys_upper(self.format_comparison_threshold_json(old_record))
        settable_parm_list = (
            "RETURNORDER",
            "SAMESCORE",
            "CLOSESCORE",
            "LIKELYSCORE",
            "PLAUSIBLESCORE",
            "UNLIKELYSCORE",
        )
        newParmData = self.settable_parms(oldParmData, parm_data, settable_parm_list)
        if newParmData.get("errors"):
            colorize_msg(newParmData["errors"], "error")
            return
        if newParmData["update_cnt"] == 0:
            colorize_msg("No changes detected", "warning")
            return

        newRecord = dict(old_record)  # must use dict to create a new instance
        newRecord["EXEC_ORDER"] = parm_data["RETURNORDER"]
        newRecord["SAME_SCORE"] = parm_data["SAMESCORE"]
        newRecord["CLOSE_SCORE"] = parm_data["CLOSESCORE"]
        newRecord["LIKELY_SCORE"] = parm_data["LIKELYSCORE"]
        newRecord["PLAUSIBLE_SCORE"] = parm_data["PLAUSIBLESCORE"]
        newRecord["UN_LIKELY_SCORE"] = parm_data["UNLIKELYSCORE"]

        self.config_data["G2_CONFIG"]["CFG_CFRTN"].remove(old_record)
        self.config_data["G2_CONFIG"]["CFG_CFRTN"].append(newRecord)
        colorize_msg("Comparison threshold successfully updated!", "success")
        self.config_updated = True

    def do_listComparisonThresholds(self, arg):
        """
        Returns the list of thresholds by comparison function return value

        Syntax:
            listComparisonThresholds [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for cfrtn_record in sorted(
            self.get_record_list("CFG_CFRTN"),
            key=lambda k: (k["CFUNC_ID"], k["CFRTN_ID"]),
        ):
            cfrtnJson = self.format_comparison_threshold_json(cfrtn_record)
            if arg and arg.lower() not in str(cfrtnJson).lower():
                continue
            json_lines.append(cfrtnJson)
        if json_lines:
            self.print_json_lines(json_lines)
        print()

    def do_deleteComparisonThreshold(self, arg):
        """
        Deletes a comparision threshold

        Syntax:
           deleteComparisonThreshold id
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = (
                dict_keys_upper(json.loads(arg))
                if arg.startswith("{")
                else {"ID": int(arg)}
            )
            parm_data["ID"] = (
                int(parm_data["ID"])
                if isinstance(parm_data["ID"], str) and parm_data["ID"].isdigit()
                else parm_data["ID"]
            )
            self.validate_parms(parm_data, ["ID"])
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        cfrtn_record = self.get_record("CFG_CFRTN", "CFRTN_ID", parm_data["ID"])
        if not cfrtn_record:
            colorize_msg(
                f"Comparison threshold ID {parm_data['ID']} does not exist", "warning"
            )
            return

        self.config_data["G2_CONFIG"]["CFG_CFRTN"].remove(cfrtn_record)
        colorize_msg("Comparison threshold successfully deleted!", "success")
        self.config_updated = True

    # distinct functions

    def do_listDistinctFunctions(self, arg):
        """
        Returns the list of distinct functions

        Syntax:
            listDistinctFunctions [filter_expression] [table|json|jsonl]
        """
        arg = self.check_arg_for_output_format("list", arg)
        json_lines = []
        for func_record in sorted(
            self.get_record_list("CFG_DFUNC"), key=lambda k: k["DFUNC_ID"]
        ):
            if arg and arg.lower() not in str(func_record).lower():
                continue
            json_lines.append(
                {
                    "id": func_record["DFUNC_ID"],
                    "function": func_record["DFUNC_CODE"],
                    "connectStr": func_record["CONNECT_STR"],
                    "anonSupport": func_record["ANON_SUPPORT"],
                    "language": func_record["LANGUAGE"],
                    "javaClassName": func_record["JAVA_CLASS_NAME"],
                }
            )

        if json_lines:
            self.print_json_lines(json_lines)

    def do_addDistinctFunction(self, arg):
        """
        Adds a new distinct function

        Syntax:
            addDistinctFunction {json_configuration}

        Examples:
            see listDistinctFunctions for examples of json_configurations

        Caution:
            Adding a new function requires a plugin to be programmed!
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["FUNCTION"])
            parm_data["ID"] = parm_data.get("ID", 0)
            parm_data["FUNCTION"] = parm_data["FUNCTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if self.get_record("CFG_DFUNC", "DFUNC_CODE", parm_data["FUNCTION"]):
            colorize_msg("Function already exists", "warning")
            return

        dfuncID = self.getDesiredValueOrNext(
            "CFG_DFUNC", "DFUNC_ID", parm_data.get("ID")
        )
        if parm_data.get("ID") and dfuncID != parm_data["ID"]:
            colorize_msg(
                "The specified ID is already taken (remove it to assign the next available)",
                "error",
            )
            return

        parm_data["FUNCLIB"] = parm_data.get("FUNCLIB", "g2func_lib")
        parm_data["VERSION"] = parm_data.get("VERSION", 1)
        parm_data["CONNECTSTR"] = parm_data.get("CONNECTSTR", None)
        parm_data["ANONSUPPORT"] = parm_data.get("ANONSUPPORT", None)
        parm_data["LANGUAGE"] = parm_data.get("LANGUAGE", None)
        parm_data["JAVACLASSNAME"] = parm_data.get("JAVACLASSNAME", None)

        newRecord = {}
        newRecord["DFUNC_ID"] = dfuncID
        newRecord["DFUNC_CODE"] = parm_data["FUNCTION"]
        newRecord["DFUNC_DESC"] = parm_data["FUNCTION"]
        newRecord["FUNC_LIB"] = parm_data["FUNCLIB"]
        newRecord["FUNC_VER"] = parm_data["VERSION"]
        newRecord["ANON_SUPPORT"] = parm_data["ANONSUPPORT"]
        newRecord["CONNECT_STR"] = parm_data["CONNECTSTR"]
        newRecord["LANGUAGE"] = parm_data["LANGUAGE"]
        newRecord["JAVA_CLASS_NAME"] = parm_data["JAVACLASSNAME"]
        self.config_data["G2_CONFIG"]["CFG_DFUNC"].append(newRecord)
        self.config_updated = True
        colorize_msg("Distinct function successfully added!", "success")

    # ===== other miscellaneous functions =====

    # Compatibility version commands

    def do_verifyCompatibilityVersion(self, arg):
        """
        Verify if the current configuration is compatible with a specific version number

        Examples:
            verifyCompatibilityVersion {"expectedVersion": "2"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        this_version = self.config_data["G2_CONFIG"]["CONFIG_BASE_VERSION"][
            "COMPATIBILITY_VERSION"
        ]["CONFIG_VERSION"]
        if this_version != parm_data["EXPECTEDVERSION"]:
            colorize_msg(f"Incompatible! This is version {this_version}", "error")
            if self.is_interactive is False:
                raise Exception("Incorrect compatibility version.")
        else:
            colorize_msg("Compatibility version successfully verified", "success")

    def do_updateCompatibilityVersion(self, arg):
        """
        Update the compatiblilty version of this configuration

        Examples:
            updateCompatibilityVersion {"fromVersion": "1", "toVersion": "2"}
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        this_version = self.config_data["G2_CONFIG"]["CONFIG_BASE_VERSION"][
            "COMPATIBILITY_VERSION"
        ]["CONFIG_VERSION"]
        if this_version != parm_data["FROMVERSION"]:
            colorize_msg(
                f"From version mismatch. This is version {this_version}", "error"
            )
            return

        self.config_data["G2_CONFIG"]["CONFIG_BASE_VERSION"]["COMPATIBILITY_VERSION"][
            "CONFIG_VERSION"
        ] = parm_data["TOVERSION"]
        self.config_updated = True
        colorize_msg("Compatibility version successfully updated!", "success")

    def do_getCompatibilityVersion(self, arg):
        """
        Retrieve the compatiblity version of this configuration

        Syntax:
            getCompatibilityVersion
        """
        try:
            this_version = self.config_data["G2_CONFIG"]["CONFIG_BASE_VERSION"][
                "COMPATIBILITY_VERSION"
            ]["CONFIG_VERSION"]
            colorize_msg(f"Compatibility version is {this_version}", "success")
        except KeyError:
            colorize_msg("Could not retrieve compatibility version", "error")

    # ===== config sections =====

    def do_getConfigSection(self, arg):
        # TODO Says json but can be others too
        # TODO Why say only Sz enginners can use this?
        """
        Returns the json configuration for a specific configuration table

        Syntax:
            getConfigSection [section name] [filter_expression] [table|json|jsonl]

        Examples:
            getConfigSection CFG_CFUNC

        Caution:
            This command should only be used by Senzing engineers
        """
        arg = self.check_arg_for_output_format(
            "list", arg
        )  # checking for list here even though a get
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return

        section_name = arg.split()[0]
        filter_str = None
        if len(arg.split()) > 1:
            filter_str = arg.replace(section_name, "").strip()
            print(f"\nfilter: {filter_str}\n")

        if self.config_data["G2_CONFIG"].get(section_name):
            if not filter_str:
                self.print_json_lines(self.config_data["G2_CONFIG"][section_name])
            else:
                output_rows = []
                for record in self.config_data["G2_CONFIG"][section_name]:
                    if filter_str.lower() in json.dumps(record).lower():
                        output_rows.append(record)
                self.print_json_lines(output_rows)
        elif section_name in self.config_data["G2_CONFIG"]:
            colorize_msg("Configuration section is empty", "warning")
        else:
            colorize_msg("Configuration section not found", "error")

    def do_addConfigSection(self, arg):
        """
        Adds a new configuration section

        Syntax:
            addConfigSection {json_configuration}

        Caution:
            This command should only be used by Senzing engineers
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = (
                dict_keys_upper(json.loads(arg))
                if arg.startswith("{")
                else {"SECTION": arg}
            )
            self.validate_parms(parm_data, ["SECTION"])
            parm_data["SECTION"] = parm_data["SECTION"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if parm_data["SECTION"] in self.config_data["G2_CONFIG"]:
            colorize_msg("Configuration section already exists!", "error")
            return

        self.config_data["G2_CONFIG"][parm_data["SECTION"]] = []
        self.config_updated = True
        colorize_msg("Configuration section successfully added!", "success")

    def do_addConfigSectionField(self, arg):
        """
        Adds a new field to an existing configuration section

        Syntax:
            addConfigSectionField {json_configuration}

        Caution:
            This command should only be used by Senzing engineers
        """
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["SECTION", "FIELD", "VALUE"])
            parm_data["SECTION"] = parm_data["SECTION"].upper()
            parm_data["FIELD"] = parm_data["FIELD"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        if parm_data["SECTION"] not in self.config_data["G2_CONFIG"]:
            colorize_msg("Configuration section does not exist", "error")
            return

        # update every record that needs it
        existed_cnt = updated_cnt = 0
        for i in range(len(self.config_data["G2_CONFIG"][parm_data["SECTION"]])):
            if (
                parm_data["FIELD"]
                in self.config_data["G2_CONFIG"][parm_data["SECTION"]][i]
            ):
                existed_cnt += 1
            else:
                self.config_data["G2_CONFIG"][parm_data["SECTION"]][i][
                    parm_data["FIELD"]
                ] = parm_data["VALUE"]
                updated_cnt += 1

        if existed_cnt > 0:
            colorize_msg(f"Field already existed on {existed_cnt} records", "warning")
        if updated_cnt > 0:
            self.config_updated = True
            colorize_msg(
                f"Configuration section field successfully added to {updated_cnt} records!",
                "success",
            )

    # ===== system parameters  =====

    def do_listSystemParameters(self, arg):
        """\nlistSystemParameters\n"""

        for i in self.config_data["G2_CONFIG"]["CFG_RTYPE"]:
            if i["RCLASS_ID"] == 2:
                print(f'\n{{"relationshipsBreakMatches": "{i["BREAK_RES"]}"}}\n')
                break

    def do_setSystemParameter(self, arg):
        """\nsetSystemParameter {"parameter": "<value>"}\n"""

        validParameters = "relationshipsBreakMatches"
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = json.loads(arg)  # don't want these upper
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        # not really expecting a list here, getting the dictionary key they used
        for parameterCode in parm_data:
            parameterValue = parm_data[parameterCode]

            if parameterCode not in validParameters:
                colorize_msg("%s is an invalid system parameter" % parameterCode, "B")

            # set all disclosed relationship types to break or not break matches
            elif parameterCode == "relationshipsBreakMatches":
                if parameterValue.upper() in ("YES", "Y"):
                    breakRes = 1
                elif parameterValue.upper() in ("NO", "N"):
                    breakRes = 0
                else:
                    colorize_msg(
                        "%s is an invalid parameter for %s"
                        % (parameterValue, parameterCode),
                        "B",
                    )
                    return

                for i in range(len(self.config_data["G2_CONFIG"]["CFG_RTYPE"])):
                    if self.config_data["G2_CONFIG"]["CFG_RTYPE"][i]["RCLASS_ID"] == 2:
                        self.config_data["G2_CONFIG"]["CFG_RTYPE"][i][
                            "BREAK_RES"
                        ] = breakRes
                        self.config_updated = True

    def do_touch(self, arg):
        """\nMarks configuration object as modified when no configuration changes have been applied yet.\n"""

        # This is a no-op. It marks the configuration as modified, without doing anything to it.
        self.config_updated = True
        print()

    # ===== Deprecated/replaced commands =====

    def print_replacement(self, old, new):
        print(
            colorize(
                f"\n{old[3:]} has been replaced, please use {new[3:]} in the future.\n",
                "dim,italics",
            )
        )

    def do_addStandardizeFunc(self, arg):
        self.do_addStandardizeFunction(arg)
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_addStandardizeFunction"
        )

    def do_addExpressionFunc(self, arg):
        self.do_addExpressionFunction(arg)
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_addExpressionFunction"
        )

    def do_addComparisonFunc(self, arg):
        self.do_addComparisonFunction(arg)
        self.print_replacement(sys._getframe(0).f_code.co_name, "do_addComparisonFunc")

    def do_addComparisonFuncReturnCode(self, arg):
        self.do_addComparisonThreshold(arg)
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_addComparisonThreshold"
        )

    def do_addFeatureComparison(self, arg):
        self.do_addComparisonCall(arg)
        self.print_replacement(sys._getframe(0).f_code.co_name, "do_addComparisonCall")

    def do_deleteFeatureComparison(self, arg):
        self.do_deleteComparisonCall(arg)
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_deleteComparisonCall"
        )

    def do_addFeatureComparisonElement(self, arg):
        self.do_addComparisonCallElement(
            add_attributes_to_arg(arg, add={"callType": "comparison"})
        )
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_addComparisonCallElement"
        )

    def do_deleteFeatureComparisonElement(self, arg):
        self.do_deleteComparisonCallElement(
            add_attributes_to_arg(arg, add={"callType": "comparison"})
        )
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_deleteComparisonCallElement"
        )

    def do_addFeatureDistinctCallElement(self, arg):
        self.do_addDistinctCallElement(
            add_attributes_to_arg(arg, add={"callType": "distinct"})
        )
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_addDistinctCallElement"
        )

    def do_setFeatureElementDerived(self, arg):
        self.do_setFeatureElement(arg)
        self.print_replacement(sys._getframe(0).f_code.co_name, "do_setFeatureElement")

    def do_setFeatureElementDisplayLevel(self, arg):
        self.do_setFeatureElement(
            add_attributes_to_arg(arg, rename="display=display_level")
        )
        self.print_replacement(sys._getframe(0).f_code.co_name, "do_setFeatureElement")

    def do_addEntityScore(self, arg):
        print(
            colorize(
                "\nThis configuration command is no longer needed\n", "dim,italics"
            )
        )

    def do_addToNameSSNLast4hash(self, arg):
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ELEMENT"])
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        parm_data["CALLTYPE"] = "expression"
        call_id, message = self.getCallID(
            "SSN_LAST4", parm_data["CALLTYPE"], "EXPRESS_BOM"
        )
        if not call_id:
            colorize_msg(message, "error")
            return

        parm_data["ID"] = call_id
        self.addCallElement(json.dumps(parm_data))
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_addExpressionCallElement"
        )

    def do_deleteFromSSNLast4hash(self, arg):
        if not arg:
            self.do_help(sys._getframe(0).f_code.co_name)
            return
        try:
            parm_data = dict_keys_upper(json.loads(arg))
            self.validate_parms(parm_data, ["ELEMENT"])
            parm_data["ELEMENT"] = parm_data["ELEMENT"].upper()
        except Exception as err:
            colorize_msg(f"Command error: {err}", "error")
            return

        parm_data["CALLTYPE"] = "expression"
        call_id, message = self.getCallID(
            "SSN_LAST4", parm_data["CALLTYPE"], "EXPRESS_BOM"
        )
        if not call_id:
            colorize_msg(message, "error")
            return

        parm_data["ID"] = call_id
        self.delete_call_element(json.dumps(parm_data))
        self.print_replacement(
            sys._getframe(0).f_code.co_name, "do_deleteExpressionCallElement"
        )

    def do_updateAttributeAdvanced(self, arg):
        self.do_setAttribute(arg)
        self.print_replacement(sys._getframe(0).f_code.co_name, "do_setAttribute")

    def do_updateFeatureVersion(self, arg):
        self.do_setFeature(arg)
        self.print_replacement(sys._getframe(0).f_code.co_name, "do_Feature")

    # ===== Class Utils =====

    def print_json_record(self, json_obj):
        if type(json_obj) not in [dict, list]:
            json_obj = json.loads(json_obj)

        if self.current_output_format_record == "table":
            render_string = self.print_json_as_table(
                json_obj if type(json_obj) == list else [json_obj]
            )
            self.print_scrolling(render_string)
            return

        if self.current_output_format_record == "json":
            json_str = json.dumps(json_obj, indent=4)
        else:
            json_str = json.dumps(json_obj)

        if self.pygments_installed:
            render_string = highlight(
                json_str, lexers.JsonLexer(), formatters.TerminalFormatter()
            )
        else:
            render_string = colorize_json(json_str)

        print(f"\n{render_string}\n")

    def print_json_lines(self, json_lines, display_header=""):
        if not json_lines:
            colorize_msg("Nothing to display", "warning")
            return

        if display_header:
            print(f"\n{display_header}")

        if self.current_output_format_list == "table":
            render_string = self.print_json_as_table(json_lines)
        elif self.current_output_format_list == "jsonl":
            render_string = ""
            for line in json_lines:
                if self.pygments_installed:
                    render_string += (
                        highlight(
                            json.dumps(line),
                            lexers.JsonLexer(),
                            formatters.TerminalFormatter(),
                        ).replace("\n", "")
                        + "\n"
                    )
                else:
                    render_string += colorize_json(json.dumps(line)) + "\n"
        else:
            json_doc = "["
            for line in json_lines:
                json_doc += json.dumps(line) + ", "
            json_doc = json_doc[0:-2] + "]"
            render_string = colorize_json(json.dumps(json.loads(json_doc), indent=4))

        # TODO Fetch terminal height nd determine if scroll is needed?
        self.print_scrolling(render_string)

    def print_json_as_table(self, json_lines):
        tblColumns = list(json_lines[0].keys())
        columnHeaderList = []
        for attr_name in tblColumns:
            columnHeaderList.append(colorize(attr_name, "attr_color"))
        table_object = prettytable.PrettyTable()
        table_object.field_names = columnHeaderList
        row_count = 0
        for json_data in json_lines:
            row_count += 1
            tblRow = []
            for attr_name in tblColumns:
                attr_value = (
                    json.dumps(json_data[attr_name])
                    if type(json_data[attr_name]) in (list, dict)
                    else str(json_data[attr_name])
                )
                if row_count % 2 == 0:  # for future alternating colors
                    tblRow.append(colorize(attr_value, "dim"))
                else:
                    tblRow.append(colorize(attr_value, "dim"))
            table_object.add_row(tblRow)

        table_object.align = "l"
        if hasattr(prettytable, "SINGLE_BORDER"):
            table_object.set_style(prettytable.SINGLE_BORDER)
        table_object.hrules = 1
        render_string = table_object.get_string()
        return render_string

    def print_scrolling(self, render_string):
        less = subprocess.Popen(["less", "-FMXSR"], stdin=subprocess.PIPE)
        try:
            less.stdin.write(render_string.encode("utf-8"))
        except IOError:
            pass
        less.stdin.close()
        less.wait()
        print()


# ===== Utility functions =====


def getFeatureBehavior(feature):
    featureBehavior = feature["FTYPE_FREQ"]
    if str(feature["FTYPE_EXCL"]).upper() in ("1", "Y", "YES"):
        featureBehavior += "E"
    if str(feature["FTYPE_STAB"]).upper() in ("1", "Y", "YES"):
        featureBehavior += "S"
    return featureBehavior


def parseFeatureBehavior(behaviorCode):
    behaviorDict = {"EXCLUSIVITY": "No", "STABILITY": "No"}
    if behaviorCode not in ("NAME", "NONE"):
        if "E" in behaviorCode:
            behaviorDict["EXCLUSIVITY"] = "Yes"
            behaviorCode = behaviorCode.replace("E", "")
        if "S" in behaviorCode:
            behaviorDict["STABILITY"] = "Yes"
            behaviorCode = behaviorCode.replace("S", "")
    if behaviorCode in ("A1", "F1", "FF", "FM", "FVM", "NONE", "NAME"):
        behaviorDict["FREQUENCY"] = behaviorCode
    else:
        behaviorDict = None
    return behaviorDict


def dict_keys_upper(dictionary):
    if isinstance(dictionary, list):
        return [v.upper() for v in dictionary]
    elif isinstance(dictionary, dict):
        return {k.upper(): v for k, v in dictionary.items()}
    else:
        return dictionary


def add_attributes_to_arg(arg, **kwargs):
    # add={"callType": "expression"}
    # rename=display=display_level
    if arg:
        parm_data = json.loads(arg)
        if kwargs.get("add"):
            parm_data.update(kwargs.get("add"))
        if kwargs.get("rename"):
            new, old = kwargs.get("rename").split("=")
            parm_data[new] = parm_data.get(old)
        arg = json.dumps(parm_data)
    return arg


if __name__ == "__main__":

    argParser = argparse.ArgumentParser()
    argParser.add_argument("file_to_process", default=None, nargs="?")
    argParser.add_argument(
        "-c",
        "--ini-file-name",
        dest="ini_file_name",
        default=None,
        help="name of a G2Module.ini file to use",
    )
    argParser.add_argument(
        "-f",
        "--force",
        dest="force_mode",
        default=False,
        action="store_true",
        help="when reading from a file, execute each command without prompts",
    )
    argParser.add_argument(
        "-H",
        "--hist_disable",
        dest="hist_disable",
        action="store_true",
        default=False,
        help="disable history file usage",
    )
    args = argParser.parse_args()

    # Check if INI file or env var is specified, otherwise use default INI file
    # iniFileName = None

    # if args.ini_file_name:
    #     iniFileName = pathlib.Path(args.ini_file_name)
    # elif os.getenv("SENZING_ENGINE_CONFIGURATION_JSON"):
    #     engine_settings = os.getenv("SENZING_ENGINE_CONFIGURATION_JSON")
    # else:
    #     iniFileName = pathlib.Path(G2Paths.get_G2Module_ini_path())

    # if iniFileName:
    #     G2Paths.check_file_exists_and_readable(iniFileName)
    #     iniParamCreator = G2IniParams()
    #     engine_settings = iniParamCreator.getJsonINIParams(iniFileName)

    secj = os.environ.get("SENZING_ENGINE_CONFIGURATION_JSON")
    if not secj or (secj and len(secj) == 0):
        print(
            "\nERROR: SENZING_ENGINE_CONFIGURATION_JSON environment variable is not set"
        )
        sys.exit(1)

    # cmd_obj = SzCmdShell(engine_settings, args.hist_disable, args.force_mode, args.file_to_process)
    cmd_obj = SzCmdShell(secj, args.hist_disable, args.force_mode, args.file_to_process)

    if args.file_to_process:
        cmd_obj.fileloop()
    else:
        cmd_obj.cmdloop()

    sys.exit()
