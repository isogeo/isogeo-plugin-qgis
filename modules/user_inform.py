# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
from pathlib import Path
import logging

# PyQT
from qgis.PyQt.QtCore import QCoreApplication, Qt, QTranslator

# PyQGIS
from qgis.gui import QgsMessageBar

# submodule
from .settings_manager import SettingsManager

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
settings_mng = SettingsManager()


# initialize locale
locale = settings_mng.get_locale()
plugin_dir = Path(__file__).parents[1]

i18n_file_path = plugin_dir / "i18n" / "isogeo_search_engine_{}.qm".format(locale)

if i18n_file_path.exists():
    translator = QTranslator()
    translator.load(str(i18n_file_path))
    QCoreApplication.installTranslator(translator)
else:
    pass

# ############################################################################
# ########## Classes ###############
# ##################################


class UserInformer:
    """A basic class to manage the displaying of message to the user."""

    def __init__(self, message_bar: object):
        if isinstance(message_bar, QgsMessageBar):
            self.bar = message_bar
        else:
            raise TypeError

    def display(self, message: str, duration: int = 6, level: int = 1):
        """A simple relay in charge of displaying messages to the user in the message
        bar given has an instanciation attribute.

        :param str message: the message to display
        :param int duration: message display duration in seconds
        :param int level: Qgis.MessageLevel used to set message bar's style

        """
        self.bar.pushMessage(message, duration=duration, level=level)

    def authentication_slot(self, auth_sig: str = "ok"):
        """Slot connected to Authenticator.auth_sig signal emitted after the format and
        accessibility of the JSON file specified by the user has been tested.

        :param str auth_sig: Options :
            - 'path'
            - 'file'
            - 'ok'
        """
        msg_dict = {
            "path": [
                self.tr("The specified file does not exist."),
                5,
                1,
            ],
            "file": [
                self.tr(
                    "The selected credentials file's format is not valid.",
                ),
                5,
                1,
            ],
            "ok": [
                self.tr(
                    "Authentication file is valid. Asking for authorization to Isogeo's" " API.",
                ),
                5,
                0,
            ],
        }
        if auth_sig in list(msg_dict.keys()):
            msg_type = msg_dict.get(auth_sig)
            self.display(message=msg_type[0], duration=msg_type[1], level=msg_type[2])
        else:
            pass

    def request_slot(self, api_sig: str):
        """Slot connected to ApiRequester.api_sig signal emitted when a problem is
        detected with the API response.

        :param str auth_sig: Options :
            - 'creds_issue'
            - 'proxy_issue'
            - 'shares_issue'
            - 'unknown_error'
            - 'unkonw_reply'
            - 'internet_issue'
            - 'config_issue'
        """
        msg_dict = {
            "creds_issue": self.tr(
                "ID and SECRET could be invalid. Provide them again."
                " If this error keeps happening, please report it in the bug tracker.",
            ),
            "proxy_issue": self.tr(
                "Proxy error found. Check your OS and QGIS proxy configuration."
                "If this error keeps happening, please report it in the bug tracker.",
            ),
            "shares_issue": self.tr(
                "The script is looping. Make sure you shared a catalog with the plugin "
                "and check your Internet connection. If this error keeps happening, "
                "please report it in the bug tracker.",
            ),
            "unknown_error": self.tr(
                "Request to Isogeo's API failed : unkown error found. Please,"
                " report it in the bug tracker.",
            ),
            "unkonw_reply": self.tr(
                "API authentication failed : unexpected API's reply. Please,"
                " report it in the bug tracker.",
            ),
            "internet_issue": self.tr(
                "Request to Isogeo's API failed : please check your Internet connection"
                " and your proxy configuration. If this error keeps happening, please "
                "report it in the bug tracker.",
            ),
            "config_issue": self.tr(
                "Search request to Isogeo's API failed : please check that 'api_base_url' and "
                "'api_auth_url' URLs specified into config.json file are pointing to the same API.",
            ),
        }
        if api_sig in list(msg_dict.keys()):
            msg = msg_dict.get(api_sig)
            self.display(message=msg, duration=10)
        else:
            pass

    def shares_slot(self, shares_sig: str):
        """Slot connected to SharesParser.shares_ready signal emitted when informations
        about the shares feeding the plugin have been parsed.

        :param str shares_sig: str passed by SharesParser
        """

        msg_dict = {
            "no_shares": self.tr(
                "No share feeds the plugin. If you want to access resources via the "
                "plugin, you must share at least one catalog containing at least one "
                "metadata with it.",
            )
        }
        if shares_sig in list(msg_dict.keys()):
            msg = msg_dict.get(shares_sig)
            self.display(message=msg, duration=10)
        else:
            pass

    def lim_slot(self, lim_sig: list):
        """
        :param dict lim_sig: informations about data limitation the message is about
        """
        if isinstance(lim_sig, list):
            msg = (
                "<b>"
                + (
                    self.tr("This data is subject to ")
                    + str(len(lim_sig))
                    + self.tr(" legal limitation(s) :")
                )
                + "</b>"
            )
            for lim in lim_sig:
                msg += "<br>- "
                if lim.description != "":
                    msg += lim.description
                else:
                    msg += "<i>"
                    msg += self.tr("No description provided")
                    msg += "</i>"
            self.display(message=msg, duration=14, level=0)
        else:
            raise TypeError

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(__class__.__name__, message)
