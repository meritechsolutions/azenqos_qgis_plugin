import sys

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QAbstractTableModel, QVariant, Qt
from PyQt5.QtSql import QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu, QTableView

from customize_properties import PropertiesWindow


class CustomizedWindowWidget(QWidget):
    header = []
    dataSet = []
    rowCount = 0
    columnCount = 0
    tableData = []
    databasePath = "/Users/Maxorz/Desktop/DB_Test/ARGazqdata.db"

    def __init__(self, parent=None, windowName=None, database=None, currentTime=None):
        super().__init__(parent=parent)
        self.window_name = windowName
        self.db = database
        self.addDatabase()
        self.properties_window = PropertiesWindow(self, self.db, self.dataSet)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)
        self.layout = QVBoxLayout()
        self.currentTime = currentTime
        self.customizeTable = CustomizeTable(
            self, None, self.db, self.rowCount, self.columnCount
        )
        self.layout.addWidget(self.customizeTable)
        self.setLayout(self.layout)

    def addDatabase(self):
        if self.db == None:
            self.db = QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(self.databasePath)

    def generateMenu(self, pos):
        menu = QMenu()
        item1 = menu.addAction(u"Customize")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.properties_window.show()

    def setHeader(self, headers):
        self.header = headers

    def setCurrentTime(self, value: str):
        if self.currentTime != value:
            self.currentTime = value

    def setDataSet(self, data_set: list):
        self.dataSet = data_set

    def setTableSize(self, sizelist: list):
        if sizelist:
            self.rowCount = sizelist[0]
            self.columnCount = sizelist[1]

    def updateTable(self):
        if self.rowCount > 0 and self.columnCount > 0:
            self.tableData = []
            for x in range(0, self.rowCount):
                dataPerRow = []
                for y in range(0, self.columnCount):
                    dataPerRow.append("")
                self.tableData.append(dataPerRow)
            if len(self.tableData) > 0:
                if self.dataSet:
                    for data in self.dataSet:
                        query = CustomizeQuery(self.db, data, "")
                        result = query.query()
                        row = result[1] - 1
                        column = result[2] - 1
                        self.tableData[row][column] = result[0]
                    self.cusvtomizeTable.setTableModel(self.tableData, self.header)

    # def structuerDatalist(self, )


class CustomizeTable(QWidget):
    def __init__(self, parent, windowName, database, rowCount: int, columnCount: int):
        super().__init__(parent)
        self.title = windowName
        self.database = database
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.currentRow = 0
        self.setupUi()

    def setupUi(self):
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.tableView = QTableView(self)
        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableView)
        self.setLayout(layout)
        self.show()

    def setTableModel(self, dataList: list, headers: list):
        self.tableModel = CustomizeModel(dataList, headers, self)
        self.proxyModel = QtCore.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.tableModel)
        self.tableView.setModel(self.proxyModel)
        self.tableView.resizeColumnsToContents()

    # def setRowCount(self, value: int):
    #     self.tableModel.rowCount(value)

    # def setColumnCount(self, value: int):
    #     self.tableModel.columnCount(value)


class CustomizeModel(QAbstractTableModel):
    def __init__(self, inputData, header, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.headerLabels = header
        self.dataSource = inputData

    def rowCount(self, parent):
        rows = 0
        if self.dataSource:
            rows = len(self.dataSource)
        return rows

    def columnCount(self, parent):
        columns = 0
        if self.headerLabels:
            columns = len(self.headerLabels)
        return columns

    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.dataSource[index.row()][index.column()])

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headerLabels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


class CustomizeQuery:
    def __init__(self, database, inputData: list, globalTime: str):
        self.db = database
        self.inputData = inputData
        self.globalTime = globalTime

    def query(self):
        condition = ""
        result = []
        if len(self.inputData) == 4:
            # inputdata = ['table','value','row',column']
            if self.globalTime:
                condition = "WHERE time <= '%s'" % (self.globalTime)
            if not self.db.isOpen():
                self.db.open()
            query = QSqlQuery()
            queryString = "SELECT %s FROM %s %s ORDER BY time DESC LIMIT 1" % (
                self.inputData[1],
                self.inputData[0],
                condition,
            )
            query.exec_(queryString)
            while query.next():
                result = [str(query.value(0)), self.inputData[2], self.inputData[3]]
            self.db.close()
        else:
            # inputdata = ['text','row','column']
            result = [self.inputData[0], self.inputData[1], self.inputData[2]]
        return result


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = CustomizedWindowWidget()
    ex.show()
    sys.exit(app.exec_())
