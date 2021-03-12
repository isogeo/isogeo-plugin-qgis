# -*- coding: UTF-8 -*-
#!/usr/bin/env python3

"""
    This script packages files into a zip ready to be uploaded to QGIS plugins
    repository.

    How to use on Windows:

        1. Launch OSGeo4W Shell inside th Isogeo QGIS Plugin repository
        2. Run:

            python tools\plugin_packager.py


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
from os import listdir, path
import json
import xml.etree.ElementTree as ET
from zipfile import ZipFile, ZipInfo

from pathlib import Path

# ##############################################################################
# ########## Globals ###############
# ##################################

# TYPES
RESOURCES_TYPES = ("**/*.svg", "**/*.png")

# Paths
DIR_PLUGIN_ROOT = Path(__file__).parent.parent
DIR_OUTPUT = DIR_PLUGIN_ROOT.resolve() / "build/latest"
DIR_OUTPUT.mkdir(exist_ok=True, parents=True)

BASE_DIR_ABS = DIR_PLUGIN_ROOT.resolve()

PLG_DIRNAME = "isogeo_search_engine"
PLG_METADATA_FILE = DIR_PLUGIN_ROOT.resolve() / "metadata.txt"
PLG_FINAL_ZIP_PATH = str(DIR_OUTPUT / PLG_DIRNAME) + ".zip"


# #############################################################################
# ########## Functions##############
# ##################################
def fix_ui_files(ui_folder: Path = "./ui"):
    """Fix UI files with some custom QGIS Qt widgets.
    See: http://gis.stackexchange.com/a/155599/19817
    """
    ui_folder = Path(ui_folder)
    for ui_file in ui_folder.glob("**/*.ui"):
        with ui_file.open("r") as f:
            ui_xml = ET.parse(f)
            root = ui_xml.getroot()
            for rsrc in root.iter("resources"):
                if len(rsrc) > 0:
                    print("WARNING - resources tag spotted in: {}".format(ui_file))
                    # AUTO REMOVE ##
                    root.remove(rsrc)
                    ui_xml.write(
                        ui_file.resolve(),
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
                        ui_file.resolve(),
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
    "Packaging the version {} of the Isogeo plugin for QGIS version {} to {}) to: {}".format(
        *version, PLG_FINAL_ZIP_PATH
    )
)

# ensure UI files are good
fix_ui_files()

# -- LED ZIPPING ----------------------------------------------------------
# release_zip = zipfile.ZipFile(PLG_FINAL_ZIP_PATH, "w")

with ZipFile(PLG_FINAL_ZIP_PATH, "w") as release_zip:

    # -- QGIS PLUGIN REQUIRED FILES -------------------------------------------------------

    release_zip.write(Path(BASE_DIR_ABS, "LICENSE"), Path(PLG_DIRNAME, "LICENSE"))
    release_zip.write(
        Path(BASE_DIR_ABS, "metadata.txt"), Path(PLG_DIRNAME, "metadata.txt")
    )
    release_zip.write(Path(BASE_DIR_ABS, "README.md"), Path(PLG_DIRNAME, "README"))

    # -- PLUGIN PYTHON CODE ------------------------------------------------------------
    release_zip.write(
        Path(BASE_DIR_ABS, "__init__.py"), Path(PLG_DIRNAME, "__init__.py")
    )
    release_zip.write(Path(BASE_DIR_ABS, "isogeo.py"), Path(PLG_DIRNAME, "isogeo.py"))

    # Python modules
    modules_path = Path("./modules")
    for file_src in list(modules_path.glob("**/*.py")):
        file_dest_zip_path = PLG_DIRNAME / file_src.parent / file_src.name
        release_zip.write(file_src, file_dest_zip_path)

    # UI files
    ui_path = Path("./ui")
    for file_src in list(ui_path.glob("**/*.py")):
        if file_src.name.startswith("ui_"):
            continue
        file_dest_zip_path = PLG_DIRNAME / file_src.parent / file_src.name
        release_zip.write(file_src, file_dest_zip_path)

    for file_src in list(ui_path.glob("**/*.ui")):
        file_dest_zip_path = PLG_DIRNAME / file_src.parent / file_src.name
        release_zip.write(file_src, file_dest_zip_path)

    # Translations
    i18n_path = Path("./i18n")
    for file_src in list(i18n_path.glob("**/*.qm")):
        file_dest_zip_path = PLG_DIRNAME / file_src.parent / file_src.name
        release_zip.write(file_src, file_dest_zip_path)

    # Resources (media files)
    resources_path = Path("./resources")
    for resource_type in RESOURCES_TYPES:
        for file_src in list(resources_path.glob(resource_type)):
            file_dest_zip_path = PLG_DIRNAME / file_src.parent / file_src.name
            release_zip.write(file_src, file_dest_zip_path)

    # UI - Base
    release_zip.write(Path(BASE_DIR_ABS, "icon.png"), Path(PLG_DIRNAME, "icon.png"))
    release_zip.write(
        Path(BASE_DIR_ABS, "resources_rc.py"), Path(PLG_DIRNAME, "resources_rc.py")
    )

    # -- User settings ----------------------------------------------------------

    QUICKSEARCHES = {
        "_default": {
            "contacts": None,
            "datatype": "type:dataset",
            "favorite": None,
            "formats": None,
            "geofilter": None,
            "inspire": None,
            "lang": "fr",
            "licenses": None,
            "ob": "relevance",
            "od": "desc",
            "operation": "intersects",
            "owners": None,
            "page": 1,
            "show": true,
            "srs": None,
            "text": "",
            "url": "https://v1.api.isogeo.com/resources/search?q=type:dataset&ob=relevance&od=desc&_include=serviceLayers,layers,limitations&_limit=10&_offset=0&_lang=fr",
        }
    }

    QUICKSEARCHES_JSON = path.join(DIR_OUTPUT.resolve(), "..", "quicksearches.json")
    with open(QUICKSEARCHES_JSON, "w") as qs:
        json.dump(QUICKSEARCHES, qs, sort_keys=True, indent=4)

    release_zip.write(
        QUICKSEARCHES_JSON,
        "{}/{}/{}".format(PLG_DIRNAME, "_user", "quicksearches.json"),
    )
