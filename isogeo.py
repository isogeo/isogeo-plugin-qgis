# -*- coding: utf-8 -*-
#! python3  # noqa: E265

"""
/***************************************************************************
 Isogeo
                                 A QGIS plugin
 Isogeo search engine within QGIS
                              -------------------
        begin                : 2016-07-22
        git sha              : $Format:%H$
        copyright            : (C) by Isogeo
        email                : projects+qgis@isogeo.com
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

# Standard library
from pathlib import Path
import platform

import logging
from logging.handlers import RotatingFileHandler
from functools import partial

# PyQT
from qgis.PyQt.QtCore import QCoreApplication, Qt, QTranslator

from qgis.PyQt.QtWidgets import QAction, QComboBox, QDesktopWidget, QProgressBar
from qgis.PyQt.QtGui import QIcon

# PyQGIS
from qgis.utils import iface, plugin_times
from qgis.core import QgsCoordinateReferenceSystem, QgsMessageLog, QgsRectangle, QgsProject


try:
    from qgis.core import Qgis
except ImportError:
    from qgis.core import QGis as Qgis

# Initialize Qt resources from file resources.py
from .resources_rc import *  # noqa: F401, F403

# UI classes
from .ui.credits.dlg_credits import IsogeoCredits

# submodule
from .modules import (
    Authenticator,
    ApiRequester,
    MetadataDisplayer,
    IsogeoPlgTools,
    SharesParser,
    SearchFormManager,
    UserInformer,
    SettingsManager
)

# ############################################################################
# ########## Globals ###############
# ##################################

# plugin directory path
plg_basepath = Path(__file__).parent
plg_reg_name = plg_basepath.name
# QGIS useful tooling and shortcuts
msgBar = iface.messageBar()

# required `_log` subfolder
plg_logdir = Path(plg_basepath) / "_logs"
if not plg_logdir.exists():
    plg_logdir.mkdir()
else:
    pass

# plugin internal submodules
plg_tools = IsogeoPlgTools()

# -- LOG FILE --------------------------------------------------------
# log level depends on plugin directory name
if plg_reg_name == plg_tools.plugin_metadata(base_path=plg_basepath, value="name"):
    log_level = logging.WARNING
elif "beta" in plg_tools.plugin_metadata(base_path=plg_basepath) or "dev" in plg_reg_name:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

logger = logging.getLogger("IsogeoQgisPlugin")

logger.setLevel(log_level)
log_form = logging.Formatter(
    "%(asctime)s || %(levelname)s " "|| %(module)s - %(lineno)d ||" " %(funcName)s || %(message)s"
)
logfile_path = Path(plg_logdir) / "log_isogeo_plugin.log"
logfile = RotatingFileHandler(logfile_path, "a", 5000000, 1, encoding="utf-8")
logfile.setLevel(log_level)
logfile.setFormatter(log_form)
logger.addHandler(logfile)

# icons
ico_log = QIcon(":/images/themes/default/mActionFolder.svg")
ico_pgis = QIcon(":/images/themes/default/mIconPostgis.svg")
ico_ora = QIcon(":/images/themes/default/mIconOracle.svg")


# ############################################################################
# ########## Classes ###############
# ##################################


class Isogeo:
    """Isogeo plugin for QGIS LTR."""

    # attributes
    plg_version = plg_tools.plugin_metadata(base_path=plg_basepath)

    logger.info("\n\n\t========== Isogeo Search Engine for QGIS ==========")
    logger.info("OS: {0}".format(platform.platform()))
    logger.info("QGIS Version: {0}".format(Qgis.QGIS_VERSION))
    logger.info("Python version: {0}".format(platform.python_version()))
    logger.info("Plugin version: {0}".format(plg_version))
    logger.info("Log level: {0}".format(log_level))

    # Screens resolution
    screens_count = QDesktopWidget().screenCount()
    for screenNbr in range(screens_count):
        sizeObject = QDesktopWidget().screenGeometry(screenNbr)
        logger.info(
            "Screen: {}/{} - Size: {}x{}".format(
                screenNbr + 1, screens_count, sizeObject.height(), sizeObject.width()
            )
        )
    del screens_count
    del sizeObject

    def __init__(self, iface):
        """Constructor.

        :param QgsInterface iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = Path(__file__).parent

        # required `_auth` subfolder
        plg_authdir = Path(plg_basepath) / "_auth"
        if not plg_authdir.exists():
            plg_authdir.mkdir()
        else:
            pass

        # required `_user` subfolder
        plg_userdir = Path(plg_basepath) / "_user"
        if not plg_userdir.exists():
            plg_userdir.mkdir()
        else:
            pass

        self.settings_mng = SettingsManager()
        self.settings_mng.tr = self.tr
        # initialize locale
        translator = QTranslator()
        locale = self.settings_mng.get_locale()
        self.lang = locale[:2]
        i18n_folder_path = self.plugin_dir / "i18n"
        if (i18n_folder_path / f"isogeo_search_engine_{locale}.qm").exists():
            i18n_file_suffix = locale
        elif (i18n_folder_path / f"isogeo_search_engine_{self.lang}.qm").exists():
            i18n_file_suffix = self.lang
        else:
            logger.warning(f"No translation file found for '{locale}' locale value, 'en' will be used.")
            i18n_file_suffix = "en"
        i18n_file_path = i18n_folder_path / f"isogeo_search_engine_{i18n_file_suffix}.qm"
        translator.load(str(i18n_file_path))
        QCoreApplication.installTranslator(translator)
        logger.info("Language applied to front: {}".format(i18n_file_suffix))

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&Isogeo")
        self.toolbar = self.iface.addToolBar("Isogeo")
        self.toolbar.setObjectName("Isogeo")
        self.pluginIsActive = False
        self.form_mng = None

        # UI submodules
        self.credits_dialog = IsogeoCredits()

        # SUBMODULES
        # self.settings_mng.load_config()

        # instantiating
        self.informer = UserInformer(message_bar=msgBar)

        self.authenticator = Authenticator(settings_manager=self.settings_mng)

        self.approps_mng = SharesParser(app_base_url=self.settings_mng.config_content.get("app_base_url"))
        self.approps_mng.tr = self.tr

        self.md_display = MetadataDisplayer(settings_manager=self.settings_mng)
        self.md_display.tr = self.tr

        self.api_requester = ApiRequester()
        self.api_requester.tr = self.tr

        self.form_mng = SearchFormManager(trad=self.tr, settings_manager=self.settings_mng)
        self.form_mng.qs_mng.url_builder = self.api_requester.build_request_url

        # connecting
        self.api_requester.api_sig.connect(self.token_slot)
        self.api_requester.api_sig.connect(self.informer.request_slot)
        self.api_requester.search_sig.connect(self.search_slot)
        self.api_requester.details_sig.connect(self.md_display.show_complete_md)
        self.api_requester.shares_sig.connect(self.approps_mng.send_share_info)

        self.authenticator.auth_sig.connect(self.auth_slot)
        self.authenticator.ask_shares.connect(self.shares_slot)

        self.approps_mng.shares_ready.connect(self.write_shares_info)
        self.approps_mng.shares_ready.connect(self.informer.shares_slot)

        # start variables
        self.savedSearch = str
        self.loopCount = 0
        self.hardReset = False
        self.showResult = False
        self.showDetails = False
        self.store = False

        self.old_text = ""
        self.page_index = 1

    # noinspection PyMethodMayBeStatic
    def tr(self, message, context="Isogeo"):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.
        :param message: String for translation.
        :type message: str, QString
        :context: str, QString
        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate(context, message)

    def add_action(
        self,
        ico_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param str icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :param str text: Text that should be shown in menu items for this action.
        :param function callback: Function to be called when the action is triggered.
        :param bool enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :param bool add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :param bool add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :param str status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :param QWidget parent: Parent widget for the new action. Defaults None.
        :param str whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        ico = QIcon(ico_path)
        action = QAction(ico, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setToolTip("Isogeo (v{})".format(self.plg_version))

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        ico_path = ":/plugins/Isogeo/icon.png"
        self.add_action(
            ico_path,
            text=self.tr("Search within Isogeo catalogs"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

    # -------------------------------------------------------------------------
    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed."""
        # delete geoservices cache
        self.form_mng.results_mng.cache_mng.clean_geoservice_cache()
        # disconnects
        self.form_mng.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe when closing the docked window:
        self.form_mng = None
        self.pluginIsActive = False
        # stop log file stream
        logging.shutdown()

        del self

    def unload(self):
        """Remove the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(self.tr("&Isogeo"), action)
            try:
                self.iface.mainWindow().statusBar().removeWidget(self.bar)
            except Exception:
                pass
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # --- AUTHENTICATION ------------------------------------------------------
    def user_authentication(self):
        """Test the validity of the user id and secret.
        This is the first major function the plugin calls when executed. It
        retrieves the id and secret from the config file. If they are set to
        their default value, it asks for them.
        If not, it tries to send a request.
        """
        self.savedSearch = "first"
        self.form_mng.switch_widgets_on_and_off(0)
        api_init = self.authenticator.manage_api_initialization()
        if api_init[0]:
            self.api_requester.setup_api_params(api_init[1])
        else:
            pass

    def auth_slot(self, auth_signal: str):
        if auth_signal == "ok":
            self.user_authentication()
        else:
            self.authenticator.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(False)
            pass

    def token_slot(self, token_signal: str):
        """Slot connected to ApiRequester.api_sig signal emitted when a response to
        a token request has been received from Isogeo's API or when the content of
        a response to any type of request can't be parsed. The 'api_sig' parameter
        correspond to the string passed by ApiRequester.handle_reply method (see
        modules/api/request.py). The value of this parameter depend on the response's
        content received from Isogeo's API.

        :param str token_signal: a string passed by the signal whose value determines
        what will be done. Options :
            - "ok" : Authentication has succeeded, the token is stored so it sends
            a search request to the API.
            - "creds_issue" : User's credentials are wrong so it displays the authentication
            form to provide good ones.
            - "NoInternet" : Asks to user to check his Internet connection.
        """
        if token_signal == "ok":
            if self.savedSearch == "first":
                logger.debug("First search since plugin started.")
                self.authenticator.first_auth = False
                self.shares_slot()
            else:
                self.api_requester.send_request()

        elif token_signal == "creds_issue":
            self.authenticator.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(False)
        else:
            self.pluginIsActive = False

    def shares_slot(self):
        logger.debug("Asking application properties to the Isogeo API.")
        self.api_requester.send_request(request_type="shares")

    # --- SEARCH --------------------------------------------------------------
    def search(self, show: bool = False, page_change: int = 0):
        """Slot connected to signals emitted by 'advances search', 'order' or
        'keywords' comboboxes, also by 'show results', 'next page' or 'previous
        page' buttons when a user interacts with one of them. It retrieves the
        selected parameters and establishes the corresponding URL, and then sends
        a search request to the API, by calling ApiRequester.send_request().

        :param bool show: True if the 'show results', 'next page' or 'previous page'
        button was pressed
        :param int page_change: -1 if 'previous page' button was pressed, 1 if
        'next page' button was pressed, 0 otherwise
        """
        logger.debug("Search function called. Building the url that is to be sent to the API")
        # Disabling all user inputs during the search function is running
        self.form_mng.switch_widgets_on_and_off(0)

        if self.store is True:
            # Store the previous search
            name = self.tr("Last search")
            self.form_mng.qs_mng.write_params(name, "Last")
            # update quick searches combobox
            self.form_mng.pop_qs_cbbs(items_list=self.form_mng.qs_mng.get_quicksearches_names())
            self.store = False
        else:
            pass

        # STORING ALL THE INFORMATIONS NEEDED TO BUILD THE URL
        # Widget position
        params = self.form_mng.save_params()
        # Info for _limit parameter
        if show is True:
            # Adding the loading bar
            self.add_loading_bar()
            self.showResult = True
            params["show"] = True
        else:
            params["show"] = False
        # Info for _offset parameter
        if page_change != 0:
            if page_change < 0 and self.page_index > 1:
                self.page_index -= 1
            elif page_change > 0 and self.page_index < plg_tools.results_pages_counter(
                total=self.results_count
            ):
                self.page_index += 1
            else:
                return False
        else:
            self.page_index = 1
        params["page"] = self.page_index
        # Info for _lang parameter
        params["lang"] = self.lang
        # URL BUILDING FUNCTION CALLED.
        self.api_requester.currentUrl = self.api_requester.build_request_url(params)
        # Sending the request to Isogeo API
        self.api_requester.send_request()
        return

    def search_slot(self, result: dict, tags: dict):
        """Slot connected to ApiRequester.search_sig signal. It updates widgets, using
        SearchFormManager appropriate methods to fill them from 'tags' parameter and put
        them in the right status. It also display the results contained in 'result'
        parameter by calling ResultManager.show_results method if necessary.

        :param dict result: parsed content of API's reply to a search request (passed by
        ApiRequester.handle_reply method)
        :param dict tags: tags contained in API's reply parsed and classed into a dict
        (passed by ApiRequester.handle_reply method)
        """
        QgsMessageLog.logMessage(
            message="Query sent & received: {}".format(result.get("query")),
            tag="Isogeo",
            level=0,
        )
        # Save entered text and filters in search form
        params = self.form_mng.save_params()

        # Show how many results there are
        self.results_count = result.get("total")
        self.form_mng.btn_show.setText(str(self.results_count) + self.tr(" results"))
        page_count = str(plg_tools.results_pages_counter(total=self.results_count))
        self.form_mng.lbl_page.setText(
            self.tr("page ") + str(self.page_index) + self.tr(" on ") + page_count
        )

        # Clear widgets
        self.form_mng.tbl_result.clearContents()
        self.form_mng.tbl_result.setRowCount(0)

        # Initialize the widgets that dont't need to be updated
        if self.savedSearch == "_default" or self.hardReset is True:
            logger.debug("Default search or reset.")
            self.form_mng.init_steps()
        else:
            logger.debug("Not default search nor reset.")
            self.old_text = self.form_mng.txt_input.text()  # only if not first search to avoid when current widgets status is not relevant

        # Filling Advanced search comboboxes from tags
        self.form_mng.pop_as_cbbs(tags)
        # Filling quick searches comboboxes from json file (also the one in settings tab)
        self.form_mng.pop_qs_cbbs(self.form_mng.qs_mng.get_quicksearches_names())
        # Sorting Advanced search comboboxes
        for cbb in self.cbbs_search_advanced:
            cbb.model().sort(0)

        # Putting comboboxes' selected index to the appropriate location
        # and updating keywords checkable combobox
        if self.hardReset is True:
            # In case of a hard reset, we don't have to worry about comboboxes' selected index
            logger.debug("Reset search")
            self.form_mng.update_cbb_keywords(tags_keywords=tags.get("keywords"))
        else:
            logger.debug("Classical search or quicksearch (no reset search)")
            if self.savedSearch == "":
                # Putting all the comboboxes selected index to their previous location.
                logger.debug("Classic search case (not quicksearch)")
                params = params
                selected_keywords = params.get("keys")
                quicksearch = ""
            else:
                # Putting all the comboboxes selected index according to params found in the json file
                logger.debug("Quicksearch case: {}".format(self.savedSearch))
                # Opening the json to get quick search's params
                params = self.form_mng.qs_mng.get_quicksearches().get(self.savedSearch)
                quicksearch = self.savedSearch
                self.savedSearch = ""
                selected_keywords = [v for k, v in params.items() if k.startswith("keyword")]

            tags_keywords = tags.get("keywords")

            if params.get("labels", {}).get("keys", False):
                selected_keywords_labels = params.get("labels").get("keys")  # https://github.com/isogeo/isogeo-plugin-qgis/issues/436
            else:
                selected_keywords_labels = []

            # Setting widgets to their previous index
            self.form_mng.set_ccb_index(params=params, quicksearch=quicksearch)
            # Updating the keywords special combobox (filling + indexing)
            self.form_mng.update_cbb_keywords(
                tags_keywords=tags_keywords,
                selected_keywords=selected_keywords,
                selected_keywords_labels=selected_keywords_labels  # https://github.com/isogeo/isogeo-plugin-qgis/issues/436
            )

        # tweaking
        plg_tools._ui_tweaker(ui_widgets=self.form_mng.tab_search.findChildren(QComboBox))

        # Formatting show result button according to the number of results
        if self.results_count == 0:
            self.form_mng.btn_show.setEnabled(False)
            self.form_mng.btn_show.setStyleSheet("QPushButton { }")
        else:
            self.form_mng.btn_show.setEnabled(True)
            self.form_mng.btn_show.setStyleSheet(
                "QPushButton " "{background-color: rgb(255, 144, 0); color: white}"
            )

        # Showing result : if button 'show result', 'next page' or 'previous page' pressed
        if self.showResult is True:
            self.form_mng.fill_tbl_result(
                results=result.get("results"),
                page_index=self.page_index,
                results_count=self.results_count,
            )
            iface.mainWindow().statusBar().removeWidget(self.bar)
            self.store = True
        else:
            pass

        # Re enable all user input fields now the search function is
        # finished.
        self.form_mng.switch_widgets_on_and_off(1)
        # Resetting attributes values
        self.hardReset = False
        self.showResult = False

    def set_widget_status(self):
        """Set a few variable and send the request to Isogeo API."""
        selected_search = self.form_mng.cbb_quicksearch_use.currentText()
        logger.debug("Quicksearch selected: {}".format(selected_search))
        # load quicksearches
        saved_searches = self.form_mng.qs_mng.get_quicksearches()
        if selected_search != self.tr("Quicksearches"):
            self.form_mng.switch_widgets_on_and_off(0)  # disable search form
            # check if selected search can be found
            if selected_search in saved_searches:
                self.savedSearch = selected_search
                search_params = saved_searches.get(selected_search)
                logger.debug(
                    "Quicksearch found in saved searches and related search params have just been loaded from it."
                )
            elif selected_search not in saved_searches and "_default" in saved_searches:
                logger.warning("Selected search ({}) not found." "'_default' will be used instead.")
                self.savedSearch = "_default"
                search_params = saved_searches.get("_default")
            else:
                logger.error(
                    "Selected search ({}) and '_default' do not exist.".format(selected_search)
                )
                return

            # Check projection settings in loaded search params
            if "epsg" in search_params:
                currentCrs = plg_tools.get_map_crs()
                logger.debug("Specific CRS found in search params: {}".format(search_params.get("epsg")))
                if currentCrs == search_params.get("epsg"):
                    canvas = iface.mapCanvas()
                    e = search_params.get("extent")
                    rect = QgsRectangle(float(e[0]), float(e[1]), float(e[2]), float(e[3]))
                    canvas.setExtent(rect)
                    canvas.refresh()
                else:
                    canvas = iface.mapCanvas()
                    qgs_prj = QgsProject.instance()

                    # because "epsg" parameter values changed working on https://github.com/isogeo/isogeo-plugin-qgis/issues/437
                    if QgsCoordinateReferenceSystem(search_params.get("epsg")).isValid():
                        originCrs = QgsCoordinateReferenceSystem(search_params.get("epsg"))
                    else:
                        originCrs = QgsCoordinateReferenceSystem("EPSG:" + str(search_params.get("epsg")))

                    if originCrs.isValid():
                        qgs_prj.setCrs(originCrs)
                        e = search_params.get("extent")
                        rect = QgsRectangle(float(e[0]), float(e[1]), float(e[2]), float(e[3]))
                        canvas.setExtent(rect)
                        canvas.refresh()
                        qgs_prj.setCrs(
                            QgsCoordinateReferenceSystem(currentCrs)
                        )
                    else:
                        logger.warning("No valid CRS could be build, neither from '{}' nor from '{}'".format(str(search_params.get("epsg")), "EPSG:" + str(search_params.get("epsg"))))
                        pass
            # load request
            self.api_requester.currentUrl = search_params.get("url") + f"&_lang={self.lang}"
            self.api_requester.send_request()
        else:
            if self.savedSearch == "first":
                logger.debug("First search. Launch '_default' search.")

                self.savedSearch = "_default"
                search_params = saved_searches.get("_default")
                self.old_text = search_params.get("text")

                self.api_requester.currentUrl = search_params.get("url") + f"&_lang={self.lang}"
                self.api_requester.send_request()

            else:
                logger.debug("No quicksearch selected.")

    def edited_search(self):
        """On the QLine edited signal, decide wether a search has to be launched."""

        current_text = self.form_mng.txt_input.text()
        if current_text == self.old_text:
            logger.debug("The lineEdit text hasn't changed. So pass without sending a request.")
        else:
            logger.debug("The line Edit text changed. Calls the search function.")
            if current_text == "Ici c'est Isogeo !":
                plg_tools.special_search("isogeo")
                self.form_mng.txt_input.clear()
                return
            elif current_text == "Picasa":
                plg_tools.special_search("picasa")
                self.form_mng.txt_input.clear()
                return
            else:
                pass
            self.search()

    def reinitialize_search(self):
        """Clear all widget, putting them all back to their default value.

        Clear all widget and send a request to the API (which ends up updating
        the fields : send_request() calls handle_reply(), which calls
        update_fields())
        """
        logger.debug("Reset search function called.")
        self.hardReset = True
        # clear widgets
        self.form_mng.reinit_widgets()
        self.old_text = self.form_mng.txt_input.text()
        # launch search
        self.search()

    # -- UTILS ----------------------------------------------------------------
    def add_loading_bar(self):
        """Display a progress bar."""
        self.bar = QProgressBar()
        self.bar.setRange(0, 0)
        self.bar.setFixedWidth(120)
        self.iface.mainWindow().statusBar().insertPermanentWidget(0, self.bar)

    def send_details_request(self, md_id):
        """Send a request for additional info about one data.

        :param str md_id: UUID of metadata to retrieve
        """
        logger.debug("Full metadata sheet asked. Building the url.")
        li_include = [
            "conditions",
            "contacts",
            "coordinate-system",
            "events",
            "feature-attributes",
            "limitations",
            "keywords",
            "specifications"
        ]
        include_value = ",".join(li_include)
        self.api_requester.currentUrl = "{}/resources/{}?_include={}&_lang={}".format(
            self.api_requester.api_url_base, md_id, include_value, self.lang
        )
        self.api_requester.send_request("details")

    def write_shares_info(self, text: str):
        """Write informations about the shares in the Settings panel.
        See: #87

        :param text str: share informations from Isogeo API
        """
        if text != "no_shares":
            logger.info("Displaying application properties.")
            self.authenticator.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(True)
            self.form_mng.txt_shares.setText(text)
            if self.savedSearch == "first":
                self.set_widget_status()
            else:
                pass
        else:
            self.pluginIsActive = False
        # method ending
        return

    # -- LAUNCH PAD------------------------------------------------------------
    # This function is launched when the plugin is activated.
    def run(self):
        """Run method that loads and starts the plugin."""
        logger.debug("Is the plugin active ? --> {}".format(self.pluginIsActive))
        if not self.pluginIsActive:
            logger.info("Opening (display) the plugin...")
            self.pluginIsActive = True
            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.form_mng is None:
                # Create the dockwidget (after translation) and keep reference
                self.form_mng = SearchFormManager(trad=self.tr, settings_manager=self.settings_mng)
                self.form_mng.qs_mng.url_builder = self.api_requester.build_request_url

                logger.debug("Plugin load time: {}".format(plugin_times.get(plg_reg_name, "NR")))
            else:
                pass

            # connect to provide cleanup on closing of dockwidget
            self.form_mng.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.RightDockWidgetArea, self.form_mng)
            self.form_mng.show()

            # Fixing a qgis.core bug that shows a warning banner "connexion time
            # out" whenever a request is sent (even successfully) See :
            # http://gis.stackexchange.com/questions/136369/download-file-from-network-using-pyqgis-2-x#comment299999_136427
            # msgBar.widgetAdded.connect(msgBar.clearWidgets)

            """ --- CONNECTING UI WIDGETS <-> FUNCTIONS --- """
            # shortcuts
            self.cbbs_search_advanced = self.form_mng.grp_filters.findChildren(QComboBox)
            # -- Search form ------------------------------------------------------
            # search terms text input
            self.form_mng.txt_input.returnPressed.connect(self.edited_search)
            self.form_mng.btn_search_go.pressed.connect(self.edited_search)
            # reset search button
            self.form_mng.btn_reinit.pressed.connect(self.reinitialize_search)
            # filters comboboxes
            self.form_mng.cbb_contact.activated.connect(self.search)
            self.form_mng.cbb_format.activated.connect(self.search)
            self.form_mng.cbb_geofilter.activated.connect(self.search)
            self.form_mng.cbb_grpTh.activated.connect(self.search)
            self.form_mng.cbb_inspire.activated.connect(self.search)
            self.form_mng.cbb_license.activated.connect(self.search)
            self.form_mng.cbb_owner.activated.connect(self.search)
            self.form_mng.cbb_srs.activated.connect(self.search)
            self.form_mng.cbb_type.activated.connect(self.search)
            self.form_mng.kw_sig.connect(self.search)

            # -- Results table ----------------------------------------------------
            # show and order results
            self.form_mng.btn_show.pressed.connect(partial(self.search, show=True))
            self.form_mng.cbb_ob.activated.connect(partial(self.search, show=True))
            self.form_mng.cbb_od.activated.connect(partial(self.search, show=True))
            # pagination
            self.form_mng.btn_next.pressed.connect(partial(self.search, show=True, page_change=1))
            self.form_mng.btn_previous.pressed.connect(partial(self.search, show=True, page_change=-1))
            # metadata display
            self.form_mng.results_mng.md_asked.connect(self.send_details_request)

            # -- Quicksearches ----------------------------------------------------

            # select and use
            self.form_mng.cbb_quicksearch_use.activated.connect(self.set_widget_status)

            # # -- Settings tab - Search --------------------------------------------
            # button to empty the cache of filepaths #135
            self.form_mng.btn_cache_trash.pressed.connect(self.form_mng.results_mng.cache_mng.cleaner)

            # -- Settings tab - Application authentication ------------------------
            # Change user -> see below for authentication form
            self.form_mng.btn_change_user.pressed.connect(self.authenticator.display_auth_form)
            # share text window
            self.form_mng.txt_shares.setOpenLinks(False)
            self.form_mng.txt_shares.anchorClicked.connect(plg_tools.open_webpage)

            # -- Settings tab - Resources -----------------------------------------
            # report and log - see #53 and  #139
            self.form_mng.btn_log_dir.setIcon(ico_log)
            self.form_mng.btn_log_dir.pressed.connect(
                partial(plg_tools.open_dir_file, target=plg_logdir)
            )
            self.form_mng.btn_report.pressed.connect(
                partial(
                    plg_tools.open_webpage,
                    link="https://github.com/isogeo/isogeo-plugin-qgis/issues/new?"
                    "assignees=&template=bug_report.md&title={}"
                    " - plugin v{} QGIS {} ({})&labels=bug&milestone=4".format(
                        self.tr("TITLE ISSUE REPORTED"),
                        plg_tools.plugin_metadata(base_path=plg_basepath),
                        Qgis.QGIS_VERSION,
                        platform.platform(),
                    ),
                )
            )
            # help button
            help_url = self.settings_mng.config_content.get("help_base_url") + "/doc-plugin-qgis/"
            self.form_mng.btn_help.pressed.connect(partial(plg_tools.open_webpage, link=help_url))
            # view credits - see: #52
            self.form_mng.btn_credits.pressed.connect(self.credits_dialog.show)

            # -- Settings tab - layer adding settings ------------------------
            self.form_mng.btn_open_pgdb_config_dialog.setIcon(ico_pgis)
            if self.form_mng.results_mng.db_mng.pgis_available:
                self.form_mng.btn_open_pgdb_config_dialog.pressed.connect(
                    partial(self.form_mng.results_mng.db_mng.open_db_config_dialog, "PostgreSQL")
                )
            else:
                self.form_mng.btn_open_pgdb_config_dialog.setEnabled(0)
                self.form_mng.btn_open_pgdb_config_dialog.setToolTip(
                    self.tr("PostgreSQL databases are not supported by your QGIS installation.")
                )

            self.form_mng.btn_open_ora_config_dialog.setIcon(ico_ora)
            if self.form_mng.results_mng.db_mng.ora_available:
                self.form_mng.btn_open_ora_config_dialog.pressed.connect(
                    partial(self.form_mng.results_mng.db_mng.open_db_config_dialog, "Oracle")
                )
            else:
                self.form_mng.btn_open_ora_config_dialog.setEnabled(0)
                self.form_mng.btn_open_ora_config_dialog.setToolTip(
                    self.tr("Oracle databases are not supported by your QGIS installation.")
                )

            """ ------- EXECUTED AFTER PLUGIN IS LAUNCHED --------------------- """
            self.form_mng.setWindowTitle("Isogeo - {}".format(self.plg_version))
            # add translator method in others modules
            plg_tools.tr = self.tr
            # checks
            url_to_check = (
                self.settings_mng.config_content.get("api_base_url")
                .replace("https://", "")
                .replace("http://", "")
            )
            plg_tools.check_proxy_configuration(url_to_check=url_to_check)  # 22
            self.form_mng.cbb_chck_kw.setEnabled(plg_tools.test_qgis_style())  # see #137

            self.form_mng.txt_input.setFocus()
            # connect limitations checker to user informer
            self.form_mng.results_mng.lim_checker.lim_sig.connect(self.informer.lim_slot)
            # launch authentication
            self.user_authentication()
        else:
            pass


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
