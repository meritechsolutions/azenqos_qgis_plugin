# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cell_setting.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_cellSetting(object):
    def setupUi(self, cellSetting):
        cellSetting.setObjectName("cellSetting")
        cellSetting.setWindowModality(QtCore.Qt.WindowModal)
        cellSetting.setEnabled(True)
        cellSetting.resize(420, 360)
        cellSetting.setMinimumSize(QtCore.QSize(420, 360))
        cellSetting.setMaximumSize(QtCore.QSize(420, 360))
        cellSetting.setBaseSize(QtCore.QSize(420, 360))
        self.tabWidget = QtWidgets.QTabWidget(cellSetting)
        self.tabWidget.setGeometry(QtCore.QRect(10, 20, 401, 301))
        self.tabWidget.setObjectName("tabWidget")
        self.CellContent = QtWidgets.QWidget()
        self.CellContent.setObjectName("CellContent")
        self.InformationElement = QtWidgets.QRadioButton(self.CellContent)
        self.InformationElement.setGeometry(QtCore.QRect(10, 10, 151, 20))
        self.InformationElement.setChecked(True)
        self.InformationElement.setObjectName("InformationElement")
        self.lblSystem = QtWidgets.QLabel(self.CellContent)
        self.lblSystem.setGeometry(QtCore.QRect(20, 40, 59, 16))
        self.lblSystem.setObjectName("lblSystem")
        self.cbSystem = QtWidgets.QComboBox(self.CellContent)
        self.cbSystem.setGeometry(QtCore.QRect(10, 60, 141, 32))
        self.cbSystem.setObjectName("cbSystem")
        self.lblMobile = QtWidgets.QLabel(self.CellContent)
        self.lblMobile.setGeometry(QtCore.QRect(180, 40, 59, 16))
        self.lblMobile.setObjectName("lblMobile")
        self.cbMobile = QtWidgets.QComboBox(self.CellContent)
        self.cbMobile.setGeometry(QtCore.QRect(170, 60, 111, 32))
        self.cbMobile.setObjectName("cbMobile")
        self.lblElement = QtWidgets.QLabel(self.CellContent)
        self.lblElement.setGeometry(QtCore.QRect(20, 100, 59, 16))
        self.lblElement.setObjectName("lblElement")
        self.lblElement_2 = QtWidgets.QLabel(self.CellContent)
        self.lblElement_2.setGeometry(QtCore.QRect(250, 100, 61, 16))
        self.lblElement_2.setObjectName("lblElement_2")
        self.fontComboBox = QtWidgets.QFontComboBox(self.CellContent)
        self.fontComboBox.setGeometry(QtCore.QRect(10, 120, 211, 32))
        self.fontComboBox.setCurrentText("")
        self.fontComboBox.setObjectName("fontComboBox")
        self.cbMobile_2 = QtWidgets.QComboBox(self.CellContent)
        self.cbMobile_2.setGeometry(QtCore.QRect(240, 120, 111, 32))
        self.cbMobile_2.setObjectName("cbMobile_2")
        self.EventCounter = QtWidgets.QRadioButton(self.CellContent)
        self.EventCounter.setGeometry(QtCore.QRect(10, 160, 151, 20))
        self.EventCounter.setChecked(False)
        self.EventCounter.setObjectName("EventCounter")
        self.cbEventCounter = QtWidgets.QFontComboBox(self.CellContent)
        self.cbEventCounter.setGeometry(QtCore.QRect(10, 180, 211, 32))
        self.cbEventCounter.setCurrentText("")
        self.cbEventCounter.setObjectName("cbEventCounter")
        self.EventCounter_2 = QtWidgets.QRadioButton(self.CellContent)
        self.EventCounter_2.setGeometry(QtCore.QRect(10, 220, 151, 20))
        self.EventCounter_2.setChecked(False)
        self.EventCounter_2.setObjectName("EventCounter_2")
        self.cbEventCounter_2 = QtWidgets.QFontComboBox(self.CellContent)
        self.cbEventCounter_2.setGeometry(QtCore.QRect(10, 240, 211, 32))
        self.cbEventCounter_2.setCurrentText("")
        self.cbEventCounter_2.setObjectName("cbEventCounter_2")
        self.tabWidget.addTab(self.CellContent, "")
        self.bbCellContent = QtWidgets.QDialogButtonBox(cellSetting)
        self.bbCellContent.setGeometry(QtCore.QRect(250, 320, 164, 32))
        self.bbCellContent.setOrientation(QtCore.Qt.Horizontal)
        self.bbCellContent.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bbCellContent.setObjectName("bbCellContent")

        self.retranslateUi(cellSetting)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(cellSetting)

    def retranslateUi(self, cellSetting):
        _translate = QtCore.QCoreApplication.translate
        cellSetting.setWindowTitle(_translate("cellSetting", "Cell setting"))
        self.InformationElement.setText(_translate("cellSetting", "Information Element"))
        self.lblSystem.setText(_translate("cellSetting", "System"))
        self.lblMobile.setText(_translate("cellSetting", "Mobile"))
        self.lblElement.setText(_translate("cellSetting", "Element"))
        self.lblElement_2.setText(_translate("cellSetting", "Argument"))
        self.EventCounter.setText(_translate("cellSetting", "Event counter"))
        self.EventCounter_2.setText(_translate("cellSetting", "Text"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.CellContent), _translate("cellSetting", "Cell Content"))
