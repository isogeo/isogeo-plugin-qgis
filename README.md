# Isogeo for QGIS
[![Build Status](https://dev.azure.com/isogeo/plugin-qgis/_apis/build/status%2Fplugin-qgis-main?repoName=isogeo%2Fisogeo-plugin-qgis&branchName=master)](https://dev.azure.com/isogeo/plugin-qgis/_build/latest?definitionId=179&repoName=isogeo%2Fisogeo-plugin-qgis&branchName=master)

![Isogeo plugin for QGIS - Logo](https://user-images.githubusercontent.com/41120579/185194393-83a13809-73e6-4590-8b64-669bf09179e0.png)

QGIS plugin from [Isogeo](https://www.isogeo.com/), a SaaS software to give an easier access to geodata.
Equivalent of [plugins for ArcGIS](https://www.isogeo.com/nos-produits/Plugins-Widgets).

You can see and vote for [this plugin on the official QGIS extensions website](https://plugins.qgis.org/plugins/isogeo_search_engine/).

[Online documentation is available here](http://help.isogeo.com/qgis/).

## Purpose

Allow Isogeo users to search for datas in their own and external metadata catalogs and add it to a QGIS project. Its goal is to improve access to internal and external geodata.

## How does it works

### Technical

It's based on Isogeo API:

* REST-ful
* oAuth2 protocol used to authenticate shares

It's fully integrated with QGIS ecosystem:

* PyQGIS 3
* PyQt 5.11.x

### Features

* [X] Text search among Isogeo shares
* [X] Dynamic filter on keywords, INSPIRE themes, group themes, catalog owners, source coordinate system, license, data type (vector, raster...), source format and contacts
* [X] Geographic filter from a layer bounding box
* [X] Geographic filter from the map canvas bounding box
* [X] Order results by relevance, alphabetic, last updated date (data or metadata), creation date (data or metadata)
* [X] Add the related data directly to the map canvas throught raw data or web services
* [X] Display full metadata information in a separated window
* [X] Save search bookmarks

## Screen captures

| Without any search | With some filters |
|:------------------:|:-----------------:|
| ![Search widget with no filters](img/en/ui_tabs_main_search_empty_en.png) | ![Search widget with some filters](img/en/ui_tabs_main_search_filtered_en.png) |

![Add data to the project](img/en/ui_tabs_main_add_service_wms_en.png)

## Getting started

In a nutshell:

1. QGIS *Plugins* menu -> *Manage and Install Plugins...*;
2. Search for *isogeo*, select it and install it.

If you want a more advanced version, check the box allowing experimental extensions in settings.

See the documentation:

* en [français](http://help.isogeo.com/qgis/fr/) ;
* in [English](http://help.isogeo.com/qgis/en/).
