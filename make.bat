Echo "Updating translations"
call pylupdate5 -noobsolete -verbose isogeo_search_engine.pro
call qt5-tools lrelease .\i18n\isogeo_search_engine_en.ts
call qt5-tools lrelease .\i18n\isogeo_search_engine_fr.ts
call qt5-tools lrelease .\i18n\isogeo_search_engine_es.ts
call qt5-tools lrelease .\i18n\isogeo_search_engine_pt_BR.ts

Echo "Compilating QT ui to Python classes"
call pyuic5 -x "ui\isogeo_dockwidget_base.ui" -o "ui\ui_isogeo.py"
call pyuic5 -x "ui\auth\ui_authentication.ui" -o "ui\auth\ui_authentication.py"
call pyuic5 -x "ui\credits\ui_credits.ui" -o "ui\credits\ui_credits.py"
call pyuic5 -x "ui\db_connections\ui_db_connections.ui" -o "ui\db_connections\ui_db_connections.py"
call pyuic5 -x "ui\metadata\ui_md_details.ui" -o "ui\metadata\ui_md_details.py"
call pyuic5 -x "ui\quicksearch\ui_quicksearch_rename.ui" -o "ui\quicksearch\ui_quicksearch_rename.py"
call pyuic5 -x "ui\quicksearch\ui_quicksearch_new.ui" -o "ui\quicksearch\ui_quicksearch_new.py"
call pyuic5 -x "ui\portal\ui_portal_base_url.ui" -o "ui\portal\ui_portal_base_url.py"

Echo "Updating Qt resources files (images)"
call pyrcc5 resources.qrc -o resources_rc.py

Echo "Packaging plugin"
call python tools\plugin_packager.py

Echo "End of compilation."
Echo "Remind that you have to remove 'import resources_rc' at the end of py files generated from ui."
