# -*- coding: UTF-8 -*-
#!/usr/bin/env python
"""This script packages files into a zip ready to be uploaded to QGIS plugins
repository.

How to use: open a command prompt and launch 'python tools\plugin_packager.py'
from inside the Isogeo plugin qgis repository.

See: http://www.qgis.org/pyqgis-cookbook/releasing.html
        Authors: J. Moura
        Python: 2.7.x
        Created: 20/07/2016
        Licence: GPL 3
"""

# ------------ Imports --------------------------------------------
from os import getcwd, listdir, makedirs, path, remove, walk
import xml.etree.ElementTree as ET
import zipfile

# ------------ UI files check --------------------------------------------

# see: http://gis.stackexchange.com/a/155599/19817
ui_dir = path.abspath(getcwd())
for dirpath, dirs, files in walk(ui_dir):
    for file in files:
        if (file.endswith(".ui")):
            with open(path.join(dirpath, file), 'r') as ui_file:
                ui_xml = ET.parse(ui_file)
                root = ui_xml.getroot()
                for rsrc in root.iter('resources'):
                    if len(rsrc) > 0:
                        print("WARNING - resources tag spotted in: {}"\
                              .format(file))
                        # AUTO REMOVE ##
                        root.remove(rsrc)
                        ui_xml.write(path.join(dirpath, file),
                                     encoding='utf-8',
                                     xml_declaration='version="1.0"',
                                     method='xml')
                        print("INFO - resources tag has been removed.")
                    else:
                        continue
                for custom in root.iter('customwidget'):
                    header = custom.getchildren()[2]
                    print(header, dir(header), header.text)
                    if header.text != "qgis.gui":
                        header.text = header.text.replace(header.text, 'qgis.gui')
                        ui_xml.write(path.join(dirpath, file),
                                     encoding='utf-8',
                                     xml_declaration='version="1.0"',
                                     method='xml')
                        print("INFO - Custom widget header fixed.")
                    else:
                        continue
        elif (file.endswith(".pyc")):
            remove(path.join(dirpath, file))

        else:
            continue

# ------------ Destination folder --------------------------------------------
# folder name
plg_dir = "isogeo_search_engine"

# where to store the zip files
dest_folder = path.abspath(r"build\latest")

if not path.isdir(dest_folder):    # test if folder already exists
    makedirs(dest_folder, 0777)
else:
    pass

# ------------ Led Zipping -------------------------------------------
final_zip = zipfile.ZipFile(path.join(dest_folder, plg_dir + ".zip"), "w")

# QGIS Plugin requirements
final_zip.write(r"LICENSE", plg_dir + r"\LICENSE")
final_zip.write(r"metadata.txt", plg_dir + r"\metadata.txt")
final_zip.write(r"README.md", plg_dir + r"\README")

# Python base code
final_zip.write(r"__init__.py", plg_dir + r"\__init__.py")
final_zip.write(r"isogeo.py", plg_dir + r"\isogeo.py")

# Modules
final_zip.write(r"modules\__init__.py", plg_dir + r"\modules\__init__.py")
final_zip.write(r"modules\api.py", plg_dir + r"\modules\api.py")
final_zip.write(r"modules\tools.py", plg_dir + r"\modules\tools.py")
final_zip.write(r"modules\url_builder.py", plg_dir + r"\modules\url_builder.py")
final_zip.write(r"modules\isogeo.qml", plg_dir + r"\modules\isogeo.qml")

# Resources
resources_files = [path.relpath(f) for f in listdir(r"resources")
                   if path.isfile(path.join(path.realpath(r"resources"), f))]

for resource in resources_files:
    final_zip.write(r"resources\\" + resource,
                    plg_dir + r"\resources\\" + resource)

# Translations
final_zip.write(r"i18n\isogeo_search_engine_fr.qm",
                plg_dir + r"\i18n\isogeo_search_engine_fr.qm")

# UI - Base
final_zip.write(r"icon.png",
                plg_dir + r"\icon.png")
final_zip.write(r"ui\__init__.py",
                plg_dir + r"\ui\__init__.py")
final_zip.write(r"ui\isogeo_dockwidget_base.ui",
                plg_dir + r"\ui\isogeo_dockwidget_base.ui")
final_zip.write(r"ui\isogeo_dockwidget.py",
                plg_dir + r"\ui\isogeo_dockwidget.py")
final_zip.write(r"ui\ui_isogeo.py",
                plg_dir + r"\ui\ui_isogeo.py")
final_zip.write(r"resources.py",
                plg_dir + r"\resources.py")
final_zip.write(r"resources.qrc",
                plg_dir + r"\resources.qrc")

# UI - Auth
final_zip.write(r"ui\auth\__init__.py",
                plg_dir + r"\ui\auth\__init__.py")
final_zip.write(r"ui\auth\ui_authentication.ui",
                plg_dir + r"\ui\auth\ui_authentication.ui")
final_zip.write(r"ui\auth\ui_authentication.py",
                plg_dir + r"\ui\auth\ui_authentication.py")
final_zip.write(r"ui\auth\dlg_authentication.py",
                plg_dir + r"\ui\auth\dlg_authentication.py")

# UI - Credits
final_zip.write(r"ui\credits\__init__.py",
                plg_dir + r"\ui\credits\__init__.py")
final_zip.write(r"ui\credits\ui_credits.ui",
                plg_dir + r"\ui\credits\ui_credits.ui")
final_zip.write(r"ui\credits\ui_credits.py",
                plg_dir + r"\ui\credits\ui_credits.py")
final_zip.write(r"ui\credits\dlg_credits.py",
                plg_dir + r"\ui\credits\dlg_credits.py")

# UI - MdDetails
final_zip.write(r"ui\mddetails\__init__.py",
                plg_dir + r"\ui\mddetails\__init__.py")
final_zip.write(r"ui\mddetails\ui_md_details.ui",
                plg_dir + r"\ui\mddetails\ui_md_details.ui")
final_zip.write(r"ui\mddetails\ui_md_details.py",
                plg_dir + r"\ui\mddetails\ui_md_details.py")
final_zip.write(r"ui\mddetails\dlg_md_details.py",
                plg_dir + r"\ui\mddetails\dlg_md_details.py")

# UI - Quicksearch - name
final_zip.write(r"ui\quicksearch\__init__.py",
                plg_dir + r"\ui\quicksearch\__init__.py")
final_zip.write(r"ui\quicksearch\ui_quicksearch_new.py",
                plg_dir + r"\ui\quicksearch\ui_quicksearch_new.py")
final_zip.write(r"ui\quicksearch\ui_quicksearch_new.ui",
                plg_dir + r"\ui\quicksearch\ui_quicksearch_new.ui")
final_zip.write(r"ui\quicksearch\dlg_quicksearch_new.py",
                plg_dir + r"\ui\quicksearch\dlg_quicksearch_new.py")

# UI - Quicksearch - rename
final_zip.write(r"ui\quicksearch\ui_quicksearch_rename.py",
                plg_dir + r"\ui\quicksearch\ui_quicksearch_rename.py")
final_zip.write(r"ui\quicksearch\ui_quicksearch_rename.ui",
                plg_dir + r"\ui\quicksearch\ui_quicksearch_rename.ui")
final_zip.write(r"ui\quicksearch\dlg_quicksearch_rename.py",
                plg_dir + r"\ui\quicksearch\dlg_quicksearch_rename.py")

# User settings
final_zip.write(r"user_settings\saved_searches.json",
                plg_dir + r"\user_settings\saved_searches.json")

# ----------------------------------------------------------------------------
