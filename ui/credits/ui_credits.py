# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\credits\ui_credits.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_dlg_credits(object):
    def setupUi(self, dlg_credits):
        dlg_credits.setObjectName("dlg_credits")
        dlg_credits.resize(490, 560)
        dlg_credits.setMinimumSize(QtCore.QSize(490, 560))
        dlg_credits.setMaximumSize(QtCore.QSize(500, 560))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/gavel.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        dlg_credits.setWindowIcon(icon)
        dlg_credits.setWindowOpacity(0.95)
        dlg_credits.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        dlg_credits.setSizeGripEnabled(False)
        self.gridLayout = QtWidgets.QGridLayout(dlg_credits)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(5, 5, 5, 5)
        self.verticalLayout.setSpacing(12)
        self.verticalLayout.setObjectName("verticalLayout")
        self.grp_realization = QtWidgets.QGroupBox(dlg_credits)
        self.grp_realization.setMaximumSize(QtCore.QSize(500, 175))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.grp_realization.setFont(font)
        self.grp_realization.setFlat(True)
        self.grp_realization.setObjectName("grp_realization")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.grp_realization)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.lbl_isogeo_logo = QtWidgets.QLabel(self.grp_realization)
        self.lbl_isogeo_logo.setMinimumSize(QtCore.QSize(222, 102))
        self.lbl_isogeo_logo.setMaximumSize(QtCore.QSize(222, 102))
        self.lbl_isogeo_logo.setText("")
        self.lbl_isogeo_logo.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/credits/isogeo.png")
        )
        self.lbl_isogeo_logo.setScaledContents(False)
        self.lbl_isogeo_logo.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_isogeo_logo.setOpenExternalLinks(True)
        self.lbl_isogeo_logo.setObjectName("lbl_isogeo_logo")
        self.horizontalLayout_4.addWidget(self.lbl_isogeo_logo)
        self.lbl_isogeo_punchline = QtWidgets.QLabel(self.grp_realization)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setUnderline(True)
        font.setWeight(50)
        self.lbl_isogeo_punchline.setFont(font)
        self.lbl_isogeo_punchline.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_isogeo_punchline.setOpenExternalLinks(True)
        self.lbl_isogeo_punchline.setObjectName("lbl_isogeo_punchline")
        self.horizontalLayout_4.addWidget(self.lbl_isogeo_punchline)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        self.verticalLayout.addWidget(self.grp_realization)
        self.grp_sponsors = QtWidgets.QGroupBox(dlg_credits)
        self.grp_sponsors.setMaximumSize(QtCore.QSize(500, 150))
        font = QtGui.QFont()
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.grp_sponsors.setFont(font)
        self.grp_sponsors.setFlat(True)
        self.grp_sponsors.setObjectName("grp_sponsors")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.grp_sponsors)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.gridLayout_5 = QtWidgets.QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.lbl_smavd_logo = QtWidgets.QLabel(self.grp_sponsors)
        self.lbl_smavd_logo.setMaximumSize(QtCore.QSize(217, 40))
        self.lbl_smavd_logo.setText("")
        self.lbl_smavd_logo.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/credits/sponsor_logo_SMAVD.jpg")
        )
        self.lbl_smavd_logo.setScaledContents(False)
        self.lbl_smavd_logo.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_smavd_logo.setOpenExternalLinks(True)
        self.lbl_smavd_logo.setObjectName("lbl_smavd_logo")
        self.gridLayout_5.addWidget(self.lbl_smavd_logo, 0, 4, 1, 1)
        self.lbl_smavd_url = QtWidgets.QLabel(self.grp_sponsors)
        self.lbl_smavd_url.setMaximumSize(QtCore.QSize(217, 40))
        self.lbl_smavd_url.setText(
            '<html><head/><body><p align="center"><a href="https://www.smavd.org/"><span style=" text-decoration: underline; color:#0000ff;">Syndicat Mixte d&apos;Am&eacute;nagement<br/>de la Durance (SMAVD)</span></a></p></body></html>'
        )
        self.lbl_smavd_url.setWordWrap(True)
        self.lbl_smavd_url.setOpenExternalLinks(True)
        self.lbl_smavd_url.setObjectName("lbl_smavd_url")
        self.gridLayout_5.addWidget(self.lbl_smavd_url, 0, 0, 1, 1)
        self.line_2 = QtWidgets.QFrame(self.grp_sponsors)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout_5.addWidget(self.line_2, 0, 1, 1, 1)
        self.verticalLayout_9.addLayout(self.gridLayout_5)
        self.line = QtWidgets.QFrame(self.grp_sponsors)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_9.addWidget(self.line)
        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.lbl_lorient_url = QtWidgets.QLabel(self.grp_sponsors)
        self.lbl_lorient_url.setMaximumSize(QtCore.QSize(217, 40))
        self.lbl_lorient_url.setText(
            '<html><head/><body><p align="center"><a href="https://www.lorient-agglo.bzh/"><span style=" text-decoration: underline; color:#0000ff;">Communaut&eacute; d&apos;agglom&eacute;ration de<br/>Lorient (Lorient Agglom&eacute;ration)</span></a></p></body></html>'
        )
        self.lbl_lorient_url.setOpenExternalLinks(True)
        self.lbl_lorient_url.setObjectName("lbl_lorient_url")
        self.gridLayout_6.addWidget(self.lbl_lorient_url, 1, 0, 1, 1)
        self.line_3 = QtWidgets.QFrame(self.grp_sponsors)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout_6.addWidget(self.line_3, 1, 1, 1, 1)
        self.lbl_lorient_logo = QtWidgets.QLabel(self.grp_sponsors)
        self.lbl_lorient_logo.setMaximumSize(QtCore.QSize(217, 40))
        self.lbl_lorient_logo.setText("")
        self.lbl_lorient_logo.setPixmap(
            QtGui.QPixmap(
                ":/plugins/Isogeo/resources/credits/sponsor_logo_ca_lorient.png"
            )
        )
        self.lbl_lorient_logo.setScaledContents(False)
        self.lbl_lorient_logo.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_lorient_logo.setWordWrap(False)
        self.lbl_lorient_logo.setOpenExternalLinks(True)
        self.lbl_lorient_logo.setObjectName("lbl_lorient_logo")
        self.gridLayout_6.addWidget(self.lbl_lorient_logo, 1, 2, 1, 1)
        self.verticalLayout_9.addLayout(self.gridLayout_6)
        self.verticalLayout.addWidget(self.grp_sponsors)
        self.grp_sources = QtWidgets.QGroupBox(dlg_credits)
        self.grp_sources.setEnabled(True)
        self.grp_sources.setMaximumSize(QtCore.QSize(500, 150))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.grp_sources.setFont(font)
        self.grp_sources.setFlat(True)
        self.grp_sources.setCheckable(False)
        self.grp_sources.setObjectName("grp_sources")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.grp_sources)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.ico_github = QtWidgets.QLabel(self.grp_sources)
        self.ico_github.setMaximumSize(QtCore.QSize(100, 100))
        self.ico_github.setToolTip("")
        self.ico_github.setAutoFillBackground(True)
        self.ico_github.setText("")
        self.ico_github.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/credits/github.svg")
        )
        self.ico_github.setScaledContents(True)
        self.ico_github.setAlignment(QtCore.Qt.AlignCenter)
        self.ico_github.setObjectName("ico_github")
        self.gridLayout_2.addWidget(self.ico_github, 0, 0, 1, 1)
        self.ico_lgplv3 = QtWidgets.QLabel(self.grp_sources)
        self.ico_lgplv3.setMinimumSize(QtCore.QSize(32, 32))
        self.ico_lgplv3.setMaximumSize(QtCore.QSize(100, 16777215))
        self.ico_lgplv3.setToolTip("")
        self.ico_lgplv3.setAutoFillBackground(True)
        self.ico_lgplv3.setText("")
        self.ico_lgplv3.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/credits/lgplv3.svg")
        )
        self.ico_lgplv3.setScaledContents(True)
        self.ico_lgplv3.setAlignment(QtCore.Qt.AlignCenter)
        self.ico_lgplv3.setObjectName("ico_lgplv3")
        self.gridLayout_2.addWidget(self.ico_lgplv3, 0, 1, 1, 1)
        self.lbl_source_repository = QtWidgets.QLabel(self.grp_sources)
        self.lbl_source_repository.setScaledContents(True)
        self.lbl_source_repository.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_source_repository.setOpenExternalLinks(True)
        self.lbl_source_repository.setObjectName("lbl_source_repository")
        self.gridLayout_2.addWidget(self.lbl_source_repository, 1, 0, 1, 1)
        self.lbl_license_logo_gpl3 = QtWidgets.QLabel(self.grp_sources)
        self.lbl_license_logo_gpl3.setText(
            '<html><head/><body><p><a href="https://en.wikipedia.org/wiki/GNU_Lesser_General_Public_License"><span style=" text-decoration: underline; color:#0000ff;">LGPL v3 - Wikipedia</span></a></p></body></html>'
        )
        self.lbl_license_logo_gpl3.setScaledContents(True)
        self.lbl_license_logo_gpl3.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_license_logo_gpl3.setOpenExternalLinks(True)
        self.lbl_license_logo_gpl3.setObjectName("lbl_license_logo_gpl3")
        self.gridLayout_2.addWidget(self.lbl_license_logo_gpl3, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.grp_sources)
        self.btn_ok_close = QtWidgets.QDialogButtonBox(dlg_credits)
        self.btn_ok_close.setMaximumSize(QtCore.QSize(500, 16777215))
        self.btn_ok_close.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.btn_ok_close.setAutoFillBackground(False)
        self.btn_ok_close.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        self.btn_ok_close.setOrientation(QtCore.Qt.Horizontal)
        self.btn_ok_close.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.btn_ok_close.setCenterButtons(True)
        self.btn_ok_close.setObjectName("btn_ok_close")
        self.verticalLayout.addWidget(self.btn_ok_close)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(dlg_credits)
        self.btn_ok_close.accepted.connect(dlg_credits.accept)
        self.btn_ok_close.rejected.connect(dlg_credits.reject)
        QtCore.QMetaObject.connectSlotsByName(dlg_credits)

    def retranslateUi(self, dlg_credits):
        _translate = QtCore.QCoreApplication.translate
        dlg_credits.setWindowTitle(_translate("dlg_credits", "Credits"))
        self.grp_realization.setTitle(_translate("dlg_credits", "Realization"))
        self.lbl_isogeo_punchline.setText(
            _translate(
                "dlg_credits",
                '<a href="https://www.isogeo.com" style="color:#6480A7;text-decoration:none;">Easy access to geodata!</a>',
            )
        )
        self.grp_sponsors.setTitle(_translate("dlg_credits", "Sponsors"))
        self.grp_sources.setTitle(_translate("dlg_credits", "Sources and license"))
        self.lbl_source_repository.setText(
            _translate(
                "dlg_credits",
                '<html><head/><body><p><a href="https://github.com/isogeo/isogeo-plugin-qgis"><span style=" text-decoration: underline; color:#0000ff;">Code hosted on Github</span></a></p></body></html>',
            )
        )


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    dlg_credits = QtWidgets.QDialog()
    ui = Ui_dlg_credits()
    ui.setupUi(dlg_credits)
    dlg_credits.show()
    sys.exit(app.exec_())
