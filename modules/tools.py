# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import configparser
import datetime
import http.client
import logging
from os import access, path, R_OK
import subprocess
from sys import platform as opersys
from urllib.request import getproxies
import webbrowser

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QSettings, QUrl
from qgis.PyQt.QtWidgets import QMessageBox

# 3rd party
from .isogeo_pysdk import IsogeoUtils

# Depending on operating system
if opersys == "win32":
    """ windows """
    from os import startfile  # to open a folder/file
else:
    pass

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

    tr = object
    last_error = list

    def __init__(self):
        """Check and manage authentication credentials."""
        # instanciate
        super(IsogeoPlgTools, self).__init__()

    def error_catcher(self, msg, tag, level):
        """Catch QGIS error messages for introspection."""
        if tag == "WMS" and level != 0:
            self.last_error = ["wms", msg]
        elif tag == "WFS" and level != 0:
            self.last_error = ["wfs", msg]
        elif tag == "PostGIS" and level != 0:
            self.last_error = ["postgis", msg]
        elif tag == "Oracle" and level != 0:
            self.last_error = ["oracle", msg]
        else:
            pass

    def format_button_title(self, title):
        """Format the title to fit the button.

        :param str title: title to format
        """
        words = title.split(" ")
        if len(words) == 1:
            if len(words[0]) > 22:
                final_text = words[0][:20] + "..."
            else:
                final_text = words[0]
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

    def open_pipedrive_test_form(self, lang):
        """Open the Isogeo Plugin&Widgets test online form in web browser.

        :param str lang: language code. If not fr (French), the English form is displayed.
        """
        if lang == "fr":
            webbrowser.open(
                "https://webforms.pipedrive.com/f/5kAUlfXAdFfv85vV3Mw1PWOYqOBpD7l9GV9wr0OlOAdmQcdC7DduZ6afScQHHZ",
                new=0,
                autoraise=True,
            )
        else:
            webbrowser.open(
                "https://webforms.pipedrive.com/f/5kAUlfXAdFfv85vV3Mw1PWOYqOBpD7l9GV9wr0OlOAdmQcdC7DduZ6afScQHHZ",
                new=0,
                autoraise=True,
            )
        # method ending
        logger.debug(
            "Isogeo Plugin&Widget test form launched in the default web browser"
        )

    def open_pipedrive_rdv_form(self, lang):
        """Open the rdv request online form in web browser.

        :param str lang: language code. If not fr (French), the English form is displayed.
        """
        if lang == "fr":
            webbrowser.open(
                "https://isogeo.pipedrive.com/scheduler/lq0ZSm/rendez-vous-isogeo",
                new=0,
                autoraise=True,
            )
        else:
            webbrowser.open(
                "https://isogeo.pipedrive.com/scheduler/lq0ZSm/rendez-vous-isogeo",
                new=0,
                autoraise=True,
            )
        # method ending
        logger.debug("Isogeo rdv request form launched in the default web browser")

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
        # canvas = iface.mapCanvas()
        if easter_code == "isogeo":
            # # WMS
            # wms_params = {
            #     "service": "WMS",
            #     "version": "1.3.0",
            #     "request": "GetMap",
            #     "layers": "Isogeo:isogeo_logo",
            #     "crs": "EPSG:3857",
            #     "format": "image/png",
            #     "styles": "isogeo_logo",
            #     "url": "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?",
            # }
            # wms_uri = unquote(urlencode(wms_params))
            # wms_lyr = QgsRasterLayer(wms_uri, "Ici c'est Isogeo !", "wms")
            # if wms_lyr.isValid:
            #     QgsProject.instance().addMapLayer(wms_lyr)
            #     logger.info("Isogeo easter egg used and WMS displayed!")
            # else:
            #     logger.error("WMS layer failed: {}".format(wms_lyr.error().message()))

            # # WFS
            # uri = QgsDataSourceUri()
            # uri.setParam("url", "http://noisy.hq.isogeo.fr:6090/geoserver/Isogeo/ows?")
            # uri.setParam("service", "WFS")
            # uri.setParam("version", "1.1.0")
            # uri.setParam("typename", "Isogeo:isogeo_logo")
            # uri.setParam("srsname", "EPSG:3857")
            # uri.setParam("restrictToRequestBBOX", "0")
            # wfs_uri = uri.uri()
            # wfs_lyr = QgsVectorLayer(wfs_uri, "Ici c'est Isogeo !", "WFS")
            # if wfs_lyr.isValid:
            #     wfs_style = path.join(
            #         path.dirname(path.realpath(__file__)), "isogeo.qml"
            #     )
            #     wfs_lyr.loadNamedStyle(wfs_style)
            #     QgsProject.instance().addMapLayer(wfs_lyr)
            #     canvas.setExtent(wfs_lyr.extent())
            #     logger.debug("Isogeo easter egg used")
            # else:
            #     logger.error(
            #         "Esater egg - WFS layer failed: {}".format(
            #             wfs_lyr.error().message()
            #         )
            #     )
            logger.info("Easter egg 'isogeo' spotted!")
        elif easter_code == "picasa":
            # project = QgsProject.instance()
            # project.setTitle("Isogeo, le Picasa de l'information géographique")
            logger.debug("Picasa easter egg used")
        else:
            pass
        # ending method
        return

    def check_proxy_configuration(self) -> bool:
        """Check adequation between system and QGIS proxy configuration. The goal is to\
            prevent network issues connecting to the API. See: https://github.com/isogeo/isogeo-plugin-qgis/issues/287

        Steps:

          1. Retrive proxy settings: from system and from QGIS
          2. Compare them:
            - Case 1: if a proxy is not set in the system or QGIS: everything is fine!
            - Case 2: if a proxy is set at the system level but not in QGIS: warn the user he should take care
            - Case 3 (a and b): if a proxy is set in QGIS but not in the system: depends on proxy type picked in QGIS
            - Case 4: if a proxy is set in QGIS and the system, ensure this is the same

        :rtype: bool
        :returns: True for cases 1, 3a ; False for cases 2, 3b and 4 depending if system and QGIS configs mismatch
        """
        # local connector
        conn_to_isogeo = http.client.HTTPSConnection("api.isogeo.com")
        # -- STEP 1 --------------------------------------------------------------------
        # retrieve system proxy settings
        system_proxy_config = getproxies()
        if system_proxy_config:
            logger.info("Proxy on the system: {}".format(system_proxy_config))
        else:
            logger.info("No proxy settings found on the system.")

        # retrieve QGIS proxy settings
        qgis_proxy_enabled = qsettings.value("proxy/proxyEnabled", False, type=bool)
        if qgis_proxy_enabled is True:
            qgis_proxy_type = qsettings.value(
                "proxy/proxyType", "DefaultProxy", type=str
            )
            logger.info("Proxy enabled in QGIS: {}".format(qgis_proxy_type))
        else:
            logger.info("No proxy enabled in QGIS.")

        # -- STEP 2 --------------------------------------------------------------------
        # Case 1 - No proxy at all
        if not any([system_proxy_config, qgis_proxy_enabled]):
            logger.info(
                "No proxy found in system and QGIS: Freedom! All signals on green! [case 1]"
            )
            try:
                # if no proxy, then we can send a request
                conn_to_isogeo.request("HEAD", "/about")
                resp_about = conn_to_isogeo.getresponse()
                # check requests status
                if resp_about.status >= 300:
                    logger.error(
                        "Connection to Isogeo failed: {} ({})".format(
                            resp_about.reason, resp_about.status
                        )
                    )
                    raise ConnectionError
                else:
                    logger.info(
                        "Network connection to Isogeo API seems to be {} ({})".format(
                            resp_about.reason, resp_about.status
                        )
                    )
            except Exception as exc:
                logger.error(
                    "Despite the absence of proxy, connection to Isogeo API failed: {}".format(
                        exc
                    )
                )

            return True

        # Case 2 - Proxy in system but not enabled in QGIS = issue is coming!
        if system_proxy_config and not qgis_proxy_enabled:
            logger.warning(
                "Proxy found in system {} but not in QGIS: please update network settings in QGIS Preferences. [case 2]".format(
                    system_proxy_config
                )
            )
            QMessageBox.warning(
                iface.mainWindow(),
                self.tr("Alert", context=__class__.__name__),
                self.tr(
                    "Proxy issue: \nYou have a proxy set up on your"
                    " OS {} but none in QGIS.\n Please set it up in "
                    "'Preferences/Options/Network' then close/reopen the plugin.".format(
                        system_proxy_config
                    ),
                    context=__class__.__name__,
                ),
            )
            return False

        # Case 3 - Proxy in QGIS but not in system
        if not system_proxy_config and qgis_proxy_enabled:
            # Case 3a - if proxy type is set to DefaultProxy, it means no proxy
            if qgis_proxy_type == "DefaultProxy":
                logger.info(
                    "{} enabled in QGIS is pointing to the system which is disabled. "
                    "Equivalent to no proxy at all. [case 3a]".format(qgis_proxy_type)
                )
                try:
                    # if no proxy, then we can send a request
                    conn_to_isogeo.request("HEAD", "/about")
                    resp_about = conn_to_isogeo.getresponse()
                    # check requests status
                    if resp_about.status >= 300:
                        logger.error(
                            "Connection to Isogeo failed: {} ({})".format(
                                resp_about.reason, resp_about.status
                            )
                        )
                        raise ConnectionError
                    else:
                        logger.info(
                            "Network connection to Isogeo API seems to be {} ({})".format(
                                resp_about.reason, resp_about.status
                            )
                        )
                except Exception as exc:
                    logger.error(
                        "Despite the absence of proxy, connection to Isogeo API failed: {}".format(
                            exc
                        )
                    )

                return True
            else:
                # Case 3b - if proxy type is not DefaultProxy, it can produce some error
                logger.warning(
                    "{} enabled in QGIS but not in system. No blocking but weird behavior could occur. [case 3b]".format(
                        qgis_proxy_type
                    )
                )
                return False

        # Case 4 - Proxy both in system and QGIS
        if system_proxy_config and qgis_proxy_enabled:
            logger.info(
                "{} enabled in QGIS and in system {}. [case 4]".format(
                    qgis_proxy_type, system_proxy_config
                )
            )
            # if proxy type is DefaultProxy, then ignore it
            if qgis_proxy_type == "DefaultProxy":
                logger.debug(
                    "QGIS is using system settings: {}. [case 4a]".format(
                        system_proxy_config
                    )
                )
                return True

            # compare system and QGIS settings
            qgis_proxy_params = {
                "host": qsettings.value("proxy/proxyHost", None, type=str),
                "port": qsettings.value("proxy/proxyPort", None, type=int),
            }
            logger.debug(qgis_proxy_params)
            return True

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
        if isinstance(in_string, str) or isinstance(in_string, bytes):
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
