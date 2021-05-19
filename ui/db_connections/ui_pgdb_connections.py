# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\db_connections\ui_pgdb_connections.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlg_pgdb_connections(object):
    def setupUi(self, dlg_pgdb_connections):
        dlg_pgdb_connections.setObjectName("dlg_pgdb_connections")
        dlg_pgdb_connections.resize(490, 300)
        dlg_pgdb_connections.setMinimumSize(QtCore.QSize(490, 200))
        dlg_pgdb_connections.setMaximumSize(QtCore.QSize(500, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/gear.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        dlg_pgdb_connections.setWindowIcon(icon)
        dlg_pgdb_connections.setWindowOpacity(0.95)
        dlg_pgdb_connections.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        dlg_pgdb_connections.setSizeGripEnabled(False)
        self.gridLayout = QtWidgets.QGridLayout(dlg_pgdb_connections)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(dlg_pgdb_connections)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(490, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAcceptDrops(True)
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.tbl = QtWidgets.QTableWidget(dlg_pgdb_connections)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tbl.sizePolicy().hasHeightForWidth())
        self.tbl.setSizePolicy(sizePolicy)
        self.tbl.setMinimumSize(QtCore.QSize(0, 100))
        self.tbl.setMaximumSize(QtCore.QSize(16777215, 200))
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
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_reload_conn = QtWidgets.QPushButton(dlg_pgdb_connections)
        self.btn_reload_conn.setMinimumSize(QtCore.QSize(200, 0))
        self.btn_reload_conn.setMaximumSize(QtCore.QSize(200, 16777215))
        self.btn_reload_conn.setObjectName("btn_reload_conn")
        self.horizontalLayout_2.addWidget(self.btn_reload_conn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem1 = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.verticalLayout.addItem(spacerItem1)
        self.btnbox = QtWidgets.QDialogButtonBox(dlg_pgdb_connections)
        self.btnbox.setMaximumSize(QtCore.QSize(600, 16777215))
        self.btnbox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btnbox.setAutoFillBackground(False)
        self.btnbox.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.btnbox.setOrientation(QtCore.Qt.Horizontal)
        self.btnbox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel
            | QtWidgets.QDialogButtonBox.Reset
            | QtWidgets.QDialogButtonBox.Save
        )
        self.btnbox.setCenterButtons(True)
        self.btnbox.setObjectName("btnbox")
        self.verticalLayout.addWidget(self.btnbox)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(dlg_pgdb_connections)
        self.btnbox.accepted.connect(dlg_pgdb_connections.accept)
        self.btnbox.rejected.connect(dlg_pgdb_connections.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_pgdb_connections)

    def retranslateUi(self, dlg_pgdb_connections):
        _translate = QtCore.QCoreApplication.translate
        dlg_pgdb_connections.setWindowTitle(
            _translate("dlg_pgdb_connections", "PostGIS database configuration")
        )
        self.label.setText(
            _translate(
                "dlg_pgdb_connections",
                "Choose the embed connection to be used to access to each PostGIS database",
            )
        )
        self.tbl.setSortingEnabled(False)
        self.btn_reload_conn.setText(
            _translate("dlg_pgdb_connections", "Reload embed connection(s)")
        )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dlg_pgdb_connections = QtWidgets.QDialog()
    ui = Ui_dlg_pgdb_connections()
    ui.setupUi(dlg_pgdb_connections)
    dlg_pgdb_connections.show()
    sys.exit(app.exec_())
