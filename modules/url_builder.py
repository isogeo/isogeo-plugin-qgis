# -*- coding: utf-8 -*-

# Standard library
from datetime import datetime
import logging
import requests
from owslib.wms import WebMapService
from urllib import unquote, urlencode
from urlparse import urlparse

# PyQT
from PyQt4.QtCore import QUrl
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest

# QGIS
from qgis.core import QgsNetworkAccessManager

# ############################################################################
# ########## Globals ###############
# ##################################

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
        # TESTING
        print(type(api_layer), rsc_type)
        if rsc_type == "service":
            layer_name = api_layer.get("id")
            layer_title = api_layer.get("titles")[0].get("value", "WMS Service")
            srv_details = api_layer.get("service")
            print(srv_details.get("path"), srv_details.get("formatVersion", "1.3.0"))
            wms = WebMapService(srv_details.get("path") + "?request=GetCapabilities&service=WMS")
            # print(dir(wms)) :
            # contents', 'exceptions', 'getOperationByName', 'getServiceXML', 'getcapabilities', 'getfeatureinfo',
            # 'getmap', 'identification', 'items', 'operations', 'password', 'provider', 'url', 'username', 'version']
            wms_lyr = wms[layer_name]
            print("CRS: ", wms_lyr.crsOptions)
            print("Formats: ", wms.getOperationByName('GetMap').formatOptions)
            print("Styles: ", wms_lyr.styles)
            # print([op.name for op in wms.operations])
            # self.complete_from_capabilities(srv_details.get("path"), "wms")
            wms_params = {"service": "WMS",
                          "version": srv_details.get("formatVersion", "1.3.0"),
                          "request": "GetMap",
                          "layers": layer_name,
                          "crs": "EPSG:3857",
                          "format": "image/png",
                          "styles": "default",
                          "url": srv_details.get("path"),
                          }
            url_final = unquote(urlencode(wms_params))
            print(url_final)
            return url_final, layer_title
        # else:
        #     pass

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
