# -*- coding: utf-8 -*-

# Standard library
import logging
from pathlib import Path
import time
from functools import partial

# PyQT
from qgis.PyQt.QtCore import QSettings, QCoreApplication, QTranslator, qVersion, QObject, pyqtSignal
from qgis.PyQt.QtWidgets import QMessageBox

# Plugin modules
from ..tools import IsogeoPlgTools

# UI class
from ...ui.auth.dlg_authentication import IsogeoAuthentication

# ############################################################################
# ########## Globals ###############
# ##################################

logger = logging.getLogger("IsogeoQgisPlugin")
qsettings = QSettings()
plg_tools = IsogeoPlgTools()

plugin_dir = Path(__file__).parents[2]

locale = qsettings.value("locale/userLocale")[0:2]
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

    auth_sig = pyqtSignal()

    # ui reference - authentication form
    ui_auth_form = IsogeoAuthentication()

    # api parameters
    api_params = {
        "app_id": "",
        "app_secret": "",
        "url_base": "https://v1.api.isogeo.com/",
        "url_auth": "https://id.api.isogeo.com/oauth/authorize",
        "url_token": "https://id.api.isogeo.com/oauth/token",
        "url_redirect": "http://localhost:5000/callback",
    }

    # plugin credentials storage parameters
    credentials_location = {"QSettings": 0, "oAuth2_file": 0}

    def __init__(self):
        # inheritance
        super().__init__()

        # API URLs - Prod
        (
            self.platform,
            self.api_url,
            self.app_url,
            self.csw_url,
            self.mng_url,
            self.oc_url,
            self.ssl,
        ) = plg_tools.set_base_url("prod")

        # credentials storage folder
        self.auth_folder = plugin_dir / "_auth"
        self.cred_filepath = self.auth_folder / "client_secrets.json"

        # translation
        self.tr = object
        self.lang = str

        self.first_auth = bool

    def emit_auth_sig(self):
        self.auth_sig.emit()
    # MANAGER -----------------------------------------------------------------
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

    # CREDENTIALS LOCATORS ----------------------------------------------------
    def credentials_check_qsettings(self):
        """Retrieve Isogeo API credentials within QGIS QSettings.
        """

        if "isogeo-plugin" in qsettings.childGroups():
            logger.warning(
                "Old credentials found and removed in QGIS QSettings: isogeo-plugin"
            )

            qsettings.remove("isogeo-plugin")
            return False
        elif "isogeo" in qsettings.childGroups():
            # looking in child groups and clean a little if needed
            qsettings.beginGroup("isogeo")
            if "app_auth" in qsettings.childGroups():
                qsettings.remove("isogeo/app_auth")
                logger.debug("QSettings clean up - app_auth")
                pass
            if "api_auth" in qsettings.childGroups():
                qsettings.remove("isogeo/api_auth")
                logger.debug("QSettings clean up - api_auth")
                pass
            if "auth" in qsettings.childGroups() and not qsettings.contains(
                "auth/app_id"
            ):
                qsettings.remove("isogeo/auth")
                logger.debug("QSettings clean up - bad formatted auth")
                pass
            if "auth" in qsettings.childGroups() and qsettings.contains("auth/app_id"):
                logger.debug("Credentials found within QGIS QSettings: isogeo/")
                pass
            qsettings.endGroup()
            return True
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

    # CREDENTIALS SAVER -------------------------------------------------------
    def credentials_storer(self, store_location: str = "QSettings"):
        """Store class attributes (API parameters) into the specified store_location.

        :param str store_location: name of targetted store location. Options:
            - QSettings
        """
        if store_location == "QSettings":
            qsettings.setValue("isogeo/auth/app_id", self.api_params["app_id"])
            qsettings.setValue("isogeo/auth/app_secret", self.api_params["app_secret"])
            qsettings.setValue("isogeo/auth/url_base", self.api_params["url_base"])
            qsettings.setValue("isogeo/auth/url_auth", self.api_params["url_auth"])
            qsettings.setValue("isogeo/auth/url_token", self.api_params["url_token"])
            qsettings.setValue(
                "isogeo/auth/url_redirect", self.api_params["url_redirect"]
            )
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
            self.api_params["app_secret"] = qsettings.value(
                "isogeo/auth/app_secret", ""
            )
            self.api_params["url_base"] = qsettings.value(
                "isogeo/auth/url_base", "https://v1.api.isogeo.com/"
            )
            self.api_params["url_auth"] = qsettings.value(
                "isogeo/auth/url_auth", "https://id.api.isogeo.com/oauth/authorize"
            )
            self.api_params["url_token"] = qsettings.value(
                "isogeo/auth/url_token", "https://id.api.isogeo.com/oauth/token"
            )
            self.api_params["url_redirect"] = qsettings.value(
                "isogeo/auth/url_redirect", "http://localhost:5000/callback"
            )
        elif credentials_source == "oAuth2_file":
            creds = plg_tools.credentials_loader(self.cred_filepath)
            self.api_params["app_id"] = creds.get("client_id")
            self.api_params["app_secret"] = creds.get("client_secret")
            self.api_params["url_base"] = creds.get("uri_base")
            self.api_params["url_auth"] = creds.get("uri_auth")
            self.api_params["url_token"] = creds.get("uri_token")
            self.api_params["url_redirect"] = creds.get("uri_redirect")
            # self.credentials_storer(store_location="QSettings")
        else:
            pass

        logger.debug(
            "Credentials updated from: {}. Application ID used: {}".format(
                credentials_source, self.api_params["app_id"]
            )
        )

    # AUTHENTICATION FORM -----------------------------------------------------
    def display_auth_form(self):
        """Show authentication form with prefilled fields and connected widgets.
        """

        # connecting widgets
        self.ui_auth_form.chb_isogeo_editor.stateChanged.connect(
            lambda: qsettings.setValue(
                "isogeo/user/editor",
                int(self.ui_auth_form.chb_isogeo_editor.isChecked()),
            )
        )
        self.ui_auth_form.btn_account_new.pressed.connect(
            partial(plg_tools.mail_to_isogeo, lang=self.lang)
        )
        self.ui_auth_form.btn_browse_credentials.fileChanged.connect(
            self.credentials_uploader
        )

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
        else :
            self.auth_sig.emit()
            pass

    def credentials_uploader(self):
        """Get file selected by the user and loads API credentials into plugin.
        If the selected is compliant, credentials are loaded from then it's
        moved inside plugin/_auth subfolder.
        """
        self.ui_auth_form.btn_browse_credentials.fileChanged.disconnect()

        selected_file = Path(self.ui_auth_form.btn_browse_credentials.filePath())
        # test file structure
        logger.debug("Loading credentials from file indicated by the user : {}".format(selected_file))
        try:
            api_credentials = plg_tools.credentials_loader(self.ui_auth_form.btn_browse_credentials.filePath())
        except Exception as e:
            logger.error("Fail to load credentials from authentication file : {}".format(e))
            self.show_error("file")
            self.ui_auth_form.btn_browse_credentials.fileChanged.connect(
            self.credentials_uploader
            )
            return False
        # move credentials file into the plugin file structure
        dest_path = self.cred_filepath
        if dest_path.is_file():
            logger.debug(
                "client_secrets.json already existed. "
                "Previous file has been renamed."
            )

            old_file_renamed = self.auth_folder / "old_client_secrets_{}.json".format(
                int(time.time())
            )
            dest_path.rename(old_file_renamed)

        else:
            pass
        try:
            selected_file.rename(dest_path)
            logger.debug(
                "Selected credentials file has been moved into plugin" "_auth subfolder"
            )    
        except Exception as e:
            logger.debug("Fail to rename authentication file : {}".format(e))
            self.show_error("path")
            self.ui_auth_form.btn_browse_credentials.fileChanged.connect(
            self.credentials_uploader
            )
            return False
        # set form
        self.ui_auth_form.ent_app_id.setText(api_credentials.get("client_id"))
        self.ui_auth_form.ent_app_secret.setText(api_credentials.get("client_secret"))
        self.ui_auth_form.lbl_api_url_value.setText(api_credentials.get("uri_auth"))
        # update class attributes from file
        self.credentials_update(credentials_source="oAuth2_file")
        # store into QSettings if existing
        self.credentials_storer(store_location="QSettings")
        self.ui_auth_form.btn_browse_credentials.fileChanged.connect(
            self.credentials_uploader
        )
        self.emit_auth_sig()
        return True
    
    def show_error(self, error_type:str):
        message_type = {
            "path" : "The specified file is not found.",
            "file" : "The selected credentials file is not valid.",
            "creds" : "Authentication failed."
        }
        QMessageBox.warning(
                self.ui_auth_form,
                self.tr("Alert", "Authenticator"),
                self.tr(
                    message_type.get(error_type), "Authenticator"
                ),
            )


    # REQUEST and RESULTS ----------------------------------------------------
    def get_tags(self, tags: dict):
        """ This parse the tags contained in API_answer[tags] and class them so
        they are more easy to handle in other function such as update_fields()

        :param dict tags: a dict of tags as thez are return by the API

        return: a dict containing one dict for each type of tags

        rtype: dict(dict)
        """
        # set dicts
        actions = {}
        contacts = {}
        formats = {}
        inspire = {}
        keywords = {}
        licenses = {}
        md_types = {}
        owners = {}
        srs = {}
        # unused = {}
        # 0/1 values
        compliance = 0
        type_dataset = 0
        # parsing tags
        for tag in sorted(tags.keys()):
            # actions
            if tag.startswith("action"):
                actions[tags.get(tag, tag)] = tag
                continue
            # compliance INSPIRE
            elif tag.startswith("conformity"):
                compliance = 1
                continue
            # contacts
            elif tag.startswith("contact"):
                contacts[tags.get(tag)] = tag
                continue
            # formats
            elif tag.startswith("format"):
                formats[tags.get(tag)] = tag
                continue
            # INSPIRE themes
            elif tag.startswith("keyword:in"):
                inspire[tags.get(tag)] = tag
                continue
            # keywords
            elif tag.startswith("keyword:is"):
                keywords[tags.get(tag)] = tag
                continue
            # licenses
            elif tag.startswith("license"):
                licenses[tags.get(tag)] = tag
                continue
            # owners
            elif tag.startswith("owner"):
                owners[tags.get(tag)] = tag
                continue
            # SRS
            elif tag.startswith("coordinate-system"):
                srs[tags.get(tag)] = tag
                continue
            # types
            elif tag.startswith("type"):
                md_types[tags.get(tag)] = tag
                if tag in ("type:vector-dataset", "type:raster-dataset"):
                    type_dataset += 1
                continue
            # ignored tags
            else:
                # unused[tags.get(tag, tag)] = tag
                continue

        # override API tags to allow all datasets filter - see #
        if type_dataset == 2:
            md_types[self.tr("Dataset", "Authenticator")] = "type:dataset"
        else:
            pass

        # storing dicts
        tags_parsed = {
            "actions": actions,
            "compliance": compliance,
            "contacts": contacts,
            "formats": formats,
            "inspire": inspire,
            "keywords": keywords,
            "licenses": licenses,
            "owners": owners,
            "srs": srs,
            "types": md_types,
            # "unused": unused
        }

        # method ending
        logger.info("Tags retrieved")
        return tags_parsed


# #############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
