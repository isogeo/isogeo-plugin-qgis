# -*- coding: utf-8 -*-

# Standard library
import logging

# PyQT
from qgis.PyQt.QtCore import pyqtSignal, QObject, pyqtSlot

# Plugin modules
from ..tools import IsogeoPlgTools

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
plg_tools = IsogeoPlgTools()
# ############################################################################
# ########## Classes ###############
# ##################################


class SharesParser(QObject):
    """Build the string informing the user about the shares feeding his plugin 
    from the Isogeo API's response to a share request.
    """

    shares_ready = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        self.tr = object

    @pyqtSlot(list)
    def send_share_info(self, shares: list):
        """Slot connected to ApiRequester.shares_sig signal emitted when a response 
        to a share request has been received from the Isogeo's API, validated and parsed.
        'shares' parameter correspond to the content of shares request's reply passed 
        by the ApiRequester.handle_reply method (see modules/api/request.py). 
        Once the string building from 'result' is done, the shares_ready signal is emitted 
        passing this string to a connected slot : Isogeo.write_shares_info (see isogeo.py).
        
        :param list shares: list of shares feeding the application
        """
        logger.debug("Application properties provided by the Isogeo API.")
        content = shares

        text = "<html>"  # opening html content
        # Isogeo application authenticated in the plugin
        app = content[0].get("applications")[0]
        text += self.tr(
            "<p>This plugin is authenticated as " "<a href='{}'>{}</a> and "
        ).format(
            app.get("url", "https://isogeo.gitbooks.io/app-plugin-qgis/content"),
            app.get("name", "Isogeo plugin for QGIS"),
        )
        # shares feeding the application
        if len(content) == 1:
            text += self.tr(" powered by 1 share:</p></br>")
        else:
            text += self.tr(" powered by {} shares:</p></br>").format(len(content))
        # shares details
        for share in content:
            # share variables
            creator_name = share.get("_creator").get("contact").get("name")
            creator_email = share.get("_creator").get("contact").get("email")
            creator_id = share.get("_creator").get("_tag")[6:]
            share_url = "https://app.isogeo.com/groups/{}/admin/shares/{}".format(
                creator_id, share.get("_id")
            )
            # formatting text
            text += "<p><a href='{}'><b>{}</b></a></p>".format(
                share_url, share.get("name")
            )
            text += self.tr("<p>Updated: {}</p>").format(
                plg_tools.handle_date(share.get("_modified"))
            )
            text += self.tr("<p>Contact: {} - {}</p>").format(
                creator_name, creator_email
            )
            text += "<p><hr></p>"
        text += "</html>"
        self.shares_ready.emit(text)


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
