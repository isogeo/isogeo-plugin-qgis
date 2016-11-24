echo "Updating translations"
pylupdate4 -noobsolete -verbose isogeo_search_engine.pro

Echo "Compilating QT ui to Python classes"
pyuic4 -x "ui\isogeo_dockwidget_base.ui" -o "ui\ui_isogeo.py"
pyuic4 -x "ui\auth\ui_authentication.ui" -o "ui\auth\ui_authentication.py"
pyuic4 -x "ui\credits\ui_credits.ui" -o "ui\credits\ui_credits.py"
pyuic4 -x "ui\mddetails\ui_md_details.ui" -o "ui\mddetails\ui_md_details.py"
pyuic4 -x "ui\quicksearch\ui_quicksearch_rename.ui" -o "ui\quicksearch\ui_quicksearch_rename.py"
pyuic4 -x "ui\quicksearch\ui_quicksearch_new.ui" -o "ui\quicksearch\ui_quicksearch_new.py"

Echo "Updating Qt resources files (images)"
pyrcc4 -o resources.py resources.qrc

Echo "End of compilation."
Echo "Remind that you have to remove 'import resources_rc' at the end of py files generated from ui."
