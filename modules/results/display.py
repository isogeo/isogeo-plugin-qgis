# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

# Standard library
import logging
from functools import partial
import json
import os

# PyQT
# from QByteArray
from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtGui import QIcon, QPixmap
from qgis.PyQt.QtWidgets import (QTableWidgetItem, QComboBox, QPushButton, QLabel, 
                                QProgressBar, QHeaderView)
# PyQGIS
from qgis.utils import iface

# Plugin modules
from .cache import CacheManager
from ..tools import IsogeoPlgTools
from ..layer.add_layer import LayerAdder

# ############################################################################
# ########## Globals ###############
# ##################################

plg_tools = IsogeoPlgTools()

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
li_formats_vect = ("shp", "dxf", "dgn", "filegdb", "tab")
li_formats_rastr = ("esriasciigrid", "geotiff",
                    "intergraphgdb", "jpeg", "png", "xyz", "ecw")

# Qt icons
# see https://github.com/qgis/QGIS/blob/master/images/images.qrc
pix_point = QPixmap(":/images/themes/default/mIconPointLayer.svg")
pix_polyg = QPixmap(":/images/themes/default/mIconPolygonLayer.svg")
pix_line = QPixmap(":/images/themes/default/mIconLineLayer.svg")
pix_rastr = QPixmap(":/images/themes/default/mIconRaster.svg")
pix_multi = QPixmap(":/plugins/Isogeo/resources/multi.svg").scaledToWidth(20)
pix_nogeo = QPixmap(":/plugins/Isogeo/resources/none.svg").scaledToWidth(20)
pix_serv = QPixmap(":/plugins/Isogeo/resources/results/cloud.svg").scaledToWidth(20)
ico_efs = QIcon(":/images/themes/default/mIconAfs.svg")
ico_ems = QIcon(":/images/themes/default/mIconAms.svg")
ico_wfs = QIcon(":/images/themes/default/mIconWfs.svg")
ico_wms = QIcon(":/images/themes/default/mIconWms.svg")
ico_wmts = QIcon(":/images/themes/default/mIconWcs.svg")
ico_pgis = QIcon(":/images/themes/default/mIconPostgis.svg")
ico_file = QIcon(":/images/themes/default/mActionFileNew.svg")

# ############################################################################
# ########## Classes ###############
# ##################################


