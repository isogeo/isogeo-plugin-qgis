# -*- coding: utf-8 -*-

# Standard library
from configparser import Error
import logging
import shutil
import time
import json
from functools import partial
from pathlib import Path

# PyQGIS
from qgis.gui import QgsMessageBar

# PyQT
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QObject,
    QSettings,
    QTranslator,
    pyqtSignal,
    qVersion,
)

# UI class
from ...ui.auth.dlg_authentication import IsogeoAuthentication

# Plugin modules
from ..tools import IsogeoPlgTools
from ..user_inform import UserInformer

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
qsettings = QSettings()
plg_tools = IsogeoPlgTools()

plugin_dir = Path(__file__).parents[2]


try:
    locale = str(qsettings.value("locale/userLocale", "fr", type=str))[0:2]
except TypeError as exc:
    logger.error(
        "Bad type in QSettings: {}. Original error: {}".format(
            type(qsettings.value("locale/userLocale")), exc
        )
    )
    locale = "fr"

locale_path = plugin_dir / "i18n" / "isogeo_search_engine_{}.qm".format(locale)

if locale_path.exists():
    translator = QTranslator()
    translator.load(str(locale_path))

    if qVersion() > "4.3.3":
        QCoreApplication.installTranslator(translator)
    else:
        pass
else:
    pass

# ############################################################################
# ########## Classes ###############
# ##################################


