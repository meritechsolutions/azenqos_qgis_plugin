import datetime
import shutil
import threading
import sys
import traceback
import os
import pandas as pd
import sqlite3
import azq_server_api

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import pyqtgraph as pg
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *
try:
    from qgis.core import *
    from qgis.utils import *
    from qgis.gui import *
except:
    pass
from globalutils import Utils
try:
    from filter_header import *
except:
    pass
from worker import Worker
from customize_properties import *
import lte_query
import wcdma_query
import gsm_query
from tsharkworker import TsharkDecodeWorker
import polqa_query
import pcap_window
import azq_utils
import qt_utils
import qgis_layers_gen


class TableWindow(QWidget):
    signal_ui_thread_emit_model_datachanged = pyqtSignal()
    signal_ui_thread_setup_ui = pyqtSignal()  # use with skip_setup_ui in ctor

    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)    

    def __init__(self, parent, title, refresh_data_from_dbcon_and_time_func=None, tableHeader=None, custom_df=None, time_list_mode=False, l3_alt_wireshark_decode=False, event_mos_score=False, gc=None, skip_setup_ui=False):
        super().__init__(parent)
        self.time_list_mode = time_list_mode  # True for windows like signalling, events where it shows data as a time list
        self.l3_alt_wireshark_decode = l3_alt_wireshark_decode  # If True then detailwidget will try decode detail_hex into alternative wireshark l3 decode
        self.event_mos_score = event_mos_score
        self.tableModel = None
        self.skip_setup_ui = skip_setup_ui

        try:
            self.gc = parent.gc
        except:
            self.gc = gc
        assert self.gc is not None

        
        self.title = title
        self.refresh_data_from_dbcon_and_time_func = refresh_data_from_dbcon_and_time_func
        self.custom_df = custom_df
        self.tableHeader = tableHeader
        self.rows = 0
        self.columns = 0
        self.fetchRows = 0
        self.fetchColumns = 0
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.dataList = []
        self.df = None  # if pandas mode this will be set
        self.df_str = None  # if pandas mode this will be set - for easy string filter/search
        self.customData = []
        self.customHeader = []
        self.currentRow = 0
        self.dateString = ""
        self.tableViewCount = 0
        self.parentWindow = parent
        self.filterList = None
        self.filterMenu = None
        self.signal_ui_thread_emit_model_datachanged.connect(
            self.ui_thread_model_datachanged
        )
        self.signal_ui_thread_setup_ui.connect(
            self.ui_thread_sutup_ui
        )
        self.prev_layout = None
        if not skip_setup_ui:
            self.setupUi()
        else:
            self.setupUiDry()
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.generateMenu)
        # self.properties_window = PropertiesWindow(
        #     self, self.gc.azenqosDatabase, self.dataList, self.tableHeader
        # )

    def setupUiDry(self):
        print("tablewindow setupuidry()")
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.resize(self.width, self.height)


    def setupUi(self):
        print("tablewindow setupui()")
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Init table
        self.tableView = QTableView(self)
        # self.tableView.setWordWrap(False)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Init filter header

        self.filterHeader = FilterHeader(self.tableView)
        """
        if self.title in ["Signaling_Events", "Signaling_Layer 3 Messages"]:
            self.filterHeader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.filterHeader.customContextMenuRequested.connect(self.headerMenu)
        """
        self.filterHeader.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.filterHeader.customContextMenuRequested.connect(self.headerMenu)

            # self.filterHeader.section.connect(self.horizontalHeader_sectionClicked)

        self.filterHeader.setSortIndicator(-1, Qt.AscendingOrder)

        self.tableView.doubleClicked.connect(self.showDetail)
        # self.tableView.clicked.connect(self.updateSlider)  - now we use onselectionchanged from modelview instead
        self.tableView.setSortingEnabled(False)
        self.tableView.setCornerButtonEnabled(False)
        self.tableView.setStyleSheet(
            """
            * {
            font-size: 11px;
            }
            QTableCornerButton::section{border-width: 0px; border-color: #BABABA; border-style:solid;}
            """
        )
        self.refreshTableContents(create_table_model=True)

        # Attach header to table, create text filter
        self.tableView.setHorizontalHeader(self.filterHeader)

        """
        self.tableView.verticalHeader().setFixedWidth(
            self.tableView.verticalHeader().sizeHint().width()
        )"""
        if self.tableHeader and len(self.tableHeader) > 0:
            self.filterHeader.setFilterBoxes(self.gc.maxColumns, self)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        # layout.setMargin(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tableView)

        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.tableView.horizontalHeader().setMinimumSectionSize(40)
        self.tableView.horizontalHeader().setDefaultSectionSize(60)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # self.tableView.verticalHeader().setMinimumSectionSize(12)
        self.tableView.verticalHeader().setDefaultSectionSize(14)

        # flayout = QFormLayout()
        # layout.addLayout(flayout)
        # for i in range(len(self.tableHeader)):
        #     headerText = self.tableHeader[i]
        #     if headerText:
        #         le = QLineEdit(self)
        #         flayout.addRow("Filter: {}".format(headerText), le)
        #         le.textChanged.connect(lambda text, col=i:
        #                             self.proxyModel.setFilterByColumn(QRegExp(text, Qt.CaseInsensitive, QRegExp.FixedString),
        #                                                     col))
        # self.setFixedWidth(layout.sizeHint())
        self.setLayout(layout)
        self.show()

        
    def contextMenuEvent(self, event):
        if not self.time_list_mode:
            return
        menu = QMenu(self)
        create_qgis_layer_action = menu.addAction("Create QGIS Map layer...")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == create_qgis_layer_action:
            if self.gc.qgis_iface is None:
                qt_utils.msgbox("Not running in QGIS-plugin mode...")
                return
            if self.tableModel is None:
                qt_utils.msgbox("No data/log loaded yet...")
                return
            if not len(self.tableModel.df):
                qt_utils.msgbox("This table is empty - no rows to use...")
                return
            layer_name = qt_utils.ask_text(self, "New layer", "Please specify layer name:")
            if layer_name:
                with sqlite3.connect(self.gc.databasePath) as dbcon:
                    # load it into qgis as new layer
                    qgis_layers_gen.create_qgis_layer_df(self.tableModel.df, dbcon, layer_name=layer_name)

    
    def headerMenu(self, pos):
        globalPos = self.mapToGlobal(pos)
        menu = QMenu()
        menu.addAction("Filter menu")
        selectedItem = menu.exec_(globalPos)
        if selectedItem:
            self.horizontalHeader_sectionClicked()

    def horizontalHeader_sectionClicked(self):
        if not self.filterMenu:
            self.filterMenu = FilterMenuWidget(self, 1)
        self.filterMenu.show()

        # posY = headerPos.y() + self.horizontalHeader.height()
        # posX = headerPos.x() + self.horizontalHeader.sectionPosition(index)
        # self.menu.exec_(QtCore.QPoint(posX, posY))

    def setFilterListModel(self, columnIndex, checkedRegexList):
        print("setFilterListModel: columnIndex {}, checkedRegexList {}".format())
        self.proxyModel.filterFromMenu[columnIndex] = checkedRegexList
        self.proxyModel.invalidateFilter()

        
    def ui_thread_model_datachanged(self):
        print("ui_thread_model_datachanged")
        # this func is supposed to be called as a slot by ui thread - triggered by signal from non-ui thread
        index_topleft = self.tableModel.index(0, 0)
        index_bottomright = self.tableModel.index(100, 100)
        # self.tableModel.dataChanged.emit(index_topleft, index_bottomright, [QtCore.Qt.DisplayRole])
        self.proxyModel.dataChanged.emit(
            index_topleft, index_bottomright, [QtCore.Qt.DisplayRole]
        )


    def setup_ui_with_custom_df(self, custom_df):
        self.custom_df = custom_df
        if self.time_list_mode:
            self.tableHeader = custom_df.columns.values.tolist()
        self.signal_ui_thread_setup_ui.emit()

        
    """
    for trigger like window.signal_ui_thread_setup_ui.emit() when skip_setup_ui flagged in ctor
    """
    def ui_thread_sutup_ui(self):
        print("ui_thread_sutup_ui")
        self.setupUi()
        

    def updateTableModelData(self, data):
        if self.tableModel is None:            
             self.setTableModel(data)
        if self.tableModel is not None:
            print("updateTableModelData()")
            self.tableModel.setData(None, data)
            self.signal_ui_thread_emit_model_datachanged.emit()  # this func is called from the sync thread which is non-ui so setdata() above's emit of dataChanged signal wont have effect, emit this signal to trigger dataChanged emit from ui thread...

    def setTableModel(self, dataList):
        print("setTableModel() dataList len: {}".format(len(dataList)))
        if isinstance(dataList, list):
            if self.rows and self.columns:

                if len(dataList) >= self.rows:
                    if self.rows < self.fetchRows:
                        self.fetchRows = self.rows

                    dataList = dataList[: self.fetchRows]

                while len(dataList) < self.rows:
                    dataList.append([])

                for dataRow in dataList:
                    if len(dataRow) >= self.columns:
                        if self.columns < self.fetchColumns:
                            self.fetchColumns = self.columns
                        dataRow = dataRow[: self.fetchColumns]
                    while len(dataRow) < self.columns:
                        dataRow.append("")

                if len(self.tableHeader) >= self.columns:
                    self.tableHeader = self.tableHeader[: self.columns]
                else:
                    while len(self.tableHeader) < self.columns:
                        self.tableHeader.append("")
                    # self.filterHeader.setFilterBoxes(len(self.tableHeader), self)

            for customItem in self.customData:
                try:
                    dataList[customItem["row"]][customItem["column"]] = customItem[
                        "text"
                    ]
                except:
                    self.customData.remove(customItem)

        if self.customHeader:
            self.tableHeader = self.customHeader

        self.dataList = dataList
        if isinstance(dataList, pd.DataFrame):
            self.set_pd_df(dataList)
            self.tableModel = PdTableModel(dataList, self)
        else:
            self.tableModel = TableModel(dataList, self.tableHeader, self)
        self.proxyModel = SortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.tableModel)
        self.tableView.setModel(self.proxyModel)
        self.tableView.setSortingEnabled(False)

        sm = self.tableView.selectionModel()
        if sm is not None:
            sm.selectionChanged.connect(self.updateSlider)

        if not self.rows:
            self.rows = self.tableModel.rowCount(self)
            self.fetchRows = self.rows

        if not self.columns:
            self.columns = self.tableModel.columnCount(self)
            self.fetchColumns = self.columns
            # print("resizeColumnsToContents()")
            # self.tableView.resizeColumnsToContents()

    
    def set_pd_df(self, dataList):
        self.dataList = dataList
        if isinstance(dataList, pd.DataFrame):
            self.df = dataList
            self.df_str = self.df.astype(str)
        else:
            self.df = None
            self.df_str = None
        
    def setDataSet(self, data_set: list):
        self.dataList = data_set

    def setTableSize(self, sizelist: list):
        if sizelist:
            self.rowCount = sizelist[0]
            self.columnCount = sizelist[1]


    def refreshTableContents(self, create_table_model=False):
        print("datatable refreshTableContents()")
        
        if self.custom_df is not None:
            print("datatable refreshTableContents() custom_df")
            self.set_pd_df(self.custom_df)
        elif self.gc.databasePath is not None and self.refresh_data_from_dbcon_and_time_func is not None:
            try:
                with sqlite3.connect(self.gc.databasePath) as dbcon:
                    print("datatable refreshTableContents() refresh_data_from_dbcon_and_time_func")
                    self.set_pd_df(self.refresh_data_from_dbcon_and_time_func(dbcon, self.gc.currentDateTimeString))
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: datatable title {} refreshTableContents() failed exception: {}".format(self.title, exstr))
                self.set_pd_df(pd.DataFrame({"status", exstr}))
            
        if self.dataList is not None:
            if create_table_model:
                print("datatable refreshTableContents() settablemodel")
                self.setTableModel(self.dataList)
            else:
                print("datatable refreshTableContents() updatetablemodeldata")
                self.updateTableModelData(
                    self.dataList
                )  # applies new self.dataList
            self.tableViewCount = self.tableView.model().rowCount()



    def setHeader(self, headers):
        # self.tableHeader = headers
        self.customHeader = headers
        self.updateTableModelData(self.dataList)
        # self.filterHeader.setFilterBoxes(len(self.tableHeader), self)

    def generateMenu(self, pos):
        menu = QMenu()
        item1 = menu.addAction(u"Customize")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == item1:
            self.properties_window.tempCustom = self.customData
            self.properties_window.tempHeader = self.customHeader
            self.properties_window.data_set = self.dataList
            self.properties_window.headers = self.tableHeader
            self.properties_window.setupUi()
            self.properties_window.setupComboBox()
            self.properties_window.show()
            

    def hilightRow(self, sampledate, threading=False):
        print("hilightRow: sampledate: %s" % sampledate)
        # QgsMessageLog.logMessage('[-- Start hilight row --]', tag="Processing")
        # start_time = time.time()
        worker = None
        self.dateString = str(sampledate)
        if not self.time_list_mode:
            # table data mode like measurements of that time needs refresh
            if threading:
                worker = Worker(self.refreshTableContents)
            else:
                self.refreshTableContents()
        else:
            # time_list_mode needs findCurrentRow()
            print(
                "datatable: threading: {} self.title: {} hilightRow: findCurrentRow()".format(
                    threading, self.title
                )
            )
            if threading:
                worker = Worker(self.findCurrentRow)
            else:
                self.findCurrentRow()

        if threading and worker:
            self.gc.threadpool.start(worker)
            

    def showDetail(self, item):
        row_index = item.row()        
        print("showDetail row_index: %d" % row_index)
        row_sr = self.tableModel.df.iloc[row_index]
        #cellContent = str(item.data())
        cellContent = ""
        for index, val in row_sr.items():
            cellContent += "[{}]: {}\n".format(index, val)
        parentWindow = None
        if self.parentWindow:
            self.parentWindow.parentWidget()
        else:
            parentWindow = self
        if self.l3_alt_wireshark_decode:
            name = row_sr["name"]
            side = row_sr["dir"]
            protocol = row_sr["protocol"]
            self.detailWidget = DetailWidget(self.gc, parentWindow, cellContent, name, side, protocol)
        elif self.event_mos_score and row_sr["name"].find("MOS Score") != -1:
            name = row_sr["name"]
            side = {}
            side["wav_file"] = os.path.join(azq_utils.tmp_gen_path(),row_sr["wave_file"])
            side["text_file"] = os.path.join(azq_utils.tmp_gen_path(),row_sr["wave_file"].replace(".wav", "_polqa.txt"))
            self.detailWidget = DetailWidget(self.gc, parentWindow, cellContent, name, side)
        else:
            self.detailWidget = DetailWidget(self.gc, parentWindow, cellContent)
        """
        print("showdetail self.tablename {}".format(self.tablename))
        if self.tablename == "signalling":
            name = item.sibling(item.row(), 2).data()
            side = item.sibling(item.row(), 3).data()
            protocol = item.sibling(item.row(), 4).data()
            cellContent = item.sibling(item.row(), 5).data()
            self.detailWidget = DetailWidget(
                self.gc, parentWindow, cellContent, name, side, protocol
            )
        else:
            if self.tablename == "events":
                time = item.sibling(item.row(), 1).data()
                name = item.sibling(item.row(), 2).data()
                info = item.sibling(item.row(), 3).data()
                self.detailWidget = DetailWidget(self.gc, parentWindow, info, name, time)
            else:
                self.detailWidget = DetailWidget(self.gc, parentWindow, cellContent)
        """

    def updateSlider(self, item):

        # get selected row time for signalling and events table

        if not self.tableHeader:
            return

        if isinstance(item, QItemSelection):
            # onselectionchanged mode signal to this slot
            idx_list = item.indexes()
            for idx in idx_list:
                print(
                    "onselectionchanged mode signal to this slot: idx.row()", idx.row()
                )
                item = idx
                break

        timeCell = None
        try:
            cellContent = str(item.data())
            try:
                timeCell = datetime.datetime.strptime(
                    str(cellContent), "%Y-%m-%d %H:%M:%S.%f"
                ).timestamp()
            except Exception as e:
                # if current cell is not Time cell
                headers = [item.lower() for item in self.tableHeader]
                try:
                    columnIndex = headers.index("time")
                except Exception as e2:
                    columnIndex = -1
                if not columnIndex == -1:
                    timeItem = item.sibling(item.row(), columnIndex)
                    cellContent = str(timeItem.data())
                    timeCell = datetime.datetime.strptime(
                        str(cellContent), "%Y-%m-%d %H:%M:%S.%f"
                    ).timestamp()
                else:
                    timeCell = timeCell
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: updateSlider exception:", exstr)
        finally:
            if timeCell is not None:
                try:
                    sliderValue = timeCell - self.gc.minTimeValue
                    sliderValue = round(sliderValue, 3)
                    self.gc.timeSlider.setValue(sliderValue)
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: updateSlider timecell exception:", exstr)

    def findCurrentRow(self):
        if isinstance(self.dataList, pd.DataFrame):
            if self.dateString:
                df = self.tableModel.df  #self.dataList
                ts_query = """time <= '{}'""".format(self.dateString)
                print("ts_query:", ts_query)
                df = df.query(ts_query).reset_index()
                print('findcurrentrow after query df len: %d', len(df))
                if len(df):
                    self.currentRow = df.index[-1]
                    self.tableView.selectRow(self.currentRow)
                return
            

    def closeEvent(self, QCloseEvent):
        indices = [i for i, x in enumerate(self.gc.openedWindows) if x == self]
        for index in indices:
            self.gc.openedWindows.pop(index)
        self.close()
        del self


