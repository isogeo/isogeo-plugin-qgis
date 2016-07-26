# -*- coding: UTF-8 -*-
#!/usr/bin/env python
"""This script packages files into a zip ready to be uploaded to QGIS plugins
repository.
See: http://www.qgis.org/pyqgis-cookbook/releasing.html
        Authors: J. Moura
        Python: 2.7.x
        Created: 20/07/2016
        Licence: GPL 3
"""

# ------------ Destination folder --------------------------------------------
import ConfigParser     # to manage ini files
from os import makedirs, path
import zipfile
# ------------ Destination folder --------------------------------------------


# ------------ Destination folder --------------------------------------------
# folder name
plg_dir = "isogeo_search_engine"

# where to store the zip files
dest_folder = path.abspath(r"build\latest")

if not path.isdir(dest_folder):    # test if folder already exists
    makedirs(dest_folder, 0777)
else:
    pass
# ----------------------------------------------------------------------------

# ------------ Generic config file -------------------------------------------
# initial settings
confile = path.join(dest_folder, 'config.ini')
config = ConfigParser.SafeConfigParser()
# add sections
config.add_section('Isogeo_ids')
# basics
config.set('Isogeo_ids', 'application_id', 'app_id')
config.set('Isogeo_ids', 'application_secret', 'app_secret')
# Writing the configuration file
with open(confile, 'wb') as configfile:
    config.write(configfile)
# ----------------------------------------------------------------------------

# ------------ Led Zipping -------------------------------------------
final_zip = zipfile.ZipFile(path.join(dest_folder, plg_dir + ".zip"), "w")

# custom
final_zip.write(confile, plg_dir + r"\config.ini")

# QGIS Plugin requirements
final_zip.write(r"LICENSE", plg_dir + r"\LICENSE")
final_zip.write(r"Makefile", plg_dir + r"\Makefile")
final_zip.write(r"metadata.txt", plg_dir + r"\metadata.txt")
final_zip.write(r"README.md", plg_dir + r"\README")

# UI
final_zip.write(r"authentification.ui", plg_dir + r"\authentification.ui")
final_zip.write(r"icon.png", plg_dir + r"\icon.png")
final_zip.write(r"isogeo_dockwidget_base.ui", plg_dir + r"\isogeo_dockwidget_base.ui")
final_zip.write(r"resources.py", plg_dir + r"\resources.py")
final_zip.write(r"resources.qrc", plg_dir + r"\resources.qrc")

# Python code
final_zip.write(r"__init__.py", plg_dir + r"\__init__.py")
final_zip.write(r"authentification.py", plg_dir + r"\authentification.py")
final_zip.write(r"isogeo.py", plg_dir + r"\isogeo.py")
final_zip.write(r"isogeo_dockwidget.py", plg_dir + r"\isogeo_dockwidget.py")
final_zip.write(r"ui_authentification.py", plg_dir + r"\ui_authentification.py")
final_zip.write(r"ui_isogeo.py", plg_dir + r"\ui_isogeo.py")

# Translations
# final_zip.write("i18n\af.ts")

# ----------------------------------------------------------------------------
