from PyQt5.QtCore import QAbstractTableModel, Qt


class PandasModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        
    def setItems(self, items):
        self.beginResetModel()
        self.items = items.copy()
        self.endResetModel()

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
        # The following takes the first sub-list, and returns
        # the length (only works if all rows are an equal length)
        return len(self._data[0])

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value = ""
                value_dict = self._data[index.row()][index.column()]
                if len(value_dict.keys()) > 0:
                    if "value" in value_dict.keys():
                        if value_dict["type"] == "text":
                            value = value_dict["value"]
                        else:
                            value = value_dict["param_name"]

                return str(value)

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            return True
        return False
        
    def flags(self, index):
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable