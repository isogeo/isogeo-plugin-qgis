# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import json
from pathlib import Path

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QSettings


# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

# ############################################################################
# ########## Classes ###############
# ##################################


class SettingsManager(QSettings):
    """Inheritance from Isogeo Python SDK utils class. It adds some
    specific tools for QGIS plugin."""

    def __init__(self):
        """Check and manage authentication credentials."""
        # instantiate
        super().__init__()

        self.quicksearches_json_path = Path(__file__).parents[1] / "_user" / "quicksearches.json"
        self.quicksearch_prefix = "isogeo/user/quicksearches/"
        self.api_base_url = str
        self.tr = object

        self.quicksearches_content = {}

    def get_locale(self):
        """Return 'locale/userLocale' setting value about QGIS language configuration"""

        try:
            locale = str(self.value("locale/userLocale", "fr", type=str))[0:2]
        except TypeError as e:
            logger.error(
                "Bad type in QSettings: {}. Original error: {}".format(
                    type(self.value("locale/userLocale")), e
                )
            )
            locale = "fr"
        return locale

    def get_value(self, setting_name: str, default_value=None, type=None):
        if type is None:
            return self.value(setting_name, default_value)
        else:
            return self.value(setting_name, default_value, type)

    def set_value(self, setting_name: str, value):
        self.setValue(setting_name, value)
        return value

    def check_json_file_exists(self, file_path: Path):
        if not (file_path.exists() and file_path.is_file()):
            return 0
        else:
            return 1

    def load_json_file(self, file_path: Path):

        if not self.check_json_file_exists(file_path):
            logger.warning(
                "{} json file can't be used, it doesn't exist or is not a file.".format(
                    str(file_path)
                )
            )
            return 0
        else:
            try:
                with open(file_path, "r") as json_file:
                    json_content = json.load(json_file)
                return json_content
            except Exception as e:
                logger.error("{} json file can't be read : {}.".format(str(file_path), str(e)))
                return -1

    def dump_json_file(self, file_path: Path, content: dict):
        with open(file_path, "w") as outfile:
            json.dump(content, outfile, sort_keys=True, indent=4)
        return

    def get_default_quicksearches_content(self):

        default_content = {
            "_default": {
                "contacts": None,
                "datatype": "type:dataset",
                "favorite": None,
                "formats": None,
                "geofilter": None,
                "groupTheme": None,
                "inspire": None,
                "labels": {
                    "contacts": " - ",
                    "datatype": "Données (vecteurs, rasters et tabulaires)",
                    "formats": " - ",
                    "groupTheme": " - ",
                    "inspire": " - ",
                    "keys": [],
                    "licenses": " - ",
                    "owners": " - ",
                    "srs": " - "
                },
                "lang": "fr",
                "licenses": None,
                "ob": "relevance",
                "od": "desc",
                "operation": "intersects",
                "owners": None,
                "page": 1,
                "show": True,
                "srs": None,
                "text": "",
                "url": "{}/resources/search?q=type:dataset&ob=relevance&od=desc&_include=serviceLayers,layers,limitations&_limit=10&_offset=0&_lang=fr".format(
                    self.api_base_url
                ),
            }
        }
        return default_content

    def load_quicksearches(self):
        # logger.debug("*=====* Loading quicksearches")
        quicksearch_json_content = self.load_quicksearches_from_json()
        # logger.debug("*=====* {} quicksearches found in json_file".format(len(quicksearch_json_content)))
        quicksearch_qsettings_content = self.load_quicksearches_from_qsettings()
        # logger.debug("*=====* {} quicksearches found in qsettings".format(len(quicksearch_qsettings_content)))

        self.quicksearches_content = self.merge_quicksearch(quicksearch_json_content, quicksearch_qsettings_content)

        return self.quicksearches_content

    def check_quicksearch_json_content(self, json_content):
        if not isinstance(json_content, dict):
            return 0
        elif not all(isinstance(key, str) for key in json_content):
            return 0
        elif not all(isinstance(json_content[key], dict) for key in json_content):
            return 0
        elif not all(all(isinstance(sub_key, str) for sub_key in json_content[key]) for key in json_content):
            return 0
        return 1

    def load_quicksearches_from_json(self):

        json_content = self.load_json_file(self.quicksearches_json_path)
        if json_content == -1:
            return 0
        elif not json_content:
            logger.warning(
                "{} json file is missing.".format(
                    self.quicksearches_json_path
                )
            )
            logger.warning("Let's create it with the default content.")
            json_content = self.get_default_quicksearches_content()
            self.update_quicksearches_json(json_content)
            return json_content
        elif not self.check_quicksearch_json_content(json_content):
            logger.warning(
                "{} json file content is not correctly formatted : {}.".format(
                    self.quicksearches_json_path, json_content
                )
            )
            logger.warning("Let's replace it with the default content.")
            json_content = self.get_default_quicksearches_content()
            self.update_quicksearches_json(json_content)
            return json_content
        else:
            if "_default" not in json_content:
                logger.warning(
                    "Missing '_default' quicksearch in _user/quicksearches.json file content : {}.".format(
                        json_content
                    )
                )
                logger.warning("Let's add the default one.")
                # if default search is missing, let's adding it to JSON file content
                json_content["_default"] = self.get_default_quicksearches_content().get("_default")
            else:
                pass

            for trad in ["Last search", "Dernière recherche"]:
                if trad in json_content and self.tr("Last search") != trad:
                    json_content[self.tr("Last search")] = json_content.get(trad)
                    del json_content[trad]
                else:
                    pass

            for quicksearch in json_content:
                quicksearch_url = json_content.get(quicksearch).get("url")
                if self.api_base_url not in quicksearch_url:
                    search_parameters = quicksearch_url.split("/resources/search?")[1]
                    base_search_url = self.api_base_url + "/resources/search?"
                    json_content[quicksearch]["url"] = (base_search_url + search_parameters)
                    logger.warning(
                        "'{}' quicksearch : URL {} replaced with {}.".format(
                            quicksearch,
                            quicksearch_url,
                            base_search_url + search_parameters,
                        )
                    )
                else:
                    pass
            self.update_quicksearches_json(json_content)
            return json_content

    def load_quicksearches_from_qsettings(self):

        qsettings_quicksearch_keys = [key for key in self.allKeys() if key.startswith(self.quicksearch_prefix)]

        if not len(qsettings_quicksearch_keys):
            return {}
        else:
            qsettings_content = {}

            for key in qsettings_quicksearch_keys:
                quicksearch_name = key.replace(self.quicksearch_prefix, "").split("/")[0]
                if quicksearch_name not in qsettings_content:
                    qsettings_content[quicksearch_name] = {}
                else:
                    pass

                quicksearch_param = key.replace(self.quicksearch_prefix, "").split("/")[1]
                if quicksearch_param != "labels":
                    qsettings_content[quicksearch_name][quicksearch_param] = self.get_value(key)
                else:
                    if quicksearch_param not in qsettings_content[quicksearch_name]:
                        qsettings_content[quicksearch_name][quicksearch_param] = {}
                    else:
                        pass
                    label = key.replace(self.quicksearch_prefix, "").split("/")[2]
                    qsettings_content[quicksearch_name][quicksearch_param][label] = self.get_value(key)

            return qsettings_content

    def merge_quicksearch(self, json_content, qsettings_content):

        # logger.debug("*=====* merging quicksearches")

        for quicksearch_name in json_content:
            quicksearch = json_content[quicksearch_name]
            if quicksearch_name in ["Last search", "Dernière recherche", "_current"] and quicksearch_name in qsettings_content:
                json_content[quicksearch_name] = qsettings_content[quicksearch_name]
            else:
                self.write_quicksearch_qsettings(quicksearch_name, quicksearch)

        for quicksearch_name in qsettings_content:
            quicksearch = qsettings_content[quicksearch_name]
            if quicksearch_name not in json_content:
                json_content[quicksearch_name] = quicksearch
            else:
                pass

        self.update_quicksearches_json(json_content)

        return json_content

    def update_quicksearches_json(self, content: dict):

        self.dump_json_file(self.quicksearches_json_path, content)
        return

    def write_quicksearch_qsettings(self, name: str, content: dict):

        # logger.debug("*=====* writing {} quicksearches in qsettings".format(name))
        for quicksearch_param in content:
            quicksearch_param_value = content[quicksearch_param]
            if quicksearch_param != "labels":
                qsetting_key = "{}{}/{}".format(self.quicksearch_prefix, name, quicksearch_param)
                qsetting_value = quicksearch_param_value
                self.set_value(qsetting_key, qsetting_value)
            else:
                for label in quicksearch_param_value:
                    qsetting_key = "{}{}/{}/{}".format(self.quicksearch_prefix, name, quicksearch_param, label)
                    qsetting_value = quicksearch_param_value[label]
                    self.set_value(qsetting_key, qsetting_value)

        return

    def update_quicksearches_qsettings(self, content: dict):

        self.remove(self.quicksearch_prefix[:-1])
        for quicksearch_name in content:
            quicksearch = content[quicksearch_name]
            self.write_quicksearch_qsettings(quicksearch_name, quicksearch)
        return

    def update_quicksearches(self, content):

        self.update_quicksearches_json(content)
        self.update_quicksearches_qsettings(content)
        self.quicksearches_content = content

        return

    def save_quicksearch(self, name: str, content: dict):

        self.quicksearches_content[name] = content
        self.update_quicksearches(self.quicksearches_content)

        return

    def rename_quicksearch(self, old_name: str, new_name: str):

        self.quicksearches_content[new_name] = self.quicksearches_content[old_name]
        self.quicksearches_content.pop(old_name)
        self.update_quicksearches(self.quicksearches_content)

        return

    def remove_quicksearch(self, name: str):

        self.quicksearches_content.pop(name)
        self.update_quicksearches(self.quicksearches_content)

        return

# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""