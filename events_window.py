# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import sqlite3
from datetime import datetime

maxtime = ''
mintime = ''

class Ui_MainWindow(object):
    def load_data(self):
        connection = sqlite3.connect("/Users/Maxorz/Desktop/replay/azqdata.db")
        query = "SELECT time, NULL, name, info FROM events"
        result = connection.execute(query)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(4)
        for row_number, row_data in enumerate(result):
            row_number + 1
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))
        query = "SELECT MAX(time), MIN(time) FROM events"
        cur = connection.cursor()
        cur.execute(query)
        result = cur.fetchone()
        maxtime = result[0]
        mintime = result[1]
        # print(datetime.strptime(mintime, '%Y-%m-%d %H:%M:%S.%f'))
        self.dateTimeEdit.setDateTime(datetime.strptime(str(mintime), '%Y-%m-%d %H:%M:%S.%f'))
        connection.close()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1024, 768)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(20, 40, 781, 411))
        self.tableWidget.setRowCount(5)
        self.tableWidget.setObjectName("tableWidget")

        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(40, 10, 160, 22))
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.horizontalSlider.setMinimum(0)
        self.horizontalSlider.setMaximum(100)
        # self.horizontalSlider.valueChanged(self.setTime)
        self.dateTimeEdit = QtWidgets.QDateTimeEdit(self.centralwidget)
        self.dateTimeEdit.setGeometry(QtCore.QRect(220, 10, 118, 22))
        self.dateTimeEdit.setObjectName("dateTimeEdit")
        self.load_data()
        print(mintime)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setHorizontalHeaderLabels(['Time', 'Eq.', 'Name', 'Info.'])
        self.tableWidget.setSortingEnabled(True)
        # self.tableWidget.setSortingEnabled(__sortingEnabled)

    def setTime(self):
        self.horizontalSlider.value()
        self.timeEdit.setDate(self.horizontalSlider.value())

