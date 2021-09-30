import contextlib
import csv
import os
import re
import shutil
import signal
import sqlite3
import sys
import threading
import traceback
import uuid

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c

import pandas as pd
import numpy as np

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QItemSelection,
    QSortFilterProxyModel,
    QAbstractTableModel,
)
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QStandardItemModel, QIcon, QPixmap, QStandardItem
from PyQt5.QtWidgets import (
    QWidget,
    QTableView,
    QAbstractItemView,
    QVBoxLayout,
    QMenu,
    QLineEdit,
    QTreeView,
    QCheckBox,
    QDialogButtonBox,
    QDialog,
    QTextEdit,
    QGridLayout,
    QPushButton,
    QFileDialog,
    QSizePolicy
)

import azq_server_api
# Adding folder path
import analyzer_vars

from filter_header import FilterHeader, SortFilterProxyModel
from worker import Worker

sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
from PyQt5 import QtCore
from tsharkworker import TsharkDecodeWorker
import azq_utils
import qt_utils
import qgis_layers_gen
import sql_utils
import preprocess_azm

SEARCH_PLACEHOLDER_TEXT = "Search regex: a|b means a or b"
DEFAULT_TABLE_WINDOW_OPTIONS_DICT_KEYS = (
    "time_list_mode",
    "list_module",
    "stretch_last_row",
)