class ResultsManager(object):
    """Basic class that holds utilitary methods for the plugin."""

    def __init__(self, isogeo_plugin):
        """Class constructor."""
        self.isogeo_widget = isogeo_plugin.dockwidget
        self.send_details_request = isogeo_plugin.send_details_request
        self.tr = isogeo_plugin.tr

        self.layer_adder = LayerAdder()
        self.layer_adder.tr = self.tr
        self.add_layer = self.layer_adder.adding
        self.pg_connections = self.build_postgis_dict(qsettings)

        self.path_cache_file = os.path.realpath(os.path.join(isogeo_plugin.plg_basepath, "_user", "paths_cache.json"))
        self.cache_mng = CacheManager(self.path_cache_file)

    def show_results(self, api_results, tbl_result=None, pg_connections=dict(), progress_bar=QProgressBar):
        """Display the results in a table ."""
        logger.info("Results manager called. Displaying the results")
        # check parameters
        if not tbl_result:
            tbl_result = self.isogeo_widget.tbl_result
        else:
            pass
        self.layer_adder.tbl_result = tbl_result
        # Get the name (and other informations) of all databases whose
        # connection is set up in QGIS
        if pg_connections == {}:
            pg_connections = self.pg_connections
        else:
            pass
        # Set table rows
        if api_results.get("total") >= 10:
            tbl_result.setRowCount(10)
        else:
            tbl_result.setRowCount(api_results.get("total"))

        # Looping inside the table lines. For each of them, showing the title,
        # abstract, geometry type, and a button that allow to add the data
        # to the canvas.
        count = 0
        for i in api_results.get("results"):
            # get useful metadata
            md_id = i.get("_id")
            md_keywords = [i.get("tags").get(k)
                           for k in i.get("tags", ["NR", ])
                           if k.startswith("keyword:isogeo")]
            md_title = i.get("title", "NR")
            ds_geometry = i.get("geometry")

            # COLUMN 1 - Title and abstract
            # Displaying the metadata title inside a button
            btn_md_title = QPushButton(plg_tools.format_button_title(md_title))
            # Connecting the button to the full metadata popup
            btn_md_title.pressed.connect(partial(
                self.send_details_request, md_id=md_id))
            # Putting the abstract as a tooltip on this button
            btn_md_title.setToolTip(i.get("abstract", "")[:300])
            # Insert it in column 1
            tbl_result.setCellWidget(count, 0, btn_md_title)

            # COLUMN 2 - Data last update
            tbl_result.setItem(
                count, 1, QTableWidgetItem(
                    plg_tools.handle_date(i.get("_modified"))))

            # COLUMN 3 - Geometry type
            lbl_geom = QLabel(tbl_result)
            if ds_geometry:
                if ds_geometry in point_list:
                    lbl_geom.setPixmap(pix_point)
                    lbl_geom.setToolTip(self.tr("Point", "ResultsManager"))
                elif ds_geometry in polygon_list:
                    lbl_geom.setPixmap(pix_polyg)
                    lbl_geom.setToolTip(self.tr("Polygon", "ResultsManager"))
                elif ds_geometry in line_list:
                    lbl_geom.setPixmap(pix_line)
                    lbl_geom.setToolTip(self.tr("Line", "ResultsManager"))
                elif ds_geometry in multi_list:
                    lbl_geom.setPixmap(pix_multi)
                    lbl_geom.setToolTip(self.tr("MultiPolygon", "ResultsManager"))
                elif ds_geometry == "TIN":
                    tbl_result.setItem(
                        count, 2, QTableWidgetItem(u"TIN"))
                else:
                    tbl_result.setItem(
                        count, 2, QTableWidgetItem(
                            self.tr("Unknown geometry", "ResultsManager")))
            else:
                if "rasterDataset" in i.get("type"):
                    lbl_geom.setPixmap(pix_rastr)
                    lbl_geom.setToolTip(self.tr("Raster", "ResultsManager"))
                elif "service" in i.get("type"):
                    lbl_geom.setPixmap(pix_serv)
                    lbl_geom.setToolTip(self.tr("Service", "ResultsManager"))
                else:
                    lbl_geom.setPixmap(pix_nogeo)
                    lbl_geom.setToolTip(self.tr("Unknown geometry", "ResultsManager"))

            tbl_result.setCellWidget(count, 2, lbl_geom)

            # COLUMN 4 - Add options
            dico_add_options = {}

            # Files and PostGIS direct access
            if "format" in i.keys():
                # If the data is a vector and the path is available, store
                # useful information in the dict
                if i.get("format", "NR") in li_formats_vect and "path" in i:
                    add_path = self._filepath_builder(i.get("path"))
                    if add_path:
                        params = ["vector", add_path,
                                  i.get("title", "NR"),
                                  i.get("abstract", "NR"),
                                  md_keywords]
                        dico_add_options[self.tr("Data file", "ResultsManager")] = params
                    else:
                        pass
                # Same if the data is a raster
                elif i.get("format", "NR") in li_formats_rastr and "path" in i:
                    add_path = self._filepath_builder(i.get("path"))
                    if add_path:
                        params = ["raster", add_path,
                                  i.get("title", "NR"),
                                  i.get("abstract", "NR"),
                                  md_keywords]
                        dico_add_options[self.tr("Data file", "ResultsManager")] = params
                    else:
                        pass
                # If the data is a postGIS table and the connexion has
                # been saved in QGIS.
                elif i.get("format") == "postgis":
                    base_name = i.get("path", "No path")
                    if base_name in pg_connections.keys():
                        params = {}
                        params["base_name"] = base_name
                        schema_table = i.get("name")
                        if schema_table is not None and "." in schema_table:
                            params["schema"] = schema_table.split(".")[0]
                            params["table"] = schema_table.split(".")[1]
                            params["abstract"] = i.get("abstract", None)
                            params["title"] = i.get("title", None)
                            params["keywords"] = md_keywords
                            dico_add_options[self.tr("PostGIS table", "ResultsManager")] = params
                        else:
                            pass
                    else:
                        pass
                else:
                    logger.debug("Metadata {} has a format but it's not recognized or path is missing".format(md_id))
                    pass
            # Associated service layers
            d_type = i.get("type")
            if d_type == "vectorDataset" or d_type == "rasterDataset":
                for layer in i.get("serviceLayers"):
                    service = layer.get("service")
                    if service is not None:
                        srv_details = {"path": service.get("path", "NR"),
                                       "formatVersion": service.get("formatVersion")}
                        # EFS
                        if service.get("format") == "efs":
                            params = self.layer_adder.build_efs_url(layer, srv_details,
                                                                 rsc_type="ds_dyn_lyr_srv",
                                                                 mode="quicky")
                        # EMS
                        elif service.get("format") == "ems":
                            params = self.layer_adder.build_ems_url(layer, srv_details,
                                                                 rsc_type="ds_dyn_lyr_srv",
                                                                 mode="quicky")
                        # WFS
                        elif service.get("format") == "wfs":
                            params = self.layer_adder.build_wfs_url(layer, srv_details,
                                                                 rsc_type="ds_dyn_lyr_srv",
                                                                 mode="quicky")

                        # WMS
                        elif service.get("format") == "wms":
                            params = self.layer_adder.build_wms_url(layer, srv_details,
                                                                 rsc_type="ds_dyn_lyr_srv",
                                                                 mode="quicky")
                        # WMTS
                        elif service.get("format") == "wmts":
                            params = self.layer_adder.build_wmts_url(layer, srv_details,
                                                                  rsc_type="ds_dyn_lyr_srv") 
                        else:
                            pass

                        if params[0] != 0:
                            basic_md = [i.get("title", "NR"), i.get("abstract", "NR"), md_keywords]
                            params.append(basic_md)
                            dico_add_options["{} : {}".format(params[0], params[1])] = params
                        else:
                            pass
                    else:
                        pass
            # New association mode. For services metadata sheet, the layers
            # are stored in the purposely named include: "layers".
            elif i.get("type") == "service":
                if i.get("layers") is not None:
                    srv_details = {"path": i.get("path", "NR"),
                                   "formatVersion": i.get("formatVersion")}
                    # EFS
                    if i.get("format") == "efs":
                        for layer in i.get("layers"):
                            name_url = self.layer_adder.build_efs_url(layer, srv_details,
                                                                  rsc_type="service",
                                                                  mode="quicky")
                            if name_url[0] != 0:
                                dico_add_options[name_url[5]] = name_url
                            else:
                                continue
                    # EMS
                    if i.get("format") == "ems":
                        for layer in i.get("layers"):
                            name_url = self.layer_adder.build_ems_url(layer, srv_details,
                                                                  rsc_type="service",
                                                                  mode="quicky")
                            if name_url[0] != 0:
                                dico_add_options[name_url[5]] = name_url
                            else:
                                continue
                    # WFS
                    if i.get("format") == "wfs":
                        for layer in i.get("layers"):
                            name_url = self.layer_adder.build_wfs_url(layer, srv_details,
                                                                 rsc_type="service",
                                                                 mode="quicky")
                            if name_url[0] != 0:
                                dico_add_options[name_url[5]] = name_url
                            else:
                                continue
                    # WMS
                    elif i.get("format") == "wms":
                        for layer in i.get("layers"):
                            name_url = self.layer_adder.build_wms_url(layer, srv_details,
                                                                 rsc_type="service",
                                                                 mode="quicky")
                            if name_url[0] != 0:
                                dico_add_options[name_url[5]] = name_url
                            else:
                                continue
                    # WMTS
                    elif i.get("format") == "wmts":
                        for layer in i.get("layers"):
                            name_url = self.layer_adder.build_wmts_url(layer, srv_details,
                                                                  rsc_type="service")
                            if name_url[0] != 0:
                                btn_label = "WMTS : {}".format(name_url[1])
                                dico_add_options[btn_label] = name_url
                            else:
                                continue
                    else:
                        pass
            else:
                pass

            # Now the plugin has tested every possibility for the layer to be
            # added. The "Add" column has to be filled accordingly.

            # If the data can't be added, just insert "can't" text.
            if dico_add_options == {}:
                text = self.tr("Can't be added", "ResultsManager")
                fake_button = QPushButton(text)
                fake_button.setStyleSheet("text-align: left")
                fake_button.setEnabled(False)
                tbl_result.setCellWidget(count, 3, fake_button)
            # If there is only one way for the data to be added, insert a
            # button.
            elif len(dico_add_options) == 1:
                text = list(dico_add_options.keys())[0]
                params = dico_add_options.get(text)
                if text.startswith("WFS"):
                    icon = ico_wfs
                elif text.startswith("WMS"):
                    icon = ico_wms
                elif text.startswith("WMTS"):
                    icon = ico_wmts
                elif text.startswith("EFS"):
                    icon = ico_efs
                elif text.startswith("EMS"):
                    icon = ico_ems
                elif text.startswith(self.tr("PostGIS table", "ResultsManager")):
                    icon = ico_pgis
                elif text.startswith(self.tr("Data file", "ResultsManager")):
                    icon = ico_file
                else :
                    logger.debug("text : {}".format(text))
                add_button = QPushButton(icon, text)
                add_button.setStyleSheet("text-align: left")
                add_button.pressed.connect(partial(self.add_layer,
                                                   layer_info=["info", params])
                                           )
                tbl_result.setCellWidget(count, 3, add_button)
            # Else, add a combobox, storing all possibilities.
            else:
                combo = QComboBox()
                for i in dico_add_options:
                    if i.startswith("WFS"):
                        icon = ico_wfs
                    elif i.startswith("WMS"):
                        icon = ico_wms
                    elif i.startswith("WMTS"):
                        icon = ico_wmts
                    elif i.startswith("EFS"):
                        icon = ico_efs
                    elif i.startswith("EMS"):
                        icon = ico_ems
                    elif i.startswith(self.tr("PostGIS table", "ResultsManager")):
                        icon = ico_pgis
                    elif i.startswith(self.tr("Data file", "ResultsManager")):
                        icon = ico_file
                    combo.addItem(icon, i, dico_add_options.get(i))
                combo.activated.connect(partial(self.add_layer,
                                                layer_info=["index", count]))
                combo.model().sort(0)   # sort alphabetically on option prefix. see: #113
                tbl_result.setCellWidget(count, 3, combo)

            count += 1
        # dimensions
        header = tbl_result.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        # Remove the "loading" bar
        iface.mainWindow().statusBar().removeWidget(progress_bar)
        # method ending
        return None

    # -- PRIVATE METHOD -------------------------------------------------------
    def _filepath_builder(self, metadata_path, mode=1):
        """Build filepath from metadata path handling various cases. See: #129.

        :param dict metadata_path: path found in metadata
        :param int mode: mode to apply. Options:
          1 = only with standard path.normpath
          2 = using raw string (useful for Windows systems)
        """
        # basic checks
        if not isinstance(mode, int):
            raise TypeError
        # building
        if mode == 1:
            filepath = os.path.normpath(metadata_path)
            dir_file = os.path.dirname(filepath)
            if dir_file not in self.cache_mng.cached_unreach_paths:
                try:
                    with open(filepath) as f:
                        return filepath
                except IOError:
                    logger.debug("Filepath is not reachable: {}".format(filepath))
                    return self._filepath_builder(metadata_path, mode=2)
            else:
                logger.debug("Path has been ignored because it's cached.")
                return False
        elif mode == 2:
            logger.debug("Using forced raw string")
            filepath = plg_tools._to_raw_string(metadata_path)
            dir_file = os.path.dirname(metadata_path)
            try:
                with open(filepath) as f:
                    return filepath
            except IOError:
                self.cache_mng.cached_unreach_paths.append(dir_file)
                logger.debug("Path is not reachable and has been cached:{}".format(dir_file))
                return False
        else:
            logger.debug("Incorrect mode: {}".format(mode))
            raise ValueError

    def build_postgis_dict(self, input_dict):
        """Build the dict that stores informations about PostGIS connexions."""
        # input_dict.beginGroup("PostgreSQL/connections")
        final_dict = {}
        for k in sorted(input_dict.allKeys()):
            if k.startswith("PostgreSQL/connections/")\
                    and k.endswith("/database"):
                if len(k.split("/")) == 4:
                    connection_name = k.split("/")[2]
                    password_saved = input_dict.value(
                        'PostgreSQL/connections/' +
                        connection_name +
                        '/savePassword')
                    user_saved = input_dict.value(
                        'PostgreSQL/connections/' +
                        connection_name +
                        '/saveUsername')
                    if password_saved == 'true' and user_saved == 'true':
                        dictionary = {'name':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/database'),
                                      'host':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/host'),
                                      'port':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/port'),
                                      'username':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/username'),
                                      'password':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/password')}
                        final_dict[
                            input_dict.value('PostgreSQL/connections/' +
                                             connection_name +
                                             '/database')
                        ] = dictionary
                    else:
                        continue
                else:
                    pass
            else:
                pass
        return final_dict


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == '__main__':
    """Standalone execution."""
