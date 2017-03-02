# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

# Standard library
from datetime import datetime
import logging
from urllib import unquote, urlencode
from urlparse import urlparse

# PyQT
from PyQt4.QtCore import QSettings, QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

# QGIS
from qgis.core import QgsNetworkAccessManager,\
                      QgsVectorLayer, QgsMapLayerRegistry, QgsRasterLayer

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
    logger.error("Depencencies - HTTPError not within owslib."
                 " Trying to get it from urllib2 directly.")
    from urllib2 import HTTPError
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
        self.manager = QNetworkAccessManager()
        # self.manager = QgsNetworkAccessManager.instance()
        self.manager.finished.connect(self.handle_download)

    def build_wfs_url(self, raw_url, rsc_type="service"):
        """Reformat the input WFS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.

        rsc_type: possible values = "service" or "link"
        """
        logger.debug("WFS URL TYPE: " + rsc_type)
        title = raw_url[0]
        input_url = raw_url[1].split("?")[0] + "?"
        try:
            list_parameters = raw_url[1].split("?")[1].split('&')
        except IndexError, e:
            logger.error("Build WFS URL failed: {}".format(e))
            return 0
        valid = False
        srs_defined = False
        for i in list_parameters:
            ilow = i.lower()
            if "typename=" in ilow:
                valid = True
                name = i.split('=')[1]
                typename = i
            elif "layers=" in ilow or "layer=" in ilow:
                valid = True
                name = i.split('=')[1]
                typename = "typename=" + name
            elif "getcapabilities" in ilow:
                valid = True
                name = title
                typename = "typename=" + name
            elif "srsname=" in ilow:
                srs_defined = True
                srs = i

        if valid is True:
            output_url = input_url + typename

            if srs_defined is True:
                output_url += '&' + srs

            output_url += '&service=WFS&version=1.0.0&request=GetFeature'

            output = ["WFS", name, output_url]
            return output

        else:
            return 0

    def build_wms_url(self, raw_url, rsc_type="service"):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # METHOD
        title = raw_url[0]
        input_url = raw_url[1].split("?")[0] + "?"
        try:
            list_parameters = raw_url[1].split("?")[1].split('&')
        except IndexError, e:
            logger.error("Build WMS URL failed: {}".format(e))
            return 0
        valid = False
        style_defined = False
        srs_defined = False
        format_defined = False
        for i in list_parameters:
            ilow = i.lower()
            if "layers=" in ilow:
                valid = True
                name = i.split('=')[1]
                layers = i
            elif "layer=" in ilow:
                valid = True
                name = i.split('=')[1]
                layers = "layers=" + name
            elif "getcapabilities" in ilow:
                valid = True
                name = title
                layers = "layers=" + title
            elif "styles=" in ilow:
                style_defined = True
                style = i
            elif "crs=" in ilow:
                srs_defined = True
                srs = i
            elif "format=" in ilow:
                format_defined = True
                imgformat = i

        if valid is True:
            if input_url.lower().startswith('url='):
                output_url = input_url + "&" + layers
            else:
                output_url = "url=" + input_url + "&" + layers

            if style_defined is True:
                output_url += '&' + style
            else:
                output_url += '&styles='

            if format_defined is True:
                output_url += '&' + imgformat
            else:
                output_url += '&format=image/png'

            if srs_defined is True:
                output_url += '&' + srs
            output = ["WMS", name, output_url]
            return output

        else:
            return 0

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

    # FIXING #90 -------------------------------------------------------------

    def new_build_wfs_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv"):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # local variables
        layer_name = api_layer.get("id")
        layer_title = api_layer.get("titles")[0].get("value", "WFS Layer")
        wfs_url_getcap = srv_details.get("path")\
                       + "?request=GetCapabilities&service=WFS"

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
            return 0, "Required GetFeature operation not available in: " + wfs_url_getcap
        else:
            logger.info("GetFeature available")
            pass

        if "DescribeFeatureType" not in [op.name for op in wfs.operations]:
            return 0, "Required DescribeFeatureType operation not available in: " + wfs_url_getcap
        else:
            logger.info("DescribeFeatureType available")
            pass

        # check if required layer is present
        try:
            wfs_lyr = wfs[layer_name]
        except KeyError as e:
            logger.error("Layer {} not found in WFS service: {}"
                         .format(layer_name,
                                 wfs_url_getcap))
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

        # print(wms_lyr_url, type(wms_lyr_url))
        wfs_url_params = {"service": "WFS",
                          "version": "1.0.0",
                          "typename": layer_name,
                          "srsname": srs,
                          }
        wfs_url_final = wfs_lyr_url + unquote(urlencode(wfs_url_params))
        logger.debug(wfs_url_final)
        return ["WFS", layer_title, wfs_url_final]
        # return QgsVectorLayer(wfs_uri, layer_title, "WFS")

    def new_build_wms_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv"):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # local variables
        layer_name = api_layer.get("id")
        layer_title = api_layer.get("titles")[0].get("value", "WMS Layer")
        wms_url_getcap = srv_details.get("path")\
                       + "?request=GetCapabilities&service=WMS"

        # basic checks on service url
        try:
            wms = WebMapService(wms_url_getcap)
        except ServiceException as e:
            logger.error(str(e))
            return 0, "WMS - Bad operation: " + wms_url_getcap, str(e)
        except HTTPError as e:
            logger.error(str(e))
            return 0, "WMS - Service not reached: " + wms_url_getcap, str(e)
        except Exception as e:
            logger.error(str(e))
            return 0, e

        # check if GetMap operation is available
        if not hasattr(wms, "getmap") or "GetMap" not in [op.name for op in wms.operations]:
            return 0, "Required GetMap operation not available in: "\
                      + wms_url_getcap
        else:
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

        # construct URL
        wms_url_params = {"service": "WMS",
                          "version": srv_details.get("formatVersion", "1.3.0"),
                          "request": "GetMap",
                          "layers": layer_name,
                          "crs": srs,
                          "format": layer_format,
                          "styles": "",
                          # "styles": lyr_style,
                          # "url": srv_details.get("path"),
                          "url": wms_lyr_url,
                          }
        wms_url_final = unquote(urlencode(wms_url_params))
        logger.debug(wms_url_final)
        return ["WMS", layer_title, wms_url_final]
        # return QgsRasterLayer(wms_url_final, layer_title, 'wms')

    def build_wmts_url(self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv"):
        """Format the input WMTS URL to fit QGIS criterias.

        Retrieve GetCapabilities from information transmitted by Isogeo API
        to complete URL syntax.
        """
        # local variables
        layer_name = api_layer.get("id")
        layer_title = api_layer.get("titles")[0].get("value", "WMTS Layer")
        wmts_url_getcap = srv_details.get("path")\
                          + "?request=GetCapabilities&service=WMTS"

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
        wmts_url_params = {"service": "WMTS",
                           "version": "1.0.0",
                           "request": "GetCapabilities",
                           "layers": layer_id,
                           "crs": srs,
                           "format": layer_format,
                           "styles": "",
                           "tileMatrixSet": tile_matrix_set,
                           "url": wmts_lyr_url,
                            }
        wmts_url_final = unquote(urlencode(wmts_url_params))
        logger.debug(wmts_url_final)
        return ["WMTS", layer_title, wmts_url_final]
        # return QgsRasterLayer(wms_url_final, layer_title, 'wms')

    # REQUESTS MANAGEMENT ----------------------------------------------------

    def request_download(self, manager, url_service):
        """Send request to download GetCapabilities."""
        url = QUrl(url_service)
        request = QNetworkRequest(url)
        logger.info("GetCapabilities download start time: {}".format(datetime.now()))
        self.manager.get(request)

    def handle_download(self, reply):
        """Handle requests reply and clean up."""
        logger.info("Download finish time: {}".format(datetime.now()))
        logger.info("Finished: {}".format(reply.isFinished()))
        logger.info("Bytes received: {}".format(len(reply.readAll())))
        reply.deleteLater()