class FilterMenuWidget(QWidget):
    def __init__(self, parent, columnIndex):
        super().__init__()
        self.parent = parent
        self.columnIndex = columnIndex
        self.setupUi(self)
        self.setupFilterMenu()
        self.setupEvent()

    def setupUi(self, FilterMenuWidget):
        self.setObjectName("FilterMenuWidget")
        self.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(FilterMenuWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.searchBox = QLineEdit(FilterMenuWidget)
        self.searchBox.setFixedHeight(24)
        self.searchBox.setPlaceholderText("Search...")
        self.verticalLayout.addWidget(self.searchBox)

        self.treeView = QTreeView(FilterMenuWidget)
        self.verticalLayout.addWidget(self.treeView)

        self.selectAllCb = QCheckBox(FilterMenuWidget)
        self.selectAllCb.setText("Select All")
        self.selectAllCb.setChecked(True)
        self.verticalLayout.addWidget(self.selectAllCb)
        self.selectAllCb.stateChanged.connect(self.selectAll)

        self.buttonBox = QtWidgets.QDialogButtonBox(FilterMenuWidget)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.model = QStandardItemModel(self.treeView)
        self.model.setHorizontalHeaderLabels(["Name"])

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setFocus()

        # self.searchBox.textChanged.connect(self.completer.setCompletionPrefix)

    def retranslateUi(self):
        title = "Filter Menu (" + self.parent.title + ")"
        self.setWindowTitle(title)

    def setupEvent(self):
        self.searchBox.textChanged.connect(self.proxyModel.setFilterRegExp)
        self.buttonBox.accepted.connect(self.setFilter)
        self.buttonBox.rejected.connect(self.close)

    def setupFilterMenu(self):
        data_unique = []
        if self.model.rowCount() == 0:
            for i in range(self.parent.tableModel.rowCount(0)):
                # if not self.parent.tableView.isRowHidden(i):
                locateOfData = self.parent.tableModel.index(i, self.columnIndex)
                data = self.parent.tableModel.data(locateOfData)
                if data not in data_unique:
                    data_unique.append(data)

            for data in data_unique:
                item = QStandardItem(data)
                item.setCheckable(True)
                item.setCheckState(Qt.Checked)
                self.model.appendRow(item)

        self.proxyModel = QSortFilterProxyModel()
        self.proxyModel.setSourceModel(self.model)
        self.proxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxyModel.setFilterKeyColumn(0)
        self.treeView.setModel(self.proxyModel)
        self.treeView.setSortingEnabled(True)
        self.treeView.sortByColumn(0, Qt.AscendingOrder)

    def selectAll(self, state):
        print("filtermenuwidget: selectAll")
        rowCount = self.model.rowCount()
        for x in range(rowCount):
            if state == 2:
                self.model.item(x, 0).setCheckState(Qt.Checked)
            else:
                self.model.item(x, 0).setCheckState(Qt.Unchecked)

    def search(self, text):
        # self.proxyModel.setFilterRegExp(text)
        print("filtermenuwidget: search: text:",text)

    def setFilter(self):
        print("filtermenuwidget: setFilter")
        checkedRegexList = []
        self.model.sort(0, Qt.AscendingOrder)
        for i in range(self.model.rowCount()):
            if self.model.item(i, 0).checkState() == 2:
                text = self.model.data(self.model.index(i, 0))
                # regex = QRegExp(text, Qt.CaseInsensitive, QRegExp.FixedString)
                checkedRegexList.append(text)
        self.parent.setFilterListModel(self.columnIndex, checkedRegexList)
        self.close()

    def closeEvent(self, QCloseEvent):
        print("filtermenuwidget: closeEvent")
        indices = [i for i, x in enumerate(self.gc.openedWindows) if x == self]
        for index in indices:
            self.gc.openedWindows.pop(index)
        self.close()
        del self


class DetailWidget(QDialog):
    closed = False

    def __init__(self, gc, parent, detailText, messageName=None, side=None, protocol=None):
        super().__init__(None)
        self.title = "Details"
        self.gc = gc
        self.detailText = detailText
        self.messageName = messageName
        self.side = side
        self.protocol = protocol
        self.left = 10
        self.top = 10
        self.parent = parent
        self.width = 640
        self.height = 480
        self.setWindowFlags(QtCore.Qt.Window)
        self.polqaWavFile = None
        if self.messageName is not None and self.messageName.find("MOS Score") != -1:
            self.setUpPolqaMosScore()
        else:
            self.setupUi()

    def setupUi(self):
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.textEdit = QTextEdit()
        self.textEdit.setPlainText(self.detailText)
        self.textEdit.setReadOnly(True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)        
        self.show()
        self.raise_()
        self.activateWindow()
        if (
            None not in [self.messageName, self.side, self.protocol]
            and "msg_raw_hex:" in self.detailText
        ):
            print("Need to decode")
            worker = TsharkDecodeWorker(
                self.gc, self.messageName, self.side, self.protocol, self.detailText
            )
            worker.signals.result.connect(self.setDecodedDetail)
            self.gc.threadpool.start(worker)
        # messageName is not None and side is not None and protocol is not None :

    def closeEvent(self, QCloseEvent):
        indices = [i for i, x in enumerate(self.gc.openedWindows) if x == self]
        for index in indices:
            self.gc.openedWindows.pop(index)
        self.close()
        if self.polqaWavFile:
            self.polqaWavFile.stop()
        del self

    def setDecodedDetail(self, detail):
        if self.closed == False:
            self.textEdit.setPlainText(
                self.detailText
                + "\n\n------\nALTERNATIVE WIRESHARK DECODE OF SAME PACKET BELOW\n------\n"
                + str(detail)
            )

    def setUpPolqaMosScore(self):
        print("do setup polqa mos score")
        self.polqaWavFile = None
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)

        dirname = os.path.dirname(__file__)

        gridlayout = QGridLayout(self)
        self.playBtn = QPushButton(self)
        self.playBtn.setIcon(QIcon(QPixmap(os.path.join(dirname, "res", "play.png"))))
        self.playBtn.setText("Play sound")
        self.saveBtn = QPushButton(self)
        self.saveBtn.setIcon(
            QIcon(QPixmap(os.path.join(dirname, "res", "save_wav.png")))
        )
        self.saveBtn.setText("Save file")

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)

        gridlayout.addWidget(self.playBtn, 0, 0, 1, 2)
        gridlayout.addWidget(self.saveBtn, 0, 2, 1, 1)
        gridlayout.addWidget(self.textEdit, 1, 0, 1, 3)

        self.playBtn.clicked.connect(self.playWavFile)
        self.saveBtn.clicked.connect(self.saveWaveFile)

        self.setLayout(gridlayout)
        f = open(self.side["text_file"], "r")
        self.textEdit.setPlainText(self.detailText+'\n'+f.read())
        f.close()
        from PyQt5 import QtMultimedia
        self.polqaWavFile = QtMultimedia.QSound(self.side["wav_file"])
        self.resize(self.width, self.height)
        self.show()
        self.raise_()
        self.activateWindow()

    def saveWaveFile(self):
        wavfilepath = str(self.polqaWavFile.fileName())
        filename = QFileDialog.getSaveFileName(
            self, "Save file as ...", wavfilepath.replace(".wav", ""), ".wav"
        )
        if filename:
            if filename[0] and filename[1]:
                filepath = str(filename[0]) + str(filename[1])
                try:
                    shutil.copyfile(wavfilepath, filepath)
                except:
                    pass
            print("save wav file")

    def playWavFile(self):
        print("play wav file")
        if self.polqaWavFile:
            self.polqaWavFile.play()


