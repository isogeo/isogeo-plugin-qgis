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

    def show(self, message: str, duration: int = 6, level: int = 1):
        self.bar.pushMessage(message, duration=duration, level=level)

    def authentication_slot(self, auth_sig: str = "ok"):
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
                    "Authentication file is valid. Asking for authorization to Isogeo's API.",
                    context=__class__.__name__,
                ),
                5,
                3,
            ],
        }
        if auth_sig in list(msg_dict.keys()):
            msg_type = msg_dict.get(auth_sig)
            self.show(message=msg_type[0], duration=msg_type[1], level=msg_type[2])
        else:
            pass

    def request_slot(self, api_sig: str):
        msg_dict = {
            "creds_issue": self.tr(
                "Redirecting code received. ID and SECRET could be invalid. Provide them again."
                " If this error keeps happening, please report it in the bug tracker.",
                context=__class__.__name__,
            ),
            "proxy_issue": self.tr(
                "Proxy error found. Check your OS and QGIS proxy configuration."
                "If this error keeps happening, please report it in the bug tracker.",
                context=__class__.__name__,
            ),
            "shares_issue": self.tr(
                "The script is looping. Make sure you shared a catalog with the plugin."
                "If this error keeps happening, please report it in the bug tracker.",
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
                "Request to Isogeo's API failed : please check your Internet connection and"
                " your proxy configuration. If this error keeps happening, please report it"
                " in the bug tracker.",
                context=__class__.__name__,
            ),
        }
        if api_sig in list(msg_dict.keys()):
            msg = msg_dict.get(api_sig)
            self.show(message=msg, duration=10)
        else:
            pass
