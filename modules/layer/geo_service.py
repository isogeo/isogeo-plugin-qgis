# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import re

from urllib.parse import urlencode, unquote, quote

# PyQT
from qgis.PyQt.QtCore import QSettings

# PyQGIS
from qgis.core import QgsDataSourceUri

# Plugin modules
from ..tools import IsogeoPlgTools

# ############################################################################
# ########## Globals ###############
# ##################################

qsettings = QSettings()
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

    logging.info("Depencencies - owslib version: {}".format(owslib.__version__))
except ImportError:
    logger.warning("Depencencies - owslib is not present")

try:
    from owslib.wfs import WebFeatureService
except ImportError as e:
    logger.warning("Depencencies - owslib WFS issue: {}".format(e))

try:
    from owslib.util import HTTPError

    logger.info("Depencencies - HTTPError within owslib")
except ImportError:
    from urllib.error import HTTPError

    logger.warning(
        "Depencencies - HTTPError not within owslib."
        " Directly imported from urllib.error"
    )
try:
    import requests
    logger.info("Depencencies - Requests version: {}".format(requests.__version__))
except ImportError:
    logger.warning("Depencencies - Requests not available")

# ############################################################################
# ########## Classes ###############
# ##################################


class GeoServiceManager:
    """Basic class that holds methods used to add layers to canvas."""

    def __init__(self):
        """Class constructor."""
        # cache
        self.cached_wfs = dict()
        self.cached_wms = dict()
        self.cached_wmts = dict()
        self.cached_efs = dict()
        self.cached_ems = dict()

        self.ogc_infos_dict = {
            "WFS": [
                "GetFeature",
                self.cached_wfs,
                WebFeatureService
            ],
            "WMS": [
                "GetMap",
                self.cached_wms,
                WebMapService
            ],
            "WMTS": [
                "GetTile",
                self.cached_wmts,
                WebMapTileService
            ]
        }

        self.esri_infos_dict = {
            "EFS": [
                self.cached_efs,
                "latestWkid"
            ],
            "EMS": [
                self.cached_ems,
                "wkid"
            ]
        }

    def choose_appropriate_srs(self, crs_options: list):
        """Return an appropriate srs depending on QGIS configuration and available
        service layer crs options.
        """

        if len(crs_options):
            # SRS definition
            srs_map = plg_tools.get_map_crs()
            srs_lyr_new = qsettings.value("/Projections/defaultBehaviour")
            srs_lyr_crs = qsettings.value("/Projections/layerDefaultCrs")
            srs_qgs_new = qsettings.value("/Projections/projectDefaultCrs")
            srs_qgs_otf_on = qsettings.value("/Projections/otfTransformEnabled")
            srs_qgs_otf_auto = qsettings.value("/Projections/otfTransformAutoEnable")

            if srs_map in crs_options:
                logger.debug("It's a SRS match! With map canvas: " + srs_map)
                srs = srs_map
            elif srs_qgs_new in crs_options and srs_qgs_otf_on == "false" and srs_qgs_otf_auto == "false":
                logger.debug(
                    "It's a SRS match! With default new project: " + srs_qgs_new
                )
                srs = srs_qgs_new
            elif srs_lyr_crs in crs_options and srs_lyr_new == "useGlobal":
                logger.debug("It's a SRS match! With default new layer: " + srs_lyr_crs)
                srs = srs_lyr_crs
            elif "EPSG:4326" in crs_options:
                logger.debug("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                srs = "EPSG:4326"
            else:
                logger.debug("Map Canvas SRS not available within service CRS. One of the following ones gonna be choosed : {}".format(crs_options))
                srs = crs_options[0]
            return srs
        else:
            return 0

    def check_ogc_service(
        self, service_type: str, service_url: str, service_version: str
    ):
        """Try to acces to the service from the given service_url and store the
        capabilities into cached_wfs dict.
        """
        # If service_type argument value is invalid, raise error
        if service_type not in self.ogc_infos_dict:
            raise ValueError(
                "'service_type' argument value should be one of {} not {}".format(
                    list(self.ogc_infos_dict.keys()),
                    service_type
                )
            )
        # It it's valid, set local variables depending on it
        else:
            main_op_name = self.ogc_infos_dict.get(service_type)[0]
            cache_dict = self.ogc_infos_dict.get(service_type)[1]
            service_connector = self.ogc_infos_dict.get(service_type)[2]

        cache_dict[service_url] = {}
        service_dict = cache_dict[service_url]

        # retrieve, clean and store service base URL
        if service_url.endswith("?"):
            service_dict["base_url"] = service_url
        elif service_url.endswith("&"):
            service_dict["base_url"] = service_url[:-1]
        elif "&" in service_url:
            service_dict["base_url"] = service_url + "&"
        else:
            service_dict["base_url"] = service_url + "?"

        # build URL of "GetCapabilities" operation
        service_dict["getCap_url"] = service_dict["base_url"] + "request=GetCapabilities&service=" + service_type

        if service_type == "WMTS":
            url = service_dict.get("getCap_url")
        else:
            url = service_dict.get("base_url")

        # Basic checks on service reachability
        try:
            service = service_connector(url=url, version=service_version)
            service_dict["reachable"] = 1
        except ServiceException as e:
            error_msg = "{} - Bad operation ({}): {}".format(
                service_type, url, str(e)
            )
            logger.error(error_msg)
            service_dict["reachable"] = 0
            service_dict["error"] = error_msg
            return service_dict["reachable"], service_dict["error"]
        except HTTPError as e:
            error_msg = "{} - Service ({}) not reached: {}".format(
                service_type, url, str(e)
            )
            logger.error(error_msg)
            service_dict["reachable"] = 0
            service_dict["error"] = error_msg
            return service_dict["reachable"], service_dict["error"]
        except Exception:
            try:
                service = service_connector(url=url)
                service_dict["reachable"] = 1
            except Exception as e:
                error_msg = "{} - Connection to service ({}) failed: {}".format(
                    service_type, url, str(e)
                )
                logger.error(error_msg)
                service_dict["reachable"] = 0
                service_dict["error"] = error_msg
                return service_dict["reachable"], service_dict["error"]

        # Store several basic informations about the service
        service_dict[service_type] = service
        service_dict["typenames"] = list(service.contents.keys())
        service_dict["version"] = service.version
        service_dict["operations"] = [op.name for op in service.operations]
        service_dict["formatOptions"] = [f.split(";", 1)[0]for f in service.getOperationByName(main_op_name).formatOptions]

        # check if main operation ("GetMap" or "GetFeature" depending on service type) is available
        # if it do, retrieve, clean and store the corresponding URL
        if main_op_name in service_dict["operations"]:
            row_main_op_url = service.getOperationByName(main_op_name).methods[0].get("url")
            if "&" in row_main_op_url:
                if service_type == "WMTS":
                    main_op_url = row_main_op_url.split("?")[0] + "?"
                    additional_params = [part for part in row_main_op_url.split("?")[1].split("&") if part != ""]
                    for param in additional_params:
                        main_op_url += quote("{}&".format(param))
                elif row_main_op_url.endswith("&"):
                    main_op_url = row_main_op_url[:-1]
                else:
                    main_op_url = row_main_op_url + "&"
            else:
                if row_main_op_url.endswith("?"):
                    main_op_url = row_main_op_url
                else:
                    main_op_url = row_main_op_url + "?"
            main_op_key = "{}_url".format(main_op_name)
            service_dict[main_op_key] = main_op_url
            service_dict["{}_isAvailable".format(main_op_name)] = 1
        else:
            service_dict["{}_isAvailable".format(main_op_name)] = 0

        # only for WMTS
        if service_type == "WMTS":
            service_dict["wmts_tms"] = {}
            for tms in service.tilematrixsets:
                crs_elem = service.tilematrixsets.get(tms).crs.split(":")
                if len(crs_elem) == 2:
                    key = service.tilematrixsets.get(tms).crs
                else:
                    key = "EPSG:" + crs_elem[-1]
                value = service.tilematrixsets.get(tms).identifier
                service_dict["wmts_tms"][key] = value
        else:
            pass

        return 1, service_dict

    def build_wfs_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input WFS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # check the service accessibility and retrieve informations
        if srv_details.get("path") not in self.cached_wfs:
            check = self.check_ogc_service(
                service_type="WFS",
                service_url=srv_details.get("path"),
                service_version=srv_details.get("formatVersion"),
            )
            if check[0]:
                wfs_dict = check[1]
            else:
                return check
        elif not self.cached_wfs.get(srv_details.get("path")).get("reachable"):
            return (
                self.cached_wfs.get(srv_details.get("path")).get("reachable"),
                self.cached_wfs.get(srv_details.get("path")).get("error"),
            )
        else:
            wfs_dict = self.cached_wfs[srv_details.get("path")]

        # retrieve base url
        wfs_url_base = wfs_dict.get("base_url")

        # retrieve and clean api_layer_name from api_layer_id
        api_layer_id = api_layer.get("id")
        api_layer_name = re.sub("\{.*?}", "", api_layer_id)

        # build layer title
        if len(api_layer.get("titles")):
            layer_title = api_layer.get("titles")[0].get("value", api_layer_name)
        else:
            layer_title = api_layer_name

        # build GetCapabilities url
        wfs_url_getcap = wfs_dict.get("getCap_url")

        # retrieve the wfs layer id (the real one) for "TYPENAME" URL parameter
        logger.debug("*=====* DEBUG ADD FROM WFS : layer_name --> {}".format(api_layer_name))
        logger.debug("*=====* DEBUG ADD FROM WFS : wfs_dict --> {}".format(wfs_dict))
        layer_typename = [typename for typename in wfs_dict.get("typenames") if api_layer_name in typename]
        if len(layer_typename) == 1:
            layer_typename = layer_typename[0]
        elif len(layer_typename) > 1:
            layer_typename = layer_typename[0]
            logger.warning(
                "WFS {} - Multiple typenames matched for {} layer, {} the first one will be choosed.".format(
                    srv_details.get("path"), api_layer_name, layer_typename
                )
            )
        else:
            logger.error(
                "WFS {} - No typename found for {} layer, the layer may not be available anymore.".format(
                    srv_details.get("path"), api_layer_name
                )
            )
            return 0, "WFS - Layer '{}' not found in service {}".format(api_layer_name, srv_details.get("path"))

        if mode == "quicky":
            li_url_params = [
                "REQUEST=GetFeature",
                "SERVICE=WFS",
                "VERSION={}".format(wfs_dict.get("version")),
                "TYPENAME={}".format(layer_typename),
            ]

            wfs_url_quicky = wfs_url_base + "&".join(li_url_params)
            btn_lbl = "WFS : {}".format(layer_title)

            return ["WFS", layer_title, wfs_url_quicky, api_layer, srv_details, btn_lbl]

        elif mode == "complete":
            # Clean, complete but slower way - OWSLib -------------------------
            wfs = wfs_dict.get("WFS")
            # check if GetFeature and DescribeFeatureType operation are available
            if not hasattr(wfs, "getfeature") or not wfs_dict.get("GetFeature_isAvailable"):
                return 0, "GetFeature operation not available in: {}".format(wfs_url_getcap)
            else:
                logger.info("GetFeature available")
                pass

            if "DescribeFeatureType" not in wfs_dict.get("operations"):
                return 0, "DescribeFeatureType operation not available in: {}".format(wfs_url_getcap)
            else:
                logger.info("DescribeFeatureType available")
                pass

            # SRS definition
            available_crs_options = ["{}:{}".format(srs.authority, srs.code) for srs in wfs[layer_typename].crsOptions]

            srs = self.choose_appropriate_srs(crs_options=available_crs_options)

            # GetFeature URL
            wfs_lyr_url = wfs_dict.get("GetFeature_url")

            # url construction
            li_url_params = [
                "REQUEST=GetFeature",
                "SERVICE=WFS",
                "VERSION={}".format(wfs_dict.get("version")),
                "TYPENAME={}".format(layer_typename),
                "SRSNAME={}".format(srs),
            ]
            wfs_url_final = wfs_lyr_url + "&".join(li_url_params)

            logger.debug("*=====* DEBUG ADD FROM WFS : wfs_url_final --> {}".format(wfs_url_final))
            return ["WFS", layer_title, wfs_url_final]
        else:
            raise ValueError(
                "'mode' argument value should be 'quicky', 'complete', not {}".format(
                    mode
                )
            )

    def build_wms_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # check the service accessibility and store service informations
        if srv_details.get("path") not in self.cached_wms:
            check = self.check_ogc_service(
                service_type="WMS",
                service_url=srv_details.get("path"),
                service_version=srv_details.get("formatVersion"),
            )
            if check[0]:
                wms_dict = check[1]
            else:
                return check
        elif not self.cached_wms.get(srv_details.get("path")).get("reachable"):
            return (
                self.cached_wms.get(srv_details.get("path")).get("reachable"),
                self.cached_wms.get(srv_details.get("path")).get("error"),
            )
        else:
            wms_dict = self.cached_wms[srv_details.get("path")]

        # retrieve base url
        wms_url_base = wms_dict.get("base_url")

        # local variables
        api_layer_id = api_layer.get("id")

        # build layer title
        if len(api_layer.get("titles")):
            layer_title = api_layer.get("titles")[0].get("value", api_layer_id)
        else:
            layer_title = api_layer_id

        # build GetCapabilities url
        wms_url_getcap = wms_dict.get("getCap_url")

        # check if we can find the api_layer_id into wms service reachable layers typenames
        logger.debug("*=====* DEBUG ADD FROM WMS : layer_name --> {}".format(api_layer_id))
        logger.debug("*=====* DEBUG ADD FROM WMS : wms_dict --> {}".format(wms_dict))
        if api_layer_id not in wms_dict.get("typenames"):
            logger.error(
                "WMS {} - No typename found for {} layer, the layer may not be available anymore.".format(
                    srv_details.get("path"), api_layer_id
                )
            )
            return (
                0,
                "WMS - Layer '{}' not found in service {}".format(
                    api_layer_id, srv_details.get("path")
                ),
            )
        else:
            pass

        if mode == "quicky":
            # let's try a quick & dirty url build
            srs_map = plg_tools.get_map_crs()
            # url construction
            # just for QGIS server WMS
            if "&" in wms_url_base:
                li_params = [
                    "SERVICE=WMS",
                    "VERSION={}".format(wms_dict.get("version")),
                    "REQUEST=GetMap",
                    "layers={}".format(api_layer_id),
                    "crs={}".format(srs_map),
                    "format=image/png",
                    "styles="
                ]
                wms_url_quicky = wms_url_base + "&".join(li_params)
            # for other service servers
            else:
                wms_url_params = {
                    "SERVICE": "WMS",
                    "VERSION": wms_dict.get("version"),
                    "REQUEST": "GetMap",
                    "layers": api_layer_id,
                    "crs": srs_map,
                    "format": "image/png",
                    "styles": "",
                    "url": wms_url_base.split("?")[0] + "?",
                }
                wms_url_quicky = unquote(urlencode(wms_url_params, "utf8", quote_via=quote))
            # method ending
            btn_lbl = "WMS : {}".format(layer_title)
            return ["WMS", layer_title, wms_url_quicky, api_layer, srv_details, btn_lbl]

        elif mode == "complete":
            # Clean, complete but slower way - OWSLib -------------------------
            wms = wms_dict.get("WMS")
            # check if GetMap operation is available
            if not hasattr(wms, "getmap") or not wms_dict.get("GetMap_isAvailable"):
                return (
                    0,
                    "Required GetMap operation not available in: " + wms_url_getcap,
                )
            else:
                logger.info("GetMap available")
                pass

            # Format definition
            formats_image = [
                f for f in wms_dict.get("formatOptions") if f in qgis_wms_formats
            ]
            if "image/png" in formats_image:
                layer_format = "image/png"
            elif "image/jpeg" in formats_image:
                layer_format = "image/jpeg"
            else:
                layer_format = formats_image[0]

            # Style definition
            # lyr_style = list(wms[api_layer_id].styles.keys())[0]

            # GetMap URL
            wms_lyr_url = wms_dict.get("GetMap_url")

            # SRS definition
            srs = self.choose_appropriate_srs(crs_options=wms[api_layer_id].crsOptions)

            # url construction
            try:
                wms_url_params = {
                    "SERVICE": "WMS",
                    "VERSION": wms_dict.get("version"),
                    "REQUEST": "GetMap",
                    "layers": api_layer_id,
                    # "crs": srs,
                    "format": layer_format,
                    "styles": "",
                    # "styles": lyr_style,
                    "url": wms_lyr_url,
                }
                wms_url_final = unquote(urlencode(wms_url_params, "utf8"))
            except UnicodeEncodeError:
                wms_url_params = {
                    "SERVICE": "WMS",
                    "VERSION": wms_dict.get("version"),
                    "REQUEST": "GetMap",
                    "layers": api_layer_id.decode("latin1"),
                    "crs": srs,
                    "format": layer_format,
                    "styles": "",
                    # "styles": lyr_style,
                    "url": wms_lyr_url,
                }
                wms_url_final = unquote(urlencode(wms_url_params, "utf8"))
            logger.debug("*=====* DEBUG ADD FROM WMS : wms_url_final --> {}".format(str(wms_url_final)))
            # method ending
            return ["WMS", layer_title, wms_url_final]
        else:
            raise ValueError(
                "'mode' argument value should be 'quicky', 'complete', not {}".format(
                    mode
                )
            )

    def build_wmts_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Format the input WMTS URL to fit QGIS criterias.

        Retrieve GetCapabilities from information transmitted by Isogeo API
        to complete URL syntax.
        """
        # check the service accessibility and store service informations
        if srv_details.get("path") not in self.cached_wmts:
            check = self.check_ogc_service(
                service_type="WMTS",
                service_url=srv_details.get("path"),
                service_version=srv_details.get("formatVersion"),
            )
            if check[0]:
                wmts_dict = check[1]
            else:
                return check
        elif not self.cached_wmts.get(srv_details.get("path")).get("reachable"):
            return (
                self.cached_wmts.get(srv_details.get("path")).get("reachable"),
                self.cached_wmts.get(srv_details.get("path")).get("error"),
            )
        else:
            wmts_dict = self.cached_wmts[srv_details.get("path")]

        logger.debug("*=====* DEBUG ADD FROM WMTS : wmts_dict --> {}".format(wmts_dict))

        # local variables
        api_layer_id = api_layer.get("id")
        wmts = wmts_dict.get("WMTS")

        # check if GetTile operation is available
        if not hasattr(wmts, "gettile") or not wmts_dict.get("GetTile_isAvailable"):
            return 0, "Required GetTile operation not available in: " + wmts_dict.get("getCap_url")
        else:
            logger.debug("GetTile available")

        # check if we can find the api_layer_id into wmts service reachable layers typenames
        logger.debug("*=====* DEBUG ADD FROM WMTS : layer_name --> {}".format(api_layer_id))
        logger.debug("*=====* DEBUG ADD FROM WMTS : wmts_dict --> {}".format(wmts_dict))
        if api_layer_id not in wmts_dict.get("typenames"):
            logger.error(
                "WMTS {} - No typename found for {} layer, the layer may not be available anymore.".format(
                    srv_details.get("path"), api_layer_id
                )
            )
            return (
                0,
                "WMTS - Layer '{}' not found in service {}".format(
                    api_layer_id, srv_details.get("path")
                ),
            )
        else:
            wmts_lyr = wmts[api_layer_id]

        # build layer title
        if len(api_layer.get("titles")):
            layer_title = api_layer.get("titles")[0].get("value", "WMTS Layer")
        elif wmts_lyr.title:
            layer_title = wmts_lyr.title
        else:
            layer_title = "WMTS Layer"

        # retrieve Tile Matrix Set & SRS
        tms_dict = wmts_dict.get("wmts_tms")
        available_crs = [crs for crs, tms in tms_dict.items() if tms in wmts_lyr._tilematrixsets]
        srs = self.choose_appropriate_srs(available_crs)

        if srs:
            tile_matrix_set = tms_dict.get(srs)
        else:
            logger.debug("WMTS - Let's choose the SRS corresponding to the only available Tile Matrix Set for this layer")
            tile_matrix_set = wmts_lyr._tilematrixsets[0]
            srs = [k for k, v in tms_dict.items() if tile_matrix_set in v][0]

        # Format definition
        formats_image = wmts_lyr.formats
        if len(formats_image):
            if "image/png" in formats_image:
                layer_format = "image/png"
            elif "image/jpeg" in formats_image:
                layer_format = "image/jpeg"
            else:
                layer_format = formats_image[0]
        else:
            logger.debug("WMTS - No format specified, let's try with 'image/png'.")
            layer_format = "image/png"

        # Style definition
        if len(wmts_lyr.styles):
            lyr_style = list(wmts_lyr.styles.keys())[0]
        else:
            lyr_style = ""

        # GetTile URL
        wmts_lyr_url = wmts_dict.get("GetTile_url")

        # construct URL
        li_uri_params = [
            "crs={}&".format(srs),
            "format={}&".format(layer_format),
            "layers={}&".format(api_layer_id),
            "styles={}&".format(lyr_style),
            "tileMatrixSet={}&".format(tile_matrix_set),
            "url={}".format(wmts_lyr_url),
            quote("SERVICE=WMTS&"),
            quote("VERSION={}&".format(wmts.version)),
            quote("REQUEST=GetCapabilities"),
        ]
        wmts_url_final = "".join(li_uri_params)
        logger.debug("*=====* DEBUG ADD FROM WMTS : wmts_url_final --> {}".format(str(wmts_url_final)))

        # method ending
        return ["WMTS", layer_title, wmts_url_final, "", ""]

    def check_esri_service(
        self, service_type: str, service_url: str
    ):
        """Try to acces to the service from the given service_url and store the
        capabilities into cached_wfs dict.
        """
        logger.debug("*=====* DEBUG ADD FROM ESRI : service_url --> {}".format(str(service_url)))
        # If service_type argument value is invalid, raise error
        if service_type not in self.esri_infos_dict:
            raise ValueError(
                "'service_type' argument value should be one of {} not {}".format(
                    list(self.esri_infos_dict.keys()),
                    service_type
                )
            )
        # It it's valid, set local variables depending on it
        else:
            cache_dict = self.esri_infos_dict.get(service_type)[0]
            srs_entry_name = self.esri_infos_dict.get(service_type)[1]

        cache_dict[service_url] = {}
        service_dict = cache_dict[service_url]

        # retrieve, clean and store service base URL
        if service_url.endswith("/"):
            service_dict["base_url"] = service_url
        else:
            service_dict["base_url"] = service_url + "/"

        # build URL of "GetCapabilities" operation
        service_dict["getCap_url"] = service_dict["base_url"] + "?f=json"

        # sending "GetCapabilities" equivalent request
        try:
            getCap_request = requests.get(service_dict["getCap_url"])
            getCap_content = getCap_request.json()
            service_dict["reachable"] = 1
        except (requests.HTTPError, requests.Timeout, requests.ConnectionError) as e:
            error_msg = "{} {} - Server connection failure: {}".format(service_type, service_dict["getCap_url"], e)
            logger.error(error_msg)
            service_dict["reachable"] = 0
            service_dict["error"] = error_msg
            return service_dict["reachable"], service_dict["error"]
        except Exception as e:
            error_msg = "{} {} - Unable to access service capabilities: {}".format(service_type, service_dict["getCap_url"], e)
            logger.error(error_msg)
            service_dict["reachable"] = 0
            service_dict["error"] = error_msg
            return service_dict["reachable"], service_dict["error"]

        # retrieve appropriate srs from service capabilities
        try:
            service_dict["appropriate_srs"] = "EPSG:" + str(getCap_content.get("spatialReference").get(srs_entry_name))
        except Exception as e:
            warning_msg = "{} {} - Unable to retrieve information about appropriate srs from service capabilities: {}".format(
                service_type, service_dict["getCap_url"], e
            )
            logger.warning(warning_msg)
            service_dict["appropriate_srs"] = ""

        return 1, service_dict

    def build_efs_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input Esri Feature Service url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # check the service accessibility and store service informations
        if srv_details.get("path") not in self.cached_efs:
            check = self.check_esri_service(
                service_type="EFS",
                service_url=srv_details.get("path"),
            )
            if check[0]:
                efs_dict = check[1]
            else:
                return check
        elif not self.cached_efs.get(srv_details.get("path")).get("reachable"):
            return (
                self.cached_efs.get(srv_details.get("path")).get("reachable"),
                self.cached_efs.get(srv_details.get("path")).get("error"),
            )
        else:
            efs_dict = self.cached_efs[srv_details.get("path")]

        # retrieve layer id
        api_layer_id = api_layer.get("id")

        # build layer title
        if len(api_layer.get("titles")):
            efs_lyr_title = api_layer.get("titles")[0].get("value", "EFS Layer")
        else:
            efs_lyr_title = "EFS Layer"

        # retrieve and clean service efs_base_url
        efs_base_url = efs_dict.get("base_url")

        # retrieve appropriate srs
        srs = efs_dict.get("appropriate_srs")

        # build EFS layer URI
        efs_uri = "crs='{}' ".format(srs)
        efs_uri += "filter='' "
        efs_uri += "url='{}{}' ".format(efs_base_url, api_layer_id)
        efs_uri += "table'' "
        efs_uri += "sql=''"

        logger.debug("*=====* DEBUG ADD FROM EFS : efs_uri --> {}".format(str(efs_uri)))
        btn_lbl = "EFS : {}".format(efs_lyr_title)
        return ["EFS", efs_lyr_title, efs_uri, api_layer, srv_details, btn_lbl]

    def build_ems_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input Esri Map Service url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # check the service accessibility and store service informations
        if srv_details.get("path") not in self.cached_ems:
            check = self.check_esri_service(
                service_type="EMS",
                service_url=srv_details.get("path"),
            )
            if check[0]:
                ems_dict = check[1]
            else:
                return check
        elif not self.cached_ems.get(srv_details.get("path")).get("reachable"):
            return (
                self.cached_ems.get(srv_details.get("path")).get("reachable"),
                self.cached_ems.get(srv_details.get("path")).get("error"),
            )
        else:
            ems_dict = self.cached_ems[srv_details.get("path")]

        # retrieve layer id
        api_layer_id = api_layer.get("id")

        # build layer title
        if len(api_layer.get("titles")):
            ems_lyr_title = api_layer.get("titles")[0].get("value", "EMS Layer")
        else:
            ems_lyr_title = "EMS Layer"

        # retrieve and clean service ems_base_url
        ems_base_url = ems_dict.get("base_url")

        # retrieve appropriate srs
        srs = ems_dict.get("appropriate_srs")

        # build EMS layer URI
        ems_uri = QgsDataSourceUri()
        ems_uri.setParam("url", ems_base_url)
        ems_uri.setParam("layer", api_layer_id)
        ems_uri.setParam("crs", srs)

        logger.debug("*=====* DEBUG ADD FROM EMS : ems_uri --> {}".format(str(ems_uri)))
        btn_lbl = "EMS : {}".format(ems_lyr_title)
        return ["EMS", ems_lyr_title, ems_uri.uri(), api_layer, srv_details, btn_lbl]
