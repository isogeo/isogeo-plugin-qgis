# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

# Standard library
import configparser
import datetime
import logging
from os import access, path, R_OK
import subprocess
from sys import platform as opersys
from urllib.request import getproxies, unquote
from urllib.parse import urlencode, urlparse
import webbrowser

# PyQGIS
from qgis.core import QgsDataSourceUri, QgsProject, QgsVectorLayer, QgsRasterLayer
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtWidgets import QMessageBox

# Depending on operating system
if opersys == "win32":
    """ windows """
    from os import startfile  # to open a folder/file
else:
    pass

# 3rd party
from .isogeo_pysdk import IsogeoUtils

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")
msgBar = iface.messageBar()

# ############################################################################
# ########## Classes ###############
# ##################################


class IsogeoPlgTools(IsogeoUtils):
    """Inheritance from Isogeo Python SDK utils class. It adds some
    specific tools for QGIS plugin."""

    last_error = None
    tr = object

    def __init__(self, auth_folder=r"../_auth"):
        """Check and manage authentication credentials."""
        # authentication
        self.auth_folder = auth_folder

        # instanciate
        super(IsogeoPlgTools, self).__init__()

    def error_catcher(self, msg, tag, level):
        """Catch QGIS error messages for introspection."""
        if tag == "WMS" and level != 0:
            self.last_error = "wms", msg
        elif tag == "WFS" and level != 0:
            self.last_error = "wfs", msg
        elif tag == "PostGIS" and level != 0:
            self.last_error = "postgis", msg
        else:
            pass

    def format_button_title(self, title):
        """Format the title to fit the button.
        
        :param str title: title to format
        """
        words = title.split(" ")
        if len(words) == 1 and len(words[0]) > 33:
            final_text = "\n" + words[0][:30] + "..."
            return final_text
        else:
            pass

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

    def get_map_crs(self):
        """Get QGIS map canvas current EPSG code."""
        current_crs = str(iface.mapCanvas().mapSettings().destinationCrs().authid())
        return current_crs

    def handle_date(self, input_date):
        """Create a date object with the string given as a date by the API.
        
        :param str input_date: input date to format
        """
        if input_date != "NR":
            date = input_date.split("T")[0]
            year = int(date.split("-")[0])
            month = int(date.split("-")[1])
            day = int(date.split("-")[2])
            new_date = datetime.date(year, month, day)
            # method ending
            return new_date.strftime("%Y-%m-%d")
        else:
            return input_date

    def mail_to_isogeo(self, lang):
        """Open the credentials request online form in web browser.
        
        :param str lang: language code. If not fr (French), the English form is displayed.
        """
        if lang == "fr":
            webbrowser.open(
                "https://www.isogeo.com/fr/Plugin-QGIS/22", new=0, autoraise=True
            )
        else:
            webbrowser.open(
                "https://www.isogeo.com/en/QGIS-Plugin/22", new=0, autoraise=True
            )
        # method ending
        logger.debug("Bugtracker launched in the default web browser")

    def open_dir_file(self, target):
        """Open a file or a directory in the explorer of the operating system.
        
        :param str target: path to the file or folder to open.
        """
        # check if the file or the directory exists
        if not path.exists(target):
            raise IOError("No such file: {0}".format(target))

        # check the read permission
        if not access(target, R_OK):
            raise IOError("Cannot access file: {0}".format(target))

        # open the directory or the file according to the os
        if opersys == "win32":  # Windows
            proc = startfile(path.realpath(target))

        elif opersys.startswith("linux"):  # Linux:
            proc = subprocess.Popen(
                ["xdg-open", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

        elif opersys == "darwin":  # Mac:
            proc = subprocess.Popen(
                ["open", "--", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

        else:
            raise NotImplementedError(
                "Your `%s` isn't a supported operating system`." % opersys
            )

        # end of function
        return proc

    def open_webpage(self, link):
        """Open a link in the user's default web browser.
        
        :param str link: URL to open. Can be a QUrl object.
        """
        if isinstance(link, QUrl):
            link = link.toString()

        webbrowser.open(link, new=0, autoraise=True)
        # method ending
        logger.debug("Link launched in the default web browser: {}".format(link))
        return

    def plugin_metadata(
        self, base_path=path.dirname(__file__), section="general", value="version"
    ):
        """Plugin metadata.txt parser.
        
        :param path base_path: directory path whete the metadata txt is stored
        :param str section: section of values. Until nom, there is only "general".
        :param str value: value to get from the file. Available values:

          * qgisMinimumVersion
          * qgisMaximumVersion
          * description
          * version - [DEFAULT]
          * author
          * email
          * about
          * tracker
          * repository
        """
        config = configparser.ConfigParser()
        if path.isfile(path.join(base_path, "metadata.txt")):
            config.read(path.join(base_path, "metadata.txt"))
            return config.get("general", value)
        else:
            logger.error(path.dirname(__file__))

    def results_pages_counter(self, total=0, page_size=10):
        """Calculate the number of pages for a given number of results.
        
        :param int total: count of metadata in a search request
        :param int page_size: count of metadata to display in each page
        """
        if total <= page_size:
            count_pages = 1
        else:
            if (total % page_size) == 0:
                count_pages = total / page_size
            else:
                count_pages = (total / page_size) + 1
        # method ending
        return int(count_pages)

    def special_search(self, easter_code="isogeo"):
        """Make some special actions in certains cases.
        
        :param str easter_code: easter egg label. Available values:
          
          * isogeo: display Isogeo logo and zoom in our office location
          * picasa: change QGS project title
        """
        canvas = iface.mapCanvas()
        if easter_code == "isogeo":
            # WMS
            wms_params = {
                "service": "WMS",
                "version": "1.3.0",
                "request": "GetMap",
                "layers": "Isogeo:isogeo_logo",
                "crs": "EPSG:3857",
                "format": "image/png",
                "styles": "isogeo_logo",
                "url": "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?",
            }
            wms_uri = unquote(urlencode(wms_params))
            wms_lyr = QgsRasterLayer(wms_uri, "Ici c'est Isogeo !", "wms")
            if wms_lyr.isValid:
                QgsProject.instance().addMapLayer(wms_lyr)
                logger.info("Isogeo easter egg used and WMS displayed!")
            else:
                logger.error("WMS layer failed: {}".format(wms_lyr.error().message()))

            # WFS
            uri = QgsDataSourceURI()
            uri.setParam("url", "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?")
            uri.setParam("service", "WFS")
            uri.setParam("version", "1.1.0")
            uri.setParam("typename", "Isogeo:isogeo_logo")
            uri.setParam("srsname", "EPSG:3857")
            uri.setParam("restrictToRequestBBOX", "0")
            wfs_uri = uri.uri()
            wfs_lyr = QgsVectorLayer(wfs_uri, "Ici c'est Isogeo !", "WFS")
            if wfs_lyr.isValid:
                wfs_style = path.join(
                    path.dirname(path.realpath(__file__)), "isogeo.qml"
                )
                wfs_lyr.loadNamedStyle(wfs_style)
                QgsProject.instance().addMapLayer(wfs_lyr)
                canvas.setExtent(wfs_lyr.extent())
                logger.debug("Isogeo easter egg used")
            else:
                logger.error(
                    "Esater egg - WFS layer failed: {}".format(
                        wfs_lyr.error().message()
                    )
                )
        elif easter_code == "picasa":
            project = QgsProject.instance()
            project.setTitle("Isogeo, le Picasa de l'information géographique")
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
                http = system_proxy_config.get("http")
                if http is None:
                    pass
                else:
                    elements = http.split(":")
                    if len(elements) == 2:
                        host = elements[0]
                        port = elements[1]
                        qgis_host = qsettings.value("proxy/proxyHost", "")
                        qgis_port = qsettings.value("proxy/proxyPort", "")
                        if qgis_host == host:
                            if qgis_port == port:
                                logger.info(
                                    "A proxy is set up both in QGIS "
                                    "and the OS and they match => "
                                    "Proxy config : OK"
                                )
                                pass
                            else:
                                QMessageBox.information(
                                    iface.mainWindow(),
                                    self.tr("Alert", "Tools"),
                                    self.tr(
                                        "Proxy issue : \nQGIS and your OS "
                                        "have different proxy set up.",
                                        "Tools",
                                    ),
                                )
                        else:
                            QMessageBox.information(
                                iface.mainWindow(),
                                self.tr("Alert", "Tools"),
                                self.tr(
                                    "Proxy issue : \nQGIS and your OS have"
                                    " different proxy set ups.",
                                    "Tools",
                                ),
                            )
                    elif len(elements) == 3 and elements[0] == "http":
                        host_short = elements[1][2:]
                        host_long = elements[0] + ":" + elements[1]
                        port = elements[2]
                        qgis_host = qsettings.value("proxy/proxyHost", "")
                        qgis_port = qsettings.value("proxy/proxyPort", "")
                        if qgis_host == host_short or qgis_host == host_long:
                            if qgis_port == port:
                                logger.info(
                                    "A proxy is set up both in QGIS"
                                    " and the OS and they match "
                                    "=> Proxy config : OK"
                                )
                                pass
                            else:
                                logger.error(
                                    "OS and QGIS proxy ports do not "
                                    "match. => Proxy config: not OK"
                                )
                                QMessageBox.information(
                                    iface.mainWindow(),
                                    self.tr("Alert", "Tools"),
                                    self.tr(
                                        "Proxy issue : \nQGIS and your OS"
                                        " have different proxy set ups.",
                                        "Tools",
                                    ),
                                )
                        else:
                            logger.error(
                                "OS and QGIS proxy hosts do not "
                                "match. => Proxy config: not OK"
                            )
                            QMessageBox.information(
                                iface.mainWindow(),
                                self.tr("Alert", "Tools"),
                                self.tr(
                                    "Proxy issue : \nQGIS and your OS have"
                                    " different proxy set ups.",
                                    "Tools",
                                ),
                            )
            else:
                logger.error(
                    "OS uses a proxy but it isn't set up in QGIS."
                    " => Proxy config: not OK"
                )
                QMessageBox.information(
                    iface.mainWindow(),
                    self.tr("Alert", "Tools"),
                    self.tr(
                        "Proxy issue : \nYou have a proxy set up on your"
                        " OS but none in QGIS.\nPlease set it up in "
                        "'Preferences/Options/Network'.",
                        "Tools",
                    ),
                )

    def test_qgis_style(self):
        """
            Check QGIS style applied to ensure compatibility with comboboxes.
            Avert the user and force change if the selected is not adapted.
            See: https://github.com/isogeo/isogeo-plugin-qgis/issues/137.
        """
        style_qgis = qsettings.value("qgis/style", "Default")
        if style_qgis in ("macintosh", "cleanlooks"):
            qsettings.setValue("qgis/style", "Plastique")
            msgBar.pushMessage(
                self.tr(
                    "The '{}' QGIS style is not "
                    "compatible with combobox. It has "
                    "been changed. Please restart QGIS."
                ).format(style_qgis),
                duration=0,
                level=msgBar.WARNING,
            )
            logger.warning(
                "The '{}' QGIS style is not compatible with combobox."
                " Isogeo plugin changed it to 'Plastique'."
                "Please restart QGIS.".format(style_qgis)
            )
            return False
        else:
            return True

    def _to_raw_string(self, in_string):
        """Basic converter for input string or unicode to raw string.
        Useful to prevent escaping in Windows paths for example.

        see: https://github.com/isogeo/isogeo-plugin-qgis/issues/129

        :param str in_string: string (str or unicode) to convert to raw
        """
        if isinstance(in_string, str) or isinstance(in_string, bytes)::
            logger.debug(in_string)
            return in_string.encode("unicode-escape")
        else:
            raise TypeError

    def _ui_tweaker(self, ui_widgets, tweak_type="comboboxes"):
        """Set of tools to tweak PyQT UI widgets.

        :param list ui_widgets: list of widgets on which apply tweaks
        :param str tweak_type: tweak to perform
        """
        if tweak_type == "comboboxes":
            # see: https://github.com/isogeo/isogeo-plugin-qgis/issues/156
            for cbb in ui_widgets:
                width = cbb.view().sizeHintForColumn(0) + 5
                cbb.view().setMinimumWidth(width)
            logger.debug("Comboboxes have been tweaked: width set on values")
        else:
            logger.debug("Tweak type not recognized.")
            pass


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
