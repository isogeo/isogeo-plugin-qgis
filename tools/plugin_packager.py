# -*- coding: UTF-8 -*-
#!/usr/bin/env python
"""This script packages files into a zip ready to be uploaded to QGIS plugins
repository.

How to use: open a command prompt and launch python tools\plugin_packager.py
from inside the Isogeo plugin qgis repository.

See: http://www.qgis.org/pyqgis-cookbook/releasing.html
        Authors: J. Moura
        Python: 2.7.x
        Created: 20/07/2016
        Licence: GPL 3
"""

# ------------ Imports --------------------------------------------
from os import listdir, makedirs, path
import zipfile

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
final_zip.write(r"modules\api.py", plg_dir + r"\modules\api.py")

# Resources
resources_files = [path.relpath(f) for f in listdir(r"resources")
                   if path.isfile(path.join(path.realpath(r"resources"), f))]

for resource in resources_files:
    final_zip.write(r"resources\\" + resource,
                    plg_dir + r"\resources\\" + resource)

# Translations
final_zip.write(r"i18n\isogeo_search_engine_fr.qm", plg_dir + r"\i18n\isogeo_search_engine_fr.qm")

# UI - Base
final_zip.write(r"icon.png", plg_dir + r"\icon.png")
final_zip.write(r"ui\__init__.py", plg_dir + r"\ui\__init__.py")
final_zip.write(r"ui\isogeo_dockwidget_base.ui", plg_dir + r"\ui\isogeo_dockwidget_base.ui")
final_zip.write(r"ui\isogeo_dockwidget.py", plg_dir + r"\ui\isogeo_dockwidget.py")
final_zip.write(r"ui\ui_isogeo.py", plg_dir + r"\ui\ui_isogeo.py")
final_zip.write(r"resources.py", plg_dir + r"\resources.py")
# final_zip.write(r"resources.qrc", plg_dir + r"\resources.qrc")

# UI - Auth
final_zip.write(r"ui\auth\__init__.py", plg_dir + r"\ui\auth\__init__.py")
final_zip.write(r"ui\auth\ui_authentication.ui", plg_dir + r"\ui\auth\ui_authentication.ui")
final_zip.write(r"ui\auth\ui_authentication.py", plg_dir + r"\ui\auth\ui_authentication.py")
final_zip.write(r"ui\auth\dlg_authentication.py", plg_dir + r"\ui\auth\dlg_authentication.py")

# UI - MdDetails
final_zip.write(r"ui\mddetails\__init__.py", plg_dir + r"\ui\mddetails\__init__.py")
final_zip.write(r"ui\mddetails\isogeo_md_details.ui", plg_dir + r"\ui\mddetails\isogeo_md_details.ui")
final_zip.write(r"ui\mddetails\isogeo_dlg_mdDetails.py", plg_dir + r"\ui\mddetails\isogeo_dlg_mdDetails.py")
final_zip.write(r"ui\mddetails\ui_isogeo_md_details.py", plg_dir + r"\ui\mddetails\ui_isogeo_md_details.py")

# UI - Saved search - name
final_zip.write(r"ui\name\__init__.py", plg_dir + r"\ui\name\__init__.py")
final_zip.write(r"ui\name\ask_research_name.py", plg_dir + r"\ui\name\ask_research_name.py")
final_zip.write(r"ui\name\ask_research_name.ui", plg_dir + r"\ui\name\ask_research_name.ui")
final_zip.write(r"ui\name\ui_ask_research_name.py", plg_dir + r"\ui\name\ui_ask_research_name.py")

# UI - Saved search - rename
final_zip.write(r"ui\rename\__init__.py", plg_dir + r"\ui\rename\__init__.py")
final_zip.write(r"ui\rename\ask_new_name.py", plg_dir + r"\ui\rename\ask_new_name.py")
final_zip.write(r"ui\rename\ask_new_name.ui", plg_dir + r"\ui\rename\ask_new_name.ui")
final_zip.write(r"ui\rename\ui_ask_new_name.py", plg_dir + r"\ui\rename\ui_ask_new_name.py")

# User settings
final_zip.write(r"user_settings\saved_researches.json", plg_dir + r"\user_settings\saved_researches.json")

# ----------------------------------------------------------------------------
