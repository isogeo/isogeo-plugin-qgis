# -*- coding: utf-8 -*-
#! python3  # noqa: E265

# Standard library
import logging
import re

# from urllib.request import unquote
from urllib.parse import urlencode, unquote

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

    def check_ogc_service(
        self, service_type: str, service_url: str, service_version: str
    ):
        """Try to acces to the service from the given service_url and store the
        capabilities into cached_wfs dict.
        """
        # Set local variables depending on service type
        if service_type == "WFS":
            cache_dict = self.cached_wfs
            main_op_name = "GetFeature"
            service_connector = WebFeatureService
        elif service_type == "WMS":
            cache_dict = self.cached_wms
            main_op_name = "GetMap"
            service_connector = WebMapService
        elif service_type == "WMTS":
            cache_dict = self.cached_wmts
            main_op_name = "GetMap"
            service_connector = WebMapTileService
        else:
            raise ValueError(
                "'service_type' argument value should be 'WFS', 'WMS' or 'WMTS', not {}".format(
                    service_type
                )
            )

        cache_dict[service_url] = {}

        # Basic checks on service reachability
        try:
            service = service_connector(url=service_url, version=service_version)
            cache_dict[service_url]["reachable"] = 1
        except ServiceException as e:
            logger.error(str(e))
            cache_dict[service_url]["reachable"] = 0
            cache_dict[service_url]["error"] = "{} - Bad operation ({}): {}".format(
                service_type, service_url, str(e)
            )
            return (
                cache_dict[service_url]["reachable"],
                cache_dict[service_url]["error"],
            )
        except HTTPError as e:
            logger.error(str(e))
            cache_dict[service_url]["reachable"] = 0
            cache_dict[service_url][
                "error"
            ] = "{} - Service ({}) not reached: {}".format(
                service_type, service_url, str(e)
            )
            return (
                cache_dict[service_url]["reachable"],
                cache_dict[service_url]["error"],
            )
        except Exception as e:
            cache_dict[service_url]["reachable"] = 0
            cache_dict[service_url][
                "error"
            ] = "{} - Connection to service ({}) failed: {}".format(
                service_type, service_url, str(e)
            )
            return (
                cache_dict[service_url]["reachable"],
                cache_dict[service_url]["error"],
            )

        # Store several informations about the service
        cache_dict[service_url][service_type] = service
        cache_dict[service_url]["typenames"] = list(service.contents.keys())
        cache_dict[service_url]["version"] = service.version
        cache_dict[service_url]["operations"] = [op.name for op in service.operations]

        if service_url.endswith("?"):
            cache_dict[service_url]["base_url"] = service_url
        else:
            cache_dict[service_url]["base_url"] = service_url + "?"

        cache_dict[service_url]["getCap_url"] = (
            cache_dict[service_url]["base_url"]
            + "request=GetCapabilities&service="
            + service_type
        )

        main_op_key = "{}_url".format(main_op_name)
        if service.getOperationByName(main_op_name).methods[0].get("url").endswith("?"):
            cache_dict[service_url][main_op_key] = (
                service.getOperationByName(main_op_name).methods[0].get("url")
            )
        else:
            cache_dict[service_url][main_op_key] = (
                service.getOperationByName(main_op_name).methods[0].get("url") + "?"
            )

        cache_dict[service_url]["formatOptions"] = [
            f.split(";", 1)[0]
            for f in service.getOperationByName(main_op_name).formatOptions
        ]

        return 1, cache_dict[service_url]

    def check_wfs(self, service_url: str, service_version: str):
        """Try to acces to the service from the given service_url and store the
        capabilities into cached_wfs dict.
        """
        self.cached_wfs[service_url] = {}

        # basic checks on service url
        try:
            wfs = WebFeatureService(url=service_url, version=service_version)
            self.cached_wfs[service_url]["reachable"] = 1
        except ServiceException as e:
            logger.error(str(e))
            self.cached_wfs[service_url]["reachable"] = 0
            self.cached_wfs[service_url][
                "error"
            ] = "WFS - Bad operation ({}): {}".format(service_url, str(e))
            return (
                self.cached_wfs[service_url]["reachable"],
                self.cached_wfs[service_url]["error"],
            )
        except HTTPError as e:
            logger.error(str(e))
            self.cached_wfs[service_url]["reachable"] = 0
            self.cached_wfs[service_url][
                "error"
            ] = "WFS - Service ({}) not reached: {}".format(service_url, str(e))
            return (
                self.cached_wfs[service_url]["reachable"],
                self.cached_wfs[service_url]["error"],
            )
        except Exception as e:
            self.cached_wfs[service_url]["reachable"] = 0
            self.cached_wfs[service_url][
                "error"
            ] = "WFS - Connection to service ({}) failed: {}".format(
                service_url, str(e)
            )
            return (
                self.cached_wfs[service_url]["reachable"],
                self.cached_wfs[service_url]["error"],
            )

        self.cached_wfs[service_url]["wfs"] = wfs
        self.cached_wfs[service_url]["typenames"] = list(wfs.contents.keys())
        self.cached_wfs[service_url]["version"] = wfs.version
        self.cached_wfs[service_url]["operations"] = [op.name for op in wfs.operations]

        return 1, self.cached_wfs[service_url]

    def check_wms(self, service_url: str, service_version: str):
        """Try to acces to the service from the given service_url and store the
        capabilities into cached_wms dict.
        """
        self.cached_wms[service_url] = {}

        # basic checks on service url
        try:
            wms = WebMapService(url=service_url, version=service_version)
            self.cached_wms[service_url]["reachable"] = 1
        except ServiceException as e:
            logger.error(str(e))
            self.cached_wms[service_url]["reachable"] = 0
            self.cached_wms[service_url][
                "error"
            ] = "WMS - Bad operation ({}): {}".format(service_url, str(e))
            return (
                self.cached_wms[service_url]["reachable"],
                self.cached_wms[service_url]["error"],
            )
        except HTTPError as e:
            logger.error(str(e))
            self.cached_wms[service_url]["reachable"] = 0
            self.cached_wms[service_url][
                "error"
            ] = "WMS - Service ({}) not reached: {}".format(service_url, str(e))
            return (
                self.cached_wms[service_url]["reachable"],
                self.cached_wms[service_url]["error"],
            )
        except Exception as e:
            self.cached_wms[service_url]["reachable"] = 0
            self.cached_wms[service_url][
                "error"
            ] = "WMS - Connection to service ({}) failed: {}".format(
                service_url, str(e)
            )
            return (
                self.cached_wms[service_url]["reachable"],
                self.cached_wms[service_url]["error"],
            )

        # Store several informations about the service
        self.cached_wms[service_url]["wms"] = wms
        self.cached_wms[service_url]["typenames"] = list(wms.contents.keys())
        self.cached_wms[service_url]["version"] = wms.version
        self.cached_wms[service_url]["operations"] = [op.name for op in wms.operations]

        if service_url.endswith("?"):
            self.cached_wms[service_url]["base_url"] = service_url
        else:
            self.cached_wms[service_url]["base_url"] = service_url + "?"

        self.cached_wms[service_url]["getCap_url"] = (
            self.cached_wms[service_url]["base_url"]
            + "request=GetCapabilities&service=WMS"
        )

        if wms.getOperationByName("GetMap").methods[0].get("url").endswith("?"):
            self.cached_wms[service_url]["getMap_url"] = (
                wms.getOperationByName("GetMap").methods[0].get("url")
            )
        else:
            self.cached_wms[service_url]["getMap_url"] = (
                wms.getOperationByName("GetMap").methods[0].get("url") + "?"
            )

        self.cached_wms[service_url]["formatOptions"] = [
            f.split(";", 1)[0] for f in wms.getOperationByName("GetMap").formatOptions
        ]

        return 1, self.cached_wms[service_url]

    def build_efs_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input Esri Feature Service url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        logger.debug("*=====* DEBUG ADD FROM EFS : api_layer --> {}".format(api_layer))
        logger.debug(
            "*=====* DEBUG ADD FROM EFS : srv_details --> {}".format(srv_details)
        )
        srs_map = plg_tools.get_map_crs()
        layer_name = api_layer.get("id")

        efs_lyr_title = "EFS Layer"
        if len(api_layer.get("titles")):
            efs_lyr_title = api_layer.get("titles")[0].get("value", "EFS Layer")
        else:
            pass

        if srv_details.get("path").endswith("/"):
            efs_lyr_url = srv_details.get("path")
        else:
            efs_lyr_url = srv_details.get("path") + "/"

        efs_url = efs_lyr_url + layer_name

        btn_lbl = "EFS : {}".format(efs_lyr_title)
        return ["EFS", efs_lyr_title, efs_url, api_layer, srv_details, btn_lbl]

    def build_ems_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input Esri Map Service url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        srs_map = plg_tools.get_map_crs()
        layer_name = api_layer.get("id")

        ems_lyr_title = "EMS Layer"
        if len(api_layer.get("titles")):
            ems_lyr_title = api_layer.get("titles")[0].get("value", "EMS Layer")
        else:
            pass

        ems_lyr_url = str(srv_details.get("path"))

        ems_uri = QgsDataSourceUri()
        ems_uri.setParam("url", ems_lyr_url)
        ems_uri.setParam("layer", layer_name)
        ems_uri.setParam("crs", srs_map)
        # ems_uri.setParam("restrictToRequestBBOX", "1")

        btn_lbl = "EMS : {}".format(ems_lyr_title)
        return ["EMS", ems_lyr_title, ems_uri.uri(), api_layer, srv_details, btn_lbl]

    def build_wfs_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # chef the service accessibility and retrieve informations
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
        wms_url_base = wfs_dict.get("base_url")

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
        logger.debug(
            "*=====* DEBUG ADD FROM WFS : layer_name --> {}".format(api_layer_name)
        )
        logger.debug(
            "*=====* DEBUG ADD FROM WFS : typenames --> {}".format(
                wfs_dict.get("typenames")
            )
        )
        logger.debug("*=====* DEBUG ADD FROM WFS : wfs_dict --> {}".format(wfs_dict))

        layer_typename = [
            wfs_typename
            for wfs_typename in wfs_dict.get("typenames")
            if api_layer_name in wfs_typename
        ]
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
            return (
                0,
                "WFS - Layer '{}' not found in service {}".format(
                    api_layer_name, srv_details.get("path")
                ),
            )

        logger.debug(
            "*=====* DEBUG ADD FROM WFS : layer_typename --> {}".format(layer_typename)
        )

        if mode == "quicky":
            li_url_params = [
                "REQUEST=GetFeatures",
                "SERVICE=WFS",
                "VERSION={}".format(wfs_dict.get("version")),
                "TYPENAME={}".format(layer_typename),
            ]

            wfs_url_quicky = wfs_url_base + "&".join(li_url_params)
            logger.debug(
                "*=====* DEBUG ADD FROM WFS : wfs_url_quicky --> {}".format(
                    wfs_url_quicky
                )
            )

            btn_lbl = "WFS : {}".format(layer_title)
            return ["WFS", layer_title, wfs_url_quicky, api_layer, srv_details, btn_lbl]
        elif mode == "complete":
            # Clean, complete but slower way - OWSLib -------------------------
            wfs = wfs_dict.get("WFS")
            # check if GetFeature and DescribeFeatureType operation are available
            if not hasattr(wfs, "getfeature") or "GetFeature" not in wfs_dict.get(
                "operations"
            ):
                return (
                    0,
                    "Required GetFeature operation not available in: " + wfs_url_getcap,
                )
            else:
                logger.info("GetFeature available")
                pass

            if "DescribeFeatureType" not in wfs_dict.get("operations"):
                return (
                    0,
                    "Required DescribeFeatureType operation not available in: "
                    + wfs_url_getcap,
                )
            else:
                logger.info("DescribeFeatureType available")
                pass

            wfs_lyr = wfs[layer_typename]

            # SRS definition
            srs_map = plg_tools.get_map_crs()
            srs_lyr_new = qsettings.value("/Projections/defaultBehaviour")
            srs_lyr_crs = qsettings.value("/Projections/layerDefaultCrs")
            srs_qgs_new = qsettings.value("/Projections/projectDefaultCrs")
            srs_qgs_otf_on = qsettings.value("/Projections/otfTransformEnabled")
            srs_qgs_otf_auto = qsettings.value("/Projections/otfTransformAutoEnable")

            # DEV
            # print("CRS: ", wms_lyr.crsOptions,
            #       "For new layers: " + srs_lyr_new + srs_lyr_crs,
            #       "For new projects: " + srs_qgs_new,
            #       "OTF enabled: " + srs_qgs_otf_on,
            #       "OTF smart enabled: " + srs_qgs_otf_auto,
            #       "Map canvas SRS:" + plg_tools.get_map_crs())

            wfs_lyr_crs_epsg = [
                "{}:{}".format(srs.authority, srs.code) for srs in wfs_lyr.crsOptions
            ]
            if srs_map in wfs_lyr_crs_epsg:
                logger.debug("It's a SRS match! With map canvas: " + srs_map)
                srs = srs_map
            elif (
                srs_qgs_new in wfs_lyr_crs_epsg
                and srs_qgs_otf_on == "false"
                and srs_qgs_otf_auto == "false"
            ):
                logger.debug(
                    "It's a SRS match! With default new project: " + srs_qgs_new
                )
                srs = srs_qgs_new
            elif srs_lyr_crs in wfs_lyr_crs_epsg and srs_lyr_new == "useGlobal":
                logger.debug("It's a SRS match! With default new layer: " + srs_lyr_crs)
                srs = srs_lyr_crs
            elif "EPSG:4326" in wfs_lyr_crs_epsg:
                logger.debug("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                srs = "EPSG:4326"
            else:
                logger.debug("Map Canvas SRS not available within service CRS.")
                srs = wfs_lyr_crs_epsg[0]

            # Style definition
            # print("Styles: ", wms_lyr.styles, type(wms_lyr.styles))
            # lyr_style = wfs_lyr.styles.keys()[0]
            # print(lyr_style)

            # GetFeature URL
            wfs_dict.get("GetFeature_url")

            # url construction
            li_url_params = [
                "REQUEST=GetFeatures",
                "SERVICE=WFS",
                "VERSION={}".format(wfs_dict.get("version")),
                "TYPENAME={}".format(layer_typename),
                "SRSNAME={}".format(srs),
            ]
            wfs_url_final = wfs_lyr_url + "&".join(li_url_params)
            # method ending
            logger.debug(
                "*=====* DEBUG ADD FROM WFS : wfs_url_final --> {}".format(
                    wfs_url_final
                )
            )
            return ["WFS", layer_title, wfs_url_final]
        else:
            return None

    def build_wms_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        # chef the service accessibility and store service informations
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
        logger.debug(
            "*=====* DEBUG ADD FROM WMS : layer_name --> {}".format(api_layer_id)
        )
        logger.debug(
            "*=====* DEBUG ADD FROM WMS : typenames --> {}".format(
                wms_dict.get("typenames")
            )
        )
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
            wms_url_params = {
                "SERVICE": "WMS",
                "VERSION": wms_dict.get("version"),
                "REQUEST": "GetMap",
                "layers": api_layer_id,
                "crs": srs_map,
                "format": "image/png",
                "styles": "",
                "url": wms_url_base,
            }
            wms_url_quicky = unquote(urlencode(wms_url_params, "utf8"))
            logger.debug(
                "*=====* DEBUG ADD FROM WMS : wfs_url_quicky --> {}".format(
                    wms_url_quicky
                )
            )
            # prevent encoding errors (#102)
            btn_lbl = "WMS : {}".format(layer_title)
            return ["WMS", layer_title, wms_url_quicky, api_layer, srv_details, btn_lbl]

        elif mode == "complete":
            # Clean, complete but slower way - OWSLib -------------------------
            wms = wms_dict.get("WMS")
            # check if GetMap operation is available
            if not hasattr(wms, "getmap") or "GetMap" not in wms_dict.get("operations"):
                return (
                    0,
                    "Required GetMap operation not available in: " + wms_url_getcap,
                )
            else:
                logger.info("GetMap available")
                pass

            wms_lyr = wms[api_layer_id]

            # SRS definition
            srs_map = plg_tools.get_map_crs()
            srs_lyr_new = qsettings.value("/Projections/defaultBehaviour")
            srs_lyr_crs = qsettings.value("/Projections/layerDefaultCrs")
            srs_qgs_new = qsettings.value("/Projections/projectDefaultCrs")
            srs_qgs_otf_on = qsettings.value("/Projections/otfTransformEnabled")
            srs_qgs_otf_auto = qsettings.value("/Projections/otfTransformAutoEnable")

            # DEV
            # print("CRS: ", wms_lyr.crsOptions,
            #       "For new layers: " + srs_lyr_new + srs_lyr_crs,
            #       "For new projects: " + srs_qgs_new,
            #       "OTF enabled: " + srs_qgs_otf_on,
            #       "OTF smart enabled: " + srs_qgs_otf_auto,
            #       "Map canvas SRS:" + plg_tools.get_map_crs())
            if srs_map in wms_lyr.crsOptions:
                logger.debug("It's a SRS match! With map canvas: " + srs_map)
                srs = srs_map
            elif (
                srs_qgs_new in wms_lyr.crsOptions
                and srs_qgs_otf_on == "false"
                and srs_qgs_otf_auto == "false"
            ):
                logger.debug(
                    "It's a SRS match! With default new project: " + srs_qgs_new
                )
                srs = srs_qgs_new
            elif srs_lyr_crs in wms_lyr.crsOptions and srs_lyr_new == "useGlobal":
                logger.debug("It's a SRS match! With default new layer: " + srs_lyr_crs)
                srs = srs_lyr_crs
            elif "EPSG:4326" in wms_lyr.crsOptions:
                logger.debug("It's a SRS match! With standard WGS 84 (EPSG:4326)")
                srs = "EPSG:4326"
            else:
                logger.debug("Map Canvas SRS not available within service CRS.")
                srs = wms_lyr.crsOptions[0]

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
            # lyr_style = list(wms_lyr.styles.keys())[0]

            # GetMap URL
            wms_lyr_url = wms_dict.get("GetMap_url")

            # url construction
            try:
                wms_url_params = {
                    "SERVICE": "WMS",
                    "VERSION": wms_dict.get("version"),
                    "REQUEST": "GetMap",
                    "layers": api_layer_id,
                    "crs": srs,
                    "format": layer_format,
                    "styles": "",
                    # "styles": lyr_style,
                    # "url": srv_details.get("path"),
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
                    # "url": srv_details.get("path"),
                    "url": wms_lyr_url,
                }
                wms_url_final = unquote(urlencode(wms_url_params, "utf8"))
            # method ending
            return ["WMS", layer_title, wms_url_final]
        else:
            return None

    def build_wmts_url(
        self, api_layer, srv_details, rsc_type="ds_dyn_lyr_srv", mode="complete"
    ):
        """Format the input WMTS URL to fit QGIS criterias.

        Retrieve GetCapabilities from information transmitted by Isogeo API
        to complete URL syntax.
        """
        # local variables
        layer_name = api_layer.get("id")

        layer_title = "WMTS Layer"
        if len(api_layer.get("titles")):
            layer_title = api_layer.get("titles")[0].get("value", "WMTS Layer")
        else:
            pass

        wmts_url_getcap = (
            srv_details.get("path") + "?request=GetCapabilities&service=WMTS"
        )
        # basic checks on service url
        try:
            wmts = WebMapTileService(wmts_url_getcap)
        except TypeError as e:
            logger.error("WMTS - OWSLib mixing str and unicode args :{}".format(e))
        except ServiceException as e:
            logger.error(e)
            return 0, "WMTS - Bad operation ({}): {}".format(wmts_url_getcap, str(e))
        except HTTPError as e:
            logger.error(e)
            return (
                0,
                "WMS - Service ({}) not reached: {}".format(wmts_url_getcap, str(e)),
            )
        except Exception as e:
            logger.error("WMTS - {}: {}".format(wmts_url_getcap, e))
            return (
                0,
                "WMS - Service ({}) not reached: {}".format(wmts_url_getcap, str(e)),
            )

        # check if GetTile operation is available
        if not hasattr(wmts, "gettile") or "GetTile" not in [
            op.name for op in wmts.operations
        ]:
            return 0, "Required GetTile operation not available in: " + wmts_url_getcap
        else:
            logger.debug("GetTile available")
            pass

        # check if layer is present and queryable
        try:
            wmts_lyr = wmts[layer_name]
            layer_title = wmts_lyr.title
            layer_id = wmts_lyr.id
        except KeyError as e:
            logger.error(
                "Layer {} not found in WMTS service: {}".format(
                    layer_name, wmts_url_getcap
                )
            )
            return (
                0,
                "Layer {} not found in WMS service: {}".format(
                    layer_name, wmts_url_getcap
                ),
                e,
            )

        # Tile Matrix Set & SRS
        srs_map = plg_tools.get_map_crs()
        def_tile_matrix_set = wmts_lyr.tilematrixsets[0]
        if srs_map in wmts_lyr.tilematrixsets:
            logger.debug("WMTS - It's a SRS match! With map canvas: " + srs_map)
            tile_matrix_set = wmts.tilematrixsets.get(srs_map).identifier
            srs = srs_map
        elif "EPSG:4326" in wmts_lyr.tilematrixsets:
            logger.debug("WMTS - It's a SRS match! With standard WGS 84 (4326)")
            tile_matrix_set = wmts.tilematrixsets.get("EPSG:4326").identifier
            srs = "EPSG:4326"
        elif "EPSG:900913" in wmts_lyr.tilematrixsets:
            logger.debug("WMTS - It's a SRS match! With Google (900913)")
            tile_matrix_set = wmts.tilematrixsets.get("EPSG:900913").identifier
            srs = "EPSG:900913"
        else:
            logger.debug("WMTS - Searched SRS not available within service CRS.")
            tile_matrix_set = wmts.tilematrixsets.get(def_tile_matrix_set).identifier
            srs = tile_matrix_set

        # Format definition
        wmts_lyr_formats = wmts.getOperationByName("GetTile").formatOptions
        formats_image = [
            f.split(" ", 1)[0] for f in wmts_lyr_formats if f in qgis_wms_formats
        ]
        if len(formats_image):
            if "image/png" in formats_image:
                layer_format = "image/png"
            elif "image/jpeg" in formats_image:
                layer_format = "image/jpeg"
            else:
                layer_format = formats_image[0]
        else:
            logger.debug("WMTS - No format available among preferred by QGIS.")
            layer_format = "image/png"

        # Style definition
        # lyr_style = wmts_lyr.styles.keys()[0]

        # GetTile URL
        wmts_lyr_url = wmts.getOperationByName("GetTile").methods
        wmts_lyr_url = wmts_lyr_url[0].get("url")
        if wmts_lyr_url[-1] == "&":
            wmts_lyr_url = wmts_lyr_url[:-1]
        else:
            pass

        # construct URL
        wmts_url_params = {
            "SERVICE": "WMTS",
            "VERSION": "1.0.0",
            "REQUEST": "GetCapabilities",
            "layers": layer_id,
            "crs": srs,
            "format": layer_format,
            "styles": "",
            "tileMatrixSet": tile_matrix_set,
            "url": wmts_lyr_url,
        }
        wmts_url_final = unquote(urlencode(wmts_url_params, "utf8"))
        logger.debug(wmts_url_final)

        # method ending
        return ["WMTS", layer_title, wmts_url_final, "", ""]
        # return QgsRasterLayer(wms_url_final, layer_title, 'wms')