class TableModel(QAbstractTableModel):
    def __init__(self, inputData, header, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.headerLabels = header
        self.dataSource = inputData
        # self.testColumnValue()

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

    # override
    def setData(self, index, data, role=QtCore.Qt.DisplayRole):
        if isinstance(data, list):
            self.dataSource = data
            index_topleft = self.index(0, 0)
            index_bottomright = self.index(100, 100)
            self.dataChanged.emit(
                index_topleft, index_bottomright, [role]
            )  # this wont have an effect if called from non-ui thread hence we use signal_ui_thread_emit_model_datachanged...
            return True
        return False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print("tablemodel data() role:", role)
        if role == QtCore.Qt.DisplayRole:
            # print("data() QtCore.Qt.DisplayRole")
            row = index.row()
            column = index.column()
            return "{}".format(self.dataSource[row][column])
        else:
            return None

    def dataString(self, index):
        return self.dataSource[index.row()][index.column()]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headerLabels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)


class PdTableModel(QAbstractTableModel):
    def __init__(self, df, parent=None, *args):
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        if "time" in df.columns:
            df["time"] = pd.to_datetime(df["time"])
        QAbstractTableModel.__init__(self, parent, *args)
        self.df_full = df
        self.df = df  # filtered data for display
        self.parent = parent

    def rowCount(self, parent):
        return len(self.df)

    def columnCount(self, parent):
        return len(self.df.columns)


    def setStrColFilters(self, filters):
        print("pdtablemodel setStrColFilters filteres START")
        self.df = self.df_full
        changed = True
        for col_index in filters.keys():
            col = self.df.columns[col_index]
            regex = filters[col_index].pattern()  # QRegExp
            if col and regex:
                print("setStrColFilters col: {} regex: {}".format(col, regex))
                self.df = self.df[self.df[col].astype(str).str.contains(regex, case=False)]
        if changed:
            """
            index_topleft = self.index(0, 0)
            index_bottomright = self.index(len(self.df), len(self.df.columns))
            self.dataChanged.emit(
                index_topleft, index_bottomright, [QtCore.Qt.DisplayRole]
            )  # this wont have an effect if called from non-ui thread hence we use signal_ui_thread_emit_model_datachanged...
            """
            self.parent.signal_ui_thread_emit_model_datachanged.emit()
            print("pdtablemodel setStrColFilters emit done")
        else:
            print("pdtablemodel setStrColFilters not changed")
            
        print("pdtablemodel setStrColFilters filteres DONE len(self.df_full) {} len(self.df) {}".format(len(self.df_full), len(self.df)))

    # override
    def setData(self, index, data, role=QtCore.Qt.DisplayRole):
        if isinstance(data, pd.DataFrame):
            self.df_full = data
            self.df = data
            """
            index_topleft = self.index(0, 0)
            index_bottomright = self.index(100, 100)
            self.dataChanged.emit(
                index_topleft, index_bottomright, [QtCore.Qt.DisplayRole]
            )  # this wont have an effect if called from non-ui thread hence we use signal_ui_thread_emit_model_datachanged...
            """
            self.parent.signal_ui_thread_emit_model_datachanged.emit()
            print("pdtablemodel setdata emit done")
            return True
        return False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print("pdtablemodel data() role:", role)
        if role == QtCore.Qt.DisplayRole:
            # print("pdtablemodel data() displayrole enter")
            try:
                ret = self.df.iloc[index.row(), index.column()]
                if pd.isnull(ret):
                    return None
                if not isinstance(ret, str):
                    if isinstance(ret, float):
                        ret = "%.02f" % ret
                    else:
                        ret = str(ret)
                if ret.endswith(".00"):
                    ret = ret[:-3]
                # print("data() index:index.row() {}, index.column() {} ret {}".format(index.row(), index.column(), ret))
                return ret
            except Exception as e:
                print("WARNING: pdtablemodel data() exception: ", e)
                return None
        else:
            return None

    def dataString(self, index):
        try:
            ret = self.df.iloc[index.row(), index.column()]
            if ret is not None:
                ret = str(ret)
                # print("datastring() index:index.row() {}, index.column() {}".format(index.row(), index.column(), ret))
                return ret
            else:
                return None
        except Exception as e:
            print("WARNING: pdtablemodel data() exception: ", e)
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            ret = str(self.df.columns[section])
            # print("headerdata section: {} ret: {}".format(section, ret))
            return ret
        return QAbstractTableModel.headerData(self, section, orientation, role)



