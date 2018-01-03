# -*- coding: utf-8 -*-

# Standard library
import datetime
import logging
from os import path
from urllib import getproxies, unquote, urlencode
import webbrowser

# PyQGIS
from qgis.core import (QgsDataSourceURI, QgsProject,
                       QgsVectorLayer, QgsMapLayerRegistry, QgsRasterLayer)
from qgis.utils import iface

# PyQT
from PyQt5.QtCore import QSettings, QUrl
from PyQt5.QtGui import QMessageBox

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

# ############################################################################
# ########## Classes ###############
# ##################################


class Tools(object):
    """Basic class that holds utilitary methods for the Isogeo plugin."""
    last_error = None

    def error_catcher(self, msg, tag, level):
        """Catch QGIS error messages for introspection."""
        # print(type(logger), dir(logger))
        # print(msg, tag, level)
        if tag == 'WMS' and level != 0:
            # logger.error("WMS error: {}".format(msg))
            self.last_error = "wms", msg
        elif tag == 'PostGIS' and level != 0:
            self.last_error = "postgis", msg
        else:
            pass

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
        # new_string = ""
        # for character in string:
        #     if character == '\\':
        #         new_string += "/"
        #     else:
        #         new_string += character
        # # method ending
        # # return new_string
        return path.realpath(string)

    def get_map_crs(self):
        """Get QGIS map canvas current EPSG code."""
        current_crs = str(iface.mapCanvas()
                               .mapRenderer()
                               .destinationCrs()
                               .authid())
        return current_crs

    def handle_date(self, input_date):
        """Create a date object with the string given as a date by the API."""
        if input_date != "NR":
            date = input_date.split("T")[0]
            year = int(date.split('-')[0])
            month = int(date.split('-')[1])
            day = int(date.split('-')[2])
            new_date = datetime.date(year, month, day)
            # method ending
            return new_date.strftime("%Y-%m-%d")
        else:
            return input_date
            pass

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
        logger.info("Bugtracker launched in the default web browser")
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
        logger.info("Bugtracker launched in the default web browser")
        return

    def results_pages_counter(self, nb_fiches):
        """Calculate the number of pages for a given number of results."""
        if nb_fiches <= 10:
            nb_page = 1
        else:
            if (nb_fiches % 10) == 0:
                nb_page = (nb_fiches / 10)
            else:
                nb_page = (nb_fiches / 10) + 1
        # method ending
        return nb_page

    def display_auth_form(self, ui_auth_form):
        """Show authentication form with prefilled fields."""
        # fillfull auth form fields from stored settings
        ui_auth_form.ent_app_id.setText(qsettings
                                        .value("isogeo-plugin/user-auth/id", 0))
        ui_auth_form.ent_app_secret.setText(qsettings
                                            .value("isogeo-plugin/user-auth/secret", 0))
        ui_auth_form.chb_isogeo_editor.setChecked(qsettings
                                                  .value("isogeo/user/editor", 0))

        # check auth validity
        # connect check button
        # ui_auth_form.btn_check_auth.connect(partial(print("check API authentication")))

        # display
        ui_auth_form.show()

    def special_search(self, easter_code="isogeo"):
        """Make some special actions in certains cases."""
        canvas = iface.mapCanvas()
        if easter_code == "isogeo":
            # WMS
            wms_params = {"service": "WMS",
                          "version": "1.3.0",
                          "request": "GetMap",
                          "layers": "Isogeo:isogeo_logo",
                          "crs": "EPSG:3857",
                          "format": "image/png",
                          "styles": "isogeo_logo",
                          "url": "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?"
                          }
            wms_uri = unquote(urlencode(wms_params))
            wms_lyr = QgsRasterLayer(wms_uri, u"Ici c'est Isogeo !", "wms")
            if wms_lyr.isValid:
                QgsMapLayerRegistry.instance().addMapLayer(wms_lyr)
                logger.info("Isogeo easter egg used and WMS displayed!")
            else:
                logger.error("WMS layer failed: {}"
                             .format(wms_lyr.error().message()))

            # WFS
            uri = QgsDataSourceURI()
            uri.setParam("url", "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?")
            uri.setParam("service", "WFS")
            uri.setParam("version", "1.1.0")
            uri.setParam("typename", "Isogeo:isogeo_logo")
            uri.setParam("srsname", "EPSG:3857")
            uri.setParam("restrictToRequestBBOX", "0")
            wfs_uri = uri.uri()
            wfs_lyr = QgsVectorLayer(wfs_uri, u"Ici c'est Isogeo !", "WFS")
            if wfs_lyr.isValid:
                wfs_style = path.join(path.dirname(path.realpath(__file__)),
                                      "isogeo.qml")
                wfs_lyr.loadNamedStyle(wfs_style)
                QgsMapLayerRegistry.instance().addMapLayer(wfs_lyr)
                canvas.setExtent(wfs_lyr.extent())
                logger.debug("Isogeo easter egg used")
            else:
                logger.error("Esater egg - WFS layer failed: {}"
                             .format(wfs_lyr.error().message()))
        elif easter_code == "picasa":
            project = QgsProject.instance()
            project.setTitle(u"Isogeo, le Picasa de l'information géographique")
            logger.debug("Picasa easter egg used")
        else:
            pass
        # ending method
        return

    def test_proxy_configuration(self):
        """Check adequation between system and QGIS proxy configuration.

        If a proxy configuration is set up for the computer, and for QGIS.
        If none or both is set up, pass. But if there is a proxy config for the
        computer but not in QGIS, pops an alert message.
        """
        system_proxy_config = getproxies()
        if system_proxy_config == {}:
            logger.info("No proxy found on the OS: OK.")
            return 0
        else:
            qgis_proxy = qsettings.value("proxy/proxyEnabled", "")
            if str(qgis_proxy) == "true":
                http = system_proxy_config.get('http')
                if http is None:
                    pass
                else:
                    elements = http.split(':')
                    if len(elements) == 2:
                        host = elements[0]
                        port = elements[1]
                        qgis_host = qsettings.value("proxy/proxyHost", "")
                        qgis_port = qsettings.value("proxy/proxyPort", "")
                        if qgis_host == host:
                            if qgis_port == port:
                                logger.info("A proxy is set up both in QGIS "
                                            "and the OS and they match => "
                                            "Proxy config : OK")
                                pass
                            else:
                                QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'),
                                    self.tr("Proxy issue : \nQGIS and your OS "
                                            "have different proxy set up."))
                        else:
                            QMessageBox.information(iface.mainWindow(
                            ), self.tr('Alert'),
                                self.tr("Proxy issue : \nQGIS and your OS have"
                                        " different proxy set ups."))
                    elif len(elements) == 3 and elements[0] == 'http':
                        host_short = elements[1][2:]
                        host_long = elements[0] + ':' + elements[1]
                        port = elements[2]
                        qgis_host = qsettings.value("proxy/proxyHost", "")
                        qgis_port = qsettings.value("proxy/proxyPort", "")
                        if qgis_host == host_short or qgis_host == host_long:
                            if qgis_port == port:
                                logger.info("A proxy is set up both in QGIS"
                                            " and the OS and they match "
                                            "=> Proxy config : OK")
                                pass
                            else:
                                logger.error("OS and QGIS proxy ports do not "
                                             "match. => Proxy config: not OK")
                                QMessageBox.information(iface.mainWindow(
                                ), self.tr('Alert'),
                                    self.tr("Proxy issue : \nQGIS and your OS"
                                            " have different proxy set ups."))
                        else:
                            logger.error("OS and QGIS proxy hosts do not "
                                         "match. => Proxy config: not OK")
                            QMessageBox.information(iface.mainWindow(
                            ), self.tr('Alert'),
                                self.tr("Proxy issue : \nQGIS and your OS have"
                                        " different proxy set ups."))
            else:
                logger.error("OS uses a proxy but it isn't set up in QGIS."
                             " => Proxy config: not OK")
                QMessageBox.information(iface.mainWindow(
                ), self.tr('Alert'),
                    self.tr("Proxy issue : \nYou have a proxy set up on your"
                            " OS but none in QGIS.\nPlease set it up in "
                            "'Preferences/Options/Network'."))
