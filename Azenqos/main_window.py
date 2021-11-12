import contextlib
import datetime
import json
import pathlib
import shutil
import threading
import traceback
import azq_cell_file

import PyQt5
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QSettings, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QPixmap, QIcon, QColor
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QDateTimeEdit,
    QToolButton,
    QHBoxLayout,
    QFileDialog,
    QMdiSubWindow,
    QApplication,
    QMainWindow,
    QSizePolicy,
    QWidget,
    QStyle,
    QMessageBox,
    QPushButton,
)
from PyQt5.uic import loadUi
from qgis._core import QgsTask

import qt_utils, azq_utils
import spider_plot
from timeslider import timeSliderThread, timeSlider

from datatable import TableWindow, create_table_window_from_api_expression_ret
from worker import Worker
try:
    # noinspection PyUnresolvedReferences
    from qgis.core import (
        QgsProject,
        QgsLayerTreeGroup,
        QgsCoordinateReferenceSystem,
        QgsPointXY,
        QgsPoint,
        QgsRectangle,
        QgsGeometry,
        QgsMessageLog,
        QgsFeatureRequest,
        QgsApplication,
        QgsWkbTypes,
        QgsVectorLayer,
        QgsFeature,
        QgsField,
        QgsFields,
        QgsSymbol,
        QgsRendererRange,
        QgsGraduatedSymbolRenderer
    )

    # from qgis.utils import
    from qgis.gui import QgsMapToolEmitPoint, QgsHighlight
    from PyQt5.QtGui import QColor
    from qgis.PyQt.QtCore import QVariant

    print("mainwindow working in qgis mode")
except:
    print("mainwindow working in standalone mode")
    pass
import os
import sys

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import analyzer_vars

try:
    import db_layer_task
except:
    pass
from atomic_int import atomic_int
import import_db_dialog
import preprocess_azm
import params_disp_df
from version import VERSION

GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
import inspect
import linechart_custom
import linechart_multi_y_axis
import time
import pandas as pd
import sqlite3

TIME_COL_DEFAULT_WIDTH = 150
NAME_COL_DEFAULT_WIDTH = 180
CURRENT_WORKSPACE_FN = "last_workspace.ini"

