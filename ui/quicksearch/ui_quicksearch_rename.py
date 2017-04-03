# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\quicksearch\ui_quicksearch_rename.ui'
#
# Created: Mon Apr 03 12:02:11 2017
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

class Ui_dlg_quicksearch_rename(object):
    def setupUi(self, dlg_quicksearch_rename):
        dlg_quicksearch_rename.setObjectName(_fromUtf8("dlg_quicksearch_rename"))
        dlg_quicksearch_rename.resize(498, 100)
        dlg_quicksearch_rename.setMinimumSize(QtCore.QSize(340, 100))
        dlg_quicksearch_rename.setMaximumSize(QtCore.QSize(700, 116))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/Isogeo/resources/bolt.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlg_quicksearch_rename.setWindowIcon(icon)
        dlg_quicksearch_rename.setWindowOpacity(0.9)
        dlg_quicksearch_rename.setAutoFillBackground(True)
        dlg_quicksearch_rename.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        dlg_quicksearch_rename.setModal(True)
        self.gridLayout = QtGui.QGridLayout(dlg_quicksearch_rename)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lbl_title = QtGui.QLabel(dlg_quicksearch_rename)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.lbl_title.setAutoFillBackground(True)
        self.lbl_title.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.lbl_title.setObjectName(_fromUtf8("lbl_title"))
        self.gridLayout.addWidget(self.lbl_title, 0, 1, 1, 1)
        self.txt_quicksearch_rename = QtGui.QLineEdit(dlg_quicksearch_rename)
        self.txt_quicksearch_rename.setMinimumSize(QtCore.QSize(50, 25))
        self.txt_quicksearch_rename.setObjectName(_fromUtf8("txt_quicksearch_rename"))
        self.gridLayout.addWidget(self.txt_quicksearch_rename, 0, 2, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 62, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 2)
        self.btn_save_cancel = QtGui.QDialogButtonBox(dlg_quicksearch_rename)
        self.btn_save_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_save_cancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.btn_save_cancel.setCenterButtons(True)
        self.btn_save_cancel.setObjectName(_fromUtf8("btn_save_cancel"))
        self.gridLayout.addWidget(self.btn_save_cancel, 3, 0, 1, 3)

        self.retranslateUi(dlg_quicksearch_rename)
        QtCore.QObject.connect(self.btn_save_cancel, QtCore.SIGNAL(_fromUtf8("accepted()")), dlg_quicksearch_rename.accept)
        QtCore.QObject.connect(self.btn_save_cancel, QtCore.SIGNAL(_fromUtf8("rejected()")), dlg_quicksearch_rename.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_quicksearch_rename)

    def retranslateUi(self, dlg_quicksearch_rename):
        dlg_quicksearch_rename.setWindowTitle(_translate("dlg_quicksearch_rename", "Isogeo - Rename quicksearch", None))
        self.lbl_title.setText(_translate("dlg_quicksearch_rename", "Quicksearch new name:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg_quicksearch_rename = QtGui.QDialog()
    ui = Ui_dlg_quicksearch_rename()
    ui.setupUi(dlg_quicksearch_rename)
    dlg_quicksearch_rename.show()
    sys.exit(app.exec_())

