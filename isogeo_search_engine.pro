FORMS = ui/isogeo_dockwidget_base.ui \
    ui/auth/ui_authentication.ui \
    ui/credits/ui_credits.ui \
    ui/db_connections/ui_db_connections.ui \
    ui/metadata/ui_md_details.ui \
    ui/quicksearch/ui_quicksearch_new.ui \
    ui/quicksearch/ui_quicksearch_rename.ui \
    ui/portal/ui_portal_base_url.ui

SOURCES = __init__.py \
	isogeo.py \
    modules/api/auth.py \
    modules/api/request.py \
    modules/api/shares.py \
    modules/layer/add_layer.py \
    modules/layer/limitations_checker.py \
    modules/layer/database.py \
    modules/quick_search.py \
    modules/results/cache.py \
    modules/results/display.py \
    modules/search_form.py \
    modules/tools.py \
    modules/user_inform.py \
    modules/metadata_display.py \
	ui/isogeo_dockwidget.py \
	ui/auth/ui_authentication.py \
    ui/credits/ui_credits.py \
    ui/db_connections/ui_db_connections.ui \
    ui/metadata/ui_md_details.py \
	ui/quicksearch/ui_quicksearch_new.py \
	ui/quicksearch/ui_quicksearch_rename.py\

TRANSLATIONS = i18n/isogeo_search_engine_fr.ts \
	i18n/isogeo_search_engine_en.ts \
	i18n/isogeo_search_engine_es.ts \
	i18n/isogeo_search_engine_pt_BR.ts \

