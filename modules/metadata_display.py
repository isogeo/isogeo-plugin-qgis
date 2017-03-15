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
        # self.complete_md.closingPlugin.connect(ui_md_details.closeEvent)

        # some basic settings
        self.complete_md.wid_bbox.setCanvasColor(Qt.white)
        self.complete_md.wid_bbox.enableAntiAliasing(True)

    def show_complete_md(self, md, lang="EN"):
        """Open the pop up window that shows the metadata sheet details."""
        logger.info("Displaying the whole metadata sheet.")
        tags = isogeo_api_mng.get_tags(md)
        isogeo_tr = IsogeoTranslator(qsettings.value('locale/userLocale')[0:2])

        # -- GENERAL ---------------------------------------------------------
        title = md.get("title", "NR")
        self.complete_md.lbl_title.setText(title)

        # -- FEATURE ATTRIBUTES ----------------------------------------------
        if md.get("type") == "vectorDataset":
            print("let's parse attributes")
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
        for i in contacts:
            ctc_txt = ""
            role = i.get("role", "NR")
            print(role, isogeo_tr.tr("roles", role))
            ctc_txt += "<b>Role :</b> {}\n\n"\
                       .format(isogeo_tr.tr("roles", role))

            # write
            # ctc_txt = ctc_txt[:-20]
            self.complete_md.val_contact.setText(ctc_txt)



        # if len(contacts):
        #     contacts_pt_cct = ["{0} ({1})".format(contact.get("contact").get("name"),
        #                                           contact.get("contact").get("email"))\
        #                        for contact in contacts if contact.get("role") == "pointOfContact"]
        #     contacts_other_cct = ["{0} ({1})".format(contact.get("contact").get("name"),
        #                                              contact.get("contact").get("email"))\
        #                           for contact in contacts if contact.get("role") != "pointOfContact"]
        #     ws["AF{}".format(idx)] = len(contacts)
        #     ws["AG{}".format(idx)] = " ;\n".join(contacts_pt_cct)
        #     ws["AH{}".format(idx)] = " ;\n".join(contacts_other_cct)
        # else:
        #     ws["AF{}".format(idx)] = 0
        #     logging.info("Vector dataset without any contact")

        # Set the data contacts (data creator, data manager, ...)
        # ctc = md.get('contacts')
        # if ctc is not None and ctc != []:
        #     ctc_text = ""
        #     for i in ctc:
        #         contact = i.get('contact')
        #         if contact is not None:
        #             ctc_text += "Contact :\n"
        #             name = contact.get('name')
        #             if name is not None:
        #                 ctc_text += name
        #                 org = contact.get('organization')
        #                 if org is not None:
        #                     ctc_text += " - " + org + "\n"
        #                 else:
        #                     ctc_text += "\n"
        #             mail = contact.get('email')
        #             if mail is not None:
        #                 ctc_text += mail + "\n"
        #             phone = contact.get('phone')
        #             if phone is not None:
        #                 ctc_text += phone + "\n"
        #             adress = contact.get('addressLine1')
        #             if adress is not None:
        #                 adress2 = contact.get('addressLine2')
        #                 if adress2 is not None:
        #                     ctc_text += adress + " - " + adress2 + "\n"
        #                 else:
        #                     ctc_text += adress + "\n"
        #             zipc = contact.get('zipCode')
        #             if zipc is not None:
        #                 ctc_text += zipc + "\n"
        #             city = contact.get('city')
        #             if city is not None:
        #                 ctc_text += city + "\n"
        #             country = contact.get('countryCode')
        #             if country is not None:
        #                 ctc_text += country + "\n"
        #         ctc_text += " ________________ \n\n"

        # else:
        #     self.complete_md.val_contact.setText("None")

        # -- HISTORY ---------------------------------------------------------
        # Set the data creation date
        self.complete_md.val_data_crea\
                        .setText(custom_tools.handle_date(
                                 md.get("_created", "NR")))
        # Set the data last modification date
        self.complete_md.val_data_updt\
                        .setText(custom_tools.handle_date(
                                 md.get("_modified", "NR")))
        # Set the date from which the data is valid
        self.complete_md.val_valid_start\
                        .setText(custom_tools.handle_date(
                                 md.get("validFrom", "NR")))
        # Set the date from which the data stops being valid
        valid_to = md.get('validTo')
        if valid_to is not None:
            self.complete_md.val_valid_end.setText(custom_tools.handle_date(
                valid_to))
        else:
            self.complete_md.val_valid_end.setText('NR')
        # Set the data owner
        if tags['owner'] != {}:
            self.complete_md.val_owner.setText(tags['owner'].values()[0])
        else:
            self.complete_md.val_owner.setText('NR')
        # Set the data coordinate system
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
        # Set the associated keywords list
        if tags['keywords'] != {}:
            keystring = ""
            for key in tags['keywords'].values():
                keystring += key + ", "
            keystring = keystring[:-2]
            self.complete_md.val_keywords.setText(keystring)
        else:
            self.complete_md.val_keywords.setText('None')
        # Set the associated INSPIRE themes list
        if tags['themeinspire'] != {}:
            inspirestring = ""
            for inspire in tags['themeinspire'].values():
                inspirestring += inspire + ", "
            inspirestring = inspirestring[:-2]
            self.complete_md.val_inspire_themes.setText(inspirestring)
        else:
            self.complete_md.val_inspire_themes.setText('None')
        # Set the data abstract
        self.complete_md.val_abstract.setText(md.get("abstract",
                                                     "NR"))
        # Set the collection method text
        coll_method = md.get('collectionMethod')
        if coll_method is not None:
            self.complete_md.val_method.setText(
                md['collectionMethod'])
        else:
            self.complete_md.val_method.setText('NR')
        coll_context = md.get('collectionContext')
        if coll_context is not None:
            self.complete_md.val_context.setText(
                md['collectionContext'])
        else:
            self.complete_md.val_context.setText('NR')
        # Set the data events list (creation, multiple modifications, ...)
        self.complete_md.list_events.clear()
        if md['events'] != []:
            for i in md['events']:
                event = custom_tools.handle_date(i['date']) + " : " + i['kind']
                if i['kind'] == 'update' and 'description' in i \
                        and i['description'] != '':
                    event += " (" + i['description'] + ")"
                self.complete_md.list_events.addItem(event)
        # Set the data usage conditions
        cond = md.get('conditions')
        if cond is not None and cond != []:
            cond_text = ""
            for i in cond:
                lc = i.get('license')
                if lc is not None:
                    name = lc.get('name')
                    if name is not None:
                        cond_text += name + "\n"
                    link = lc.get('link')
                    if link is not None:
                        cond_text += link + "\n"
                desc = i.get('description')
                if desc is not None and desc != []:
                    cond_text += desc + "\n"
                cond_text += " ________________ \n\n"
            cond_text = cond_text[:-20]
            # self.complete_md.val_conditions.setText(cond_text)
        else:
            # self.complete_md.val_conditions.setText("None")
            pass
        # Set the data usage limitations
        lim = md.get('limitations')
        if lim is not None and lim != []:
            lim_text = ""
            for i in lim:
                lim_type = i.get('type')
                if lim_type == 'legal':
                    restriction = i.get('restriction')
                    if restriction is not None:
                        lim_text += restriction + "\n"
                desc = i.get('description')
                if desc is not None and desc != []:
                    lim_text += desc + "\n"
                dr = i.get('directive')
                if dr is not None:
                    lim_text += "Directive :\n"
                    name = dr.get('name')
                    if name is not None:
                        lim_text += name + "\n"
                    dr_desc = dr.get('desc')
                    if dr_desc is not None:
                        lim_text += dr_desc + "\n"
                lim_text += " ________________ \n\n"
            lim_text = lim_text[:-20]
            self.complete_md.val_limitations.setText(lim_text)
        else:
            self.complete_md.val_limitations.setText("None")


        # -- GEOGRAPHY ---------------------------------------------------
        # print(dir(self.complete_md.wid_bbox))
        geojson_contributors = path.join(
                               path.dirname(QgsApplication.developersMapFilePath()),
                                            'contributors.json')

        layer = QgsVectorLayer(geojson_contributors, "youhou", "ogr")
        layers = QgsMapLayerRegistry.instance().mapLayers()
        # QgsMapLayerRegistry.instance().addMapLayer(layer)
        map_canvas_layer_list = [QgsMapCanvasLayer(layer)]
        # layers.addMapLayer(layer)
        self.complete_md.wid_bbox.setLayerSet(map_canvas_layer_list)
        self.complete_md.wid_bbox.setExtent(layer.extent())


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
