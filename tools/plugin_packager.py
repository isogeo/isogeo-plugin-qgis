# -*- coding: UTF-8 -*-
#!/usr/bin/env python3

"""
    This script packages files into a zip ready to be uploaded to QGIS plugins
    repository.

    How to use on Windows:

        1. Launch OSGeo4W Shell inside th Isogeo QGIS Plugin repository
        2. Run:
            ```bash
            python tools\plugin_packager.py
            ```

    See: https://docs.qgis.org/testing/en/docs/pyqgis_developer_cookbook/releasing.html

    Authors: J. Moura (Isogeo)
    Python: 3.7.x
    Created: 20/07/2016
    License: GPL 3
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from configparser import ConfigParser
from os import listdir, makedirs, path, remove, walk
import json
import xml.etree.ElementTree as ET
import zipfile

from pathlib import Path

# ##############################################################################
# ########## Globals ###############
# ##################################

# Paths
DIR_PLUGIN_ROOT = Path(__file__).parent.parent
DIR_OUTPUT = DIR_PLUGIN_ROOT.resolve() / "build/latest"
DIR_OUTPUT.mkdir(exist_ok=True, parents=True)

BASE_DIR_ABS = DIR_PLUGIN_ROOT.resolve()

PLG_DIRNAME = "isogeo_search_engine"
PLG_METADATA_FILE = DIR_PLUGIN_ROOT.resolve() / "metadata.txt"

# #############################################################################
# ########## Functions##############
# ##################################
def fix_ui_files(ui_folder: Path = "./ui"):
    """Fix UI files with some custom QGIS Qt widgets.
    See: http://gis.stackexchange.com/a/155599/19817
    """
    ui_folder = Path(ui_folder)
    for ui_file in ui_folder.glob("**/*.ui"):
        with ui_file.open("r") as ui_file:
            ui_xml = ET.parse(ui_file)
            root = ui_xml.getroot()
            for rsrc in root.iter("resources"):
                if len(rsrc) > 0:
                    print("WARNING - resources tag spotted in: {}".format(f))
                    # AUTO REMOVE ##
                    root.remove(rsrc)
                    ui_xml.write(
                        path.join(dirpath, f),
                        encoding="utf-8",
                        xml_declaration='version="1.0"',
                        method="xml",
                    )
                    print("INFO - resources tag has been removed.")
                else:
                    continue
            for custom in root.iter("customwidget"):
                header = list(custom)[2]
                if header.text != "qgis.gui":
                    header.text = header.text.replace(header.text, "qgis.gui")
                    ui_xml.write(
                        path.join(dirpath, f),
                        encoding="utf-8",
                        xml_declaration='version="1.0"',
                        method="xml",
                    )
                    print("INFO - Custom widget header fixed.")
                else:
                    continue


def remove_files(start_folder: Path = ".", glob_pattern: str = "**/*.pyc"):
    """Remove files under the start folder which are matching the glob pattern."""
    start_folder = Path(start_folder)
    for file_to_be_removed in list(start_folder.glob(glob_pattern)):
        file_to_be_removed.unlink()


def plugin_metadata():
    """Retrieve plugin information from the conventional `metadata.txt`."""
    config = ConfigParser()
    if PLG_METADATA_FILE.is_file():
        config.read(PLG_METADATA_FILE.resolve())
        return (
            config.get("general", "version"),
            config.get("general", "qgisMinimumVersion"),
            config.get("general", "qgisMaximumVersion"),
        )
    else:
        raise IOError("Metadata text not found")


# ##############################################################################
# ##### Main program ###############
# ##################################

# clean up
remove_files()  # remove Python compiled files

# get plugin metadata
version = plugin_metadata()
print(
    "Packaging the version {} of the Isogeo plugin for QGIS version {} to {})".format(
        *version
    )
)

# ensure UI files are good
fix_ui_files()

# ------------ Led Zipping -------------------------------------------
RELEASE_ZIP = zipfile.ZipFile(
    path.join(DIR_OUTPUT.resolve(), PLG_DIRNAME + ".zip"), "w"
)

# AUTH folder
auth_folder = zipfile.ZipInfo(path.join(PLG_DIRNAME, "_auth/"))
RELEASE_ZIP.writestr(auth_folder, "")

# LOG folder
log_folder = zipfile.ZipInfo(path.join(PLG_DIRNAME, "_logs/"))
RELEASE_ZIP.writestr(log_folder, "")


# USER folder
user_folder = zipfile.ZipInfo(path.join(PLG_DIRNAME, "_user/"))
RELEASE_ZIP.writestr(user_folder, "")

# QGIS Plugin requirements
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "LICENSE"), "{}/{}".format(PLG_DIRNAME, "LICENSE")
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "metadata.txt"), "{}/{}".format(PLG_DIRNAME, "metadata.txt")
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "README.md"), "{}/{}".format(PLG_DIRNAME, "README")
)

# Python base code
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "__init__.py"), "{}/{}".format(PLG_DIRNAME, "__init__.py")
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "isogeo.py"), "{}/{}".format(PLG_DIRNAME, "isogeo.py")
)

# Python modules
modules_path = Path("./modules")
for module_file in list(modules_path.glob("**/*.py")):
    module_file_zip_path = PLG_DIRNAME / module_file.parent / module_file.name
    RELEASE_ZIP.write(module_file.resolve(), module_file_zip_path.resolve())

# Translations
i18n_path = Path("./i18n")
for module_file in list(i18n_path.glob("**/*.qm")):
    module_file_zip_path = PLG_DIRNAME / module_file.parent / module_file.name
    RELEASE_ZIP.write(module_file.resolve(), module_file_zip_path.resolve())


# Resources (media files)
RESOURCES_FILES = [
    path.relpath(f)
    for f in listdir("resources")
    if path.isfile(path.join(path.realpath("resources"), f))
]

for resource in RESOURCES_FILES:
    RELEASE_ZIP.write(
        path.join(BASE_DIR_ABS, "resources", resource),
        "{}/{}/{}".format(PLG_DIRNAME, "resources", resource),
    )


# UI - Base
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "icon.png"), "{}/{}".format(PLG_DIRNAME, "icon.png")
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "resources_rc.py"), "{}/{}".format(PLG_DIRNAME, "resources_rc.py")
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "resources.qrc"),
    "{}/{}".format(PLG_DIRNAME, "resources.qrc"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "__init__.py"),
    "{}/{}/{}".format(PLG_DIRNAME, "ui", "__init__.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "isogeo_dockwidget_base.ui"),
    "{}/{}/{}".format(PLG_DIRNAME, "ui", "isogeo_dockwidget_base.ui"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "isogeo_dockwidget.py"),
    "{}/{}/{}".format(PLG_DIRNAME, "ui", "isogeo_dockwidget.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "ui_isogeo.py"),
    "{}/{}/{}".format(PLG_DIRNAME, "ui", "ui_isogeo.py"),
)

# UI - Auth
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "auth", "__init__.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "__init__.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "auth", "ui_authentication.ui"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "ui_authentication.ui"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "auth", "ui_authentication.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "ui_authentication.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "auth", "dlg_authentication.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "dlg_authentication.py"),
)

# UI - Credits
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "credits", "__init__.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "__init__.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "credits", "ui_credits.ui"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "ui_credits.ui"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "credits", "ui_credits.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "ui_credits.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "credits", "dlg_credits.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "dlg_credits.py"),
)

# UI - MdDetails
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "metadata", "__init__.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "__init__.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "metadata", "ui_md_details.ui"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "ui_md_details.ui"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "metadata", "ui_md_details.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "ui_md_details.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "metadata", "dlg_md_details.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "dlg_md_details.py"),
)

# UI - Quicksearch - name
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "quicksearch", "__init__.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "__init__.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_new.ui"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_new.ui"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_new.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_new.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "quicksearch", "dlg_quicksearch_new.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "dlg_quicksearch_new.py"),
)

# UI - Quicksearch - rename
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_rename.ui"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_rename.ui"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_rename.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_rename.py"),
)
RELEASE_ZIP.write(
    path.join(BASE_DIR_ABS, "ui", "quicksearch", "dlg_quicksearch_rename.py"),
    "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "dlg_quicksearch_rename.py"),
)

# -- User settings ----------------------------------------------------------

QUICKSEARCHES = {
    "_default": {
        "contact": None,
        "datatype": "type:dataset",
        "favorite": None,
        "format": None,
        "geofilter": None,
        "inspire": None,
        "license": None,
        "ob": "relevance",
        "od": "desc",
        "operation": "intersects",
        "owner": None,
        "srs": None,
        "text": "",
        "url": "https://v1.api.isogeo.com/resources/search?_limit=0&_offset=0",
    }
}

QUICKSEARCHES_JSON = path.join(DIR_OUTPUT.resolve(), "..", "quicksearches.json")
with open(QUICKSEARCHES_JSON, "w") as qs:
    json.dump(QUICKSEARCHES, qs, sort_keys=True, indent=4)

RELEASE_ZIP.write(
    QUICKSEARCHES_JSON, "{}/{}/{}".format(PLG_DIRNAME, "_user", "quicksearches.json")
)
