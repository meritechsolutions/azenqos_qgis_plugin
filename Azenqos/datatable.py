import datetime
import shutil
import threading
import sys
import os
import pandas as pd
import sqlite3

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import pyqtgraph as pg
import numpy as np
import global_config as gc

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
from .globalutils import Utils
from .filter_header import *
from .gsm_query import GsmDataQuery
from .cdma_evdo_query import CdmaEvdoQuery
from .lte_query import LteDataQuery
from .nr_query import NrDataQuery
from .signalling_query import SignalingDataQuery
from .wcdma_query import WcdmaDataQuery
from .worker import Worker
from .customize_properties import *
import lte_query
import wcdma_query
import gsm_query
from .tsharkworker import TsharkDecodeWorker
import polqa_query
import pcap_window


class TableWindow(QWidget):
    signal_ui_thread_emit_model_datachanged = pyqtSignal()

    def __init__(self, parent, windowName):
        super().__init__(parent)
        self.title = windowName
        self.rows = 0
        self.columns = 0
        self.fetchRows = 0
        self.fetchColumns = 0
        self.tablename = ""
        self.tableHeader = None
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.dataList = []
        self.customData = []
        self.customHeader = []
        self.currentRow = 0
        self.dateString = ""
        self.tableViewCount = 0
        self.parentWindow = parent
        self.filterList = None
        self.filterMenu = None
        self.signal_ui_thread_emit_model_datachanged.connect(
            self.ui_thread_emit_model_datachanged
        )
        self.setupUi()
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.generateMenu)
        # self.properties_window = PropertiesWindow(
        #     self, gc.azenqosDatabase, self.dataList, self.tableHeader
        # )

    def setupUi(self):
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)

        # Init table
        self.tableView = QTableView(self)
        # self.tableView.setWordWrap(False)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Init filter header

        self.filterHeader = FilterHeader(self.tableView)
        if self.title in ["Signaling_Events", "Signaling_Layer 3 Messages"]:
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
            self.filterHeader.setFilterBoxes(gc.maxColumns, self)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setMargin(0)
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
        self.proxyModel.filterFromMenu[columnIndex] = checkedRegexList
        self.proxyModel.invalidateFilter()

    def ui_thread_emit_model_datachanged(self):
        print("ui_thread_emit_model_datachanged")
        # this func is supposed to be called as a slot by ui thread - triggered by signal from non-ui thread
        index_topleft = self.tableModel.index(0, 0)
        index_bottomright = self.tableModel.index(100, 100)
        # self.tableModel.dataChanged.emit(index_topleft, index_bottomright, [QtCore.Qt.DisplayRole])
        self.proxyModel.dataChanged.emit(
            index_topleft, index_bottomright, [QtCore.Qt.DisplayRole]
        )

    def updateTableModelData(self, data):
        # self.setTableModel(self.dataList)
        if self.tableModel is not None:
            print("updateTableModelData()")
            self.tableModel.setData(None, data)
            self.signal_ui_thread_emit_model_datachanged.emit()  # this func is called from the sync thread which is non-ui so setdata() above's emit of dataChanged signal wont have effect, emit this signal to trigger dataChanged emit from ui thread...

    def setTableModel(self, dataList):
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

    def setDataSet(self, data_set: list):
        self.dataList = data_set

    def setTableSize(self, sizelist: list):
        if sizelist:
            self.rowCount = sizelist[0]
            self.columnCount = sizelist[1]

    def refreshTableContents(self, create_table_model=False):
        with sqlite3.connect(gc.databasePath) as dbcon:
            if self.title is not None:
                # GSM
                if self.title == "GSM_Radio Parameters":
                    self.dataList = gsm_query.get_gsm_radio_params_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "GSM_Serving + Neighbors":
                    self.dataList = gsm_query.get_gsm_serv_and_neigh__df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "GSM_Current Channel":
                    self.tableHeader = ["Element", "Value"]
                    self.dataList = gsm_query.get_gsm_current_channel_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "GSM_C/I":
                    self.dataList = gsm_query.get_coi_df(
                        dbcon, gc.currentDateTimeString
                    )
                # TODO: find the way to find event counter
                # elif self.title == "GSM_Events Counter":
                #     self.tableHeader = ["Event", "MS1", "MS2", "MS3", "MS4"]

                # WCDMA
                if self.title == "WCDMA_Active + Monitored Sets":
                    self.dataList = wcdma_query.get_wcdma_acive_monitored_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "WCDMA_Radio Parameters":
                    self.dataList = wcdma_query.get_wcdma_radio_params_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "WCDMA_BLER Summary":
                    self.dataList = wcdma_query.get_bler_sum_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "WCDMA_Line Chart":
                    self.tableHeader = ["Element", "Value", "MS", "Color"]
                elif self.title == "WCDMA_Bearers":
                    self.dataList = wcdma_query.get_wcdma_bearers_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "WCDMA_Pilot Poluting Cells":
                    self.tableHeader = ["Time", "N Cells", "SC", "RSCP", "Ec/Io"]
                    self.dataList = WcdmaDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getPilotPolutingCells()
                elif self.title == "WCDMA_Active + Monitored Bar":
                    self.tableHeader = ["Cell Type", "Ec/Io", "RSCP"]
                    self.dataList = WcdmaDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getActiveMonitoredBar()
                elif self.title == "WCDMA_Pilot Analyzer":
                    self.tableHeader = ["Element", "Value", "Cell Type", "Color"]

                # LTE
                elif self.title == "LTE_Radio Parameters":
                    self.dataList = lte_query.get_lte_radio_params_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "LTE_Serving + Neighbors":
                    self.dataList = lte_query.get_lte_serv_and_neigh_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "LTE_PUCCH/PDSCH Parameters":
                    self.dataList = lte_query.get_lte_pucch_pdsch_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "LTE_Data":
                    self.dataList = lte_query.get_lte_data_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "LTE_LTE Line Chart":
                    self.tableHeader = ["Element", "Value", "MS", "Color"]
                elif self.title == "LTE_LTE RLC":
                    self.dataList = lte_query.get_lte_rlc_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "LTE_LTE VoLTE":
                    self.dataList = lte_query.get_volte_disp_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "LTE_LTE RRC/SIB States":
                    print("LTE_LTE RRC/SIB States gen datalist")
                    self.dataList = lte_query.get_lte_rrc_sib_states_df(
                        dbcon, gc.currentDateTimeString
                    )
                elif self.title == "5G NR_Radio Parameters":
                    self.dataList = NrDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getRadioParameters()
                elif self.title == "5G NR_Serving + Neighbors":
                    self.dataList = NrDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getServingAndNeighbors()

                # CDMA/EVDO
                elif self.title == "CDMA/EVDO_Radio Parameters":
                    self.tableHeader = ["Element", "Value"]
                    self.dataList = CdmaEvdoQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getRadioParameters()
                elif self.title == "CDMA/EVDO_Serving + Neighbors":
                    self.tableHeader = ["Time", "PN", "Ec/Io", "Type"]
                    self.dataList = CdmaEvdoQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getServingAndNeighbors()
                elif self.title == "CDMA/EVDO_EVDO Parameters":
                    self.tableHeader = ["Element", "Value"]
                    self.dataList = CdmaEvdoQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getEvdoParameters()
            
                # PCAP
                elif self.title == "PCAP_PCAP List":
                    # self.dataList = lte_query.get_volte_disp_df(
                    #     dbcon, gc.currentDateTimeString
                    # )
                    self.dataList = pcap_window.get_all_pcap_content(gc.logPath)
                # Data
                elif self.title == "Data_GSM Data Line Chart":
                    self.tableHeader = ["Element", "Value", "MS", "Color"]
                elif self.title == "Data_WCDMA Data Line Chart":
                    self.tableHeader = ["Element", "Value", "MS", "Color"]
                elif self.title == "Data_GPRS/EDGE Information":
                    self.tableHeader = ["Element", "Value"]
                elif self.title == "Data_Web Browser":
                    self.tableHeader = ["Type", "Object"]
                    self.windowHeader = ["ID", "URL", "Type", "State", "Size(%)"]
                elif self.title == "Data_HSDPA/HSPA + Statistics":
                    self.tableHeader = ["Element", "Value"]
                elif self.title == "Data_HSUPA Statistics":
                    self.tableHeader = ["Element", "Value"]
                elif self.title == "Data_LTE Data Statistics":
                    self.tableHeader = ["Element", "Value", "", ""]
                elif self.title == "Data_LTE Data Line Chart":
                    self.tableHeader = ["Element", "Value", "MS", "Color"]
                elif self.title == "Data_Wifi Connected AP":
                    self.tableHeader = ["Element", "Value"]
                elif self.title == "Data_Wifi Scanned APs":
                    self.tableHeader = [
                        "Time",
                        "BSSID",
                        "SSID",
                        "Freq",
                        "Ch.",
                        "Level",
                        "Encryption",
                    ]
                elif self.title == "Data_Wifi Graph":
                    return False
                elif self.title == "Data_5G NR Data Line Chart":
                    self.tableHeader = ["Element", "Value", "MS", "Color"]

                # Signaling
                elif self.title == "Signaling_Events":
                    self.tableHeader = ["Time", "", "Eq.", "Name", "Info."]
                    self.tablename = "events"
                    self.dataList = SignalingDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getEvents()
                elif self.title == "Signaling_Layer 3 Messages":
                    self.tableHeader = ["Time", "", "Eq.", "Protocol", "Name", "Detail"]
                    self.tablename = "signalling"
                    self.dataList = SignalingDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getLayerThreeMessages()
                elif self.title == "Signaling_Benchmark":
                    self.tableHeader = ["", "MS1", "MS2", "MS3", "MS4"]
                    # self.tablename = 'signalling'
                    self.dataList = SignalingDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getBenchmark()
                elif self.title == "Signaling_MM Reg States":
                    self.tableHeader = ["Element", "Value"]
                    self.tablename = "mm_state"
                    self.dataList = SignalingDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getMmRegStates()
                elif self.title == "Signaling_Serving System Info":
                    self.tableHeader = ["Element", "Value"]
                    self.tablename = "serving_system"
                    self.dataList = SignalingDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getServingSystemInfo()
                elif self.title == "Signaling_Debug Android/Event":
                    self.tableHeader = ["Element", "Value"]
                    # self.tablename = 'serving_system'
                    self.dataList = SignalingDataQuery(
                        gc.azenqosDatabase, gc.currentDateTimeString
                    ).getDebugAndroidEvent()

                if self.dataList is not None:
                    if create_table_model:
                        self.setTableModel(self.dataList)
                    else:
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

        # QgsMessageLog.logMessage('[-- Start hilight row --]', tag="Processing")
        # start_time = time.time()
        worker = None
        self.dateString = str(sampledate)
        # self.findCurrentRow()
        if (self.dataList is None) or self.title not in [
            "Signaling_Events",
            "Signaling_Layer 3 Messages",
        ]:
            print(
                "datatable: threading: {} self.title: {} hilightRow: refreshTableContents()".format(
                    threading, self.title
                )
            )
            if threading:
                worker = Worker(self.refreshTableContents)
            else:
                self.refreshTableContents()
        else:
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
            gc.threadpool.start(worker)
        # elapse_time = time.time() - start_time
        # del worker
        # QgsMessageLog.logMessage('Hilight rows elapse time: {0} s.'.format(str(elapse_time)), tag="Processing")
        # QgsMessageLog.logMessage('[-- End hilight row --]', tag="Processing")

    def showDetail(self, item):
        parentWindow = self.parentWindow.parentWidget()
        cellContent = str(item.data())
        if self.tablename == "signalling":
            name = item.sibling(item.row(), 1).data()
            side = item.sibling(item.row(), 2).data()
            protocol = item.sibling(item.row(), 3).data()
            cellContent = item.sibling(item.row(), 4).data()
            self.detailWidget = DetailWidget(
                parentWindow, cellContent, name, side, protocol
            )
        else:
            if self.tablename == "events":
                time = item.sibling(item.row(), 0).data()
                name = item.sibling(item.row(), 1).data()
                info = item.sibling(item.row(), 2).data()
                self.detailWidget = DetailWidget(parentWindow, info, name, time)
            else:
                self.detailWidget = DetailWidget(parentWindow, cellContent)

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
                    sliderValue = timeCell - gc.minTimeValue
                    sliderValue = round(sliderValue, 3)
                    gc.timeSlider.setValue(sliderValue)
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: updateSlider timecell exception:", exstr)

    def findCurrentRow(self):

        if isinstance(self.dataList, pd.DataFrame):
            if self.dateString:
                df = self.dataList
                ts_query = """time <= '{}'""".format(self.dateString)
                print("ts_query:", ts_query)
                df = df.query(ts_query)
                # print('findcurrentrow filt df.index:', df.index)
                if len(df):
                    self.tableView.selectRow(df.index[-1])
                return

        startRange = 0
        indexList = []
        timeDiffList = []

        if self.currentRow and gc.isSliderPlay == True:
            startRange = self.currentRow

        for row in range(0, self.tableViewCount):
            index = self.tableView.model().index(row, 0)
            value = self.tableView.model().data(index)
            if Utils().datetimeStringtoTimestamp(value):
                gc.currentTimestamp = datetime.datetime.strptime(
                    self.dateString, "%Y-%m-%d %H:%M:%S.%f"
                ).timestamp()
                timestamp = datetime.datetime.strptime(
                    value, "%Y-%m-%d %H:%M:%S.%f"
                ).timestamp()
                if timestamp <= gc.currentTimestamp:
                    indexList.append(row)
                    timeDiffList.append(abs(gc.currentTimestamp - timestamp))

        if not len(timeDiffList) == 0:
            if indexList[timeDiffList.index(min(timeDiffList))] < self.tableViewCount:
                currentTimeindex = indexList[timeDiffList.index(min(timeDiffList))]
                self.tableView.selectRow(currentTimeindex)
        else:
            currentTimeindex = 0
            self.tableView.selectRow(currentTimeindex)
        self.currentRow = currentTimeindex

    def closeEvent(self, QCloseEvent):
        indices = [i for i, x in enumerate(gc.openedWindows) if x == self]
        for index in indices:
            gc.openedWindows.pop(index)
        # if self.tablename and self.tablename in gc.tableList:
        #     gc.tableList.remove(self.tablename)
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
        rowCount = self.model.rowCount()
        for x in range(rowCount):
            if state == 2:
                self.model.item(x, 0).setCheckState(Qt.Checked)
            else:
                self.model.item(x, 0).setCheckState(Qt.Unchecked)

    def search(self, text):
        # self.proxyModel.setFilterRegExp(text)
        print(text)

    def setFilter(self):
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
        indices = [i for i, x in enumerate(gc.openedWindows) if x == self]
        for index in indices:
            gc.openedWindows.pop(index)
        self.close()
        del self


