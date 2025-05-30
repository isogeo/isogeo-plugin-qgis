# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import re
import json
from xml.etree import ElementTree
from urllib.parse import urlencode, unquote, quote

# PyQGIS
from qgis.core import (
    QgsDataSourceUri,
    QgsCoordinateTransform,
    QgsProject,
    QgsCoordinateReferenceSystem,
    QgsRectangle,
    QgsNetworkAccessManager  # https://github.com/isogeo/isogeo-plugin-qgis/issues/467
)
from qgis.utils import iface

# PyQT
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest

# Plugin modules
from ..tools import IsogeoPlgTools
from ..settings_manager import SettingsManager

# ############################################################################
# ########## Globals ###############
# ##################################

settings_mng = SettingsManager()
logger = logging.getLogger("IsogeoQgisPlugin")
plg_tools = IsogeoPlgTools()

qgis_wms_formats = (
    "image/png",
    "image/png8",
    "image/jpeg",
    "image/svg",
    "image/gif",
    "image/geotiff",
    "image/tiff",
)

# ############################################################################
# ##### Conditional imports ########
# ##################################

try:
    from owslib.wms import WebMapService
    from owslib.wmts import WebMapTileService
    from owslib.util import ServiceException
    import owslib

    logging.info("Dependencies - owslib version: {}".format(owslib.__version__))
except ImportError:
    logger.warning("Dependencies - owslib is not present")

try:
    from owslib.wfs import WebFeatureService
except ImportError as e:
    logger.warning("Dependencies - owslib WFS issue: {}".format(e))

try:
    from owslib.util import HTTPError

    logger.info("Dependencies - HTTPError within owslib")
except ImportError:
    from urllib.error import HTTPError

    logger.warning(
        "Dependencies - HTTPError not within owslib." " Directly imported from urllib.error"
    )

try:
    from owslib.util import Authentication

    logger.info("Dependencies - Authentication within owslib")
except ImportError:
    logger.warning("Dependencies - Authentication not within owslib.")

try:
    import requests

    logger.info("Dependencies - Requests version: {}".format(requests.__version__))
except ImportError:
    logger.warning("Dependencies - Requests not available")

# ############################################################################
# ########## Classes ###############
# ##################################


