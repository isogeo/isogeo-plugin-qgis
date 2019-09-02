"""
Provenance :
https://stackoverflow.com/questions/48280817/how-to-make-items-in-qcombobox-class-checkable-pyqt5/48283889#48283889
"""


# PyQT
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QComboBox
from qgis.PyQt.QtGui import QStandardItemModel

class CheckableComboBox(QComboBox):
    def __init__(self, parent = None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)
