# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtGui import QIcon

# UI classes
from ..ui.portal.dlg_portal_base_url import IsogeoPortalBaseUrl

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")

msgBar = iface.messageBar()

ico_bolt = QIcon(":/plugins/Isogeo/resources/edit.svg")

# ############################################################################
# ########## Classes ###############
# ##################################


class PortalURLManager:
    """A basic class to manage quick searches :
    - Create a new quick search by giving it a name and writing its parameters in the JSON file
    (`_user/quicksearches.json`)
    - Rename a quick search
    - Delete a quick search
    """

    def __init__(self, settings_manager: object = None):

        # Setting ui elements
        self.portalURL_config_dialog = IsogeoPortalBaseUrl()

        # Connecting ui
        self.portalURL_config_dialog.accepted.connect(self.save)
        self.portalURL_config_dialog.chb_portal_url.stateChanged.connect(self.update_input_state)

        self.settings_mng = settings_manager

    def open_dialog(self):
        """"""

        self.portalURL_config_dialog.input_portal_url.setText(
            self.settings_mng.config_content.get("portal_base_url")
        )
        self.portalURL_config_dialog.chb_portal_url.setChecked(
            int(self.settings_mng.config_content.get("isogeo/settings/add_metadata_url_portal"))
        )
        self.portalURL_config_dialog.open()

    def save(self):
        """"""

        # save base portal URL in QSettings
        self.settings_mng.set_config_value(
            "portal_base_url", self.portalURL_config_dialog.input_portal_url.text()
        )
        is_checked = int(self.portalURL_config_dialog.chb_portal_url.isChecked())
        self.settings_mng.set_config_value("isogeo/settings/add_metadata_url_portal", is_checked)

    def update_input_state(self):
        """"""

        is_checked = int(self.portalURL_config_dialog.chb_portal_url.isChecked())
        self.portalURL_config_dialog.input_portal_url.setEnabled(is_checked)
