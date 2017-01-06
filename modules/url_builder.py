# -*- coding: utf-8 -*-

# Standard library
import logging
from urllib import unquote, urlencode
from urlparse import urlparse

# PyQT
from PyQt4.QtCore import QUrl


class UrlBuilder(object):
    """Basic class that holds utilitary methods for the plugin."""

    def build_wfs_url(self, raw_url, rsc_type="service"):
        """Reformat the input WFS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.

        rsc_type: possible values = "service" or "link"
        """
        title = raw_url[0]
        input_url = raw_url[1].split("?")[0] + "?"
        try:
            list_parameters = raw_url[1].split("?")[1].split('&')
        except IndexError, e:
            logging.error("Build WFS URL failed: {}".format(e))
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
        url_parsed = urlparse(raw_url[1])
        print(url_parsed)
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
            logging.error("Build WMS URL failed: {}".format(e))
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
