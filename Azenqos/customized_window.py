from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import * #QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import * #QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customize_properties import PropertiesWindow
import sys


class CustomizedWindowWidget(QWidget):
    header = []
    dataSet = []
    rowCount = 0
    columnCount = 0
    def __init__(self, parent = None, windowName = None, database = None, currentTime = None):
        super().__init__(parent=parent)
        self.window_name = windowName
        self.database = database
        self.properties_window = PropertiesWindow(self, database, self.dataSet)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)
        self.layout = QVBoxLayout()
        self.currentTime = currentTime
        self.dataDict = None
        self.customizeTable = CustomizeTable(self, None, self.database, self.rowCount, self.columnCount)
        self.layout.addWidget(self.customizeTable)
        self.setLayout(self.layout)

    def generateMenu(self, pos):
        menu = QMenu()
        item1 = menu.addAction(u'Customize')
        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.properties_window.show()

    def setHeader(self, headers):
        self.header = headers
        print(self.header)

    def setCurrentTime(self, value: str):
        if self.currentTime != value:
            self.currentTime = value

    def setDataSet(self, data_set: list):
        self.dataSet = data_set
        print(self.dataSet)

    def setTableSize(self, sizelist: list):
        if sizelist:
            self.rowCount = sizelist[0]
            self.columnCount = sizelist[1]
            # self.updateTable()

    def updateTable(self):
        for data in self.dataSet:
            query = CustomizeQuery(self.database,self.dataSet,'',)
            return False

class CustomizeTable(QWidget):
    def __init__(self, parent, windowName: list, database, rowCount: int, columnCount: int):
        super().__init__(parent)
        self.title = windowName
        self.database = database
        self.tablename = ''
        self.tableHeader = None
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.dataList = []
        self.currentRow = 0
        self.dateString = ''
        self.setupUi()

    def setupUi(self):
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.tableView = QTableView(self)
        self.tableView.horizontalHeader().setSortIndicator(
            -1, Qt.AscendingOrder)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tableView)
        self.setLayout(layout)
        self.show()

    def setTableModel(self):
        self.tableModel = CustomizeModel(self.dataList, self.tableHeader, self)
        self.proxyModel = QtCore.QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.tableModel)
        self.tableView.setModel(self.proxyModel)
        self.tableView.resizeColumnsToContents()

    def setRowCount(self, value: int):
        self.tableModel.rowCount(value)

    def setColumnCount(self, value: int):
        self.tableModel.columnCount(value)


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
        condition = ''
        result = []
        if len(self.inputData) == 4 :
            #inputdata = ['table','value','row',column']
            if self.globalTime:
                condition = 'where time <= \'%s\'' % (self.globalTime)
            if not self.db.isOpen():
                self.db.open()
            query = QSqlQuery()
            queryString = 'select %s from %s %s LIMIT 1' % (self.inputData[1], self.inputData[0], condition)
            query.exec_(queryString)
            while query.next():
                result = [query.value(0), self.inputData[2], self.inputData[3]]
            self.db.close()
        else:
            #inputdata = ['text','row','column']
            result = [self.inputData[0], self.inputData[1], self.inputData[2]]
        return result


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = CustomizedWindowWidget()
    ex.show()
    sys.exit(app.exec_())