from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import * #QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import * #QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customize_properties import PropertiesWindow
import sys


class CustomizedWindowWidget(QWidget):
    dataSet = []
    def __init__(self, parent = None, windowName = None, database = None, currentTime = None):
        super().__init__(parent=parent)
        self.window_name = windowName
        self.properties_window = PropertiesWindow(self, database, self.dataSet)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)
        self.layout = QVBoxLayout()
        self.currentTime = currentTime
        self.header = []
        self.dataDict = None

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
        print(self.header)

    def setCurrentTime(self, value):
        if self.currentTime != value:
            self.currentTime = value

    def setDataSet(self, data_set):
        self.dataSet = data_set
        print(self.dataSet)

class CustomizeTable(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent=parent)



# class CustomizedTable(QTableWidget):
#     def __init__(self, int, int_, parent=None):
#         super().__init__(int, int_, parent=parent)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = CustomizedWindowWidget()
    ex.show()
    sys.exit(app.exec_())