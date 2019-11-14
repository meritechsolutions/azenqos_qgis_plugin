from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import * #QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import * #QSqlQuery, QSqlDatabase
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from customize_properties import PropertiesWindow
import sys

class MainWidget(QWidget):
    def __init__(self, parent = None, windowName = None):
        super().__init__(parent=parent)
        self.window_name = windowName
        self.properties_window = PropertiesWindow()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.generateMenu)

        ### This property holds how the widget shows a context menu
        # self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)     # +++
        ### This signal is emitted when the widget's contextMenuPolicy is Qt::CustomContextMenu,
        ### and the user has requested a context menu on the widget.
        # self.tableWidget.customContextMenuRequested.connect(self.generateMenu) # +++

        # self.tableWidget.viewport().installEventFilter(self)

        self.layout = QVBoxLayout()

    def createCustomizeTable(self, row, column):
        self.tableWidget = QTableWidget(row, column, self)
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

    def generateMenu(self, pos):
        menu = QMenu()
        item1 = menu.addAction(u'Customize')
        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.properties_window.show()


# class CustomizedTable(QTableWidget):
#     def __init__(self, int, int_, parent=None):
#         super().__init__(int, int_, parent=parent)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = MainWidget()
    ex.show()
    sys.exit(app.exec_())