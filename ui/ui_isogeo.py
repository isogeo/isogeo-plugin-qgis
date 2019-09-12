# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui\isogeo_dockwidget_base.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_IsogeoDockWidgetBase(object):
    def setupUi(self, IsogeoDockWidgetBase):
        IsogeoDockWidgetBase.setObjectName("IsogeoDockWidgetBase")
        IsogeoDockWidgetBase.resize(623, 822)
        IsogeoDockWidgetBase.setMinimumSize(QtCore.QSize(623, 759))
        IsogeoDockWidgetBase.setMaximumSize(QtCore.QSize(900, 1792))
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/icon.png"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        IsogeoDockWidgetBase.setWindowIcon(icon)
        IsogeoDockWidgetBase.setLocale(
            QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates)
        )
        IsogeoDockWidgetBase.setWindowTitle("Isogeo")
        self.dockWidgetContents = QtWidgets.QWidget()
        self.dockWidgetContents.setMaximumSize(QtCore.QSize(900, 1792))
        self.dockWidgetContents.setObjectName("dockWidgetContents")
        self.gridLayout = QtWidgets.QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.dockWidgetContents)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.tabWidget.setFont(font)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_search = QtWidgets.QWidget()
        self.tab_search.setMaximumSize(QtCore.QSize(875, 2000))
        self.tab_search.setObjectName("tab_search")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.tab_search)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.btn_show = QtWidgets.QPushButton(self.tab_search)
        self.btn_show.setMinimumSize(QtCore.QSize(250, 30))
        self.btn_show.setMaximumSize(QtCore.QSize(360, 30))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/eye.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_show.setIcon(icon1)
        self.btn_show.setObjectName("btn_show")
        self.horizontalLayout_17.addWidget(self.btn_show)
        self.cbb_ob = QtWidgets.QComboBox(self.tab_search)
        self.cbb_ob.setMinimumSize(QtCore.QSize(45, 20))
        self.cbb_ob.setMaximumSize(QtCore.QSize(50, 30))
        self.cbb_ob.setMaxCount(6)
        self.cbb_ob.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_ob.setMinimumContentsLength(20)
        self.cbb_ob.setObjectName("cbb_ob")
        self.horizontalLayout_17.addWidget(self.cbb_ob)
        self.cbb_od = QtWidgets.QComboBox(self.tab_search)
        self.cbb_od.setMinimumSize(QtCore.QSize(40, 20))
        self.cbb_od.setMaximumSize(QtCore.QSize(50, 30))
        self.cbb_od.setMaxVisibleItems(3)
        self.cbb_od.setMaxCount(3)
        self.cbb_od.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_od.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_od.setMinimumContentsLength(20)
        self.cbb_od.setObjectName("cbb_od")
        self.horizontalLayout_17.addWidget(self.cbb_od)
        self.line_2 = QtWidgets.QFrame(self.tab_search)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_17.addWidget(self.line_2)
        self.btn_reinit = QtWidgets.QPushButton(self.tab_search)
        self.btn_reinit.setMinimumSize(QtCore.QSize(30, 25))
        self.btn_reinit.setMaximumSize(QtCore.QSize(75, 30))
        self.btn_reinit.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/undo.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_reinit.setIcon(icon2)
        self.btn_reinit.setIconSize(QtCore.QSize(18, 18))
        self.btn_reinit.setObjectName("btn_reinit")
        self.horizontalLayout_17.addWidget(self.btn_reinit)
        self.btn_quicksearch_save = QtWidgets.QPushButton(self.tab_search)
        self.btn_quicksearch_save.setMinimumSize(QtCore.QSize(30, 25))
        self.btn_quicksearch_save.setMaximumSize(QtCore.QSize(75, 30))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.btn_quicksearch_save.setFont(font)
        self.btn_quicksearch_save.setText("")
        icon3 = QtGui.QIcon()
        icon3.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/save.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_quicksearch_save.setIcon(icon3)
        self.btn_quicksearch_save.setIconSize(QtCore.QSize(18, 18))
        self.btn_quicksearch_save.setObjectName("btn_quicksearch_save")
        self.horizontalLayout_17.addWidget(self.btn_quicksearch_save)
        self.gridLayout_8.addLayout(self.horizontalLayout_17, 2, 0, 1, 1)
        self.lyt_search = QtWidgets.QGridLayout()
        self.lyt_search.setObjectName("lyt_search")
        self.cbb_quicksearch_use = QtWidgets.QComboBox(self.tab_search)
        self.cbb_quicksearch_use.setMinimumSize(QtCore.QSize(250, 30))
        self.cbb_quicksearch_use.setMaximumSize(QtCore.QSize(300, 40))
        self.cbb_quicksearch_use.setSizeIncrement(QtCore.QSize(2, 0))
        self.cbb_quicksearch_use.setAutoFillBackground(True)
        self.cbb_quicksearch_use.setInsertPolicy(
            QtWidgets.QComboBox.InsertAlphabetically
        )
        self.cbb_quicksearch_use.setIconSize(QtCore.QSize(20, 20))
        self.cbb_quicksearch_use.setObjectName("cbb_quicksearch_use")
        icon4 = QtGui.QIcon()
        icon4.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/bolt.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.cbb_quicksearch_use.addItem(icon4, "")
        self.lyt_search.addWidget(self.cbb_quicksearch_use, 1, 2, 1, 3)
        self.cbb_chck_kw = QgsCheckableComboBox(self.tab_search)
        self.cbb_chck_kw.setMinimumSize(QtCore.QSize(250, 25))
        self.cbb_chck_kw.setAutoFillBackground(True)
        self.cbb_chck_kw.setObjectName("cbb_chck_kw")
        self.lyt_search.addWidget(self.cbb_chck_kw, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.lyt_search.addItem(spacerItem, 1, 1, 1, 1)
        self.btn_search_go = QtWidgets.QPushButton(self.tab_search)
        self.btn_search_go.setMinimumSize(QtCore.QSize(30, 30))
        self.btn_search_go.setMaximumSize(QtCore.QSize(200, 30))
        self.btn_search_go.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_search_go.setAutoFillBackground(True)
        self.btn_search_go.setText("")
        icon5 = QtGui.QIcon()
        icon5.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/search.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_search_go.setIcon(icon5)
        self.btn_search_go.setAutoDefault(True)
        self.btn_search_go.setDefault(True)
        self.btn_search_go.setFlat(False)
        self.btn_search_go.setObjectName("btn_search_go")
        self.lyt_search.addWidget(self.btn_search_go, 0, 3, 1, 2)
        self.txt_input = QtWidgets.QLineEdit(self.tab_search)
        self.txt_input.setMinimumSize(QtCore.QSize(200, 30))
        self.txt_input.setAutoFillBackground(True)
        self.txt_input.setInputMask("")
        self.txt_input.setText("")
        self.txt_input.setObjectName("txt_input")
        self.lyt_search.addWidget(self.txt_input, 0, 0, 1, 3)
        self.gridLayout_8.addLayout(self.lyt_search, 0, 0, 1, 1)
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        spacerItem1 = QtWidgets.QSpacerItem(
            98, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_12.addItem(spacerItem1)
        self.btn_previous = QtWidgets.QPushButton(self.tab_search)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_previous.sizePolicy().hasHeightForWidth())
        self.btn_previous.setSizePolicy(sizePolicy)
        self.btn_previous.setText("")
        icon6 = QtGui.QIcon()
        icon6.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/caret-left.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_previous.setIcon(icon6)
        self.btn_previous.setObjectName("btn_previous")
        self.horizontalLayout_12.addWidget(self.btn_previous)
        self.lbl_page = QtWidgets.QLabel(self.tab_search)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.lbl_page.setFont(font)
        self.lbl_page.setObjectName("lbl_page")
        self.horizontalLayout_12.addWidget(self.lbl_page)
        self.btn_next = QtWidgets.QPushButton(self.tab_search)
        self.btn_next.setText("")
        icon7 = QtGui.QIcon()
        icon7.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/caret-right.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_next.setIcon(icon7)
        self.btn_next.setObjectName("btn_next")
        self.horizontalLayout_12.addWidget(self.btn_next)
        spacerItem2 = QtWidgets.QSpacerItem(
            128, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_12.addItem(spacerItem2)
        self.gridLayout_8.addLayout(self.horizontalLayout_12, 4, 0, 1, 1)
        self.tbl_result = QtWidgets.QTableWidget(self.tab_search)
        self.tbl_result.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tbl_result.setObjectName("tbl_result")
        self.tbl_result.setColumnCount(4)
        self.tbl_result.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_result.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_result.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_result.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tbl_result.setHorizontalHeaderItem(3, item)
        self.tbl_result.horizontalHeader().setVisible(False)
        self.tbl_result.horizontalHeader().setSortIndicatorShown(False)
        self.tbl_result.verticalHeader().setVisible(False)
        self.gridLayout_8.addWidget(self.tbl_result, 3, 0, 1, 1)
        self.grp_filters = QgsCollapsibleGroupBox(self.tab_search)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grp_filters.sizePolicy().hasHeightForWidth())
        self.grp_filters.setSizePolicy(sizePolicy)
        self.grp_filters.setMaximumSize(QtCore.QSize(800, 16777215))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.grp_filters.setFont(font)
        self.grp_filters.setProperty("collapsed", False)
        self.grp_filters.setProperty("scrollOnExpand", True)
        self.grp_filters.setObjectName("grp_filters")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.grp_filters)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.lyt_horiz_filters = QtWidgets.QHBoxLayout()
        self.lyt_horiz_filters.setObjectName("lyt_horiz_filters")
        self.lyt_vert_filters_left = QtWidgets.QVBoxLayout()
        self.lyt_vert_filters_left.setObjectName("lyt_vert_filters_left")
        self.lyt_vert_filter_geo = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_geo.setObjectName("lyt_vert_filter_geo")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.ico_geofilter = QtWidgets.QLabel(self.grp_filters)
        self.ico_geofilter.setMaximumSize(QtCore.QSize(18, 18))
        self.ico_geofilter.setText("")
        self.ico_geofilter.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/map.svg")
        )
        self.ico_geofilter.setScaledContents(True)
        self.ico_geofilter.setObjectName("ico_geofilter")
        self.horizontalLayout.addWidget(self.ico_geofilter)
        self.lbl_geofilter = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_geofilter.setFont(font)
        self.lbl_geofilter.setObjectName("lbl_geofilter")
        self.horizontalLayout.addWidget(self.lbl_geofilter)
        spacerItem3 = QtWidgets.QSpacerItem(
            48, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout.addItem(spacerItem3)
        self.lyt_vert_filter_geo.addLayout(self.horizontalLayout)
        self.cbb_geofilter = QtWidgets.QComboBox(self.grp_filters)
        self.cbb_geofilter.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_geofilter.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_geofilter.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_geofilter.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_geofilter.setObjectName("cbb_geofilter")
        self.lyt_vert_filter_geo.addWidget(self.cbb_geofilter)
        self.lyt_vert_filters_left.addLayout(self.lyt_vert_filter_geo)
        self.lyt_vert_filter_format = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_format.setObjectName("lyt_vert_filter_format")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ico_format = QtWidgets.QLabel(self.grp_filters)
        self.ico_format.setMaximumSize(QtCore.QSize(18, 18))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.ico_format.setFont(font)
        self.ico_format.setText("")
        self.ico_format.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/cube.svg")
        )
        self.ico_format.setScaledContents(True)
        self.ico_format.setObjectName("ico_format")
        self.horizontalLayout_3.addWidget(self.ico_format)
        self.lbl_format = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_format.setFont(font)
        self.lbl_format.setObjectName("lbl_format")
        self.horizontalLayout_3.addWidget(self.lbl_format)
        spacerItem4 = QtWidgets.QSpacerItem(
            138, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_3.addItem(spacerItem4)
        self.lyt_vert_filter_format.addLayout(self.horizontalLayout_3)
        self.cbb_format = QtWidgets.QComboBox(self.grp_filters)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbb_format.sizePolicy().hasHeightForWidth())
        self.cbb_format.setSizePolicy(sizePolicy)
        self.cbb_format.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_format.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_format.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_format.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_format.setObjectName("cbb_format")
        self.lyt_vert_filter_format.addWidget(self.cbb_format)
        self.lyt_vert_filters_left.addLayout(self.lyt_vert_filter_format)
        self.lyt_vert_filter_inspire = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_inspire.setObjectName("lyt_vert_filter_inspire")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.ico_inspire = QtWidgets.QLabel(self.grp_filters)
        self.ico_inspire.setMaximumSize(QtCore.QSize(18, 18))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.ico_inspire.setFont(font)
        self.ico_inspire.setText("")
        self.ico_inspire.setPixmap(QtGui.QPixmap(":/plugins/Isogeo/resources/leaf.svg"))
        self.ico_inspire.setScaledContents(True)
        self.ico_inspire.setObjectName("ico_inspire")
        self.horizontalLayout_4.addWidget(self.ico_inspire)
        self.lbl_inspire = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_inspire.setFont(font)
        self.lbl_inspire.setObjectName("lbl_inspire")
        self.horizontalLayout_4.addWidget(self.lbl_inspire)
        spacerItem5 = QtWidgets.QSpacerItem(
            78, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_4.addItem(spacerItem5)
        self.lyt_vert_filter_inspire.addLayout(self.horizontalLayout_4)
        self.cbb_inspire = QtWidgets.QComboBox(self.grp_filters)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbb_inspire.sizePolicy().hasHeightForWidth())
        self.cbb_inspire.setSizePolicy(sizePolicy)
        self.cbb_inspire.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_inspire.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_inspire.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_inspire.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_inspire.setObjectName("cbb_inspire")
        self.lyt_vert_filter_inspire.addWidget(self.cbb_inspire)
        self.lyt_vert_filters_left.addLayout(self.lyt_vert_filter_inspire)
        self.lyt_vert_filter_contact = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_contact.setContentsMargins(-1, -1, -1, 0)
        self.lyt_vert_filter_contact.setObjectName("lyt_vert_filter_contact")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_15.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.ico_contact = QtWidgets.QLabel(self.grp_filters)
        self.ico_contact.setMaximumSize(QtCore.QSize(18, 18))
        self.ico_contact.setText("")
        self.ico_contact.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/phone_blue.svg")
        )
        self.ico_contact.setScaledContents(True)
        self.ico_contact.setObjectName("ico_contact")
        self.horizontalLayout_15.addWidget(self.ico_contact)
        self.lbl_contact = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_contact.setFont(font)
        self.lbl_contact.setScaledContents(True)
        self.lbl_contact.setObjectName("lbl_contact")
        self.horizontalLayout_15.addWidget(self.lbl_contact)
        spacerItem6 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_15.addItem(spacerItem6)
        self.lyt_vert_filter_contact.addLayout(self.horizontalLayout_15)
        self.cbb_contact = QtWidgets.QComboBox(self.grp_filters)
        self.cbb_contact.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_contact.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_contact.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_contact.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_contact.setObjectName("cbb_contact")
        self.lyt_vert_filter_contact.addWidget(self.cbb_contact)
        self.lyt_vert_filters_left.addLayout(self.lyt_vert_filter_contact)
        self.lyt_horiz_filters.addLayout(self.lyt_vert_filters_left)
        self.lyt_vert_filters_right = QtWidgets.QVBoxLayout()
        self.lyt_vert_filters_right.setObjectName("lyt_vert_filters_right")
        self.lyt_vert_filter_type = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_type.setObjectName("lyt_vert_filter_type")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.ico_type = QtWidgets.QLabel(self.grp_filters)
        self.ico_type.setMaximumSize(QtCore.QSize(18, 18))
        self.ico_type.setText("")
        self.ico_type.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/asterisk.svg")
        )
        self.ico_type.setScaledContents(True)
        self.ico_type.setObjectName("ico_type")
        self.horizontalLayout_2.addWidget(self.ico_type)
        self.lbl_type = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_type.setFont(font)
        self.lbl_type.setObjectName("lbl_type")
        self.horizontalLayout_2.addWidget(self.lbl_type)
        spacerItem7 = QtWidgets.QSpacerItem(
            48, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_2.addItem(spacerItem7)
        self.lyt_vert_filter_type.addLayout(self.horizontalLayout_2)
        self.cbb_type = QtWidgets.QComboBox(self.grp_filters)
        self.cbb_type.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_type.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_type.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_type.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_type.setObjectName("cbb_type")
        self.lyt_vert_filter_type.addWidget(self.cbb_type)
        self.lyt_vert_filters_right.addLayout(self.lyt_vert_filter_type)
        self.lyt_vert_filter_workgroup = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_workgroup.setObjectName("lyt_vert_filter_workgroup")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.ico_owner = QtWidgets.QLabel(self.grp_filters)
        self.ico_owner.setMaximumSize(QtCore.QSize(18, 18))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.ico_owner.setFont(font)
        self.ico_owner.setText("")
        self.ico_owner.setPixmap(QtGui.QPixmap(":/plugins/Isogeo/resources/users.svg"))
        self.ico_owner.setScaledContents(True)
        self.ico_owner.setObjectName("ico_owner")
        self.horizontalLayout_5.addWidget(self.ico_owner)
        self.lbl_owner = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_owner.setFont(font)
        self.lbl_owner.setObjectName("lbl_owner")
        self.horizontalLayout_5.addWidget(self.lbl_owner)
        spacerItem8 = QtWidgets.QSpacerItem(
            148, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_5.addItem(spacerItem8)
        self.lyt_vert_filter_workgroup.addLayout(self.horizontalLayout_5)
        self.cbb_owner = QtWidgets.QComboBox(self.grp_filters)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbb_owner.sizePolicy().hasHeightForWidth())
        self.cbb_owner.setSizePolicy(sizePolicy)
        self.cbb_owner.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_owner.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_owner.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_owner.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_owner.setObjectName("cbb_owner")
        self.lyt_vert_filter_workgroup.addWidget(self.cbb_owner)
        self.lyt_vert_filters_right.addLayout(self.lyt_vert_filter_workgroup)
        self.lyt_vert_filter_srs = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_srs.setObjectName("lyt_vert_filter_srs")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.ico_srs = QtWidgets.QLabel(self.grp_filters)
        self.ico_srs.setMaximumSize(QtCore.QSize(18, 18))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.ico_srs.setFont(font)
        self.ico_srs.setText("")
        self.ico_srs.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/search/globe.svg")
        )
        self.ico_srs.setScaledContents(True)
        self.ico_srs.setObjectName("ico_srs")
        self.horizontalLayout_6.addWidget(self.ico_srs)
        self.lbl_srs = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_srs.setFont(font)
        self.lbl_srs.setObjectName("lbl_srs")
        self.horizontalLayout_6.addWidget(self.lbl_srs)
        spacerItem9 = QtWidgets.QSpacerItem(
            68, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_6.addItem(spacerItem9)
        self.lyt_vert_filter_srs.addLayout(self.horizontalLayout_6)
        self.cbb_srs = QtWidgets.QComboBox(self.grp_filters)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbb_srs.sizePolicy().hasHeightForWidth())
        self.cbb_srs.setSizePolicy(sizePolicy)
        self.cbb_srs.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_srs.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_srs.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_srs.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_srs.setObjectName("cbb_srs")
        self.lyt_vert_filter_srs.addWidget(self.cbb_srs)
        self.lyt_vert_filters_right.addLayout(self.lyt_vert_filter_srs)
        self.lyt_vert_filter_licence = QtWidgets.QVBoxLayout()
        self.lyt_vert_filter_licence.setObjectName("lyt_vert_filter_licence")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.ico_license = QtWidgets.QLabel(self.grp_filters)
        self.ico_license.setMaximumSize(QtCore.QSize(18, 18))
        self.ico_license.setText("")
        self.ico_license.setPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/gavel.svg")
        )
        self.ico_license.setScaledContents(True)
        self.ico_license.setObjectName("ico_license")
        self.horizontalLayout_8.addWidget(self.ico_license)
        self.lbl_license = QtWidgets.QLabel(self.grp_filters)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.lbl_license.setFont(font)
        self.lbl_license.setObjectName("lbl_license")
        self.horizontalLayout_8.addWidget(self.lbl_license)
        spacerItem10 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_8.addItem(spacerItem10)
        self.lyt_vert_filter_licence.addLayout(self.horizontalLayout_8)
        self.cbb_license = QtWidgets.QComboBox(self.grp_filters)
        self.cbb_license.setMinimumSize(QtCore.QSize(250, 20))
        self.cbb_license.setMaximumSize(QtCore.QSize(360, 25))
        self.cbb_license.setInsertPolicy(QtWidgets.QComboBox.InsertAlphabetically)
        self.cbb_license.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon
        )
        self.cbb_license.setObjectName("cbb_license")
        self.lyt_vert_filter_licence.addWidget(self.cbb_license)
        self.lyt_vert_filters_right.addLayout(self.lyt_vert_filter_licence)
        self.lyt_horiz_filters.addLayout(self.lyt_vert_filters_right)
        self.verticalLayout_13.addLayout(self.lyt_horiz_filters)
        self.gridLayout_2.addLayout(self.verticalLayout_13, 0, 0, 1, 1)
        self.gridLayout_8.addWidget(self.grp_filters, 1, 0, 1, 1)
        self.grp_filters.raise_()
        self.tbl_result.raise_()
        self.tabWidget.addTab(self.tab_search, icon5, "")
        self.tab_settings = QtWidgets.QWidget()
        self.tab_settings.setObjectName("tab_settings")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.tab_settings)
        self.gridLayout_7.setObjectName("gridLayout_7")
        spacerItem11 = QtWidgets.QSpacerItem(
            20, 105, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        self.gridLayout_7.addItem(spacerItem11, 7, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab_settings)
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 121))
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.cbb_quicksearch_edit = QtWidgets.QComboBox(self.groupBox_2)
        self.cbb_quicksearch_edit.setMinimumSize(QtCore.QSize(221, 24))
        self.cbb_quicksearch_edit.setObjectName("cbb_quicksearch_edit")
        self.horizontalLayout_9.addWidget(self.cbb_quicksearch_edit)
        spacerItem12 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_9.addItem(spacerItem12)
        self.btn_rename_sr = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_rename_sr.setMinimumSize(QtCore.QSize(111, 25))
        self.btn_rename_sr.setMaximumSize(QtCore.QSize(115, 25))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_rename_sr.setFont(font)
        icon8 = QtGui.QIcon()
        icon8.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/pencil.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_rename_sr.setIcon(icon8)
        self.btn_rename_sr.setObjectName("btn_rename_sr")
        self.horizontalLayout_9.addWidget(self.btn_rename_sr)
        self.btn_delete_sr = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_delete_sr.setMinimumSize(QtCore.QSize(60, 25))
        self.btn_delete_sr.setMaximumSize(QtCore.QSize(60, 25))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.btn_delete_sr.setFont(font)
        self.btn_delete_sr.setText("")
        icon9 = QtGui.QIcon()
        icon9.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/trash.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_delete_sr.setIcon(icon9)
        self.btn_delete_sr.setObjectName("btn_delete_sr")
        self.horizontalLayout_9.addWidget(self.btn_delete_sr)
        self.verticalLayout_10.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.lbl_default = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_default.setFont(font)
        self.lbl_default.setObjectName("lbl_default")
        self.horizontalLayout_10.addWidget(self.lbl_default)
        spacerItem13 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_10.addItem(spacerItem13)
        self.btn_default_save = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_default_save.setMinimumSize(QtCore.QSize(111, 25))
        self.btn_default_save.setMaximumSize(QtCore.QSize(115, 25))
        self.btn_default_save.setText("")
        self.btn_default_save.setIcon(icon3)
        self.btn_default_save.setObjectName("btn_default_save")
        self.horizontalLayout_10.addWidget(self.btn_default_save)
        self.btn_default_reset = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_default_reset.setMinimumSize(QtCore.QSize(60, 25))
        self.btn_default_reset.setMaximumSize(QtCore.QSize(60, 25))
        self.btn_default_reset.setText("")
        self.btn_default_reset.setIcon(icon2)
        self.btn_default_reset.setObjectName("btn_default_reset")
        self.horizontalLayout_10.addWidget(self.btn_default_reset)
        self.verticalLayout_10.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.lbl_geo_op = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_geo_op.setFont(font)
        self.lbl_geo_op.setObjectName("lbl_geo_op")
        self.horizontalLayout_11.addWidget(self.lbl_geo_op)
        spacerItem14 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_11.addItem(spacerItem14)
        self.cbb_geo_op = QtWidgets.QComboBox(self.groupBox_2)
        self.cbb_geo_op.setMinimumSize(QtCore.QSize(176, 25))
        self.cbb_geo_op.setMaximumSize(QtCore.QSize(250, 25))
        self.cbb_geo_op.setObjectName("cbb_geo_op")
        self.horizontalLayout_11.addWidget(self.cbb_geo_op)
        self.verticalLayout_10.addLayout(self.horizontalLayout_11)
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_13.setSizeConstraint(
            QtWidgets.QLayout.SetDefaultConstraint
        )
        self.horizontalLayout_13.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.lbl_cache = QtWidgets.QLabel(self.groupBox_2)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_cache.setFont(font)
        self.lbl_cache.setObjectName("lbl_cache")
        self.horizontalLayout_13.addWidget(self.lbl_cache)
        spacerItem15 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_13.addItem(spacerItem15)
        self.btn_cache_trash = QtWidgets.QPushButton(self.groupBox_2)
        self.btn_cache_trash.setMinimumSize(QtCore.QSize(60, 25))
        self.btn_cache_trash.setMaximumSize(QtCore.QSize(60, 25))
        self.btn_cache_trash.setAutoFillBackground(True)
        self.btn_cache_trash.setIcon(icon9)
        self.btn_cache_trash.setFlat(False)
        self.btn_cache_trash.setObjectName("btn_cache_trash")
        self.horizontalLayout_13.addWidget(self.btn_cache_trash)
        self.verticalLayout_10.addLayout(self.horizontalLayout_13)
        self.gridLayout_4.addLayout(self.verticalLayout_10, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_2, 0, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(self.tab_settings)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.txt_shares = QtWidgets.QTextBrowser(self.groupBox)
        self.txt_shares.setObjectName("txt_shares")
        self.gridLayout_5.addWidget(self.txt_shares, 1, 0, 1, 1)
        self.horizontalLayout_21 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_21.setObjectName("horizontalLayout_21")
        self.lbl_auth = QtWidgets.QLabel(self.groupBox)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_auth.setFont(font)
        self.lbl_auth.setObjectName("lbl_auth")
        self.horizontalLayout_21.addWidget(self.lbl_auth)
        spacerItem16 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_21.addItem(spacerItem16)
        self.btn_change_user = QtWidgets.QPushButton(self.groupBox)
        self.btn_change_user.setMinimumSize(QtCore.QSize(91, 24))
        self.btn_change_user.setText("")
        icon10 = QtGui.QIcon()
        icon10.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/key.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_change_user.setIcon(icon10)
        self.btn_change_user.setObjectName("btn_change_user")
        self.horizontalLayout_21.addWidget(self.btn_change_user)
        self.gridLayout_5.addLayout(self.horizontalLayout_21, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox, 5, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(self.tab_settings)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_6 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.horizontalLayout_24 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_24.setObjectName("horizontalLayout_24")
        self.lbl_report = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_report.setFont(font)
        self.lbl_report.setObjectName("lbl_report")
        self.horizontalLayout_24.addWidget(self.lbl_report)
        spacerItem17 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_24.addItem(spacerItem17)
        self.btn_log_dir = QtWidgets.QPushButton(self.groupBox_4)
        self.btn_log_dir.setMinimumSize(QtCore.QSize(80, 25))
        self.btn_log_dir.setMaximumSize(QtCore.QSize(100, 30))
        self.btn_log_dir.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_log_dir.setAutoFillBackground(True)
        icon11 = QtGui.QIcon()
        icon11.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/folder-open-o.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_log_dir.setIcon(icon11)
        self.btn_log_dir.setObjectName("btn_log_dir")
        self.horizontalLayout_24.addWidget(self.btn_log_dir)
        self.btn_report = QtWidgets.QPushButton(self.groupBox_4)
        self.btn_report.setMinimumSize(QtCore.QSize(80, 25))
        self.btn_report.setMaximumSize(QtCore.QSize(100, 30))
        self.btn_report.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_report.setAutoFillBackground(True)
        self.btn_report.setText("")
        icon12 = QtGui.QIcon()
        icon12.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/bullhorn.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_report.setIcon(icon12)
        self.btn_report.setObjectName("btn_report")
        self.horizontalLayout_24.addWidget(self.btn_report)
        self.verticalLayout_12.addLayout(self.horizontalLayout_24)
        self.horizontalLayout_23 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_23.setObjectName("horizontalLayout_23")
        self.lbl_help = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_help.setFont(font)
        self.lbl_help.setObjectName("lbl_help")
        self.horizontalLayout_23.addWidget(self.lbl_help)
        spacerItem18 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_23.addItem(spacerItem18)
        self.btn_help = QtWidgets.QPushButton(self.groupBox_4)
        self.btn_help.setMinimumSize(QtCore.QSize(80, 25))
        self.btn_help.setMaximumSize(QtCore.QSize(100, 30))
        self.btn_help.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_help.setAutoFillBackground(True)
        self.btn_help.setText("")
        icon13 = QtGui.QIcon()
        icon13.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/question.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_help.setIcon(icon13)
        self.btn_help.setObjectName("btn_help")
        self.horizontalLayout_23.addWidget(self.btn_help)
        self.verticalLayout_12.addLayout(self.horizontalLayout_23)
        self.horizontalLayout_22 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_22.setObjectName("horizontalLayout_22")
        self.lbl_credits = QtWidgets.QLabel(self.groupBox_4)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.lbl_credits.setFont(font)
        self.lbl_credits.setObjectName("lbl_credits")
        self.horizontalLayout_22.addWidget(self.lbl_credits)
        spacerItem19 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        self.horizontalLayout_22.addItem(spacerItem19)
        self.btn_credits = QtWidgets.QPushButton(self.groupBox_4)
        self.btn_credits.setMinimumSize(QtCore.QSize(80, 25))
        self.btn_credits.setMaximumSize(QtCore.QSize(100, 30))
        self.btn_credits.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_credits.setText("")
        icon14 = QtGui.QIcon()
        icon14.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/info.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.btn_credits.setIcon(icon14)
        self.btn_credits.setObjectName("btn_credits")
        self.horizontalLayout_22.addWidget(self.btn_credits)
        self.verticalLayout_12.addLayout(self.horizontalLayout_22)
        self.gridLayout_6.addLayout(self.verticalLayout_12, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_4, 6, 0, 1, 1)
        icon15 = QtGui.QIcon()
        icon15.addPixmap(
            QtGui.QPixmap(":/plugins/Isogeo/resources/settings/gear.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.tabWidget.addTab(self.tab_settings, icon15, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)
        IsogeoDockWidgetBase.setWidget(self.dockWidgetContents)

        self.retranslateUi(IsogeoDockWidgetBase)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(IsogeoDockWidgetBase)

    def retranslateUi(self, IsogeoDockWidgetBase):
        _translate = QtCore.QCoreApplication.translate
        self.btn_show.setToolTip(
            _translate("IsogeoDockWidgetBase", "Display the results list")
        )
        self.btn_show.setText(_translate("IsogeoDockWidgetBase", "Show results"))
        self.cbb_ob.setToolTip(_translate("IsogeoDockWidgetBase", "Sorting method"))
        self.cbb_od.setToolTip(_translate("IsogeoDockWidgetBase", "Sorting direction"))
        self.btn_reinit.setToolTip(
            _translate("IsogeoDockWidgetBase", "Reset all input fields")
        )
        self.btn_quicksearch_save.setToolTip(
            _translate("IsogeoDockWidgetBase", "Save research")
        )
        self.cbb_quicksearch_use.setToolTip(
            _translate("IsogeoDockWidgetBase", "Quick searches")
        )
        self.cbb_quicksearch_use.setItemText(
            0, _translate("IsogeoDockWidgetBase", "Quicksearches")
        )
        self.btn_search_go.setToolTip(
            _translate("IsogeoDockWidgetBase", "Launch search")
        )
        self.txt_input.setToolTip(
            _translate("IsogeoDockWidgetBase", "Enter your search terms")
        )
        self.txt_input.setPlaceholderText(
            _translate(
                "IsogeoDockWidgetBase", "roads, habitat, cadastral parcel, transport"
            )
        )
        self.lbl_page.setText(_translate("IsogeoDockWidgetBase", "Page x on x"))
        self.tbl_result.setSortingEnabled(False)
        item = self.tbl_result.horizontalHeaderItem(0)
        item.setText(_translate("IsogeoDockWidgetBase", "Title"))
        item = self.tbl_result.horizontalHeaderItem(1)
        item.setText(_translate("IsogeoDockWidgetBase", "Modified"))
        item = self.tbl_result.horizontalHeaderItem(2)
        item.setText(_translate("IsogeoDockWidgetBase", "Type"))
        item = self.tbl_result.horizontalHeaderItem(3)
        item.setText(_translate("IsogeoDockWidgetBase", "Add"))
        self.grp_filters.setTitle(_translate("IsogeoDockWidgetBase", "Advanced search"))
        self.lbl_geofilter.setText(
            _translate("IsogeoDockWidgetBase", "Geographic filter")
        )
        self.lbl_format.setText(_translate("IsogeoDockWidgetBase", "Format (source)"))
        self.lbl_inspire.setText(_translate("IsogeoDockWidgetBase", "INSPIRE keywords"))
        self.lbl_contact.setText(_translate("IsogeoDockWidgetBase", "Contact"))
        self.lbl_type.setText(_translate("IsogeoDockWidgetBase", "Resource type"))
        self.lbl_owner.setText(_translate("IsogeoDockWidgetBase", "Metadata owner"))
        self.lbl_srs.setText(
            _translate("IsogeoDockWidgetBase", "Coordinate system (source)")
        )
        self.lbl_license.setText(_translate("IsogeoDockWidgetBase", "License"))
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_search),
            _translate("IsogeoDockWidgetBase", "Search"),
        )
        self.groupBox_2.setTitle(_translate("IsogeoDockWidgetBase", "Search settings"))
        self.cbb_quicksearch_edit.setToolTip(
            _translate("IsogeoDockWidgetBase", "Edit quicksearch")
        )
        self.btn_rename_sr.setText(_translate("IsogeoDockWidgetBase", "Rename"))
        self.lbl_default.setText(_translate("IsogeoDockWidgetBase", "Default search"))
        self.lbl_geo_op.setText(
            _translate(
                "IsogeoDockWidgetBase", "Geographical operator applied to the filter"
            )
        )
        self.lbl_cache.setText(_translate("IsogeoDockWidgetBase", "Paths cache"))
        self.btn_cache_trash.setToolTip(
            _translate("IsogeoDockWidgetBase", "Empty the paths cached")
        )
        self.groupBox.setTitle(
            _translate("IsogeoDockWidgetBase", "Authentication settings")
        )
        self.lbl_auth.setText(
            _translate("IsogeoDockWidgetBase", "Set plugin authentication:")
        )
        self.groupBox_4.setTitle(_translate("IsogeoDockWidgetBase", "Resources"))
        self.lbl_report.setText(
            _translate("IsogeoDockWidgetBase", "Report an issue on the bug tracker")
        )
        self.btn_log_dir.setToolTip(
            _translate(
                "IsogeoDockWidgetBase", 'Get the log file: "log_isogeo_plugin.log"'
            )
        )
        self.btn_log_dir.setText(_translate("IsogeoDockWidgetBase", "LOG File"))
        self.lbl_help.setText(
            _translate("IsogeoDockWidgetBase", "Open online plugin help")
        )
        self.btn_help.setToolTip(
            _translate("IsogeoDockWidgetBase", "Open online help in default browser")
        )
        self.lbl_credits.setText(
            _translate("IsogeoDockWidgetBase", "Open plugin credits")
        )
        self.btn_credits.setToolTip(
            _translate("IsogeoDockWidgetBase", "Open credits popup")
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_settings),
            _translate("IsogeoDockWidgetBase", "Settings"),
        )


from qgis.gui import QgsCollapsibleGroupBox
from qgscheckablecombobox import QgsCheckableComboBox

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    IsogeoDockWidgetBase = QtWidgets.QDockWidget()
    ui = Ui_IsogeoDockWidgetBase()
    ui.setupUi(IsogeoDockWidgetBase)
    IsogeoDockWidgetBase.show()
    sys.exit(app.exec_())
