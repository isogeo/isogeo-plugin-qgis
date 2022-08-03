# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\portal\ui_portal_base_url.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlg_portal_base_url(object):
    def setupUi(self, dlg_portal_base_url):
        dlg_portal_base_url.setObjectName("dlg_portal_base_url")
        dlg_portal_base_url.setWindowModality(QtCore.Qt.WindowModal)
        dlg_portal_base_url.resize(597, 110)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dlg_portal_base_url.sizePolicy().hasHeightForWidth())
        dlg_portal_base_url.setSizePolicy(sizePolicy)
        dlg_portal_base_url.setMinimumSize(QtCore.QSize(340, 100))
        dlg_portal_base_url.setMaximumSize(QtCore.QSize(700, 110))
        dlg_portal_base_url.setFocusPolicy(QtCore.Qt.StrongFocus)
        dlg_portal_base_url.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/edit.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        dlg_portal_base_url.setWindowIcon(icon)
        dlg_portal_base_url.setWindowOpacity(1.0)
        dlg_portal_base_url.setAutoFillBackground(True)
        dlg_portal_base_url.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        dlg_portal_base_url.setSizeGripEnabled(False)
        dlg_portal_base_url.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(dlg_portal_base_url)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbl_title = QtWidgets.QLabel(dlg_portal_base_url)
        self.lbl_title.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.lbl_title.setFont(font)
        self.lbl_title.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.lbl_title.setAutoFillBackground(True)
        self.lbl_title.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.lbl_title.setObjectName("lbl_title")
        self.horizontalLayout.addWidget(self.lbl_title)
        self.input_portal_url = QtWidgets.QLineEdit(dlg_portal_base_url)
        self.input_portal_url.setMinimumSize(QtCore.QSize(50, 25))
        self.input_portal_url.setObjectName("input_portal_url")
        self.horizontalLayout.addWidget(self.input_portal_url)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.chb_portal_url = QtWidgets.QCheckBox(dlg_portal_base_url)
        self.chb_portal_url.setObjectName("chb_portal_url")
        self.horizontalLayout_2.addWidget(self.chb_portal_url)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem)
        self.btn_save_cancel = QtWidgets.QDialogButtonBox(dlg_portal_base_url)
        self.btn_save_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_save_cancel.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Save
        )
        self.btn_save_cancel.setCenterButtons(True)
        self.btn_save_cancel.setObjectName("btn_save_cancel")
        self.verticalLayout.addWidget(self.btn_save_cancel)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(dlg_portal_base_url)
        self.btn_save_cancel.accepted.connect(dlg_portal_base_url.accept)
        self.btn_save_cancel.rejected.connect(dlg_portal_base_url.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_portal_base_url)

    def retranslateUi(self, dlg_portal_base_url):
        _translate = QtCore.QCoreApplication.translate
        dlg_portal_base_url.setWindowTitle(
            _translate("dlg_portal_base_url", "Isogeo - Portal base URL configuration")
        )
        self.lbl_title.setText(
            _translate("dlg_portal_base_url", "Specify the portal base URL here:")
        )
        self.chb_portal_url.setText(
            _translate("dlg_portal_base_url", "Add portal metadata URL to layer's properties")
        )


import resources_rc

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dlg_portal_base_url = QtWidgets.QDialog()
    ui = Ui_dlg_portal_base_url()
    ui.setupUi(dlg_portal_base_url)
    dlg_portal_base_url.show()
    sys.exit(app.exec_())
