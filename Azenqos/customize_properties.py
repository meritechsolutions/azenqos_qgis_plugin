from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtSql import QSqlQuery
import sys
from cell_content_header import HeaderContent
from customize_window_editor import CellSetting
from worker import Worker
import globalutils

MAX_COLUMNS = 50
MAX_ROWS = 1000


class PropertiesWindow(QWidget):
    def __init__(self, main_window=None, database=None, data_set=None):
        super().__init__(None)

        self.main_window = main_window
        self.db = database
        self.data_set = data_set

        self.previousColumnLength = 1
        self.previousRowLength = 1
        self.currentColumnLength = 1
        self.currentRowLength = 1
        self.currentColumnSelect = 0
        self.currentRowSelect = 0
        self.currentSelect = None
        self.parentCurrentSelect = None
        self.setupUi()
        self.setupComboBox()
        self.tempCustom = []

    def setupUi(self):
        self.setObjectName("Properties")
        self.setFixedSize(360, 360)
        self.setMouseTracking(False)
        self.verticalLayoutWidget = QWidget(self)
        self.verticalLayoutWidget.setGeometry(QRect(0, 0, 360, 320))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(10, 20, 10, 10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout

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
        self.buttonBox.setGeometry(QRect(13, 320, 331, 32))
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Close)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.buttonBox.accepted.connect(self.submit)
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
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.Table), _translate("Properties", "Table")
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.CellContent),
            _translate("Properties", "Cell Content"),
        )
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
        self.ledtTitle.setText(self.main_window.title)
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
        self.cbRows.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.cbRows.setMaxVisibleItems(5)
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
        self.cbColumns.setStyleSheet("QComboBox { combobox-popup: 0; }")
        self.cbColumns.setMaxVisibleItems(5)
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
        self.treeWidget.itemChanged.connect(self.changeTreeWidgetItem)
        self.treeWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.treeWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        header = self.treeWidget.header()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(False)

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
            self.cbColumns.addItem(str(column + 1))

        self.cbRows.clear()
        for row in range(MAX_ROWS):
            self.cbRows.addItem(str(row + 1))

        self.cbColumns.currentTextChanged.connect(self.onChangeColumns)
        self.cbRows.currentTextChanged.connect(self.onChangeRows)

        self.cbColumns.setCurrentText(
            str(self.main_window.tableModel.columnCount(self))
        )
        self.cbRows.setCurrentText(str(self.main_window.tableModel.rowCount(self)))

    def onChangeColumns(self, value):
        self.treeWidget.clear()
        if value:
            self.currentColumnLength = int(value)
            self.changeTreeWidget()

    def onChangeRows(self, value):
        self.treeWidget.clear()
        if value:
            self.currentRowLength = int(value)
            self.changeTreeWidget()

    def onClickTreeItem(self, current, previous):
        if current:
            self.currentSelect = current
            self.parentCurrentSelect = current.parent()
            if self.parentCurrentSelect:
                self.editBtn.setDisabled(False)
                parentName = self.parentCurrentSelect.text(0)
                if parentName == "Header":
                    self.parentName = "Header"
                else:
                    self.parentName = "Row"
                    if self.parentCurrentSelect.text(0).startswith("Row"):
                        self.currentRowSelect = int(
                            self.parentCurrentSelect.text(0).replace("Row ", "")
                        )
                        self.currentColumnSelect = (
                            self.parentCurrentSelect.indexOfChild(current) + 1
                        )
            else:
                self.editBtn.setDisabled(True)

    def editBtnEvent(self):
        if self.parentName:
            if self.parentName == "Header":
                self.editHeader()
            else:
                self.editRow()

    def editHeader(self):
        self.header_editor = HeaderContent(self.currentSelect)
        self.header_editor.show()

    def editRow(self):
        self.cell_setting = CellSetting(
            self,
            self.currentSelect,
            self.db,
            self.currentRowSelect,
            self.currentColumnSelect,
        )
        self.cell_setting.show()

    def changeTreeWidgetItem(self, data, col):
        previousCustom = next(
            (
                x
                for x in self.tempCustom
                if x["row"] == self.currentRowSelect - 1
                and x["column"] == self.currentColumnSelect - 1
            ),
            None,
        )
        if previousCustom:
            self.tempCustom.remove(previousCustom)
        self.tempCustom.append(
            {
                "row": self.currentRowSelect - 1,
                "column": self.currentColumnSelect - 1,
                "text": data.text(col),
            }
        )

    def changeTreeWidget(self):

        headers = []

        self.header = QTreeWidgetItem(self.treeWidget, ["Header"])

        for column in range(self.currentColumnLength):
            try:
                header_name = self.main_window.tableHeader[column]
            except:
                header_name = '""'
            headerItem = QTreeWidgetItem(self.header, [header_name])
            headers.append(header_name)

        rows = []
        for row in range(self.currentRowLength):
            columnlist = []
            rowItem = QTreeWidgetItem(self.treeWidget, [str("Row %i") % (row + 1)])
            for column in range(self.currentColumnLength):
                try:
                    column_name = str(self.data_set[row][column])
                    if not column_name:
                        column_name = '""'
                except:
                    column_name = '""'
                item = QTreeWidgetItem(rowItem, [column_name])
                columnlist.append(column_name)
            rows.append(columnlist)

        # self.data_set = self.getDataSet()

    def getHeaders(self):
        headerTable = []
        headerCount = self.header.childCount()
        for header in range(0, headerCount):
            headerTable.append(self.header.child(header).text(0))
        return headerTable

    def getDataSet(self):
        data = []
        toplevel_count = self.treeWidget.topLevelItemCount()
        for toplevel_index in range(1, toplevel_count):
            row = toplevel_index
            row_item = self.treeWidget.topLevelItem(toplevel_index)
            children_count = row_item.childCount()
            sub_data = []
            for child_index in range(0, children_count):
                column = child_index + 1
                text = row_item.child(child_index).text(0)
                if text == '""':
                    sub_data += [""]
                else:
                    sub_data += text.split(",")

            data.append(sub_data)
            # print(data)
            # ['table','value']
        return data

    def setDatabase(self, database):
        self.db = database

    def submit(self):
        title = self.ledtTitle.text()
        if title:
            self.main_window.setWindowTitle(title)

        headers = self.getHeaders()
        if headers:
            self.main_window.setHeader(headers)

        data_set = self.getDataSet()
        if data_set:
            self.main_window.setDataSet(data_set)

        if self.cbRows.currentText() and self.cbColumns.currentText():
            tableSize = [
                int(self.cbRows.currentText()),
                int(self.cbColumns.currentText()),
            ]
            self.main_window.setTableSize(tableSize)
            self.main_window.updateTable()

        self.main_window.customData = self.tempCustom
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PropertiesWindow()
    ex.show()
    sys.exit(app.exec_())
