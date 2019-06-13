## Why

This plugin has been developed according to [Issue](https://github.com/isogeo/isogeo-plugin-qgis/issues/186).
It allows you to do the same as the *external_module* (`api_auth_with_qt\external_module`) in the QGIS environment by using the `QgsNetworkAccessManager` class instead of the `QNetworkAccessManager` class.

## How to use it

1. Install [*Plugin-Builder*](https://plugins.qgis.org/plugins/pluginbuilder/) in QGIS3

2. Use it to create a new plugin named *api_with_qt*

3. In the plugin folder (`...\QGIS3\profiles\default\python\plugins\api_with_qt`), replace original `api_with_qt_dialop.py` and `api_with_qt.py` files by those in this folder (`api_auth_with_qt\for_qgis_plugin`)

4. Enable the *api_with_qt* plugin in QGIS 3 and launch it.
