# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\quicksearch\ui_quicksearch_new.ui'
#
# Created: Fri Apr 28 17:51:14 2017
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

class Ui_dlg_quicksearch_new(object):
    def setupUi(self, dlg_quicksearch_new):
        dlg_quicksearch_new.setObjectName(_fromUtf8("dlg_quicksearch_new"))
        dlg_quicksearch_new.setWindowModality(QtCore.Qt.WindowModal)
        dlg_quicksearch_new.resize(468, 100)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(dlg_quicksearch_new.sizePolicy().hasHeightForWidth())
        dlg_quicksearch_new.setSizePolicy(sizePolicy)
        dlg_quicksearch_new.setMinimumSize(QtCore.QSize(340, 100))
        dlg_quicksearch_new.setMaximumSize(QtCore.QSize(700, 110))
        dlg_quicksearch_new.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/Isogeo/resources/bolt.svg")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        dlg_quicksearch_new.setWindowIcon(icon)
        dlg_quicksearch_new.setWindowOpacity(0.9)
        dlg_quicksearch_new.setAutoFillBackground(True)
        dlg_quicksearch_new.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        dlg_quicksearch_new.setSizeGripEnabled(False)
        dlg_quicksearch_new.setModal(True)
        self.gridLayout = QtGui.QGridLayout(dlg_quicksearch_new)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        spacerItem = QtGui.QSpacerItem(20, 62, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 3)
        self.lbl_title = QtGui.QLabel(dlg_quicksearch_new)
        self.lbl_title.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_title.setFont(font)
        self.lbl_title.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.lbl_title.setAutoFillBackground(True)
        self.lbl_title.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.lbl_title.setObjectName(_fromUtf8("lbl_title"))
        self.gridLayout.addWidget(self.lbl_title, 0, 0, 1, 1)
        self.btn_save_cancel = QtGui.QDialogButtonBox(dlg_quicksearch_new)
        self.btn_save_cancel.setOrientation(QtCore.Qt.Horizontal)
        self.btn_save_cancel.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.btn_save_cancel.setCenterButtons(True)
        self.btn_save_cancel.setObjectName(_fromUtf8("btn_save_cancel"))
        self.gridLayout.addWidget(self.btn_save_cancel, 2, 0, 1, 4)
        self.txt_quicksearch_name = QtGui.QLineEdit(dlg_quicksearch_new)
        self.txt_quicksearch_name.setMinimumSize(QtCore.QSize(50, 25))
        self.txt_quicksearch_name.setObjectName(_fromUtf8("txt_quicksearch_name"))
        self.gridLayout.addWidget(self.txt_quicksearch_name, 0, 1, 1, 3)

        self.retranslateUi(dlg_quicksearch_new)
        QtCore.QObject.connect(self.btn_save_cancel, QtCore.SIGNAL(_fromUtf8("accepted()")), dlg_quicksearch_new.accept)
        QtCore.QObject.connect(self.btn_save_cancel, QtCore.SIGNAL(_fromUtf8("rejected()")), dlg_quicksearch_new.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_quicksearch_new)

    def retranslateUi(self, dlg_quicksearch_new):
        dlg_quicksearch_new.setWindowTitle(_translate("dlg_quicksearch_new", "Isogeo - New quicksearch", None))
        self.lbl_title.setText(_translate("dlg_quicksearch_new", "Quicksearch name:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    dlg_quicksearch_new = QtGui.QDialog()
    ui = Ui_dlg_quicksearch_new()
    ui.setupUi(dlg_quicksearch_new)
    dlg_quicksearch_new.show()
    sys.exit(app.exec_())

