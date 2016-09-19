echo "Updating translations"
pylupdate4 -noobsolete -verbose isogeo_search_engine.pro

Echo "Compilating QT ui to Python classes"
pyuic4 -x "ui\isogeo_dockwidget_base.ui" -o "ui\ui_isogeo.py"
pyuic4 -x "ui\auth\ui_authentication.ui" -o "ui\auth\ui_authentication.py"
pyuic4 -x "ui\mddetails\isogeo_md_details.ui" -o "ui\mddetails\ui_isogeo_md_details.py"
pyuic4 -x "ui\name\ask_research_name.ui" -o "ui\name\ui_ask_research_name.py"
pyuic4 -x "ui\rename\ask_new_name.ui" -o "ui\rename\ui_ask_new_name.py"

Echo "Updating Qt resources files (images)"
pyrcc4 -o resources.py resources.qrc

Echo "End of compilation."
Echo "Remind that you have to remove 'import resources_rc' at the end of py files generated from ui."


rem @sed -re 's/import resources_rc/from QuickOSM import resources_rc/g' ui/osm_file_temp.py > ui/osm_file.py