class DetailWidget(QDialog):
    closed = False

    def __init__(self, parent, detailText, messageName=None, side=None, protocol=None):
        super().__init__(None)
        self.title = "Details"
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
        if messageName == "MOS Score":
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
        self.resize(self.width, self.height)
        self.show()
        self.raise_()
        self.activateWindow()
        if (
            None not in [self.messageName, self.side, self.protocol]
            and "msg_raw_hex:" in self.detailText
        ):
            print("Need to decode")
            worker = TsharkDecodeWorker(
                self.messageName, self.side, self.protocol, self.detailText
            )
            worker.signals.result.connect(self.setDecodedDetail)
            gc.threadpool.start(worker)
        # messageName is not None and side is not None and protocol is not None :

    def closeEvent(self, QCloseEvent):
        indices = [i for i, x in enumerate(gc.openedWindows) if x == self]
        for index in indices:
            gc.openedWindows.pop(index)
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
        self.getPolqa()
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

    def getPolqa(self):
        print("get polqa data")
        if self.messageName:
            polqaDict = polqa_query.PolqaQuery(
                gc.azenqosDatabase, self.side, self.detailText
            ).getPolqa()
            if polqaDict:
                self.textEdit.setPlainText(polqaDict["output_text"])
                from PyQt5 import QtMultimedia
                self.polqaWavFile = QtMultimedia.QSound(
                    gc.logPath + "/" + polqaDict["wave_file"]
                )


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
        QAbstractTableModel.__init__(self, parent, *args)
        self.df = df

    def rowCount(self, parent):
        return len(self.df)

    def columnCount(self, parent):
        return len(self.df.columns)

    # override
    def setData(self, index, data, role=QtCore.Qt.DisplayRole):
        if isinstance(data, pd.DataFrame):
            self.df = data
            index_topleft = self.index(0, 0)
            index_bottomright = self.index(100, 100)
            self.dataChanged.emit(
                index_topleft, index_bottomright, [QtCore.Qt.DisplayRole]
            )  # this wont have an effect if called from non-ui thread hence we use signal_ui_thread_emit_model_datachanged...
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
