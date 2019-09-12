# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\quicksearch\ui_quicksearch_rename.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlg_quicksearch_rename(object):
    def setupUi(self, dlg_quicksearch_rename):
        dlg_quicksearch_rename.setObjectName("dlg_quicksearch_rename")
        dlg_quicksearch_rename.resize(498, 100)
        dlg_quicksearch_rename.setMinimumSize(QtCore.QSize(340, 100))
        dlg_quicksearch_rename.setMaximumSize(QtCore.QSize(700, 116))
        dlg_quicksearch_rename.setFocusPolicy(QtCore.Qt.StrongFocus)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/bolt.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        dlg_quicksearch_rename.setWindowIcon(icon)
        dlg_quicksearch_rename.setWindowOpacity(0.9)
        dlg_quicksearch_rename.setAutoFillBackground(True)
        dlg_quicksearch_rename.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        dlg_quicksearch_rename.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(dlg_quicksearch_rename)
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_title = QtWidgets.QLabel(dlg_quicksearch_rename)
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.lbl_title.setAutoFillBackground(True)
        self.lbl_title.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.lbl_title.setObjectName("lbl_title")
        self.gridLayout.addWidget(self.lbl_title, 0, 1, 1, 1)
        self.txt_quicksearch_rename = QtWidgets.QLineEdit(dlg_quicksearch_rename)
        self.txt_quicksearch_rename.setMinimumSize(QtCore.QSize(50, 25))
        self.txt_quicksearch_rename.setObjectName("txt_quicksearch_rename")
        self.gridLayout.addWidget(self.txt_quicksearch_rename, 0, 2, 1, 1)
        self.btn_save_cancel = QtWidgets.QDialogButtonBox(dlg_quicksearch_rename)
        self.btn_save_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_save_cancel.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save
        )
        self.btn_save_cancel.setCenterButtons(True)
        self.btn_save_cancel.setObjectName("btn_save_cancel")
        self.gridLayout.addWidget(self.btn_save_cancel, 2, 0, 1, 3)

        self.retranslateUi(dlg_quicksearch_rename)
        self.btn_save_cancel.accepted.connect(dlg_quicksearch_rename.accept)
        self.btn_save_cancel.rejected.connect(dlg_quicksearch_rename.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_quicksearch_rename)

    def retranslateUi(self, dlg_quicksearch_rename):
        _translate = QtCore.QCoreApplication.translate
        dlg_quicksearch_rename.setWindowTitle(
            _translate("dlg_quicksearch_rename", "Isogeo - Rename quicksearch")
        )
        self.lbl_title.setText(
            _translate("dlg_quicksearch_rename", "Quicksearch new name:")
        )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dlg_quicksearch_rename = QtWidgets.QDialog()
    ui = Ui_dlg_quicksearch_rename()
    ui.setupUi(dlg_quicksearch_rename)
    dlg_quicksearch_rename.show()
    sys.exit(app.exec_())
