# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\quicksearch\ui_quicksearch_new.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlg_quicksearch_new(object):
    def setupUi(self, dlg_quicksearch_new):
        dlg_quicksearch_new.setObjectName("dlg_quicksearch_new")
        dlg_quicksearch_new.setWindowModality(QtCore.Qt.WindowModal)
        dlg_quicksearch_new.resize(468, 100)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            dlg_quicksearch_new.sizePolicy().hasHeightForWidth()
        )
        dlg_quicksearch_new.setSizePolicy(sizePolicy)
        dlg_quicksearch_new.setMinimumSize(QtCore.QSize(340, 100))
        dlg_quicksearch_new.setMaximumSize(QtCore.QSize(700, 110))
        dlg_quicksearch_new.setFocusPolicy(QtCore.Qt.StrongFocus)
        dlg_quicksearch_new.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/bolt.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        dlg_quicksearch_new.setWindowIcon(icon)
        dlg_quicksearch_new.setWindowOpacity(0.9)
        dlg_quicksearch_new.setAutoFillBackground(True)
        dlg_quicksearch_new.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        dlg_quicksearch_new.setSizeGripEnabled(False)
        dlg_quicksearch_new.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(dlg_quicksearch_new)
        self.gridLayout.setObjectName("gridLayout")
        self.lbl_title = QtWidgets.QLabel(dlg_quicksearch_new)
        self.lbl_title.setMinimumSize(QtCore.QSize(0, 25))
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
        self.gridLayout.addWidget(self.lbl_title, 0, 0, 1, 1)
        self.txt_quicksearch_name = QtWidgets.QLineEdit(dlg_quicksearch_new)
        self.txt_quicksearch_name.setMinimumSize(QtCore.QSize(50, 25))
        self.txt_quicksearch_name.setObjectName("txt_quicksearch_name")
        self.gridLayout.addWidget(self.txt_quicksearch_name, 0, 1, 1, 2)
        self.btn_save_cancel = QtWidgets.QDialogButtonBox(dlg_quicksearch_new)
        self.btn_save_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_save_cancel.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save
        )
        self.btn_save_cancel.setCenterButtons(True)
        self.btn_save_cancel.setObjectName("btn_save_cancel")
        self.gridLayout.addWidget(self.btn_save_cancel, 1, 0, 1, 3)

        self.retranslateUi(dlg_quicksearch_new)
        self.btn_save_cancel.accepted.connect(dlg_quicksearch_new.accept)
        self.btn_save_cancel.rejected.connect(dlg_quicksearch_new.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_quicksearch_new)

    def retranslateUi(self, dlg_quicksearch_new):
        _translate = QtCore.QCoreApplication.translate
        dlg_quicksearch_new.setWindowTitle(
            _translate("dlg_quicksearch_new", "Isogeo - New quicksearch")
        )
        self.lbl_title.setText(_translate("dlg_quicksearch_new", "Quicksearch name:"))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dlg_quicksearch_new = QtWidgets.QDialog()
    ui = Ui_dlg_quicksearch_new()
    ui.setupUi(dlg_quicksearch_new)
    dlg_quicksearch_new.show()
    sys.exit(app.exec_())
