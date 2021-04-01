# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
from datetime import datetime

# PyQGIS
from qgis.core import (
    QgsProject,
    QgsMessageLog,
    QgsVectorLayer,
    QgsPointXY,
    QgsRectangle,
    QgsFeature,
    QgsGeometry,
    QgsRasterLayer,
    QgsRenderContext,
)

# PyQT
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QTableWidgetItem

# 3rd party
from .isogeo_pysdk import IsogeoTranslator

# Plugin modules
from .tools import IsogeoPlgTools

# UI module
from ..ui.metadata.dlg_md_details import IsogeoMdDetails

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
logger = logging.getLogger("IsogeoQgisPlugin")

plg_tools = IsogeoPlgTools()

osm_lbls = (
    "contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers"
    "=Reference_Labels&styles=default&tileMatrixSet=250m&url=https://gibs.earthdata.nasa.gov/wmts"
    "/epsg4326/best/1.0.0/WMTSCapabilities.xml"
)
osm_refs = (
    "contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/png&layers"
    "=Reference_Features&styles=default&tileMatrixSet=250m&url=https://gibs.earthdata.nasa.gov/wm"
    "ts/epsg4326/best/1.0.0/WMTSCapabilities.xml"
)
blue_marble = (
    "contextualWMSLegend=0&crs=EPSG:4326&dpiMode=7&featureCount=10&format=image/jpeg&la"
    "yers=BlueMarble_ShadedRelief_Bathymetry&styles=default&tileMatrixSet=500m&url=https://gibs.e"
    "arthdata.nasa.gov/wmts/epsg4326/best/1.0.0/WMTSCapabilities.xml"
)

li_lyrs_refs = [
    QgsRasterLayer(osm_lbls, "Labels", "wms"),
    QgsRasterLayer(osm_refs, "Refs", "wms"),
    QgsRasterLayer(blue_marble, "Base", "wms"),
]

# ############################################################################
# ########## Classes ###############
# ##################################