class TableWindow(QWidget):
    signal_ui_thread_emit_model_datachanged = pyqtSignal()
    signal_ui_thread_emit_new_model = pyqtSignal()
    signal_ui_thread_setup_ui = pyqtSignal()  # use with skip_setup_ui in ctor
    signal_ui_thread_emit_select_row = pyqtSignal(int)

    progress_update_signal = pyqtSignal(int)
    status_update_signal = pyqtSignal(str)

    def __init__(
        self,
        parent,
        title,
        refresh_df_func_or_py_eval_str=None,
        tableHeader=None,
        custom_df=None,
        gc=None,
        skip_setup_ui=False,
        mdi=None,
        func_key=None,

        # these params will be written to options_dict
        time_list_mode=False,
        list_module=False,
        stretch_last_row=False,
        options=None,
    ):
        super().__init__(parent)
        if options is None:
            options = {}
        self.tableModel = None
        self.skip_setup_ui = skip_setup_ui
        self.mdi = mdi
        self.func_key = func_key

        ################ support old params not put in options dict
        print("options0:", options)
        if time_list_mode:
            options["time_list_mode"] = time_list_mode
        print("options1:", options)
        if list_module:
            options["list_module"] = list_module
        if stretch_last_row:
            options["stretch_last_row"] = stretch_last_row
        print("options2:", options)
        for key in DEFAULT_TABLE_WINDOW_OPTIONS_DICT_KEYS:
            if key not in options.keys():
                options[key] = False
        print("options3:", options)
        self.time_list_mode = options["time_list_mode"]  # True for windows like signalling, events where it shows data as a time list
        self.list_module = options["list_module"]
        self.stretch_last_row = options["stretch_last_row"]
        self.options = options
        ################

        # self.settings.setValue("func_key",self.func_key)
        self.selected_row_time = None
        self.selected_row_time_string = None
        self.selected_row_log_hash = None

        try:
            self.gc = parent.gc
        except:
            self.gc = gc
        assert self.gc is not None

        self.title = title
        self.refresh_data_from_dbcon_and_time_func = refresh_df_func_or_py_eval_str

        print("datatable.tablewindow title: {} time_list_mode: {} self.time_list_mode: {} options: {}".format(self.title, time_list_mode, self.time_list_mode,  self.options))

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
        self.df_str = (
            None  # if pandas mode this will be set - for easy string filter/search
        )
        self.customData = []
        self.customHeader = []
        self.currentRow = 0
        self.find_row_time_string = ""
        self.find_row_log_hash = None
        self.tableViewCount = 0
        self.parentWindow = parent
        self.parent = parent
        self.filterList = None
        self.filterMenu = None
        self.signal_ui_thread_emit_model_datachanged.connect(
            self.ui_thread_model_datachanged
        )
        self.signal_ui_thread_emit_new_model.connect(
            self.ui_thread_new_model
        )
        self.signal_ui_thread_setup_ui.connect(self.ui_thread_sutup_ui)
        self.ui_thread_selecting_row_dont_trigger_timechanged = False
        self.signal_ui_thread_emit_select_row.connect(
            self.ui_thread_emit_select_row
        )
        self.prev_layout = None
        if not skip_setup_ui:
            self.setupUi()
        else:
            self.setupUiDry()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.generateMenu)
        # self.properties_window = PropertiesWindow(
        #     self, self.gc.azenqosDatabase, self.dataList, self.tableHeader
        # )

    def ui_thread_emit_select_row(self, row):
        print("ui_thread_emit_select_row: {} start".format(row))
        try:
            self.ui_thread_selecting_row_dont_trigger_timechanged = True
            self.tableView.selectRow(self.currentRow)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: ui_thread_emit_select_row() title {} exception: {}".format(
                    self.title,
                    exstr
                )
            )
        finally:
            self.ui_thread_selecting_row_dont_trigger_timechanged = False
        print("ui_thread_emit_select_row: {} done".format(row))


    def setupUiDry(self):
        print("tablewindow setupuidry()")
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setMinimumSize(self.width, self.height)
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
        self.refreshTableContents()

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
        #self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # self.tableView.verticalHeader().setMinimumSectionSize(12)
        self.tableView.verticalHeader().setDefaultSectionSize(14)
        self.tableView.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.verticalHeader().setStretchLastSection(self.stretch_last_row)
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
        menu = QMenu(self)
        actions_dict = {"create_qgis_layer": None, "custom_expression": None, "to_csv": None, "to_parquet": None}
        if self.time_list_mode and self.df is not None and 'log_hash' in self.df.columns and 'time' in self.df.columns:
            actions_dict["create_qgis_layer"] = menu.addAction("Create QGIS Map layer...")
        if isinstance(self.refresh_data_from_dbcon_and_time_func, (str, list, dict)):
            actions_dict["custom_expression"] = menu.addAction("Customize SQL/Python expression...")
        if self.tableModel.df is not None:
            actions_dict["to_csv"] = menu.addAction("Dump to CSV...")
            actions_dict["to_parquet"] = menu.addAction("Dump to Parquet...")
        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action is None:
            return
        if action == actions_dict["custom_expression"]:
            expression = azq_utils.ask_custom_sql_or_py_expression(self, table_view_mode=self.time_list_mode, existing_content=self.refresh_data_from_dbcon_and_time_func)
            if expression:
                self.refresh_data_from_dbcon_and_time_func = expression
                self.refreshTableContents()
        elif action == actions_dict["to_csv"] or action == actions_dict["to_parquet"]:
            df = self.tableModel.df
            try:
                if len(df) and "log_hash" in df.columns and "time" in df.columns:
                    if ("lat" not in df.columns) or ("lon" not in df.columns):
                        print("need to merge lat and lon")
                        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                            df = preprocess_azm.merge_lat_lon_into_df(dbcon, df).rename(
                                columns={"positioning_lat": "lat", "positioning_lon": "lon"}
                            )
                fp, _ = QFileDialog.getSaveFileName(
                    self, "Select dump file/location", QtCore.QDir.rootPath(), "*.csv" if action == actions_dict["to_csv"] else "*.parquet"
                )
                if fp:
                    if action == actions_dict["to_csv"]:
                        df.to_csv(fp, index=False, quoting=csv.QUOTE_ALL)
                    else:
                        df.to_parquet(fp)
                    qt_utils.msgbox("Dumped to file: {}".format(fp))
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print(
                    "WARNING: datatable title {} dump table to file contextmenu exception: {}".format(
                        self.title, exstr
                    )
                )
                qt_utils.msgbox("dump failed: " + exstr, title="Failed")

        elif action == actions_dict["create_qgis_layer"]:
            if self.gc.qgis_iface is None:
                qt_utils.msgbox("Not running in QGIS-plugin mode...")
                return
            if self.tableModel is None:
                qt_utils.msgbox("No data/log loaded yet...")
                return
            if not len(self.tableModel.df):
                qt_utils.msgbox("This table is empty - no rows to use...")
                return
            if self.tableModel.df is None or (
                (
                    "log_hash" not in self.tableModel.df.columns
                    or "time" not in self.tableModel.df.columns
                ) and
                (
                        "lat" not in self.tableModel.df.columns
                        or "lon" not in self.tableModel.df.columns
                )
            ):
                qt_utils.msgbox(
                    "This table doesn't contain 'lat' and 'lon' columns, and alson doesn't contain the required columns to auto match/add lat/lon from logs: 'log_hash' and 'time'"
                )
            else:
                layer_name = qt_utils.ask_text(
                    self, "New layer", "Please specify layer name:"
                )
                if layer_name:
                    # load it into qgis as new layer
                    try:
                        tmpdbfp = self.gc.databasePath
                        tmpdbfp +=  "_{}.db".format(uuid.uuid4())

                        df = self.tableModel.df
                        if ("lat" not in df.columns) or ("lon" not in df.columns):
                            print("need to merge lat and lon")
                            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                                df = preprocess_azm.merge_lat_lon_into_df(dbcon, df).rename(
columns={"positioning_lat": "lat", "positioning_lon": "lon"}
                            )
                        qgis_layers_gen.dump_df_to_spatialite_db(
                        df, tmpdbfp, layer_name, is_indoor=self.gc.is_indoor
                        )
                        assert os.path.isfile(tmpdbfp)
                        qgis_layers_gen.create_qgis_layer_from_spatialite_db(
                            tmpdbfp, layer_name, label_col="name" if "name" in self.tableModel.df.columns else None
                        )
                    except:
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print(
                            "WARNING: create_qgis_layer_df exception title {} refreshTableContents() failed exception: {}".format(
                                self.title, exstr
                            )
                        )
                        qt_utils.msgbox("create layer failed: "+exstr, title="Failed")

    def headerMenu(self, pos):
        globalPos = self.mapToGlobal(pos)
        menu = QMenu()
        menu.addAction("Filter menu")
        selectedItem = menu.exec_(globalPos)
        if selectedItem:
            col = self.tableView.currentIndex().column()
            print("headermenuselected col: {}".format(col))
            self.horizontalHeader_sectionClicked(col)

    def horizontalHeader_sectionClicked(self, col):
        print("horizontalHeader_sectionClicked col {}".format(col))
        self.filterMenu = FilterMenuWidget(self, col)
        self.filterMenu.show()

        # posY = headerPos.y() + self.horizontalHeader.height()
        # posX = headerPos.x() + self.horizontalHeader.sectionPosition(index)
        # self.menu.exec_(QtCore.QPoint(posX, posY))

    def setFilterListModel(self, columnIndex, checkedRegexList):
        print(
            "setFilterListModel: columnIndex {}, checkedRegexList {}".format(
                columnIndex, checkedRegexList
            )
        )
        self.proxyModel.filterFromMenu[columnIndex] = checkedRegexList
        self.proxyModel.invalidateFilter()

    def ui_thread_new_model(self):
        self.setTableModel(self.dataList)

    def ui_thread_model_datachanged(self):
        print("ui_thread_model_datachanged")
        # this func is supposed to be called as a slot by ui thread - triggered by signal from non-ui thread
        index_topleft = self.tableModel.index(0, 0)
        index_bottomright = self.tableModel.index(100, 100)
        # self.tableModel.dataChanged.emit(index_topleft, index_bottomright, [QtCore.Qt.DisplayRole])
        self.proxyModel.dataChanged.emit(
            index_topleft, index_bottomright, [QtCore.Qt.DisplayRole]
        )
        self.tableView.scrollToTop()

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
            sm.selectionChanged.connect(self.update_selected_log_hash_time)

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
            df = dataList
            self.df = df
            self.df_str = self.df.astype(str)
            self.tableHeader = df.columns.values.tolist()
            self.rows = len(df)
            self.fetchRows = self.rows
            self.columns = len(df.columns)
            self.fetchColumns = self.columns
        else:
            self.df = None
            self.df_str = None

    def setDataSet(self, data_set: list):
        self.dataList = data_set

    def setTableSize(self, sizelist: list):
        if sizelist:
            self.rowCount = sizelist[0]
            self.columnCount = sizelist[1]

    def refreshTableContents(self):
        print("datatable refreshTableContents()")
        create_table_model = True  # always recreate tablemodel for non
        self.setMinimumSize(0, 0)
        if self.custom_df is not None:
            print("datatable refreshTableContents() custom_df")
            self.set_pd_df(self.custom_df)
        elif (
            self.gc.databasePath is not None
            and self.refresh_data_from_dbcon_and_time_func is not None
        ):
            try:
                with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                    refresh_dict = {"time": self.gc.currentDateTimeString, "log_hash": self.gc.selected_point_match_dict["log_hash"]}
                    print(
                        "datatable refreshTableContents() refresh_data_from_dbcon_and_time_func: refresh_dict:", refresh_dict
                    )
                    df = None
                    if isinstance(self.refresh_data_from_dbcon_and_time_func, str):
                        time = refresh_dict["time"]
                        log_hash = refresh_dict["log_hash"]
                        eval_str = self.refresh_data_from_dbcon_and_time_func
                        if sql_utils.is_sql_select(eval_str):
                            sql_str = eval_str
                            print("datatable refersh param title: {} sql sql_str: {}".format(self.title, sql_str))
                            df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon, sql_str, log_hash, time)
                        else:
                            print("datatable refersh param title: {} py eval_str: {}".format(self.title, eval_str))
                            df = eval(eval_str)
                            if not isinstance(df, pd.DataFrame):
                                df = pd.DataFrame({"py_eval_result":[df]})
                    elif isinstance(self.refresh_data_from_dbcon_and_time_func, list):
                        df_list = []
                        time = refresh_dict["time"]
                        log_hash = refresh_dict["log_hash"]
                        for eval_str in self.refresh_data_from_dbcon_and_time_func:
                            if sql_utils.is_sql_select(eval_str):
                                sql_str = eval_str
                                print("datatable refersh param title: {} sql sql_str: {}".format(self.title, sql_str))
                                df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon, sql_str, log_hash, time)
                                df_list.append(df)
                            else:
                                print("datatable refersh param title: {} py eval_str: {}".format(self.title, eval_str))
                                df = eval(eval_str)
                                if not isinstance(df, pd.DataFrame):
                                    df = pd.DataFrame({"py_eval_result":[df]})
                                df_list.append(df)
                        df = pd.concat(df_list)
                    elif isinstance(self.refresh_data_from_dbcon_and_time_func, dict):
                        time = refresh_dict["time"]
                        log_hash = refresh_dict["log_hash"]
                        df_dict_list = []
                        for key in self.refresh_data_from_dbcon_and_time_func:
                            df_list = []
                            for eval_str in self.refresh_data_from_dbcon_and_time_func[key]:
                                if sql_utils.is_sql_select(eval_str):
                                    sql_str = eval_str
                                    print("datatable refersh param title: {} sql sql_str: {}".format(self.title, sql_str))
                                    df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon, sql_str, log_hash, time, col_name=key)
                                    df_list.append(df)
                                else:
                                    print("datatable refersh param title: {} py eval_str: {}".format(self.title, eval_str))
                                    df = eval(eval_str)
                                    if not isinstance(df, pd.DataFrame):
                                        df = pd.DataFrame({"py_eval_result":[df]})
                                    df_list.append(df)
                            df = pd.concat(df_list)
                            df_dict_list.append(df)
                        df = pd.concat(df_dict_list, axis=1)
                        df = df.loc[:,~df.columns.duplicated()]
                    else:
                        print("datatable refersh param title: {} refresh_data_from_dbcon_and_time_func: {}".format(self.title, self.refresh_data_from_dbcon_and_time_func))
                        df = self.refresh_data_from_dbcon_and_time_func(dbcon, refresh_dict)
                    assert df is not None
                    assert isinstance(df, pd.DataFrame)
                    print("datatable refersh param view got df:\n", df.head())
                    self.set_pd_df(df)
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print(
                    "WARNING: datatable title {} refreshTableContents() failed exception: {}".format(
                        self.title, exstr
                    )
                )
                self.set_pd_df(pd.DataFrame({"Failed": [exstr]}))

        if self.dataList is not None:
            if create_table_model:
                print("datatable refreshTableContents() settablemodel")
                self.signal_ui_thread_emit_new_model.emit()
            else:
                print("datatable refreshTableContents() updatetablemodeldata")
                self.updateTableModelData(self.dataList)  # applies new self.dataList
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
        print("hilightRow: sampledate: %s start" % sampledate)
        # QgsMessageLog.logMessage('[-- Start hilight row --]', tag="Processing")
        # start_time = time.time()
        worker = None


        find_row_time_string = str(sampledate)
        find_row_time = azq_utils.datetimeStringtoTimestamp(find_row_time_string)
        find_row_log_hash = self.gc.selected_point_match_dict["log_hash"]

        ######### check same timestamp from last select propagate back to us - dont drift to last row with same ts
        print("hilightRow: find_row_time: {} self.selected_row_time: {}".format(find_row_time, self.selected_row_time))
        print("hilightRow: find_row_log_hash: {} self.selected_row_log_hash: {}".format(find_row_log_hash, self.selected_row_log_hash))
        if (find_row_time is not None and self.selected_row_time is not None):
            if find_row_time == self.selected_row_time:
                if (find_row_log_hash is None and self.selected_row_log_hash is None) or (find_row_log_hash is not None and self.selected_row_log_hash is not None and find_row_log_hash == self.selected_row_log_hash):
                    print("find_row_time == self.selected_row_time and same log_hash so omit this hilightrow() call")
                    return

        # findCurrentRow() will look as these two instance vars
        self.find_row_log_hash = find_row_log_hash
        self.find_row_time = find_row_time
        self.find_row_time_string = find_row_time_string

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
        print("hilightRow: sampledate: %s done" % sampledate)

    def showDetail(self, item):
        row_index = item.row()
        print("showDetail row_index: %d" % row_index)
        row_sr = self.tableModel.df.iloc[row_index]
        # cellContent = str(item.data())
        cellContent = ""
        for index, val in row_sr.items():
            cellContent += "[{}]: {}\n".format(index, val)
        if self.parentWindow:
            self.parentWindow.parentWidget()
        else:
            pass
        if 'name' in row_sr.index and 'dir' in row_sr.index and 'protocol' in row_sr.index:
            name = row_sr["name"]
            side = row_sr["dir"]
            protocol = row_sr["protocol"]
            self.detailWidget = DetailWidget(
                self.gc, self, cellContent, name, side, protocol
            )
        elif 'name' in row_sr.index and row_sr["name"].find("MOS Score") != -1:
            name = row_sr["name"]
            side = {}
            side["wav_file"] = os.path.join(
                azq_utils.tmp_gen_path(), row_sr["wave_file"]
            )
            side["text_file"] = os.path.join(
                azq_utils.tmp_gen_path(),
                row_sr["wave_file"].replace(".wav", "_polqa.txt"),
            )
            self.detailWidget = DetailWidget(
                self.gc, self, cellContent, name, side
            )
        elif self.list_module:
            import module_dialog
            dlg = module_dialog.module_dialog(self, row_sr, self.gc, self.mdi)
            dlg.show()
        else:
            self.detailWidget = DetailWidget(self.gc, self, cellContent)
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

    def update_selected_log_hash_time(self, item):
        print("update_selected_log_hash_time start self.ui_thread_selecting_row_dont_trigger_timechanged: {}".format(self.ui_thread_selecting_row_dont_trigger_timechanged))
        if self.ui_thread_selecting_row_dont_trigger_timechanged:
            print("update_selected_log_hash_time done because self.ui_thread_selecting_row_dont_trigger_timechanged: {}".format(
                self.ui_thread_selecting_row_dont_trigger_timechanged)
            )
            return
        # get selected row time for signalling and events table
        if not self.tableHeader:
            print("update_selected_log_hash_time: not self.tableHeader so return")
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

        selected_row_time = None
        selected_row_time_string = None
        selected_row_log_hash = None
        try:
            # check maybe current cell is not Time cell
            print("update_selected_log_hash_time get timecell0")
            headers = [item.lower() for item in self.tableHeader]
            print("update_selected_log_hash_time get timecell1")
            time_col_index = -1
            log_hash_col_index = -1
            time_col_index = headers.index("time")
            try:
                log_hash_col_index = headers.index("log_hash")
            except Exception as e:
                print("WARNING: get log_hash_col_index failed for this datatable - exception:", e)
            print("update_selected_log_hash_time get timecell2 time_col_index: {}".format(time_col_index))
            ret_contents = []
            for col_index in [time_col_index, log_hash_col_index]:
                print("update_selected_log_hash_time get col_index:", col_index)
                timeItem = item.sibling(item.row(), col_index)
                ret_contents.append(str(timeItem.data()))
            print("ret_contents:", ret_contents)
            selected_row_time_string = ret_contents[0]
            selected_row_time = azq_utils.datetimeStringtoTimestamp(ret_contents[0])
            selected_row_log_hash = np.int64(ret_contents[1])  # in windows somehow int not covering int64 of log_hash in some tests
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: update_selected_log_hash_time exception:", exstr)
        finally:
            if selected_row_time is not None:
                self.selected_row_time = selected_row_time
                self.selected_row_time_string = selected_row_time_string
                self.selected_row_log_hash = selected_row_log_hash
                try:
                    sliderValue = selected_row_time - self.gc.minTimeValue
                    sliderValue = round(sliderValue, 3)
                    self.gc.selected_row_time = selected_row_time
                    self.gc.selected_row_log_hash = selected_row_log_hash
                    self.gc.selected_point_match_dict = dict.fromkeys(analyzer_vars.SELECTED_POINT_MATCH_PARAMS)  # new dict with non vals in keys
                    self.gc.selected_point_match_dict["time"] = selected_row_time
                    self.gc.selected_point_match_dict["log_hash"] = selected_row_log_hash
                    self.gc.timeSlider.setValue(sliderValue)
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: updateSlider timecell exception:", exstr)
        print("updateslider done: self.gc.selected_row_time: {}, self.gc.selected_row_log_hash: {}".format(self.gc.selected_row_time, self.gc.selected_row_log_hash))

    def findCurrentRow(self):
        print("findcurrentrow start")
        if isinstance(self.dataList, pd.DataFrame):
            if self.find_row_time_string:
                df = self.tableModel.df  # self.dataList
                print("findcurrentrow cur df len:", len(df))
                ts_query = """time <= '{}'""".format(self.find_row_time_string)
                if self.find_row_log_hash is not None:
                    ts_query = """time <= '{}' and log_hash == {}""".format(self.find_row_time_string, self.find_row_log_hash)
                print("datatable findCurrentRow() ts_query:", ts_query)
                df = df[["log_hash", "time"]].reset_index().query(ts_query)  # we need new index as we want the row number, as this df might be a slice of an earlier filter so index wont be correct
                print("query done df head:\n", df.head())
                print("findcurrentrow after query df len: %d", len(df))
                if len(df):
                    self.currentRow = df.index[-1]
                    print("set currentrow: {}".format(self.currentRow))
                    self.signal_ui_thread_emit_select_row.emit(self.currentRow)
                return
        print("findcurrentrow done")

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
        self.verticalLayout = QVBoxLayout(FilterMenuWidget)
        self.verticalLayout.setObjectName("verticalLayout")

        self.searchBox = QLineEdit(FilterMenuWidget)
        self.searchBox.setFixedHeight(24)
        self.searchBox.setPlaceholderText(SEARCH_PLACEHOLDER_TEXT)
        self.verticalLayout.addWidget(self.searchBox)

        self.treeView = QTreeView(FilterMenuWidget)
        self.verticalLayout.addWidget(self.treeView)

        self.selectAllCb = QCheckBox(FilterMenuWidget)
        self.selectAllCb.setText("Select All")
        self.selectAllCb.setChecked(True)
        self.verticalLayout.addWidget(self.selectAllCb)
        self.selectAllCb.stateChanged.connect(self.selectAll)

        self.buttonBox = QDialogButtonBox(FilterMenuWidget)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.model = QStandardItemModel(self.treeView)
        self.model.setHorizontalHeaderLabels(["Name"])

        self.retranslateUi()
        #QtCore.QMetaObject.connectSlotsByName(self)
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
        self.proxyModel.setFilterKeyColumn(self.columnIndex)
        self.treeView.setModel(self.proxyModel)
        self.treeView.setSortingEnabled(True)
        self.treeView.sortByColumn(self.columnIndex, Qt.AscendingOrder)

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
        print("filtermenuwidget: search: text:", text)

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
        '''
        indices = [i for i, x in enumerate(self.gc.openedWindows) if x == self]
        for index in indices:
            self.gc.openedWindows.pop(index)
        '''
        self.close()
        del self



