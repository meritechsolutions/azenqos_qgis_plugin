import datetime
import threading
import sys
import os
import pandas as pd

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


class TableWindow(QWidget):
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
        self.tableView.horizontalHeader().setSortIndicator(-1, Qt.AscendingOrder)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Init filter header
        self.filterHeader = FilterHeader(self.tableView)
        self.filterHeader.setSortIndicator(-1, Qt.AscendingOrder)
        self.tableView.doubleClicked.connect(self.showDetail)
        self.tableView.clicked.connect(self.updateSlider)
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
        self.specifyTablesHeader()

        # Attach header to table, create text filter
        self.tableView.setHorizontalHeader(self.filterHeader)
        self.tableView.verticalHeader().setFixedWidth(
            self.tableView.verticalHeader().sizeHint().width()
        )
        if self.tableHeader and len(self.tableHeader) > 0:
            self.filterHeader.setFilterBoxes(gc.maxColumns, self)

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.tableView)
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

    def updateTable(self):
        self.setTableModel(self.dataList)

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
                    dataList[customItem["row"]][customItem["column"]] = customItem["text"]
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

        if not self.rows:
            self.rows = self.tableModel.rowCount(self)
            self.fetchRows = self.rows

        if not self.columns:
            self.columns = self.tableModel.columnCount(self)
            self.fetchColumns = self.columns
        # self.tableView.resizeColumnsToContents()

    def setDataSet(self, data_set: list):
        self.dataList = data_set

    def setTableSize(self, sizelist: list):
        if sizelist:
            self.rowCount = sizelist[0]
            self.columnCount = sizelist[1]

    def specifyTablesHeader(self):
        if self.title is not None:
            # GSM
            if self.title == "GSM_Radio Parameters":
                self.tableHeader = ["Element", "Full", "Sub"]
                self.dataList = GsmDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getRadioParameters()
                # self.dataList = GsmDataQuery(None).getRadioParameters()
            elif self.title == "GSM_Serving + Neighbors":
                self.tableHeader = [
                    "Time",
                    "Cellname",
                    "LAC",
                    "BSIC",
                    "ARFCN",
                    "RxLev",
                    "C1",
                    "C2",
                    "C31",
                    "C32",
                ]
                self.dataList = GsmDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getServingAndNeighbors()
            elif self.title == "GSM_Current Channel":
                self.tableHeader = ["Element", "Value"]
                self.dataList = GsmDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getCurrentChannel()
            elif self.title == "GSM_C/I":
                self.tableHeader = ["Time", "ARFCN", "Value"]
                self.dataList = GsmDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getCSlashI()
            # TODO: find the way to find event counter
            # elif self.title == "GSM_Events Counter":
            #     self.tableHeader = ["Event", "MS1", "MS2", "MS3", "MS4"]

            # WCDMA
            if self.title == "WCDMA_Active + Monitored Sets":
                self.tableHeader = [
                    "Time",
                    "CellName",
                    "CellType",
                    "SC",
                    "Ec/Io",
                    "RSCP",
                    "Freq",
                    "Event",
                ]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getActiveMonitoredSets()
            elif self.title == "WCDMA_Radio Parameters":
                self.tableHeader = ["Element", "Value"]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getRadioParameters()
            elif self.title == "WCDMA_Active Set List":
                self.tableHeader = [
                    "Time",
                    "Freq",
                    "PSC",
                    "Cell Position",
                    "Cell TPC",
                    "Diversity",
                ]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getActiveSetList()
            elif self.title == "WCDMA_Monitored Set List":
                self.tableHeader = ["Time", "Freq", "PSC", "Cell Position", "Diversity"]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getMonitoredSetList()
            elif self.title == "WCDMA_BLER Summary":
                self.tableHeader = ["Element", "Value"]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getBlerSummary()
            elif self.title == "WCDMA_BLER / Transport Channel":
                self.tableHeader = ["Transport Channel", "Percent", "Err", "Rcvd"]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getBLER_TransportChannel()
            elif self.title == "WCDMA_Line Chart":
                self.tableHeader = ["Element", "Value", "MS", "Color"]
            elif self.title == "WCDMA_Bearers":
                self.tableHeader = [
                    "N Bearers",
                    "Bearers ID",
                    "Bearers Rate DL",
                    "Bearers Rate UL",
                ]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getBearers()
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
            elif self.title == "WCDMA_CM GSM Reports":
                self.tableHeader = ["Time", "", "Eq.", "Name", "Info."]

            elif self.title == "WCDMA_CM GSM Cells":
                self.tableHeader = ["Time", "ARFCN", "RxLev", "BSIC", "Measure"]
                self.dataList = WcdmaDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getCmGsmCells()
            elif self.title == "WCDMA_Pilot Analyzer":
                self.tableHeader = ["Element", "Value", "Cell Type", "Color"]

            # LTE
            elif self.title == "LTE_Radio Parameters":
                self.tableHeader = ["Element", "PCC", "SCC0", "SCC1"]
                self.dataList = LteDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getRadioParameters()
            elif self.title == "LTE_Serving + Neighbors":
                self.tableHeader = ["Time", "EARFCN", "Band", "PCI", "RSRP", "RSRQ"]
                self.dataList = LteDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getServingAndNeighbors()
            elif self.title == "LTE_PUCCH/PDSCH Parameters":
                self.tableHeader = ["Element", "Value"]
                self.dataList = LteDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getPucchPdschParameters()
            elif self.title == "LTE_LTE Line Chart":
                self.tableHeader = ["Element", "Value", "MS", "Color"]
            elif self.title == "LTE_LTE RLC":
                self.tableHeader = ["Element", "Value", "", "", ""]
                self.dataList = LteDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getRlc()
            elif self.title == "LTE_LTE VoLTE":
                self.tableHeader = ["Element", "Value"]
                self.dataList = LteDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getVolte()

                
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

            elif self.title == "Signaling_Layer 1 Messages":
                self.tableHeader = ["Time", "", "Eq.", "Name", "Info."]
                self.tablename = "events"
                self.dataList = SignalingDataQuery(
                    gc.azenqosDatabase, gc.currentDateTimeString
                ).getLayerOneMessages()
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
                self.setTableModel(self.dataList)
                self.tableViewCount = self.tableView.model().rowCount()

            # if self.tablename and self.tablename != "":
            #     global gc.tableList
            #     if not self.tablename in gc.tableList:
            #         gc.tableList.append(self.tablename)

    # def mousePressEvent(self, QMouseEvent):
    #     if QMouseEvent.button() == Qt.LeftButton:
    #         pass
    #     elif QMouseEvent.button() == Qt.RightButton:
    #         self.generateMenu

    def setHeader(self, headers):
        # self.tableHeader = headers
        self.customHeader = headers
        self.updateTable()
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

    def hilightRow(self, sampledate):
        # QgsMessageLog.logMessage('[-- Start hilight row --]', tag="Processing")
        # start_time = time.time()
        worker = None
        self.dateString = str(sampledate)
        # self.findCurrentRow()
        if (self.dataList is None) or self.title not in [
            "Signaling_Events",
            "Signaling_Layer 1 Messages",
            "Signaling_Layer 3 Messages",
        ]:
            worker = Worker(self.specifyTablesHeader())
        else:
            worker = Worker(self.findCurrentRow())

        if worker:
            gc.threadpool.start(worker)
        # elapse_time = time.time() - start_time
        # del worker
        # QgsMessageLog.logMessage('Hilight rows elapse time: {0} s.'.format(str(elapse_time)), tag="Processing")
        # QgsMessageLog.logMessage('[-- End hilight row --]', tag="Processing")

    def showDetail(self, item):
        parentWindow = self.parentWindow.parentWidget()
        '''if self.tablename == "signalling":
            item = item.sibling(item.row(), 4)'''
        cellContent = str(item.data())
        self.detailWidget = DetailWidget(parentWindow, cellContent)

    def updateSlider(self, item):
        cellContent = str(item.data())
        timeCell = None
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
        finally:
            if timeCell is not None:
                sliderValue = timeCell - gc.minTimeValue
                sliderValue = round(sliderValue, 3)
                gc.timeSlider.setValue(sliderValue)

    def findCurrentRow(self):
        
        if isinstance(self.dataList, pd.DataFrame):
            if self.dateString:
                df = self.dataList
                ts_query = """time <= '{}'""".format(self.dateString)
                print("ts_query:", ts_query)
                df = df.query(ts_query)
                #print('findcurrentrow filt df.index:', df.index)
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


class DetailWidget(QDialog):
    def __init__(self, parent, detailText):
        super().__init__(None)
        self.title = "Details"
        self.detailText = detailText
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.setWindowFlags(
            QtCore.Qt.Window
        )
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

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
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

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:            
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
                #print("data() index:index.row() {}, index.column() {} ret {}".format(index.row(), index.column(), ret))
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
                #print("datastring() index:index.row() {}, index.column() {}".format(index.row(), index.column(), ret))
                return ret
            else:
                return None
        except Exception as e:
            print("WARNING: pdtablemodel data() exception: ", e)
            return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            ret = str(self.df.columns[section])
            print("headerdata section: {} ret: {}".format(section, ret))
            return ret
        return QAbstractTableModel.headerData(self, section, orientation, role)
