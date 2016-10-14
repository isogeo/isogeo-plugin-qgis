# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_authentication.ui'
#
# Created: Fri Oct 14 15:25:36 2016
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
        dlg_form_auth_prompt.resize(575, 225)
        dlg_form_auth_prompt.setMinimumSize(QtCore.QSize(575, 225))
        dlg_form_auth_prompt.setMaximumSize(QtCore.QSize(575, 225))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/ui/resources/settings.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlg_form_auth_prompt.setWindowIcon(icon)
        dlg_form_auth_prompt.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.grb_need_account = QtGui.QGroupBox(dlg_form_auth_prompt)
        self.grb_need_account.setGeometry(QtCore.QRect(9, 110, 557, 71))
        self.grb_need_account.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.grb_need_account.setObjectName(_fromUtf8("grb_need_account"))
        self.btn_account_new = QtGui.QPushButton(self.grb_need_account)
        self.btn_account_new.setGeometry(QtCore.QRect(140, 30, 250, 25))
        self.btn_account_new.setMinimumSize(QtCore.QSize(200, 20))
        self.btn_account_new.setMaximumSize(QtCore.QSize(250, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/ui/resources/keys.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_account_new.setIcon(icon1)
        self.btn_account_new.setObjectName(_fromUtf8("btn_account_new"))
        self.grb_connection_ready = QtGui.QGroupBox(dlg_form_auth_prompt)
        self.grb_connection_ready.setGeometry(QtCore.QRect(9, 9, 557, 81))
        self.grb_connection_ready.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.grb_connection_ready.setObjectName(_fromUtf8("grb_connection_ready"))
        self.ent_app_id = QtGui.QLineEdit(self.grb_connection_ready)
        self.ent_app_id.setGeometry(QtCore.QRect(130, 20, 410, 20))
        self.ent_app_id.setMinimumSize(QtCore.QSize(410, 20))
        self.ent_app_id.setMaximumSize(QtCore.QSize(410, 20))
        self.ent_app_id.setObjectName(_fromUtf8("ent_app_id"))
        self.ent_app_secret = QtGui.QLineEdit(self.grb_connection_ready)
        self.ent_app_secret.setGeometry(QtCore.QRect(130, 50, 410, 20))
        self.ent_app_secret.setMinimumSize(QtCore.QSize(410, 20))
        self.ent_app_secret.setMaximumSize(QtCore.QSize(410, 20))
        self.ent_app_secret.setText(_fromUtf8(""))
        self.ent_app_secret.setMaxLength(64)
        self.ent_app_secret.setObjectName(_fromUtf8("ent_app_secret"))
        self.lbl_app_id = QtGui.QLabel(self.grb_connection_ready)
        self.lbl_app_id.setGeometry(QtCore.QRect(10, 20, 96, 16))
        self.lbl_app_id.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.lbl_app_id.setObjectName(_fromUtf8("lbl_app_id"))
        self.lbl_app_secret = QtGui.QLabel(self.grb_connection_ready)
        self.lbl_app_secret.setGeometry(QtCore.QRect(10, 50, 121, 16))
        self.lbl_app_secret.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.lbl_app_secret.setObjectName(_fromUtf8("lbl_app_secret"))
        self.btn_ok_cancel = QtGui.QDialogButtonBox(dlg_form_auth_prompt)
        self.btn_ok_cancel.setGeometry(QtCore.QRect(410, 193, 156, 23))
        self.btn_ok_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_ok_cancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.btn_ok_cancel.setCenterButtons(False)
        self.btn_ok_cancel.setObjectName(_fromUtf8("btn_ok_cancel"))

        self.retranslateUi(dlg_form_auth_prompt)
        QtCore.QObject.connect(self.btn_ok_cancel, QtCore.SIGNAL(_fromUtf8("accepted()")), dlg_form_auth_prompt.accept)
        QtCore.QObject.connect(self.btn_ok_cancel, QtCore.SIGNAL(_fromUtf8("rejected()")), dlg_form_auth_prompt.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_form_auth_prompt)

    def retranslateUi(self, dlg_form_auth_prompt):
        dlg_form_auth_prompt.setWindowTitle(_translate("dlg_form_auth_prompt", "Isogeo authentication settings", None))
        self.grb_need_account.setTitle(_translate("dlg_form_auth_prompt", "Don\'t have an account yet ?", None))
        self.btn_account_new.setText(_translate("dlg_form_auth_prompt", "Request plugin access", None))
        self.grb_connection_ready.setTitle(_translate("dlg_form_auth_prompt", "I already have Isogeo ID and SECRET for this application", None))
        self.lbl_app_id.setText(_translate("dlg_form_auth_prompt", "Application ID:", None))
        self.lbl_app_secret.setText(_translate("dlg_form_auth_prompt", "Application SECRET:", None))