class main_window(QMainWindow):

    signal_ui_thread_emit_time_slider_updated = pyqtSignal(float)
    task_done_signal = pyqtSignal(str)
    signal_trigger_zoom_to_active_layer = pyqtSignal(str)
    add_created_layers_signal = pyqtSignal(str, object)
    curInstance = None

    def __init__(self, qgis_iface, parent=None):
        curInstance = self
        if qgis_iface is not None and parent is None:
            parent = qgis_iface.mainWindow()
        print("mainwindow __init__ parent: {}".format(parent))
        super(main_window, self).__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        azq_utils.cleanup_died_processes_tmp_folders()

        ######## instance vars
        self.closed = False
        self.gc = analyzer_vars.analyzer_vars()
        self.gc.qgis_iface = qgis_iface
        self.gc.main_window = self
        self.timechange_service_thread = None
        self.is_legacy_indoor = False
        self.is_leg_nr_tables = False
        self.asked_easy_mode = False
        self.close_all_layers = True
        self.timechange_to_service_counter = atomic_int(0)
        self.signal_ui_thread_emit_time_slider_updated.connect(
            self.ui_thread_emit_time_slider_updated
        )
        self.task_done_signal.connect(
            self.task_done_slot
        )

        self.signal_trigger_zoom_to_active_layer.connect(
            self.slot_trigger_zoom_to_active_layer
        )

        self.db_layer_task = None
        self.cell_layer_task = None
        self.zoom_thread = None

        self.dbfp = None
        self.qgis_iface = qgis_iface
        self.crs_already_set = False
        self.timeSliderThread = timeSliderThread(self.gc)
        self.current_workspace_settings = QSettings(
            azq_utils.get_settings_fp(CURRENT_WORKSPACE_FN), QSettings.IniFormat
        )
        ########################
        self.setupUi()

        if self.qgis_iface is None:
            print("analyzer_window: standalone mode")
        else:
            print("analyzer_window: qgis mode")
            self.canvas = qgis_iface.mapCanvas()
            self.clickTool = QgsMapToolEmitPoint(self.canvas)
            self.setMapTool()
            self.reg_map_tool_click_point(self.clickCanvas)
            self.canvas.selectionChanged.connect(self.selectChanged)
            self.add_created_layers_signal.connect(self._add_created_layers)
            self.add_map_layer()
            self.set_project_crs()
        try:
            QgsProject.instance().layersAdded.connect(self.on_layers_added)
        except:
            pass

        self.timechange_service_thread = threading.Thread(target=self.timeChangedWorkerFunc, args=tuple(), daemon=True)
        self.timechange_service_thread.start()
        self.setMinimumSize(50, 50)
        azq_utils.adb_kill_server_threaded()  # otherwise cant update plugin as adb files would be locked
        print("main_window __init__() done")

    @pyqtSlot()
    def on_actionTile_triggered(self):
        print("tile")
        self.mdi.tileSubWindows()

    @pyqtSlot()
    def on_actionCascade_triggered(self):
        print("cascade")
        self.mdi.cascadeSubWindows()

    @pyqtSlot()
    def on_actionExit_triggered(self):
        print("exit")
        self.close()

    @pyqtSlot()
    def on_actionSettings_triggered(self):
        print("settings")
        self.gc.save_preferences()
        print("launch settings start")
        azq_utils.launch_file(analyzer_vars.get_pref_fp())
        print("launch settings done")

    @pyqtSlot()
    def on_actionEdit_settings_triggered(self):
        print("edit settings")
        self.gc.save_preferences()
        print("launch settings start")
        azq_utils.launch_file(analyzer_vars.get_pref_fp())
        qt_utils.msgbox("Please edit, save the file, then click on menu: File > Load settings", parent=self)

    @pyqtSlot()
    def on_actionRestore_settings_triggered(self):
        print("restore settings")
        self.gc.delete_preferences()  # also restores current pref
        self.gc.save_preferences()
        kv_str = ""
        for key in self.gc.pref:
            kv_str += "{}: {}\n".format(key, self.gc.pref[key])
        qt_utils.msgbox("Default settings restored:\n\n{}".format(kv_str), parent=self)

    @pyqtSlot()
    def on_actionLoad_settings_triggered(self):
        print("load settings")
        ret = self.gc.load_preferences()
        kv_str = ""
        for key in self.gc.pref:
            kv_str += "{}: {}\n".format(key, self.gc.pref[key])
        qt_utils.msgbox("Settings loaded success: {}\n\n{}".format(ret, kv_str), parent=self)

    @pyqtSlot()
    def on_actionOpen_log_triggered(self):
        print("open log")
        self.open_logs()

    @pyqtSlot()
    def on_actionOpen_workspace_triggered(self):
        print("open workspace")
        self.loadWorkspaceFile()

    @pyqtSlot()
    def on_actionSave_workspace_triggered(self):
        print("save workspace")
        self.saveWorkspaceFile()

    @pyqtSlot()
    def on_actionSupport_triggered(self):
        print("action support")
        qt_utils.msgbox("Please email support@azenqos.com", "Technical support", self)

    ############# server_modules menu slots
    @pyqtSlot()
    def on_actionSession_info_triggered(self):
        msg = "Not logged in"
        if self.is_logged_in():
            msg = """
Logged in: {}
Server: {}
User: {}
Log_hash list: {}""".format(
                "Yes" if self.gc.login_dialog.token else "No",
                self.gc.login_dialog.server,
                self.gc.login_dialog.user,
                self.gc.login_dialog.lhl,
            )
        qt_utils.msgbox(msg, parent=self)

    @pyqtSlot()
    def on_actionLogin_triggered(self):
        if self.is_logged_in():
            qt_utils.msgbox(
                "WARNING: You are already logged in - close login dialog to cancel re-login...",
                parent=self,
            )
        import login_dialog

        dlg = login_dialog.login_dialog(self, self.gc, download_db_zip=False)
        dlg.show()
        ret = dlg.exec()
        if ret == 0:  # dismissed
            return
        self.gc.login_dialog = dlg

    @pyqtSlot()
    def on_actionLogout_triggered(self):
        msg = "Logged out..."
        if not self.is_logged_in():
            msg = "Not logged in yet..."
        else:
            self.gc.login_dialog.token = None
        qt_utils.msgbox(msg, parent=self)


    @pyqtSlot()
    def on_actionServer_overview_layers_triggered(self):
        if not self.is_logged_in():
            self.on_actionLogin_triggered()
            if not self.is_logged_in():
                return
        import server_overview_widget
        widget = server_overview_widget.server_overview_widget(self, self.gc)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, widget, allow_no_log_opened=True, w=None, h=None)

    @pyqtSlot()
    def on_actionServerAIPrediction_triggered(self):
        if not self.is_logged_in():
            self.on_actionLogin_triggered()
            if not self.is_logged_in():
                return
        import predict_widget
        widget = predict_widget.predict_widget(self, self.gc)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, widget, allow_no_log_opened=True, w=None, h=None)

    @pyqtSlot()
    def on_actionOSM_triggered(self):
        self.add_map_layer()

    def reg_map_tool_click_point(self, func):
        print("reg_map_tool_click_point func:", func)
        self.clickTool.canvasClicked.connect(func)

    def dereg_map_tool_click_point(self, func):
        print("dereg_map_tool_click_point func:", func)
        self.clickTool.canvasClicked.disconnect(func)

    @pyqtSlot()
    def on_actionRun_server_modules_triggered(self):
        if not self.is_logged_in():
            qt_utils.msgbox("Please login to server first...", parent=self)
            return
        azq_report_gen_expression = "list_modules_with_process_cell_func.run()"
        swa = SubWindowArea(self.mdi, self.gc)
        widget = create_table_window_from_api_expression_ret(
            swa,
            "Server processing modules",
            self.gc,
            self.gc.login_dialog.server,
            self.gc.login_dialog.token,
            self.gc.login_dialog.lhl,
            azq_report_gen_expression,
            mdi=self.mdi,
            list_module=True,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionRun_PY_EVAL_code_triggered(self):
        if not self.is_logged_in():
            qt_utils.msgbox("Please login to server first...", parent=self)
            return
        py_eval_code = qt_utils.ask_text(
            self, "PY_EVAL code", "Please enter PY_EVAL code to run:"
        )
        if py_eval_code:
            swa = SubWindowArea(self.mdi, self.gc)
            widget = create_table_window_from_api_expression_ret(
                swa,
                "PY_EVAL server run",
                self.gc,
                self.gc.login_dialog.server,
                self.gc.login_dialog.token,
                self.gc.login_dialog.lhl,
                py_eval_code,
            )
            self.add_subwindow_with_widget(swa, widget)

    def run_py_eval_code_code_and_emit_to_window_once_done(self, py_eval_code, window):

        time.sleep(1)
        df = pd.DataFrame({"status": ["done"], "status2": ["done2"]})
        window.df = df
        window.tableHeader = df.columns.values.tolist()
        window.signal_ui_thread_emit_new_df.emit()

    @pyqtSlot()
    def on_actionRun_SQL_code_triggered(self):
        if not self.is_logged_in():
            qt_utils.msgbox("Please login to server first...", parent=self)
            return
        py_eval_code = qt_utils.ask_text(
            self, "SQL code", "Please enter SQL code to run:"
        )
        if py_eval_code:
            py_eval_code = "sql_helpers.read_sql('''{}''', dbcon)".format(py_eval_code)
            swa = SubWindowArea(self.mdi, self.gc)
            widget = create_table_window_from_api_expression_ret(
                swa,
                "SQL run from server",
                self.gc,
                self.gc.login_dialog.server,
                self.gc.login_dialog.token,
                self.gc.login_dialog.lhl,
                py_eval_code,
            )
            self.add_subwindow_with_widget(swa, widget)

    def is_logged_in(self):
        return self.gc.is_logged_in()

    ############# log menu slots
    @pyqtSlot()
    def on_actionLog_Info_triggered(self):
        self.add_param_window("pd.read_sql('''select log_hash, time, max(script_name) as script_name, max(script)as script, max(phonemodel) as phonemodel, max(imsi) as imsi, max(imei) as imei from log_info group by log_hash''',dbcon)", title="Log Info", time_list_mode=True)

    @pyqtSlot()
    def on_actionLogs_triggered(self):
        self.add_param_window("pd.read_sql('''select log_hash, time, log_start_time, log_end_time, log_tag, log_ori_file_name, log_app_version, log_license_edition, log_required_pc_version, log_timezone_offset from logs group by log_hash''',dbcon)", title="Logs", time_list_mode=True)

    @pyqtSlot()
    def on_actionLocation_triggered(self):
        self.add_param_window("pd.read_sql('''select log_hash, time, printf('%.8f', positioning_lat) as latitude, printf('%.8f', positioning_lon) as longitude from location where positioning_lat is not null''',dbcon)", title="Location", time_list_mode=True)

    ############# system menu slots
    @pyqtSlot()
    def on_actionTechnology_triggered(self):
        print("technology")
        import system_sql_query
        self.add_param_window(system_sql_query.SYSTEM_TECHNOLOGY_SQL_LIST, title="Technology", stretch_last_row=True, time_list_mode=True)

    @pyqtSlot()
    def on_actionGSM_WCDMA_System_Info_triggered(self):
        print("action gsm wdcma system info")
        import system_sql_query
        self.add_param_window(system_sql_query.GSM_WCDMA_SYSTEM_INFO_SQL_LIST, title="GSM/WCDMA System Info")

    @pyqtSlot()
    def on_actionLTE_System_Info_triggered(self):
        print("action lte system info")
        import system_sql_query
        self.add_param_window(system_sql_query.LTE_SYSTEM_INFO_SQL_LIST, title="LTE System Info")

    ############# footprint menu slots

    @pyqtSlot()
    def on_actionNR_PCI_Footprint_triggered(self):
        print("action nr pci footprint")
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "NR PCI Footprint", technology = "nr")
        dlg.show()

    @pyqtSlot()
    def on_actionLTE_PCI_Footprint_triggered(self):
        print("action lte pci footprint")
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "LTE PCI Footprint", technology = "lte")
        dlg.show()

    @pyqtSlot()
    def on_actionWCDMA_PSC_Footprint_triggered(self):
        print("action wcdma psc footprint")
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "WCDMA PSC Footprint", technology = "wcdma")
        dlg.show()

    @pyqtSlot()
    def on_actionGSM_BCCH_Footprint_triggered(self):
        print("action gsm bcch footprint")
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "GSM BCCH Footprint", technology = "gsm")
        dlg.show()

    ############# signalling menu slots
    @pyqtSlot()
    def on_actionLayer_3_Messages_triggered(self):
        self.add_param_window("pd.read_sql('''select log_hash, time, name, symbol as dir, protocol, detail_str from signalling''',dbcon).sort_values(by='time')", title="Layer-3 Messages", stretch_last_row=True, time_list_mode=True)

    @pyqtSlot()
    def on_actionEvents_triggered(self):
        has_wave_file = False
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            try:
                mos_df = pd.read_sql("select log_hash, time, 'MOS Score' as name, polqa_mos as info, wav_filename as wave_file from polqa_mos", dbcon)
                if len(mos_df) > 0 and "wave_file" in mos_df.columns:
                    has_wave_file = True
            except:
                pass
        if has_wave_file:
            self.add_param_window("pd.read_sql('''select log_hash, time, name, info, '' as wave_file from events union all select log_hash, time, 'MOS Score' as name, polqa_mos as info, wav_filename as wave_file from polqa_mos order by time''',dbcon)", title="Events", stretch_last_row=True, time_list_mode=True, func_key=inspect.currentframe().f_code.co_name)
        else:
            self.add_param_window("pd.read_sql('''select log_hash, time, name, info, '' as wave_file from events order by time''',dbcon)", title="Events", stretch_last_row=True, time_list_mode=True, func_key=inspect.currentframe().f_code.co_name)

    ############# NR menu slots
    @pyqtSlot()
    def on_action5GNR_Radio_triggered(self):
        print("action nr radio params")
        import nr_radio_query
        self.add_param_window(nr_radio_query.NR_RADIO_PARAMS_SQL_LIST, title="NR Radio")

    @pyqtSlot()
    def on_action5GNR_Data_triggered(self):
        print("action nr data params")
        import nr_data_query
        self.add_param_window(nr_data_query.NR_DATA_PARAMS_SQL_LIST, title="NR Data")

    def add_param_window(self, refresh_func_or_py_eval_str_or_sql_str, title="Param Window", time_list_mode=False, stretch_last_row=False, options=None, func_key=None):
        swa = SubWindowArea(self.mdi, self.gc)
        print("add_param_window: time_list_mode:", time_list_mode)
        widget = TableWindow(
            swa,
            title,
            refresh_func_or_py_eval_str_or_sql_str,
            time_list_mode=time_list_mode,
            stretch_last_row=stretch_last_row,
            options=options,
            func_key=func_key
        )
        self.add_subwindow_with_widget(swa, widget)
        #widget.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    @pyqtSlot()
    def on_actionCustom_Instant_View_triggered(self):
        import textwrap
        expression = azq_utils.ask_custom_sql_or_py_expression(
            self,
            table_view_mode=False,
            msg="Enter SQL select (must have log_hash,time columns) or Python expression",
            existing_content=textwrap.dedent(
            '''
            pd.read_sql("""
                            
            select log_hash, time,
            name, info, detail
            from events
            where {log_hash_filt_part} time between DATETIME('{time}','-2 seconds') and '{time}'
            order by time desc limit 1
            
            """.format(
            log_hash_filt_part='log_hash = {} and '.format(log_hash) if log_hash is not None else '',
            time=time),
            dbcon).transpose().reset_index()
            '''.strip()
            ).strip()
        )
        print("on_actionCustom_Instant_View_triggered new expression:", expression)
        if expression:
            title = qt_utils.ask_text(self, title="New window title", msg="Please enter desired title of new window",
                                      existing_content="Custom instant view")
            self.add_param_window(expression, title=title, time_list_mode=False)


    @pyqtSlot()
    def on_actionCustom_Table_View_triggered(self):
        import textwrap
        expression = azq_utils.ask_custom_sql_or_py_expression(
            self,
            table_view_mode=True,
            existing_content= textwrap.dedent(
            '''
            select
            log_hash, time,
            name, detail_str 
            from signalling
            union
            select log_hash, time,
            name, info
            from events
            order by log_hash, time
            '''.strip()
            ).strip()
        )
        print("on_actionCustom_Table_View_triggered new expression:", expression)
        if expression:
            title = qt_utils.ask_text(self, title="New window title", msg="Please enter desired title of new window",
                                      existing_content="Custom table view")
            self.add_param_window(expression, title=title, time_list_mode=True, stretch_last_row=True)


    @pyqtSlot()
    def on_actionExynosServiceMode_BasicInfo_2_triggered(self):
        self.add_param_window("select log_hash, time, exynos_basic_info from exynos_basic_info", title="ExynosServiceMode BasicInfo", stretch_last_row=True)


    @pyqtSlot()
    def on_actionExynosServiceMode_NR_Radio_triggered(self):
        import exynos_service_mode_nr_query
        self.add_param_window(exynos_service_mode_nr_query.RADIO_SELECT_FROM_PART, title="ExynosServiceMode NR Radio")


    @pyqtSlot()
    def on_actionExynosServiceMode_NR_Data_triggered(self):
        import exynos_service_mode_nr_query
        self.add_param_window(exynos_service_mode_nr_query.DATA_SELECT_FROM_PART, title="ExynosServiceMode NR Data")


    @pyqtSlot()
    def on_actionExynosServiceMode_NR_Reg_triggered(self):
        import exynos_service_mode_nr_query
        self.add_param_window(exynos_service_mode_nr_query.REG_SELECT_FROM_PART, title="ExynosServiceMode NR Reg")


    @pyqtSlot()
    def on_actionExynos_LTE_Radio_triggered(self):
        import exynos_service_mode_lte_query
        self.add_param_window(exynos_service_mode_lte_query.RADIO_SELECT_FROM_PART, title="ExynosServiceMode LTE Radio")


    @pyqtSlot()
    def on_actionExynosServiceMode_LTE_Data_triggered(self):
        import exynos_service_mode_lte_query
        self.add_param_window(exynos_service_mode_lte_query.DATA_SELECT_FROM_PART, title="ExynosServiceMode LTE Data")


    @pyqtSlot()
    def on_actionExynosServiceMode_LTE_Reg_triggered(self):
        import exynos_service_mode_lte_query
        self.add_param_window(exynos_service_mode_lte_query.REG_SELECT_FROM_PART, title="ExynosServiceMode LTE Reg")


    @pyqtSlot()
    def on_action5GNR_Radio_Parameters_triggered(self):
        print("action old nr radio params")
        import nr_sql_query
        if self.is_leg_nr_tables == False:
            self.add_param_window(nr_sql_query.NR_RADIO_PARAMS_SQL_LIST, title="NR Radio Parameters", func_key=inspect.currentframe().f_code.co_name)
        else:
            print("is legacy nr")
            self.add_param_window(nr_sql_query.OLD_NR_RADIO_PARAMS_SQL_LIST, title="NR Radio Parameters", func_key=inspect.currentframe().f_code.co_name)

    @pyqtSlot()
    def on_action5GNR_Serving_Neighbors_triggered(self):
        print("action nr serving neigh")
        import nr_sql_query
        if self.is_leg_nr_tables == False:
            self.add_param_window(nr_sql_query.NR_SERV_AND_NEIGH_SQL_LIST_DICT, title="NR Serving + Neighbors", func_key=inspect.currentframe().f_code.co_name)
        else:
            print("is legacy nr")
            self.add_param_window(nr_sql_query.OLD_NR_SERV_AND_NEIGH_SQL_LIST_DICT, title="NR Serving + Neighbors", func_key=inspect.currentframe().f_code.co_name)

    @pyqtSlot()
    def on_action5GNR_Beams_triggered(self):
        print("action nr beams")
        import nr_sql_query
        self.add_param_window(nr_sql_query.NR_BEAMS_SQL_LIST_DICT, title="NR Beams")

    @pyqtSlot()
    def on_action5GNR_Data_Params_triggered(self):
        print("action old nr data")
        import nr_sql_query
        if self.is_leg_nr_tables == False:
            self.add_param_window(nr_sql_query.NR_DATA_PARAMS_SQL_LIST, title="NR Data", func_key=inspect.currentframe().f_code.co_name)
        else:
            print("is legacy nr")
            self.add_param_window(nr_sql_query.OLD_NR_DATA_PARAMS_SQL_LIST, title="NR Data", func_key=inspect.currentframe().f_code.co_name)

    ############# LTE menu slots
    @pyqtSlot()
    def on_actionLTE_Radio_Parameters_triggered(self):
        print("action lte radio params")
        import lte_sql_query
        self.add_param_window(lte_sql_query.LTE_RADIO_PARAMS_SQL_LIST_DICT, title="LTE Radio Parameters")

    @pyqtSlot()
    def on_actionLTE_Serving_Neighbors_triggered(self):
        print("action lte serving neigh")
        import lte_sql_query
        self.add_param_window(lte_sql_query.LTE_SERV_AND_NEIGH_SQL_LIST_DICT, title="LTE Serving + Neighbors")
        
    @pyqtSlot()
    def on_actionLTE_Data_Params_triggered(self):
        print("action lte data param")
        import lte_sql_query
        self.add_param_window(lte_sql_query.LTE_DATA_PARAMS_SQL_LIST_DICT, title="LTE Data Params")

    @pyqtSlot()
    def on_actionLTE_PUCCH_PDSCH_Params_triggered(self):
        print("action lte pucch pdsch param")
        import lte_sql_query
        self.add_param_window(lte_sql_query.LTE_PUCCH_PDSCH_SQL_LIST_DICT, title="PUCCH/PDSCH Params")
        
    @pyqtSlot()
    def on_actionLTE_RRC_SIB_States_triggered(self):
        print("action lte rrc sib states")
        import lte_sql_query
        self.add_param_window(lte_sql_query.LTE_RRC_SIB_SQL_LIST, title="LTE RRC/SIB States")
        
    @pyqtSlot()
    def on_actionLTE_RLC_triggered(self):
        print("action lte rlc")
        import lte_sql_query
        self.add_param_window(lte_sql_query.LTE_RLC_SQL_LIST_DICT, title="LTE RLC")

    @pyqtSlot()
    def on_actionLTE_VoLTE_triggered(self):
        print("action lte volte")
        import lte_sql_query
        self.add_param_window(lte_sql_query.LTE_VOLTE_SQL_LIST, title="LTE VoLTE")

    ############# WCDMA menu slots

    @pyqtSlot()
    def on_actionWCDMA_Radio_Parameters_triggered(self):
        print("action wcdma radio params")
        import wcdma_sql_query
        self.add_param_window(wcdma_sql_query.WCDMA_RADIO_PARAMS_SQL_LIST, title="WCDMA Radio Parameters")

    @pyqtSlot()
    def on_actionWCDMA_Active_Monitored_sets_triggered(self):
        print("action wcdma active monitored")
        import wcdma_sql_query
        self.add_param_window(wcdma_sql_query.WCDMA_ACTIVE_MONITORED_SQL_LIST_DICT, title="WCDMA Active + Monitored sets")

    @pyqtSlot()
    def on_actionWCDMA_BLER_Summary_triggered(self):
        print("action wcdma bler summary")
        import wcdma_sql_query
        self.add_param_window(wcdma_sql_query.WCDMA_BLER_SQL_LIST, title="WCDMA BLER Summary")
        
    @pyqtSlot()
    def on_actionWCDMA_Bearers_triggered(self):
        print("action wcdma bearers")
        import wcdma_sql_query
        self.add_param_window(wcdma_sql_query.WCDMA_BLER_SQL_LIST_DICT, title="WCDMA Bearers")

    ############# GSM menu slots

    @pyqtSlot()
    def on_actionGSM_Physical_Parameters_triggered(self):
        print("action gsm radio params")
        import gsm_sql_query
        self.add_param_window(gsm_sql_query.GSM_RADIO_PARAMS_SQL_LIST, title="GSM Radio Parameters")

    @pyqtSlot()
    def on_actionGSM_Serving_Neighbors_triggered(self):
        print("action gsm serving neigh")
        import gsm_sql_query
        self.add_param_window(gsm_sql_query.GSM_SERV_AND_NEIGH_SQL_LIST_DICT, title="GSM Serving + Neighbors")

    @pyqtSlot()
    def on_actionGSM_Current_Channel_triggered(self):
        print("action gsm current channel")
        import gsm_sql_query
        self.add_param_window(gsm_sql_query.GSM_CURRENT_CHANNEL_SQL_LIST, title="GSM Current Channel")

    @pyqtSlot()
    def on_actionGSM_C_I_triggered(self):
        print("action gsm coi")
        import gsm_sql_query
        self.add_param_window(gsm_sql_query.GSM_COI_SQL_LIST_DICT, title="GSM C/I")

    ############# PCAP menu slots

    @pyqtSlot()
    def on_actionPCAP_triggered(self):
        print("action pcap")
        import pcap_window

        headers = [
            "log_hash",
            "time",
            "source",
            "destination",
            "protocol",
            "tcp.srcport",
            "tcp.dstport",
            "udp.srcport",
            "udp0.dstport",
            "packet.size",
            "info",
            "file_name",
        ]
        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "PCAP",
            pcap_window.new_get_all_pcap_content(azq_utils.tmp_gen_path()),
            tableHeader=headers,
            time_list_mode=True,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# Add Layer menu slots

    @pyqtSlot()
    def on_actionAdd_Layer_triggered(self):
        print("action add layer")
        elm_df = preprocess_azm.get_elm_df_from_csv()
        elm_df = elm_df.loc[(elm_df["var_type"] == "Double") | (elm_df["var_type"] == "Integer"), ("var_name", "name", "n_arg_max")].reset_index(drop=True)
        swa = SubWindowArea(self.mdi, self.gc)

        widget = TableWindow(
            swa,
            "Add Layer",
            elm_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# Data menu slots

    @pyqtSlot()
    def on_actionWiFi_Active_triggered(self):
        print("action wifi active")
        import data_sql_query
        self.add_param_window(data_sql_query.WIFI_ACTIVE_SQL_LIST, title="WiFi Active")

    @pyqtSlot()
    def on_actionWiFi_Scan_triggered(self):
        print("action wifi scan")
        import data_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "WiFi Scan",
            data_query.get_wifi_scan_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionGPRS_EDGE_Information_triggered(self):
        print("action gprs edge info")
        import data_sql_query
        self.add_param_window(data_sql_query.GPRS_EDGE_SQL_LIST, title="GPRS/EDGE Information")

    @pyqtSlot()
    def on_actionHSDPA_Statistics_triggered(self):
        print("action hadpa statistics")
        import data_sql_query
        self.add_param_window(data_sql_query.HSDPA_STATISTICS_SQL_LIST, title="HSDPA Statistics")

    @pyqtSlot()
    def on_actionHSUPA_Statistics_triggered(self):
        print("action haupa statistics")
        import data_sql_query
        self.add_param_window(data_sql_query.HSUPA_STATISTICS_SQL_LIST, title="HSUPA Statistics")
    
    ############# Session menu slots

    @pyqtSlot()
    def on_actionVoice_Report_triggered(self):
        print("action action voice report")
        self.add_param_window("pd.read_sql('select * from pp_voice_report',dbcon)", title="Voice Report", time_list_mode=True)


    @pyqtSlot()
    def on_actionLog_To_Operator_Map_triggered(self):
        print("action action log to operator map")
        self.add_param_window("pd.read_sql('select * from pp_log_to_operator_map',dbcon)", title="Log To Operator Map", time_list_mode=True)


    @pyqtSlot()
    def on_actionShow_Polqa_Mos_Samples_triggered(self):
        print("action action show polqa mos samples")
        self.add_param_window("pd.read_sql('select * from pp_show_polqa_mos_samples',dbcon)", title="Show Polqa Mos Samples", time_list_mode=True)


    @pyqtSlot()
    def on_actionFtp_Download_triggered(self):
        print("action action ftp download")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_ftp_download',dbcon)", title="Ftp Download", time_list_mode=True)


    @pyqtSlot()
    def on_actionVoice_Dial_triggered(self):
        print("action action voice dial")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_voice_dial',dbcon)", title="Voice Dial", time_list_mode=True)


    @pyqtSlot()
    def on_actionAnswer_triggered(self):
        print("action action answer")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_answer',dbcon)", title="Answer", time_list_mode=True)


    @pyqtSlot()
    def on_actionSMS_triggered(self):
        print("action action sms")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_sms',dbcon)", title="SMS", time_list_mode=True)


    @pyqtSlot()
    def on_actionMMS_triggered(self):
        print("action action mms")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_mms',dbcon)", title="MMS", time_list_mode=True)


    @pyqtSlot()
    def on_actionFtp_Upload_triggered(self):
        print("action action ftp upload")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_ftp_upload',dbcon)", title="Ftp Upload", time_list_mode=True)


    @pyqtSlot()
    def on_actionHttp_Download_triggered(self):
        print("action action http download")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_http_download',dbcon)", title="Http Download", time_list_mode=True)


    @pyqtSlot()
    def on_actionHttp_Upload_triggered(self):
        print("action action http upload")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_http_upload',dbcon)", title="Http Upload", time_list_mode=True)


    @pyqtSlot()
    def on_actionBrowse_triggered(self):
        print("action action browse")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_browse',dbcon)", title="Browse", time_list_mode=True)


    @pyqtSlot()
    def on_actionSS_Youtube_triggered(self):
        print("action action ss youtube")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_youtube',dbcon)", title="SS Youtube", time_list_mode=True)


    @pyqtSlot()
    def on_actionPing_triggered(self):
        print("action action ping")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_ping',dbcon)", title="Ping", time_list_mode=True)


    @pyqtSlot()
    def on_actionTraceroute_triggered(self):
        print("action action traceroute")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_traceroute',dbcon)", title="Traceroute", time_list_mode=True)


    @pyqtSlot()
    def on_actionOokla_Speed_Test_triggered(self):
        print("action action ookla speed test")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_ookla_speed_test',dbcon)", title="Ookla Speed Test", time_list_mode=True)


    @pyqtSlot()
    def on_actionDropbox_Download_triggered(self):
        print("action action dropbox download")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_dropbox_download',dbcon)", title="Dropbox Download", time_list_mode=True)


    @pyqtSlot()
    def on_actionDropbox_Upload_triggered(self):
        print("action action dropbox upload")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_dropbox_upload',dbcon)", title="Dropbox Upload", time_list_mode=True)


    @pyqtSlot()
    def on_actionLine_triggered(self):
        print("action action line")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_line',dbcon)", title="Line", time_list_mode=True)


    @pyqtSlot()
    def on_actionLine_Receive_triggered(self):
        print("action action line receive")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_line_receive',dbcon)", title="Line Receive", time_list_mode=True)


    @pyqtSlot()
    def on_actionLine_Call_triggered(self):
        print("action action line call")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_line_call',dbcon)", title="Line Call", time_list_mode=True)


    @pyqtSlot()
    def on_actionLine_Call_Answer_triggered(self):
        print("action action line call answer")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_line_call_answer',dbcon)", title="Line Call Answer", time_list_mode=True)


    @pyqtSlot()
    def on_actionLine_Mo_Call_triggered(self):
        print("action action line mo call")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_line_mo_call',dbcon)", title="Line Mo Call", time_list_mode=True)


    @pyqtSlot()
    def on_actionLine_Mt_Call_triggered(self):
        print("action action line mt call")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_line_mt_call',dbcon)", title="Line Mt Call", time_list_mode=True)


    @pyqtSlot()
    def on_actionFacebook_Post_Status_triggered(self):
        print("action action facebook post status")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_facebook_post_status',dbcon)", title="Facebook Post Status", time_list_mode=True)


    @pyqtSlot()
    def on_actionFacebook_Post_Photo_triggered(self):
        print("action action facebook post photo")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_facebook_post_photo',dbcon)", title="Facebook Post Photo", time_list_mode=True)


    @pyqtSlot()
    def on_actionFacebook_Download_Photo_triggered(self):
        print("action action facebook download photo")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_facebook_download_photo',dbcon)", title="Facebook Download Photo", time_list_mode=True)       


    @pyqtSlot()
    def on_actionFacebook_Download_Feed_triggered(self):
        print("action action facebook download feed")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_facebook_download_feed',dbcon)", title="Facebook Download Feed", time_list_mode=True)


    @pyqtSlot()
    def on_actionFacebook_Video_triggered(self):
        print("action action facebook video")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_facebook_video',dbcon)", title="Facebook Video", time_list_mode=True)


    @pyqtSlot()
    def on_actionInstagram_Download_Photo_triggered(self):
        print("action action instagram download photo")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_instagram_download_photo',dbcon)", title="Instagram Download Photo", time_list_mode=True)     


    @pyqtSlot()
    def on_actionInstagram_Post_Photo_triggered(self):
        print("action action instagram post photo")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_instagram_post_photo',dbcon)", title="Instagram Post Photo", time_list_mode=True)


    @pyqtSlot()
    def on_actionInstagram_Post_Video_triggered(self):
        print("action action instagram post video")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_instagram_post_video',dbcon)", title="Instagram Post Video", time_list_mode=True)


    @pyqtSlot()
    def on_actionInstagram_Post_Comment_triggered(self):
        print("action action instagram post comment")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_instagram_post_comment',dbcon)", title="Instagram Post Comment", time_list_mode=True)


    @pyqtSlot()
    def on_actionWhats_App_Send_Message_triggered(self):
        print("action action whats app send message")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_whats_app_send_message',dbcon)", title="Whats App Send Message", time_list_mode=True)


    @pyqtSlot()
    def on_actionWhats_App_Call_triggered(self):
        print("action action whats app call")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_whats_app_call',dbcon)", title="Whats App Call", time_list_mode=True)


    @pyqtSlot()
    def on_actionSend_Email_triggered(self):
        print("action action send email")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_send_email',dbcon)", title="Send Email", time_list_mode=True)


    @pyqtSlot()
    def on_actionDns_Lookup_triggered(self):
        print("action action dns lookup")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_dns_lookup',dbcon)", title="Dns Lookup", time_list_mode=True)


    @pyqtSlot()
    def on_actionLong_Sung_Ping_triggered(self):
        print("action action long sung ping")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_long_sung_ping',dbcon)", title="Long Sung Ping", time_list_mode=True)


    @pyqtSlot()
    def on_actionVideo_triggered(self):
        print("action action video")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_video',dbcon)", title="Video", time_list_mode=True)


    @pyqtSlot()
    def on_actionNperf_Test_triggered(self):
        print("action action nperf test")
        self.add_param_window("pd.read_sql('select * from pp_statement_sum_nperf_test',dbcon)", title="Nperf Test", time_list_mode=True)

    ############# Legacy Session menu slots

    @pyqtSlot()
    def on_actiondatasession_triggered(self):
        print("action data session")
        self.add_param_window("pd.read_sql('''select * from datasession''',dbcon)", title="datasession", time_list_mode=True)

    @pyqtSlot()
    def on_actionline_mo_triggered(self):
        print("action line session")
        self.add_param_window("pd.read_sql('''select * from line_mo''',dbcon)", title="line_mo", time_list_mode=True)

    @pyqtSlot()
    def on_actionpingsession_triggered(self):
        print("action ping session")
        self.add_param_window("pd.read_sql('''select * from pingsession''',dbcon)", title="pingsession", time_list_mode=True)

    @pyqtSlot()
    def on_actionspeedtestsession_triggered(self):
        print("action speedtest session")
        self.add_param_window("pd.read_sql('''select * from speedtestsession''',dbcon)", title="speedtestsession", time_list_mode=True)

    @pyqtSlot()
    def on_actionyoutube_triggered(self):
        print("action youtube session")
        self.add_param_window("pd.read_sql('''select * from youtube''',dbcon)", title="youtube", time_list_mode=True)

    @pyqtSlot()
    def on_actionyoutube_buffer_duration_triggered(self):
        print("action youtube buffer duration session")
        self.add_param_window("pd.read_sql('''select * from youtube_buffer_duration''',dbcon)", title="youtube_buffer_duration", time_list_mode=True)


    ############# Line Chart NR

    @pyqtSlot()
    def on_actionNR_Line_Chart_triggered(self):
        print("action nr line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "nr_servingbeam_ss_rsrp_1"},
                {"name": "nr_servingbeam_ss_rsrq_1"},
                {"name": "nr_servingbeam_ss_sinr_1"},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        if self.add_subwindow_with_widget(swa, linechart_window):
            linechart_window.open()
            linechart_window.setWindowTitle("NR Line Chart")

    @pyqtSlot()
    def on_actionNR_DATA_Line_Chart_triggered(self):
        print("action nr data line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "data_trafficstat_dl/1000", "data": True},
                {"name": "data_trafficstat_ul/1000", "data": True},
                {"name": "nr_p_plus_scell_nr_pdsch_tput_mbps", "data": True},
                {"name": "nr_p_plus_scell_nr_pusch_tput_mbps", "data": True},
                {"name": "nr_p_plus_scell_lte_dl_pdcp_tput_mbps", "data": True},
                {"name": "nr_p_plus_scell_lte_ul_pdcp_tput_mbps", "data": True},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle("NR Data Line Chart")

    ############# Line Chart LTE

    @pyqtSlot()
    def on_actionLTE_Line_Chart_triggered(self):
        print("action lte line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "lte_sinr_1"},
                {"name": "lte_inst_rsrp_1"},
                {"name": "lte_inst_rsrq_1"},
                {"name": "lte_inst_rssi_1"},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle("LTE Line Chart")

    @pyqtSlot()
    def on_actionLTE_DATA_Line_Chart_triggered(self):
        print("action lte data line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "data_trafficstat_dl/1000", "data": True},
                {"name": "data_trafficstat_ul/1000", "data": True},
                {"name": "lte_l1_throughput_mbps_1", "data": True},
                {"name": "lte_bler_1", "data": True},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle("LTE Data Line Chart")

    ############# Line Chart WCDMA

    @pyqtSlot()
    def on_actionWCDMA_Line_Chart_triggered(self):
        print("action wcdma line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "wcdma_aset_ecio_avg"},
                {"name": "wcdma_aset_rscp_avg"},
                {"name": "wcdma_rssi"},
                {"name": "wcdma_bler_average_percent_all_channels"},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle("WCDMA Line Chart")

    @pyqtSlot()
    def on_actionWCDMA_DATA_Line_Chart_triggered(self):
        print("action wcdma data line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "data_wcdma_rlc_dl_throughput", "data": True},
                {"name": "data_app_dl_throughput_1", "data": True},
                {"name": "data_hsdpa_thoughput", "data": True},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle("WCDMA Data Line Chart")

    ############# Line Chart GSM

    @pyqtSlot()
    def on_actionGSM_Line_Chart_triggered(self):
        print("action gsm line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "gsm_rxlev_sub_dbm"},
                {"name": "gsm_rxqual_sub"},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle("GSM Line Chart")

    @pyqtSlot()
    def on_actionGSM_DATA_Line_Chart_triggered(self):
        print("action gsm data line chart")
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=[
                {"name": "data_gsm_rlc_dl_throughput", "data": True},
                {"name": "data_app_dl_throughput_1", "data": True},
            ],
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle("GSM Data Line Chart")


    def add_subwindow_with_widget(self, swa, widget, w=280, h=250, allow_no_log_opened=False):
        if allow_no_log_opened == False:
            if self.gc.db_fp is None or os.path.isfile(self.gc.db_fp) == False:
                qt_utils.msgbox(msg="Please open a log first", title="Log not opened", parent=self)
                return False
        swa.setWidget(widget)
        self.mdi.addSubWindow(swa)
        if w and h:
            swa.resize(w, h)
        swa.show()
        self.gc.openedWindows.append(widget)
        return True

    def status(self, msg):
        self.ui.statusbar.showMessage(msg)

    def setupUi(self):
        self.ui = loadUi(azq_utils.get_module_fp("main_window.ui"), self)
        self.toolbar = self.ui.toolBar
        self.ui.statusbar.showMessage("Please open a log to start...")
        try:
            self.mdi = self.ui.mdi
            self.gc.mdi = self.mdi
            dirname = os.path.dirname(__file__)
            self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))

            # Time Slider
            self.gc.timeSlider = timeSlider(self, self.gc)
            self.gc.timeSlider.setToolTip(
                "<b>Time Bar</b><br> <i>Drag</i> to jump replay to desired time."
            )
            self.gc.timeSlider.setMinimumWidth(100)
            self.gc.timeSlider.setMaximumWidth(360)
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(
                self.gc.timeSlider.sizePolicy().hasHeightForWidth()
            )
            self.gc.timeSlider.setSizePolicy(sizePolicy)
            from PyQt5 import QtCore

            self.gc.timeSlider.setBaseSize(QtCore.QSize(500, 0))
            self.gc.timeSlider.setPageStep(1000)  # 1 second for pageup/down, use neg for pgup to go backwards
            self.gc.timeSlider.setSingleStep(100)  # 1 second for pageup/down
            self.gc.timeSlider.setInvertedControls(True)  # so pageup would go to past, pagedown would go to future time
            self.gc.timeSlider.setSliderPosition(0)
            self.gc.timeSlider.setOrientation(QtCore.Qt.Horizontal)
            self.gc.timeSlider.setObjectName("timeSlider")
            self.gc.timeSlider.setTracking(True)
            self.gc.timeSlider.setToolTip(
                "Use 'PgUp/PgDn' keys to move 1 second, use arrow keys to move 100 milliseconds - when selected."
            )

            # Play Speed Textbox
            self.speedLabel = QLabel(self)
            self.speedLabel.setGeometry(QtCore.QRect(480, 82, 40, 22))
            self.speedLabel.setObjectName("Speed")
            self.playSpeed = QLineEdit(self)
            self.onlyDouble = QDoubleValidator(self)
            self.onlyDouble.setRange(0.0, 120.0, 2)
            self.onlyDouble.setNotation(QDoubleValidator.StandardNotation)
            self.playSpeed.setValidator(self.onlyDouble)
            self.playSpeed.setMaximumWidth(50)
            self.playSpeed.setFixedWidth(60)

            self.playSpeed.textChanged.connect(self.setPlaySpeed)

            # Datetime Textbox
            self.timeEdit = QDateTimeEdit(self)
            self.timeEdit.setGeometry(QtCore.QRect(480, 56, 140, 22))
            self.timeEdit.setObjectName("timeEdit")
            self.timeEdit.setDisplayFormat("hh:mm:ss.zzz")
            self.timeEdit.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
            self.timeEdit.setReadOnly(True)

            # Time label
            self.timeSliderLabel = QLabel(self)
            self.timeSliderLabel.setGeometry(QtCore.QRect(300, 30, 100, 16))
            self.timeSliderLabel.setObjectName("timeSliderLabel")

            self.setupPlayStopButton()

            # Import Database Button
            self.importDatabaseBtn = QToolButton()
            self.importDatabaseBtn.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "import.png")))
            )
            self.importDatabaseBtn.setObjectName("importDatabaseBtn")
            self.importDatabaseBtn.setToolTip(
                "<b>Open logs</b><br>Open test logs to analyze/replay its data."
            )

            # Save Button
            self.saveBtn = QToolButton()
            self.saveBtn.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "save.png")))
            )
            self.saveBtn.setObjectName("saveBtn")
            self.saveBtn.setToolTip(
                "<b>Save sqlite database</b><br>Save current current DB (spatialite) to file..."
            )

            # Map tool Button
            resourcePath = os.path.join(dirname, "res", "crosshair.png")
            self.maptool = QToolButton()
            self.maptool.setIcon(QIcon(QPixmap(resourcePath)))
            self.maptool.setToolTip(
                "<b>QGIS map select tool</b><br>Click on a QGIS map layer to do time-sync with all open analyzer windows."
            )
            self.importDatabaseBtn.setObjectName("importDatabaseBtn")


            # Layer Select Button
            self.layerSelect = QToolButton()
            self.layerSelect.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "layer.png")))
            )
            self.layerSelect.setObjectName("layerBtn")
            self.layerSelect.setToolTip(
                "<b>Load layers</b><br>Click to load additional layers from the currently opened log file into the QGIS map."
            )

            # Layer Select Button
            self.cellsSelect = QToolButton()
            self.cellsSelect.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "cells.png")))
            )
            self.cellsSelect.setObjectName("cellsBtn")
            self.cellsSelect.setToolTip(
                "<b>Load layers</b><br>Click to load cell files..."
            )

            # refresh connected phone button
            self.sync_connected_phone_button = QToolButton()
            self.sync_connected_phone_button.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "refresh.png")))
            )
            self.sync_connected_phone_button.setObjectName("sync_connected_phone_button")
            self.sync_connected_phone_button.setToolTip(
                "<b>Re-sync connected phone data</b><br>For connected phone mode..."
            )
            self.sync_connected_phone_button.setEnabled(False)

            self.gc.timeSlider.valueChanged.connect(self.timeChange)
            self.saveBtn.clicked.connect(self.saveDbAs)
            self.layerSelect.clicked.connect(self.on_button_selectLayer)
            self.cellsSelect.clicked.connect(self.selectCells)
            self.importDatabaseBtn.clicked.connect(self.open_logs)
            self.maptool.clicked.connect(self.setMapTool)
            self.sync_connected_phone_button.clicked.connect(self.sync_connected_phone)
            self.setupToolBar()

            self.setWindowTitle(
                "AZENQOS Log Replay & Analyzer tool      v.%.03f" % VERSION
            )
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: setupUi failed - exception: {}".format(exstr))

    def setupToolBar(self):
        self.toolbar.setFloatable(True)
        self.toolbar.setMovable(True)
        self.toolbar.addWidget(self.importDatabaseBtn)
        self.toolbar.addWidget(self.saveBtn)
        self.toolbar.addWidget(self.maptool)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.layerSelect)
        self.toolbar.addWidget(self.cellsSelect)
        self.toolbar.addWidget(self.sync_connected_phone_button)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.timeSliderLabel)
        self.toolbar.addWidget(self.playButton)
        self.toolbar.addWidget(self.pauseButton)
        self.toolbar.addWidget(self.gc.timeSlider)
        self.toolbar.addWidget(self.timeEdit)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.speedLabel)
        self.toolbar.addWidget(self.playSpeed)


    def clear_highlights(self):
        if self.qgis_iface and self.gc.highlight_list:
            for h in self.gc.highlight_list:
                self.qgis_iface.mapCanvas().scene().removeItem(h)
            self.gc.highlight_list.clear()


    def selectChanged(self):
        self.clear_highlights()
        canvas = self.qgis_iface.mapCanvas()
        layer = self.qgis_iface.activeLayer()
        if not layer:
            return False
        if layer.type() == layer.VectorLayer:
            i = -1
            for sf in layer.selectedFeatures():
                i += 1
                print("selectChanged selectedfeature rect sf i:", i, sf)
                h = QgsHighlight(canvas, sf.geometry(), layer)
                # set highlight symbol properties
                h.setColor(QColor(0, 0, 0, 255))
                h.setWidth(3)
                self.gc.highlight_list.append(h)
                canvas.flashFeatureIds(layer, layer.selectedFeatureIds(), flashes=1)
                break



    def updateUi(self):
        if not self.gc.slowDownValue == 1:
            self.playSpeed.setText("{:.2f}".format(self.gc.slowDownValue))
        elif not self.gc.fastForwardValue == 1:
            self.playSpeed.setText("{:.2f}".format(self.gc.fastForwardValue))
        else:
            self.playSpeed.setText("{:.2f}".format(1))
        print("updateui self.gc.currentTimestamp", self.gc.currentTimestamp)
        if self.gc.currentTimestamp:
            self.timeEdit.setDateTime(
                datetime.datetime.fromtimestamp(self.gc.currentTimestamp)
            )
        
        

    def setPlaySpeed(self, value):
        value = float(1) if value == "" else float(value)
        if value >= float(1):
            self.gc.fastForwardValue = value
            self.gc.slowDownValue = 1
        elif value == float(0):
            self.gc.fastForwardValue = 1
            self.gc.slowDownValue = 1
        elif value < float(1):
            self.gc.fastForwardValue = 1
            self.gc.slowDownValue = value

    def setupPlayStopButton(self):
        self.horizontalLayout = QWidget(self)
        self.horizontalLayout.setGeometry(QtCore.QRect(290, 70, 90, 48))
        self.playButton = QToolButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.setToolTip(
            "<b>Play</b><br><i>Start</i> or <i>Resume</i> log replay."
        )
        self.pauseButton = QToolButton()
        self.pauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pauseButton.setToolTip("<b>Pause</b><br> <i>Pause</i> log replay")
        layout = QHBoxLayout(self.horizontalLayout)
        layout.addStretch(1)
        layout.addWidget(self.playButton)
        layout.addWidget(self.pauseButton)
        self.playButton.clicked.connect(self.startPlaytimeThread)
        self.pauseButton.clicked.connect(self.pauseTime)

    def startPlaytimeThread(self):
        print("%s: startPlaytimeThread" % os.path.basename(__file__))
        print("self.gc.sliderLength {}".format(self.gc.sliderLength))
        print("self.gc.minTimeValue {}".format(self.gc.minTimeValue))
        print("self.gc.maxTimeValue {}".format(self.gc.maxTimeValue))
        print(
            "self.timeSliderThread.getCurrentValue()",
            self.timeSliderThread.getCurrentValue(),
        )
        print("self.gc.sliderLength", self.gc.sliderLength)
        if self.timeSliderThread.getCurrentValue() < self.gc.sliderLength:
            self.gc.isSliderPlay = True
            self.playButton.setDisabled(True)
            self.playSpeed.setDisabled(True)
            self.timeSliderThread.changeValue.connect(self.setTimeValue)
            self.timeSliderThread.start()

    def setMapTool(self):
        self.canvas.setMapTool(self.clickTool)

    def on_button_selectLayer(self):
        self.on_actionAdd_Layer_triggered()

    def selectCells(self):
        if self.qgis_iface:

            fileNames, _ = QFileDialog.getOpenFileNames(
                self, "Select cell files", QtCore.QDir.rootPath(), "*.*"
            )

            if fileNames:
                try:
                    import azq_cell_file
                    azq_cell_file.check_cell_files(fileNames)
                    self.gc.cell_files = fileNames
                except Exception as e:
                    qt_utils.msgbox("Failed to load the sepcified cellfiles:\n\n{}".format(str(e)),
                                    title="Invalid cellfiles", parent=self)
                    self.gc.cell_files = []
                    return
            else:
                return
            assert self.gc.cell_files
            self.add_cell_layers()  # this will set cellfiles
            if self.gc.db_fp:
                self.add_spider_layer()
            else:
                pass
                # qt_utils.msgbox("No log opened", title="Please open a log first", parent=self)
                # return

    def pauseTime(self):
        self.gc.timeSlider.setEnabled(True)
        self.playButton.setEnabled(True)
        self.playSpeed.setEnabled(True)
        self.timeSliderThread.quit()
        threading.Event()
        self.gc.isSliderPlay = False

    def setTimeValue(self, value):
        print("%s: setTimeValue %s" % (os.path.basename(__file__), value))
        print(value)
        self.gc.timeSlider.setValue(value)
        print("mw self.gc.timeSlider.value()", self.gc.timeSlider.value())
        self.gc.timeSlider.update()
        if value >= self.gc.sliderLength:
            self.pauseTime()

    def task_done_slot(self, msg):
        print("main_window task_done_slot msg:", msg)
        if msg == "cell_layer_task.py":
            self.cell_layer_task.add_layers_from_ui_thread()
        elif msg == "db_layer_task.py":
            self.db_layer_task.add_layers_from_ui_thread()


    def ui_thread_emit_time_slider_updated(self, timestamp):
        print("ui_thread_emit_time_slider_updated")
        import datetime
        sampledate = datetime.datetime.fromtimestamp(timestamp)
        self.timeEdit.setDateTime(sampledate)


    def clickCanvas(self, point, button):
        print("clickCanvas start")
        layerData = []
        selected_time = None
        selected_log_hash = None
        selected_posid = None
        selected_seqid = None
        selected_lat = None
        selected_lon = None
        try:
            self.clearAllSelectedFeatures()
        except:
            pass
        qgis_selected_layers = self.qgis_iface.layerTreeView().selectedLayers()
        print("qgis_selected_layers: ", qgis_selected_layers)
        for layer in qgis_selected_layers:
            if not layer:
                continue
            if layer.type() == layer.VectorLayer:
                if layer.featureCount() == 0:
                    # There are no features - skip
                    continue
                print("layer.name()", layer.name())
                # Loop through all features in a rect near point xy
                offset_meters = 300
                offset = azq_cell_file.METER_IN_WGS84 * offset_meters
                if self.is_legacy_indoor:
                    offset = 0.01
                p1 = QgsPointXY(point.x() - offset, point.y() - offset)
                p2 = QgsPointXY(point.x() + offset, point.y() + offset)
                rect = QgsRectangle(p1, p2)
                nearby_features = layer.getFeatures(rect)
                layer_fields = layer.fields()
                has_seqid = "seqid" in layer_fields.names()
                has_posid = "posid" in layer_fields.names()
                has_log_hash = "log_hash" in layer_fields.names()

                ########## fitler for one nearest feature only - faster way
                from qgis._core import QgsSpatialIndex
                spIndex = QgsSpatialIndex()  # create spatial index object
                feat = QgsFeature()
                # insert features to index
                for f in nearby_features:
                    spIndex.insertFeature(f)
                # QgsSpatialIndex.nearestNeighbor (QgsPoint point, int neighbors)
                nearestIds = spIndex.nearestNeighbor(point, 1)  # we need only one neighbour
                if not len(nearestIds):
                    continue
                featureId = nearestIds[0]
                fit2 = layer.getFeatures(QgsFeatureRequest().setFilterFid(featureId))
                ftr = QgsFeature()
                fit2.nextFeature(ftr)
                closestFeatureId = featureId
                #############################

                try:
                    feature = layer.getFeature(closestFeatureId)
                    attrs = feature.attributes()
                    print("attrs:", attrs)
                    time = feature.attribute("time")
                    log_hash = None
                    posid = None
                    seqid = None
                    lat = None
                    lon = None
                    try:
                        fpoint = layer.getFeature(closestFeatureId).geometry().asPoint()
                        lat = fpoint.y()
                        lon = fpoint.x()
                        if has_log_hash:
                            log_hash = layer.getFeature(closestFeatureId).attribute("log_hash")
                        if has_posid:
                            posid = layer.getFeature(closestFeatureId).attribute("posid")
                        if has_seqid:
                            seqid = layer.getFeature(closestFeatureId).attribute("seqid")
                    except:
                        # in case this layer added by user and no 'log_hash' col
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print("WARNING: clickoncanvas closestFeatureId inner attribute exception: {}".format(exstr))
                    info = (layer, closestFeatureId, time, log_hash, posid, seqid, lat, lon)
                    layerData.append(info)
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: clickoncanvas closestFeatureId attribute exception: {}".format(exstr))


        print("len(layerData) n nearest features:", len(layerData))
        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            return

        for (layer, closestFeatureId, time, log_hash, posid, seqid, lat, lon) in layerData:
            layer.select(closestFeatureId)
            selected_time = time
            selected_log_hash = log_hash
            selected_posid = posid
            selected_seqid = seqid
            selected_lat = lat
            selected_lon = lon
            break  # break on first one

        selectedTimestamp = None
        selectedTimestamp = azq_utils.datetimeStringtoTimestamp(selected_time)
        if selectedTimestamp:
            timeSliderValue = self.gc.sliderLength - (
                self.gc.maxTimeValue - selectedTimestamp
            )
            self.gc.timeSlider.setValue(timeSliderValue)
            self.gc.timeSlider.update()

            single_point_match_dict = {
                "log_hash": selected_log_hash,
                "posid": selected_posid,
                "seqid": selected_seqid,
                "time": selected_time,
                "selected_lat": selected_lat,
                "selected_lon": selected_lon,
            }
            self.gc.selected_point_match_dict = single_point_match_dict
            # self.canvas.refreshself.gc.tableList()

            # draw cell
            ori_active_layer = None
            try:
                ori_active_layer = self.gc.qgis_iface.activeLayer()
            except:
                pass

            if self.gc.cell_files:
                print("single_point_match_dict:", single_point_match_dict)
                options_dict = {"distance_limit_m": int(self.gc.pref["point_to_site_match_max_distance_meters"])}
                freq_code_match_mode = self.gc.pref["point_to_site_serving_match_cgi"] == "0"
                pref_key = "cell_{}_sector_size_meters".format("lte")
                sector_size_meters = float(self.gc.pref[pref_key])
                options_dict["sector_size_meters"] = sector_size_meters

                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "nr", single_point_match_dict=single_point_match_dict,
                                            plot_spider_param="nr_servingbeam_pci_1",
                                            freq_code_match_mode=freq_code_match_mode, options_dict=options_dict)
                for i in range(3):
                    spider_plot.plot_rat_spider(
                        self.gc.cell_files, self.gc.databasePath, "nr",
                        single_point_match_dict=single_point_match_dict,
                        plot_spider_param= "nr_detectedbeam{}_pci_1".format(i+1),
                        freq_code_match_mode=True,  # neigh cant use cgi mode as cgi in sib1 is of serving
                        dotted_lines=True,
                        options_dict=options_dict
                    )

                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "lte", single_point_match_dict=single_point_match_dict,
                                            plot_spider_param="lte_physical_cell_id_1",
                                            freq_code_match_mode=freq_code_match_mode, options_dict=options_dict)
                for i in range(3):
                    spider_plot.plot_rat_spider(
                        self.gc.cell_files, self.gc.databasePath, "lte",
                        single_point_match_dict=single_point_match_dict,
                        plot_spider_param="lte_neigh_physical_cell_id_{}".format(i+1),
                        freq_code_match_mode=True,  # neigh cant use cgi mode as cgi in sib1 is of serving
                        dotted_lines=True,
                        options_dict=options_dict
                    )

                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "wcdma", single_point_match_dict=single_point_match_dict,
                                            plot_spider_param="wcdma_aset_sc_1",
                                            freq_code_match_mode=freq_code_match_mode, options_dict=options_dict)
                for i in range(3):
                    spider_plot.plot_rat_spider(
                        self.gc.cell_files, self.gc.databasePath, "wcdma",
                        single_point_match_dict=single_point_match_dict,
                        plot_spider_param="wcdma_mset_sc_{}".format(i+1),
                        freq_code_match_mode=True,  # neigh cant use cgi mode as cgi in sib1 is of serving
                        dotted_lines=True,
                        options_dict=options_dict
                    )

                spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, "gsm", single_point_match_dict=single_point_match_dict,
                                            plot_spider_param="gsm_bsic",
                                            freq_code_match_mode=freq_code_match_mode, options_dict=options_dict)
                for i in range(3):
                    spider_plot.plot_rat_spider(
                        self.gc.cell_files, self.gc.databasePath, "gsm",
                        single_point_match_dict=single_point_match_dict,
                        plot_spider_param="gsm_neighbor_bsic_{}".format(i+1),
                        freq_code_match_mode=True,  # neigh cant use cgi mode as cgi in sib1 is of serving
                        dotted_lines=True,
                        options_dict=options_dict
                    )

            if ori_active_layer is not None:
                self.gc.qgis_iface.setActiveLayer(ori_active_layer)

        print("clickCanvas done")


    def loadAllMessages(self):
        getSelected = self.presentationTreeWidget.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            if baseNode.text(0) is not None:
                getChildNode = baseNode.text(0)
                getParentNode = baseNode.parent().text(0)
                self.classifySelectedItems(getParentNode, getChildNode)


    def sync_connected_phone(self):
        print("sync_connecter_phone START")
        if not (self.gc.log_mode and self.gc.log_mode == "adb"):
            qt_utils.msgbox("This button is for re-sync data from phone in 'Connected phone mode' (chosen in 'Open logs') only.", "Not in 'Connected phone mode'", parent=self)
            return
        self.open_logs(connected_mode_refresh=True, ask_close_all_layers=False)
        print("sync_connecter_phone DONE")


    def open_logs(self, connected_mode_refresh=False, ask_close_all_layers=True):
        if self.gc.databasePath:
            self.gc.databasePath = None
            self.gc.db_fp = None
            if ask_close_all_layers:
                reply = qt_utils.ask_yes_no(None, "Open log", "Close all layers?")
                print("reply", reply)
                self.close_all_layers = False
                if reply == 0:
                    self.close_all_layers = True
            self.cleanup()
            '''
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Log already open")
            if self.qgis_iface is not None:
                msgBox.setText("To open a new log, click on the AZENQOS QGIS plugin icon/menu to close this and start a new session...")
            else:
                msgBox.setText("To open a new log, please close/exit first...")
            msgBox.addButton(QPushButton("OK"), QMessageBox.YesRole)
            msgBox.exec_()            
            return
            '''
        dlg = import_db_dialog.import_db_dialog(self, self.gc, connected_mode_refresh=connected_mode_refresh)
        dlg.show()
        ret = dlg.exec()
        print("import_db_dialog ret: {}".format(ret))
        if self.gc.log_mode == "adb":
            self.sync_connected_phone_button.setEnabled(True)
        else:
            self.sync_connected_phone_button.setEnabled(False)
        if not self.gc.databasePath:
            # dialog not completed successfully
            return
        if self.gc.db_fp and self.qgis_iface:
            print("starting layertask")
            if self.close_all_layers:
                self.add_map_layer()
            self.add_spider_layer()
            self.add_indoor_map_layers()
            self.add_cell_layers()
            self.add_db_layers()
        else:
            print("log not opened")
            return

        if self.gc.sliderLength:
            self.gc.timeSlider.setRange(0, self.gc.sliderLength)
        if self.gc.databasePath:
            self.load_current_workspace()
            self.ui.statusbar.showMessage(
                "Opened log db: {}".format(self.gc.databasePath)
            )
            if connected_mode_refresh:
                if self.gc.sliderLength:
                    self.gc.timeSlider.setValue(self.gc.sliderLength - 1)
        else:
            self.ui.statusbar.showMessage("Log not opened...")
        self.updateUi()
        self.is_leg_nr_tables = preprocess_azm.is_leg_nr_tables()

    def timeChange(self):
        self.gc.selected_row_log_hash = None  # this change comes from the timeslider so set selected_row_log_hash to None
        ret = self.timechange_to_service_counter.inc_and_get()
        print(
            "%s: timeChange: timechange_to_service_counter: %d"
            % (os.path.basename(__file__), ret)
        )

    def timeChangedWorkerFunc(self):
        print("timeChangedWorkerFunc START")
        while True:
            try:
                if self.closed:
                    break
                ret = self.timechange_to_service_counter.get()
                # print(print("timeChangedWorkerFunc : {}", ret))
                if ret > 1:
                    self.timechange_to_service_counter.dec_and_get()
                    continue  # skip until we remain 1 then do work
                if ret == 1:
                    print(
                        "%s: timeChangedWorkerFunc: timechange_to_service_counter: %d so calling timeChangeImpl() START"
                        % (os.path.basename(__file__), ret)
                    )
                    try:
                        self.timeChangeImpl()
                    except:
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print("WARNING: timeChangeImpl - exception: {}".format(exstr))
                    print(
                        "%s: timeChangedWorkerFunc: timechange_to_service_counter: %d so calling timeChangeImpl() END"
                        % (os.path.basename(__file__), ret)
                    )
                    ret = self.timechange_to_service_counter.dec_and_get()
                # print("%s: timeChangedWorkerFunc: timechange_to_service_counter: %d" % (os.path.basename(__file__), ret))
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: timeChangedWorkerFunc - exception: {}".format(exstr))
            # print("{}: timeChangedWorkerFunc thread self.gc.threadpool.maxThreadCount() {} self.gc.threadpool.activeThreadCount() {}".format(os.path.basename(__file__), self.gc.threadpool.maxThreadCount(),  self.gc.threadpool.activeThreadCount()))
            time.sleep(0.1)

        print("timeChangedWorkerFunc END")

    def timeChangeImpl(self):
        print("%s: timeChange0" % os.path.basename(__file__))
        value = self.gc.timeSlider.value()
        print(value)
        # print("%s: timeChange1" % os.path.basename(__file__))
        timestampValue = self.gc.minTimeValue + value
        print(timestampValue)
        # print("%s: timeChange2" % os.path.basename(__file__))
        sampledate = datetime.datetime.fromtimestamp(timestampValue)
        # print("%s: timeChange3" % os.path.basename(__file__))
        # print("%s: timeChange4" % os.path.basename(__file__))
        self.timeSliderThread.set(value)
        # print("%s: timeChange5" % os.path.basename(__file__))
        self.gc.currentTimestamp = timestampValue
        # print("%s: timeChange6" % os.path.basename(__file__))
        self.gc.currentDateTimeString = "%s" % (
            datetime.datetime.fromtimestamp(self.gc.currentTimestamp).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]
        )
        # print("%s: timeChange7" % os.path.basename(__file__))
        # print("signal_ui_thread_emit_time_slider_updated.emit()")
        self.signal_ui_thread_emit_time_slider_updated.emit(self.gc.currentTimestamp)

        self.hilightFeature()

        opened_windows = list(self.gc.mdi.subWindowList())
        print("%s: timeChange8" % os.path.basename(__file__), "len(opened_windows): ", len(opened_windows))
        #TODO port gc.openedWindows later because lower parts still exception - self.gc.openedWindows = opened_windows
        if len(self.gc.openedWindows) > 0:
            for window in self.gc.openedWindows:
                is_visible = False
                try:
                    is_visible = window.isVisible()  # handle c++ window deleted runtime error
                except:
                    pass
                if not is_visible:
                    print("window {} not visible so omit".format(window))
                    continue
                if isinstance(window, linechart_custom.LineChart):
                    window.updateTime(sampledate)
                elif isinstance(window, linechart_multi_y_axis.LineChart):
                    window.updateTime(sampledate)
                elif not window.title in self.gc.linechartWindowname:
                    print(
                        "%s: timeChange7 hilightrow window %s"
                        % (os.path.basename(__file__), window.title)
                    )
                    window.hilightRow(sampledate)
                else:
                    print(
                        "%s: timeChange7 movechart window %s"
                        % (os.path.basename(__file__), window.title)
                    )
                    window.moveChart(sampledate)
        print("%s: timeChange9" % os.path.basename(__file__))
        # text = "[--" + str(len(self.gc.tableList) + "--]"
        # QgsMessageLog.logMessage(text)

        print(
            "{}: timeChange end1 self.gc.threadpool.maxThreadCount() {} self.gc.threadpool.activeThreadCount() {}".format(
                os.path.basename(__file__),
                self.gc.threadpool.maxThreadCount(),
                self.gc.threadpool.activeThreadCount(),
            )
        )


    def hilightFeature(self):
        try:
            self.selectFeatureOnLayersByTime()
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: selectFeatureOnLayersByTime from hilightFeature exception: {}".format(
                    exstr
                )
            )


    def selectFeatureOnLayersByTime(self):
        if self.qgis_iface is None:
            return
        qgis_selected_layers = self.qgis_iface.layerTreeView().selectedLayers()
        for layer in qgis_selected_layers:
            try:
                print("selectFeatureOnLayersByTime layer: %s" % layer.name())
                layer.removeSelection()
                end_dt = datetime.datetime.fromtimestamp(self.gc.currentTimestamp)
                start_dt = end_dt - datetime.timedelta(
                    seconds=10.0
                )
                # 2020-10-08 15:35:55.431000
                filt_expr = ""
                if self.gc.selected_row_log_hash:
                    filt_expr = "log_hash = {} and ".format(self.gc.selected_row_log_hash)
                filt_expr += "time >= '%s' and time <= '%s'" % (start_dt, end_dt)
                print("filt_expr:", filt_expr)
                layerFeatures = list(layer.getFeatures(QgsFeatureRequest().setFilterExpression(filt_expr).setFlags(QgsFeatureRequest.NoGeometry)))
                print("filt request ret len:", len(layerFeatures))
                lc = 0
                fids = []
                time_list = []
                for lf in layerFeatures:
                    lc += 1
                    fids.append(lf.id())
                    lft = lf.attribute("time")
                    print("ltf0: {} type: {}".format(lft, type(lft)))  # - sometimes comes as qdatetime we cant add
                    if isinstance(lft, str):
                        print("ltf1: {} type: {}".format(lft, type(lft)))#  - sometimes comes as qdatetime we cant add
                        time_list.append(lft)
                    if isinstance(lft, PyQt5.QtCore.QDateTime):
                        print("ltf2: {} type: {}".format(lft, type(lft)))  # - sometimes comes as qdatetime we cant add
                        time_list.append(lft.toMSecsSinceEpoch())

                if len(fids) and len(time_list):
                    print("time_list: {}".format(time_list))
                    sr = pd.Series(time_list, index=fids, dtype="datetime64[ns]")
                    sids = [sr.idxmax()]
                    print("sr:", sr)
                    print("select ids:", sids)
                    layer.selectByIds(sids)
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print(
                    "WARNING: selectFeatureOnLayersByTime layer.name() {} exception: {}".format(
                        layer.name(), exstr
                    )
                )


    def loadWorkspaceFile(self):
        print("loadFile()")
        fp, _ = QFileDialog.getOpenFileName(
            self, "Open workspace file", QtCore.QDir.rootPath(), "*.ini"
        )
        if fp:
            print("loadWorkspaceFile:", fp)
            if len(self.gc.openedWindows) > 0:
                for mdiwindow in self.mdi.subWindowList():
                    mdiwindow.close()
                self.gc.openedWindows = []
            shutil.copyfile(fp, azq_utils.get_settings_fp(CURRENT_WORKSPACE_FN))
            self.current_workspace_settings.sync()  # load changes
            self.load_current_workspace()
            self.current_workspace_settings.sync()

    def saveWorkspaceFile(self):
        from PyQt5 import QtCore

        fp, _ = QFileDialog.getSaveFileName(
            self, "Save workspace file", QtCore.QDir.rootPath(), "*.ini"
        )
        if fp:
            print("saveWorkspaceFile:", fp)
            self.save_current_workspace()
            self.current_workspace_settings.sync()  # save changes
            shutil.copyfile(azq_utils.get_settings_fp(CURRENT_WORKSPACE_FN), fp)


    def saveDbAs(self):
        if not self.gc.db_fp:
            qt_utils.msgbox("No log opened", title="Please open a log first", parent=self)
            return
        from PyQt5 import QtCore
        fp, _ = QFileDialog.getSaveFileName(
            self, "Save current DB file as", QtCore.QDir.rootPath(), "*.db"
        )
        if fp:
            print("saveDbAs:", fp)
            ret = shutil.copyfile(self.gc.db_fp, fp)
            qt_utils.msgbox("File saved: {}".format(ret), parent=self)


    def closeEvent(self, event):
        print("analyzer_window: closeEvent:", event)
        # just close it as it might be ordered by qgis close (unload()) too
        self.close()
        event.accept()


    def cleanup(self):
        try:
            self.save_current_workspace()
            self.pauseTime()

            # remove selected features:
            self.clear_highlights()

            # Begin removing layers
            if self.qgis_iface:
                project = QgsProject.instance()
                '''
                for (id_l, layer) in project.mapLayers().items():
                    if layer.type() == layer.VectorLayer:
                        print("vlayer: rm sel", layer.name)
                        layer.removeSelection()
                    to_be_deleted = project.mapLayersByName(layer.name())[0]
                    project.removeMapLayer(to_be_deleted.id())
                    del layer
                '''
                
                if self.close_all_layers:
                    project.removeAllMapLayers()
                    project.clear()
                else:
                    for layer in project.mapLayers().values():
                        if layer.name() == "OSM":
                            # project.removeMapLayer(project.mapLayersByName(layer.name())[0].id())
                            continue
                        new_layer_name = layer.name()+"_old"
                        layer.setName(new_layer_name)

            print("cleanup: len(self.gc.openedWindows)", len(self.gc.openedWindows))
            for widget in self.gc.openedWindows:
                print("closing widget title:", widget.title)
                try:
                    widget.close()
                except Exception as e:
                    print("WARNING: widget.close() exception:", e)

            self.gc.openedWindows = []
            for window in self.mdi.subWindowList():
                try:
                    window.close()
                except Exception as e:
                    print("WARNING: widget.close() exception:", e)
            assert len(self.mdi.subWindowList()) == 0
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: cleanup() exception:", exstr)


    def close(self):
        try:
            self.cleanup()
            # End removing layer
            self.removeAzenqosGroup()
            for mdiwindow in self.mdi.subWindowList():
                print("mdiwindow close ", mdiwindow)
                mdiwindow.close()
            self.mdi.close()
            azq_utils.close_scrcpy_proc()
            print("Close App")
            azq_utils.adb_kill_server_threaded()  # otherwise cant update plugin as adb files would be locked
            self.closed = True
            print("cleanup() done")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: close() exception:", exstr)

    def removeToolBarActions(self):
        actions = self.toolbar.actions()
        for action in actions:
            self.toolbar.removeAction(action)


    def clearAllSelectedFeatures(self):
        if self.qgis_iface:
            layer = self.qgis_iface.activeLayer()
            if layer:
                layer.removeSelection()
            self.clear_highlights()


    def removeAzenqosGroup(self):
        if self.qgis_iface:
            root = QgsProject.instance().layerTreeRoot()
            azqGroup = root.findGroup("Azenqos")
            if azqGroup:
                root.removeChildNode(azqGroup)


    def set_project_crs(self):
        if self.qgis_iface:
            print("setting project crs")
            my_crs = QgsCoordinateReferenceSystem(4326)
            QgsProject.instance().setCrs(my_crs)
            self.crs_already_set = True

    def on_layers_added(self, layers):
        if layers is None:
            return
        print('on_layers_added start len:', len(layers))
        for layer in layers:
            name = layer.name()
            import system_sql_query
            #if name in system_sql_query.rat_to_main_param_dict.values():
            if self.gc.qgis_iface.activeLayer() is not None:
                pass
            print("renamingLayers layer:", name)
            if "azqdata " in name:
                try:
                    param = name.split("azqdata ")[1]
                    layer.setName(param)
                except Exception as e:
                    print("WARNING: renaming layers exception: {}".format(e))



    '''
    -
    
    if name[0] == "azqdata":
        -
    -  # Handle duplicate layers
    -
    if " ".join(name[1:]) in self.gc.activeLayers:
        -                    toBeRemoved = QgsProject.instance().mapLayersByName(
            -                        " ".join(name[1:])
            -)
    -
    if len(toBeRemoved) > 0:
        -                        QgsProject.instance().removeMapLayer(toBeRemoved[0])
    -                        self.gc.activeLayers.remove(" ".join(name[1:]))
    -
    -  # Setting up layer data source
    -                layer.setName(" ".join(name[1:]))
    -                self.gc.activeLayers.append(" ".join(name[1:]))
    -  # uri.setDataSource("", " ".join(name[1:]), geom_column)
    -  # layer.setDataSource(uri.uri(), " ".join(name[1:]), "spatialite")
    -
    -  # Force adding layer to root node
    -  # cloneLayer = layer.clone()
    -  # root.insertChildNode(0, cloneLayer)
    -
    pass
    '''

    def save_current_workspace(self):
        # mod from https://stackoverflow.com/questions/23279125/python-pyqt4-functions-to-save-and-restore-ui-widget-values
        """
        save "ui" controls and values to registry "setting"
        :return:
        """
        try:
            print("save_current_workspace() START")
            print("save_current_workspace() geom")
            self.current_workspace_settings.setValue(
                GUI_SETTING_NAME_PREFIX + "geom", self.saveGeometry()
            )
            print("save_current_workspace() state")
            self.current_workspace_settings.setValue(GUI_SETTING_NAME_PREFIX + "state", self.saveState())

            swl = self.mdi.subWindowList()
            swl = [w for w in swl if (w is not None and w.widget() is not None)]
            print(
                "save_current_workspace() len(swl)",
                len(swl),
                "len(gc.openedWindows)",
                len(self.gc.openedWindows),
            )

            if swl:
                self.current_workspace_settings.setValue(GUI_SETTING_NAME_PREFIX + "n_windows", len(swl))
                i = 0
                for window in swl:
                    # window here is a subwindow: class SubWindowArea(QMdiSubWindow)
                    try:
                        if not window.widget():
                            continue
                        print(
                            "save_current_workspace() window_{}_title".format(i), window.widget().title
                        )

                        self.current_workspace_settings.setValue(
                            GUI_SETTING_NAME_PREFIX + "window_{}_title".format(i),
                            window.widget().title,
                        )
                        self.current_workspace_settings.setValue(
                            GUI_SETTING_NAME_PREFIX + "window_{}_func_key".format(i),
                            window.widget().func_key,
                        )
                        self.current_workspace_settings.setValue(
                            GUI_SETTING_NAME_PREFIX + "window_{}_geom".format(i),
                            window.saveGeometry(),
                        )

                        if isinstance(window.widget(), TableWindow):
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_table_horizontal_headerview_state".format(i),
                                window.widget().tableView.horizontalHeader().saveState(),
                            )

                        self.current_workspace_settings.setValue(
                            GUI_SETTING_NAME_PREFIX + "window_{}_refresh_df_func_or_py_eval_str".format(i),
                            window.widget().refresh_data_from_dbcon_and_time_func,
                        )
                        self.current_workspace_settings.setValue(
                            GUI_SETTING_NAME_PREFIX + "window_{}_options".format(i),
                            json.dumps(window.widget().options),
                        )
                        i += 1
                        self.current_workspace_settings.setValue(GUI_SETTING_NAME_PREFIX + "n_windows", i)
                    except:
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print("WARNING: save_current_workspace() for window exception: {}".format(exstr))
                    # tablewindows dont have saveState() self.settings.setValue(GUI_SETTING_NAME_PREFIX + "window_{}_state".format(i), window.saveState())

            wsfp = azq_utils.get_settings_fp(CURRENT_WORKSPACE_FN)
            if os.path.isfile(wsfp):
                os.remove(wsfp)
            self.current_workspace_settings.sync()  # save to disk
            print("save_current_workspace() DONE")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: save_current_workspace() - exception: {}".format(exstr))

    def qgis_msgbar(self, title, msg):
        if self.qgis_iface:
            self.qgis_iface.messageBar().clearWidgets()
            self.qgis_iface.messageBar().pushInfo(title, msg)

    def add_db_layers(self, select=False):
        print("add_db_layers 0")
        if self.gc.db_fp:
            print("add_db_layers 2")
            self.qgis_msgbar("Creating layers", "Please wait...")
            self._create_db_layers(None)
            '''
            self.load_db_layers_task = QgsTask.fromFunction('Load db layers', self._create_db_layers,
                                                            on_finished=self._create_db_layers_done)
                                       
            print("add_db_layers 3")
            QgsApplication.taskManager().addTask(self.load_db_layers_task)
            '''
            print("add_db_layers 4")
        else:
            qt_utils.msgbox("No log opened", title="Please open a log first", parent=self)

    def _create_db_layers(self, task):
        print("_add_db_layers start")
        table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer = db_layer_task.create_layers(
            self.gc)
        obj = (table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer)
        #this was for older QgsTask.fromFunction but this always creates the QObject::setParent: Cannot set parent... although we already sent it via signales, perhaps qvectorlayer should be created in ui thread too... self.add_created_layers_signal.emit("", obj)
        self._add_created_layers(None, obj)
        print("_add_db_layers done")

    def _create_db_layers_done(self, exception, result=None):
        print("_add_db_layers_done exception: {} result: {}".format(exception, result))

    def _add_created_layers(self, signal_msg, obj):
        print("add_created_layers signal_msg:", signal_msg)
        table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer = obj
        db_layer_task.ui_thread_add_layers_to_qgis(self.gc, table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer)
        self.qgis_msgbar("Done", "Loading layers completed")
        self.trigger_zoom_to_active_layer()

    def trigger_zoom_to_active_layer(self, wait_secs=0.6):
        print("trigger_zoom_to_active_layer")
        if self.zoom_thread is None or self.zoom_thread.is_alive() == False:
            print("trigger_zoom_to_active_layer create")
            self.zoom_thread = threading.Thread(
            target=self.zoom_after_secs,
            args=(wait_secs,),
                daemon=True
            )
            self.zoom_thread.start()
        else:
            print("trigger_zoom_to_active_layer omit because already working")

    def zoom_after_secs(self, secs):
        print("zoom_after_secs wait")
        time.sleep(secs)
        print("zoom_after_secs start")
        self.signal_trigger_zoom_to_active_layer.emit("")

    def slot_trigger_zoom_to_active_layer(self, msg):
        print("slot_trigger_zoom_to_active_layer")
        self.gc.qgis_iface.zoomToActiveLayer()

    def add_map_layer(self):
        layers_names = []
        for layer in QgsProject.instance().mapLayers().values():
            layers_names.append(layer.name())
        map_layer_name = "OSM"
        if map_layer_name in layers_names:
            return  # no need to add

        urlWithParams = (
            "type=xyz&url=http://tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png"
        )
        from qgis._core import QgsRasterLayer
        rlayer = QgsRasterLayer(urlWithParams, map_layer_name, "wms")
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
        else:
            QgsMessageLog.logMessage("Invalid layer")

        if azq_utils.is_container_mode():
            # server mode login to self must work
            import integration_test_helpers
            import login_dialog
            integration_test_helpers.silent_login(self.gc, login_dialog.DOCKER_NW_SERVER_URL,
                                                  os.environ["DASHBOARD_USER"], os.environ["DASHBOARD_PASS"])
            assert self.gc.is_logged_in()


        if not self.asked_easy_mode and azq_utils.is_container_mode():
            self.asked_easy_mode = True
            reply = qt_utils.ask_yes_no(None, "Easy mode", "Start Overview/AI-Predict mode?")
            print("reply", reply)
            if reply == 0:
                self.gc.easy_overview_mode = True
                print("show server overview")
                self.on_actionServer_overview_layers_triggered()  # TODO open this year - 60 second bin
                self.on_actionServerAIPrediction_triggered()

    def add_spider_layer(self):
        import spider_plot
        import azq_cell_file
        print("add_spider_layer self.gc.cell_files:", self.gc.cell_files)
        if not self.gc.cell_files:
            return
        try:
            azq_cell_file.read_cellfiles(self.gc.cell_files, "lte", add_cell_lat_lon_sector_distance_meters=0.001)
        except Exception as e:
            qt_utils.msgbox("Failed to load the sepcified cellfiles: {}".format(str(e)), title="Invalid cellfiles", parent=self)
            return
        for rat in azq_cell_file.CELL_FILE_RATS:
            options_dict = {"distance_limit_m": int(self.gc.pref["spider_match_max_distance_meters"])}
            pref_key = "cell_{}_sector_size_meters".format(rat)
            sector_size_meters = float(self.gc.pref[pref_key])
            options_dict["sector_size_meters"] = sector_size_meters
            freq_code_match_mode = self.gc.pref["spider_match_cgi"] == "0"
            spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, rat, options_dict=options_dict, freq_code_match_mode=freq_code_match_mode)

    def add_indoor_map_layers(self):
        rotate_indoor_map_path = os.path.join(self.gc.logPath, "map_rotated.png")
        indoor_map_path = os.path.join(self.gc.logPath, "map.jpg")
        tif_map_path = os.path.join(self.gc.logPath, "map_rotated.tif")
        from PIL import Image
        is_rotate_indoor_map = False
        if os.path.isfile(rotate_indoor_map_path):
            indoor_map_path = rotate_indoor_map_path
            is_rotate_indoor_map = True
        if os.path.isfile(indoor_map_path):
            self.gc.is_indoor = True
            indoor_map_image = Image.open(indoor_map_path)
            w, h = indoor_map_image.size
            nw_lon = 0
            nw_lat = 1
            ne_lon = 1
            ne_lat = 1
            se_lon = 1
            se_lat = 0
            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                try:
                    indoor_bg_df = pd.read_sql("select * from indoor_background_img", dbcon)
                    if len(indoor_bg_df) > 0:
                        map_type = "ori"
                        if is_rotate_indoor_map:
                            map_type = "rotated"
                        nw_lon = indoor_bg_df["indoor_{}_img_north_west_lon".format(map_type)][0]
                        nw_lat = indoor_bg_df["indoor_{}_img_north_west_lat".format(map_type)][0]
                        ne_lon = indoor_bg_df["indoor_{}_img_north_east_lon".format(map_type)][0]
                        ne_lat = indoor_bg_df["indoor_{}_img_north_east_lat".format(map_type)][0]
                        se_lon = indoor_bg_df["indoor_{}_img_south_east_lon".format(map_type)][0]
                        se_lat = indoor_bg_df["indoor_{}_img_south_east_lat".format(map_type)][0]
                    else:
                        self.is_legacy_indoor = True
                except:
                    self.is_legacy_indoor = True

            os.system("gdal_translate -of GTiff -a_srs EPSG:4326 -gcp 0 0 {nw_lon} {nw_lat} -gcp {width} 0 {ne_lon} {ne_lat} -gcp {width} {height} {se_lon} {se_lat} {jpg_path} {tif_path}".format(width=w, height=h, jpg_path=indoor_map_path, tif_path=tif_map_path, nw_lon=nw_lon, nw_lat=nw_lat, ne_lon=ne_lon, ne_lat=ne_lat, se_lon=se_lon, se_lat=se_lat))
            self.qgis_iface.addRasterLayer(tif_map_path, "indoor_map")
            
        return

    def add_cell_layers(self):
        print("add_cell_layers self.gc.cell_files:", self.gc.cell_files)
        if not self.gc.cell_files:
            return
        import azq_cell_file
        try:
            azq_cell_file.read_cellfiles(self.gc.cell_files, "lte", add_cell_lat_lon_sector_distance_meters=0.001)
        except Exception as e:
            qt_utils.msgbox("Failed to load the sepcified cellfiles: {}".format(str(e)), title="Invalid cellfiles", parent=self)
            return
        if self.gc.cell_files:
            import azq_cell_file
            import azq_utils
            import cell_layer_task
            rrv = azq_cell_file.CELL_FILE_RATS.copy()
            rrv.reverse()  # by default gsm is biggest so put it at the bottom
            for rat in rrv:
                try:
                    layer_name = rat.upper() + "_cells"
                    pref_key = "cell_{}_sector_size_meters".format(rat)
                    sector_size_meters = float(self.gc.pref[pref_key])
                    df = azq_cell_file.read_cellfiles(self.gc.cell_files, rat, add_sector_polygon_wkt_sector_size_meters=sector_size_meters)
                    csv_fp = os.path.join(azq_utils.tmp_gen_path(), "cell_file_sectors_" + rat + ".csv")
                    if len(df):
                        df.to_csv(csv_fp, encoding='utf-8')
                        uri = pathlib.Path(csv_fp).as_uri()
                        uri += "?crs=epsg:4326&wktField={}".format('sector_polygon_wkt')
                        print("csv uri: {}".format(uri))
                        layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
                        try:
                            param_att_rat = {'gsm': 'bcch', 'wcdma': 'psc', 'lte': 'pci', 'nr': 'pci'}
                            param_db_rat = {'gsm': 'gsm_arfcn_bcch', 'wcdma': 'wcdma_aset_sc_1', 'lte': 'lte_physical_cell_id_1', 'nr': 'nr_servingbeam_pci_1'}
                            param_name_in_cell = param_att_rat[rat]
                            param_name_in_db = param_db_rat[rat]
                            color_range_list = []
                            param_with_color_df = cell_layer_task.cell_in_logs_with_color(self.gc.cell_files, self.gc.databasePath, rat)
                            param_with_color_df[param_name_in_db] = param_with_color_df[param_name_in_db].astype(int)
                            print(param_with_color_df)
                            fes = layer.getFeatures()
                            for fe in fes:
                                param_val_in_fe = int(fe.attribute(param_name_in_cell))
                                print(param_val_in_fe, list(param_with_color_df[param_name_in_db]))
                                if param_val_in_fe in list(param_with_color_df[param_name_in_db]):
                                    tmp_df = param_with_color_df[param_with_color_df[param_name_in_db] == param_val_in_fe].reset_index()
                                    color = tmp_df.loc[0, 'ColorXml']
                                else:
                                    color = '#666666'

                                symbol = QgsSymbol.defaultSymbol(layer.geometryType())
                                symbol.setColor(QColor(color))
                                color_per_param = QgsRendererRange(param_val_in_fe, param_val_in_fe, symbol, str(param_val_in_fe))
                                color_range_list.append(color_per_param)

                            renderer = QgsGraduatedSymbolRenderer(param_name_in_cell, color_range_list)
                            renderer.setMode(QgsGraduatedSymbolRenderer.Custom)
                            layer.setRenderer(renderer)
                        except:
                            type_, value_, traceback_ = sys.exc_info()
                            exstr = str(traceback.format_exception(type_, value_, traceback_))
                            print("WARNING: add cell file color for rat {} - exception: {}".format(rat, exstr))
                        QgsProject.instance().addMapLayers([layer])
                        pass
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: add cell file for rat {} - exception: {}".format(rat, exstr))
            return
        else:
            qt_utils.msgbox("No cell-files specified", parent=self)


    def load_current_workspace(self):
        """
        restore "ui" controls with values stored in registry "settings"
        :return:
        """
        try:
            print("load_current_workspace() START")
            self.current_workspace_settings.sync()  # load from disk
            window_geom = self.current_workspace_settings.value(GUI_SETTING_NAME_PREFIX + "geom")
            if window_geom:
                print("load_current_workspace() geom")
                self.restoreGeometry(window_geom)
            """
            state_value = self.settings.value(GUI_SETTING_NAME_PREFIX + "state")
            if state_value:
                print("load_current_workspace() state")
                self.restoreState(state_value)
            """
            n_windows = self.current_workspace_settings.value(GUI_SETTING_NAME_PREFIX + "n_windows")
            if n_windows:
                n_windows = int(n_windows)
                for i in range(n_windows):
                    try:
                        title = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_title".format(i)
                        )
                        geom = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_geom".format(i)
                        )
                        func = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_func_key".format(i)
                        )

                        hh_state = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_table_horizontal_headerview_state".format(i)
                        )

                        refresh_df_func_or_py_eval_str = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_refresh_df_func_or_py_eval_str".format(i)
                        )

                        options = json.loads(self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_options".format(i)
                        ))

                        print("load_current_workspace() window i: {} title: {} options: {}".format(i, title,
                                                                                                             options))
                        if func is not None:
                            # on..._triggered func like on L3 triggered etc
                            func_key = "self." + func + "()" 
                            print(func_key)
                            eval(func_key)
                        else:
                            # like for custom windows - newer style
                            self.add_param_window(refresh_df_func_or_py_eval_str, title=title, options=options)

                        if geom:
                            for window in self.mdi.subWindowList():
                                if not window.widget():
                                    continue
                                if window.widget().title == title:
                                    print(
                                        "load_current_workspace() window i {} title {} setgeom".format(
                                            i, title
                                        )
                                    )
                                    window.restoreGeometry(geom)
                                    if hh_state:
                                        window.widget().tableView.horizontalHeader().restoreState(hh_state)
                                        window.widget().tableView.horizontalHeader().adjustPositions()
                                    break
                    except:
                        type_, value_, traceback_ = sys.exc_info()
                        exstr = str(traceback.format_exception(type_, value_, traceback_))
                        print("WARNING: load_current_workspace() window i: {} - exception: {}".format(i, exstr))

            print("load_current_workspace() DONE")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: load_current_workspace() - exception: {}".format(exstr))
            try:
                print("doing qsettings clear()")
                self.current_workspace_settings.clear()
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: qsettings clear() - exception: {}".format(exstr))




class SubWindowArea(QMdiSubWindow):
    def __init__(self, item, gc):
        super().__init__(item)
        self.gc = gc
        dirname = os.path.dirname(__file__)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))

    def closeEvent(self, QCloseEvent):
        self.gc.mdi.removeSubWindow(self)


def main():
    app = QApplication([])
    window = main_window(None)
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
