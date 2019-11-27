# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cell_setting.ui'
#
# Created by: PyQt5 UI code generator 5.13.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class CellSetting(QWidget):
    def __init__(self, selectitem, database):
        super().__init__(None)
        
        self.selected_item = selectitem
        self.system_types = ['WCDMA', 'General', 'Positioning', 'Data', 'Non-Access-Stratum', 'Wifi', 'LTE', 'CDMA', 'Android', 'NB-IoT', 'Unlisted']
        self.system_data_obj = None
        self.setupUi()
        
    
    def setupUi(self):
        self.setObjectName("cellSetting")
        self.setWindowModality(Qt.WindowModal)
        self.setEnabled(True)
        self.resize(420, 400)
        self.setMinimumSize(QSize(420, 400))
        self.setMaximumSize(QSize(420, 400))
        self.setBaseSize(QSize(420, 400))
        
        self.tabWidget = QTabWidget(self)
        self.tabWidget.setGeometry(QRect(10, 20, 401, 321))
        self.tabWidget.setObjectName("tabWidget")
        
        self.CellContent = QWidget()
        self.CellContent.setObjectName("CellContent")
        
        self.rbInformationElement = QRadioButton(self.CellContent)
        self.rbInformationElement.setGeometry(QRect(10, 10, 151, 20))
        self.rbInformationElement.setObjectName("rbInformationElement")
        
        self.lblSystem = QLabel(self.CellContent)
        self.lblSystem.setGeometry(QRect(20, 40, 59, 16))
        self.lblSystem.setObjectName("lblSystem")
        
        self.cbSystem = QComboBox(self.CellContent)
        self.cbSystem.setGeometry(QRect(10, 60, 141, 32))
        self.cbSystem.setObjectName("cbSystem")
        
        self.lblMobile = QLabel(self.CellContent)
        self.lblMobile.setGeometry(QRect(180, 40, 59, 16))
        self.lblMobile.setObjectName("lblMobile")
        
        self.cbMobile = QComboBox(self.CellContent)
        self.cbMobile.setGeometry(QRect(170, 60, 111, 32))
        self.cbMobile.setObjectName("cbMobile")
        
        self.lblElement = QLabel(self.CellContent)
        self.lblElement.setGeometry(QRect(20, 100, 59, 16))
        self.lblElement.setObjectName("lblElement")
        
        self.fcbElement = QFontComboBox(self.CellContent)
        self.fcbElement.setGeometry(QRect(10, 120, 211, 32))
        self.fcbElement.setCurrentText("")
        self.fcbElement.setObjectName("fcbElement")
        
        self.lblArgument = QLabel(self.CellContent)
        self.lblArgument.setGeometry(QRect(250, 100, 61, 16))
        self.lblArgument.setObjectName("lblArgument")
        
        self.cbArgument = QComboBox(self.CellContent)
        self.cbArgument.setGeometry(QRect(240, 120, 111, 32))
        self.cbArgument.setObjectName("cbArgument")
        
        self.rbEventCounter = QRadioButton(self.CellContent)
        self.rbEventCounter.setGeometry(QRect(10, 160, 151, 20))
        self.rbEventCounter.setObjectName("rbEventCounter")
        
        self.fcbEventCounter = QFontComboBox(self.CellContent)
        self.fcbEventCounter.setGeometry(QRect(10, 180, 211, 32))
        self.fcbEventCounter.setCurrentText("")
        self.fcbEventCounter.setObjectName("fcbEventCounter")
        
        self.rbText = QRadioButton(self.CellContent)
        self.rbText.setGeometry(QRect(10, 220, 151, 20))
        self.rbText.setObjectName("rbText")
        
        self.leText = QLineEdit(self.CellContent)
        self.leText.setGeometry(QRect(10, 240, 211, 32))
        self.leText.setObjectName("leText")
        
        self.tabWidget.addTab(self.CellContent, "")
        
        self.bbCellContent = QDialogButtonBox(self)
        self.bbCellContent.setGeometry(QRect(250, 350, 164, 32))
        self.bbCellContent.setOrientation(Qt.Horizontal)
        self.bbCellContent.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
        self.bbCellContent.setObjectName("bbCellContent")

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(self)
        
        #Set signal events
        self.rbInformationElement.toggled.connect(self.rbInformationElementSelected)
        self.rbEventCounter.toggled.connect(self.rbEventCounterSelected)
        self.rbText.toggled.connect(self.rbTextSelected)
        self.rbText.setChecked(True)
        

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("cellSetting", "Cell setting"))
        self.rbInformationElement.setText(_translate("cellSetting", "Information Element"))
        self.lblSystem.setText(_translate("cellSetting", "System"))
        self.lblMobile.setText(_translate("cellSetting", "Mobile"))
        self.lblElement.setText(_translate("cellSetting", "Element"))
        self.lblArgument.setText(_translate("cellSetting", "Argument"))
        self.rbEventCounter.setText(_translate("cellSetting", "Event counter"))
        self.rbText.setText(_translate("cellSetting", "Text"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.CellContent), _translate("cellSetting", "Cell Content"))

    def rbTextSelected(self):
        self.leText.setEnabled(True)
        self.cbSystem.setDisabled(True)
        self.cbMobile.setDisabled(True)
        self.fcbElement.setDisabled(True)
        self.fcbEventCounter.setDisabled(True)
        self.cbArgument.setDisabled(True)
        
    def rbInformationElementSelected(self):
        self.fcbEventCounter.setDisabled(True)
        self.leText.setDisabled(True)
        self.cbSystem.setEnabled(True)
        self.cbMobile.setEnabled(True)
        self.fcbElement.setDisabled(True)
        self.cbArgument.setDisabled(True)
        
    def rbEventCounterSelected(self):
        self.cbSystem.setDisabled(True)
        self.cbMobile.setDisabled(True)
        self.fcbElement.setDisabled(True)
        self.fcbEventCounter.setEnabled(True)
        self.cbArgument.setDisabled(True)
        self.leText.setDisabled(True)
        
    def prepareSystemTypes(self):
        return False