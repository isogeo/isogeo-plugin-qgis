# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

# Standard library
from datetime import datetime
import logging
import re
from urllib import unquote, urlencode
from urlparse import urlparse

# PyQT
from PyQt4.QtCore import QSettings, QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

# QGIS
from qgis.core import (QgsDataSourceURI, QgsNetworkAccessManager,
                       QgsVectorLayer, QgsMapLayerRegistry, QgsRasterLayer)

# Custom modules
from .tools import Tools

# ############################################################################
# ########## Globals ###############
# ##################################

custom_tools = Tools()
qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

qgis_wms_formats = ('image/png', 'image/png8',
                    'image/jpeg',
                    'image/svg',
                    'image/gif',
                    'image/geotiff', 'image/tiff')

# ############################################################################
# ##### Conditional imports ########
# ##################################

try:
    from owslib.wms import WebMapService
    from owslib.wmts import WebMapTileService
    from owslib.util import ServiceException
    import owslib
    logger.info("Depencencies - owslib version: {}"
                .format(owslib.__version__))
except ImportError as e:
    logger.error("Depencencies - owslib is not present")
    # raise e

try:
    from owslib.wfs import WebFeatureService
except ImportError as e:
    logger.error("Depencencies - owslib WFS issue: {}"
                 .format(e))

try:
    from owslib.util import HTTPError
    logger.info("Depencencies - HTTPError within owslib")
except ImportError as e:
    from urllib2 import HTTPError
    logger.error("Depencencies - HTTPError not within owslib."
                 "Directly imported from urllib2.")
try:
    import requests
    logger.info("Depencencies - Requests version: {}"
                .format(requests.__version__))
except ImportError as e:
    logger.warning("Depencencies - Requests not available")

# ############################################################################
# ########## Classes ###############
# ##################################


