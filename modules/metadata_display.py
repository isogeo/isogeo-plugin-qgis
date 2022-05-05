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
    QgsFeature,
    QgsGeometry,
    QgsRasterLayer,
    QgsRenderContext,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)

# PyQT
from qgis.PyQt.QtCore import QSettings, Qt
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QTableWidgetItem, QLabel
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

osm_standard = r"type=xyz&format=image/png&styles=default&tileMatrixSet=250m&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png"

ref_lyr = QgsRasterLayer(osm_standard, "OSM_Standard", "wms")

# ############################################################################
# ########## Classes ###############
# ##################################


class MetadataDisplayer:
    """Manage metadata displaying in QGIS UI."""

    md_edition_url = str

    def __init__(self, app_base_url: str):
        """Class constructor."""
        self.complete_md = IsogeoMdDetails()
        self.complete_md.stackedWidget.setCurrentIndex(0)

        # some basic settings
        self.app_base_url = app_base_url
        self.complete_md.btn_md_edit.pressed.connect(
            lambda: plg_tools.open_webpage(link=self.md_edition_url)
        )

        self.complete_md.wid_bbox.setCanvasColor(Qt.white)
        self.complete_md.wid_bbox.enableAntiAliasing(True)

        self.tr = object

    def show_complete_md(self, md: dict, tags: dict):
        """Open the pop up window that shows the metadata sheet details.

        :param md dict: Isogeo metadata dict
        """
        logger.info("Displaying the whole metadata sheet.")
        try:
            locale = str(qsettings.value("locale/userLocale", "fr", type=str))[0:2]
        except TypeError as e:
            logger.error(
                "Bad type in QSettings: {}. Original error: {}".format(
                    type(qsettings.value("locale/userLocale")), e
                )
            )
            locale = "fr"
        isogeo_tr = IsogeoTranslator(locale)

        # clean map canvas
        vec_lyr = [i.id() for i in self.complete_md.wid_bbox.layers() if i.type() == 0]
        QgsProject.instance().removeMapLayers(vec_lyr)
        self.complete_md.wid_bbox.refresh()

        # -- GENERAL ---------------------------------------------------------
        if md.get("title"):
            if md.get("name"):
                self.complete_md.lbl_title.setText("<strong>{}</strong> ({})".format(md.get("title"), md.get("name")))
            else:
                self.complete_md.lbl_title.setText("<strong>{}</strong>".format(md.get("title")))
        elif md.get("name"):
            self.complete_md.lbl_title.setText("<strong>{}</strong>".format(md.get("name")))
        else:
            self.complete_md.lbl_title.setTextFormat(Qt.TextFormat(1))
            self.complete_md.lbl_title.setText(
                "<strong><i>{}</i></strong>".format(self.tr("Undefined", context=__class__.__name__))
            )

        plg_tools.format_widget_title(self.complete_md.lbl_title, self.complete_md.lbl_title.width())

        self.complete_md.val_owner.setText(
            md.get("_creator").get("contact").get("name", "NR")
        )
        # Keywords
        kwords = tags.get("keywords", {"none": "NR"})
        self.complete_md.val_keywords.setText(" ; ".join(kwords.keys()))
        # Group themes
        themes = tags.get("groupTheme", {"none": "NR"})
        self.complete_md.val_group_themes.setText(" ; ".join(themes.keys()))
        # INSPIRE themes
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
        if md.get("type") in ("vectorDataset", "noGeoDataset"):
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
                alias_text = i.get("alias", "")
                if i.get("comment", "") != "" and alias_text == "":
                    alias_text += "<i>{}</i>".format(i.get("comment", ""))
                elif i.get("comment", "") != "":
                    alias_text += "<br><i>{}</i>".format(i.get("comment", ""))
                else:
                    pass
                alias_label = QLabel(alias_text)
                alias_label.setWordWrap(True)

                tbl_attr.setItem(idx, 0, QTableWidgetItem(i.get("name", "")))
                tbl_attr.setCellWidget(idx, 1, alias_label)
                tbl_attr.setItem(idx, 2, QTableWidgetItem(i.get("dataType", "")))
                tbl_attr.setItem(idx, 3, QTableWidgetItem(i.get("description", "")))
                idx += 1

            # adapt size
            tbl_attr.horizontalHeader().setStretchLastSection(True)
            tbl_attr.verticalHeader().setSectionResizeMode(3)

            # adapt alias column labels width to column width
            alias_column_width = tbl_attr.horizontalHeader().sectionSize(1)
            for i in range(idx):
                tbl_attr.cellWidget(i, 1).setMaximumWidth(alias_column_width)

            tbl_attr.horizontalHeader().sectionResized.connect(self.resize_alias_labels)

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
            if item.get("organization", "NR") == "NR":
                ctct_label = "{}</b>".format(item.get("name", "NR"))
            else:
                ctct_label = "{}</b> ({})".format(item.get("name", "NR"), item.get("organization"))

            if ctact.get("role", "NR") == "pointOfContact":
                content = "<b>{0}<br><a href='mailto:{1}' target='_top'>{1}</a><br>{2}" "<br>{3} {4}<br>{5} {6}<br>{6}<br>{7}".format(
                    ctct_label,
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
                    "<b>{0} - {1}<br><a href='mailto:{2}' target='_blank'>{2}"
                    "</a><br>{3}<br>{4} {5}<br>{6} {7}<br>{8}".format(
                        isogeo_tr.tr("roles", ctact.get("role")),
                        ctct_label,
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
        events = [ev for ev in md.get("events", []) if ev.get("kind") == "update"]
        tbl_events = self.complete_md.tbl_events
        tbl_events.clearContents()
        tbl_events.setRowCount(len(events))
        idx = 0
        for event in events:
            tbl_events.setItem(
                idx, 0, QTableWidgetItem(plg_tools.handle_date(event.get("date", "NR")))
            )
            tbl_events.setItem(idx, 1, QTableWidgetItem(event.get("description", "")))
            idx += 1

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
            if locale == "fr":
                spec_text = "<a href='{1}'><b>{0} ({2})</b></a> : {3}".format(
                    s_in.get("specification").get("name", "NR"),
                    s_in.get("specification").get("link", ""),
                    s_date,
                    s_conformity,
                )
            else:
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
        if "envelope" in md and isinstance(md.get("envelope"), dict):
            qgs_prj = QgsProject.instance()
            # display
            self.complete_md.grp_bbox.setDisabled(0)
            # get convex hull coordinates and create the polygon
            md_lyr = self.envelope2layer(md.get("envelope"))
            li_lyr = [md_lyr, ref_lyr]
            # add layers
            qgs_prj.addMapLayers(li_lyr, 0)
            map_canvas_layer_list = [
                qgs_prj.mapLayer(md_lyr.id()),
                qgs_prj.mapLayer(ref_lyr.id()),
            ]

            self.complete_md.wid_bbox.setLayers(map_canvas_layer_list)
            self.complete_md.wid_bbox.setExtent(md_lyr.extent())
            self.complete_md.wid_bbox.zoomOut()
            self.complete_md.wid_bbox.setDisabled(1)
        else:
            self.complete_md.grp_bbox.setDisabled(1)

        if md.get("type") == "noGeoDataset":
            self.complete_md.val_geoContext.setText(md.get("geoContext"))
        else:
            pass

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
        # only if user declared himself as Isogeo editor in authentication form
        self.md_edition_url = "{}/groups/{}/resources/{}/identification".format(self.app_base_url, wg_id, md.get("_id"))

        self.complete_md.btn_md_edit.setEnabled(
            int(qsettings.value("isogeo/user/editor", 1))
        )

        # -- ADD OPTIONS ------------------------------------------------------
        self.complete_md.btn_addtomap.setHidden(1)
        self.complete_md.btn_xml_dl.setHidden(1)

        # -- DISPLAY ---------------------------------------------------------
        self.fields_displayer(md.get("type"), md.get("series"))
        # Finally open the damned window
        self.complete_md.li_menu.setCurrentRow(0)
        self.complete_md.stackedWidget.setCurrentIndex(0)
        self.complete_md.stackedWidget.setCurrentWidget(self.complete_md.stackedWidget.widget(0))
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
        # prepare geom feature
        feature = QgsFeature()
        # prepare coordinates transformation to match OSM WMTS srs
        mercator = QgsCoordinateReferenceSystem(
            4326, QgsCoordinateReferenceSystem.EpsgCrsId
        )
        pseudo_mercator = QgsCoordinateReferenceSystem(
            3857, QgsCoordinateReferenceSystem.EpsgCrsId
        )
        coord_transformer = QgsCoordinateTransform(
            mercator, pseudo_mercator, QgsProject.instance()
        )

        if envelope.get("type") == "Polygon":
            md_lyr = QgsVectorLayer(
                "Polygon?crs=epsg:3857", "Metadata envelope", "memory"
            )
            coords = envelope.get("coordinates")[0]
            poly_pts = [
                coord_transformer.transform(QgsPointXY(round(i[0], 3), round(i[1], 3)))
                for i in coords
            ]
            feature.setGeometry(QgsGeometry.fromPolygonXY([poly_pts]))
        elif envelope.get("type") == "MultiPolygon":
            md_lyr = QgsVectorLayer(
                "Polygon?crs=epsg:3857", "Metadata envelope", "memory"
            )
            coords = envelope.get("bbox")
            poly_pts = [
                coord_transformer.transform(QgsPointXY(round(i[0], 3), round(i[1], 3)))
                for i in coords
            ]
            feature.setGeometry(QgsGeometry.fromPolygonXY([poly_pts]))
        elif envelope.get("type") == "Point":
            md_lyr = QgsVectorLayer(
                "Point?crs=epsg:3857", "Metadata envelope", "memory"
            )
            coords = envelope.get("coordinates")
            point = QgsPointXY(round(coords[0], 3), round(coords[1], 3))
            feature.setGeometry(QgsGeometry.fromPointXY(point))
        else:
            md_lyr = QgsVectorLayer(
                "Polygon?crs=epsg:3857", "Metadata envelope", "memory"
            )
            return md_lyr

        # Design the feature
        symbols = md_lyr.renderer().symbols(QgsRenderContext())
        symbol = symbols[0]
        symbol.setColor(QColor.fromRgb(255, 20, 147))
        symbol.setOpacity(0.25)

        # add the feature to the layer
        md_lyr.dataProvider().addFeatures([feature])
        md_lyr.updateExtents()
        # method ending
        return md_lyr

    def fields_displayer(self, md_type="vectorDataset", series=0):
        """Adapt display according to metadata type."""
        menu_list = self.complete_md.li_menu
        if md_type == "vectorDataset":
            # general
            self.complete_md.val_group_themes.setHidden(0)
            self.complete_md.ico_group_themes.setHidden(0)
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
            self.complete_md.grp_geoContext.setHidden(1)
            self.complete_md.grp_technic.setHidden(0)
            self.complete_md.ico_feat_count.setHidden(0)
            self.complete_md.lbl_feat_count.setHidden(0)
            self.complete_md.val_feat_count.setHidden(0)
            self.complete_md.ico_geometry.setHidden(0)
            self.complete_md.lbl_geometry.setHidden(0)
            self.complete_md.val_geometry.setHidden(0)
            self.complete_md.ico_srs.setHidden(0)
            self.complete_md.lbl_srs.setHidden(0)
            self.complete_md.val_srs.setHidden(0)
            self.complete_md.ico_scale.setHidden(0)
            self.complete_md.lbl_scale.setHidden(0)
            self.complete_md.val_scale.setHidden(0)
            self.complete_md.ico_resolution.setHidden(0)
            self.complete_md.lbl_resolution.setHidden(0)
            self.complete_md.val_resolution.setHidden(0)
            self.complete_md.line.setHidden(0)
            self.complete_md.grp_bbox.setHidden(0)
            # quality
            self.complete_md.grp_topoConsist.setHidden(0)
            # menus
            menu_list.item(1).setHidden(0)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            menu_list.item(5).setHidden(0)  # quality
            return

        elif md_type == "noGeoDataset":
            # general
            self.complete_md.val_group_themes.setHidden(0)
            self.complete_md.ico_group_themes.setHidden(0)
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
            self.complete_md.grp_geoContext.setHidden(0)
            self.complete_md.grp_technic.setHidden(0)
            self.complete_md.ico_feat_count.setHidden(0)
            self.complete_md.lbl_feat_count.setHidden(0)
            self.complete_md.val_feat_count.setHidden(0)
            self.complete_md.ico_geometry.setHidden(1)
            self.complete_md.lbl_geometry.setHidden(1)
            self.complete_md.val_geometry.setHidden(1)
            self.complete_md.ico_srs.setHidden(1)
            self.complete_md.lbl_srs.setHidden(1)
            self.complete_md.val_srs.setHidden(1)
            self.complete_md.ico_scale.setHidden(1)
            self.complete_md.lbl_scale.setHidden(1)
            self.complete_md.val_scale.setHidden(1)
            self.complete_md.ico_resolution.setHidden(1)
            self.complete_md.lbl_resolution.setHidden(1)
            self.complete_md.val_resolution.setHidden(1)
            self.complete_md.line.setHidden(1)
            self.complete_md.grp_bbox.setHidden(1)
            # quality
            self.complete_md.grp_topoConsist.setHidden(1)
            # menus
            menu_list.item(1).setHidden(0)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            menu_list.item(5).setHidden(0)  # quality
            return

        elif md_type == "rasterDataset" and not series:
            # geography
            self.complete_md.val_feat_count.setHidden(1)
            self.complete_md.val_geometry.setHidden(1)
            self.complete_md.grp_geoContext.setHidden(1)
            # geography
            self.complete_md.grp_technic.setHidden(0)
            # geography
            self.complete_md.ico_feat_count.setHidden(1)
            self.complete_md.lbl_feat_count.setHidden(1)
            self.complete_md.val_feat_count.setHidden(1)
            self.complete_md.ico_geometry.setHidden(1)
            self.complete_md.lbl_geometry.setHidden(1)
            self.complete_md.val_geometry.setHidden(1)
            self.complete_md.ico_srs.setHidden(0)
            self.complete_md.lbl_srs.setHidden(0)
            self.complete_md.val_srs.setHidden(0)
            self.complete_md.ico_scale.setHidden(0)
            self.complete_md.lbl_scale.setHidden(0)
            self.complete_md.val_scale.setHidden(0)
            self.complete_md.ico_resolution.setHidden(0)
            self.complete_md.lbl_resolution.setHidden(0)
            self.complete_md.val_resolution.setHidden(0)
            self.complete_md.line.setHidden(0)
            self.complete_md.grp_bbox.setHidden(0)
            # quality
            self.complete_md.grp_topoConsist.setHidden(1)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            menu_list.item(5).setHidden(0)  # quality
            return

        elif md_type == "rasterDataset" and series:
            # geography
            self.complete_md.ico_feat_count.setHidden(1)
            self.complete_md.lbl_feat_count.setHidden(1)
            self.complete_md.val_feat_count.setHidden(1)
            self.complete_md.ico_geometry.setHidden(1)
            self.complete_md.lbl_geometry.setHidden(1)
            self.complete_md.val_geometry.setHidden(1)
            self.complete_md.ico_srs.setHidden(0)
            self.complete_md.lbl_srs.setHidden(0)
            self.complete_md.val_srs.setHidden(0)
            self.complete_md.ico_scale.setHidden(0)
            self.complete_md.lbl_scale.setHidden(0)
            self.complete_md.val_scale.setHidden(0)
            self.complete_md.ico_resolution.setHidden(0)
            self.complete_md.lbl_resolution.setHidden(0)
            self.complete_md.val_resolution.setHidden(0)
            self.complete_md.line.setHidden(0)
            self.complete_md.grp_bbox.setHidden(0)
            self.complete_md.grp_geoContext.setHidden(1)
            # geography
            self.complete_md.grp_technic.setHidden(0)
            # quality
            self.complete_md.grp_topoConsist.setHidden(1)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            menu_list.item(5).setHidden(0)  # quality
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
            self.complete_md.grp_geoContext.setHidden(1)
            # quality
            self.complete_md.grp_topoConsist.setHidden(1)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(0)  # geography and technical
            menu_list.item(5).setHidden(0)  # quality
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
            self.complete_md.grp_geoContext.setHidden(1)
            # quality
            self.complete_md.grp_topoConsist.setHidden(1)
            # menus
            menu_list.item(1).setHidden(1)  # attributes
            menu_list.item(4).setHidden(1)  # geography and technical
            menu_list.item(5).setHidden(1)  # quality
            return

        else:
            # should not exist
            logger.error("Metadata type not recognized:", md_type)
            return

    def resize_alias_labels(self, column_index, old_width, new_width):
        """Slot to self.complete_md.tbl_attributes.horizontalHeader().sectionResized signal. Resize
        alias labels to fit column width

        :param int column_index: index of the column
        :param int old_width: old width of the column
        :param int new_width: new width of the column
        """
        if column_index == 1:
            for i in range(self.complete_md.tbl_attributes.rowCount()):
                self.complete_md.tbl_attributes.cellWidget(i, 1).setMaximumWidth(new_width)
        else:
            pass


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