class GeoServiceManager:
    """Basic class that holds methods used to facilitate geographic services handling
    for layer adding."""

    # def __init__(self, cache_manager: object):
    def __init__(self):
        """Class constructor."""

        # specific infos related to OGC service type
        self.ogc_infos_dict = {
            "WFS": ["GetFeature", WebFeatureService],
            "WMS": ["GetMap", WebMapService],
            "WMTS": ["GetTile", WebMapTileService],
        }
        # specific infos related to ESRI service type
        self.esri_infos_dict = {"EFS": "latestWkid", "EMS": "wkid"}

        # set local cache dict
        self.service_cached_dict = {
            "WFS": dict(),
            "WMS": dict(),
            "WMTS": dict(),
            "EFS": dict(),
            "EMS": dict(),
        }

        settings_mng.load_afs_connections()

    def find_wfs_layer(self, api_layer_id: str, typenames: list, wfs_url_base: str):

        layer_typename = None

        raw_id = api_layer_id
        cleaned_id = re.sub("\{.*?}", "", raw_id)
        slugified_id = plg_tools.slugify_layer_id(raw_id)
        need_rebuild = re.findall("\{https{0,1}:\/\/(.*?)\}", raw_id)
        rebuild_id = f"{need_rebuild[0]}:{cleaned_id}" if len(need_rebuild) else None
        candidates = [raw_id, cleaned_id, slugified_id, rebuild_id] if rebuild_id else [raw_id, cleaned_id, slugified_id]

        if any(string in typenames for string in candidates):
            potential_typenames = [string for string in candidates if string in typenames]
            layer_typename = potential_typenames[0]
        else:
            for string in candidates:
                diptych_typenames = [tn for tn in typenames if len(tn.split(":")) == 2]

                li_potential_typenames = [
                    [tn for tn in typenames if string == tn.upper()],
                    [tn for tn in diptych_typenames if string == tn.split(":")[1]],
                    [tn for tn in diptych_typenames if string in tn.split(":")[1]],
                    [tn for tn in typenames if string in tn]
                ]
                for potential_typenames in li_potential_typenames:
                    if len(potential_typenames):
                        layer_typename = potential_typenames[0]
                        if len(potential_typenames) > 1:
                            logger.warning(
                                f"WFS {wfs_url_base} - Multiple typenames matched for '{string}' layer, '{layer_typename}' picked."
                            )
                        break
                if layer_typename:
                    break
        return layer_typename

    def choose_appropriate_srs(self, crs_options: list):
        """Return an appropriate srs depending on QGIS configuration and available
        service layer crs options.

        :param list crs_options: service layer available crs options (for example : ["EPSG:2154", "WGS84:4326"])
        """
        if len(crs_options):
            # SRS definition
            srs_map = plg_tools.get_map_crs()
            # srs_lyr_new = settings_mng.get_value("projections/defaultBehaviour", None)
            srs_lyr_crs = settings_mng.get_value("projections/layerDefaultCrs", None)
            srs_qgs_new = settings_mng.get_value("app/projections/defaultProjectCrs", None)
            # srs_qgs_otf_on = settings_mng.get_value("app/projections/otfTransformEnabled", "false")
            # srs_qgs_otf_auto = settings_mng.get_value("app/projections/otfTransformAutoEnable", "false")

            if srs_map in crs_options:
                logger.debug("It's a SRS match! With map canvas: " + srs_map)
                srs = srs_map
            elif srs_qgs_new is not None and srs_qgs_new in crs_options:
                logger.debug("It's a SRS match! With default new project: " + srs_qgs_new)
                srs = srs_qgs_new
            elif srs_lyr_crs is not None and srs_lyr_crs in crs_options:
                logger.debug("It's a SRS match! With default new layer: " + srs_lyr_crs)
                srs = srs_lyr_crs
            elif "EPSG:4326" in crs_options:
                logger.debug("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                srs = "EPSG:4326"
            else:
                logger.debug(
                    "Map Canvas SRS not available within service CRS. One of the following ones gonna be chosen : {}".format(
                        crs_options
                    )
                )
                li_srs_candidates = [
                    crs_option for crs_option in crs_options if "EPSG" in crs_option
                ]
                if len(li_srs_candidates):
                    srs = li_srs_candidates[0]
                else:
                    srs = crs_options[0]
        else:
            srs = "EPSG:4326"
        return srs

    def build_layer_title(self, service_type: str, api_layer: dict):
        """Build the title of the layer according to informations provided by Isogeo API
        and specific service type.

        :param str service_type: type of OGC or ESRI service ("WFS", "WMS", "WMTS", "EFS" or "EMS")
        :param dict api_layer: dict object containing Isogeo API informations about the layer

        """
        # If service_type argument value is invalid, raise error
        accepted_values = list(self.service_cached_dict.keys())
        if service_type not in accepted_values:
            error_msg = "'service_type' argument value should be one of {} not {}".format(
                accepted_values, service_type
            )
            raise ValueError(error_msg)
            # If it's valid, let's build this layer title
        else:
            if service_type in self.esri_infos_dict:
                generic_title = "{} layer ({})".format(service_type, api_layer.get("id"))
                if api_layer.get("title", None) is not None:
                    layer_title = api_layer.get("title")
                else:
                    layer_title = generic_title
            else:
                if service_type == "WFS":
                    api_layer_id = re.sub("\{.*?}", "", api_layer.get("id"))
                else:
                    api_layer_id = api_layer.get("id")
                generic_title = api_layer_id
                if api_layer.get("title", None) is not None:
                    layer_title = api_layer.get("title")
                else:
                    layer_title = generic_title

            return layer_title

    # For now, only working for a specific business geographic WFS (https://github.com/isogeo/isogeo-plugin-qgis/issues/359)
    def parse_ogc_xml(self, service_type, service_dict: dict):
        """Called if owslib modules can't be used to parse the xml return by GetCapabilities request.

        :param str service_type: type of OGC service ("WFS", "WMS", or "WMTS")
        :param dict service_dict: the dict to fill with infos retrieved from XML content
        """
        # If service_type argument value is invalid, raise error
        if service_type not in self.ogc_infos_dict:
            raise ValueError(
                "'service_type' argument value should be one of {} not {}".format(
                    list(self.ogc_infos_dict.keys()), service_type
                )
            )
        # It it's valid, set local variables depending on it
        else:
            # First, specify that the dict gonna fill by the risky way
            service_dict["manual"] = 1

            # Then, launch the GetCapabilities request
            url = service_dict.get("getCap_url")
            r = requests.get(url=url, verify=False)

        # Finally, parse XML content returned
        if r.status_code == 200:
            service_dict["reachable"] = 1
            xml_root = ElementTree.fromstring(r.text)
            tag_prefix = xml_root.tag.split("}")[0] + "}"

            # retrieve basic infos
            service_dict["version"] = xml_root.get("version")
            main_op_name = self.ogc_infos_dict.get(service_type)[0]

            if service_type == "WFS":
                # check if get data operation is available + retrieve formatOptions
                if any("OperationsMetadata" in child.tag for child in xml_root):
                    xml_operationsMetadata = [child for child in xml_root if "OperationsMetadata" in child.tag][0]
                    if any(main_op_name in ope.get("name") for ope in xml_operationsMetadata):
                        service_dict["{}_isAvailable".format(main_op_name)] = 1
                        main_op_elem = [ope for ope in xml_operationsMetadata if main_op_name in ope.get("name")]
                        if len(main_op_elem) == 1:
                            service_dict["formatOptions"] = [
                                subelem.text for subelem in main_op_elem[0] if subelem.tag.endswith("Format")
                            ]
                    else:
                        service_dict["{}_isAvailable".format(main_op_name)] = 0
                elif any("Capability" in child.tag for child in xml_root):
                    xml_Capability = [child for child in xml_root if "Capability" in child.tag][0]
                    if any("Request" in child.tag for child in xml_Capability):
                        xml_Request = [child for child in xml_Capability if "Request" in child.tag][0]
                        if any(main_op_name in child.tag for child in xml_Request):
                            service_dict["{}_isAvailable".format(main_op_name)] = 1
                        else:
                            service_dict["{}_isAvailable".format(main_op_name)] = 0
                    else:
                        service_dict["{}_isAvailable".format(main_op_name)] = 0
                else:
                    service_dict["{}_isAvailable".format(main_op_name)] = 0

                # retrieving layers typenames and building layers list (crs, typename)
                xml_featureTypelist = xml_root.find(tag_prefix + "FeatureTypeList")
                li_typenames = []
                li_layers = []
                for featureType in xml_featureTypelist.findall(tag_prefix + "FeatureType"):
                    layer_dict = {}
                    # typename
                    featureType_name = featureType.find(tag_prefix + "Name")
                    if featureType_name is None:
                        continue
                    else:
                        layer_dict["typename"] = featureType_name.text
                        li_typenames.append(featureType_name.text)

                    # Default CRS
                    featureType_DefaultSRS = featureType.find(tag_prefix + "DefaultSRS")
                    featureType_DefaultCRS = featureType.find(tag_prefix + "DefaultCRS")
                    featureType_SRS = featureType.find(tag_prefix + "SRS")
                    if featureType_DefaultSRS is not None:
                        layer_dict["srs_id"] = featureType_DefaultSRS.text
                        layer_dict["EPSG"] = featureType_DefaultSRS.text.split(":")[-1]
                    elif featureType_DefaultCRS is not None:
                        layer_dict["srs_id"] = featureType_DefaultCRS.text
                        layer_dict["EPSG"] = featureType_DefaultCRS.text.split(":")[-1]
                    elif featureType_SRS is not None:
                        layer_dict["srs_id"] = featureType_SRS.text
                        layer_dict["EPSG"] = featureType_SRS.text.split(":")[-1]
                    else:
                        layer_dict["EPSG"] = ""

                    li_layers.append(layer_dict)

            elif service_type == "WMS":
                xml_cap = [child for child in xml_root if "Capability" in child.tag][0]

                # check if get data operation is available + retrieve formatOptions
                xml_request = [child for child in xml_cap if "Request" in child.tag][0]
                main_op_elem = [child for child in xml_request.findall(tag_prefix + main_op_name)]
                if len(main_op_elem) == 1:
                    service_dict["{}_isAvailable".format(main_op_name)] = 1
                    li_formatOptions = [
                        child.text for child in main_op_elem[0].findall(tag_prefix + "Format")
                    ]
                    service_dict["formatOptions"] = li_formatOptions
                elif len(main_op_elem) == 0:
                    service_dict["{}_isAvailable".format(main_op_name)] = 0
                else:
                    service_dict["{}_isAvailable".format(main_op_name)] = 1

                # retrieving CRS options common to all layers
                li_common_crs = [child.text for child in xml_cap.iter(tag_prefix + "CRS")]

                # retrieving layers typenames and building layers list (bbox, crs, typename)
                li_typenames = []
                li_layers = []
                for layer in xml_cap.find(tag_prefix + "Layer").findall(tag_prefix + "Layer"):
                    layer_dict = {}
                    # typename
                    li_layer_typenames = [
                        child.text for child in layer.findall(tag_prefix + "Name")
                    ]
                    if not len(li_layer_typenames):
                        continue
                    else:
                        li_typenames.append(li_layer_typenames[0])
                        layer_dict["typename"] = li_layer_typenames[0]

                    # CRS options
                    li_layer_crs = [child.text for child in layer.findall(tag_prefix + "CRS")]
                    if not len(li_layer_crs):
                        layer_dict["crsOptions"] = li_common_crs
                    else:
                        layer_dict["crsOptions"] = li_common_crs + li_layer_crs

                    # BBOX
                    li_bboxes = [
                        elem
                        for elem in layer.findall(tag_prefix + "BoundingBox")
                        if elem.get("CRS") in layer_dict["crsOptions"]
                    ]
                    if len(li_bboxes):
                        xmin = str(li_bboxes[0].get("minx"))
                        ymin = str(li_bboxes[0].get("miny"))
                        xmax = str(li_bboxes[0].get("maxx"))
                        ymax = str(li_bboxes[0].get("maxy"))
                        bbox_crs = str(li_bboxes[0].get("CRS"))

                        layer_dict["bbox"] = (xmin, ymin, xmax, ymax, bbox_crs)
                    else:
                        wgs84_bbox = layer.find(tag_prefix + "EX_GeographicBoundingBox")
                        if len(wgs84_bbox) and "EPSG:4326" in layer_dict.get("crsOptions"):
                            xmin = str(wgs84_bbox.find(tag_prefix + "southBoundLatitude").text)
                            ymin = str(wgs84_bbox.find(tag_prefix + "westBoundLongitude").text)
                            xmax = str(wgs84_bbox.find(tag_prefix + "northBoundLatitude").text)
                            ymax = str(wgs84_bbox.find(tag_prefix + "eastBoundLongitude").text)
                            bbox_crs = "EPSG:4326"

                            layer_dict["bbox"] = (xmin, ymin, xmax, ymax, bbox_crs)
                        else:
                            layer_dict["bbox"] = ()

                    li_layers.append(layer_dict)

            else:  # WMTS
                # check if get data operation is available + retrieve formatOptions
                xml_operationsMetadata = [
                    child for child in xml_root if "OperationsMetadata" in child.tag
                ][0]
                li_ope_names = [ope.get("name") for ope in xml_operationsMetadata]
                if main_op_name in li_ope_names:
                    service_dict["{}_isAvailable".format(main_op_name)] = 1
                else:
                    service_dict["{}_isAvailable".format(main_op_name)] = 0

                # retrieving available tileMatrixSets to store them into a dict
                dict_tms = {}
                for tms in xml_root.find(tag_prefix + "Contents").findall(
                    tag_prefix + "TileMatrixSet"
                ):
                    li_tms_id = [child.text for child in tms if child.tag.endswith("Identifier")]
                    li_tms_crs = [child.text for child in tms if child.tag.endswith("SupportedCRS")]

                    if not len(li_tms_id) or not len(li_tms_crs):
                        continue
                    else:
                        dict_tms[li_tms_id[0]] = li_tms_crs[0]

                # retrieving layers typenames and building layers list (typename, format, tms, styles, crs)
                li_typenames = []
                li_layers = []
                for layer in xml_root.find(tag_prefix + "Contents").findall(tag_prefix + "Layer"):
                    layer_dict = {}
                    # typename
                    li_layer_typenames = [
                        child.text for child in layer if child.tag.endswith("Identifier")
                    ]
                    if not len(li_layer_typenames):
                        continue
                    else:
                        li_typenames.append(li_layer_typenames[0])
                        layer_dict["typename"] = li_layer_typenames[0]
                    # format
                    li_layer_formats = [
                        child.text for child in layer if child.tag.endswith("Format")
                    ]
                    if not len(li_layer_formats):
                        layer_dict["formats"] = ""
                    else:
                        layer_dict["formats"] = li_layer_formats
                    # tms
                    xml_tmsLink = [
                        child for child in layer if child.tag.endswith("TileMatrixSetLink")
                    ][0]
                    li_layer_tms = [
                        child.text for child in xml_tmsLink if child.tag.endswith("TileMatrixSet")
                    ]
                    if not len(li_layer_tms):
                        layer_dict["tms"] = ""
                    else:
                        layer_dict["tms"] = li_layer_tms[0]
                    # styles
                    li_layer_styles = []
                    li_xml_styles = [child for child in layer if child.tag.endswith("Style")]
                    for style_elem in li_xml_styles:
                        li_elem_identifier = [
                            child.text for child in style_elem if child.tag.endswith("Identifier")
                        ]
                        if not len(li_elem_identifier):
                            continue
                        else:
                            li_layer_styles.append(li_elem_identifier[0])
                    layer_dict["styles"] = li_layer_styles
                    # crs
                    layer_dict["crsOptions"] = [dict_tms.get(layer_dict.get("tms"))]

                    li_layers.append(layer_dict)

        else:
            raise Exception(
                "GetCapabilities request failed using requests: {}:{}".format(
                    r.status_code, r.reason
                )
            )

        service_dict["typenames"] = li_typenames
        service_dict[service_type] = li_layers
        return service_dict

    def check_ogc_service(self, service_type: str, service_url: str, service_version: str):
        """Try to access to the given OGC service URL (using owslib library modules) and
        store various informations into cached_wfs, cached_wms or cached_wmts dict
        depending on service_type.

        :param str service_type: type of OGC service ("WFS", "WMS", or "WMTS")
        :param str service_url: the OGC service base URL
        :param str service_version: the OGC service version
        """
        # If service_type argument value is invalid, raise error
        if service_type not in self.ogc_infos_dict:
            raise ValueError(
                "'service_type' argument value should be one of {} not {}".format(
                    list(self.ogc_infos_dict.keys()), service_type
                )
            )
        # It it's valid, set local variables depending on it
        else:
            cache_dict = self.service_cached_dict.get(service_type)
            main_op_name = self.ogc_infos_dict.get(service_type)[0]
            service_connector = self.ogc_infos_dict.get(service_type)[1]

        cache_dict[service_url] = {}
        service_dict = cache_dict[service_url]

        # retrieve, clean and store service base URL
        if "?" in service_url:
            if service_url.endswith("?"):
                service_dict["base_url"] = service_url
            else:
                service_dict["base_url"] = service_url + "&"
        elif "&" in service_url:
            if service_url.endswith("&"):
                service_dict["base_url"] = service_url[:-1]
            else:
                service_dict["base_url"] = service_url + "&"
        else:
            service_dict["base_url"] = service_url + "?"

        # build URL of "GetCapabilities" operation
        service_dict["getCap_url"] = (
            service_dict["base_url"] + "request=GetCapabilities&service=" + service_type
        )

        if service_type == "WMTS":
            url = service_dict.get("getCap_url")
        else:
            url = service_dict.get("base_url")

        # Basic checks on service reachability
        try:
            service = service_connector(url=url, version=service_version)
            service_dict["reachable"] = 1
            service_dict["manual"] = 0
        except ServiceException as e:
            error_msg = "{} <i>{}</i> - <b>Bad operation</b>:\n{}".format(service_type, url, plg_tools.shorten_error(e))
            service_dict["reachable"] = 0
            service_dict["error"] = error_msg
        except HTTPError as e:
            error_msg = "{} <i>{}</i> - <b>Service not reached</b>:\n{}".format(
                service_type, url, plg_tools.shorten_error(e)
            )
            service_dict["reachable"] = 0
            service_dict["error"] = error_msg
        except requests.exceptions.SSLError as e:
            logger.error(
                "SSL Error raised trying to connect to {} service {}:\n{}".format(
                    service_type, url, plg_tools.shorten_error(e)
                )
            )
            try:
                auth = Authentication(verify=False)
                service = service_connector(url=url, version=service_version, auth=auth)
                service_dict["reachable"] = 1
                service_dict["manual"] = 0
                logger.info("Using owslib.Authentication module with 'verify=false' worked !")
            except Exception as e:
                logger.warning(
                    "Error raised trying to use owslib.Authentication module:\n{}".format(plg_tools.shorten_error(e))
                )
                try:
                    service_dict = self.parse_ogc_xml(service_type, service_dict)
                    logger.info("parse_ogc_xml method has to be used.")
                    return 1, service_dict
                except Exception as e_bis:
                    error_msg = (
                        "{} <i>{}</i> - <b>Connection to service failed (SSL Error)</b>:\n{}".format(
                            service_type, url, plg_tools.shorten_error(e_bis)
                        )
                    )
                    service_dict["reachable"] = 0
                    service_dict["error"] = error_msg
        except Exception as e:
            logger.warning(
                "Error raised trying to use {} from owslib specifying service version:\n{}".format(service_connector.__name__, plg_tools.shorten_error(e))
            )
            try:
                service = service_connector(url=url)
                service_dict["reachable"] = 1
            except Exception as e_bis:
                logger.warning(
                    "Error raised trying to use {} from owslib without specifying service version:\n{}".format(service_connector.__name__, plg_tools.shorten_error(e_bis))
                )
                try:
                    service_dict = self.parse_ogc_xml(service_type, service_dict)
                    logger.info("parse_ogc_xml method has to be used.")
                    return 1, service_dict
                except Exception as e_ter:
                    error_msg = "{} <i>{}</i> - <b>Connection to service failed</b>:\n{}".format(
                        service_type, url, plg_tools.shorten_error(e_ter)
                    )
                    service_dict["reachable"] = 0
                    service_dict["error"] = error_msg

        # if the service can't be reached, return the error
        if not service_dict.get("reachable"):
            return service_dict["reachable"], service_dict["error"]
        else:
            pass

        # Store several basic informations about the service
        service_dict[service_type] = service
        service_dict["typenames"] = list(service.contents.keys())
        service_dict["version"] = service_version
        service_dict["operations"] = [op.name for op in service.operations if hasattr(op, "name")]
        service_dict["formatOptions"] = [
            f.split(";", 1)[0] for f in service.getOperationByName(main_op_name).formatOptions
        ]

        # check if main operation ("GetMap" or "GetFeature" depending on service type) is available
        # if it do, retrieve, clean and store the corresponding URL
        if main_op_name in service_dict["operations"]:
            service_dict["{}_isAvailable".format(main_op_name)] = 1
        else:
            service_dict["{}_isAvailable".format(main_op_name)] = 0

        # only for WMTS
        if service_type == "WMTS":
            service_dict["wmts_tms"] = {}
            for tms in service.tilematrixsets:
                crs_elem = service.tilematrixsets.get(tms).crs.split(":")
                if len(crs_elem) == 2:
                    value = service.tilematrixsets.get(tms).crs
                else:
                    value = "EPSG:" + crs_elem[-1]
                key = service.tilematrixsets.get(tms).identifier
                service_dict["wmts_tms"][key] = value
        else:
            pass

        return 1, service_dict

    def build_wfs_url(self, api_layer: dict, srv_details: dict):
        """Build a WFS layer URL -according to QGIS expectations- using informations
        provided by Isogeo API.

        :param dict api_layer: dict object containing Isogeo API informations about the layer
        :param dict srv_details: dict object containing Isogeo API informations about the service
        """
        wfs_cached_dict = self.service_cached_dict.get("WFS")
        # check the service accessibility and retrieve informations
        if srv_details.get("path") not in wfs_cached_dict:
            check = self.check_ogc_service(
                service_type="WFS",
                service_url=srv_details.get("path"),
                service_version=srv_details.get("formatVersion"),
            )
            if check[0]:
                wfs_dict = check[1]
            else:
                return check
        elif not wfs_cached_dict.get(srv_details.get("path")).get("reachable"):
            return (
                wfs_cached_dict.get(srv_details.get("path")).get("reachable"),
                wfs_cached_dict.get(srv_details.get("path")).get("error"),
            )
        else:
            wfs_dict = wfs_cached_dict[srv_details.get("path")]
        # local variables
        wfs_url_getcap = wfs_dict.get("getCap_url")
        wfs_url_base = wfs_dict.get("base_url")
        wfs = wfs_dict.get("WFS")
        api_layer_id = api_layer.get("id")
        # check if GetFeature and DescribeFeatureType operation are available
        if not hasattr(wfs, "getfeature") and not wfs_dict.get("GetFeature_isAvailable"):
            return 0, f"GetFeature operation not available in: {wfs_url_getcap}"
        # check if layer can be found
        layer_typename = self.find_wfs_layer(api_layer_id, wfs_dict.get("typenames"), wfs_url_base)
        if not layer_typename:
            return 0, f"WFS <i>{wfs_url_base}</i> - <b>Unable to find '{api_layer_id}' layer</b>, the layer may not be available anymore."
        layer_title = self.build_layer_title("WFS", api_layer)

        # build URL
        li_url_params = [
            "REQUEST=GetFeature",
            "SERVICE=WFS",
            "VERSION={}".format(wfs_dict.get("version")),
            "TYPENAME={}".format(layer_typename),
            "RESULTTYPE=results"
        ]
        if api_layer.get("type") == "table":
            pass
        else:
            # SRS definition
            if wfs_dict.get("manual"):
                wfs_lyr = [lyr for lyr in wfs if lyr.get("typename") == layer_typename][0]
                available_crs_options = ["EPSG:" + wfs_lyr.get("EPSG")]
            else:
                available_crs_options = [
                    "{}:{}".format(srs.authority, srs.code) for srs in wfs[layer_typename].crsOptions
                ]
            srs = self.choose_appropriate_srs(crs_options=available_crs_options)
            srs_code = srs.split(":")[1] if bool(re.fullmatch(r'[+-]?\d+', srs.split(":")[1].strip())) else False
            if wfs_dict.get("manual"):
                srs_id = wfs_lyr.get("srs_id")
                li_url_params.append("SRSNAME={}".format(srs))
            elif len(wfs[layer_typename].crsOptions):
                srs_id = [crsOption.id for crsOption in wfs[layer_typename].crsOptions if srs_code in str(crsOption.code)][0]
                li_url_params.append("SRSNAME={}".format(srs))
            else:
                srs_id = False

            # trying to set BBOX parameter as current map canvas extent
            if "EPSG" in srs and srs_id and srs_code:
                canvas_rectangle = iface.mapCanvas().extent()
                canvas_crs = iface.mapCanvas().mapSettings().destinationCrs()
                destination_crs = QgsCoordinateReferenceSystem(
                    int(srs_code), QgsCoordinateReferenceSystem.EpsgCrsId
                )
                coord_transformer = QgsCoordinateTransform(
                    canvas_crs, destination_crs, QgsProject.instance()
                )

                destCrs_rectangle = coord_transformer.transform(canvas_rectangle)

                bbox_parameter = "BBOX={},{},{},{},{}&restrictToRequestBBOX=1".format(
                    destCrs_rectangle.yMinimum(),
                    destCrs_rectangle.xMinimum(),
                    destCrs_rectangle.yMaximum(),
                    destCrs_rectangle.xMaximum(),
                    srs_id,
                )
                li_url_params.append(bbox_parameter)
            else:
                pass

        wfs_url_final = wfs_url_base + "&".join(li_url_params)

        return ("WFS", layer_title, wfs_url_final)

    def build_wms_url(self, api_layer: dict, srv_details: dict):
        """Build a WMS layer URL -according to QGIS expectations- using informations
        provided by Isogeo API.

        :param dict api_layer: dict object containing Isogeo API informations about the layer
        :param dict srv_details: dict object containing Isogeo API informations about the service
        """
        wms_cached_dict = self.service_cached_dict.get("WMS")
        # check the service accessibility and store service informations
        if srv_details.get("path") not in wms_cached_dict:
            check = self.check_ogc_service(
                service_type="WMS",
                service_url=srv_details.get("path"),
                service_version=srv_details.get("formatVersion"),
            )
            if check[0]:
                wms_dict = check[1]
            else:
                return check
        elif not wms_cached_dict.get(srv_details.get("path")).get("reachable"):
            return (
                wms_cached_dict.get(srv_details.get("path")).get("reachable"),
                wms_cached_dict.get(srv_details.get("path")).get("error"),
            )
        else:
            wms_dict = self.service_cached_dict.get("WMS")[srv_details.get("path")]

        # local variables
        api_layer_id = api_layer.get("id")
        wms_url_getcap = wms_dict.get("getCap_url")
        wms_url_base = wms_dict.get("base_url")
        wms = wms_dict.get("WMS")

        # build layer title
        layer_title = self.build_layer_title("WMS", api_layer)

        # check layer availability
        if api_layer_id not in wms_dict.get("typenames"):
            error_msg = "WMS <i>{}</i> - <b>Unable to find '{}' layer</b>, the layer may not be available anymore.".format(
                wms_url_base, api_layer_id
            )
            return 0, error_msg
        elif wms_dict.get("manual"):  # if the wms_lyr object was generated via parse_ogc_xml
            wms_lyr = [lyr for lyr in wms if lyr.get("typename") == api_layer_id][0]
        else:
            wms_lyr = wms[api_layer_id]

        # check if GetMap operation is available
        if not hasattr(wms, "getmap") and not wms_dict.get("GetMap_isAvailable"):
            return (
                0,
                "Required GetMap operation not available in: {}".format(wms_url_getcap),
            )
        else:
            logger.info("GetMap available")

        # Update 'layers' param value in the case of multi-layer
        li_layer_name = [api_layer_id]
        li_layer_title = [layer_title]
        # if hasattr(wms_lyr, "layers"):
        #     if len(wms_lyr.layers):
        #         li_layer_name = []
        #         li_layer_title = []
        #         for layer in wms_lyr.layers:
        #             li_layer_name.append(layer.name)
        #             li_layer_title.append(layer.title)
        #     else:
        #         pass
        # else:
        #     pass

        # WIDTH and HEIGHT parameters
        canvas_size = iface.mapCanvas().size()
        width = str(canvas_size.width() - 1)
        height = str(canvas_size.height() - 1)

        # Style definition (+ WIDTH and HEIGHT)
        if hasattr(wms_lyr, "styles") and len(wms_lyr.styles):
            li_styles = list(wms_lyr.styles.keys())
            li_style_candidates = [style for style in li_styles if "normal" in style]
            if len(li_style_candidates):
                lyr_style = li_style_candidates[0]
            else:
                lyr_style = li_styles[0]
                lyr_style = ""
        else:
            lyr_style = ""

        # Format definition
        formats_image = [f for f in wms_dict.get("formatOptions") if f in qgis_wms_formats]
        if "image/png" in formats_image:
            layer_format = "image/png"
        elif "image/jpeg" in formats_image:
            layer_format = "image/jpeg"
        else:
            layer_format = formats_image[0]

        # SRS definition
        if hasattr(wms_lyr, "crsOptions"):
            srs = self.choose_appropriate_srs(crs_options=wms_lyr.crsOptions)
        elif "crsOptions" in wms_lyr:  # if the wms_lyr object was generated via parse_ogc_xml
            srs = self.choose_appropriate_srs(crs_options=wms_lyr.get("crsOptions"))
        else:
            srs = self.choose_appropriate_srs(crs_options=[])

        # BBOX parameter
        destination_crs = QgsCoordinateReferenceSystem(srs)
        has_bbox = False
        if hasattr(wms_lyr, "boundingBoxWGS84") or hasattr(wms_lyr, "boundingBox"):
            has_bbox = True
        elif wms_dict.get("manual") and "bbox" in wms_lyr and len(wms_lyr.get("bbox", ())) == 5:
            has_bbox = True
        else:
            pass

        if not destination_crs.isValid():
            bbox = ""
            logger.warning(
                "BBOX parameter cannot be set because srs is not recognized : {}.".format(srs)
            )
        elif not has_bbox:
            bbox = ""
            logger.warning(
                "BBOX parameter cannot be set because wms layer object has no boundingBox attributes."
            )
        else:
            source_crs_id = ""
            if hasattr(wms_lyr, "boundingBox"):
                wms_lyr_bbox = wms_lyr.boundingBox
            elif hasattr(wms_lyr, "boundingBoxWGS84"):
                wms_lyr_bbox = wms_lyr.boundingBoxWGS84
                source_crs_id = "EPSG:4326"
            else:
                wms_lyr_bbox = wms_lyr.get("bbox")

            if source_crs_id == "EPSG:4326":
                pass
            else:
                if len(wms_lyr_bbox) >= 5:
                    source_crs_id = wms_lyr_bbox[4]
                else:  # because apparently this is not always the case : https://magosm.magellium.com/geoserver/ows?
                    source_crs_id = srs

            logger.info("Let's use {} bbox.".format(source_crs_id))
            source_crs = QgsCoordinateReferenceSystem(source_crs_id)

            coord_transformer = QgsCoordinateTransform(
                source_crs, destination_crs, QgsProject.instance()
            )
            bbox_rectangle = QgsRectangle(
                float(wms_lyr_bbox[0]),
                float(wms_lyr_bbox[1]),
                float(wms_lyr_bbox[2]),
                float(wms_lyr_bbox[3]),
            )
            transformed_bbox_rectangle = coord_transformer.transform(bbox_rectangle)

            bbox = "{},{},{},{}".format(
                transformed_bbox_rectangle.xMinimum(),
                transformed_bbox_rectangle.yMinimum(),
                transformed_bbox_rectangle.xMaximum(),
                transformed_bbox_rectangle.yMaximum(),
            )

        li_url = []
        for layer_name in li_layer_name:
            # url construction
            wms_url_params = {
                "SERVICE": "WMS",
                "VERSION": wms_dict.get("version"),
                "REQUEST": "GetMap",
                "layers": layer_name,
                "crs": srs,
                "format": layer_format,
                "styles": lyr_style,
                "TRANSPARENT": "TRUE",
                "BBOX": bbox,
                "WIDTH": width,
                "HEIGHT": height,
            }

            if "&" in wms_url_base:  # for case when there is already params into base url
                wms_url_params["url"] = "{}?{}".format(
                    wms_url_base.split("?")[0], quote(wms_url_base.split("?")[1])
                )
            else:  # for "easy" base url
                wms_url_params["url"] = wms_url_base.split("?")[0] + "?"

            url_for_requests = unquote(wms_url_params.get("url")) + "&".join(
                [
                    "{}={}".format(k, v)
                    for k, v in wms_url_params.items()
                    if k != "url"
                    # if k != "url" and v != ""
                ]
            )

            check_requests = requests.get(url_for_requests, verify=False)
            if check_requests.status_code == 400:
                wms_url_final = url_for_requests
            else:
                wms_url_final = unquote(urlencode(wms_url_params, "utf8"))
            li_url.append(wms_url_final)

        return ("WMS", li_layer_title, li_url)

    def build_wmts_url(self, api_layer: dict, srv_details: dict):
        """Build a WMTS layer URL -according to QGIS expectations- using informations
        provided by Isogeo API.

        :param dict api_layer: dict object containing Isogeo API informations about the layer
        :param dict srv_details: dict object containing Isogeo API informations about the service
        """
        wmts_cached_dict = self.service_cached_dict.get("WMTS")
        # check the service accessibility and store service informations
        if srv_details.get("path") not in wmts_cached_dict:
            check = self.check_ogc_service(
                service_type="WMTS",
                service_url=srv_details.get("path"),
                service_version=srv_details.get("formatVersion"),
            )
            if check[0]:
                wmts_dict = check[1]
            else:
                return check
        elif not wmts_cached_dict.get(srv_details.get("path")).get("reachable"):
            return (
                wmts_cached_dict.get(srv_details.get("path")).get("reachable"),
                wmts_cached_dict.get(srv_details.get("path")).get("error"),
            )
        else:
            wmts_dict = wmts_cached_dict.get(srv_details.get("path"))

        # local variables
        api_layer_id = api_layer.get("id")
        wmts = wmts_dict.get("WMTS")
        wmts_lyr_url = wmts_dict.get("base_url")

        # build layer title
        layer_title = self.build_layer_title("WMTS", api_layer)

        # check layer availability + retrieve its real id for "layers" URL parameter
        if api_layer_id in wmts_dict.get("typenames"):
            layer_typename = api_layer_id
        elif any(api_layer_id in typename.split(":") for typename in wmts_dict.get("typenames")):
            layer_typename = [
                typename
                for typename in wmts_dict.get("typenames")
                if api_layer_id in typename.split(":")
            ][0]
        elif any(api_layer_id in typename for typename in wmts_dict.get("typenames")):
            layer_typenames = [
                typename for typename in wmts_dict.get("typenames") if api_layer_id in typename
            ]
            if len(layer_typenames) > 1:
                warning_msg = "WMTS {} - Multiple typenames matched for '{}' layer, the first one will be chosen: {}".format(
                    wmts_lyr_url, api_layer_id, layer_typenames[0]
                )
                logger.warning(warning_msg)
            else:
                pass
            layer_typename = layer_typenames[0]
        else:
            error_msg = "WMTS <i>{}</i> - <b>Unable to find '{}' layer</b>, the layer may not be available anymore.".format(
                wmts_lyr_url, api_layer_id
            )
            return 0, error_msg

        if wmts_dict.get("manual"):  # if the wms_lyr object was generated via parse_ogc_xml
            wmts_lyr = [lyr for lyr in wmts if lyr.get("typename") == api_layer_id][0]
        else:
            wmts_lyr = wmts[layer_typename]

        # check if GetTile operation is available
        if not hasattr(wmts, "gettile") and not wmts_dict.get("GetTile_isAvailable"):
            return (
                0,
                "Required GetTile operation not available in: " + wmts_dict.get("getCap_url"),
            )
        else:
            logger.debug("GetTile available")

        # retrieve Tile Matrix Set & SRS
        if wmts_dict.get("manual"):
            srs = self.choose_appropriate_srs(wmts_lyr.get("crsOptions"))
            tile_matrix_set = wmts_lyr.get("tms")
        else:
            tms_dict = wmts_dict.get("wmts_tms")
            available_crs = [
                crs for tms, crs in tms_dict.items() if tms in wmts_lyr._tilematrixsets
            ]
            srs = self.choose_appropriate_srs(available_crs)
            if srs:
                tile_matrix_set = [tms for tms, crs in tms_dict.items() if crs == srs][0]
            else:
                logger.debug(
                    "WMTS - Let's choose the SRS corresponding to the only available Tile Matrix Set for this layer"
                )
                tile_matrix_set = wmts_lyr._tilematrixsets[0]
                srs = [v for k, v in tms_dict.items() if tile_matrix_set in k][0]

        # Format definition
        if wmts_dict.get("manual"):
            formats_image = wmts_lyr.get("formats")
        else:
            formats_image = wmts_lyr.formats
        if len(formats_image):
            if "image/jpeg" in formats_image:
                layer_format = "image/jpeg"
            elif "image/png" in formats_image:
                layer_format = "image/png"
            else:
                layer_format = formats_image[0]
        else:
            logger.debug("WMTS - No format specified, let's try with 'image/png'.")
            layer_format = "image/png"

        # Style definition
        if hasattr(wmts_lyr, "styles") and len(wmts_lyr.styles):
            lyr_style = list(wmts_lyr.styles.keys())[0]
        elif wmts_dict.get("manual") and len(wmts_lyr.get("styles")):
            lyr_style = wmts_lyr.get("styles")[0]
        else:
            lyr_style = ""

        # construct URL
        li_uri_params = [
            "crs={}&".format(srs),
            "format={}&".format(layer_format),
            "layers={}&".format(layer_typename),
            "styles={}&".format(lyr_style),
            "tileMatrixSet={}&".format(tile_matrix_set),
            "url={}".format(wmts_lyr_url),
            quote("SERVICE=WMTS&"),
            quote("VERSION={}&".format(wmts_dict.get("version"))),
            quote("REQUEST=GetCapabilities"),
        ]
        wmts_url_final = "".join(li_uri_params)

        # method ending
        return ("WMTS", layer_title, wmts_url_final)

    def check_esri_service(self, service_type: str, service_url: str):
        """Try to access to the given ESRI service URL (using request library) and store
        various informations into cached_efs or cached_ems dict depending on
        service_type.

        :param str service_type: type of ESRI service ("EFS" or "EMS")
        :param str service_url: the ESRI service base URL
        """
        # If service_type argument value is invalid, raise error
        if service_type not in self.esri_infos_dict:
            raise ValueError(
                "'service_type' argument value should be one of {} not {}".format(
                    list(self.esri_infos_dict.keys()), service_type
                )
            )
        # It it's valid, set local variables depending on it
        else:
            cache_dict = self.service_cached_dict.get(service_type)
            srs_entry_name = self.esri_infos_dict.get(service_type)

        cache_dict[service_url] = {}
        service_dict = cache_dict[service_url]

        # retrieve, clean and store service base URL
        if service_url.endswith("/"):
            service_dict["base_url"] = service_url
        else:
            service_dict["base_url"] = service_url + "/"

        # check if a afs_connection exists in QSettings - https://github.com/isogeo/isogeo-plugin-qgis/issues/467
        service_dict["afs_connection"] = False
        for afs_connection in settings_mng.afs_connections:
            if settings_mng.afs_connections.get(afs_connection).get("url") in service_url and settings_mng.afs_connections.get(afs_connection).get("authcfg"):
                service_dict["afs_connection"] = afs_connection
                break
            else:
                pass

        # build URL of "GetCapabilities" operation
        service_dict["getCap_url"] = service_dict["base_url"] + "?f=json"

        # try to send "GetCapabilities" equivalent request
        if service_dict.get("afs_connection"):
            authcfg = settings_mng.afs_connections.get(service_dict.get("afs_connection")).get("authcfg")
            try:
                qnam = QgsNetworkAccessManager.instance()
                request = QNetworkRequest(QUrl(service_dict["getCap_url"]))
                reply = qnam.blockingGet(request, authcfg)

                reply_content_str = reply.content().data().decode("utf8")
                reply_content_json = json.loads(reply_content_str)

                getCap_content = reply_content_json
                service_dict["reachable"] = 1

                del qnam
            except Exception as e:
                error_msg = "{} <i>{}</i> - <b>Unable to access service capabilities</b>: {}".format(
                    service_type, service_dict["getCap_url"], e
                )
                getCap_content = ""
                service_dict["reachable"] = 0
                service_dict["error"] = error_msg
        else:
            try:
                getCap_request = requests.get(service_dict["getCap_url"], verify=False)
                getCap_content = getCap_request.json()
                service_dict["reachable"] = 1
            except (requests.HTTPError, requests.Timeout, requests.ConnectionError) as e:
                error_msg = "{} <i>{}</i> - <b>Server connection failure</b>: {}".format(
                    service_type, service_dict["getCap_url"], e
                )
                getCap_content = ""
                service_dict["reachable"] = 0
                service_dict["error"] = error_msg
            except Exception as e:
                error_msg = "{} <i>{}</i> - <b>Unable to access service capabilities</b>: {}".format(
                    service_type, service_dict["getCap_url"], e
                )
                getCap_content = ""
                service_dict["reachable"] = 0
                service_dict["error"] = error_msg

        # if the service is an ETS provided as EMS by Isogeo API
        if "tileInfo" in getCap_content:
            error_msg = "{} <i>{}</i> - This <b>service is an EsriTileService</b> provided as {} by Isogeo API. No layer will be added.".format(
                service_type, service_dict["getCap_url"], service_type
            )
            service_dict["reachable"] = 0
            service_dict["error"] = error_msg
            return service_dict["reachable"], service_dict["error"]
        # if a token is needed
        elif "error" in getCap_content:
            if getCap_content.get("error").get("code") == 499:
                error_msg = "{} <i>{}</i> - This <b>service is private</b>. You cannot access its content from Isogeo plugin.".format(
                    service_type, service_dict["getCap_url"]
                )
                service_dict["reachable"] = 0
                service_dict["error"] = error_msg
            else:
                pass
        else:
            pass

        # if the service can't be reached, return the error
        if not service_dict.get("reachable"):
            return service_dict["reachable"], service_dict["error"]
        else:
            pass

        # retrieve appropriate srs from service capabilities
        if "spatialReference" in getCap_content:
            if srs_entry_name in getCap_content.get("spatialReference"):
                service_dict["appropriate_srs"] = "EPSG:" + str(
                    getCap_content.get("spatialReference").get(srs_entry_name)
                )
            elif "wkt" in getCap_content.get("spatialReference"):
                service_dict["appropriate_srs"] = QgsCoordinateReferenceSystem.fromWkt(getCap_content.get("spatialReference").get("wkt")).authid()
            else:
                service_dict["appropriate_srs"] = ""
        else:
            warning_msg = "{} {} - Unable to retrieve information about appropriate srs from service capabilities: 'spatialReference' is missing into GetCapabilities".format(
                service_type, service_dict["getCap_url"]
            )
            logger.warning(warning_msg)
            service_dict["appropriate_srs"] = ""

        return 1, service_dict

    def build_efs_url(self, api_layer: dict, srv_details: dict):
        """Build a EFS layer URL -according to QGIS expectations- using informations
        provided by Isogeo API.

        :param dict api_layer: dict object containing Isogeo API informations about the layer
        :param dict srv_details: dict object containing Isogeo API informations about the service
        """
        efs_cached_dict = self.service_cached_dict.get("EFS")
        # check the service accessibility and store service informations
        if srv_details.get("path") not in efs_cached_dict:
            check = self.check_esri_service(
                service_type="EFS",
                service_url=srv_details.get("path"),
            )
            if check[0]:
                efs_dict = check[1]
            else:
                return check
        elif not efs_cached_dict.get(srv_details.get("path")).get("reachable"):
            return (
                efs_cached_dict.get(srv_details.get("path")).get("reachable"),
                efs_cached_dict.get(srv_details.get("path")).get("error"),
            )
        else:
            efs_dict = efs_cached_dict[srv_details.get("path")]

        # retrieve layer id
        api_layer_id = api_layer.get("id")

        # build layer title
        layer_title = self.build_layer_title("EFS", api_layer)

        # retrieve and clean service efs_base_url
        efs_base_url = efs_dict.get("base_url")

        # retrieve appropriate srs
        if efs_dict.get("appropriate_srs") not in ["EPSG:None", ""]:
            srs = efs_dict.get("appropriate_srs")
        else:
            srs = plg_tools.get_map_crs()
        # build EFS layer URI
        efs_uri = "crs='{}' ".format(srs)
        efs_uri += "url='{}{}' ".format(efs_base_url, api_layer_id)

        if efs_dict.get("afs_connection"):
            authcfg = settings_mng.afs_connections.get(efs_dict.get("afs_connection")).get("authcfg")
            efs_uri = "authcfg={} {}".format(authcfg, efs_uri)
        else:
            pass

        return ("EFS", layer_title, efs_uri)

    def build_ems_url(self, api_layer: dict, srv_details: dict):
        """Build a EMS layer URL -according to QGIS expectations- using informations
        provided by Isogeo API.

        :param dict api_layer: dict object containing Isogeo API informations about the layer
        :param dict srv_details: dict object containing Isogeo API informations about the service
        """
        ems_cached_dict = self.service_cached_dict.get("EMS")
        # check the service accessibility and store service informations
        if srv_details.get("path") not in ems_cached_dict:
            check = self.check_esri_service(
                service_type="EMS",
                service_url=srv_details.get("path"),
            )
            if check[0]:
                ems_dict = check[1]
            else:
                return check
        elif not ems_cached_dict.get(srv_details.get("path")).get("reachable"):
            return (
                ems_cached_dict.get(srv_details.get("path")).get("reachable"),
                ems_cached_dict.get(srv_details.get("path")).get("error"),
            )
        else:
            ems_dict = ems_cached_dict[srv_details.get("path")]

        # retrieve layer id
        api_layer_id = api_layer.get("id")

        # build layer title
        layer_title = self.build_layer_title("EMS", api_layer)

        # retrieve and clean service ems_base_url
        ems_base_url = ems_dict.get("base_url")

        # retrieve appropriate srs
        srs = ems_dict.get("appropriate_srs")

        # build EMS layer URI
        ems_uri = QgsDataSourceUri()
        ems_uri.setParam("url", ems_base_url)
        ems_uri.setParam("layer", api_layer_id)
        ems_uri.setParam("crs", srs)

        ems_uri = ems_uri.uri()

        if ems_dict.get("afs_connection"):
            authcfg = settings_mng.afs_connections.get(ems_dict.get("afs_connection")).get("authcfg")
            ems_uri = "authcfg={} {}".format(authcfg, ems_uri)
        else:
            pass

        return ("EMS", layer_title, ems_uri)
