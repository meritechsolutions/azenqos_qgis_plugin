# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'form.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from cell_content_header import HeaderContent
from customize_window_editor import CellSetting

MAX_COLUMNS = 10
MAX_ROWS = 100

class PropertiesWindow(QWidget):
    def __init__(self, main_window = None, database = None):
        super().__init__(None)
        
        self.main_window = main_window
        self.db = database
        
        self.currentColumn = 1
        self.currentRow = 1
        self.currentSelect = None
        self.setupUi()
        self.setupComboBox()

    def setupUi(self):
        self.setObjectName("Properties")
        self.setFixedSize(360,360)
        self.setMouseTracking(False)
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 360, 300))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(10, 20, 10, 10)
        self.verticalLayout.setObjectName("verticalLayout")

        self.tabWidget = QTabWidget(self.verticalLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tabWidget.setElideMode(Qt.ElideRight)
        self.tabWidget.setObjectName("tabWidget")

        self.setupTableTab()
        self.setupContentTab()

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setGeometry(QRect(13, 310, 331, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.close)
        self.buttonBox.rejected.connect(self.close)

        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi()
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(self)

    def createTable(self):
        return False

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("Properties", "Properties"))
        self.lblTitle.setText(_translate("Properties", "Title"))
        self.lblRow.setText(_translate("Properties", "Row"))
        self.lblColumns.setText(_translate("Properties", "Columns"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Table), _translate("Properties", "Table"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.CellContent), _translate("Properties", "Cell Content"))
        self.editBtn.setText(_translate("Properties", "Edit"))
        self.mobileLbl.setText(_translate("Properties", "Mobile"))
        self.setAllBtn.setText(_translate("Properties", "Set All"))

    def setupTableTab(self):
        self.Table = QWidget()
        self.Table.setEnabled(True)
        self.Table.setObjectName("Table")
        
        self.formLayoutWidget = QWidget(self.Table)
        self.formLayoutWidget.setGeometry(QRect(0, 0, 331, 301))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(30, 20, 10, 10)
        self.formLayout.setSpacing(10)
        self.formLayout.setObjectName("formLayout")
        
        self.lblTitle = QLabel(self.formLayoutWidget)
        self.lblTitle.setObjectName("lblTitle")
        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.lblTitle)
        
        self.ledtTitle = QLineEdit(self.formLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ledtTitle.sizePolicy().hasHeightForWidth())
        self.ledtTitle.setSizePolicy(sizePolicy)
        self.ledtTitle.setObjectName("ledtTitle")
        self.ledtTitle.setText("Status window")
        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.ledtTitle)
        
        self.lblRow = QLabel(self.formLayoutWidget)
        self.lblRow.setObjectName("lblRow")
        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.lblRow)
        
        self.cbRows = QComboBox(self.formLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbRows.sizePolicy().hasHeightForWidth())
        self.cbRows.setSizePolicy(sizePolicy)
        self.cbRows.setObjectName("cbRows")
        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.cbRows)
        
        self.lblColumns = QLabel(self.formLayoutWidget)
        self.lblColumns.setObjectName("lblColumns")
        self.formLayout.setWidget(5, QFormLayout.LabelRole, self.lblColumns)
        
        self.cbColumns = QComboBox(self.formLayoutWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbColumns.sizePolicy().hasHeightForWidth())
        self.cbColumns.setSizePolicy(sizePolicy)
        self.cbColumns.setLayoutDirection(Qt.LeftToRight)
        self.cbColumns.setObjectName("cbColumns")
        self.formLayout.setWidget(5, QFormLayout.FieldRole, self.cbColumns)
        self.tabWidget.addTab(self.Table, "")

    def setupContentTab(self):
        self.CellContent = QWidget()
        self.CellContent.setObjectName("CellContent")
        
        self.treeWidget = QTreeWidget(self.CellContent)
        self.treeWidget.setGeometry(QRect(10, 20, 251, 182))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setHeaderHidden(True)
        self.treeWidget.currentItemChanged.connect(self.onClickTreeItem)
        
        self.editBtn = QPushButton(self.CellContent)
        self.editBtn.setGeometry(QRect(262, 20, 71, 31))
        self.editBtn.setObjectName("editBtn")
        self.editBtn.setDisabled(True)
        self.editBtn.clicked.connect(self.editBtnEvent)
        
        self.mobileLbl = QLabel(self.CellContent)
        self.mobileLbl.setGeometry(QRect(10, 210, 61, 31))
        self.mobileLbl.setObjectName("mobileLbl")
        
        self.mobileCb = QComboBox(self.CellContent)
        self.mobileCb.setGeometry(QRect(60, 210, 71, 31))
        self.mobileCb.setObjectName("mobileCb")
        
        self.setAllBtn = QPushButton(self.CellContent)
        self.setAllBtn.setGeometry(QRect(130, 210, 91, 32))
        self.setAllBtn.setObjectName("setAllBtn")
        self.tabWidget.addTab(self.CellContent, "")

    def setupComboBox(self):
        self.cbColumns.clear()
        for column in range(MAX_COLUMNS):
            if column == 0:
                self.cbColumns.addItem("")
            else:
                self.cbColumns.addItem(str(column))
            
        self.cbRows.clear()
        for row in range(MAX_ROWS):
            if row == 0:
                self.cbRows.addItem("")
            else:
                self.cbRows.addItem(str(row))
            
        self.cbColumns.currentTextChanged.connect(self.onChangeColumns)
        self.cbRows.currentTextChanged.connect(self.onChangeRows)
        
    def onChangeColumns(self, value):
        self.treeWidget.clear()
        if value:
            self.currentColumn = int(value)
            self.changeTreeWidget()
    
    def onChangeRows(self, value):
        self.treeWidget.clear()
        if value:
            self.currentRow = int(value)
            self.changeTreeWidget()
        
    def onClickTreeItem(self, current, previous):
        if current:
            self.currentSelect = current
            parent_element = current.parent() 
            if parent_element:
                self.editBtn.setDisabled(False)
                parentName = parent_element.text(0)
                if parentName == 'Header':
                    self.parentName = 'Header'
                else:
                    self.parentName = 'Row'
            else:
                self.editBtn.setDisabled(True)
            
    def editBtnEvent(self):
        if self.parentName:
            if self.parentName == 'Header':
                self.editHeader()
            else:
                self.editRow()
    
    def editHeader(self):
        self.header_editor = HeaderContent(self.currentSelect)
        self.header_editor.show()
    
    def editRow(self):
        self.cell_setting = CellSetting(self.currentSelect, self.db)
        self.cell_setting.show()
    
    def changeTreeWidget(self):
        header = QTreeWidgetItem(self.treeWidget, ['Header'])
        for column in range(self.currentColumn):
            QTreeWidgetItem(header, ['\"\"'])
        for row in range(self.currentRow):
            rowItem = QTreeWidgetItem(self.treeWidget, [str('Row %i') % (row + 1)])
            for column in range(self.currentColumn):
                item = QTreeWidgetItem(rowItem, [str('Column %i') % (column + 1)])
        
        
class CustomizeTable(QTableWidget):
    def __init__(self):
        super().__init__(None)
    
    def setStructure(self, row, column, data):
        self.setRowCount(row)
        self.setColumnCount(column)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PropertiesWindow()
    ex.show()
    sys.exit(app.exec_())