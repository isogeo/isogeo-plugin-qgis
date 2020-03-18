# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging

# PyQGIS
from qgis.gui import QgsMessageBar

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

# ############################################################################
# ########## Classes ###############
# ##################################


class UserInformer:
    """ A basic class to manage the displaying of message to the user.
    """

    def __init__(self, message_bar: object, trad: object):
        if isinstance(message_bar, QgsMessageBar):
            self.bar = message_bar
        else:
            raise TypeError
        self.tr = trad

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
                self.tr(
                    "The specified file does not exist.", context=__class__.__name__
                ),
                5,
                1,
            ],
            "file": [
                self.tr(
                    "The selected credentials file's format is not valid.",
                    context=__class__.__name__,
                ),
                5,
                1,
            ],
            "ok": [
                self.tr(
                    "Authentication file is valid. Asking for authorization to Isogeo's"
                    " API.",
                    context=__class__.__name__,
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
            - 'unkown_error'
            - 'unkonw_reply'
            - 'internet_issue'
        """
        msg_dict = {
            "creds_issue": self.tr(
                "ID and SECRET could be invalid. Provide them again."
                " If this error keeps happening, please report it in the bug tracker.",
                context=__class__.__name__,
            ),
            "proxy_issue": self.tr(
                "Proxy error found. Check your OS and QGIS proxy configuration."
                "If this error keeps happening, please report it in the bug tracker.",
                context=__class__.__name__,
            ),
            "shares_issue": self.tr(
                "The script is looping. Make sure you shared a catalog with the plugin "
                "and check your Internet connection. If this error keeps happening, "
                "please report it in the bug tracker.",
                context=__class__.__name__,
            ),
            "unkown_error": self.tr(
                "Request to Isogeo's API failed : unkown error found. Please,"
                " report it in the bug tracker.",
                context=__class__.__name__,
            ),
            "unkonw_reply": self.tr(
                "API authentication failed : unexpected API's reply. Please,"
                " report it in the bug tracker.",
                context=__class__.__name__,
            ),
            "internet_issue": self.tr(
                "Request to Isogeo's API failed : please check your Internet connection"
                " and your proxy configuration. If this error keeps happening, please "
                "report it in the bug tracker.",
                context=__class__.__name__,
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
                context=__class__.__name__,
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
        logger.debug(
            "lim_sig emitted, passing {} to UserInformer lim_slot".format(lim_sig)
        )
        if isinstance(lim_sig, list):
            msg = self.tr(
                "This data is subject to {} legal limitation(s) :".format(len(lim_sig)),
                context=__class__.__name__,
            )
            for lim in lim_sig:
                if lim.description != "":
                    msg += "\n - {}".format(lim.description)
                else:
                    msg += self.tr(
                        "\n - No description provided", context=__class__.__name__
                    )
            self.display(message=msg, duration=14, level=0)
        else:
            raise TypeError
