echo "Updating translations"
pylupdate4 -noobsolete isogeo_search_engine.pro

Echo "Compilating QT ui to Python classes"
pyuic4 -x ui\ui_authentication.ui -o ui\ui_authentication.py

Echo "Updating Qt resources files (images)"
pyrcc4 -o resources.py resources.qrc

Echo "End of compilation."
Echo "Remind that you have to remove 'import resources_rc' at the end of py files generated from ui."
