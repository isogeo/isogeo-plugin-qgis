# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

# Standard library
import logging
from functools import partial

# PyQT
# from QByteArray
from PyQt4.QtCore import QSettings
from PyQt4.QtGui import (QIcon, QTableWidgetItem, QComboBox, QPushButton,
                         QLabel, QPixmap, QProgressBar)

# PyQGIS
from qgis.utils import iface

# Custom modules
from .tools import Tools
from .url_builder import UrlBuilder

# ############################################################################
# ########## Globals ###############
# ##################################

custom_tools = Tools()
srv_url_bld = UrlBuilder()
qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

# Isogeo geometry types
polygon_list = ("CurvePolygon", "MultiPolygon",
                "MultiSurface", "Polygon", "PolyhedralSurface")
point_list = ("Point", "MultiPoint")
line_list = ("CircularString", "CompoundCurve", "Curve",
             "LineString", "MultiCurve", "MultiLineString")
multi_list = ("Geometry", "GeometryCollection")

# Isogeo formats
vectorformat_list = ('shp', 'dxf', 'dgn', 'filegdb', 'tab')
rasterformat_list = ('esriasciigrid', 'geotiff',
                     'intergraphgdb', 'jpeg', 'png', 'xyz', 'ecw')


# Qt icons
lbl_polyg = QLabel().setPixmap(QPixmap(':/plugins/Isogeo/resources/polygon.png'))
lbl_point = QLabel().setPixmap(QPixmap(':/plugins/Isogeo/resources/point.png'))
lbl_line = QLabel().setPixmap(QPixmap(':/plugins/Isogeo/resources/line.png'))
lbl_multi = QLabel().setPixmap(QPixmap(':/plugins/Isogeo/resources/multi.png'))
lbl_rastr = QLabel().setPixmap(QPixmap(':/plugins/Isogeo/resources/raster.png'))
lbl_nogeo = QLabel().setPixmap(QPixmap(':/plugins/Isogeo/resources/ban.png'))

# ############################################################################
# ########## Classes ###############
# ##################################