class Authenticator(QObject):
    """Basic class to manage user authentication to Isogeo's API :
        - Getting credentials from oAuth2 file or QGIS Settings
        - Storing credentials
        - Displaying authentication form

    :param str auth_folder: the path to the plugin/_auth subfolder
    where oAuth2 file is stored.
    """

    auth_sig = pyqtSignal(str)
    ask_shares = pyqtSignal()

    # ui reference - authentication form
    ui_auth_form = IsogeoAuthentication()
    # display messages to the user
    msgbar = QgsMessageBar(ui_auth_form)
    ui_auth_form.msgbar_vlayout.addWidget(msgbar)

    # set config.json file path
    json_content = dict
    json_path = Path(__file__).parents[2] / "config.json"

    # plugin credentials storage parameters
    credentials_location = {"QSettings": 0, "oAuth2_file": 0}

    def __init__(self):
        # inheritance
        super().__init__()

        # api parameters
        self.load_json_file_content()
        if not self.json_content:
            raise Error("Unable to load {} file content.".format(self.json_path))
        else:
            if self.json_content.get("api_base_url").endswith("/"):
                v1_url = self.json_content.get("api_base_url")[:-1]
            else:
                v1_url = self.json_content.get("api_base_url")

            if self.json_content.get("api_auth_url").endswith("/"):
                id_url = self.json_content.get("api_auth_url")[:-1]
            else:
                id_url = self.json_content.get("api_auth_url")

            self.api_params = {
                "app_id": "",
                "app_secret": "",
                "url_base": v1_url,
                "url_auth": "{}/oauth/authorize".format(id_url),
                "url_token": "{}/oauth/token".format(id_url),
                "url_redirect": "http://localhost:5000/callback",
            }

            if self.json_content.get("app_base_url").endswith("/"):
                self.app_url = self.json_content.get("app_base_url")[:-1]
            else:
                self.app_url = self.json_content.get("app_base_url")

        # credentials storage folder
        self.auth_folder = plugin_dir / "_auth"
        self.cred_filepath = self.auth_folder / "client_secrets.json"

        # translation
        self.tr = object
        self.lang = str

        # inform user
        self.informer = object
        self.first_auth = bool

    # CONFIG FILE LOADER ---------------------------------------------------------------------------
    def load_json_file_content(self):
        """Retrieve API and app URLs from config.json file"""
        try:
            with open(self.json_path, "r") as json_content:
                self.json_content = json.load(json_content)

            if not isinstance(self.json_content, dict):
                logger.warning(
                    "config.json file content is not correctly formatted : {}.".format(
                        self.json_content
                    )
                )
                self.json_content = 0
            elif not all(
                key in list(self.json_content.keys())
                for key in [
                    "api_base_url",
                    "api_auth_url",
                    "app_base_url",
                    "help_base_url",
                    "background_map_url",
                ]
            ):
                logger.warning(
                    "Missing key in config.json file content : {}.".format(self.json_content)
                )
                self.json_content = 0
            else:
                logger.info(
                    "config.json file content successfully loaded : {}.".format(self.json_content)
                )
                qsettings.setValue("isogeo/env/api_base_url", self.json_content.get("api_base_url"))
                qsettings.setValue("isogeo/env/api_auth_url", self.json_content.get("api_auth_url"))
                qsettings.setValue("isogeo/env/app_base_url", self.json_content.get("app_base_url"))
                qsettings.setValue(
                    "isogeo/env/help_base_url", self.json_content.get("help_base_url")
                )
                qsettings.setValue(
                    "isogeo/settings/background_map_url",
                    self.json_content.get("background_map_url"),
                )

        except Exception as e:
            if not self.json_path.exists() or not self.json_path.is_file():
                logger.warning(
                    "config.json file can't be used : {} doesn't exist or is not a file : {}".format(
                        str(self.json_path), str(e)
                    )
                )
                logger.warning("Let's create one with default values: {}.".format(self.json_path))
                self.json_content = {
                    "api_base_url": qsettings.value(
                        "isogeo/env/api_base_url", "https://v1.api.isogeo.com"
                    ),
                    "api_auth_url": qsettings.value(
                        "isogeo/env/api_auth_url", "https://id.api.isogeo.com"
                    ),
                    "app_base_url": qsettings.value(
                        "isogeo/env/app_base_url", "https://app.isogeo.com"
                    ),
                    "help_base_url": qsettings.value(
                        "isogeo/env/help_base_url", "https://help.isogeo.com"
                    ),
                    "background_map_url": qsettings.value(
                        "isogeo/settings/background_map_url",
                        "type=xyz&format=image/png&styles=default&tileMatrixSet=250m&url=http://tile.openstreetmap.org/{z}/{x}/{y}.png",
                    ),
                }
                with open(self.json_path, "w") as json_content:
                    json.dump(self.json_content, json_content, indent=4)
            else:
                logger.error("config.json file can't be read : {}.".format(str(e)))
                self.json_content = 0

    # MANAGER --------------------------------------------------------------------------------------
    def manage_api_initialization(self):
        """Perform several operations to use Isogeo API:

        1. check if existing credentials are stored into QGIS or a file
        2. gettings credentials from there storage location (QGIS settings or file)
        3. display auth form if no credentials are found

        :returns: True and a dictionnary containing api parameters nessary for the
        instanciation of the ApiRequester class if credentials are found. False and
        None if no credentials are found.

        :rtype: bool, dict
        """
        # try to retrieve existing credentials from potential sources
        self.credentials_location["QSettings"] = self.credentials_check_qsettings()
        self.credentials_location["oAuth2_file"] = self.credentials_check_file()

        # update class attributes from credentials found
        if self.credentials_location.get("QSettings"):
            self.credentials_update("QSettings")
        elif self.credentials_location.get("oAuth2_file"):
            self.credentials_update("oAuth2_file")
        else:
            logger.info("No credentials found. ")
            self.first_auth = True
            self.display_auth_form()
            return False, None

        return True, self.api_params

    # CREDENTIALS LOCATORS -------------------------------------------------------------------------
    def credentials_check_qsettings(self):
        """Retrieve Isogeo API credentials within QGIS QSettings."""

        if "isogeo-plugin" in qsettings.childGroups():
            logger.warning("Old credentials found and removed in QGIS QSettings: isogeo-plugin")

            qsettings.remove("isogeo-plugin")
            return False
        elif "isogeo" in qsettings.childGroups():
            # looking in child groups and clean a little if needed
            qsettings.beginGroup("isogeo")
            if "auth" in qsettings.childGroups() and qsettings.contains("auth/app_id"):
                logger.debug("Credentials found within QGIS QSettings: isogeo/")
                qsettings.endGroup()
                return True
            else:
                logger.debug("Missing 'isogeo/auth' entry within QGIS QSettings.")
                qsettings.endGroup()
                return False
        else:
            logger.debug("No Isogeo credentials found within QGIS QSettings.")
            pass
        return False

    def credentials_check_file(self):
        """Retrieve Isogeo API credentials from a file stored inside the
        plugin/_auth subfolder.

        return: True if credentials can be retrieved from oAuth2 file.
        False if the file doesn't exists or if credentials can't be retrieved.

        :rtype: bool
        """
        credentials_filepath = self.cred_filepath
        # check if a client_secrets.json file is stored inside the _auth subfolder
        if not credentials_filepath.is_file():
            logger.debug("No credential files found: {}".format(credentials_filepath))
            return False
        else:
            pass
        # check file structure
        try:
            plg_tools.credentials_loader(credentials_filepath)
            logger.debug("Credentials found in {}".format(credentials_filepath))
        except Exception as e:
            logger.debug(e)
            return False
        # end of method
        return True

    # CREDENTIALS SAVER ----------------------------------------------------------------------------
    def credentials_storer(self, store_location: str = "QSettings"):
        """Store class attributes (API parameters) into the specified store_location.

        :param str store_location: name of targetted store location. Options:
            - QSettings
        """
        if store_location == "QSettings":
            qsettings.setValue("isogeo/auth/app_id", self.api_params.get("app_id"))
            qsettings.setValue("isogeo/auth/app_secret", self.api_params.get("app_secret"))
        else:
            pass
        logger.debug("Credentials stored into: {}".format(store_location))

    def credentials_update(self, credentials_source: str = "QSettings"):
        """Update class attributes (API parameters) from specified credentials source.

        :param str credentials_source: name of targetted credentials source. Options:
            - QSettings
            - oAuth2_file
        """
        # update class attributes
        if credentials_source == "QSettings":
            self.api_params["app_id"] = qsettings.value("isogeo/auth/app_id", "")
            self.api_params["app_secret"] = qsettings.value("isogeo/auth/app_secret", "")
        elif credentials_source == "oAuth2_file":
            creds = plg_tools.credentials_loader(self.cred_filepath)
            self.api_params["app_id"] = creds.get("client_id")
            self.api_params["app_secret"] = creds.get("client_secret")
            self.credentials_storer(store_location="QSettings")
        else:
            pass

        logger.debug(
            "Credentials updated from: {}. Application ID used: {}".format(
                credentials_source, self.api_params["app_id"]
            )
        )

    # AUTHENTICATION FORM --------------------------------------------------------------------------
    def display_auth_form(self):
        """Show authentication form with prefilled fields and connected widgets."""
        self.informer = UserInformer(message_bar=self.msgbar, trad=self.tr)
        self.auth_sig.connect(self.informer.authentication_slot)
        self.ui_auth_form.chb_isogeo_editor.stateChanged.connect(
            lambda: qsettings.setValue(
                "isogeo/user/editor",
                int(self.ui_auth_form.chb_isogeo_editor.isChecked()),
            )
        )
        self.ui_auth_form.btn_free_test.pressed.connect(
            partial(plg_tools.open_pipedrive_test_form, lang=self.lang)
        )
        self.ui_auth_form.btn_rdv_isogeo.pressed.connect(
            partial(plg_tools.open_pipedrive_rdv_form, lang=self.lang)
        )
        self.ui_auth_form.btn_browse_credentials.fileChanged.connect(self.credentials_uploader)

        self.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(False)

        # fillfull auth form fields from stored settings
        self.ui_auth_form.ent_app_id.setText(self.api_params["app_id"])
        self.ui_auth_form.ent_app_secret.setText(self.api_params["app_secret"])
        self.ui_auth_form.lbl_api_url_value.setText(self.api_params["url_base"])
        self.ui_auth_form.chb_isogeo_editor.setChecked(
            int(qsettings.value("isogeo/user/editor", 0))
        )
        # display
        logger.debug("Authentication form filled and ready to be launched.")
        self.ui_auth_form.show()

        if self.first_auth:
            pass
        else:
            self.ask_shares.emit()
            pass

    def credentials_uploader(self):
        """Get file selected by the user and loads API credentials into plugin.
        If the selected is compliant, credentials are loaded from then it's
        moved inside plugin/_auth subfolder. auth_sig is emitted to inform the user
        about indicated file's accessibility and format validity.
        """
        self.ui_auth_form.btn_browse_credentials.fileChanged.disconnect()

        # test file structure
        selected_file = Path(self.ui_auth_form.btn_browse_credentials.filePath())
        logger.debug(
            "Loading credentials from file indicated by the user : {}".format(selected_file)
        )
        try:
            api_credentials = plg_tools.credentials_loader(
                self.ui_auth_form.btn_browse_credentials.filePath()
            )
        except IOError as e:
            self.auth_sig.emit("path")
            logger.error(
                "Fail to load credentials from authentication file. IOError : {}".format(e)
            )
            self.ui_auth_form.btn_browse_credentials.fileChanged.connect(self.credentials_uploader)
            self.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(False)
            return False
        except ValueError as e:
            self.auth_sig.emit("file")
            logger.error(
                "Fail to load credentials from authentication file. ValueError : {}".format(e)
            )
            self.ui_auth_form.btn_browse_credentials.fileChanged.connect(self.credentials_uploader)
            self.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(False)
            return False

        # rename existing credentials file with prefix 'old_' and datetime as suffix
        dest_path = self.cred_filepath
        if dest_path.is_file():
            logger.debug("client_secrets.json already existed. " "Previous file has been renamed.")

            old_file_renamed = self.auth_folder / "old_client_secrets_{}.json".format(
                int(time.time())
            )
            dest_path.rename(old_file_renamed)

        else:
            pass

        # move new credentials file to the _auth subfolder
        try:
            shutil.copyfile(str(selected_file), str(dest_path))  # using pathlib.Path (= os.rename)
            logger.debug("Selected credentials file has been moved into plugin _auth subfolder")
        except OSError as e:
            logger.error(
                "Move new file raised: {}. Maybe because of moving from a "
                "different disk drive.".format(e)
            )
        except Exception as exc:
            logger.error("Failed to move authentication file: {}".format(exc))
            self.auth_sig.emit("path")
            self.ui_auth_form.btn_browse_credentials.fileChanged.connect(self.credentials_uploader)
            self.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(False)
            return False

        # set form
        self.ui_auth_form.ent_app_id.setText(api_credentials.get("client_id"))
        self.ui_auth_form.ent_app_secret.setText(api_credentials.get("client_secret"))
        self.ui_auth_form.lbl_api_url_value.setText(self.api_params["url_auth"])
        # update class attributes from file
        self.credentials_update(credentials_source="oAuth2_file")
        # store into QSettings if existing
        self.credentials_storer(store_location="QSettings")
        self.ui_auth_form.btn_browse_credentials.fileChanged.connect(self.credentials_uploader)
        self.auth_sig.emit("ok")
        return True


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
