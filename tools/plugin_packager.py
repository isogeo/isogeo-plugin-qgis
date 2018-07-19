# -*- coding: UTF-8 -*-
#!/usr/bin/env python

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
    Python: 2.7.x
    Created: 20/07/2016
    License: GPL 3
"""

# ------------ Imports -------------------------------------------------------
from __future__ import (absolute_import, print_function, unicode_literals)
import ConfigParser
from os import listdir, makedirs, path, remove, walk
import json
import xml.etree.ElementTree as ET
import zipfile

# ------------ Globals -------------------------------------------------------

BASE_DIR_REL = path.dirname(path.dirname(path.abspath(__file__)))
BASE_DIR_ABS = path.normpath(BASE_DIR_REL)

# ------------ Functions -----------------------------------------------
def plugin_version(base_path=path.dirname(__file__)):
    config = ConfigParser.ConfigParser()
    if path.isfile(path.join(BASE_DIR_ABS,'metadata.txt')):
        config.read(path.join(BASE_DIR_ABS,'metadata.txt'))
        return (config.get('general', 'version'),
                config.get('general', 'qgisMinimumVersion'),
                config.get('general', 'qgisMaximumVersion'))
    else:
        raise IOError("Metadata text not found")

version = plugin_version()
print("Packaging the version {} of the Isogeo plugin for QGIS version {} to {})"
      .format(*version))

# ------------ UI files check -----------------------------------------------
# see: http://gis.stackexchange.com/a/155599/19817
for dirpath, dirs, files in walk(BASE_DIR_ABS):
    for f in files:
        if f.endswith(".ui"):
            with open(path.join(dirpath, f), 'r') as ui_file:
                ui_xml = ET.parse(ui_file)
                root = ui_xml.getroot()
                for rsrc in root.iter('resources'):
                    if len(rsrc) > 0:
                        print("WARNING - resources tag spotted in: {}"\
                              .format(f))
                        # AUTO REMOVE ##
                        root.remove(rsrc)
                        ui_xml.write(path.join(dirpath, f),
                                     encoding='utf-8',
                                     xml_declaration='version="1.0"',
                                     method='xml')
                        print("INFO - resources tag has been removed.")
                    else:
                        continue
                for custom in root.iter('customwidget'):
                    header = custom.getchildren()[2]
                    # print(header, dir(header), header.text)
                    if header.text != "qgis.gui":
                        header.text = header.text.replace(header.text, 'qgis.gui')
                        ui_xml.write(path.join(dirpath, f),
                                     encoding='utf-8',
                                     xml_declaration='version="1.0"',
                                     method='xml')
                        print("INFO - Custom widget header fixed.")
                    else:
                        continue
        elif f.endswith(".pyc"):
            remove(path.join(dirpath, f))
        else:
            continue

# ------------ Destination folder --------------------------------------------
# folder name
PLG_DIRNAME = "isogeo_search_engine"

# where to store the zip files
DEST_DIR = path.join(BASE_DIR_ABS, "build/latest")

if not path.isdir(DEST_DIR):    # test if folder already exists
    makedirs(DEST_DIR, 0777)
else:
    pass

# ------------ Led Zipping -------------------------------------------
RELEASE_ZIP = zipfile.ZipFile(path.join(DEST_DIR, PLG_DIRNAME + ".zip"), "w")

# LOG folder
log_folder = zipfile.ZipInfo(path.join(PLG_DIRNAME, "_logs/"))
RELEASE_ZIP.writestr(log_folder, "")


# USER folder
user_folder = zipfile.ZipInfo(path.join(PLG_DIRNAME, "_user/"))
RELEASE_ZIP.writestr(user_folder, "")

# QGIS Plugin requirements
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "LICENSE"),
                  "{}/{}".format(PLG_DIRNAME, "LICENSE"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "metadata.txt"),
                  "{}/{}".format(PLG_DIRNAME, "metadata.txt"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "README.md"),
                  "{}/{}".format(PLG_DIRNAME, "README"))

# Python base code
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "__init__.py"),
                  "{}/{}".format(PLG_DIRNAME, "__init__.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "isogeo.py"),
                  "{}/{}".format(PLG_DIRNAME, "isogeo.py"))

# Modules
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "modules", "__init__.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "modules", "__init__.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "modules", "api.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "modules", "api.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "modules", "metadata_display.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "modules", "metadata_display.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "modules", "results.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "modules", "results.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "modules", "tools.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "modules", "tools.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "modules", "url_builder.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "modules", "url_builder.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "modules", "isogeo.qml"),
                  "{}/{}/{}".format(PLG_DIRNAME, "modules", "isogeo.qml"))

# Resources (media files)
RESOURCES_FILES = [path.relpath(f) for f in listdir("resources")
                   if path.isfile(path.join(path.realpath("resources"), f))]

for resource in RESOURCES_FILES:
    RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "resources", resource),
                      "{}/{}/{}".format(PLG_DIRNAME, "resources", resource))

# Translations
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "i18n", "isogeo_search_engine_fr.qm"),
                  "{}/{}/{}".format(PLG_DIRNAME, "i18n", "isogeo_search_engine_fr.qm"))

# UI - Base
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "icon.png"),
                  "{}/{}".format(PLG_DIRNAME, "icon.png"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "resources.py"),
                  "{}/{}".format(PLG_DIRNAME, "resources.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "resources.qrc"),
                  "{}/{}".format(PLG_DIRNAME, "resources.qrc"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "__init__.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "ui", "__init__.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "isogeo_dockwidget_base.ui"),
                  "{}/{}/{}".format(PLG_DIRNAME, "ui", "isogeo_dockwidget_base.ui"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "isogeo_dockwidget.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "ui", "isogeo_dockwidget.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "ui_isogeo.py"),
                  "{}/{}/{}".format(PLG_DIRNAME, "ui", "ui_isogeo.py"))

# UI - Auth
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "auth", "__init__.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "__init__.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "auth", "ui_authentication.ui"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "ui_authentication.ui"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "auth", "ui_authentication.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "ui_authentication.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "auth", "dlg_authentication.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "auth", "dlg_authentication.py"))

# UI - Credits
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "credits", "__init__.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "__init__.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "credits", "ui_credits.ui"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "ui_credits.ui"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "credits", "ui_credits.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "ui_credits.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "credits", "dlg_credits.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "credits", "dlg_credits.py"))

# UI - MdDetails
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "metadata", "__init__.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "__init__.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "metadata", "ui_md_details.ui"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "ui_md_details.ui"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "metadata", "ui_md_details.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "ui_md_details.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "metadata", "dlg_md_details.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "metadata", "dlg_md_details.py"))

# UI - Quicksearch - name
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "quicksearch", "__init__.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "__init__.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_new.ui"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_new.ui"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_new.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_new.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "quicksearch", "dlg_quicksearch_new.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "dlg_quicksearch_new.py"))

# UI - Quicksearch - rename
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_rename.ui"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_rename.ui"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "quicksearch", "ui_quicksearch_rename.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "ui_quicksearch_rename.py"))
RELEASE_ZIP.write(path.join(BASE_DIR_ABS, "ui", "quicksearch", "dlg_quicksearch_rename.py"),
                  "{}/{}/{}/{}".format(PLG_DIRNAME, "ui", "quicksearch", "dlg_quicksearch_rename.py"))

# -- User settings ----------------------------------------------------------

QUICKSEARCHES = {"_default": {"contact": None,
                              "datatype": None,
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
                              },
                }

QUICKSEARCHES_JSON = path.join(DEST_DIR, "..", "quicksearches.json")
with open(QUICKSEARCHES_JSON, "w") as qs:
    json.dump(QUICKSEARCHES, qs, sort_keys=True, indent=4)

RELEASE_ZIP.write(QUICKSEARCHES_JSON,
                  "{}/{}/{}".format(PLG_DIRNAME, "_user", "quicksearches.json"))
