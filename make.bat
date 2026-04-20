Echo "Updating translations"
call pylupdate5 -noobsolete -verbose isogeo_search_engine.pro
call qt5-tools lrelease .\i18n\isogeo_search_engine_en.ts
call qt5-tools lrelease .\i18n\isogeo_search_engine_fr.ts
call qt5-tools lrelease .\i18n\isogeo_search_engine_es.ts
call qt5-tools lrelease .\i18n\isogeo_search_engine_pt_BR.ts

Echo "Updating Qt resources files (images)"
call pyrcc5 resources.qrc -o resources_rc.py
powershell -Command "(Get-Content resources_rc.py) -replace 'from PyQt5 import QtCore', 'from qgis.PyQt import QtCore' | Set-Content resources_rc.py"

Echo "Packaging plugin"
call python tools\plugin_packager.py

Echo "End of compilation."
