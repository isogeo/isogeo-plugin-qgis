echo "Updating translations"
pylupdate5 -noobsolete -verbose isogeo_search_engine.pro

Echo "Compilating QT ui to Python classes"
pyuic5 -x "ui\isogeo_dockwidget_base.ui" -o "ui\ui_isogeo.py"
pyuic5 -x "ui\auth\ui_authentication.ui" -o "ui\auth\ui_authentication.py"
pyuic5 -x "ui\credits\ui_credits.ui" -o "ui\credits\ui_credits.py"
pyuic5 -x "ui\metadata\ui_md_details.ui" -o "ui\metadata\ui_md_details.py"
pyuic5 -x "ui\quicksearch\ui_quicksearch_rename.ui" -o "ui\quicksearch\ui_quicksearch_rename.py"
pyuic5 -x "ui\quicksearch\ui_quicksearch_new.ui" -o "ui\quicksearch\ui_quicksearch_new.py"

Echo "Updating Qt resources files (images)"
pyrcc5 -o resources.py resources.qrc

Echo "Packaging plugin"
python tools\plugin_packager.py

Echo "End of compilation."
Echo "Remind that you have to remove 'import resources_rc' at the end of py files generated from ui."
