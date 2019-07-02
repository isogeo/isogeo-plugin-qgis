from qgis.PyQt.QtWidgets import QApplication, QPushButton, QLabel, QWidget, QVBoxLayout
from qgis.PyQt.QtCore import Qt

class AuthWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.btn = QPushButton("Launch")
        self.lbl_expected = QLabel()
        self.lbl_expected.setAlignment(Qt.AlignCenter)
        self.lbl_found = QLabel()
        self.lbl_found.setAlignment(Qt.AlignCenter)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.btn)
        self.layout.addWidget(self.lbl_expected)
        self.layout.addWidget(self.lbl_found)
        self.setLayout(self.layout)

        self.setWindowTitle("Connect to Isogeo API using PyQT")


if __name__ == "__main__":
    app = QApplication([])

    widget = AuthWidget()
    widget.resize(400, 100)
    widget.show()
    app.exec()