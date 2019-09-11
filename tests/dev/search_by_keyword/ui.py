# PyQt
from qgis.PyQt.QtWidgets import QApplication, QPushButton, QLabel, QWidget, QVBoxLayout, QComboBox, QGridLayout
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QStandardItemModel

# Custom widget
from checkable_combobox import CheckableComboBox

class AuthWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.lbl_expected = QLabel()
        self.lbl_expected.setAlignment(Qt.AlignCenter)
        self.lbl_found = QLabel()
        self.lbl_found.setAlignment(Qt.AlignCenter)
        self.lbl_selection = QLabel()
        self.lbl_selection.setAlignment(Qt.AlignCenter)
        self.kw_cbbox = CheckableComboBox()
        self.btn_reset = QPushButton("Reset")

        self.layout = QGridLayout()
        self.layout.addWidget(self.lbl_expected, 1, 0, 1, 2)
        self.layout.addWidget(self.lbl_found, 2, 0, 1, 2)
        self.layout.addWidget(self.kw_cbbox, 3, 0)
        self.layout.addWidget(self.btn_reset, 3, 1)
        self.layout.addWidget(self.lbl_selection, 4, 0, 1, 2)
        self.setLayout(self.layout)

        self.setWindowTitle("Select Isogeo keywords using PyQT")


if __name__ == "__main__":
    app = QApplication([])

    widget = AuthWidget()
    widget.resize(300, 300)
    widget.show()
    app.exec()