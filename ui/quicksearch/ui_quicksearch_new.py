# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\quicksearch\ui_quicksearch_new.ui'
#
# Created: Thu Dec 29 18:30:11 2016
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

class Ui_Name(object):
    def setupUi(self, Name):
        Name.setObjectName(_fromUtf8("Name"))
        Name.resize(498, 189)
        self.gridLayout = QtGui.QGridLayout(Name)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Name)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.name = QtGui.QLineEdit(Name)
        self.name.setObjectName(_fromUtf8("name"))
        self.gridLayout.addWidget(self.name, 2, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(238, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 4, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(Name)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 4, 1, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 62, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 3, 0, 1, 1)
        self.label_2 = QtGui.QLabel(Name)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_2.setFont(font)
        self.label_2.setText(_fromUtf8(""))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)

        self.retranslateUi(Name)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Name.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Name.reject)
        QtCore.QMetaObject.connectSlotsByName(Name)

    def retranslateUi(self, Name):
        Name.setWindowTitle(_translate("Name", "Dialog", None))
        self.label.setText(_translate("Name", "Please name your saved research.", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Name = QtGui.QDialog()
    ui = Ui_Name()
    ui.setupUi(Name)
    Name.show()
    sys.exit(app.exec_())

