# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

# Standard library
from functools import partial
from os import path
import logging

# PyQGIS
from qgis.core import QgsApplication, QgsMapLayerRegistry, QgsMessageLog, QgsVectorLayer
from qgis.gui import QgsMapCanvas, QgsMapCanvasLayer

# PyQT
from PyQt4.QtCore import QSettings, Qt
from PyQt4.QtGui import QTableWidgetItem

# Custom modules
from .api import IsogeoApiManager
from .tools import Tools
from .translator import IsogeoTranslator
from .url_builder import UrlBuilder

# ############################################################################
# ########## Globals ###############
# ##################################

custom_tools = Tools()
isogeo_api_mng = IsogeoApiManager()
logger = logging.getLogger("IsogeoQgisPlugin")
qsettings = QSettings()
srv_url_bld = UrlBuilder()

# ############################################################################
# ########## Classes ###############
# ##################################


class MetadataDisplayer(object):
    """Basic class that holds utilitary methods for the plugin."""

    def __init__(self, ui_md_details):
        """Class constructor."""
        self.complete_md = ui_md_details
        # self.complete_md.btn_ok_close.connect(ui_md_details.closeEvent)

        # some basic settings
        self.map = QgsMapCanvas(parent=self.complete_md.wid_bbox)
        # self.complete_md.wid_bbox.setCanvasColor(Qt.white)
        # self.complete_md.wid_bbox.enableAntiAliasing(True)

    def show_complete_md(self, md, lang="EN"):
        """Open the pop up window that shows the metadata sheet details."""
        logger.info("Displaying the whole metadata sheet.")
        tags = isogeo_api_mng.get_tags(md)
        isogeo_tr = IsogeoTranslator(qsettings.value('locale/userLocale')[0:2])

        # -- GENERAL ---------------------------------------------------------
        title = md.get("title", "NR")
        self.complete_md.lbl_title.setText(md.get("title", "NR"))
        self.complete_md.val_owner.setText(md.get("_creator")
                                             .get("contact")
                                             .get("name", "NR"))
        # Keywords
        kwords = tags.get("keywords", {"none": "NR"})
        self.complete_md.val_keywords.setText(" ; ".join(kwords.values()))
        # INSPIRE themes and conformity
        themes = tags.get("themeinspire", {"none": "NR"})
        self.complete_md.val_inspire_themes.setText(" ; ".join(themes.values()))
        if tags.get("inspire_conformity"):
            self.complete_md.ico_inspire_conformity.setEnabled(1)
            self.complete_md.ico_inspire_conformity.setToolTip(
                                                    isogeo_tr.tr("quality",
                                                                 "isConform")\
                                                    + " INSPIRE")
        else:
            self.complete_md.ico_inspire_conformity.setDisabled(1)
            self.complete_md.ico_inspire_conformity.setToolTip(
                                                    isogeo_tr.tr("quality",
                                                                 "isNotConform")\
                                                    + " INSPIRE")
        # Abstract
        self.complete_md.val_abstract.setText(md.get("abstract", "NR"))

        # -- FEATURE ATTRIBUTES ----------------------------------------------
        if md.get("type") == "vectorDataset":
            tbl_attr = self.complete_md.tbl_attributes
            fields = md.get("feature-attributes", dict())
            tbl_attr.setRowCount(len(fields))
            idx = 0
            for i in fields:
                tbl_attr.setItem(idx, 0, QTableWidgetItem(i.get("name", "NR")))
                tbl_attr.setItem(idx, 1, QTableWidgetItem(i.get("alias", "")))
                tbl_attr.setItem(idx, 2, QTableWidgetItem(i.get("dataType", "")))
                tbl_attr.setItem(idx, 3, QTableWidgetItem(i.get("description", "")))
                idx += 1

            # adapt size
            tbl_attr.horizontalHeader().setStretchLastSection(True)
            tbl_attr.verticalHeader().setResizeMode(3)
        else:
            menu_list = self.complete_md.li_menu
            item = menu_list.item(1)
            item.setHidden(1)
            pass

        # -- CONTACTS --------------------------------------------------------
        contacts = md.get("contacts", dict())
        contacts_pt_cct = ["<b>{1}</b> ({2})"
                           "<br><a href='mailto:{3}' target='_top'>{3}</a>"
                           "<br>{4}"
                           "<br>{5} {6}"
                           "<br>{7} {8}"
                           "<br>{8}"
                           "<br>{9}"
                           .format(isogeo_tr.tr("roles", ctact.get("role")),
                                   ctact.get("contact").get("name", "NR"),
                                   ctact.get("contact").get("organization", "NR"),
                                   ctact.get("contact").get("email", "NR"),
                                   ctact.get("contact").get("phone", "NR"),
                                   ctact.get("contact").get("addressLine1", ""),
                                   ctact.get("contact").get("addressLine2", ""),
                                   ctact.get("contact").get("zipCode", ""),
                                   ctact.get("contact").get("city", ""),
                                   ctact.get("contact").get("country", ""))\
                           for ctact in sorted(contacts) if ctact.get("role", "NR") == "pointOfContact"]
        contacts_other_cct = ["<b>{0} - {1}</b> ({2})"
                              "<br><a href='mailto:{3}' target='_blank'>{3}</a>"
                              "<br>{4}"
                              "<br>{5} {6}"
                              "<br>{7} {8}"
                              "<br>{9}"
                              .format(isogeo_tr.tr("roles", ctact.get("role")),
                                      ctact.get("contact").get("name", "NR"),
                                      ctact.get("contact").get("organization", "NR"),
                                      ctact.get("contact").get("email", "NR"),
                                      ctact.get("contact").get("phone", ""),
                                      ctact.get("contact").get("addressLine1", ""),
                                      ctact.get("contact").get("addressLine2", ""),
                                      ctact.get("contact").get("zipCode", ""),
                                      ctact.get("contact").get("city", ""),
                                      ctact.get("contact").get("country", ""),)
                              for ctact in sorted(contacts) if ctact.get("role") != "pointOfContact"]

        # write
        self.complete_md.val_ct_pointof.setText("<br>________________<br>".join(contacts_pt_cct))
        self.complete_md.val_ct_other.setText("<br>__________________<br>".join(contacts_other_cct))

        # -- HISTORY ---------------------------------------------------------
        # Data creation and last update dates
        self.complete_md.val_data_crea.setText(custom_tools.handle_date(
                                               md.get("_created", "NR")))
        self.complete_md.val_data_update.setText(custom_tools.handle_date(
                                                 md.get("_modified", "NR")))
        # Update frequency information
        if md.get("updateFrequency", None):
            freq = md.get("updateFrequency")
            frequency_info = "{}{} {}"\
                             .format(isogeo_tr.tr(None, "frequencyUpdateHelp"),
                                     ''.join(i for i in freq if i.isdigit()),
                                     isogeo_tr.tr("frequencyShortTypes",
                                                  freq[-1]))
            self.complete_md.val_frequency.setText(frequency_info)
        else:
            self.complete_md.val_frequency.setText("NR")
        # Validity
        self.complete_md.val_valid_start.setText(custom_tools.handle_date(
                                                 md.get("validFrom", "NR")))
        self.complete_md.val_valid_end.setText(custom_tools.handle_date(
                                               md.get("validTo", "NR")))
        self.complete_md.val_valid_comment.setText(md.get("validComment", "NR"))
        # Collect information
        self.complete_md.val_method.setText(md.get("collectionMethod", "NR"))
        self.complete_md.val_context.setText(md.get("collectionContext", "NR"))

        # last modifications
        events = md.get("events", dict())
        tbl_events = self.complete_md.tbl_events
        tbl_events.setRowCount(len(events))
        idx = 0
        for e in events:
            if e.get("kind") == "update":
                tbl_events.setItem(idx, 0, QTableWidgetItem(custom_tools.handle_date(e.get("date", "NR"))))
                tbl_events.setItem(idx, 1, QTableWidgetItem(e.get("description", "")))
                idx += 1
            else:
                pass

        # adapt size
        tbl_events.horizontalHeader().setStretchLastSection(True)
        tbl_events.verticalHeader().setResizeMode(3)

        # -- TECHNICAL -------------------------------------------------------
        # SRS
        if tags['srs'] != {}:
            self.complete_md.val_srs.setText(tags['srs'].values()[0])
        else:
            self.complete_md.val_srs.setText('NR')
        # Set the data format
        if tags['formats'] != {}:
            self.complete_md.val_format.setText(
                tags['formats'].values()[0])
        else:
            self.complete_md.val_format.setText('NR')
        # Geography
        # print(dir(self.complete_md.wid_bbox))
        geojson_contributors = path.join(path.dirname(
                                         QgsApplication.developersMapFilePath()),
                                         "contributors.json")

        layer = QgsVectorLayer(geojson_contributors, "Contributors", "ogr")
        layers = QgsMapLayerRegistry.instance().mapLayers()
        # QgsMapLayerRegistry.instance().addMapLayer(layer)
        map_canvas_layer_list = [QgsMapCanvasLayer(layer)]
        # layers.addMapLayer(layer)
        self.complete_md.wid_bbox.setLayerSet(map_canvas_layer_list)
        self.complete_md.wid_bbox.setExtent(layer.extent())

        # -- CGUs ------------------------------------------------------------
        # Licences
        cgus_in = md.get("conditions", dict())
        cgus_out = []
        for c_in in cgus_in:
            if "license" in c_in:
                cgu_text = "<a href='{1}'><b>{0}</b></a>"\
                           "<br>{2}"\
                           "<br>{3}".format(c_in.get("license").get("name", "NR"),
                                            c_in.get("license").get("link", ""),
                                            c_in.get("description", ""),
                                            c_in.get("license").get("content", ""))
            else:
                cgu_text = "<b>{0}</b>"\
                           "<br>{1}".format(isogeo_tr.tr("conditions", "noLicense"),
                                            c_in.get("description", ""))



            # store into the final list
            cgus_out.append(cgu_text)

        # write
        self.complete_md.val_licenses.setText("<br>________________<br>".join(cgus_out))          

        # Limitations
        lims_in = md.get("limitations", dict())
        lims_out = []
        for l_in in lims_in:
            lim_text = "<b>{0}</b>"\
                       "<br>{1}".format(isogeo_tr.tr("limitations", l_in.get("type")),
                                        l_in.get("description", ""))
            # legal type
            if l_in.get("type") == "legal":
                lim_text += "<br>" + isogeo_tr.tr("restrictions", l_in.get("restriction"))
            else:
                pass
            # INSPIRE precision
            if "directive" in l_in:
                lim_text += "<br><u>INSPIRE</u><br>"\
                            "<ul><li>{}</li><li>Tea</li></ul>"\
                            .format(l_in.get("directive").get("name"),
                                    l_in.get("directive").get("description"))
            else:
                pass

            # store into the final list
            lims_out.append(lim_text)

        # write
        self.complete_md.val_limitations.setText("<br>________________<br>".join(lims_out))

        # for l_in in lims_in:
        #     limitation = {}
        #     # ensure other fields
        #     limitation["description"] = self.clean_xml(l_in.get("description", ""))
        #     limitation["type"] = self.tr("limitations", l_in.get("type"))
        #     # legal type
        #     if l_in.get("type") == "legal":
        #         limitation["restriction"] = self.tr("restrictions", l_in.get("restriction"))
        #     else:
        #         pass
        #     # INSPIRE precision
        #     if "directive" in l_in.keys():
        #         limitation["inspire"] = self.clean_xml(l_in.get("directive").get("name"))
        #         limitation["content"] = self.clean_xml(l_in.get("directive").get("description"))
        #     else:
        #         pass

            # store into the final list
            # lims_out.append(limitation)

        # -- ADVANCED  TAB ---------------------------------------------------
        # Workgroup owner
        wg_id = md.get("_creator").get("_id")
        wg_contact = md.get("_creator").get("contact")
        self.complete_md.val_owner_name.setText(wg_contact.get("name", ""))
        self.complete_md.val_owner_email.setText(wg_contact.get("email", ""))
        self.complete_md.val_owner_phone.setText(wg_contact.get("phone", ""))
        self.complete_md.val_owner_address.setText(wg_contact.get("addressLine1", ""))
        self.complete_md.val_owner_city.setText(wg_contact.get("zipCode", ""))
        self.complete_md.val_owner_country.setText(wg_contact.get("countryCode", ""))

        # Metadata
        self.complete_md.val_md_lang.setText(md.get("language", ""))
        self.complete_md.val_md_date_crea.setText(custom_tools.handle_date(
                                                  md.get("_modified")[:19]))
        self.complete_md.val_md_date_update.setText(custom_tools.handle_date(
                                                    md.get("_created")[:19]))

        # -- EDIT LINK -------------------------------------------------------
        url_edition = "https://app.isogeo.com/groups/{}/resources/{}"\
                      .format(wg_id, md.get("_id"))
        self.complete_md.btn_md_edit.pressed.connect(
             partial(custom_tools.open_webpage, link=url_edition))

        # -- DISPLAY ---------------------------------------------------------
        # Finally open the damn window
        self.complete_md.show()
        try:
            QgsMessageLog.logMessage("Detailed metadata displayed: {}"
                                     .format(title),
                                     "Isogeo")
        except UnicodeEncodeError:
            QgsMessageLog.logMessage("Detailed metadata displayed: {}"
                                     .format(title.encode("latin1")),
                                     "Isogeo")
