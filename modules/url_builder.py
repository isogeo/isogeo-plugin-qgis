# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

# Standard library
from datetime import datetime
import logging
import requests
from owslib.wms import WebMapService
from owslib.util import HTTPError, ServiceException
# from owslib.util import *
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
        # TESTING
        
        logger.debug("WFS URL TYPE: " + rsc_type)
        # print(url_parsed)
        # wms_params = {"service": "WMS",
        #               "version": "1.3.0",
        #               "request": "GetMap",
        #               "layers": "Isogeo:isogeo_logo",
        #               "crs": "EPSG:3857",
        #               "format": "image/png",
        #               "styles": "isogeo_logo",
        #               "url": "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?"
        #               }
        # wms_uri = unquote(urlencode(wms_params))

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

    def new_build_wms_url(self, api_layer, rsc_type="service"):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        #
        qgis_wms_formats = ('image/png', 'image/png8',
                            'image/jpeg',
                            'image/svg',
                            'image/gif',
                            'image/geotiff', 'image/tiff')
        # TESTING
        # print(type(api_layer), rsc_type)
        if rsc_type == "service":
            layer_name = api_layer.get("id")
            layer_title = api_layer.get("titles")[0].get("value", "WMS Service")
            srv_details = api_layer.get("service")
            wms_url_getcap = srv_details.get("path")\
                           + "?request=GetCapabilities&service=WMS"
            # print(srv_details.get("path"), srv_details.get("formatVersion", "1.3.0"))
            # wms = WebMapService(wms_url_getcap)
            try:
                wms = WebMapService(wms_url_getcap)
                # print(dir(wms)) :
                # contents', 'exceptions', 'getOperationByName', 'getServiceXML', 'getcapabilities',
                # 'getfeatureinfo', 'getmap', 'identification', 'items',
                # 'operations', 'password', 'provider', 'url', 'username', 'version']
            except ServiceException as e:
                print(str(e))
                return 0, "WMS - Bad operation: " + wms_url_getcap, str(e)
            except HTTPError as e:
                print(str(e))
                return 0, "WMS - Service not reached: " + wms_url_getcap, str(e)
            except Exception as e:
                return 0, e
            # check if GetMap operation is available
            if "GetMap" not in [op.name for op in wms.operations]:
                return 0, "Required GetMap operation not available in: " + wms_url_getcap
            else:
                pass
            # check if layer is present and queryable
            try:
                wms_lyr = wms[layer_name]
            except KeyError as e:
                return (0,
                        "Layer {} not found in WMS service: {}"
                        .format(layer_name,
                                wms_url_getcap),
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

            if srs_map in wms_lyr.crsOptions:
                print("It's a SRS match! With map canvas: " + srs_map)
                srs = srs_map
            elif srs_qgs_new in wms_lyr.crsOptions\
                 and srs_qgs_otf_on == "false"\
                 and srs_qgs_otf_auto == "false":
                print("It's a SRS match! With default new project: " + srs_qgs_new)
                srs = srs_qgs_new
            elif srs_lyr_crs in wms_lyr.crsOptions and srs_lyr_new == "useGlobal":
                print("It's a SRS match! With default new layer: " + srs_lyr_crs)
                srs = srs_lyr_crs
            elif "EPSG:4326" in wms_lyr.crsOptions:
                print("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                srs = "EPSG:4326"
            else:
                print("Map Canvas SRS not available within service CRS.")
                srs = ""

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
            # print("Styles: ", wms_lyr.styles, type(wms_lyr.styles))
            lyr_style = wms_lyr.styles.keys()[0]
            # print(lyr_style)

            # GetMap URL
            wms_lyr_url = wms.getOperationByName('GetMap').methods
            # print(wms_lyr_url, type(wms_lyr_url))

            # self.complete_from_capabilities(srv_details.get("path"), "wms")
            wms_url_params = {"service": "WMS",
                              "version": srv_details.get("formatVersion", "1.3.0"),
                              "request": "GetMap",
                              "layers": layer_name,
                              "crs": srs,
                              "format": layer_format,
                              "styles": lyr_style,
                              "url": srv_details.get("path"),
                              }
            wms_url_final = unquote(urlencode(wms_url_params))
            print(wms_url_final)
            return ["WMS", layer_title, wms_url_final]
            # return QgsRasterLayer(wms_url_final, layer_title, 'wms')
        else:
            pass

    def complete_from_capabilities(self, url_service, service_type):
        """Complete services URI from services GetCapabilities."""
        print(url_service)
        url_parsed = urlparse(url_service)
        print(url_parsed)
        self.request_download(self.manager, url_service)

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
