# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\auth\ui_authentication.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlg_form_auth_prompt(object):
    def setupUi(self, dlg_form_auth_prompt):
        dlg_form_auth_prompt.setObjectName("dlg_form_auth_prompt")
        dlg_form_auth_prompt.resize(800, 400)
        dlg_form_auth_prompt.setMinimumSize(QtCore.QSize(800, 400))
        dlg_form_auth_prompt.setMaximumSize(QtCore.QSize(800, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/key.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        dlg_form_auth_prompt.setWindowIcon(icon)
        dlg_form_auth_prompt.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        dlg_form_auth_prompt.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(dlg_form_auth_prompt)
        self.verticalLayout.setObjectName("verticalLayout")
        self.msgbar_vlayout = QtWidgets.QVBoxLayout()
        self.msgbar_vlayout.setObjectName("msgbar_vlayout")
        self.verticalLayout.addLayout(self.msgbar_vlayout)
        self.grb_connection_ready = QtWidgets.QGroupBox(dlg_form_auth_prompt)
        self.grb_connection_ready.setMinimumSize(QtCore.QSize(500, 150))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.grb_connection_ready.setFont(font)
        self.grb_connection_ready.setAutoFillBackground(False)
        self.grb_connection_ready.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.grb_connection_ready.setFlat(True)
        self.grb_connection_ready.setObjectName("grb_connection_ready")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.grb_connection_ready)
        self.gridLayout_2.setObjectName("gridLayout_2")
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_2.addItem(spacerItem, 1, 3, 1, 1)
        self.ent_app_id = QtWidgets.QLineEdit(self.grb_connection_ready)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ent_app_id.sizePolicy().hasHeightForWidth())
        self.ent_app_id.setSizePolicy(sizePolicy)
        self.ent_app_id.setMinimumSize(QtCore.QSize(475, 25))
        self.ent_app_id.setMaximumSize(QtCore.QSize(800, 30))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.ent_app_id.setFont(font)
        self.ent_app_id.setToolTip("")
        self.ent_app_id.setAutoFillBackground(True)
        self.ent_app_id.setText("")
        self.ent_app_id.setMaxLength(100)
        self.ent_app_id.setFrame(True)
        self.ent_app_id.setReadOnly(True)
        self.ent_app_id.setCursorMoveStyle(QtCore.Qt.LogicalMoveStyle)
        self.ent_app_id.setObjectName("ent_app_id")
        self.gridLayout_2.addWidget(self.ent_app_id, 2, 3, 1, 1)
        self.lbl_app_secret = QtWidgets.QLabel(self.grb_connection_ready)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_app_secret.sizePolicy().hasHeightForWidth())
        self.lbl_app_secret.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_app_secret.setFont(font)
        self.lbl_app_secret.setAutoFillBackground(False)
        self.lbl_app_secret.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.lbl_app_secret.setScaledContents(True)
        self.lbl_app_secret.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.lbl_app_secret.setObjectName("lbl_app_secret")
        self.gridLayout_2.addWidget(self.lbl_app_secret, 3, 1, 1, 1)
        self.chb_isogeo_editor = QtWidgets.QCheckBox(self.grb_connection_ready)
        self.chb_isogeo_editor.setMinimumSize(QtCore.QSize(300, 20))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.chb_isogeo_editor.setFont(font)
        self.chb_isogeo_editor.setToolTip("")
        self.chb_isogeo_editor.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.chb_isogeo_editor.setAutoFillBackground(False)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/authentication/user.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.chb_isogeo_editor.setIcon(icon1)
        self.chb_isogeo_editor.setTristate(False)
        self.chb_isogeo_editor.setObjectName("chb_isogeo_editor")
        self.gridLayout_2.addWidget(self.chb_isogeo_editor, 5, 3, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout_2.addItem(spacerItem1, 0, 4, 1, 1)
        self.lbl_browse_credentials = QtWidgets.QLabel(self.grb_connection_ready)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_browse_credentials.setFont(font)
        self.lbl_browse_credentials.setAutoFillBackground(False)
        self.lbl_browse_credentials.setScaledContents(True)
        self.lbl_browse_credentials.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.lbl_browse_credentials.setObjectName("lbl_browse_credentials")
        self.gridLayout_2.addWidget(self.lbl_browse_credentials, 0, 1, 1, 1)
        self.btn_ok_cancel = QtWidgets.QDialogButtonBox(self.grb_connection_ready)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.btn_ok_cancel.sizePolicy().hasHeightForWidth())
        self.btn_ok_cancel.setSizePolicy(sizePolicy)
        self.btn_ok_cancel.setMinimumSize(QtCore.QSize(30, 30))
        self.btn_ok_cancel.setMaximumSize(QtCore.QSize(16777215, 100))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_ok_cancel.setFont(font)
        self.btn_ok_cancel.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_ok_cancel.setAutoFillBackground(False)
        self.btn_ok_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_ok_cancel.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save
        )
        self.btn_ok_cancel.setCenterButtons(True)
        self.btn_ok_cancel.setObjectName("btn_ok_cancel")
        self.gridLayout_2.addWidget(self.btn_ok_cancel, 6, 0, 1, 7)
        spacerItem2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout_2.addItem(spacerItem2, 2, 4, 1, 1)
        self.lbl_app_id = QtWidgets.QLabel(self.grb_connection_ready)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_app_id.sizePolicy().hasHeightForWidth())
        self.lbl_app_id.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_app_id.setFont(font)
        self.lbl_app_id.setAutoFillBackground(False)
        self.lbl_app_id.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.lbl_app_id.setScaledContents(True)
        self.lbl_app_id.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.lbl_app_id.setObjectName("lbl_app_id")
        self.gridLayout_2.addWidget(self.lbl_app_id, 2, 1, 1, 1)
        self.ent_app_secret = QtWidgets.QLineEdit(self.grb_connection_ready)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ent_app_secret.sizePolicy().hasHeightForWidth())
        self.ent_app_secret.setSizePolicy(sizePolicy)
        self.ent_app_secret.setMinimumSize(QtCore.QSize(475, 25))
        self.ent_app_secret.setMaximumSize(QtCore.QSize(800, 30))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.ent_app_secret.setFont(font)
        self.ent_app_secret.setFocusPolicy(QtCore.Qt.NoFocus)
        self.ent_app_secret.setAutoFillBackground(True)
        self.ent_app_secret.setText("")
        self.ent_app_secret.setMaxLength(64)
        self.ent_app_secret.setEchoMode(QtWidgets.QLineEdit.PasswordEchoOnEdit)
        self.ent_app_secret.setReadOnly(True)
        self.ent_app_secret.setPlaceholderText("*******************************************")
        self.ent_app_secret.setObjectName("ent_app_secret")
        self.gridLayout_2.addWidget(self.ent_app_secret, 3, 3, 1, 1)
        self.lbl_api_url = QtWidgets.QLabel(self.grb_connection_ready)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_api_url.setFont(font)
        self.lbl_api_url.setAutoFillBackground(False)
        self.lbl_api_url.setScaledContents(True)
        self.lbl_api_url.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter
        )
        self.lbl_api_url.setObjectName("lbl_api_url")
        self.gridLayout_2.addWidget(self.lbl_api_url, 4, 1, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.gridLayout_2.addItem(spacerItem3, 3, 4, 1, 1)
        self.btn_browse_credentials = QgsFileWidget(self.grb_connection_ready)
        self.btn_browse_credentials.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_browse_credentials.sizePolicy().hasHeightForWidth())
        self.btn_browse_credentials.setSizePolicy(sizePolicy)
        self.btn_browse_credentials.setMinimumSize(QtCore.QSize(475, 30))
        self.btn_browse_credentials.setMaximumSize(QtCore.QSize(800, 30))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_browse_credentials.setFont(font)
        self.btn_browse_credentials.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.btn_browse_credentials.setAcceptDrops(False)
        self.btn_browse_credentials.setFileWidgetButtonVisible(True)
        self.btn_browse_credentials.setUseLink(False)
        self.btn_browse_credentials.setFullUrl(False)
        self.btn_browse_credentials.setFilter("*.json")
        self.btn_browse_credentials.setDefaultRoot("")
        self.btn_browse_credentials.setObjectName("btn_browse_credentials")
        self.gridLayout_2.addWidget(self.btn_browse_credentials, 0, 3, 1, 1)
        self.lbl_api_url_value = QtWidgets.QLabel(self.grb_connection_ready)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        font.setKerning(True)
        self.lbl_api_url_value.setFont(font)
        self.lbl_api_url_value.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.lbl_api_url_value.setAutoFillBackground(False)
        self.lbl_api_url_value.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.lbl_api_url_value.setText("https://v1.api.isogeo.com/")
        self.lbl_api_url_value.setOpenExternalLinks(True)
        self.lbl_api_url_value.setObjectName("lbl_api_url_value")
        self.gridLayout_2.addWidget(self.lbl_api_url_value, 4, 3, 1, 1)
        self.ent_app_id.raise_()
        self.ent_app_secret.raise_()
        self.lbl_app_id.raise_()
        self.lbl_app_secret.raise_()
        self.btn_ok_cancel.raise_()
        self.chb_isogeo_editor.raise_()
        self.btn_browse_credentials.raise_()
        self.lbl_browse_credentials.raise_()
        self.lbl_api_url_value.raise_()
        self.lbl_api_url.raise_()
        self.verticalLayout.addWidget(self.grb_connection_ready)
        self.grb_need_account = QtWidgets.QGroupBox(dlg_form_auth_prompt)
        self.grb_need_account.setMinimumSize(QtCore.QSize(200, 100))
        self.grb_need_account.setMaximumSize(QtCore.QSize(16777215, 200))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.grb_need_account.setFont(font)
        self.grb_need_account.setAutoFillBackground(False)
        self.grb_need_account.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.grb_need_account.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter
        )
        self.grb_need_account.setFlat(True)
        self.grb_need_account.setObjectName("grb_need_account")
        self.gridLayout = QtWidgets.QGridLayout(self.grb_need_account)
        self.gridLayout.setObjectName("gridLayout")
        self.btn_rdv_isogeo = QtWidgets.QPushButton(self.grb_need_account)
        self.btn_rdv_isogeo.setMinimumSize(QtCore.QSize(200, 30))
        self.btn_rdv_isogeo.setMaximumSize(QtCore.QSize(700, 30))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_rdv_isogeo.setFont(font)
        self.btn_rdv_isogeo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_rdv_isogeo.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.btn_rdv_isogeo.setAutoFillBackground(True)
        self.btn_rdv_isogeo.setAutoDefault(False)
        self.btn_rdv_isogeo.setDefault(False)
        self.btn_rdv_isogeo.setObjectName("btn_rdv_isogeo")
        self.gridLayout.addWidget(self.btn_rdv_isogeo, 2, 1, 1, 1)
        self.btn_free_test = QtWidgets.QPushButton(self.grb_need_account)
        self.btn_free_test.setMinimumSize(QtCore.QSize(200, 30))
        self.btn_free_test.setMaximumSize(QtCore.QSize(700, 30))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_free_test.setFont(font)
        self.btn_free_test.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_free_test.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.btn_free_test.setAutoFillBackground(True)
        self.btn_free_test.setAutoDefault(False)
        self.btn_free_test.setDefault(False)
        self.btn_free_test.setObjectName("btn_free_test")
        self.gridLayout.addWidget(self.btn_free_test, 2, 0, 1, 1)
        self.lbl_access_conditions = QtWidgets.QLabel(self.grb_need_account)
        self.lbl_access_conditions.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_access_conditions.setFont(font)
        self.lbl_access_conditions.setTextFormat(QtCore.Qt.RichText)
        self.lbl_access_conditions.setObjectName("lbl_access_conditions")
        self.gridLayout.addWidget(self.lbl_access_conditions, 1, 0, 1, 2)
        self.verticalLayout.addWidget(self.grb_need_account)

        self.retranslateUi(dlg_form_auth_prompt)
        self.btn_ok_cancel.accepted.connect(dlg_form_auth_prompt.accept)
        self.btn_ok_cancel.rejected.connect(dlg_form_auth_prompt.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_form_auth_prompt)

    def retranslateUi(self, dlg_form_auth_prompt):
        _translate = QtCore.QCoreApplication.translate
        dlg_form_auth_prompt.setWindowTitle(
            _translate("dlg_form_auth_prompt", "Isogeo authentication settings")
        )
        self.grb_connection_ready.setTitle(
            _translate(
                "dlg_form_auth_prompt", "I already have Isogeo ID and SECRET for this application"
            )
        )
        self.ent_app_id.setPlaceholderText(
            _translate("dlg_form_auth_prompt", "plugin-qgis-org-a1b23c4d5f6g7h8i9j10kl11mn13op14")
        )
        self.lbl_app_secret.setText(_translate("dlg_form_auth_prompt", "Application SECRET:"))
        self.chb_isogeo_editor.setText(
            _translate("dlg_form_auth_prompt", "I've got edition rights on app.isogeo.com")
        )
        self.lbl_browse_credentials.setText(_translate("dlg_form_auth_prompt", "From a file:"))
        self.lbl_app_id.setText(_translate("dlg_form_auth_prompt", "Application ID:"))
        self.lbl_api_url.setToolTip(
            _translate("dlg_form_auth_prompt", "Only for information, the Isogeo API base URL")
        )
        self.lbl_api_url.setText(_translate("dlg_form_auth_prompt", "API location:"))
        self.btn_browse_credentials.setToolTip(
            _translate("dlg_form_auth_prompt", "Pick your credentials file")
        )
        self.btn_browse_credentials.setDialogTitle(
            _translate("dlg_form_auth_prompt", "Locate the Isogeo API credentials file")
        )
        self.grb_need_account.setTitle(
            _translate("dlg_form_auth_prompt", "Don't have an account yet ?")
        )
        self.btn_rdv_isogeo.setText(
            _translate("dlg_form_auth_prompt", "Make an appointment with Isogeo team")
        )
        self.btn_free_test.setText(
            _translate("dlg_form_auth_prompt", "Test the Isogeo QGIS Plugin for free")
        )
        self.lbl_access_conditions.setText(
            _translate(
                "dlg_form_auth_prompt",
                "<html><head/><body><p>It is simple and free to test the Isogeo QGIS Plugin on a sample of data : </p></body></html>",
            )
        )


from qgsfilewidget import QgsFileWidget

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dlg_form_auth_prompt = QtWidgets.QDialog()
    ui = Ui_dlg_form_auth_prompt()
    ui.setupUi(dlg_form_auth_prompt)
    dlg_form_auth_prompt.show()
    sys.exit(app.exec_())