def create_table_window_from_api_expression_ret(parent, title, gc, server, token, lhl, azq_report_gen_expression):
    window = TableWindow(parent, title, None, gc=gc, time_list_mode=True, skip_setup_ui=True)
    gen_thread = threading.Thread(
        target=run_api_expression_and_set_results_to_table_window,
                    args=(
                        window,
                        server, token, lhl, azq_report_gen_expression
                    )
    )
    gen_thread.start()
    return window


def run_api_expression_and_set_results_to_table_window(window, server, token, lhl, azq_report_gen_expression):
    try:
        ret_dict = azq_server_api.api_py_eval_get_parsed_ret_dict(server, token, lhl, azq_report_gen_expression, progress_update_signal=window.progress_update_signal, status_update_signal=window.status_update_signal, done_signal=None)
        #time.sleep(1)
        print("api call ret_dict: {}".format(ret_dict))
        df = azq_server_api.parse_py_eval_ret_dict_for_df(server, token, ret_dict)
        if df is None:
            df = pd.DataFrame(
                {
                    "result": [ret_dict["ret"]],
                }
            )
        window.setup_ui_with_custom_df(df)
    except Exception as ex:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: api_py_eval_and_wait_completion exception: {}", exstr)
        df = pd.DataFrame({'FAILED':[exstr]})
        window.setup_ui_with_custom_df(df)

