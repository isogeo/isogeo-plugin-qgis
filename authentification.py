# -*- coding: utf-8 -*-

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal


from ui_authentification import Ui_Dialog



class authentification(QtGui.QDialog, Ui_Dialog):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(authentification, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
