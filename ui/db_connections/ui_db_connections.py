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
        dlg_db_connections.resize(490, 200)
        dlg_db_connections.setMinimumSize(QtCore.QSize(490, 200))
        dlg_db_connections.setMaximumSize(QtCore.QSize(500, 300))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/plugins/Isogeo/resources/gavel.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
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
        self.cbb_label = QtWidgets.QLabel(dlg_db_connections)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbb_label.sizePolicy().hasHeightForWidth())
        self.cbb_label.setSizePolicy(sizePolicy)
        self.cbb_label.setMaximumSize(QtCore.QSize(490, 20))
        self.cbb_label.setObjectName("cbb_label")
        self.verticalLayout.addWidget(self.cbb_label)
        self.connections_cbb = QtWidgets.QComboBox(dlg_db_connections)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.connections_cbb.sizePolicy().hasHeightForWidth())
        self.connections_cbb.setSizePolicy(sizePolicy)
        self.connections_cbb.setObjectName("connections_cbb")
        self.verticalLayout.addWidget(self.connections_cbb)
        self.btn_ok_close = QtWidgets.QDialogButtonBox(dlg_db_connections)
        self.btn_ok_close.setMaximumSize(QtCore.QSize(500, 16777215))
        self.btn_ok_close.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btn_ok_close.setAutoFillBackground(False)
        self.btn_ok_close.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.btn_ok_close.setOrientation(QtCore.Qt.Horizontal)
        self.btn_ok_close.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel)
        self.btn_ok_close.setCenterButtons(True)
        self.btn_ok_close.setObjectName("btn_ok_close")
        self.verticalLayout.addWidget(self.btn_ok_close)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(dlg_db_connections)
        self.btn_ok_close.accepted.connect(dlg_db_connections.accept)
        self.btn_ok_close.rejected.connect(dlg_db_connections.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_db_connections)

    def retranslateUi(self, dlg_db_connections):
        _translate = QtCore.QCoreApplication.translate
        dlg_db_connections.setWindowTitle(_translate("dlg_db_connections", "db_connections"))
        self.cbb_label.setText(_translate("dlg_db_connections", "Choose the registered connection to use to add \'{}\' layer from \'{}\' database:"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dlg_db_connections = QtWidgets.QDialog()
    ui = Ui_dlg_db_connections()
    ui.setupUi(dlg_db_connections)
    dlg_db_connections.show()
    sys.exit(app.exec_())