class ResultsManager(object):
    """Basic class that holds utilitary methods for the plugin."""

    def __init__(self, isogeo_plugin):
        """Class constructor."""
        self.isogeo_widget = isogeo_plugin.dockwidget
        self.add_layer = isogeo_plugin.add_layer
        self.send_details_request = isogeo_plugin.send_details_request
        self.tr = isogeo_plugin.tr
        self.pg_connections = srv_url_bld.build_postgis_dict(qsettings)

    def show_results(self, api_results, tbl_result=None, pg_connections=dict(), progress_bar=QProgressBar):
        """Display the results in a table ."""
        logger.info("Results manager called. Displaying the results")
        # check parameters
        if not tbl_result:
            tbl_result = self.isogeo_widget.tbl_result
        else:
            pass
        # Get the name (and other informations) of all databases whose
        # connection is set up in QGIS
        if pg_connections == {}:
            pg_connections = self.pg_connections
        else:
            pass
        # Set rable rows
        if api_results.get('total') >= 10:
            tbl_result.setRowCount(10)
        else:
            tbl_result.setRowCount(api_results.get('total'))

        # Looping inside the table lines. For each of them, showing the title,
        # abstract, geometry type, and a button that allow to add the data
        # to the canvas.
        count = 0
        for i in api_results.get('results'):
            # get useful metadata
            md_id = i.get('_id')
            md_keywords = [i.get("tags").get(k)
                           for k in i.get("tags", ["NR", ])
                           if k.startswith("keyword:isogeo")]
            md_title = i.get("title", "NR")
            ds_geometry = i.get('geometry')
            # Displaying the metadata title inside a button
            btn_md_title = QPushButton(custom_tools.format_button_title(md_title))
            # Connecting the button to the full metadata popup
            btn_md_title.pressed.connect(partial(
                self.send_details_request, md_id=md_id))
            # Putting the abstract as a tooltip on this button
            btn_md_title.setToolTip(i.get('abstract', "")[:300])
            # Insert it in column 1
            tbl_result.setCellWidget(
                count, 0, btn_md_title)
            # Insert the modification date in column 2
            tbl_result.setItem(
                count, 1, QTableWidgetItem(
                    custom_tools.handle_date(i.get('_modified'))))
            # Getting the geometry
            label = QLabel()
            if ds_geometry:
                # If the geometry type is point, insert point icon in column 3
                if ds_geometry in point_list:
                    tbl_result.setCellWidget(count, 2, lbl_point)
                # If the type is polygon, insert polygon icon in column 3
                elif ds_geometry in polygon_list:
                    tbl_result.setCellWidget(count, 2, lbl_polyg)
                # If the type is line, insert line icon in column 3
                elif ds_geometry in line_list:
                    tbl_result.setCellWidget(count, 2, lbl_line)
                # If the type is multi, insert multi icon in column 3
                elif ds_geometry in multi_list:
                    tbl_result.setCellWidget(count, 2, lbl_multi)
                # If the type is TIN, insert TIN text in column 3
                elif ds_geometry == "TIN":
                    tbl_result.setItem(
                        count, 2, QTableWidgetItem(u'TIN'))
                # If the type isn't any of the above, unknown(shouldn't happen)
                else:
                    tbl_result.setItem(
                        count, 2, QTableWidgetItem(
                            self.tr('Unknown geometry', "ResultsManager")))
            # If the data doesn't have a geometry type
            else:
                # It may be a raster, then raster icon in column 3
                if "rasterDataset" in i.get('type'):
                    tbl_result.setCellWidget(count, 2, lbl_rastr)
                # Or it isn't spatial, then "no geometry" icon in column 3
                else:
                    tbl_result.setCellWidget(count, 2, lbl_nogeo)

            # We are still looping inside the table lines. For a given line, we
            # have displayed title, date, and geometry type. Now we have to
            # deal with the "add data" column. We need to see if the data can
            # be added directly, and/or using a geographical service.
            link_dict = {}

            if 'format' in i.keys():
                # If the data is a vector and the path is available, store
                # useful information in the dict
                if i.get('format', "NR") in vectorformat_list and 'path' in i:
                    path = custom_tools.format_path(i.get('path'))
                    try:
                        open(path)
                        params = ["vector", path,
                                  i.get("title", "NR"),
                                  i.get("abstract", "NR"),
                                  md_keywords]
                        link_dict[self.tr('Data file', "ResultsManager")] = params
                    except IOError:
                        pass
                # Same if the data is a raster
                elif i.get('format', "NR") in rasterformat_list and 'path' in i:
                    path = custom_tools.format_path(i.get('path'))
                    try:
                        open(path)
                        params = ["raster", path,
                                  i.get("title", "NR"),
                                  i.get("abstract", "NR"),
                                  md_keywords]
                        link_dict[self.tr('Data file', "ResultsManager")] = params
                    except IOError:
                        pass
                # If the data is a postGIS table and the connexion has
                # been saved in QGIS.
                elif i.get('format') == 'postgis':
                    # Récupère le nom de la base de données
                    base_name = i.get('path')
                    if base_name in pg_connections.keys():
                        params = {}
                        params['base_name'] = base_name
                        schema_table = i.get('name')
                        if schema_table is not None and "." in schema_table:
                            params['schema'] = schema_table.split(".")[0]
                            params['table'] = schema_table.split(".")[1]
                            params['abstract'] = i.get("abstract", None)
                            params['title'] = i.get("title", None)
                            params['keywords'] = md_keywords
                            link_dict[self.tr('PostGIS table', "ResultsManager")] = params
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            # We are now testing the WMS and WFS links that may be associated
            # to the metadata sheet

            # First, we look in "links". This is the old deprecated syntax.
            # At some point, all services should be associated using the new
            # one and this part of the code should be removed.
            for link in i.get('links'):
                # If the link is a WMS
                if link.get('kind') == 'wms':
                    # Test if all the needed information is in the url.
                    url = [link.get('title'), link.get('url')]
                    name_url = srv_url_bld.build_wms_url(url, rsc_type="link")
                    # In which case, store it in the dict.
                    if name_url != 0:
                        link_dict[u"WMS : " + name_url[1]] = name_url
                    else:
                        pass
                # If the link is a WFS
                elif link.get('kind') == 'wfs':
                    url = [link.get('title'), link.get('url')]
                    name_url = srv_url_bld.build_wfs_url(url, rsc_type="link")
                    if name_url != 0:
                        link_dict[u"WFS : " + name_url[1]] = name_url
                    else:
                        pass
                # If the link is a second level association
                elif link.get('type') == 'link':
                    _link = link.get('link')
                    if 'kind' in _link:
                        # WMS
                        if _link.get('kind') == 'wms':
                            url = [link.get('title'), link.get('url')]
                            name_url = srv_url_bld.build_wms_url(url, rsc_type="link")
                            if name_url != 0:
                                link_dict[u"WMS : " + name_url[1]] = name_url
                            else:
                                pass
                        # WFS
                        elif _link.get('kind') == 'wfs':
                            url = [link.get('title'), link.get('url')]
                            name_url = srv_url_bld.build_wfs_url(url, rsc_type="link")
                            if name_url != 0:
                                link_dict[u"WFS : " + name_url[1]] = name_url
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            # This is the new association mode. The layer and service
            # information are stored in the "serviceLayers" include, when
            # associated with a vector or raster data.
            d_type = i.get('type')
            if d_type == "vectorDataset" or d_type == "rasterDataset":
                for layer in i.get('serviceLayers'):
                    service = layer.get("service")
                    if service is not None:
                        srv_details = {"path": service.get("path", "NR"),
                                       "formatVersion": service.get("formatVersion")}
                        # WFS
                        if service.get("format") == "wfs":
                            try:
                                path = "{0}?typeName={1}".format(service.get("path"),
                                                                 layer.get("id"))
                            except UnicodeEncodeError:
                                logger.error("Encoding error in service layer name (UID). Metadata: {0} | service layer: {1}"
                                             .format(i.get("_id"),
                                                     layer.get("_id")))
                                continue
                            name_url = srv_url_bld.new_build_wfs_url(layer, srv_details,
                                                                     rsc_type="ds_dyn_lyr_srv",
                                                                     mode="quicky")
                            if name_url[0] != 0:
                                link_dict[name_url[5]] = name_url
                            else:
                                pass
                        # WMS
                        elif service.get("format") == "wms":
                            try:
                                path = "{0}?layers={1}".format(service.get("path"),
                                                               layer.get("id"))
                            except UnicodeEncodeError:
                                logger.error("Encoding error in service layer name (UID). Metadata: {0} | service layer: {1}"
                                             .format(i.get("_id"),
                                                     layer.get("_id")))
                                continue
                            name_url = srv_url_bld.new_build_wms_url(layer, srv_details,
                                                                     rsc_type="ds_dyn_lyr_srv",
                                                                     mode="quicky")
                            if name_url[0] != 0:
                                link_dict[name_url[5]] = name_url
                            else:
                                pass
                        # WMTS
                        elif service.get("format") == "wmts":
                            # try:
                            #     path = "{0}?layers={1}".format(service.get("path"),
                            #                                    layer.get("id"))
                            # except UnicodeEncodeError:
                            #     logger.error("Encoding error in service layer name (UID). Metadata: {0} | service layer: {1}"
                            #                  .format(i.get("_id"),
                            #                          layer.get("_id")))
                            #     continue
                            name_url = srv_url_bld.build_wmts_url(layer, srv_details,
                                                                  rsc_type="ds_dyn_lyr_srv")
                            if name_url[0] != 0:
                                link_dict[u"WMTS : " + name_url[1]] = name_url
                            else:
                                pass
                        else:
                            pass
                    else:
                        pass
            # New association mode. For services metadata sheet, the layers
            # are stored in the purposely named include: "layers".
            elif i.get('type') == "service":
                if i.get("layers") is not None:
                    srv_details = {"path": i.get("path", "NR"),
                                   "formatVersion": i.get("formatVersion")}
                    # WFS
                    if i.get("format") == "wfs":
                        for layer in i.get('layers'):
                            try:
                                path = "{0}?typeName={1}".format(srv_details.get("path"),
                                                                 layer.get("id"))
                            except UnicodeEncodeError:
                                logger.error("Encoding error in service layer name (UID). Metadata: {0} | service layer: {1}"
                                             .format(i.get("_id"),
                                                     layer.get("_id")))
                                continue
                            name_url = srv_url_bld.new_build_wfs_url(layer, srv_details,
                                                                     rsc_type="service",
                                                                     mode="quicky")
                            if name_url[0] != 0:
                                link_dict[name_url[5]] = name_url
                            else:
                                continue
                                pass
                    # WMS
                    elif i.get("format") == "wms":
                        for layer in i.get('layers'):
                            try:
                                path = "{0}?layers={1}".format(srv_details.get("path"),
                                                               layer.get("id"))
                            except UnicodeEncodeError:
                                logger.error("Encoding error in service layer name (UID). Metadata: {0} | service layer: {1}"
                                             .format(i.get("_id"),
                                                     layer.get("_id")))
                                continue
                            name_url = srv_url_bld.new_build_wms_url(layer, srv_details,
                                                                     rsc_type="service",
                                                                     mode="quicky")
                            if name_url[0] != 0:
                                link_dict[name_url[5]] = name_url
                                # link_dict["WMS : " + name_url[1]] = name_url
                            else:
                                continue
                                pass
                    # WMTS
                    elif i.get("format") == "wmts":
                        for layer in i.get('layers'):
                            # try:
                            #     path = "{0}?layers={1}".format(srv_details.get("path"),
                            #                                    layer.get("id"))
                            # except UnicodeEncodeError:
                            #     logger.error("Encoding error in service layer name (UID). Metadata: {0} | service layer: {1}"
                            #                  .format(i.get("_id"),
                            #                          layer.get("_id")))
                            #     continue
                            name_url = srv_url_bld.build_wmts_url(layer, srv_details,
                                                                  rsc_type="service")
                            if name_url[0] != 0:
                                btn_label = "WMTS : {}".format(name_url[1])
                                link_dict[btn_label] = name_url
                            else:
                                continue
                                pass
                    else:
                        pass
            else:
                pass

            # Now the plugin has tested every possibility for the layer to be
            # added. The "Add" column has to be filled accordingly.

            # If the data can't be added, just insert "can't" text.
            if link_dict == {}:
                text = self.tr("Can't be added", "ResultsManager")
                fake_button = QPushButton(text)
                fake_button.setStyleSheet("text-align: left")
                fake_button.setEnabled(False)
                tbl_result.setCellWidget(count, 3, fake_button)
            # If there is only one way for the data to be added, insert a
            # button.
            elif len(link_dict) == 1:
                text = link_dict.keys()[0]
                params = link_dict.get(text)
                if text.startswith("WMS"):
                    icon = QIcon(':/plugins/Isogeo/resources/wms.png')
                elif text.startswith("WFS"):
                    icon = QIcon(':/plugins/Isogeo/resources/wfs.png')
                elif text.startswith("WMTS"):
                    icon = QIcon(':/plugins/Isogeo/resources/wms.png')
                elif text.startswith(self.tr('PostGIS table', "ResultsManager")):
                    icon = QIcon(':/plugins/Isogeo/resources/database.svg')
                elif text.startswith(self.tr('Data file', "ResultsManager")):
                    icon = QIcon(':/plugins/Isogeo/resources/file.svg')
                add_button = QPushButton(icon, text)
                add_button.setStyleSheet("text-align: left")
                add_button.pressed.connect(partial(self.add_layer,
                                                   layer_info=["info", params])
                                           )
                tbl_result.setCellWidget(count, 3, add_button)
            # Else, add a combobox, storing all possibilities.
            else:
                combo = QComboBox()
                for key in link_dict.keys():
                    if key.startswith("WMS"):
                        icon = QIcon(':/plugins/Isogeo/resources/wms.png')
                    elif key.startswith("WFS"):
                        icon = QIcon(':/plugins/Isogeo/resources/wfs.png')
                    elif key.startswith("WMTS"):
                        icon = QIcon(':/plugins/Isogeo/resources/wms.png')
                    elif key.startswith(self.tr('PostGIS table', "ResultsManager")):
                        icon = QIcon(':/plugins/Isogeo/resources/database.svg')
                    elif key.startswith(self.tr('Data file', "ResultsManager")):
                        icon = QIcon(':/plugins/Isogeo/resources/file.svg')
                    combo.addItem(icon, key, link_dict[key])
                combo.activated.connect(partial(self.add_layer,
                                                layer_info=["index", count]))
                tbl_result.setCellWidget(count, 3, combo)

            count += 1
        # Remove the "loading" bar
        iface.mainWindow().statusBar().removeWidget(progress_bar)
        # method ending
        return None
