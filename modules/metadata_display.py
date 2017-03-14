# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

# Standard library
import logging

# PyQGIS
from qgis.core import QgsMessageLog

# PyQT
from PyQt4.QtCore import QSettings
from PyQt4.QtGui import QTableWidgetItem

# Custom modules
from .api import IsogeoApiManager
from .tools import Tools
from .url_builder import UrlBuilder

# ############################################################################
# ########## Globals ###############
# ##################################

isogeo_api_mng = IsogeoApiManager()
custom_tools = Tools()
srv_url_bld = UrlBuilder()
qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

# ############################################################################
# ########## Classes ###############
# ##################################


class MetadataDisplayer(object):
    """Basic class that holds utilitary methods for the plugin."""

    def __init__(self, ui_md_details):
        """Class constructor."""
        self.complete_md = ui_md_details

    def show_complete_md(self, content):
        """Open the pop up window that shows the metadata sheet details."""
        logger.info("Displaying the whole metadata sheet.")
        tags = isogeo_api_mng.get_tags(content)
        # IDENTIFICATION
        title = content.get("title", "NR")
        self.complete_md.lbl_title.setText(title)
        # HISTORY
        # Set the data creation date
        self.complete_md.val_data_crea\
                        .setText(custom_tools.handle_date(
                                 content.get("_created", "NR")))
        # Set the data last modification date
        self.complete_md.val_data_updt\
                        .setText(custom_tools.handle_date(
                                 content.get("_modified", "NR")))
        # Set the date from which the data is valid
        self.complete_md.val_valid_start\
                        .setText(custom_tools.handle_date(
                                 content.get("validFrom", "NR")))
        # Set the date from which the data stops being valid
        valid_to = content.get('validTo')
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
        self.complete_md.val_abstract.setText(content.get("abstract",
                                                              "NR"))
        # Set the collection method text
        coll_method = content.get('collectionMethod')
        if coll_method is not None:
            self.complete_md.val_method.setText(
                content['collectionMethod'])
        else:
            self.complete_md.val_method.setText('NR')
        coll_context = content.get('collectionContext')
        if coll_context is not None:
            self.complete_md.val_context.setText(
                content['collectionContext'])
        else:
            self.complete_md.val_context.setText('NR')
        # Set the data contacts (data creator, data manager, ...)
        ctc = content.get('contacts')
        if ctc is not None and ctc != []:
            ctc_text = ""
            for i in ctc:
                role = i.get('role')
                if role is not None:
                    ctc_text += "Role :\n" + role + "\n\n"
                else:
                    ctc_text += "Role :\nNR\n\n"
                contact = i.get('contact')
                if contact is not None:
                    ctc_text += "Contact :\n"
                    name = contact.get('name')
                    if name is not None:
                        ctc_text += name
                        org = contact.get('organization')
                        if org is not None:
                            ctc_text += " - " + org + "\n"
                        else:
                            ctc_text += "\n"
                    mail = contact.get('email')
                    if mail is not None:
                        ctc_text += mail + "\n"
                    phone = contact.get('phone')
                    if phone is not None:
                        ctc_text += phone + "\n"
                    adress = contact.get('addressLine1')
                    if adress is not None:
                        adress2 = contact.get('addressLine2')
                        if adress2 is not None:
                            ctc_text += adress + " - " + adress2 + "\n"
                        else:
                            ctc_text += adress + "\n"
                    zipc = contact.get('zipCode')
                    if zipc is not None:
                        ctc_text += zipc + "\n"
                    city = contact.get('city')
                    if city is not None:
                        ctc_text += city + "\n"
                    country = contact.get('countryCode')
                    if country is not None:
                        ctc_text += country + "\n"
                ctc_text += " ________________ \n\n"
            ctc_text = ctc_text[:-20]
            self.complete_md.val_contact.setText(ctc_text)
        else:
            self.complete_md.val_contact.setText("None")
        # Set the data events list (creation, multiple modifications, ...)
        self.complete_md.list_events.clear()
        if content['events'] != []:
            for i in content['events']:
                event = custom_tools.handle_date(i['date']) + " : " + i['kind']
                if i['kind'] == 'update' and 'description' in i \
                        and i['description'] != '':
                    event += " (" + i['description'] + ")"
                self.complete_md.list_events.addItem(event)
        # Set the data usage conditions
        cond = content.get('conditions')
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
        lim = content.get('limitations')
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
        # Set the data attributes description
        if 'feature-attributes' in content:
            nb = len(content['feature-attributes'])
            self.complete_md.tbl_attributes.setRowCount(nb)
            count = 0
            for i in content['feature-attributes']:
                self.complete_md.tbl_attributes.setItem(
                    count, 0, QTableWidgetItem(i['name']))
                self.complete_md.tbl_attributes.setItem(
                    count, 1, QTableWidgetItem(i['dataType']))
                if 'description' in i:
                    self.complete_md.tbl_attributes.setItem(
                        count, 2, QTableWidgetItem(i['description']))
                count += 1
            self.complete_md.tbl_attributes.horizontalHeader(
            ).setStretchLastSection(True)
            self.complete_md.tbl_attributes.verticalHeader(
            ).setResizeMode(3)
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