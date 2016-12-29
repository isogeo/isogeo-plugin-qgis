# -*- coding: utf-8 -*-

# Standard library
import datetime
import logging
from os import path
from urllib import unquote, urlencode
import webbrowser

# PyQGIS
from qgis.core import QgsMapLayerRegistry, QgsRasterLayer, QgsRectangle,\
                      QgsVectorLayer
from qgis.utils import iface

# PyQT
from PyQt4.QtCore import QUrl


class Tools(object):
    """Basic class that holds utilitary methods for the plugin."""

    def format_button_title(self, title):
        """Format the title for it to fit the button."""
        words = title.split(' ')
        line_length = 0
        lines = []
        string = ""
        for word in words:
            line_length += len(word)
            if line_length < 22:
                string += word + " "
            else:
                line_length = len(word)
                lines.append(string[:-1])
                string = word + " "
        if string[:-1] not in lines:
            lines.append(string[:-1])
        final_text = ""
        for line in lines:
            final_text += line + "\n"
        final_text = final_text[:-1]
        # method ending
        return final_text

    def format_path(self, string):
        """Reformat windows path for them to be understood by QGIS."""
        new_string = ""
        for character in string:
            if character == '\\':
                new_string += "/"
            else:
                new_string += character
        # method ending
        return new_string

    def handle_date(self, input_date):
        """Create a date object with the string given as a date by the API."""
        date = input_date.split("T")[0]
        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])
        new_date = datetime.date(year, month, day)
        # method ending
        return new_date.strftime("%Y-%m-%d")

    def mail_to_isogeo(self, lang):
        """Open the credentials request online form in web browser."""
        if lang == "fr":
            webbrowser.open('http://www.isogeo.com/fr/Plugin-QGIS/22',
                            new=0,
                            autoraise=True
                            )
        else:
            webbrowser.open('http://www.isogeo.com/en/QGIS-Plugin/22',
                            new=0,
                            autoraise=True
                            )
        # method ending
        logging.info("Bugtracker launched in the default web browser")
        return

    def open_webpage(self, link):
        """Open the bugtracker on the user's default browser."""
        if type(link) is QUrl:
            link = link.toString()

        webbrowser.open(
            link,
            new=0,
            autoraise=True)
        # method ending
        logging.info("Bugtracker launched in the default web browser")
        return

    def results_pages_counter(self, nb_fiches):
        """Calculate the number of pages for a given number of results."""
        if nb_fiches <= 15:
            nb_page = 1
        else:
            if (nb_fiches % 15) == 0:
                nb_page = (nb_fiches / 15)
            else:
                nb_page = (nb_fiches / 15) + 1
        # method ending
        return nb_page

    def special_search(self, easter_code="isogeo"):
        """Make some special actions in certains cases."""
        canvas = iface.mapCanvas()
        if easter_code == "isogeo":
            # WMS
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
            # wms_lyr = QgsRasterLayer(wms_uri, u"Ici c'est Isogeo !", "wms")
            # if wms_lyr.isValid:
            #     QgsMapLayerRegistry.instance().addMapLayer(wms_lyr)

            #     logging.info("Isogeo easter egg used and WMS displayed!")
            # else:
            #     logging.error("WMS layer failed: {}"
            #                   .format(wms_lyr.error().message()))

            # WFS
            wfs_params = {"service": "WFS",
                          "version": "1.0.0",
                          "request": "GetFeature",
                          "typename": "Isogeo:isogeo_logo",
                          "srsname": "EPSG:3857",
                          }
            wfs_uri = "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?"\
                      + unquote(urlencode(wfs_params))
            wfs_lyr = QgsVectorLayer(wfs_uri, u"Ici c'est Isogeo !", "WFS")
            if wfs_lyr.isValid:
                wfs_style = path.join(path.dirname(path.realpath(__file__)),
                                      "isogeo.qml")
                wfs_lyr.loadNamedStyle(wfs_style)
                QgsMapLayerRegistry.instance().addMapLayer(wfs_lyr)
                logging.info("Isogeo easter egg used and WFS displayed!")
            else:
                logging.error("WFS layer failed: {}"
                              .format(wfs_lyr.error().message()))
            canvas.setExtent(QgsRectangle(2.224199,48.815573,2.469921, 48.902145))
        else:
            pass
        # ending method
        return
