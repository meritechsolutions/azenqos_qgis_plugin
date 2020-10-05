import sys
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from worker import Worker
from PyQt5.QtCore import *

threadpool = QThreadPool()


class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        print("data() role", role)
        if role == Qt.DisplayRole:
            # See below for the nested-list data structure.
            # .row() indexes into the outer list,
            # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def setData(self, index, data, role=QtCore.Qt.DisplayRole):
        self._data = data
        index_topleft = self.index(0, 0)
        index_bottomright = self.index(0, 1)
        self.dataChanged.emit(index_topleft, index_bottomright, [role])
        print("model setdata emit done")
        return True

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])


class MainWindow(QtWidgets.QMainWindow):
    signal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.table = QtWidgets.QTableView()

        data = [
            [4, 9, 2],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]

        self.model = TableModel(data)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)
        # self.change_data()
        self.signal.connect(self.onsignal)
        worker = Worker(self.change_data)
        threadpool.start(worker)

    def onsignal(self):
        print("onsignal")
        index_topleft = self.model.index(0, 0)
        index_bottomright = self.model.index(0, 1)
        self.model.dataChanged.emit(
            index_topleft, index_bottomright, [QtCore.Qt.DisplayRole]
        )
        self.update()

    def change_data(self):
        time.sleep(1)
        print("change_data()")
        data = [
            [1, 1, 1],
            [1, 0, 0],
            [3, 5, 0],
            [3, 3, 2],
            [7, 8, 9],
        ]
        self.model.setData(None, data)
        self.signal.emit()


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()
