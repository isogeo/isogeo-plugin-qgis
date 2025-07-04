# -*- coding: utf-8 -*-

# Standard library
import logging
import shutil
import time
from pathlib import Path

# PyQGIS
from qgis.gui import QgsMessageBar

# PyQT
from qgis.PyQt.QtCore import (
    QCoreApplication,
    QObject,
    QTranslator,
    pyqtSignal
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
plg_tools = IsogeoPlgTools()


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

    # plugin credentials storage parameters
    credentials_location = {"QSettings": 0, "oAuth2_file": 0}

    def __init__(self, settings_manager: object = None):
        # inheritance
        super().__init__()

        self.settings_mng = settings_manager

        # initialize locale
        locale = self.settings_mng.get_locale()
        plugin_dir = Path(__file__).parents[2]

        i18n_file_path = plugin_dir / "i18n" / "isogeo_search_engine_{}.qm".format(locale)

        if i18n_file_path.exists():
            translator = QTranslator()
            translator.load(str(i18n_file_path))
            QCoreApplication.installTranslator(translator)
        else:
            pass

        # api parameters
        self.settings_mng.load_config()
        v1_url = self.settings_mng.config_content.get("api_base_url")
        id_url = self.settings_mng.config_content.get("api_auth_url")

        self.api_params = {
            "app_id": "",
            "app_secret": "",
            "url_base": v1_url,
            "url_auth": "{}/oauth/authorize".format(id_url),
            "url_token": "{}/oauth/token".format(id_url),
            "url_redirect": "http://localhost:5000/callback",
        }

        # credentials storage folder
        self.auth_folder = plugin_dir / "_auth"
        self.cred_filepath = self.auth_folder / "client_secrets.json"

        # inform user
        self.informer = object
        self.first_auth = bool

    # MANAGER --------------------------------------------------------------------------------------
    def manage_api_initialization(self):
        """Perform several operations to use Isogeo API:

        1. check if existing credentials are stored into QGIS or a file
        2. get credentials from there storage location (QGIS settings or file)
        3. display auth form if no credentials are found

        :returns: True and a dictionary containing api parameters necessary for the
        instanciation of the ApiRequester class if credentials are found. False and
        None if no credentials are found.

        :rtype: bool, dict
        """
        # try to retrieve existing credentials from potential sources
        self.credentials_location["QSettings"] = self.credentials_check_qsettings()
        self.credentials_location["oAuth2_file"] = self.credentials_check_file()

        # update class attributes from credentials found
        if self.credentials_location.get("oAuth2_file"):
            self.credentials_update("oAuth2_file")
            logger.info("Credentials will be fetched from _auth\client_secrets.json file.")
        elif self.credentials_location.get("QSettings"):
            self.credentials_update("QSettings")
            logger.info("Credentials will be fetched from QSettings.")
        else:
            logger.info("No credentials found. ")
            self.first_auth = True
            self.display_auth_form()
            return False, None

        return True, self.api_params

    # CREDENTIALS LOCATORS -------------------------------------------------------------------------
    def credentials_check_qsettings(self):
        """Retrieve Isogeo API credentials within QGIS QSettings."""

        if "isogeo-plugin" in self.settings_mng.childGroups():
            logger.warning("Old credentials found and removed in QGIS QSettings: isogeo-plugin")

            self.settings_mng.remove("isogeo-plugin")
            return False
        elif "isogeo" in self.settings_mng.childGroups():
            # looking in child groups and clean a little if needed
            self.settings_mng.beginGroup("isogeo")
            if "auth" in self.settings_mng.childGroups() and self.settings_mng.contains("auth/app_id"):
                logger.debug("Credentials found within QGIS QSettings: isogeo/")
                self.settings_mng.endGroup()
                return True
            else:
                logger.debug("Missing 'isogeo/auth' entry within QGIS QSettings.")
                self.settings_mng.endGroup()
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
            self.settings_mng.set_value("isogeo/auth/app_id", self.api_params.get("app_id"))
            self.settings_mng.set_value("isogeo/auth/app_secret", self.api_params.get("app_secret"))
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
            self.api_params["app_id"] = self.settings_mng.get_value("isogeo/auth/app_id", "")
            self.api_params["app_secret"] = self.settings_mng.get_value("isogeo/auth/app_secret", "")
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
        self.informer = UserInformer(message_bar=self.msgbar)
        self.auth_sig.connect(self.informer.authentication_slot)
        self.ui_auth_form.chb_isogeo_editor.stateChanged.connect(
            lambda: self.settings_mng.set_value(
                "isogeo/user/editor",
                int(self.ui_auth_form.chb_isogeo_editor.isChecked()),
            )
        )
        self.ui_auth_form.btn_browse_credentials.fileChanged.connect(self.credentials_uploader)

        self.ui_auth_form.btn_ok_cancel.buttons()[0].setEnabled(False)

        # fullfil auth form fields from stored settings
        self.ui_auth_form.ent_app_id.setText(self.api_params["app_id"])
        self.ui_auth_form.ent_app_secret.setText(self.api_params["app_secret"])
        self.ui_auth_form.lbl_api_url_value.setText(self.api_params["url_base"])
        self.ui_auth_form.chb_isogeo_editor.setChecked(
            int(self.settings_mng.get_value("isogeo/user/editor", 0))
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
