import pandas as pd
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QCheckBox, QItemDelegate


class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001
    COL_PARAM_NAME = 0
    COL_MAIN_PARAM = 1

    def __init__(self, items=[], parent=None):
        super(DataFrameModel, self).__init__(parent)
        self.items = items.copy()
        self._columns_list = ["parameter name", "main parameter"]

    def setItems(self, items):
        self.beginResetModel()
        self.items = items.copy()
        self.endResetModel()
    
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        self.beginResetModel()
        if role == QtCore.Qt.CheckStateRole and index.column() == self.COL_MAIN_PARAM:
            col_name = self._columns_list[index.column()]
            if value == QtCore.Qt.Checked:
                for item in self.items:
                    item[col_name] = False
                self.items[index.row()][col_name] = True
            else:
                self.items[index.row()][col_name] = False
        self.endResetModel()
        return True


    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.DisplayRole,
    ):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._columns_list[section])
        return QtCore.QVariant()
       

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.items)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._columns_list)

    # def flags(self, index):
    #     if index.column() == self.COL_MAIN_PARAM:
    #         return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
    #     return QtCore.Qt.ItemIsEnabled

    def flags(self, index):
        if not index.isValid():
            return None
        if index.column() == self.COL_MAIN_PARAM:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (
            0 <= index.row() < self.rowCount()
            and 0 <= index.column() < self.columnCount()
        ):
            return QtCore.QVariant()

        col = index.column()
        row = index.row()

        col_name = self._columns_list[col]

        if role == QtCore.Qt.DisplayRole:
            if col == self.COL_PARAM_NAME:
                return str(self.items[row][col_name])
        elif role == QtCore.Qt.CheckStateRole:
            if col == self.COL_MAIN_PARAM:
                if self.items[row][col_name]:
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked
        # elif role == QtCore.Qt.CheckStateRole:
        #     return None

        return QtCore.QVariant()


    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b"display",
            DataFrameModel.DtypeRole: b"dtype",
            DataFrameModel.ValueRole: b"value",
        }
        return roles
