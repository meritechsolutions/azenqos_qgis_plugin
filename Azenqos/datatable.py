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
import pyqtgraph as pg
import wave
import datetime
from functools import partial

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c

import pandas as pd
import numpy as np

from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QItemSelection,
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
    QSizePolicy,
    QLabel
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
        custom_table_param_list=None,
        custom_last_instant_table_param_list=None,
        custom_table_main_not_null=False,
        selected_ue=None,

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
        self.custom_table_param_list = custom_table_param_list
        self.custom_table_main_not_null = custom_table_main_not_null
        self.custom_last_instant_table_param_list = custom_last_instant_table_param_list

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
        self.selected_ue = selected_ue
        self.selected_logs = None
        if len(self.gc.device_configs):
            self.selected_logs = self.gc.device_configs[0]["log_hash"]
            if self.selected_ue is not None:
                title_ue_suffix = "(" + self.gc.device_configs[self.selected_ue]["name"]+ ")"
                if title_ue_suffix not in self.title:
                    self.title = self.title + title_ue_suffix 
                    self.selected_logs = self.gc.device_configs[self.selected_ue]["log_hash"]

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
        self.svg_icon_fp= None
        self.image_path = None
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

    def setup_image_ui(self):
        self.setObjectName(self.title)
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, 400, 300)
        print("image_path", self.image_path)
        self.label = QLabel(self)
        self.pixmap = QPixmap(self.image_path)
        self.label.setPixmap(self.pixmap)
        self.label.resize(self.pixmap.width(),
                          self.pixmap.height())
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.show()


    def contextMenuEvent(self, event):
        menu = QMenu(self)
        actions_dict = {"create_qgis_layer": None, "custom_expression": None, "to_csv": None, "to_parquet": None, "custom_table": None}
        if self.time_list_mode and self.df is not None and 'log_hash' in self.df.columns and 'time' in self.df.columns:
            actions_dict["create_qgis_layer"] = menu.addAction("Create QGIS Map layer...")
        if self.df is not None and "lat" in self.df.columns and "lon" in self.df.columns:
            self.svg_icon_fp = azq_utils.get_module_fp("map-marker-alt.svg")
            actions_dict["create_qgis_layer"] = menu.addAction("Create QGIS Map layer...")
        if isinstance(self.refresh_data_from_dbcon_and_time_func, (str, list, dict)):
            actions_dict["custom_expression"] = menu.addAction("Customize SQL/Python expression...")
        if self.custom_table_param_list:
            actions_dict["custom_table"] = menu.addAction("Customize table...")
        if self.custom_last_instant_table_param_list:
            actions_dict["custom_last_instant_table"] = menu.addAction("Customize table...")
        if not self.custom_last_instant_table_param_list:
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
        elif action == actions_dict["custom_last_instant_table"]:
            import custom_last_instant_table_dialog
            dlg = custom_last_instant_table_dialog.custom_last_instant_table_dialog(self.gc, self.custom_last_instant_table_param_list, self.title, selected_ue=self.selected_ue)
            def on_result(param_list, title, selected_ue):
                self.custom_df=param_list
                self.custom_last_instant_table_param_list=param_list
                self.title=title
                self.selected_ue=selected_ue
                self.setObjectName(self.title)
                self.setWindowTitle(self.title)
                self.refreshTableContents()
            dlg.on_result.connect(on_result)
            dlg.show()
        elif action == actions_dict["custom_table"]:
            import custom_table_dialog
            dlg = custom_table_dialog.custom_table_dialog(self.gc, self.custom_table_param_list, self.title, selected_ue=self.selected_ue, main_not_null=self.custom_table_main_not_null)
            def on_result(df, param_list, title, selected_ue, main_not_null):
                self.custom_df=df
                self.custom_table_param_list=param_list
                self.custom_table_main_not_null = main_not_null
                self.title=title
                self.selected_ue=selected_ue
                self.setObjectName(self.title)
                self.setWindowTitle(self.title)
                self.refreshTableContents()
            dlg.on_result.connect(on_result)
            dlg.show()
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
                        if not fp.endswith(".csv"):
                            fp += ".csv"
                        df.to_csv(fp, index=False, quoting=csv.QUOTE_ALL)
                    else:
                        if not fp.endswith(".parquet"):
                            fp += ".parquet"
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
                    azq_utils.create_layer_in_qgis(self.gc.databasePath, self.tableModel.df, layer_name, is_indoor=self.gc.is_indoor, svg_icon_fp=self.svg_icon_fp)


    def headerMenu(self, pos):
        globalPos = self.mapToGlobal(pos)
        menu = QMenu()
        menu.addAction("Filter menu")
        selectedItem = menu.exec_(globalPos)
        if selectedItem:
            # col = self.tableView.currentIndex().column()
            col = self.filterHeader.logicalIndexAt(pos.x())
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
        self.proxyModel.setFilterListModel(columnIndex, checkedRegexList)
        # self.proxyModel.invalidateFilter()

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

    def set_image_window(self, image_path):
        self.image_path = image_path
        self.signal_ui_thread_setup_ui.emit()

    """
    for trigger like window.signal_ui_thread_setup_ui.emit() when skip_setup_ui flagged in ctor
    """

    def ui_thread_sutup_ui(self):
        print("ui_thread_sutup_ui")
        if self.image_path is not None:
            self.setup_image_ui()
        else:
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
        refresh_dict = {"time": self.gc.currentDateTimeString, "log_hash": self.gc.selected_point_match_dict["log_hash"]}
        if self.customHeader:
            self.tableHeader = self.customHeader

        self.dataList = dataList
        if isinstance(dataList, pd.DataFrame):
            self.set_pd_df(dataList)
            self.tableModel = PdTableModel(dataList, self)
        else:
            self.tableModel = TableModel(dataList, self.tableHeader, refresh_dict["time"], refresh_dict["log_hash"], self.gc, self)
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
                            df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon, sql_str, log_hash, time, selected_logs=self.selected_logs)
                            if not isinstance(df, pd.DataFrame):
                                df = pd.DataFrame({"py_eval_result":[df]})
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
                                df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon, sql_str, log_hash, time, selected_logs=self.selected_logs)
                                if not isinstance(df, pd.DataFrame):
                                    df = pd.DataFrame()
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
                                    df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon, sql_str, log_hash, time, col_name=key, selected_logs=self.selected_logs)
                                    if not isinstance(df, pd.DataFrame):
                                        df = pd.DataFrame()
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
                        if self.title.lower() == "add layer" or self.title.lower().startswith("pcap"):
                            df = self.refresh_data_from_dbcon_and_time_func
                        elif self.title.lower().startswith("wifi scan"):
                            df = self.refresh_data_from_dbcon_and_time_func(dbcon, refresh_dict, selected_logs=self.selected_logs)
                        else:
                            df = self.refresh_data_from_dbcon_and_time_func(dbcon, refresh_dict)
                    assert df is not None
                    assert isinstance(df, pd.DataFrame)
                    if self.time_list_mode:
                        
                        df["time"] = pd.to_datetime(df["time"])
                        if self.title == "Events" and len(self.gc.pre_wav_file_list) > 0:
                            import voice_call_setup_df
                            pre_wav_file_df = voice_call_setup_df.get_voice_call_setup_df(self.gc.pre_wav_file_list)
                            df = df.append(pre_wav_file_df)
                            df["time"] = pd.to_datetime(df["time"])
                            df["log_hash"] = df["log_hash"].astype(np.int64)

                        if "time" in df.columns:
                            df = df.sort_values(by="time")
                            if "log_hash" in df.columns and len(df) > 0:
                                if len(self.gc.device_configs):
                                    for device in self.gc.device_configs:
                                        df.loc[df["log_hash"].astype(str).isin(device["log_hash"]), "UE"] = device["name"]
                                    df["UE"] = df["UE"].astype(str)
                                elif len(self.gc.log_list) > 0:
                                    i = 1
                                    for lh in self.gc.log_list:
                                        df.loc[df["log_hash"] == lh, "UE"] = i
                                        i += 1
                                    df["UE"] = df["UE"].astype(int).astype(str)
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

        if self.gc.has_wave_file == True:
            try:
                if self.detailWidget:
                    self.detailWidget.move_cursor(find_row_time)
            except:
                pass

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

        if not self.time_list_mode :
            # table data mode like measurements of that time needs refresh
            if threading:
                worker = Worker(self.refreshTableContents)
            else:
                self.refreshTableContents()
        else:
            if self.gc.live_mode:
                if "time" in self.df:
                    with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                        eval_str = self.refresh_data_from_dbcon_and_time_func
                        sql = re.search(r"^pd\.read_sql\('(.*)',dbcon\)",eval_str).group(1)
                        where = "where time > '{}'".format(self.df["time"].max())
                        sql = sql_utils.add_first_where_filt(sql, where)
                        append_df = pd.read_sql(sql, dbcon)
                        append_df["time"] = pd.to_datetime(append_df["time"])
                        if len(self.gc.device_configs) and "log_hash" in append_df.columns:
                            for device in self.gc.device_configs:
                                append_df.loc[append_df["log_hash"].astype(str).isin(device["log_hash"]), "UE"] = device["name"]
                            append_df["UE"] = append_df["UE"].astype(str)
                        df = pd.concat([self.df, append_df]).sort_values("time").reset_index(drop = True)
                        self.set_pd_df(df)
                        self.signal_ui_thread_emit_new_model.emit()
                        self.tableViewCount = self.tableView.model().rowCount()
                    if threading:
                        worker = Worker(self.findCurrentRow)
                    else:
                        self.findCurrentRow()
                else:
                    if threading:
                        worker = Worker(self.refreshTableContents)
                        worker = Worker(self.findCurrentRow)
                    else:
                        self.refreshTableContents()
                        self.findCurrentRow()
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
        try:
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
            elif self.title.lower() == "add layer":
                param_name = row_sr["var_name"]
                n_arg_max = row_sr["n_arg_max"]
                import add_map_layer_dialog

                dlg = add_map_layer_dialog.add_map_layer_dialog(self.gc, param_name, n_arg_max)
                dlg.show()
            elif 'name' in row_sr.index and (row_sr["name"] == "MOS Score" or row_sr["name"] == "voice call setup"):
                name = row_sr["name"]
                side = {}
                side["name"] = row_sr["name"]
                side["log_hash"] = row_sr["log_hash"]
                side["wav_file"] = os.path.join(
                    azq_utils.tmp_gen_path(), str(row_sr["log_hash"]), row_sr["wave_file"]
                )
                if row_sr["name"] == "MOS Score":
                    side["text_file"] = os.path.join(
                        azq_utils.tmp_gen_path(), str(row_sr["log_hash"]), row_sr["wave_file"].replace(".wav", "_polqa.txt"),
                    )
                side["time"] = row_sr["time"]
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
        except:
            pass

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

        self.proxyModel = SortFilterProxyModel()
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
        if self.messageName is not None and (messageName == "MOS Score" or messageName == "voice call setup"):
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
            self.clear_selection()
            if not substring:
                self.move_to_top()
                return
            # Setup the regex engine
            regex = re.compile(substring, flags=re.IGNORECASE)
            n = 0
            print("next_match: {}".format(next_match))
            matches = list(re.finditer(regex, self.textEdit.toPlainText()))
            if next_match == False:
                self.nth_match = 0
            else:
                self.nth_match = (self.nth_match+1) if (self.nth_match < len(matches)-1) else 0
            print("self.nth_match: {}".format(self.nth_match))

            # hilight in the ui
            MAX_UI_HIGHLIGHT_N = 10  # if thousands of matches this will block ui and ui thread so keep it quick
            ui_background_color_format = QtGui.QTextCharFormat()
            ui_background_color_format.setBackground(QtGui.QBrush(QtGui.QColor(255, 255, 0)))

            if not len(matches):
                self.move_to_top()

            for i in range(len(matches)):
                # hilight - dont hilight all as this is slow and will hang the ui thread
                do_hilight = n > self.nth_match - MAX_UI_HIGHLIGHT_N/2 and n < self.nth_match + MAX_UI_HIGHLIGHT_N/2
                if do_hilight:
                    match = matches[i]
                    cursor = self.textEdit.textCursor()
                    cursor.setPosition(match.start())
                    cursor.setPosition(match.end(), QtGui.QTextCursor.KeepAnchor)
                    cursor.mergeCharFormat(ui_background_color_format)
                # underline and move the position
                if n == self.nth_match:
                    match = matches[i]
                    cursor = self.textEdit.textCursor()
                    cursor.setPosition(match.start())
                    self.textEdit.setTextCursor(cursor)  # move to first match
                    cursor.setPosition(match.end(), QtGui.QTextCursor.KeepAnchor)
                    selected_format = QtGui.QTextCharFormat()
                    selected_format.setFontUnderline(True)
                    cursor.mergeCharFormat(selected_format)
                n += 1

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
        self.findEdit.returnPressed.connect(self.findedit_text_next)
        self.findEdit.textChanged.connect(self.findedit_text_changed)
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
        self.start_time_s = azq_utils.datetimeStringtoTimestamp(str(self.side["time"]))
        self.framerate = 0
        
        self.show_ref_wave_check_box = QCheckBox("Show reference")
        self.show_ref_wave_check_box.setChecked(False)
        self.show_ref_wave_check_box.hide()
        enable_show_ref_wave_check_box = partial(self.show_ref_wave, self.show_ref_wave_check_box)
        disable_show_ref_wave_check_box = partial(self.hide_ref_wave, self.show_ref_wave_check_box)
        self.show_ref_wave_check_box.stateChanged.connect(
            lambda x: enable_show_ref_wave_check_box() if x else disable_show_ref_wave_check_box()
        )

        pg.setConfigOptions(background="#c0c0c0", foreground="k", antialias=True)
        
        self.wave_sine = pg.GraphicsWindow()
        self.wave_sine.scene().sigMouseClicked.connect(self.on_click)
        self.v_line = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen("k")
        )

        self.textEdit = QTextEdit()
        self.textEdit.setReadOnly(True)

        gridlayout.addWidget(self.playBtn, 0, 0, 1, 2)
        gridlayout.addWidget(self.show_ref_wave_check_box, 0, 2, 1, 1)
        gridlayout.addWidget(self.saveBtn, 0, 3, 1, 1)
        gridlayout.addWidget(self.wave_sine, 1, 0, 1, 4)
        gridlayout.addWidget(self.textEdit, 2, 0, 2, 4)

        self.playBtn.clicked.connect(self.playWavFile)
        self.saveBtn.clicked.connect(self.saveWaveFile)

        if self.side["name"] == "MOS Score":
            self.show_ref_wave_check_box.show()
            self.setLayout(gridlayout)
            f = open(self.side["text_file"], "r")
            self.textEdit.setPlainText(self.detailText + "\n" + f.read())
            f.close()

        self.polqaWavFile = (self.side["wav_file"])
        self.set_ref_wave()
        self.set_wave()
        self.show_ref_wave_check_box.setChecked(False)
        self.hide_ref_wave(self.show_ref_wave_check_box)
        self.resize(self.width, self.height)
        self.show()
        self.raise_()
        self.activateWindow()

    def draw_cursor(self, x):
        self.v_line.setPos(x)

    def show_ref_wave(self, checkbox):
        self.wave_sine.axes1.show()

    def hide_ref_wave(self, checkbox):
        self.wave_sine.axes1.hide()
    
    def move_cursor(self, current_time_s):
        time_s = current_time_s-self.start_time_s
        x = time_s * self.framerate
        self.draw_cursor(x)
        
    def on_click(self, event):
        x = self.wave_sine.axes0.vb.mapSceneToView(event.scenePos()).x()
        self.draw_cursor(x)
        sliderValue = (x/self.framerate)+self.start_time_s - self.gc.minTimeValue
        sliderValue = round(sliderValue, 3)
        self.gc.timeSlider.setValue(sliderValue)
    
    def set_ref_wave(self):
        ref_wave_file_name = "polqaref_np"
        ref_framerate = 48000.0
        ref_nframes = 305732
        if len(self.gc.is_mos_nb_lh_list) > 0 and self.side["log_hash"] in self.gc.is_mos_nb_lh_list:
            print("is_mos_nb_lh_list")
            ref_wave_file_name = "polqarefnb_np"
            ref_framerate = 8000.0
            ref_nframes = 50956
        ref_wave_file_path = azq_utils.get_module_fp(ref_wave_file_name)
        if os.path.isfile(ref_wave_file_path):
            data = np.fromfile(ref_wave_file_path, dtype="int16")
            self.wave_sine.axes1 = self.wave_sine.addPlot(
                0, 0,axisItems={"bottom": RefTimeAxisItem(orientation="bottom", framerate=ref_framerate)}
            )
            self.wave_sine.axes1.plot(data,
                pen=pg.mkPen("b"),)
            self.wave_sine.axes1.setTitle("Reference")
            self.wave_sine.axes1.setLimits(
                xMin=-0,
                xMax=ref_nframes,
                yMin=-40000,
                yMax=40000
            )

    def set_wave(self):
        if self.polqaWavFile:
            if os.path.isfile(self.polqaWavFile):
                wf = wave.open(self.polqaWavFile, 'rb')
                self.framerate = float(wf.getframerate())
                self.nframe = wf.getnframes()
                buf = wf.readframes(self.nframe)
                data = np.frombuffer(buf, dtype="int16")
                self.wave_sine.axes0 = self.wave_sine.addPlot(
                    1, 0, axisItems={"bottom": TimeAxisItem(orientation="bottom", framerate=self.framerate, start_time = self.start_time_s)}
                )
                self.wave_sine.axes0.addItem(self.v_line, ignoreBounds=True)
                self.wave_sine.axes0.plot(data,
                    pen=pg.mkPen("b"),)
                self.wave_sine.axes0.setTitle("Degraded")
                self.wave_sine.axes0.setLimits(
                    xMin=-0,
                    xMax=self.nframe,
                    yMin=-40000,
                    yMax=40000
                )
                self.draw_cursor(0)

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
    def __init__(self, inputData, header, time, log_hash, gc, parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.headerLabels = header
        self.dataSource = inputData
        self.time = time
        self.log_hash = log_hash
        self.gc = gc
        # self.testColumnValue()

    def rowCount(self, parent):
        rows = 0
        if self.dataSource:
            rows = len(self.dataSource)
        return rows

    def columnCount(self, parent):
        columns = 0
        if self.dataSource:
            columns = len(self.dataSource[0])
        return columns

    def get_complementary(self, color):
        if color[0] == '#':
            color = color[1:]
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
        comp_color = "#FFFFFF"
        if (red*0.299 + green*0.587 + blue*0.114) > 130:
            comp_color = "#000000"
        return comp_color

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                value_dict = self.dataSource[index.row()][index.column()]
                value_dict["color"] = "#FFFFFF"
                value_dict["percent"] = None
                if "type" in value_dict.keys():
                    if value_dict["type"] == "text":
                        value = value_dict["value"]
                    else:
                        table_name = preprocess_azm.get_table_for_column(value_dict["value"])
                        sql = "select {} from {}".format(value_dict["value"] , table_name)
                        sql = sql_utils.sql_lh_time_match_for_select_from_part(sql, self.log_hash, self.time)
                        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                            df = pd.read_sql(sql, dbcon)
                            if len(df) > 0:
                                value = df[value_dict["value"]].iloc[-1]
                                import db_preprocess
                                if value_dict["value"] in db_preprocess.cached_theme_dict.keys():
                                    theme_df = db_preprocess.cached_theme_dict[value_dict["value"]]
                                    theme_df["Lower"] = theme_df["Lower"].astype(float)
                                    theme_df["Upper"] = theme_df["Upper"].astype(float)
                                    theme_range = theme_df["Upper"].max() - theme_df["Lower"].min()
                                    value_dict["percent"] = (float(value) - theme_df["Lower"].min()) / theme_range
                                    color_df = theme_df.loc[(theme_df["Lower"]<=float(value))&(theme_df["Upper"]>float(value)), "ColorXml"]
                                    if len(color_df) > 0:
                                        value_dict["color"] = color_df.iloc[0]
                            else:
                                value = ""
                            if not isinstance(value, str):
                                if isinstance(value, float):
                                    value = "%.02f" % value
                                else:
                                    value = str(value)
                else:
                    value = ""
                return value
            
            if role == QtCore.Qt.BackgroundRole:
                try:
                    value_dict = self.dataSource[index.row()][index.column()]
                    if "percent" in value_dict.keys():
                        if value_dict["percent"] is not None:
                            # gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(1, 0))
                            # gradient.setColorAt(0, QtGui.QColor(value_dict["color"]))
                            # gradient.setColorAt(value_dict["percent"], QtGui.QColor(value_dict["color"]))
                            # gradient.setColorAt(value_dict["percent"]+0.001, Qt.white)
                            # gradient.setColorAt(1, Qt.white)
                            # gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
                            return QtCore.QVariant(QtGui.QColor(value_dict["color"]))
                except Exception as e:
                    print("WARNING: pdtablemodel data() exception: ", e)
                    return None
                
            if role == QtCore.Qt.ForegroundRole:
                value_dict = self.dataSource[index.row()][index.column()]
                if "color" in value_dict.keys():
                    fg_color = self.get_complementary(value_dict["color"])
                    return QtCore.QVariant(QtGui.QColor(fg_color))
            else:
                return None
        
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

def epochToDateString(epoch):
    try:
        return datetime.datetime.fromtimestamp(epoch).strftime("%H:%M:%S.%f")[:-3]
    except:
        return ""

class TimeAxisItem(pg.AxisItem):
    """Internal timestamp for x-axis"""

    def __init__(self, framerate, start_time, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)
        self.framerate = framerate
        self.start_time = start_time

    def tickStrings(self, values, scale, spacing):
        return [epochToDateString(self.start_time+(value/self.framerate)) for value in values]

class RefTimeAxisItem(pg.AxisItem):
    """Internal timestamp for x-axis"""

    def __init__(self, framerate, *args, **kwargs):
        super(RefTimeAxisItem, self).__init__(*args, **kwargs)
        self.framerate = framerate

    def tickStrings(self, values, scale, spacing):
        return [(value/self.framerate) for value in values]

class PdTableModel(QAbstractTableModel):
    def __init__(self, df, parent=None, *args):
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        if "time" in df.columns and len(df):
            try:
                df["time"] = pd.to_datetime(df["time"])
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: datatable time convert exception: {}", exstr)

        QAbstractTableModel.__init__(self, parent, *args)
        self.df_full = df
        self.df = df  # filtered data for display
        self.parent = parent
        self.filters = {}
        self.filterFromMenu = {}

    def setFilters(self, filters):
        self.filters = filters
        self.filter()
    
    def setFilterFromMenu(self, filterFromMenu):
        self.filterFromMenu = filterFromMenu
        self.filter()

    def rowCount(self, parent):
        return len(self.df)

    def columnCount(self, parent):
        return len(self.df.columns)

    def filter(self):
        print("pdtablemodel filteres START")
        self.df = self.df_full
        changed = True
        for col_index in self.filters.keys():
            col = self.df.columns[col_index]
            regex = self.filters[col_index].pattern()  # QRegExp
            if col and regex:
                print("filters col: {} regex: {}".format(col, regex))
                try:
                    self.df = self.df[
                        self.df[col].astype(str).str.contains(regex, case=False)
                    ]
                except Exception as exe:
                    print("WARNING: datatable regex filter exception:", exe)
        for col_index in self.filterFromMenu.keys():
            col = self.df.columns[col_index]
            regexlist = self.filterFromMenu[col_index]  # QRegExp
            if col and regexlist:
                print("filterFromMenu col: {} regex: {}".format(col, regexlist))
                try:
                    self.df = self.df[
                        self.df[col].isin(regexlist)
                    ]
                except Exception as exe:
                    print("WARNING: datatable regex filter exception:", exe)
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

    def get_complementary(self, color):
        if color[0] == '#':
            color = color[1:]
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
        comp_color = "#FFFFFF"
        if (red*0.299 + green*0.587 + blue*0.114) > 130:
            comp_color = "#000000"
        return comp_color

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # print("pdtablemodel data() role:", role)
        ret = self.df.iloc[index.row(), index.column()]
        ret_tuple = None    
        if isinstance(ret, str):
            if ret.startswith("ret_tuple"):
                ret = ret.replace("ret_tuple", "")
                ret = ret.split(",")
                ret = (float(ret[0]), ret[1], float(ret[2]))
        if isinstance(ret, tuple):
            ret_tuple = ret
        if role == QtCore.Qt.DisplayRole:
            # print("pdtablemodel data() displayrole enter")
            try:
                if pd.isnull(ret):
                    return None
                if not isinstance(ret, str):
                    if isinstance(ret, tuple):
                        ret = ret[0]
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
        if role == QtCore.Qt.BackgroundRole:
            try:
                if isinstance(ret_tuple, tuple):
                    # percent = float(ret_tuple[2])
                    color = "#FFFFFF"
                    if ret[1] is not None:
                        color = str(ret[1])
                    # gradient = QtGui.QLinearGradient(QtCore.QPointF(0, 0), QtCore.QPointF(1, 0))
                    # gradient.setColorAt(0, QtGui.QColor(color))
                    # gradient.setColorAt(percent, QtGui.QColor(color))
                    # gradient.setColorAt(percent+0.001, Qt.white)
                    # gradient.setColorAt(1, Qt.white)
                    # gradient.setCoordinateMode(QtGui.QLinearGradient.ObjectBoundingMode)
                    return QtCore.QVariant(QtGui.QColor(color))
            except Exception as e:
                print("WARNING: pdtablemodel data() exception: ", e)
                return None
            
        if role == QtCore.Qt.ForegroundRole:
            if isinstance(ret_tuple, tuple):
                color = "#FFFFFF"
                if ret[1] is not None:
                    color = str(ret[1])
                fg_color = self.get_complementary(color)
                return QtCore.QVariant(QtGui.QColor(fg_color))
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
        daemon=True
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
        target_fp = azq_server_api.parse_py_eval_ret_dict_for_df(server, token, ret_dict)
        print("target_fp:", target_fp)
        if "parquet" in target_fp:
            print("read parquet to df")
            df = pd.read_parquet(target_fp)
            #df.columns = [x.decode("utf-8") for x in df.columns]
            for col in df.columns:
                try:
                    df[col] = df[col].apply(lambda x: x.decode("utf-8"))
                except:
                    pass
            if df is None:
                df = pd.DataFrame({"result": [ret_dict["ret"]],})
            window.setup_ui_with_custom_df(df)
        elif "png" in target_fp:
            print("add image to image window")
            window.set_image_window(target_fp)
    except Exception:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: api_py_eval_and_wait_completion exception: {}", exstr)
        df = pd.DataFrame({"FAILED": [exstr]})
        window.setup_ui_with_custom_df(df)
