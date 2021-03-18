# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\db_connections\ui_db_connections.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_dlg_db_connections(object):
    def setupUi(self, dlg_db_connections):
        dlg_db_connections.setObjectName("dlg_db_connections")
        dlg_db_connections.resize(490, 300)
        dlg_db_connections.setMinimumSize(QtCore.QSize(490, 200))
        dlg_db_connections.setMaximumSize(QtCore.QSize(500, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/Isogeo/resources/settings/gear.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlg_db_connections.setWindowIcon(icon)
        dlg_db_connections.setWindowOpacity(0.95)
        dlg_db_connections.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        dlg_db_connections.setSizeGripEnabled(False)
        self.gridLayout = QtWidgets.QGridLayout(dlg_db_connections)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(dlg_db_connections)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(490, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tbl = QtWidgets.QTableWidget(dlg_db_connections)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tbl.sizePolicy().hasHeightForWidth())
        self.tbl.setSizePolicy(sizePolicy)
        self.tbl.setMinimumSize(QtCore.QSize(0, 0))
        self.tbl.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.tbl.setAutoFillBackground(False)
        self.tbl.setEditTriggers(QtWidgets.QAbstractItemView.CurrentChanged)
        self.tbl.setAlternatingRowColors(False)
        self.tbl.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.tbl.setRowCount(0)
        self.tbl.setColumnCount(2)
        self.tbl.setObjectName("tbl")
        self.tbl.horizontalHeader().setVisible(True)
        self.tbl.horizontalHeader().setCascadingSectionResizes(False)
        self.tbl.horizontalHeader().setDefaultSectionSize(230)
        self.tbl.horizontalHeader().setHighlightSections(False)
        self.tbl.horizontalHeader().setMinimumSectionSize(20)
        self.tbl.horizontalHeader().setSortIndicatorShown(False)
        self.tbl.horizontalHeader().setStretchLastSection(False)
        self.tbl.verticalHeader().setVisible(False)
        self.horizontalLayout.addWidget(self.tbl)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.btnbox = QtWidgets.QDialogButtonBox(dlg_db_connections)
        self.btnbox.setMaximumSize(QtCore.QSize(600, 16777215))
        self.btnbox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btnbox.setAutoFillBackground(False)
        self.btnbox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.btnbox.setOrientation(QtCore.Qt.Horizontal)
        self.btnbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Reset|QtWidgets.QDialogButtonBox.Save)
        self.btnbox.setCenterButtons(True)
        self.btnbox.setObjectName("btnbox")
        self.verticalLayout.addWidget(self.btnbox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(dlg_db_connections)
        self.btnbox.accepted.connect(dlg_db_connections.accept)
        self.btnbox.rejected.connect(dlg_db_connections.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_db_connections)

    def retranslateUi(self, dlg_db_connections):
        _translate = QtCore.QCoreApplication.translate
        dlg_db_connections.setWindowTitle(_translate("dlg_db_connections", "PostGIS database configuration"))
        self.label.setText(_translate("dlg_db_connections", "Choose the embed connection to be used to access to each PostGIS database"))
        self.tbl.setSortingEnabled(False)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dlg_db_connections = QtWidgets.QDialog()
    ui = Ui_dlg_db_connections()
    ui.setupUi(dlg_db_connections)
    dlg_db_connections.show()
    sys.exit(app.exec_())

