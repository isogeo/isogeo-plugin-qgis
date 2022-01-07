# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging

# PyQGIS
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QSettings

# UI classes
from ..ui.portal.dlg_portal_base_url import IsogeoPortalBaseUrl

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()

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

    def __init__(self):

        # Setting ui elements
        self.portalURL_config_dialog = IsogeoPortalBaseUrl()

        # Connecting ui
        self.portalURL_config_dialog.accepted.connect(self.save)
        self.portalURL_config_dialog.chb_portal_url.stateChanged.connect(
            self.update_input_state
        )

    def open_dialog(self):
        """"""

        self.portalURL_config_dialog.input_portal_url.setText(
            qsettings.value("isogeo/settings/portal_base_url", "")
        )
        self.portalURL_config_dialog.chb_portal_url.setChecked(
            int(qsettings.value("isogeo/settings/add_metadata_url_portal", 0))
        )
        self.portalURL_config_dialog.open()

    def save(self):
        """"""

        # save base portal URL in qsettings
        qsettings.setValue(
            "isogeo/settings/portal_base_url", self.portalURL_config_dialog.input_portal_url.text()
        )
        is_checked = int(self.portalURL_config_dialog.chb_portal_url.isChecked())
        qsettings.setValue("isogeo/settings/add_metadata_url_portal", is_checked)

    def update_input_state(self):
        """"""

        is_checked = int(self.portalURL_config_dialog.chb_portal_url.isChecked())
        self.portalURL_config_dialog.input_portal_url.setEnabled(is_checked)
