from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import * #QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import * #QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customize_properties import PropertiesWindow
import sys


class CustomizedWindowWidget(QWidget):
    def __init__(self, parent = None, windowName = None, database = None, currentTime = None):
        super().__init__(parent=parent)
        self.window_name = windowName
        self.properties_window = PropertiesWindow(self, database)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)
        self.layout = QVBoxLayout()
        self.currentTime = currentTime
        self.header = []

    def createCustomizeTable(self, row, column, data = None):
        if hasattr(self, 'tableView'):
            self.tableView.setRowCount(row)
            self.tableView.setColumnCount(column)
        else:
            self.tableView = QTableView(self)
            self.layout.addWidget(self.tableView)
            self.setLayout(self.layout)

    def generateMenu(self, pos):
        menu = QMenu()
        item1 = menu.addAction(u'Customize')
        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.properties_window.show()

    def setHeader(self, headers):
        self.header = headers

class CustomeizeQuery:
    def __init__(self, database, table, column, columnNo, rowNo, globalTime, dataList):
        self.db = database
        self.table = table
        self.column = column
        self.columnNo = columnNo
        self.rowNo = rowNo
        self.globalTime = globalTime
        self.dataList = dataList

    def query(self):
        self.db.open()
        query = QSqlQuery()
        queryString = 'select %s from %s where time >= \'%s\' LIMIT 1' % (self.column, self.table, self.globalTime)
        query.exec_(queryString)
        while query.next():
            result = [query.value(0), self.columnNo, self.rowNo]
            self.dataList.append(result)
        azenqosDatabase.close()
        return self.dataList



# class CustomizedTable(QTableWidget):
#     def __init__(self, int, int_, parent=None):
#         super().__init__(int, int_, parent=parent)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = CustomizedWindowWidget()
    ex.show()
    sys.exit(app.exec_())