class UrlBuilder(object):
    """Basic class that holds utilitary methods for the plugin."""

    def __init__(self):
        """Class constructor."""
        self.cached_wfs = dict()
        self.cached_wms = dict()
        self.cached_wmts = dict()

    def build_postgis_dict(self, input_dict):
        """Build the dict that stores informations about PostGIS connexions."""
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

    def build_efs_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"):
        """Reformat the input Esri Feature Service url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        srs_map = custom_tools.get_map_crs()
        layer_name = api_layer.get("id")
        efs_lyr_title = api_layer.get("titles")[0].get("value", "EFS Layer")
        efs_lyr_url = "{}/{}".format(srv_details.get("path"), layer_name)

        efs_uri = QgsDataSourceURI()
        efs_uri.setParam("url", efs_lyr_url)
        efs_uri.setParam("crs", srs_map)
        efs_uri.setParam("restrictToRequestBBOX", "1")

        btn_lbl = "EFS : {}".format(efs_lyr_title)
        return ["arcgisfeatureserver", efs_lyr_title, efs_uri.uri(),
                api_layer, srv_details, btn_lbl]

    def build_ems_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"):
        """Reformat the input Esri Map Service url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        srs_map = custom_tools.get_map_crs()
        layer_name = api_layer.get("id")
        ems_lyr_title = api_layer.get("titles")[0].get("value", "EMS Layer")
        ems_lyr_url = "{}/{}".format(srv_details.get("path"), layer_name)

        ems_uri = QgsDataSourceURI()
        ems_uri.setParam("url", ems_lyr_url)
        ems_uri.setParam("crs", srs_map)
        ems_uri.setParam("restrictToRequestBBOX", "1")

        btn_lbl = "EMS : {}".format(ems_lyr_title)
        return ["arcgismapserver", ems_lyr_title, ems_uri.uri(),
                api_layer, srv_details, btn_lbl]

    def build_wfs_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # local variables
        layer_title = api_layer.get("titles")[0].get("value", "WFS Layer")
        wfs_url_getcap = srv_details.get("path")\
                         + "?request=GetCapabilities&service=WFS"
        geoserver = "geoserver" in wfs_url_getcap
        layer_id = api_layer.get("id")
        layer_name = re.sub('\{.*?}', "", layer_id)
        # handling WFS namespaces
        if "{" in layer_id:
            namespace = layer_id[layer_id.find("{") + 1:layer_id.find("}")]
            logging.debug("WFS - Namespace: " + namespace)
        else:
            namespace = ""

        if mode == "quicky":
            # let's try a quick & dirty url build
            srs_map = custom_tools.get_map_crs()
            wfs_url_base = srv_details.get("path")
            uri = QgsDataSourceURI()
            uri.setParam("url", wfs_url_base)
            uri.setParam("typename", layer_name)
            uri.setParam("version", "auto")
            uri.setParam("srsname", srs_map)
            uri.setParam("restrictToRequestBBOX", "1")
            wfs_url_quicky = uri.uri()

            btn_lbl = "WFS : {}".format(layer_title)
            return ["WFS", layer_title, wfs_url_quicky,
                    api_layer, srv_details, btn_lbl]
        elif mode == "complete":
            # Clean, complete but slower way - OWSLib -------------------------
            if srv_details.get("path") == self.cached_wfs.get("srv_path"):
                logger.debug("WFS: already in cache")
            else:
                self.cached_wfs["srv_path"] = srv_details.get("path")
                logger.debug("WFS: new service")
                pass
            # basic checks on service url
            try:
                wfs = WebFeatureService(wfs_url_getcap)
            except ServiceException as e:
                logger.error(str(e))
                return 0, "WFS - Bad operation: " + wfs_url_getcap, str(e)
            except HTTPError as e:
                logger.error(str(e))
                return 0, "WFS - Service not reached: " + wfs_url_getcap, str(e)
            except Exception as e:
                return 0, e

            # check if GetFeature and DescribeFeatureType operation are available
            if not hasattr(wfs, "getfeature") or "GetFeature" not in [op.name for op in wfs.operations]:
                self.cached_wfs["GetFeature"] = 0
                return 0, "Required GetFeature operation not available in: " + wfs_url_getcap
            else:
                self.cached_wfs["GetFeature"] = 1
                logger.info("GetFeature available")
                pass

            if "DescribeFeatureType" not in [op.name for op in wfs.operations]:
                self.cached_wfs["DescribeFeatureType"] = 0
                return 0, "Required DescribeFeatureType operation not available in: " + wfs_url_getcap
            else:
                self.cached_wfs["DescribeFeatureType"] = 1
                logger.info("DescribeFeatureType available")
                pass

            # check if required layer is present
            try:
                wfs_lyr = wfs[layer_name]
            except KeyError as e:
                logger.error("Layer {} not found in WFS service: {}"
                             .format(layer_name,
                                     wfs_url_getcap))
                if geoserver and layer_name in [l.split(":")[1] for l in list(wfs.contents)]:
                    layer_name = list(wfs.contents)[[l.split(":")[1]
                                                    for l in list(wfs.contents)].index(layer_name)]
                    try:
                        wfs_lyr = wfs[layer_name]
                    except KeyError as e:
                        return (0,
                                "Layer {} not found in WFS service: {}"
                                .format(layer_name,
                                        wfs_url_getcap),
                                e)

            # SRS definition
            srs_map = custom_tools.get_map_crs()
            srs_lyr_new = qsettings.value("/Projections/defaultBehaviour")
            srs_lyr_crs = qsettings.value("/Projections/layerDefaultCrs")
            srs_qgs_new = qsettings.value("/Projections/projectDefaultCrs")
            srs_qgs_otf_on = qsettings.value("/Projections/otfTransformEnabled")
            srs_qgs_otf_auto = qsettings.value("/Projections/otfTransformAutoEnable")

            # DEV
            # print("CRS: ", wms_lyr.crsOptions,
            #       "For new layers: " + srs_lyr_new + srs_lyr_crs,
            #       "For new projects: " + srs_qgs_new,
            #       "OTF enabled: " + srs_qgs_otf_on,
            #       "OTF smart enabled: " + srs_qgs_otf_auto,
            #       "Map canvas SRS:" + custom_tools.get_map_crs())

            wfs_lyr_crs_epsg = ["{}:{}".format(srs.authority, srs.code)
                                for srs in wfs_lyr.crsOptions]
            self.cached_wfs["CRS"] = wfs_lyr_crs_epsg
            if srs_map in wfs_lyr_crs_epsg:
                logger.debug("It's a SRS match! With map canvas: " + srs_map)
                srs = srs_map
            elif srs_qgs_new in wfs_lyr_crs_epsg\
                 and srs_qgs_otf_on == "false"\
                 and srs_qgs_otf_auto == "false":
                logger.debug("It's a SRS match! With default new project: " + srs_qgs_new)
                srs = srs_qgs_new
            elif srs_lyr_crs in wfs_lyr_crs_epsg and srs_lyr_new == "useGlobal":
                logger.debug("It's a SRS match! With default new layer: " + srs_lyr_crs)
                srs = srs_lyr_crs
            elif "EPSG:4326" in wfs_lyr_crs_epsg:
                logger.debug("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                srs = "EPSG:4326"
            else:
                logger.debug("Map Canvas SRS not available within service CRS.")
                srs = wfs_lyr_crs_epsg[0]

            # Style definition
            # print("Styles: ", wms_lyr.styles, type(wms_lyr.styles))
            # lyr_style = wfs_lyr.styles.keys()[0]
            # print(lyr_style)

            # GetFeature URL
            wfs_lyr_url = wfs.getOperationByName('GetFeature').methods
            wfs_lyr_url = wfs_lyr_url[0].get("url")
            if wfs_lyr_url[-1] != "&":
                wfs_lyr_url = wfs_lyr_url + "&"
            else:
                pass
            self.cached_wfs["url"] = wfs_lyr_url

            # url construction
            try:
                wfs_url_params = {"SERVICE": "WFS",
                                  "VERSION": "1.0.0",
                                  "TYPENAME": layer_name,
                                  "SRSNAME": srs,
                                  }
                wfs_url_final = wfs_lyr_url + unquote(urlencode(wfs_url_params, "utf8"))
            except UnicodeEncodeError:
                wfs_url_params = {"SERVICE": "WFS",
                                  "VERSION": "1.0.0",
                                  "TYPENAME": layer_name.decode("latin1"),
                                  "SRSNAME": srs,
                                  }
                wfs_url_final = wfs_lyr_url + unquote(urlencode(wfs_url_params))
            # method ending
            logger.debug(wfs_url_final)
            # logger.debug(uri)
            return ["WFS", layer_title, wfs_url_final]
            # return ["WFS", layer_title, uri.uri()]
        else:
            return None

    def build_wms_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # local variables
        layer_name = api_layer.get("id")
        layer_title = api_layer.get("titles")[0].get("value", "WMS Layer")
        wms_url_getcap = srv_details.get("path")\
                       + "?request=GetCapabilities&service=WMS"
        geoserver = "geoserver" in wms_url_getcap

        if mode == "quicky":
            # let's try a quick & dirty url build
            srs_map = custom_tools.get_map_crs()
            wms_url_base = srv_details.get("path")
            if "?" not in wms_url_base:
                wms_url_base = wms_url_base + "?"
            else:
                pass
            # url construction
            wms_url_params = {"SERVICE": "WMS",
                              "VERSION": srv_details.get("formatVersion", "1.3.0"),
                              "REQUEST": "GetMap",
                              "layers": layer_name,
                              "crs": srs_map,
                              "format": "image/png",
                              "styles": "",
                              "url": wms_url_base,
                              }
            wms_url_quicky = unquote(urlencode(wms_url_params, "utf8"))
            # prevent encoding errors (#102)
            try:
                btn_lbl = "WMS : {}".format(layer_title)
                return ["WMS", layer_title, wms_url_quicky,
                        api_layer, srv_details, btn_lbl]
            except UnicodeEncodeError as e:
                btn_lbl = "WMS : {}".format(layer_name)
                logger.debug(e)
                return ["WMS", layer_title, wms_url_quicky,
                        api_layer, srv_details, btn_lbl]

        elif mode == "complete":
            # Clean, complete but slower way - OWSLib -------------------------
            if srv_details.get("path") == self.cached_wms.get("srv_path"):
                logger.debug("WMS: already in cache")
            else:
                self.cached_wms["srv_path"] = srv_details.get("path")
                logger.debug("WMS: new service")
                pass
            # basic checks on service url
            try:
                wms = WebMapService(wms_url_getcap)
                self.cached_wms["Reachable"] = 1
            except ServiceException as e:
                logger.error(str(e))
                self.cached_wms["Reachable"] = 0
                return 0, "WMS - Bad operation: " + wms_url_getcap, str(e)
            except HTTPError as e:
                self.cached_wms["Reachable"] = 0
                logger.error(str(e))
                return 0, "WMS - Service not reached: " + wms_url_getcap, str(e)
            except Exception as e:
                self.cached_wms["Reachable"] = 0
                logger.error(str(e))
                return 0, e

            # check if GetMap operation is available
            if not hasattr(wms, "getmap") or "GetMap" not in [op.name for op in wms.operations]:
                self.cached_wms["GetMap"] = 1
                return 0, "Required GetMap operation not available in: "\
                          + wms_url_getcap
            else:
                self.cached_wms["GetMap"] = 0
                pass
            # check if layer is present and queryable
            try:
                wms_lyr = wms[layer_name]
            except KeyError as e:
                logger.error("Layer {} not found in WMS service: {}"
                             .format(layer_name,
                                     wms_url_getcap))
                return (0,
                        "Layer {} not found in WMS service: {}"
                        .format(layer_name,
                                wms_url_getcap), e)

            # SRS definition
            srs_map = custom_tools.get_map_crs()
            srs_lyr_new = qsettings.value("/Projections/defaultBehaviour")
            srs_lyr_crs = qsettings.value("/Projections/layerDefaultCrs")
            srs_qgs_new = qsettings.value("/Projections/projectDefaultCrs")
            srs_qgs_otf_on = qsettings.value("/Projections/otfTransformEnabled")
            srs_qgs_otf_auto = qsettings.value("/Projections/otfTransformAutoEnable")

            # DEV
            # print("CRS: ", wms_lyr.crsOptions,
            #       "For new layers: " + srs_lyr_new + srs_lyr_crs,
            #       "For new projects: " + srs_qgs_new,
            #       "OTF enabled: " + srs_qgs_otf_on,
            #       "OTF smart enabled: " + srs_qgs_otf_auto,
            #       "Map canvas SRS:" + custom_tools.get_map_crs())
            self.cached_wms["CRS"] = wms_lyr.crsOptions
            if srs_map in wms_lyr.crsOptions:
                logger.debug("It's a SRS match! With map canvas: " + srs_map)
                srs = srs_map
            elif srs_qgs_new in wms_lyr.crsOptions\
                 and srs_qgs_otf_on == "false"\
                 and srs_qgs_otf_auto == "false":
                logger.debug("It's a SRS match! With default new project: " + srs_qgs_new)
                srs = srs_qgs_new
            elif srs_lyr_crs in wms_lyr.crsOptions and srs_lyr_new == "useGlobal":
                logger.debug("It's a SRS match! With default new layer: " + srs_lyr_crs)
                srs = srs_lyr_crs
            elif "EPSG:4326" in wms_lyr.crsOptions:
                logger.debug("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                srs = "EPSG:4326"
            else:
                logger.debug("Map Canvas SRS not available within service CRS.")
                srs = wms_lyr.crsOptions[0]

            # Format definition
            wms_lyr_formats = wms.getOperationByName('GetMap').formatOptions
            formats_image = [f.split(" ", 1)[0] for f in wms_lyr_formats
                             if f in qgis_wms_formats]
            self.cached_wms["formats"] = formats_image
            if "image/png" in formats_image:
                layer_format = "image/png"
            elif "image/jpeg" in formats_image:
                layer_format = "image/jpeg"
            else:
                layer_format = formats_image[0]

            # Style definition
            lyr_style = wms_lyr.styles.keys()[0]

            # GetMap URL
            wms_lyr_url = wms.getOperationByName('GetMap').methods
            wms_lyr_url = wms_lyr_url[0].get("url")
            if wms_lyr_url[-1] == "&":
                wms_lyr_url = wms_lyr_url[:-1]
            else:
                pass
            self.cached_wms["url"] = wms_lyr_url

            # url construction
            try:
                wms_url_params = {"SERVICE": "WMS",
                                  "VERSION": srv_details.get("formatVersion", "1.3.0"),
                                  "REQUEST": "GetMap",
                                  "layers": layer_name,
                                  "crs": srs,
                                  "format": layer_format,
                                  "styles": "",
                                  # "styles": lyr_style,
                                  # "url": srv_details.get("path"),
                                  "url": wms_lyr_url,
                                  }
                wms_url_final = unquote(urlencode(wms_url_params, "utf8"))
            except UnicodeEncodeError:
                wms_url_params = {"SERVICE": "WMS",
                                  "VERSION": srv_details.get("formatVersion", "1.3.0"),
                                  "REQUEST": "GetMap",
                                  "layers": layer_name.decode("latin1"),
                                  "crs": srs,
                                  "format": layer_format,
                                  "styles": "",
                                  # "styles": lyr_style,
                                  # "url": srv_details.get("path"),
                                  "url": wms_lyr_url,
                                  }
                wms_url_final = unquote(urlencode(wms_url_params, "utf8"))
            # method ending
            return ["WMS", layer_title, wms_url_final]
        else:
            return None

    def build_wmts_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"):
        """Format the input WMTS URL to fit QGIS criterias.

        Retrieve GetCapabilities from information transmitted by Isogeo API
        to complete URL syntax.
        """
        # local variables
        layer_name = api_layer.get("id")
        layer_title = api_layer.get("titles")[0].get("value", "WMTS Layer")
        wmts_url_getcap = srv_details.get("path")\
                          + "?request=GetCapabilities&service=WMTS"
        geoserver = "geoserver" in wmts_url_getcap
        # basic checks on service url
        try:
            wmts = WebMapTileService(wmts_url_getcap)
        except TypeError as e:
            logger.error("WMTS - OWSLib mixing str and unicode args", e)
            wmts = WebMapTileService(unicode(wmts_url_getcap))
        except ServiceException as e:
            logger.error(e)
            return 0, "WMTS - Bad operation: " + wmts_url_getcap, str(e)
        except HTTPError as e:
            logger.error(e)
            return 0, "WMTS - Service not reached: " + wmts_url_getcap, e
        except Exception as e:
            logger.error("WMTS - {}: {}".format(wmts_url_getcap, e))
            return 0, "WMTS - Service not reached: " + wmts_url_getcap, e

        # check if GetTile operation is available
        if not hasattr(wmts, "gettile") or "GetTile" not in [op.name for op in wmts.operations]:
            return 0, "Required GetTile operation not available in: " + wmts_url_getcap
        else:
            logger.debug("GetTile available")
            pass

        # check if layer is present and queryable
        try:
            wmts_lyr = wmts[layer_name]
            layer_title = wmts_lyr.title
            layer_id = wmts_lyr.id
        except KeyError as e:
            logger.error("Layer {} not found in WMTS service: {}"
                         .format(layer_name,
                                 wmts_url_getcap))
            return (0,
                    "Layer {} not found in WMS service: {}"
                    .format(layer_name,
                            wmts_url_getcap), e)

        # Tile Matrix Set & SRS
        srs_map = custom_tools.get_map_crs()
        def_tile_matrix_set = wmts_lyr.tilematrixsets[0]
        if srs_map in wmts_lyr.tilematrixsets:
            logger.debug("WMTS - It's a SRS match! With map canvas: " + srs_map)
            tile_matrix_set = wmts.tilematrixsets.get(srs_map).identifier
            srs = srs_map
        elif "EPSG:4326" in wmts_lyr.tilematrixsets:
            logger.debug("WMTS - It's a SRS match! With standard WGS 84 (4326)")
            tile_matrix_set = wmts.tilematrixsets.get("EPSG:4326").identifier
            srs = "EPSG:4326"
        elif "EPSG:900913" in wmts_lyr.tilematrixsets:
            logger.debug("WMTS - It's a SRS match! With Google (900913)")
            tile_matrix_set = wmts.tilematrixsets.get("EPSG:900913").identifier
            srs = "EPSG:900913"
        else:
            logger.debug("WMTS - Searched SRS not available within service CRS.")
            tile_matrix_set = wmts.tilematrixsets.get(def_tile_matrix_set).identifier
            srs = tile_matrix_set

        # Format definition
        wmts_lyr_formats = wmts.getOperationByName('GetTile').formatOptions
        formats_image = [f.split(" ", 1)[0] for f in wmts_lyr_formats
                         if f in qgis_wms_formats]
        if len(formats_image):
            if "image/png" in formats_image:
                layer_format = "image/png"
            elif "image/jpeg" in formats_image:
                layer_format = "image/jpeg"
            else:
                layer_format = formats_image[0]
        else:
            logger.debug("WMTS - No format available among preferred by QGIS.")
            layer_format = "image/png"

        # Style definition
        lyr_style = wmts_lyr.styles.keys()[0]

        # GetTile URL
        wmts_lyr_url = wmts.getOperationByName('GetTile').methods
        wmts_lyr_url = wmts_lyr_url[0].get("url")
        if wmts_lyr_url[-1] == "&":
            wmts_lyr_url = wmts_lyr_url[:-1]
        else:
            pass

        # construct URL
        wmts_url_params = {"SERVICE": "WMTS",
                           "VERSION": "1.0.0",
                           "REQUEST": "GetCapabilities",
                           "layers": layer_id,
                           "crs": srs,
                           "format": layer_format,
                           "styles": "",
                           "tileMatrixSet": tile_matrix_set,
                           "url": wmts_lyr_url,
                           }
        wmts_url_final = unquote(urlencode(wmts_url_params))
        logger.debug(wmts_url_final)
        # prevent encoding errors (#102)
        # try:
        #     layer_title = str(layer_title)
        # except UnicodeEncodeError as e:
        #     layer_title = layer_title.encode("latin1")
        #     logger.debug(e)
        # except UnicodeDecodeError as e:
        #     layer_title = layer_title.decode("latin1")
        #     logger.debug(e)

        # method ending
        return ["WMTS", layer_title, wmts_url_final]
        # return QgsRasterLayer(wms_url_final, layer_title, 'wms')
