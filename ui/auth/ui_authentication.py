# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\auth\ui_authentication.ui'
#
# Created: Mon Mar 27 20:58:22 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dlg_form_auth_prompt(object):
    def setupUi(self, dlg_form_auth_prompt):
        dlg_form_auth_prompt.setObjectName(_fromUtf8("dlg_form_auth_prompt"))
        dlg_form_auth_prompt.resize(783, 300)
        dlg_form_auth_prompt.setMinimumSize(QtCore.QSize(750, 300))
        dlg_form_auth_prompt.setMaximumSize(QtCore.QSize(800, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ui/resources/settings.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlg_form_auth_prompt.setWindowIcon(icon)
        dlg_form_auth_prompt.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        dlg_form_auth_prompt.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(dlg_form_auth_prompt)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.grb_connection_ready = QtGui.QGroupBox(dlg_form_auth_prompt)
        self.grb_connection_ready.setMinimumSize(QtCore.QSize(500, 135))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.grb_connection_ready.setFont(font)
        self.grb_connection_ready.setAutoFillBackground(True)
        self.grb_connection_ready.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.grb_connection_ready.setFlat(True)
        self.grb_connection_ready.setObjectName(_fromUtf8("grb_connection_ready"))
        self.gridLayout_2 = QtGui.QGridLayout(self.grb_connection_ready)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lbl_app_secret = QtGui.QLabel(self.grb_connection_ready)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_app_secret.sizePolicy().hasHeightForWidth())
        self.lbl_app_secret.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_app_secret.setFont(font)
        self.lbl_app_secret.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.lbl_app_secret.setObjectName(_fromUtf8("lbl_app_secret"))
        self.gridLayout_2.addWidget(self.lbl_app_secret, 1, 1, 1, 1)
        self.lbl_app_id = QtGui.QLabel(self.grb_connection_ready)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbl_app_id.sizePolicy().hasHeightForWidth())
        self.lbl_app_id.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_app_id.setFont(font)
        self.lbl_app_id.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.lbl_app_id.setObjectName(_fromUtf8("lbl_app_id"))
        self.gridLayout_2.addWidget(self.lbl_app_id, 0, 1, 1, 1)
        self.ent_app_id = QtGui.QLineEdit(self.grb_connection_ready)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ent_app_id.sizePolicy().hasHeightForWidth())
        self.ent_app_id.setSizePolicy(sizePolicy)
        self.ent_app_id.setMinimumSize(QtCore.QSize(475, 20))
        self.ent_app_id.setMaximumSize(QtCore.QSize(800, 20))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.ent_app_id.setFont(font)
        self.ent_app_id.setObjectName(_fromUtf8("ent_app_id"))
        self.gridLayout_2.addWidget(self.ent_app_id, 0, 2, 1, 1)
        self.btn_check_auth = QtGui.QPushButton(self.grb_connection_ready)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_check_auth.sizePolicy().hasHeightForWidth())
        self.btn_check_auth.setSizePolicy(sizePolicy)
        self.btn_check_auth.setMinimumSize(QtCore.QSize(0, 50))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_check_auth.setFont(font)
        self.btn_check_auth.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/Isogeo/resources/sign-in.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_check_auth.setIcon(icon1)
        self.btn_check_auth.setDefault(True)
        self.btn_check_auth.setObjectName(_fromUtf8("btn_check_auth"))
        self.gridLayout_2.addWidget(self.btn_check_auth, 0, 4, 2, 1)
        self.btn_ok_cancel = QtGui.QDialogButtonBox(self.grb_connection_ready)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
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
        self.btn_ok_cancel.setAutoFillBackground(True)
        self.btn_ok_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_ok_cancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.btn_ok_cancel.setCenterButtons(True)
        self.btn_ok_cancel.setObjectName(_fromUtf8("btn_ok_cancel"))
        self.gridLayout_2.addWidget(self.btn_ok_cancel, 2, 0, 1, 5)
        self.ent_app_secret = QtGui.QLineEdit(self.grb_connection_ready)
        self.ent_app_secret.setMinimumSize(QtCore.QSize(475, 20))
        self.ent_app_secret.setMaximumSize(QtCore.QSize(800, 20))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.ent_app_secret.setFont(font)
        self.ent_app_secret.setText(_fromUtf8(""))
        self.ent_app_secret.setMaxLength(64)
        self.ent_app_secret.setObjectName(_fromUtf8("ent_app_secret"))
        self.gridLayout_2.addWidget(self.ent_app_secret, 1, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 3, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem1, 1, 3, 1, 1)
        self.verticalLayout.addWidget(self.grb_connection_ready)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.grb_need_account = QtGui.QGroupBox(dlg_form_auth_prompt)
        self.grb_need_account.setMinimumSize(QtCore.QSize(200, 150))
        self.grb_need_account.setMaximumSize(QtCore.QSize(16777215, 200))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.grb_need_account.setFont(font)
        self.grb_need_account.setAutoFillBackground(True)
        self.grb_need_account.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.grb_need_account.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.grb_need_account.setFlat(True)
        self.grb_need_account.setObjectName(_fromUtf8("grb_need_account"))
        self.gridLayout = QtGui.QGridLayout(self.grb_need_account)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btn_account_new = QtGui.QPushButton(self.grb_need_account)
        self.btn_account_new.setMinimumSize(QtCore.QSize(200, 30))
        self.btn_account_new.setMaximumSize(QtCore.QSize(700, 50))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_account_new.setFont(font)
        self.btn_account_new.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_account_new.setAutoFillBackground(True)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/Isogeo/resources/send-o.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_account_new.setIcon(icon2)
        self.btn_account_new.setDefault(True)
        self.btn_account_new.setObjectName(_fromUtf8("btn_account_new"))
        self.gridLayout.addWidget(self.btn_account_new, 1, 0, 1, 1)
        self.lbl_access_conditions = QtGui.QLabel(self.grb_need_account)
        self.lbl_access_conditions.setMaximumSize(QtCore.QSize(700, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_access_conditions.setFont(font)
        self.lbl_access_conditions.setTextFormat(QtCore.Qt.RichText)
        self.lbl_access_conditions.setObjectName(_fromUtf8("lbl_access_conditions"))
        self.gridLayout.addWidget(self.lbl_access_conditions, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.grb_need_account)

        self.retranslateUi(dlg_form_auth_prompt)
        QtCore.QObject.connect(self.btn_ok_cancel, QtCore.SIGNAL(_fromUtf8("accepted()")), dlg_form_auth_prompt.accept)
        QtCore.QObject.connect(self.btn_ok_cancel, QtCore.SIGNAL(_fromUtf8("rejected()")), dlg_form_auth_prompt.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_form_auth_prompt)

    def retranslateUi(self, dlg_form_auth_prompt):
        dlg_form_auth_prompt.setWindowTitle(_translate("dlg_form_auth_prompt", "Isogeo authentication settings", None))
        self.grb_connection_ready.setTitle(_translate("dlg_form_auth_prompt", "I already have Isogeo ID and SECRET for this application", None))
        self.lbl_app_secret.setText(_translate("dlg_form_auth_prompt", "Application SECRET:", None))
        self.lbl_app_id.setText(_translate("dlg_form_auth_prompt", "Application ID:", None))
        self.btn_check_auth.setToolTip(_translate("dlg_form_auth_prompt", "Check access validity", None))
        self.btn_check_auth.setText(_translate("dlg_form_auth_prompt", "Check", None))
        self.grb_need_account.setTitle(_translate("dlg_form_auth_prompt", "Don\'t have an account yet ?", None))
        self.btn_account_new.setText(_translate("dlg_form_auth_prompt", "Request plugin access", None))
        self.lbl_access_conditions.setText(_translate("dlg_form_auth_prompt", "<!DOCTYPE html>\n"
"<html>\n"
"<body>\n"
"\n"
"<ul>\n"
"    <li>Completely free to access generic Open Data</li>\n"
"    <li>Completely free to work with 20 of your geographic data and services (Isogeo account required)</li>\n"
"    <li>Ask for our annual plans to work with your whole geographic data and services !</li>\n"
"</ul> \n"
"\n"
"</body>\n"
"</html>\n"
"", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg_form_auth_prompt = QtGui.QDialog()
    ui = Ui_dlg_form_auth_prompt()
    ui.setupUi(dlg_form_auth_prompt)
    dlg_form_auth_prompt.show()
    sys.exit(app.exec_())

