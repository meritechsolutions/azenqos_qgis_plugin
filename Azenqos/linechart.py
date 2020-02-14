from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import * #QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import * #QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import globalutils

class Ui_LTE_LCwidget(QWidget):
    def __init__(self, parent, windowName, azenqosDB):
        super().__init__(parent)
        self.title = windowName
        self.database = azenqosDB
        self.width = 640
        self.height = 480
        self.maximumHeight = 480
        self.maximumWidth = 640
        self.setupUi()


    def setupUi(self):
        self.setObjectName("LTE_LCwidget")
        # self.resize(841, 586)
        layout = QVBoxLayout(self)

        # Graph Area
        self.lte_GArea = QScrollArea(self)
        self.lte_GArea.setGeometry(QtCore.QRect(20, 10, 601, 371))
        self.lte_GArea.setWidgetResizable(True)
        self.lte_GArea.setObjectName("lte_GArea")

        # Scroll Area
        # self.scrollAreaWidgetContents = QWidget(self.lte_GArea)
        # self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        # self.lte_GArea.setWidget(self.scrollAreaWidgetContents)
        # self.scrollAreaWidgetContents.resize(self.lte_GArea.sizeHint())

        # DataTable
        self.lte_tableWidget = QTableWidget(self)
        self.lte_tableWidget.setObjectName("lte_tableWidget")
        self.lte_tableWidget.setColumnCount(4)
        self.lte_tableWidget.setRowCount(5)
        self.lte_tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        item = QTableWidgetItem()
        self.lte_tableWidget.setVerticalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.lte_tableWidget.setVerticalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.lte_tableWidget.setVerticalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.lte_tableWidget.setVerticalHeaderItem(3, item)
        item = QTableWidgetItem()
        self.lte_tableWidget.setVerticalHeaderItem(4, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_tableWidget.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_tableWidget.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(0, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(0, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(0, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_tableWidget.setItem(0, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(1, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(1, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(1, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_tableWidget.setItem(1, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(2, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(2, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(2, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 124, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_tableWidget.setItem(2, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(3, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(3, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(3, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 119, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_tableWidget.setItem(3, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(4, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(4, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_tableWidget.setItem(4, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        # brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        # brush.setStyle(QtCore.Qt.SolidPattern)
        # item.setForeground(brush)
        self.lte_tableWidget.setItem(4, 3, item)
        self.lte_tableWidget.horizontalHeader().setVisible(True)
        self.lte_tableWidget.horizontalHeader().setHighlightSections(True)
        self.lte_tableWidget.verticalHeader().setVisible(False)

        # DateLabel
        # self.datelabel = QLabel(self)
        # self.datelabel.setGeometry(QtCore.QRect(455, 38, 47, 13))
        # font = QtGui.QFont()
        # font.setPointSize(10)
        # font.setBold(True)
        # font.setWeight(75)
        # self.datelabel.setFont(font)
        # self.datelabel.setObjectName("datelabel")
        # self.lineEdit = QLineEdit(self)
        # self.lineEdit.setGeometry(QtCore.QRect(503, 36, 88, 20))
        # font = QtGui.QFont()
        # font.setPointSize(10)
        # font.setBold(True)
        # font.setWeight(75)
        # self.lineEdit.setFont(font)
        # self.lineEdit.setReadOnly(True)
        # self.lineEdit.setObjectName("lineEdit")
        # self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)

        # Graph's Widget
        self.lte_widget = LineChart(self.lte_GArea, self.title,
                                     self.lte_tableWidget, None,
                                     self.database)
        # self.lte_widget.setGeometry(QtCore.QRect(10, 9, 581, 351))
        # self.lte_widget.resize(self.lte_widget.sizeHint())
        self.lte_widget.setObjectName("lte_widget")
        self.lte_GArea.setWidget(self.lte_widget)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        layout.addWidget(self.lte_GArea)
        layout.addWidget(self.lte_tableWidget)

        # layout.addWidget(self.datelabel)
        # layout.addWidget(self.lineEdit)
        # layout.addWidget(self.lte_widget)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(
            _translate("LTE_LCwidget", "LTE Line Chart [MS1]"))
        item = self.lte_tableWidget.verticalHeaderItem(0)
        item.setText(_translate("LTE_LCwidget", "1"))
        item = self.lte_tableWidget.verticalHeaderItem(1)
        item.setText(_translate("LTE_LCwidget", "2"))
        item = self.lte_tableWidget.verticalHeaderItem(2)
        item.setText(_translate("LTE_LCwidget", "3"))
        item = self.lte_tableWidget.verticalHeaderItem(3)
        item.setText(_translate("LTE_LCwidget", "4"))
        item = self.lte_tableWidget.verticalHeaderItem(4)
        item.setText(_translate("LTE_LCwidget", "5"))
        item = self.lte_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("LTE_LCwidget", "Element"))
        item = self.lte_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("LTE_LCwidget", "Value"))
        item = self.lte_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("LTE_LCwidget", "MS"))
        item = self.lte_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("LTE_LCwidget", "Color"))
        __sortingEnabled = self.lte_tableWidget.isSortingEnabled()
        self.lte_tableWidget.setSortingEnabled(False)
        item = self.lte_tableWidget.item(0, 0)
        item.setText(_translate("LTE_LCwidget", "SINR Rx[0][1]"))
        item = self.lte_tableWidget.item(0, 2)
        item.setText(_translate("LTE_LCwidget", "MS1"))
        item = self.lte_tableWidget.item(1, 0)
        item.setText(_translate("LTE_LCwidget", "SINR Rx[1][1]"))
        item = self.lte_tableWidget.item(1, 2)
        item.setText(_translate("LTE_LCwidget", "MS1"))
        item = self.lte_tableWidget.item(2, 0)
        item.setText(_translate("LTE_LCwidget", "Inst RSRP[1]"))
        item = self.lte_tableWidget.item(2, 2)
        item.setText(_translate("LTE_LCwidget", "MS1"))
        item = self.lte_tableWidget.item(3, 0)
        item.setText(_translate("LTE_LCwidget", "Inst RSRQ[1]"))
        item = self.lte_tableWidget.item(3, 2)
        item.setText(_translate("LTE_LCwidget", "MS1"))
        item = self.lte_tableWidget.item(4, 0)
        item.setText(_translate("LTE_LCwidget", "Inst RSSI[1]"))
        item = self.lte_tableWidget.item(4, 2)
        item.setText(_translate("LTE_LCwidget", "MS1"))
        self.lte_tableWidget.setSortingEnabled(__sortingEnabled)
        # self.datelabel.setText(_translate("LTE_LCwidget", "Date :"))

    def moveChart(self, sampledate):
        self.lte_widget.moveLineChart(sampledate)


# WCDMA Line Chart UI
class Ui_WCDMA_LCwidget(QWidget):
    def __init__(self, parent, windowName, azenqosDB):
        super().__init__(parent)
        self.title = windowName
        self.database = azenqosDB
        self.width = 640
        self.height = 480
        self.maximumHeight = 480
        self.maximumWidth = 640
        self.setupUi()

    def setupUi(self):
        self.setObjectName("WCDMA_LCwidget")
        layout = QVBoxLayout(self)
        # self.resize(841, 586)

        # Graph Area
        self.wcdma_GArea = QScrollArea(self)
        self.wcdma_GArea.setGeometry(QtCore.QRect(20, 10, 801, 371))
        self.wcdma_GArea.setWidgetResizable(True)
        self.wcdma_GArea.setObjectName("wcdma_GArea")

        # Scroll Area
        # self.scrollAreaWidgetContents = QWidget()
        # self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 799, 369))
        # self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        # self.wcdma_GArea.setWidget(self.scrollAreaWidgetContents)

        # DataTable
        self.wcdma_tableWidget = QTableWidget(self)
        self.wcdma_tableWidget.setGeometry(QtCore.QRect(20, 395, 451, 161))
        self.wcdma_tableWidget.setObjectName("wcdma_tableWidget")
        self.wcdma_tableWidget.setColumnCount(4)
        self.wcdma_tableWidget.setRowCount(4)
        self.wcdma_tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.wcdma_tableWidget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        item = QTableWidgetItem()
        self.wcdma_tableWidget.setVerticalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.wcdma_tableWidget.setVerticalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.wcdma_tableWidget.setVerticalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.wcdma_tableWidget.setVerticalHeaderItem(3, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_tableWidget.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_tableWidget.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(0, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(0, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(0, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_tableWidget.setItem(0, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(1, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(1, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(1, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_tableWidget.setItem(1, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(2, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(2, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(2, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 124, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_tableWidget.setItem(2, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(3, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(3, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_tableWidget.setItem(3, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 119, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_tableWidget.setItem(3, 3, item)
        self.wcdma_tableWidget.horizontalHeader().setVisible(True)
        self.wcdma_tableWidget.horizontalHeader().setHighlightSections(True)
        self.wcdma_tableWidget.verticalHeader().setVisible(False)

        # DateLabel
        self.datelabel = QLabel(self)
        self.datelabel.setGeometry(QtCore.QRect(655, 38, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.datelabel.setFont(font)
        self.datelabel.setObjectName("datelabel")
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(703, 36, 88, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit.setFont(font)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)

        # Graph's Widget
        self.wcdma_widget = LineChart(self.wcdma_GArea,
                                       self.title, self.wcdma_tableWidget,
                                       None, self.database)
        self.wcdma_widget.setGeometry(QtCore.QRect(10, 9, 581, 351))
        self.wcdma_widget.resize(self.wcdma_widget.sizeHint())
        self.wcdma_widget.setObjectName("wcdma_widget")
        self.wcdma_GArea.setWidget(self.wcdma_widget)


        # Graph's Widget
        # self.lte_widget = LineChart(self.lte_GArea, self.title,
        #                              self.lte_tableWidget, None,self.database)
        # self.lte_widget.setGeometry(QtCore.QRect(10, 9, 581, 351))
        # self.lte_widget.resize(self.lte_widget.sizeHint())
        # self.lte_widget.setObjectName("lte_widget")
        # self.lte_GArea.setWidget(self.lte_widget)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        layout.addWidget(self.wcdma_GArea)
        layout.addWidget(self.wcdma_tableWidget)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(
            _translate("WCDMA_LCwidget", "WCDMA Line Chart [MS1]"))
        item = self.wcdma_tableWidget.verticalHeaderItem(0)
        item.setText(_translate("WCDMA_LCwidget", "1"))
        item = self.wcdma_tableWidget.verticalHeaderItem(1)
        item.setText(_translate("WCDMA_LCwidget", "2"))
        item = self.wcdma_tableWidget.verticalHeaderItem(2)
        item.setText(_translate("WCDMA_LCwidget", "3"))
        item = self.wcdma_tableWidget.verticalHeaderItem(3)
        item.setText(_translate("WCDMA_LCwidget", "4"))
        item = self.wcdma_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("WCDMA_LCwidget", "Element"))
        item = self.wcdma_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("WCDMA_LCwidget", "Value"))
        item = self.wcdma_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("WCDMA_LCwidget", "MS"))
        item = self.wcdma_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("WCDMA_LCwidget", "Color"))
        __sortingEnabled = self.wcdma_tableWidget.isSortingEnabled()
        self.wcdma_tableWidget.setSortingEnabled(False)
        item = self.wcdma_tableWidget.item(0, 0)
        item.setText(_translate("WCDMA_LCwidget", "ASET Ec/Io Avg."))
        item = self.wcdma_tableWidget.item(0, 2)
        item.setText(_translate("WCDMA_LCwidget", "MS1"))
        item = self.wcdma_tableWidget.item(1, 0)
        item.setText(_translate("WCDMA_LCwidget", "WCDMA RSSI"))
        item = self.wcdma_tableWidget.item(1, 2)
        item.setText(_translate("WCDMA_LCwidget", "MS1"))
        item = self.wcdma_tableWidget.item(2, 0)
        item.setText(_translate("WCDMA_LCwidget", "BLER Average Percent"))
        item = self.wcdma_tableWidget.item(2, 2)
        item.setText(_translate("WCDMA_LCwidget", "MS1"))
        item = self.wcdma_tableWidget.item(3, 0)
        item.setText(_translate("WCDMA_LCwidget", "ASET RSCP Avg."))
        item = self.wcdma_tableWidget.item(3, 2)
        item.setText(_translate("WCDMA_LCwidget", "MS1"))
        self.wcdma_tableWidget.setSortingEnabled(__sortingEnabled)
        self.datelabel.setText(_translate("WCDMA_LCwidget", "Date :"))

    def moveChart(self, sampledate):
        self.wcdma_widget.moveLineChart(sampledate)


# LTE Data Line Chart UI
class Ui_LTE_Data_LCwidget(QWidget):
    def __init__(self, parent, windowName, azenqosDB):
        super().__init__(parent)
        self.title = windowName
        self.database = azenqosDB
        self.width = 640
        self.height = 480
        self.maximumHeight = 480
        self.maximumWidth = 640
        self.setupUi()

    def setupUi(self):
        self.setObjectName("LTE_Data_LCwidget")
        self.resize(841, 586)

        # Graph Area
        self.lte_datalc_GArea = QScrollArea(self)
        self.lte_datalc_GArea.setGeometry(QtCore.QRect(20, 10, 801, 371))
        self.lte_datalc_GArea.setWidgetResizable(True)
        self.lte_datalc_GArea.setObjectName("lte_datalc_GArea")

        # Scroll Area
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 799, 369))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.lte_datalc_GArea.setWidget(self.scrollAreaWidgetContents)

        # DataTable
        self.lte_data_tableWidget = QTableWidget(self)
        self.lte_data_tableWidget.setGeometry(QtCore.QRect(20, 395, 530, 161))
        self.lte_data_tableWidget.setObjectName("lte_data_tableWidget")
        self.lte_data_tableWidget.setColumnCount(4)
        self.lte_data_tableWidget.setRowCount(4)
        self.lte_data_tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.lte_data_tableWidget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        item = QTableWidgetItem()
        self.lte_data_tableWidget.setVerticalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.lte_data_tableWidget.setVerticalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.lte_data_tableWidget.setVerticalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.lte_data_tableWidget.setVerticalHeaderItem(3, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_data_tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_data_tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_data_tableWidget.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.lte_data_tableWidget.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(0, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(0, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(0, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_data_tableWidget.setItem(0, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(1, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(1, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(1, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_data_tableWidget.setItem(1, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(2, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(2, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(2, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 124, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_data_tableWidget.setItem(2, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(3, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(3, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.lte_data_tableWidget.setItem(3, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 119, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.lte_data_tableWidget.setItem(3, 3, item)
        self.lte_data_tableWidget.horizontalHeader().setVisible(True)
        self.lte_data_tableWidget.horizontalHeader().setHighlightSections(True)
        self.lte_data_tableWidget.verticalHeader().setVisible(False)

        # DateLabel
        self.datelabel = QLabel(self)
        self.datelabel.setGeometry(QtCore.QRect(655, 38, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.datelabel.setFont(font)
        self.datelabel.setObjectName("datelabel")
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(703, 36, 88, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit.setFont(font)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)

        # Graph's Widget
        self.lte_data_widget = LineChart(self.scrollAreaWidgetContents,
                                          self.title,
                                          self.lte_data_tableWidget,
                                          self.lineEdit,
                                          self.database)
        self.lte_data_widget.setGeometry(QtCore.QRect(10, 9, 781, 351))
        self.lte_data_widget.setObjectName("lte_data_widget")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(
            _translate("LTE_Data_LCwidget", "LTE Data Line Chart [MS1]"))
        item = self.lte_data_tableWidget.verticalHeaderItem(0)
        item.setText(_translate("LTE_Data_LCwidget", "1"))
        item = self.lte_data_tableWidget.verticalHeaderItem(1)
        item.setText(_translate("LTE_Data_LCwidget", "2"))
        item = self.lte_data_tableWidget.verticalHeaderItem(2)
        item.setText(_translate("LTE_Data_LCwidget", "3"))
        item = self.lte_data_tableWidget.verticalHeaderItem(3)
        item.setText(_translate("LTE_Data_LCwidget", "4"))
        item = self.lte_data_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("LTE_Data_LCwidget", "Element"))
        item = self.lte_data_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("LTE_Data_LCwidget", "Value"))
        item = self.lte_data_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("LTE_Data_LCwidget", "MS"))
        item = self.lte_data_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("LTE_Data_LCwidget", "Color"))
        __sortingEnabled = self.lte_data_tableWidget.isSortingEnabled()
        self.lte_data_tableWidget.setSortingEnabled(False)
        item = self.lte_data_tableWidget.item(0, 0)
        item.setText(
            _translate("LTE_Data_LCwidget",
                       "Download Overall Throughput(kbps)"))
        item = self.lte_data_tableWidget.item(0, 2)
        item.setText(_translate("LTE_Data_LCwidget", "MS1"))
        item = self.lte_data_tableWidget.item(1, 0)
        item.setText(
            _translate("LTE_Data_LCwidget", "Upload Overall Throughput(kbps)"))
        item = self.lte_data_tableWidget.item(1, 2)
        item.setText(_translate("LTE_Data_LCwidget", "MS1"))
        item = self.lte_data_tableWidget.item(2, 0)
        item.setText(
            _translate("LTE_Data_LCwidget", "LTE L1 Throughput Mbps[1]"))
        item = self.lte_data_tableWidget.item(2, 2)
        item.setText(_translate("LTE_Data_LCwidget", "MS1"))
        item = self.lte_data_tableWidget.item(3, 0)
        item.setText(_translate("LTE_Data_LCwidget", "LTE BLER[1]"))
        item = self.lte_data_tableWidget.item(3, 2)
        item.setText(_translate("LTE_Data_LCwidget", "MS1"))
        self.lte_data_tableWidget.setSortingEnabled(__sortingEnabled)
        self.datelabel.setText(_translate("LTE_Data_LCwidget", "Date :"))

    def moveChart(self, sampledate):
        self.lte_data_widget.moveLineChart(sampledate)


# WCDMA Data Line Chart UI
class Ui_WCDMA_Data_LCwidget(QWidget):
    def __init__(self, parent, windowName, azenqosDB):
        super().__init__(parent)
        self.title = windowName
        self.database = azenqosDB
        self.width = 640
        self.height = 480
        self.maximumHeight = 480
        self.maximumWidth = 640
        self.setupUi()

    def setupUi(self):
        self.setObjectName("WCDMA_Data_LCwidget")
        layout = QVBoxLayout(self)

        # Graph Area
        self.wcdma_datalc_GArea = QScrollArea(self)
        self.wcdma_datalc_GArea.setGeometry(QtCore.QRect(20, 10, 801, 371))
        self.wcdma_datalc_GArea.setWidgetResizable(True)
        self.wcdma_datalc_GArea.setObjectName("wcdma_datalc_GArea")

        # Scroll Area
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 799, 369))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.wcdma_datalc_GArea.setWidget(self.scrollAreaWidgetContents)

        # DataTable
        self.wcdma_data_tableWidget = QTableWidget(
            self)
        self.wcdma_data_tableWidget.setGeometry(QtCore.QRect(
            20, 395, 515, 171))
        self.wcdma_data_tableWidget.setObjectName("wcdma_data_tableWidget")
        self.wcdma_data_tableWidget.setColumnCount(4)
        self.wcdma_data_tableWidget.setRowCount(4)
        self.wcdma_data_tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.wcdma_data_tableWidget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        item = QTableWidgetItem()
        self.wcdma_data_tableWidget.setVerticalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.wcdma_data_tableWidget.setVerticalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.wcdma_data_tableWidget.setVerticalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.wcdma_data_tableWidget.setVerticalHeaderItem(3, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_data_tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_data_tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_data_tableWidget.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.wcdma_data_tableWidget.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(0, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(0, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(0, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_data_tableWidget.setItem(0, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(1, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(1, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(1, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_data_tableWidget.setItem(1, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(2, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(2, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(2, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 124, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_data_tableWidget.setItem(2, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(3, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(3, 1, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.wcdma_data_tableWidget.setItem(3, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 119, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.wcdma_data_tableWidget.setItem(3, 3, item)
        self.wcdma_data_tableWidget.horizontalHeader().setVisible(True)
        self.wcdma_data_tableWidget.horizontalHeader().setHighlightSections(
            True)
        self.wcdma_data_tableWidget.verticalHeader().setVisible(False)

        # DateLabel
        self.datelabel = QLabel(WCDMA_Data_LCwidget)
        self.datelabel.setGeometry(QtCore.QRect(655, 38, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.datelabel.setFont(font)
        self.datelabel.setObjectName("datelabel")
        self.lineEdit = QLineEdit(WCDMA_Data_LCwidget)
        self.lineEdit.setGeometry(QtCore.QRect(703, 36, 88, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit.setFont(font)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)

        # Graph's Widget
        self.wcdma_data_widget = LineChart(self.scrollAreaWidgetContents,
                                            self.title,
                                            self.wcdma_data_tableWidget,
                                            self.lineEdit,
                                            self.database)
        self.wcdma_data_widget.setGeometry(QtCore.QRect(10, 9, 781, 351))
        self.wcdma_data_widget.setObjectName("wcdma_data_widget")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(
            _translate("WCDMA_Data_LCwidget", "WCDMA Data Line Chart [MS1]"))
        item = self.wcdma_data_tableWidget.verticalHeaderItem(0)
        item.setText(_translate("WCDMA_Data_LCwidget", "1"))
        item = self.wcdma_data_tableWidget.verticalHeaderItem(1)
        item.setText(_translate("WCDMA_Data_LCwidget", "2"))
        item = self.wcdma_data_tableWidget.verticalHeaderItem(2)
        item.setText(_translate("WCDMA_Data_LCwidget", "3"))
        item = self.wcdma_data_tableWidget.verticalHeaderItem(3)
        item.setText(_translate("WCDMA_Data_LCwidget", "4"))
        item = self.wcdma_data_tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("WCDMA_Data_LCwidget", "Element"))
        item = self.wcdma_data_tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("WCDMA_Data_LCwidget", "Value"))
        item = self.wcdma_data_tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("WCDMA_Data_LCwidget", "MS"))
        item = self.wcdma_data_tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("WCDMA_Data_LCwidget", "Color"))
        __sortingEnabled = self.wcdma_data_tableWidget.isSortingEnabled()
        self.wcdma_data_tableWidget.setSortingEnabled(False)
        item = self.wcdma_data_tableWidget.item(0, 0)
        item.setText(
            _translate("WCDMA_Data_LCwidget",
                       "WCDMA RLC DL Throughput (kbit/s)"))
        item = self.wcdma_data_tableWidget.item(0, 2)
        item.setText(_translate("WCDMA_Data_LCwidget", "MS1"))
        item = self.wcdma_data_tableWidget.item(1, 0)
        item.setText(
            _translate("WCDMA_Data_LCwidget",
                       "Application DL Throughput(kbps)[1]"))
        item = self.wcdma_data_tableWidget.item(1, 2)
        item.setText(_translate("WCDMA_Data_LCwidget", "MS1"))
        item = self.wcdma_data_tableWidget.item(2, 0)
        item.setText(
            _translate("WCDMA_Data_LCwidget",
                       "Download Session Average Throughput(kbps)"))
        item = self.wcdma_data_tableWidget.item(2, 2)
        item.setText(_translate("WCDMA_Data_LCwidget", "MS1"))
        item = self.wcdma_data_tableWidget.item(3, 0)
        item.setText(_translate("WCDMA_Data_LCwidget",
                                "Data HSDPA Throughput"))
        item = self.wcdma_data_tableWidget.item(3, 2)
        item.setText(_translate("WCDMA_Data_LCwidget", "MS1"))
        self.wcdma_data_tableWidget.setSortingEnabled(__sortingEnabled)
        self.datelabel.setText(_translate("WCDMA_Data_LCwidget", "Date :"))

    def moveChart(self, sampledate):
        self.wcdma_data_widget.moveLineChart(sampledate)

# WCDMA Pilot Analyzer Line Chart
class Ui_WCDMA_PA_LCwidget(QWidget):
    def __init__(self, parent, windowName, azenqosDB):
        super().__init__(parent)
        self.title = windowName
        self.database = azenqosDB
        self.width = 640
        self.height = 480
        self.maximumHeight = 480
        self.maximumWidth = 640
        self.setupUi()

    def setupUi(self):

        self.setObjectName("PA_widget")
        self.resize(841, 586)

        #Graph Area
        self.pa_GArea = QScrollArea(self)
        self.pa_GArea.setGeometry(QtCore.QRect(20, 10, 801, 371))
        self.pa_GArea.setWidgetResizable(True)
        self.pa_GArea.setObjectName("pa_GArea")

        #Scroll Area
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 799, 369))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        #Data Table
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(20, 390, 421, 171))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setRowCount(5)
        item = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(1, item)
        item = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(2, item)
        item = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(3, item)
        item = QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(4, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(0, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(0, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.tableWidget.setItem(0, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(1, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(1, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.tableWidget.setItem(1, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(2, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(2, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 124, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.tableWidget.setItem(2, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(3, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(3, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(255, 119, 171))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.tableWidget.setItem(3, 3, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(4, 0, item)
        item = QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignCenter)
        self.tableWidget.setItem(4, 2, item)
        item = QTableWidgetItem()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.tableWidget.setItem(4, 3, item)
        self.tableWidget.horizontalHeader().setVisible(True)
        self.tableWidget.horizontalHeader().setHighlightSections(True)
        self.tableWidget.verticalHeader().setVisible(False)

        #Data Label
        self.datelabel = QLabel(self)
        self.datelabel.setGeometry(QtCore.QRect(655, 38, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.datelabel.setFont(font)
        self.datelabel.setObjectName("datelabel")
        self.lineEdit = QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(703, 36, 88, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lineEdit.setFont(font)
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)

        self.pa_widget = LineChart(self.scrollAreaWidgetContents,
                                                self.title,
                                                self.tableWidget,
                                                self.lineEdit,
                                                self.database)
        self.pa_widget.setGeometry(QtCore.QRect(10, 9, 781, 351))
        self.pa_widget.setObjectName("pa_widget")
        self.pa_GArea.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("PA_widget", "WCDMA Pilot Analyzer [MS1]"))
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(_translate("PA_widget", "1"))
        item = self.tableWidget.verticalHeaderItem(1)
        item.setText(_translate("PA_widget", "2"))
        item = self.tableWidget.verticalHeaderItem(2)
        item.setText(_translate("PA_widget", "3"))
        item = self.tableWidget.verticalHeaderItem(3)
        item.setText(_translate("PA_widget", "4"))
        item = self.tableWidget.verticalHeaderItem(4)
        item.setText(_translate("PA_widget", "5"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("PA_widget", "Element"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("PA_widget", "Value"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("PA_widget", "Cell Type"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("PA_widget", "Color"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        self.tableWidget.setSortingEnabled(__sortingEnabled)

    def moveChart(self, sampledate):
        self.pa_widget.moveLineChart(sampledate)


# Class For Line Chart
class LineChart(QWidget):
    def __init__(self, parent, windowName, tablewidget, datelabel = None, azenqosDB = None):
        super().__init__(parent)

        self.database = azenqosDB

        #For pyqtgraph--------------------------------------------
        pg.setConfigOptions(foreground = '#000000',background = 'w',antialias = True)
        pg.TickSliderItem(orientation='bottom', allowAdd=True)
        self.canvas = pg.GraphicsWindow()

        #SetLayOut(Both)
        vertical_layout = QVBoxLayout(parent)
        vertical_layout.addWidget(self.canvas)

        #pyqtgraph Defualt Setting---------------------------------------------------------
        self.stringaxis = pg.AxisItem(orientation='bottom')
        self.canvas.axes = self.canvas.addPlot(axisItems={'bottom': self.stringaxis})
        self.setLayout(vertical_layout)
        self.canvas.axes.hideButtons()
        self.canvas.axes.disableAutoRange()
        self.canvas.axes.showGrid(y=True)
        self.canvas.axes.setMouseEnabled(x=True, y=False)
        self.canvas.axes.scene().sigMouseClicked.connect(self.get_table_data)
        #----------------------------------------------------------------------------------

        self.title = windowName
        self.tablewidget = tablewidget
        # self.datelabel = datelabel
        self.Date = []
        self.Time = []
        self.lines = []
        self.result = {}
        self.xdict = {}
        self.ColorArr = []

        self.datelabel = QLineEdit(self)
        self.datelabel.setGeometry(QtCore.QRect(400, 30, 110, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.datelabel.setFont(font)
        self.datelabel.setReadOnly(True)
        self.datelabel.setObjectName("lineEdit")
        self.datelabel.setAlignment(QtCore.Qt.AlignCenter)

        # Choose Line Chart By WindowName
        if self.title == 'LTE_LTE Line Chart':
            self.LTE()
        elif self.title == 'WCDMA_Line Chart':
            self.WCDMA()
        elif self.title == 'Data_LTE Data Line Chart':
            self.LTE_Data()
        elif self.title == 'Data_WCDMA Data Line Chart':
            self.WCDMA_Data()

    # Event Function
    def on_pick(self,event):
    #For pyqtgraph---------------------------------------------------------------------
        for Line in range(len(self.lines)):
            if self.lines[Line] == event:
                self.lines[Line].setPen(pg.mkPen(color=self.ColorArr[Line],width=4))
            else:
                self.lines[Line].setPen(pg.mkPen(color=self.ColorArr[Line],width=2))

    # Show Data In Table
    def get_table_data(self, event):
        Chart_datalist = []
        #For pyqtgraph-----------------------------------------------
        mousePoint = self.canvas.axes.vb.mapSceneToView(event.pos())
        x, y = int(mousePoint.x()), mousePoint.y()
        #For Matplotlib----------------------------------------------
        # x, y = int(event.xdata), event.ydata
        #------------------------------------------------------------

        for dict_item in self.result.items():
            keyStr = dict_item[0]
            if not keyStr.endswith('time'):
                Chart_datalist.append(dict_item[1][x])
        for row in range(len(Chart_datalist)):
            Value = round(Chart_datalist[row], 3)
            self.tablewidget.item(row, 1).setText(str(Value))


    # Create LTE Line Chart
    def LTE(self):
        # Open Database And Query
        ChartQuery = LineChartQuery([
            'time', 'lte_sinr_rx0_1', 'lte_sinr_rx1_1', 'lte_inst_rsrp_1',
            'lte_inst_rsrq_1', 'lte_inst_rssi_1'
        ], 'lte_cell_meas', '', self.database)
        self.result = ChartQuery.getData()
        for index in range(len(self.result['time'])):
            self.Date.append(self.result['time'][index].split(' ')[0])
            self.Time.append(self.result['time'][index].split(' ')[1])

        if self.result['time'] != '':
            # Graph setting
            self.datelabel.setText("Date: " + self.Date[0])
            # For Matplotlib-----------------------------------------
            # self.canvas.axes.set_title('LTE Line Chart')
            # self.canvas.axes.set_facecolor('#fef8e7')
            # self.canvas.axes.autoscale(False)
            # self.canvas.axes.xaxis.grid(True)
            # self.canvas.axes.yaxis.grid(True)
            # self.canvas.axes.set_xticklabels(self.Time)
            # self.canvas.axes.yaxis.set_major_locator(plt.MaxNLocator(10))
            # self.canvas.axes.yaxis.set_major_formatter(plt.ScalarFormatter())

            # Ploting Graph
            self.ColorArr = ['#ff0000', '#0000ff', '#007c00', '#ff77ab', '#000000']

            # For Matplotlib-----------------------------------------
            # for data in self.result.items():
            #     if data[0] != 'time':
            #         newline, = self.canvas.axes.plot(self.Time,
            #                                          data[1]
            #                                          )
            #         self.lines.append(newline, )
            #for colorindex in range(len(self.lines)):
                #self.lines[colorindex].set_color(self.ColorArr[colorindex])

            # Scale Editing
            # self.canvas.axes.set_ylim(-120, 20)
            # self.canvas.axes.set_xlim(self.Time[0], self.Time[4])

            # Call Event Function
            # pick = self.canvas.mpl_connect('pick_event', self.on_pick)
            # tabledata = self.canvas.mpl_connect('button_press_event',self.get_table_data)

            # For pyqtgraph-----------------------------------------------------------------
            x = self.Time
            self.xdict = dict(enumerate(x))
            self.stringaxis.setTicks([self.xdict.items()])
            for data in self.result.items():
                if data[0] != 'time':
                    newline = self.canvas.axes.plot(x=list(self.xdict.keys()),y=data[1])
                    newline.curve.setClickable(True)
                    self.lines.append(newline)

            for colorindex in range(len(self.lines)):
                self.lines[colorindex].setPen(pg.mkPen(self.ColorArr[colorindex],width=2))

            # Scale Editing
            self.canvas.axes.setYRange(-120,30)
            self.canvas.axes.setXRange(list(self.xdict.keys())[0],list(self.xdict.keys())[4])

            # Call Event Function
            pick = [self.lines[i].sigClicked.connect(self.on_pick) for i in range(len(self.lines))]

    # Create WCDMA Line Chart
    def WCDMA(self):

        # ยังไม่เสร็จ -- No data in Database

        # Open Database And Query

        condition = """LEFT JOIN wcdma_rx_power wrp ON wcm.time = wrp.time
                       LEFT JOIN wcdma_bler wb ON wcm.time = wb.time"""
        ChartQuery = LineChartQuery(['wcm.time','wcm.wcdma_aset_ecio_avg','wcm.wcdma_aset_rscp_avg',
                    'wrp.wcdma_rssi','wb.wcdma_bler_average_percent_all_channels'],'wcdma_cell_meas wcm',condition,self.database)
        self.result = ChartQuery.getData()

        for index in range(len(self.result['wcm.time'])):
            self.Date.append(self.result['wcm.time'][index].split(' ')[0])
            self.Time.append(self.result['wcm.time'][index].split(' ')[1])

        if self.result['wcm.time'] != '':
            # Graph setting
            self.datelabel.setText(self.Date[0])
            # For Matplotlib-----------------------------------------
            # self.canvas.axes.set_title('WCDMA Line Chart')
            # self.canvas.axes.set_facecolor('#fef8e7')
            # self.canvas.axes.autoscale(False)
            # self.canvas.axes.xaxis.grid(True)
            # self.canvas.axes.yaxis.grid(True)
            # self.canvas.axes.set_xticklabels(self.Time)
            # self.canvas.axes.yaxis.set_major_locator(plt.MaxNLocator(10))
            # self.canvas.axes.yaxis.set_major_formatter(plt.ScalarFormatter())

            # Ploting Graph
            self.ColorArr = ['#ff0000', '#0000ff', '#007c00', '#ff77ab', '#000000']
            # For Matplotlib-----------------------------------------
            # for data in self.result.items():
            #     if data[0] != 'wcm.time':
            #         newline, = self.canvas.axes.plot(self.Time,
            #                                          data[1],
            #                                          picker=5,
            #                                          linewidth=1)
            #         self.lines.append(newline, )

            # for colorindex in range(len(self.lines)):
            #     self.lines[colorindex].set_color(ColorArr[colorindex])

            # Scale Editing
            # self.canvas.axes.set_ylim(-120, 20)
            # self.canvas.axes.set_xlim(self.Time[0], self.Time[4])

            # Call Event Function
            # pick = self.canvas.mpl_connect('pick_event', self.on_pick)
            # tabledata = self.canvas.mpl_connect('button_press_event',
            #                                     self.get_table_data)

            # For pyqtgraph-----------------------------------------------------------------
            x = self.Time
            self.xdict = dict(enumerate(x))
            self.stringaxis.setTicks([self.xdict.items()])
            for data in self.result.items():
                    if data[0] != 'wcm.time':
                        newline = self.canvas.axes.plot(x=list(self.xdict.keys()),y=data[1])
                        newline.curve.setClickable(True)
                        self.lines.append(newline)

            for colorindex in range(len(self.lines)):
                self.lines[colorindex].setPen(pg.mkPen(self.ColorArr[colorindex],width=2))

            # Scale Editing
            self.canvas.axes.setYRange(-120,20)
            self.canvas.axes.setXRange(list(self.xdict.keys())[0],list(self.xdict.keys())[4])

            # Call Event Function
            pick = [self.lines[i].sigClicked.connect(self.on_pick) for i in range(len(self.lines))]

    # Create WCDMA Data Line Chart
    def WCDMA_Data(self):

        # ยังไม่เสร็จ -- No data in Database

        # Open Database And Query

        condition = """LEFT JOIN data_app_throughput dat ON dwrs.time = dat.time
                       LEFT JOIN wcdma_hsdpa_stats whs ON dwrs.time = whs.time"""
        ChartQuery = LineChartQuery(['dwrs.time','dwrs.data_wcdma_rlc_dl_throughput','dat.data_app_dl_throughput_1',
                                    'dat.data_download_session_average','whs.data_hsdpa_thoughput'],'data_wcdma_rlc_stats dwrs',condition,self.database)
        self.result = ChartQuery.getData()

        for index in range(len(self.result['dwrs.time'])):
            self.Date.append(self.result['dwrs.time'][index].split(' ')[0])
            self.Time.append(self.result['dwrs.time'][index].split(' ')[1])

        if self.result['dwrs.time'] != '':
            # Graph setting
            self.datelabel.setText(self.Date[0])
            # For Matplotlib-----------------------------------------
            #self.canvas.axes.set_title('WCDMA Data Line Chart')
            # self.canvas.axes.set_facecolor('#fef8e7')
            # self.canvas.axes.autoscale(False)
            # self.canvas.axes.xaxis.grid(True)
            # self.canvas.axes.yaxis.grid(True)
            # self.canvas.axes.set_xticklabels(self.Time)
            # self.canvas.axes.yaxis.set_major_locator(plt.MaxNLocator(10))
            # self.canvas.axes.yaxis.set_major_formatter(plt.ScalarFormatter())

            # Ploting Graph
            self.ColorArr = ['#ff0000', '#0000ff', '#007c00', '#ff77ab', '#000000']
            # For Matplotlib-----------------------------------------
            # for data in self.result.items():
            #     if data[0] != 'dwrs.time':
            #         newline, = self.canvas.axes.plot(self.Time,
            #                                          data[1],
            #                                          picker=5,
            #                                          linewidth=1)
            #         self.lines.append(newline, )

            # for colorindex in range(len(self.lines)):
            #     self.lines[colorindex].set_color(ColorArr[colorindex])

            # Scale Editing
            # self.canvas.axes.set_ylim(-120, 20)
            # self.canvas.axes.set_xlim(self.Time[0], self.Time[4])

            # Call Event Function
            # pick = self.canvas.mpl_connect('pick_event', self.on_pick)
            # tabledata = self.canvas.mpl_connect('button_press_event',
            #                                     self.get_table_data)

            # For pyqtgraph-----------------------------------------------------------------
            x = self.Time
            self.xdict = dict(enumerate(x))
            self.stringaxis.setTicks([self.xdict.items()])
            for data in self.result.items():
                if data[0] != 'dwrs.time':
                    newline = self.canvas.axes.plot(x=list(self.xdict.keys()),y=data[1])
                    newline.curve.setClickable(True)
                    self.lines.append(newline)

            for colorindex in range(len(self.lines)):
                self.lines[colorindex].setPen(pg.mkPen(self.ColorArr[colorindex],width=2))

            # Scale Editing
            self.canvas.axes.setYRange(-120,20)
            self.canvas.axes.setXRange(list(self.xdict.keys())[0],list(self.xdict.keys())[4])

            # Call Event Function
            pick = [self.lines[i].sigClicked.connect(self.on_pick) for i in range(len(self.lines))]

    # Create LTE Data Line Chart
    def LTE_Data(self):

        # Open Database And Query
        condition = """LEFT JOIN data_app_throughput dat ON lldt.time = dat.time"""
        ChartQuery = LineChartQuery(['lldt.time','dat.data_download_overall','dat.data_upload_overall',
                        'lldt.lte_l1_throughput_mbps_1','lldt.lte_bler_1'],'lte_l1_dl_tp lldt',condition,self.database)
        self.result = ChartQuery.getData()

        for index in range(len(self.result['lldt.time'])):
            self.Date.append(self.result['lldt.time'][index].split(' ')[0])
            self.Time.append(self.result['lldt.time'][index].split(' ')[1])

        if self.result['lldt.time'] != '':
            # Graph setting
            self.datelabel.setText(self.Date[0])
            # For Matplotlib-----------------------------------------
            # self.canvas.axes.set_title('LTE Data Line Chart')
            # self.canvas.axes.set_facecolor('#fef8e7')
            # self.canvas.axes.autoscale(False)
            # self.canvas.axes.xaxis.grid(True)
            # self.canvas.axes.yaxis.grid(True)
            # self.canvas.axes.set_xticklabels(self.Time)
            # self.canvas.axes.yaxis.set_major_locator(plt.MaxNLocator(5))
            # self.canvas.axes.yaxis.set_major_formatter(plt.ScalarFormatter())

            # Ploting Graph
            self.ColorArr = ['#ff0000', '#0000ff', '#007c00', '#ff77ab', '#000000']
            # For Matplotlib-----------------------------------------
            # for data in self.result.items():
            #     if data[0] != 'lldt.time':
            #         newline, = self.canvas.axes.plot(self.Time,
            #                                          data[1],
            #                                          picker=5,
            #                                          linewidth=1)
            #         self.lines.append(newline, )

            # for colorindex in range(len(self.lines)):
            #     self.lines[colorindex].set_color(ColorArr[colorindex])

            # Scale Editing
            # self.canvas.axes.set_ylim(-5, 35)
            # self.canvas.axes.set_xlim(self.Time[0], self.Time[4])

            # Call Event Function
            # pick = self.canvas.mpl_connect('pick_event', self.on_pick)
            # tabledata = self.canvas.mpl_connect('button_press_event',
            #                                     self.get_table_data)

            # For pyqtgraph-----------------------------------------------------------------
            x = self.Time
            self.xdict = dict(enumerate(x))
            self.stringaxis.setTicks([self.xdict.items()])
            for data in self.result.items():
                if data[0] != 'lldt.time':
                    newline = self.canvas.axes.plot(x=list(self.xdict.keys()),y=data[1])
                    newline.curve.setClickable(True)
                    self.lines.append(newline)

            for colorindex in range(len(self.lines)):
                self.lines[colorindex].setPen(pg.mkPen(self.ColorArr[colorindex],width=2))

            # Scale Editing
            self.canvas.axes.setYRange(-5, 35)
            self.canvas.axes.setXRange(list(self.xdict.keys())[0],list(self.xdict.keys())[4])

            # Call Event Function
            pick = [self.lines[i].sigClicked.connect(self.on_pick) for i in range(len(self.lines))]

    def moveLineChart(self, sampledate):
        #For pyqtgraph-----------------------------------------------
        # Shift Part
        dateString = str(sampledate)
        timeString = dateString.split(' ')[1][:8]
        # timeString = '00:19:18'
        if len(self.Time) > 0:
            currentTimeindex = 0
            recentTimeindex = 0
            for timeItem in self.Time:
                time_without_ms = timeItem[:8]
                # if time_without_ms == timeString:
                if time_without_ms == timeString:
                    print(time_without_ms, timeString)
                    # if self.Time.index(timeItem) + 4 < len(self.Time):
                    currentTimeindex = self.Time.index(timeItem)
                    #     self.canvas.axes.setXRange(list(self.xdict.keys())[currentTimeindex],list(self.xdict.keys())[currentTimeindex+4])
                    #     break
                else:
                    if time_without_ms > timeString:
                        index = self.Time.index(timeItem) - 1
                        print(self.Time[index], timeString)
                        if self.Time[index] <= timeString:
                            currentTimeindex = index
                    # else:
                    #     currentTimeindex = self.Time.index(timeItem) - 1
                if currentTimeindex > 0:
                    if self.Time.index(timeItem) + 4 < len(self.Time):
                        self.canvas.axes.setXRange(list(self.xdict.keys())[currentTimeindex],list(self.xdict.keys())[currentTimeindex+4])
                        break

            #For Matplotlib----------------------------------------------
            # # Shift Part
            # dateString = str(sampledate)
            # timeString = dateString.split(' ')[1][:8]
            # currentTimeindex = 0
            # for timeItem in self.Time:
            #     if timeItem[:8] == timeString:
            #         if self.Time.index(timeItem)+4 < len(self.Time):
            #             currentTimeindex = self.Time.index(timeItem)
            #             self.canvas.axes.set_xlim(self.Time[currentTimeindex],
            #                                     self.Time[currentTimeindex + 4])
            #             break
            #         else:
            #             break
            # self.canvas.draw()
            #---------------------------------------------------------------------

            # Update table part
            Chart_datalist = []
            for dict_item in self.result.items():
                keyStr = dict_item[0]
                if not keyStr.endswith('time'):
                    Chart_datalist.append(dict_item[1][currentTimeindex])
            for row in range(len(Chart_datalist)):
                Value = round(Chart_datalist[row], 3)
                self.tablewidget.item(row, 1).setText(str(Value))

    def resizeEvent(self, QResizeEvent):
        size = QResizeEvent.size()
        width = size.width()
        height = size.height()
        datalabelX = int((width * 0.94) - 110)
        datalabelY = int((height * 0.11) - 20)
        # print(datalabelX)
        # print(datalabelY)
        self.datelabel.move(QPoint(datalabelX, datalabelY))

class LineChartQuery:
    def __init__(self, fieldArr, tableName, conditionStr, azenqosDatabase):
        self.fieldArr = fieldArr
        self.tableName = tableName
        self.condition = conditionStr
        self.result = dict()
        self.database = azenqosDatabase

    def countField(self):
        fieldCount = 0
        if self.fieldArr is not None:
            fieldCount = len(self.fieldArr)
        return fieldCount

    def selectFieldToQuery(self):
        selectField = '*'
        if self.fieldArr is not None:
            selectField = ",".join(self.fieldArr)
        return selectField

    def getData(self):
        #result = dict()
        selectField = self.selectFieldToQuery()
        self.database.open()
        query = QSqlQuery()
        queryString = 'select %s from %s %s' % (selectField, self.tableName,
                                                self.condition)
        query.exec_(queryString)
        while query.next():
            for field in range(len(self.fieldArr)):
                fieldName = self.fieldArr[field]
                validatedValue = self.valueValidation(query.value(field))
                if fieldName in self.result:
                    if isinstance(self.result[fieldName], list):
                        self.result[fieldName].append(validatedValue)
                    else:
                        self.result[fieldName] = [validatedValue]
                else:
                    self.result[fieldName] = [validatedValue]

        if not self.result:
            for field in range(len(self.fieldArr)):
                fieldName = self.fieldArr[field]
                self.result[fieldName] = ''
        self.database.close()
        # print(self.result, lineno())
        return self.result

    def valueValidation(self, value):
        validatedValue = 0.00
        if value:
            validatedValue = value
        return validatedValue
