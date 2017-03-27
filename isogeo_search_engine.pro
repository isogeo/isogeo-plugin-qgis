FORMS = ui/isogeo_dockwidget_base.ui \
    ui/auth/ui_authentication.ui \
    ui/credits/ui_credits.ui \
    ui/metadata/ui_md_details.ui \
    ui/quicksearch/ui_quicksearch_new.ui \
    ui/quicksearch/ui_quicksearch_rename.ui

SOURCES = __init__.py \
	isogeo.py \
    modules\api.py \
    modules\metadata_display.py \
    modules\results.py \
    modules\tools.py \
    modules\url_builder.py \
	ui/isogeo_dockwidget.py \
	ui/auth/ui_authentication.py \
    ui/credits/ui_credits.py \
    ui/metadata/ui_md_details.py \
	ui/quicksearch/ui_quicksearch_new.py \
	ui/quicksearch/ui_quicksearch_rename.py

TRANSLATIONS = i18n/isogeo_search_engine_fr.ts \
	i18n/isogeo_search_engine_en.ts
