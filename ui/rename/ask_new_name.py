# -*- coding: utf-8 -*-

import os

from PyQt4 import QtGui, uic
from PyQt4.QtCore import pyqtSignal


from ui_ask_new_name import Ui_Rename



class ask_new_name(QtGui.QDialog, Ui_Rename):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(ask_new_name, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
