from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QSortFilterProxyModel, QRegExp, Qt
from PyQt5.QtWidgets import QHeaderView


class SortFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}
        self.filterFromMenu = {}

    def setFilterByColumn(self, regex, column):
        print(
            "SortFilterProxyModel: setFilterByColumn regex: {} column: {}".format(
                regex, column
            )
        )
        self.filters[column] = regex
        print("type(self.sourceModel())", type(self.sourceModel()))
        self.sourceModel().setStrColFilters(self.filters)
        # self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if True:  # now we using pdtablemodel.setStrColFilters above already
            return True

        print(
            "SortFilterProxyModel: filterAcceptsRow source_row: {} source_parent: {}".format(
                source_row, source_parent
            )
        )
        for key, regex in self.filters.items():
            ix = self.sourceModel().index(source_row, key, source_parent)
            if ix.isValid():
                if regex.indexIn(str(self.sourceModel().dataString(ix))) == -1:
                    return False

        if self.filterFromMenu:
            for key, regexlist in self.filterFromMenu.items():
                ix = self.sourceModel().index(source_row, key, source_parent)
                if ix.isValid():
                    if str(self.sourceModel().dataString(ix)) not in regexlist:
                        return False

        return True


class FilterHeader(QHeaderView):
    filterActivated = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(QtCore.Qt.Horizontal, parent)
        self._editors = []
        self._padding = 4
        self.setStretchLastSection(True)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setResizeMode(QHeaderView.Interactive)
        # self.setResizeMode(QtGui.QHeaderView.Stretch)
        # self.setDefaultAlignment(
        #     QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.setSortIndicatorShown(True)
        self.sectionResized.connect(self.adjustPositions)
        parent.horizontalScrollBar().valueChanged.connect(self.adjustPositions)

    def setFilterBoxes(self, count, parent):
        while self._editors:
            editor = self._editors.pop()
            editor.deleteLater()
        for index in range(count):
            editor = QtGui.QLineEdit(self.parent())
            editor.setPlaceholderText("Filter")
            editor.textChanged.connect(
                lambda text, col=index: parent.proxyModel.setFilterByColumn(
                    QRegExp(text, Qt.CaseInsensitive, QRegExp.FixedString), col
                )
            )
            editor.textChanged.connect(self.adjustPositions)
            self._editors.append(editor)
        self._verticalWidth = parent.tableView.verticalHeader().sizeHint().width()
        self.adjustPositions()

    def sizeHint(self):
        size = super().sizeHint()
        if self._editors:
            height = self._editors[0].sizeHint().height()
            size.setHeight(size.height() + height + self._padding)
        return size

    def updateGeometries(self):
        if self._editors:
            height = self._editors[0].sizeHint().height()
            self.setViewportMargins(0, 0, 0, height + self._padding)
        else:
            self.setViewportMargins(0, 0, 0, 0)
        super().updateGeometries()
        self.adjustPositions()

    def adjustPositions(self, dummy=None):
        for index, editor in enumerate(self._editors):
            height = editor.sizeHint().height()
            editor.move(
                self.sectionPosition(index) - self.offset() + self._verticalWidth,
                height + (self._padding // 2),
            )
            editor.resize(self.sectionSize(index), height)

    def filterText(self, index):
        if 0 <= index < len(self._editors):
            return self._editors[index].text()
        return ""

    def setFilterText(self, index, text):
        if 0 <= index < len(self._editors):
            self._editors[index].setText(text)

    def clearFilters(self):
        for editor in self._editors:
            editor.clear()