class MetadataDisplayer:
    """Manage metadata displaying in QGIS UI."""

    url_edition = "https://app.isogeo.com"

    def __init__(self):
        """Class constructor."""
        self.complete_md = IsogeoMdDetails()
        self.complete_md.stackedWidget.setCurrentIndex(0)

        # some basic settings
        self.complete_md.wid_bbox.setCanvasColor(Qt.white)
        self.complete_md.wid_bbox.enableAntiAliasing(True)

        self.complete_md.btn_md_edit.pressed.connect(
            lambda: plg_tools.open_webpage(link=self.url_edition)
        )

        self.tr = object

    def show_complete_md(self, md: dict, tags: dict):
        """Open the pop up window that shows the metadata sheet details.

        :param md dict: Isogeo metadata dict
        """
        logger.info("Displaying the whole metadata sheet.")
        isogeo_tr = IsogeoTranslator(qsettings.value("locale/userLocale")[0:2])

        # clean map canvas
        vec_lyr = [i.id() for i in self.complete_md.wid_bbox.layers() if i.type() == 0]
        QgsProject.instance().removeMapLayers(vec_lyr)
        self.complete_md.wid_bbox.refresh()

        # -- GENERAL ---------------------------------------------------------
        if md.get("title"):
            self.complete_md.lbl_title.setText(md.get("title"))
        elif md.get("name"):
            self.complete_md.lbl_title.setText(md.get("name"))
        else:
            self.complete_md.lbl_title.setTextFormat(Qt.TextFormat(1))
            self.complete_md.lbl_title.setText(
                "<i>{}</i>".format(self.tr("Undefined", context=__class__.__name__))
            )

        self.complete_md.val_owner.setText(
            md.get("_creator").get("contact").get("name", "NR")
        )
        # Keywords
        kwords = tags.get("keywords", {"none": "NR"})
        self.complete_md.val_keywords.setText(" ; ".join(kwords.keys()))
        # INSPIRE themes and conformity
        themes = tags.get("inspire", {"none": "NR"})
        self.complete_md.val_inspire_themes.setText(" ; ".join(themes.keys()))
        if tags.get("compliance"):
            self.complete_md.ico_inspire_conformity.setEnabled(1)
            self.complete_md.ico_inspire_conformity.setToolTip(
                isogeo_tr.tr("quality", "isConform") + " INSPIRE"
            )
        else:
            self.complete_md.ico_inspire_conformity.setDisabled(1)
            self.complete_md.ico_inspire_conformity.setToolTip(
                isogeo_tr.tr("quality", "isNotConform") + " INSPIRE"
            )
        # Abstract
        self.complete_md.val_abstract.setText(md.get("abstract", "NR"))

        # -- FEATURE ATTRIBUTES ----------------------------------------------
        if md.get("type") == "vectorDataset":
            # display
            menu_list = self.complete_md.li_menu
            item = menu_list.item(1)
            item.setHidden(0)
            # fillfull
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
            tbl_attr.verticalHeader().setSectionResizeMode(3)
        else:
            menu_list = self.complete_md.li_menu
            item = menu_list.item(1)
            item.setHidden(1)
            pass

        # -- CONTACTS --------------------------------------------------------
        contacts = md.get("contacts", dict())
        contacts_pt_cct = []
        contacts_other_cct = []

        for ctact in sorted(contacts, key=lambda i: i.get("contact").get("name")):
            item = ctact.get("contact")

            if ctact.get("role", "NR") == "pointOfContact":
                content = "<b>{0}</b> ({1})<br><a href='mailto:{2}' target='_top'>{2}</a><br>{3}" "<br>{4} {5}<br>{6} {7}<br>{7}<br>{8}".format(
                    # isogeo_tr.tr("roles", ctact.get("role")),
                    item.get("name", "NR"),
                    item.get("organization", "NR"),
                    item.get("email", "NR"),
                    item.get("phone", "NR"),
                    item.get("addressLine1", ""),
                    item.get("addressLine2", ""),
                    item.get("zipCode", ""),
                    item.get("city", ""),
                    item.get("country", ""),
                )
                contacts_pt_cct.append(content)

            else:
                content = (
                    "<b>{0} - {1}</b> ({2})<br><a href='mailto:{3}' target='_blank'>{3}"
                    "</a><br>{4}<br>{5} {6}<br>{7} {8}<br>{9}".format(
                        isogeo_tr.tr("roles", ctact.get("role")),
                        item.get("name", "NR"),
                        item.get("organization", "NR"),
                        item.get("email", "NR"),
                        item.get("phone", ""),
                        item.get("addressLine1", ""),
                        item.get("addressLine2", ""),
                        item.get("zipCode", ""),
                        item.get("city", ""),
                        item.get("country", ""),
                    )
                )
                contacts_other_cct.append(content)

        # write
        self.complete_md.val_ct_pointof.setText("<br><hr><br>".join(contacts_pt_cct))
        self.complete_md.val_ct_other.setText("<br><hr><br>".join(contacts_other_cct))

        # -- HISTORY ---------------------------------------------------------
        # Data creation and last update dates
        self.complete_md.val_data_crea.setText(
            plg_tools.handle_date(md.get("created", "NR"))
        )
        self.complete_md.val_data_update.setText(
            plg_tools.handle_date(md.get("modified", "NR"))
        )
        # Update frequency information
        if md.get("updateFrequency", None):
            freq = md.get("updateFrequency")
            frequency_info = "{}{} {}".format(
                isogeo_tr.tr("frequencyTypes", "frequencyUpdateHelp"),
                "".join(i for i in freq if i.isdigit()),
                isogeo_tr.tr("frequencyShortTypes", freq[-1]),
            )
            self.complete_md.val_frequency.setText(frequency_info)
        else:
            self.complete_md.val_frequency.setText("NR")
        # Validity
        self.complete_md.val_valid_start.setText(
            plg_tools.handle_date(md.get("validFrom", "NR"))
        )
        self.complete_md.val_valid_end.setText(
            plg_tools.handle_date(md.get("validTo", "NR"))
        )
        self.complete_md.val_valid_comment.setText(md.get("validityComment", "NR"))
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
                tbl_events.setItem(
                    idx, 0, QTableWidgetItem(plg_tools.handle_date(e.get("date", "NR")))
                )
                tbl_events.setItem(idx, 1, QTableWidgetItem(e.get("description", "")))
                idx += 1
            else:
                pass

        # adapt size
        tbl_events.horizontalHeader().setStretchLastSection(True)
        tbl_events.verticalHeader().setSectionResizeMode(3)

        # -- TECHNICAL -------------------------------------------------------
        # SRS
        coord_sys = md.get("coordinate-system", {"None": "NR"})
        self.complete_md.val_srs.setText(
            "{} (EPSG:{})".format(
                coord_sys.get("name", "NR"), coord_sys.get("code", "NR")
            )
        )
        # Set the data format
        if tags.get("formats") != {}:
            self.complete_md.val_format.setText(list(tags.get("formats").keys())[0])
        else:
            self.complete_md.val_format.setText("NR")

        # feature info
        self.complete_md.val_feat_count.setText(str(md.get("features", "/")))
        self.complete_md.val_geometry.setText(md.get("geometry", ""))
        self.complete_md.val_resolution.setText(str(md.get("distance", "")) + " m")
        self.complete_md.val_scale.setText("1:" + str(md.get("scale", "")))

        # Quality
        self.complete_md.val_topology.setText(md.get("topologicalConsistency", ""))
        # Specifications
        specs_in = md.get("specifications", dict())
        specs_out = []
        for s_in in specs_in:
            # translate specification conformity
            if s_in.get("conformant"):
                s_conformity = isogeo_tr.tr("quality", "isConform")
            else:
                s_conformity = isogeo_tr.tr("quality", "isNotConform")
            # make data human readable
            if s_in.get("specification").get("published"):
                s_date = datetime.strptime(
                    s_in.get("specification").get("published"), "%Y-%m-%dT%H:%M:%S"
                )
                s_date = s_date.strftime("%Y-%m-%d")
            else:
                s_date = "<i>Date de publication non renseignée</i>"
            # prepare text
            spec_text = "<a href='{1}'><b>{0} ({2})</b></a>: {3}".format(
                s_in.get("specification").get("name", "NR"),
                s_in.get("specification").get("link", ""),
                s_date,
                s_conformity,
            )
            # store into the final list
            specs_out.append(spec_text)
        # write
        self.complete_md.val_specifications.setText("<br><hr><br>".join(specs_out))

        # Geography
        if "envelope" in md:
            qgs_prj = QgsProject.instance()
            # display
            self.complete_md.wid_bbox.setDisabled(0)
            # get convex hull coordinates and create the polygon
            md_lyr = self.envelope2layer(md.get("envelope"))
            # add layers
            qgs_prj.addMapLayers(
                [md_lyr, li_lyrs_refs[0], li_lyrs_refs[1], li_lyrs_refs[2]], 0
            )

            map_canvas_layer_list = [
                qgs_prj.mapLayer(md_lyr.id()),
                qgs_prj.mapLayer(li_lyrs_refs[0].id()),
                qgs_prj.mapLayer(li_lyrs_refs[1].id()),
                qgs_prj.mapLayer(li_lyrs_refs[2].id()),
            ]

            self.complete_md.wid_bbox.setLayers(map_canvas_layer_list)
            self.complete_md.wid_bbox.setExtent(md_lyr.extent())
            self.complete_md.wid_bbox.zoomOut()
        else:
            self.complete_md.grp_bbox.setDisabled(1)

        # -- CGUs ------------------------------------------------------------
        # Licences
        cgus_in = md.get("conditions", dict())
        cgus_out = []
        for c_in in cgus_in:
            if "license" in c_in:
                cgu_text = "<a href='{1}'><b>{0}</b></a><br>{2}<br>{3}".format(
                    c_in.get("license").get("name", "NR"),
                    c_in.get("license").get("link", ""),
                    c_in.get("description", ""),
                    c_in.get("license").get("content", ""),
                )
            else:
                cgu_text = "<b>{0}</b><br>{1}".format(
                    isogeo_tr.tr("conditions", "noLicense"), c_in.get("description", "")
                )

            # store into the final list
            cgus_out.append(cgu_text)

        # write
        self.complete_md.val_licenses.setText("<br><hr><br>".join(cgus_out))

        # Limitations
        lims_in = md.get("limitations", dict())
        lims_out = []
        for l_in in lims_in:
            lim_text = "<b>{0}</b><br>{1}".format(
                isogeo_tr.tr("limitations", l_in.get("type")),
                l_in.get("description", ""),
            )
            # legal type
            if l_in.get("type") == "legal":
                lim_text += "<br>" + isogeo_tr.tr(
                    "restrictions", l_in.get("restriction")
                )
            else:
                pass
            # INSPIRE precision
            if "directive" in l_in:
                lim_text += (
                    "<br><u>INSPIRE</u><br><ul><li>{}</li><li>{}</li></ul>".format(
                        l_in.get("directive").get("name"),
                        l_in.get("directive").get("description"),
                    )
                )
            else:
                pass

            # store into the final list
            lims_out.append(lim_text)

        # write
        self.complete_md.val_limitations.setText("<br><hr><br>".join(lims_out))

        # -- ADVANCED  TAB ---------------------------------------------------
        # Workgroup owner
        wg_id = md.get("_creator").get("_id")
        wg_contact = md.get("_creator").get("contact")
        self.complete_md.val_owner_name.setText(wg_contact.get("name", ""))
        self.complete_md.val_owner_email.setText(wg_contact.get("email", ""))
        self.complete_md.val_owner_phone.setText(wg_contact.get("phone", ""))
        self.complete_md.val_owner_address.setText(
            "{}<br>{}".format(
                wg_contact.get("addressLine1", "NR"), wg_contact.get("addressLine2", "")
            )
        )
        self.complete_md.val_owner_city.setText(wg_contact.get("zipCode", ""))
        self.complete_md.val_owner_country.setText(wg_contact.get("countryCode", ""))

        # Metadata
        self.complete_md.val_md_lang.setText(md.get("language", "NR"))
        self.complete_md.val_md_date_crea.setText(
            plg_tools.handle_date(md.get("_created")[:19])
        )
        self.complete_md.val_md_date_update.setText(
            plg_tools.handle_date(md.get("_modified")[:19])
        )

        # -- EDIT LINK -------------------------------------------------------
        self.url_edition = plg_tools.get_edit_url(
            md_id=md.get("_id"), md_type=md.get("type"), owner_id=wg_id
        )

        # only if user declared himself as Isogeo editor in authentication form
        self.complete_md.btn_md_edit.setEnabled(
            int(qsettings.value("isogeo/user/editor", 1))
        )

        # -- ADD OPTIONS ------------------------------------------------------
        self.complete_md.btn_addtomap.setHidden(1)
        self.complete_md.btn_xml_dl.setHidden(1)

        # -- DISPLAY ---------------------------------------------------------
        self.fields_displayer(md.get("type"), md.get("series"))
        # Finally open the damned window
        self.complete_md.show()
        try:
            QgsMessageLog.logMessage(
                message="Detailed metadata displayed: {}".format(
                    self.complete_md.lbl_title.text()
                ),
                tag="Isogeo",
                level=0,
            )
        except UnicodeEncodeError:
            QgsMessageLog.logMessage(
                message="Detailed metadata displayed: {}".format(
                    self.complete_md.lbl_title.text()
                ),
                tag="Isogeo",
                level=0,
            )

    def envelope2layer(self, envelope):
        """Transform metadata envelope into a QGIS layer."""
        # layer
        md_lyr = QgsVectorLayer("Polygon?crs=epsg:4326", "Metadata envelope", "memory")
        symbols = md_lyr.renderer().symbols(QgsRenderContext())
        symbol = symbols[0]
        symbol.setColor(QColor.fromRgb(255, 20, 147))
        symbol.setOpacity(0.25)

        if envelope.get("type") == "Polygon":
            # parse coordinates
            coords = envelope.get("coordinates")[0]
            poly_pts = [QgsPointXY(round(i[0], 3), round(i[1], 3)) for i in coords]
            # add geometry to layer
            poly = QgsFeature()
            poly.setGeometry(QgsGeometry.fromPolygonXY([poly_pts]))
            md_lyr.dataProvider().addFeatures([poly])
            md_lyr.updateExtents()
        elif envelope.get("type") == "MultiPolygon":
            coords = envelope.get("bbox")
            bbox = QgsRectangle(
                round(coords[0], 3),
                round(coords[1], 3),
                round(coords[2], 3),
                round(coords[3], 3),
            )
            poly = QgsFeature()
            poly.setGeometry(QgsGeometry.fromWkt(bbox.asWktPolygon()))
            md_lyr.dataProvider().addFeatures([poly])
            md_lyr.updateExtents()
        elif envelope.get("type") == "Point":
            return md_lyr
        else:
            pass
        # method ending
        return md_lyr

    def fields_displayer(self, md_type="vectorDataset", series=0):
        """Adapt display according to metadata type."""
        menu_list = self.complete_md.li_menu
        if md_type == "vectorDataset":
            # general
            self.complete_md.val_inspire_themes.setHidden(0)
            self.complete_md.ico_inspire_themes.setHidden(0)
            self.complete_md.ico_inspire_conformity.setHidden(0)
            self.complete_md.val_feat_count.setHidden(0)
            self.complete_md.val_geometry.setHidden(0)
            # history
            self.complete_md.lbl_frequency.setHidden(0)
            self.complete_md.ico_frequency.setHidden(0)
            self.complete_md.val_frequency.setHidden(0)
            self.complete_md.lbl_valid_start.setHidden(0)
            self.complete_md.ico_valid_start.setHidden(0)
            self.complete_md.val_valid_start.setHidden(0)
            self.complete_md.lbl_valid_end.setHidden(0)
            self.complete_md.ico_valid_end.setHidden(0)
            self.complete_md.val_valid_end.setHidden(0)
            self.complete_md.lbl_valid_comment.setHidden(0)
            self.complete_md.ico_valid_comment.setHidden(0)
            self.complete_md.val_valid_comment.setHidden(0)
            self.complete_md.grp_collect_context.setHidden(0)
            self.complete_md.grp_collect_method.setHidden(0)
            # geography
            self.complete_md.grp_technic.setHidden(0)
            self.complete_md.ico_feat_count.setHidden(0)
            self.complete_md.lbl_feat_count.setHidden(0)
            self.complete_md.val_feat_count.setHidden(0)
            self.complete_md.ico_geometry.setHidden(0)
            self.complete_md.lbl_geometry.setHidden(0)
            self.complete_md.val_geometry.setHidden(0)
            # menus
            menu_list.item(1).setHidden(0)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            return

        elif md_type == "rasterDataset" and not series:
            # geography
            self.complete_md.val_feat_count.setHidden(1)
            self.complete_md.val_geometry.setHidden(1)
            # geography
            self.complete_md.grp_technic.setHidden(0)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            return

        elif md_type == "rasterDataset" and series:
            # geography
            self.complete_md.ico_feat_count.setHidden(1)
            self.complete_md.lbl_feat_count.setHidden(1)
            self.complete_md.val_feat_count.setHidden(1)
            self.complete_md.ico_geometry.setHidden(1)
            self.complete_md.lbl_geometry.setHidden(1)
            self.complete_md.val_geometry.setHidden(1)
            # geography
            self.complete_md.grp_technic.setHidden(0)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            return

        elif md_type == "service":
            # general
            self.complete_md.val_inspire_themes.setHidden(1)
            self.complete_md.ico_inspire_themes.setHidden(1)
            self.complete_md.ico_inspire_conformity.setHidden(1)
            # history
            self.complete_md.lbl_frequency.setHidden(1)
            self.complete_md.ico_frequency.setHidden(1)
            self.complete_md.val_frequency.setHidden(1)
            self.complete_md.lbl_valid_start.setHidden(1)
            self.complete_md.ico_valid_start.setHidden(1)
            self.complete_md.val_valid_start.setHidden(1)
            self.complete_md.lbl_valid_end.setHidden(1)
            self.complete_md.ico_valid_end.setHidden(1)
            self.complete_md.val_valid_end.setHidden(1)
            self.complete_md.lbl_valid_comment.setHidden(1)
            self.complete_md.ico_valid_comment.setHidden(1)
            self.complete_md.val_valid_comment.setHidden(1)
            self.complete_md.grp_collect_context.setHidden(1)
            self.complete_md.grp_collect_method.setHidden(1)
            # geography
            self.complete_md.grp_technic.setHidden(0)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            return

        elif md_type == "resource":
            # history
            self.complete_md.lbl_frequency.setHidden(1)
            self.complete_md.ico_frequency.setHidden(1)
            self.complete_md.val_frequency.setHidden(1)
            self.complete_md.lbl_valid_start.setHidden(1)
            self.complete_md.ico_valid_start.setHidden(1)
            self.complete_md.val_valid_start.setHidden(1)
            self.complete_md.lbl_valid_end.setHidden(1)
            self.complete_md.ico_valid_end.setHidden(1)
            self.complete_md.val_valid_end.setHidden(1)
            self.complete_md.lbl_valid_comment.setHidden(1)
            self.complete_md.ico_valid_comment.setHidden(1)
            self.complete_md.val_valid_comment.setHidden(1)
            self.complete_md.grp_collect_context.setHidden(1)
            self.complete_md.grp_collect_method.setHidden(1)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(1)  # geography and technical
            return

        else:
            # should not exist
            logger.error("Metadata type not recognized:", md_type)
            return


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
