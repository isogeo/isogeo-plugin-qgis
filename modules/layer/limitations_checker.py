# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from functools import partial

# PyQT
from qgis.PyQt.QtCore import QSettings, QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QMessageBox

# isogeo_pysdk
from ..isogeo_pysdk.models import Limitation, Directive

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

# ############################################################################
# ########## Classes ###############
# ##################################


class LimitationsChecker(QObject):
    """Basic class that holds methods to check the conditions and limitations of access
    to the data before adding them to the canvas."""

    lim_sig = pyqtSignal(list)

    def __init__(self, layer_adder, tr):
        # inheritance
        super().__init__()
        self.layer_adder = layer_adder
        self.tr = tr

    def check(self, data_info: dict):
        logger.debug("Checking data access conditions and limitation")
        limitations = data_info.get("limitations", None)
        # if there are no limits, ok for adding the layer
        if len(limitations) == 0:
            logger.debug("No limitations found, let's add this layer to the canvas !")
            self.layer_adder.adding(layer_info=data_info.get("layer"))
        else:
            li_lim = []
            for lim in limitations:
                lim = Limitation(**lim)
                if lim.directive:
                    directive = Directive(**lim.directive)
                else:
                    directive = Directive()
                # for 'legal' limitations, fill the list
                if lim.type == "legal":
                    # for this directive, no need to informe the user
                    if (
                        lim.restriction == "other"
                        and directive._id == "6756c1875d06446982ed941555102c72"
                    ):
                        pass
                    # for other legal limitations, need to informe the user
                    else:
                        logger.debug("legal limitation detected : {}".format(lim))
                        li_lim.append(lim)
                # for any 'security' limitation, let's show the blocking popup and end the method
                elif lim.type == "security":
                    popup = QMessageBox()
                    popup.setWindowTitle("Limitations")

                    popup_txt = "<b>" + self.tr(
                        "This data is subject to a security limitation :",
                        __class__.__name__,
                    ) + "</b>"
                    if lim.description != "":
                        popup_txt += "<br>{}".format(lim.description)
                    else:
                        popup_txt += "<br><i>"
                        popup_txt += self.tr(
                            "No description provided", context=__class__.__name__
                        )
                        popup_txt += "</i>"
                    popup.setText(popup_txt)

                    popup.setInformativeText(
                        "<b>" + self.tr(
                            "Do you want to add the layer to the canvas anyway ?",
                            context=__class__.__name__,
                        ) + "</b>"
                    )
                    popup.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                    popup.setDefaultButton(QMessageBox.No)
                    popup.finished.connect(
                        partial(self.finished_slot, data_info.get("layer"))
                    )
                    popup.exec()
                    return
                else:
                    logger.info(
                        "Unexpected data limitation type : {}".format(lim.to_str())
                    )
                    pass
            # if all limitations are 'legal' type and 'No limit' INSPIRE directive, let's add the layer
            if len(li_lim) == 0:
                self.layer_adder.adding(layer_info=data_info.get("layer"))
                return
            # if there are other 'legal' type limitation, let's inform the user before adding the layer
            else:
                self.lim_sig.emit(li_lim)
                self.layer_adder.adding(layer_info=data_info.get("layer"))
                return

    def finished_slot(self, layer_info, i):
        if i == QMessageBox.Yes:
            self.layer_adder.adding(layer_info=layer_info)
            return
        else:
            return