class DetailWidget(QDialog):    

    def __init__(
        self, gc, parent, detailText, messageName=None, side=None, protocol=None
    ):
        super().__init__(parent)
        self.closed = False
        self.title = "Details"
        self.gc = gc
        self.detailText = detailText
        self.nth_match = 0
        self.messageName = messageName
        self.side = side
        self.protocol = protocol
        self.left = 10
        self.top = 10
        self.parent = parent
        print("detailwidget self.parent", self.parent)
        self.width = 640
        self.height = 480
        self.setWindowFlags(QtCore.Qt.Window)
        self.polqaWavFile = None
        if self.messageName is not None and self.messageName.find("MOS Score") != -1:
            self.setUpPolqaMosScore()
        else:
            self.setupUi()

    def findedit_text_next(self):
        substring = self.findEdit.text().strip()
        self.search_and_highlight(substring, next_match=True)

    def findedit_text_changed(self):
        substring = self.findEdit.text().strip()
        self.search_and_highlight(substring, next_match=False)


    def clear_selection(self):
        # Process the displayed document
        cursor = self.textEdit.textCursor()
        cursor.select(QtGui.QTextCursor.Document)
        cursor.setCharFormat(QtGui.QTextCharFormat())
        cursor.clearSelection()
        #self.textEdit.setTextCursor(cursor)

    def move_to_top(self):
        # Process the displayed document
        cursor = self.textEdit.textCursor()
        cursor.setPosition(0)
        cursor.movePosition(QtGui.QTextCursor.Start)
        self.textEdit.setTextCursor(cursor)


    def search_and_highlight(self, substring, next_match=False):
        try:
            format = QtGui.QTextCharFormat()
            format.setBackground(QtGui.QBrush(QtGui.QColor(255,255,0)))
            # Setup the regex engine
            regex = re.compile(substring, flags=re.IGNORECASE)
            self.clear_selection()
            if not substring:
                self.move_to_top()
                return
            matched = False
            n = 0
            print("next_match: {}".format(next_match))
            matches = list(re.finditer(regex, self.textEdit.toPlainText()))
            if next_match == False:
                self.nth_match = 0
            else:
                self.nth_match = (self.nth_match+1) if (self.nth_match < len(matches)-1) else 0
            print("self.nth_match: {}".format(self.nth_match))
            for match in matches:
                matched = True
                cursor = self.textEdit.textCursor()
                # Select the matched text and apply the desired format
                #print("match {} {}".format(match.start(), match.end()))
                cursor.setPosition(match.start())
                cursor.setPosition(match.end(), QtGui.QTextCursor.KeepAnchor)
                cursor.mergeCharFormat(format)
                if n == self.nth_match:
                    cursor = self.textEdit.textCursor()
                    cursor.setPosition(match.start())
                    self.textEdit.setTextCursor(cursor)  # move to first match
                    cursor.setPosition(match.end(), QtGui.QTextCursor.KeepAnchor)
                    selected_format = QtGui.QTextCharFormat()
                    selected_format.setFontUnderline(True)
                    cursor.mergeCharFormat(selected_format)
                n += 1
            if not matched:
                self.move_to_top()
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: detailwidget search_and_highlight() exception: {}".format(exstr))


    def setupUi(self):
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.textEdit = QTextEdit()
        self.textEdit.setPlainText(self.detailText)
        self.textEdit.setReadOnly(True)
        self.text_style = """
            * {
            font-size: 11px;
            }
            QTableCornerButton::section{border-width: 0px; border-color: #BABABA; border-style:solid;}
            """
        self.textEdit.setStyleSheet(self.text_style)
        self.findEdit = QLineEdit()
        self.findEdit.setPlaceholderText(SEARCH_PLACEHOLDER_TEXT)
        self.findEdit.setStyleSheet(self.text_style)
        self.findEdit.setMaximumHeight(25)
        self.findEdit.textChanged.connect(self.findedit_text_changed)
        self.findEdit.returnPressed.connect(self.findedit_text_next)
        layout = QVBoxLayout(self)
        layout.addWidget(self.findEdit)
        layout.addWidget(self.textEdit)
        self.setLayout(layout)

        try:
            import main_window
            window_geom = self.gc.main_window.current_workspace_settings.value(                
                main_window.GUI_SETTING_NAME_PREFIX + "detail_widget_geom"
            )
            if window_geom:                
                self.restoreGeometry(window_geom)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: detailwidget restoregeom failed - exception: {}".format(exstr))
        
        self.show()
        #self.raise_()
        #self.activateWindow()
        
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
        try:
            import main_window
            self.gc.main_window.current_workspace_settings.setValue(
                
                main_window.GUI_SETTING_NAME_PREFIX + "detail_widget_geom", self.saveGeometry()
            )
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: closeevent savegeom failed - exception: {}".format(exstr))
        self.close()
        self.closed = True
        del self
        

    def setDecodedDetail(self, detail):
        if self.closed == False:
            self.textEdit.setPlainText(
                self.detailText
                + "\n------\nALTERNATIVE WIRESHARK DECODE OF SAME PACKET BELOW\n------\n"
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
        self.textEdit.setPlainText(self.detailText + "\n" + f.read())
        f.close()

        self.polqaWavFile = (self.side["wav_file"])
        self.resize(self.width, self.height)
        self.show()
        self.raise_()
        self.activateWindow()

    def saveWaveFile(self):
        wavfilepath = str(self.polqaWavFile)
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
            if os.path.isfile(self.polqaWavFile):
                try:
                    print("play wav startfile start")
                    azq_utils.launch_file(self.polqaWavFile)
                    print("play wav startfile done")
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: play wav startfile exception: {}", exstr)
                    pass
            else:
                print("WARNING: NOT os.path.isfile(self.polqaWavFile): {}".format(self.polqaWavFile))


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
                self.df = self.df[
                    self.df[col].astype(str).str.contains(regex, case=False)
                ]
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

        print(
            "pdtablemodel setStrColFilters filteres DONE len(self.df_full) {} len(self.df) {}".format(
                len(self.df_full), len(self.df)
            )
        )

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
                if ret.endswith("000") and "." in ret:
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


def create_table_window_from_api_expression_ret(
    parent,
    title,
    gc,
    server,
    token,
    lhl,
    azq_report_gen_expression,
    mdi=None,
    list_module=False,
):
    window = TableWindow(
        parent,
        title,
        None,
        gc=gc,
        time_list_mode=True,
        skip_setup_ui=True,
        mdi=mdi,
        list_module=list_module,
    )
    gen_thread = threading.Thread(
        target=run_api_expression_and_set_results_to_table_window,
        args=(window, server, token, lhl, azq_report_gen_expression),
    )
    gen_thread.start()
    return window


def run_api_expression_and_set_results_to_table_window(
    window, server, token, lhl, azq_report_gen_expression
):
    try:
        ret_dict = azq_server_api.api_py_eval_get_parsed_ret_dict(
            server,
            token,
            lhl,
            azq_report_gen_expression,
            progress_update_signal=window.progress_update_signal,
            status_update_signal=window.status_update_signal,
            done_signal=None,
        )
        # time.sleep(1)
        print("api call ret_dict: {}".format(ret_dict))
        df = azq_server_api.parse_py_eval_ret_dict_for_df(server, token, ret_dict)
        if df is None:
            df = pd.DataFrame({"result": [ret_dict["ret"]],})
        window.setup_ui_with_custom_df(df)
    except Exception:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: api_py_eval_and_wait_completion exception: {}", exstr)
        df = pd.DataFrame({"FAILED": [exstr]})
        window.setup_ui_with_custom_df(df)
