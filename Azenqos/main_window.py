import contextlib
import datetime
import json
import textwrap
import uuid
import pathlib
import shutil
import threading
import traceback
import azq_cell_file
import add_pilot_pollution_layer

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
    QFrame,
    QToolBar,
    QHeaderView,
)
from PyQt5.uic import loadUi


import qt_utils, azq_utils
import spider_plot
import sql_utils
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
        QgsGraduatedSymbolRenderer,
        QgsDataSourceUri
    )
    from qgis.core import (
        QgsProcessingContext,
        QgsTaskManager,
        QgsTask,
        QgsProcessingAlgRunnerTask,
        Qgis,
        QgsProcessingFeedback,
        QgsApplication,
        QgsMessageLog,
    )
    from qgis.gui import QgsMapToolEmitPoint, QgsHighlight
    from PyQt5.QtGui import QColor
    from qgis.PyQt.QtCore import QVariant
    from qgis._core import QgsTask

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
import open_multiple_ue_dialog
import preprocess_azm
import params_disp_df
from version import VERSION

GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal

signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c
import inspect
import linechart_custom
import linechart_multi_y_axis
import wifi_scan_chart
import time
import pandas as pd
import sqlite3

TIME_COL_DEFAULT_WIDTH = 150
NAME_COL_DEFAULT_WIDTH = 180
CURRENT_WORKSPACE_FN = "last_workspace.ini"
AZQ_REPLAY_ENV_ACTIONS_KEY = "AZQ_REPLAY_ENV_ACTIONS_KEY"

class VLine(QFrame):
    # a simple VLine, like the one you get from designer
    def __init__(self):
        super(VLine, self).__init__()
        self.setFrameShape(self.VLine|self.Sunken)

class main_window(QMainWindow):

    signal_ui_thread_emit_time_slider_updated = pyqtSignal(float)
    task_done_signal = pyqtSignal(str)
    poi_open_signal = pyqtSignal()
    poi_result_signal = pyqtSignal(object, object)
    poi_progress_signal = pyqtSignal(int)
    refresh_signal = pyqtSignal()
    open_cellfile_progress_signal = pyqtSignal(int)
    open_cellfile_complete_signal = pyqtSignal()
    on_load_cellfile_error_signal = pyqtSignal(str)
    cellfile_layer_created_signal = pyqtSignal(object)
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
        if AZQ_REPLAY_ENV_ACTIONS_KEY in os.environ and os.environ[AZQ_REPLAY_ENV_ACTIONS_KEY]:
            self.gc.automated_mode = True
        self.gc.qgis_iface = qgis_iface
        self.gc.main_window = self
        self.gc.has_wave_file = False
        self.gc.live_mode = False
        self.gc.live_mode_update_time = False
        self.gc.is_mos_nb_lh_list = []
        self.timechange_service_thread = None
        self.is_legacy_indoor = False
        self.is_leg_nr_tables = False
        self.asked_easy_mode = False
        self.close_all_layers = True
        self.update_from_data_table = None
        self.timechange_to_service_counter = atomic_int(0)
        self.signal_ui_thread_emit_time_slider_updated.connect(
            self.ui_thread_emit_time_slider_updated
        )
        self.task_done_signal.connect(
            self.task_done_slot
        )
        self.last_window = None

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
        import progress_dialog
        self.poi_progress = progress_dialog.progress_dialog("Calculating...")
        self.open_cellfile_progress = progress_dialog.progress_dialog("Load Cell Files...")
        self.open_cellfile_progress_signal.connect(self.set_open_cellfile_progress)
        self.open_cellfile_complete_signal.connect(self.open_cellfile_complete)
        self.on_load_cellfile_error_signal.connect(self.open_cellfile_fail)
        self.cellfile_layer_created_signal.connect(self.on_cell_layer_created)
        self.refresh_signal.connect(self.refresh)
        self.poi_open_signal.connect(self.on_poi_open)
        self.poi_progress_signal.connect(self.set_poi_progress)
        self.poi_result_signal.connect(self.create_poi_window)
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
            if not self.gc.automated_mode:
                self.add_map_layer()
        try:
            QgsProject.instance().layersAdded.connect(self.on_layers_added)
        except:
            pass

        self.timechange_service_thread = threading.Thread(target=self.timeChangedWorkerFunc, args=tuple(), daemon=True)
        self.timechange_service_thread.start()
        self.setMinimumSize(50, 50)
        azq_utils.adb_kill_server_threaded()  # otherwise cant update plugin as adb files would be locked

        ##### set project crs to 4326 - this wont work if we call it here, need to call it from a delayed signal
        def emit_init_done(delay=0.5):
            time.sleep(delay)
            self.task_done_signal.emit("init")
        t = threading.Thread(target=emit_init_done)
        t.start()
        ######################################################################################################
        print("main_window __init__() done")

    def set_open_cellfile_progress(self, value):
        self.open_cellfile_progress.set_value(value)

    def open_cellfile_fail(self, msg_str):
        qt_utils.msgbox(msg_str, parent=self)

    def open_cellfile_complete(self):
        self.open_cellfile_progress.hide()

    def on_cell_layer_created(self, layer):
        QgsProject.instance().addMapLayers([layer])

    def on_poi_open(self):
        self.poi_progress.show()

    def set_poi_progress(self, value):
        self.poi_progress.set_value(value)
    
    def create_poi_window(self, df, title):
        self.add_param_window(custom_df=df, title=title, allow_no_log_opened=True)
        self.poi_progress.hide()

    def refresh(self):
        if self.gc.sliderLength:
            self.gc.timeSlider.setRange(0, self.gc.sliderLength)
            if self.gc.live_mode_update_time:
                self.gc.timeSlider.setValue(self.gc.sliderLength - 1)

    def dump_last_window(self, fp):
        print("dump_last_window START")
        if self.last_window is not None:
            print("dump_last_window START dump_data")
            self.last_window.tableModel.dump_data(fp, to_csv=True)
            print("dump_last_window END dump_data fp:", fp, "exists:", os.path.isfile(fp))
        print("dump_last_window END")
    
    def get_top_label_text(self, fp):
        print("get_top_label_text START")
        if self.mdi is not None:
            print("get_top_label_text START dump_data")
            top_label_text = self.ui.top_label.text()
            with open(fp, "w") as f:
                f.write(top_label_text)
            print("get_top_label_text END dump_data fp:", fp, "exists:", os.path.isfile(fp))
        print("get_top_label_text END")

    @pyqtSlot()
    def on_actionTile_triggered(self):
        print("tile")
        self.mdi.tileSubWindows()


    @pyqtSlot()
    def on_actionCloseAllSubWindows_triggered(self):
        print("tile")
        self.mdi.closeAllSubWindows()



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
    def on_actionOpen_multiple_UE_log_file_sets_triggered(self):
        print("open multiple UE log file sets")
        self.open_logs(multi_ue_mode=True)

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


    def add_image_view_swa(self, image_fp:str, width:int, height:int):
        swa = SubWindowArea(self.mdi, self.gc)
        im = QPixmap(image_fp)
        im = im.scaled(width, height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        label = QLabel()
        #lblImage->setSizePolicy(QSizePolicy::Ignored, QSizePolicy::Ignored );
        self.add_subwindow_with_widget(swa, label, allow_no_log_opened=True)
        label.setPixmap(im)
        label.setScaledContents(True)

    @pyqtSlot()
    def on_actionUser_Guide_triggered(self):
        url = QtCore.QUrl('https://docs.google.com/document/d/13ERtna5Rwuh0qgYUB0n8qihoW6hCO30TCJAIw_tXri0/edit?usp=sharing')
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')

    @pyqtSlot()
    def on_actionInstall_Update_Guide_triggered(self):
        url = QtCore.QUrl('https://github.com/freewillfx-azenqos/azenqos_qgis_plugin/blob/master/README.md')
        if not QtGui.QDesktopServices.openUrl(url):
            QtGui.QMessageBox.warning(self, 'Open Url', 'Could not open url')

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
        self.add_subwindow_with_widget(swa, widget, allow_no_log_opened=True)

    def run_py_eval_code_code_and_emit_to_window_once_done(self, py_eval_code, window):

        time.sleep(1)
        df = pd.DataFrame({"status": ["done"], "status2": ["done2"]})
        window.df = df
        window.tableHeader = df.columns.values.tolist()
        window.signal_ui_thread_emit_new_df.emit()

    def is_logged_in(self):
        return self.gc.is_logged_in()

    ############# log menu slots
    @pyqtSlot()
    def on_actionLog_Info_triggered(self):
        self.add_param_window("pd.read_sql('select log_hash, time, max(script_name) as script_name, max(script)as script, max(phonemodel) as phonemodel, max(imsi) as imsi, max(imei) as imei from log_info group by log_hash',dbcon)", title="Log Info", time_list_mode=True)

    @pyqtSlot()
    def on_actionLogs_triggered(self):
        self.add_param_window("pd.read_sql('select log_hash, time, log_start_time, log_end_time, log_tag, log_ori_file_name, log_app_version, log_license_edition, log_required_pc_version, log_timezone_offset from logs group by log_hash',dbcon)", title="Logs", time_list_mode=True)

    @pyqtSlot()
    def on_actionLocation_triggered(self):
        self.add_param_window("pd.read_sql('select log_hash, time, positioning_lat as latitude, positioning_lon as longitude from location where positioning_lat is not null',dbcon)", title="Location", time_list_mode=True)

    ############# system menu slots
    @pyqtSlot()
    def on_actionTechnology_triggered(self, selected_ue = None):
        print("technology")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import rat_plot_df
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            self.add_param_window(custom_df = rat_plot_df.get(dbcon),  title="Technology", selected_ue=selected_ue, time_list_mode=True)

    @pyqtSlot()
    def on_actionGSM_WCDMA_System_Info_triggered(self, selected_ue = None):
        print("action gsm wdcma system info")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/gsm_wcdma_system_info.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="GSM/WCDMA System Info", selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionLTE_System_Info_triggered(self, selected_ue = None):
        print("action lte system info")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/lte_system_info.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="GLTE System Info", selected_ue=selected_ue)

    ############# footprint menu slots

    @pyqtSlot()
    def on_actionNR_PCI_Footprint_triggered(self, selected_ue = None):
        print("action nr pci footprint")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "NR PCI Footprint", technology = "nr", selected_ue=selected_ue)
        dlg.show()

    @pyqtSlot()
    def on_actionLTE_PCI_Footprint_triggered(self, selected_ue = None):
        print("action lte pci footprint")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "LTE PCI Footprint", technology = "lte", selected_ue=selected_ue)
        dlg.show()

    @pyqtSlot()
    def on_actionWCDMA_PSC_Footprint_triggered(self, selected_ue = None):
        print("action wcdma psc footprint")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "WCDMA PSC Footprint", technology = "wcdma", selected_ue=selected_ue)
        dlg.show()

    @pyqtSlot()
    def on_actionGSM_BCCH_Footprint_triggered(self, selected_ue = None):
        print("action gsm bcch footprint")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import footprint_dialog

        dlg = footprint_dialog.footprint_dialog(self, self.gc, title = "GSM BCCH Footprint", technology = "gsm", selected_ue=selected_ue)
        dlg.show()

    ############# signalling menu slots
    @pyqtSlot()
    def on_actionLayer_3_Messages_triggered(self):
        self.add_param_window("pd.read_sql('select log_hash, time, name, symbol as dir, protocol, info, detail_str from signalling',dbcon).sort_values(by='time')", title="Layer-3 Messages", stretch_last_row=True, time_list_mode=True)

    @pyqtSlot()
    def on_actionEvents_triggered(self):
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            try:
                mos_df = pd.read_sql("select log_hash, time, 'MOS Score' as name, polqa_mos as info, wav_filename as wave_file from polqa_mos", dbcon)
                if len(mos_df) > 0 and "wave_file" in mos_df.columns:
                    self.gc.has_wave_file = True
                check_nb_df = pd.read_sql("select log_hash from events where info = 'is_mos_test_polqa_nb'", dbcon)
                if len(check_nb_df) > 0:
                    self.gc.is_mos_nb_lh_list = check_nb_df['log_hash'].tolist()
            except:
                pass
        if self.gc.has_wave_file == True:
            self.add_param_window('''pd.read_sql('select log_hash, time, name, info, detail, "" as wave_file from events union all select log_hash, time, "MOS Score" as name, polqa_mos as info, "" as detail, wav_filename as wave_file from polqa_mos where polqa_mos is not null',dbcon).sort_values(by='time')''', title="Events", stretch_last_row=True, time_list_mode=True, func_key=inspect.currentframe().f_code.co_name)
        else:
            self.add_param_window('''pd.read_sql('select log_hash, time, name, info, detail, "" as wave_file from events',dbcon).sort_values(by='time')''', title="Events", stretch_last_row=True, time_list_mode=True, func_key=inspect.currentframe().f_code.co_name)

    ############# NR menu slots
    @pyqtSlot()
    def on_action5GNR_Radio_triggered(self, selected_ue = None):
        print("action nr radio params")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/nr_radio.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="NR Radio Parameters", selected_ue=selected_ue)

    @pyqtSlot()
    def on_action5GNR_Data_triggered(self, selected_ue = None):
        print("action nr data params")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/nr_data.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="NR Data Parameters", selected_ue=selected_ue)



    def add_param_window(self, refresh_func_or_py_eval_str_or_sql_str=None, title="Param Window", time_list_mode=False, stretch_last_row=False, options=None, func_key=None, custom_df=None, custom_table_param_list=None, custom_last_instant_table_param_list=None, custom_table_main_not_null=False, allow_no_log_opened=False, selected_ue=None,
                         col_min_size=40,
                         col_default_size=70,
                         resize_to_contents=False,
    ):
        swa = SubWindowArea(self.mdi, self.gc)
        print("add_param_window: time_list_mode:", time_list_mode)
        widget = TableWindow(
            swa,
            title,
            refresh_func_or_py_eval_str_or_sql_str,
            time_list_mode=time_list_mode,
            stretch_last_row=stretch_last_row,
            options=options,
            func_key=func_key,
            custom_df=custom_df,
            custom_table_param_list=custom_table_param_list,
            custom_last_instant_table_param_list=custom_last_instant_table_param_list,
            custom_table_main_not_null=custom_table_main_not_null,
            selected_ue=selected_ue,
            col_min_size=col_min_size,
            col_default_size=col_default_size,
            gc=self.gc,
        )
        self.last_window = widget
        
        def updateTime(time):
            self.update_from_data_table = widget
            self.setTimeValue(time)

        widget.signal_ui_thread_emit_select_row_time.connect(updateTime)
        self.add_subwindow_with_widget(swa, widget, allow_no_log_opened=allow_no_log_opened)
        if resize_to_contents:
            widget.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


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
            name, info, detail_str 
            from signalling
            union
            select log_hash, time,
            name, info, detail
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
    def on_actionCustom_Instant_View_UI_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import custom_last_instant_table_dialog
        dlg = custom_last_instant_table_dialog.custom_last_instant_table_dialog(self.gc, selected_ue=selected_ue)
        dlg.on_result.connect(lambda param_list, title, selected_ue: self.add_param_window(custom_df=param_list, title=title, custom_last_instant_table_param_list=param_list, selected_ue=selected_ue))
        dlg.show()

    @pyqtSlot()
    def on_actionCustom_Table_View_UI_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import custom_table_dialog
        dlg = custom_table_dialog.custom_table_dialog(self.gc, selected_ue=selected_ue)
        dlg.on_result.connect(lambda df, param_list, title, selected_ue, main_not_null: self.add_param_window(custom_df=df, title=title, time_list_mode=True, custom_table_param_list=param_list, selected_ue=selected_ue, custom_table_main_not_null=main_not_null))
        dlg.show()

    @pyqtSlot()
    def on_actionExynosServiceMode_BasicInfo_2_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        self.add_param_window("select log_hash, time, exynos_basic_info from exynos_basic_info", title="ExynosServiceMode BasicInfo", stretch_last_row=True, selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionExynosServiceMode_NR_Radio_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/exynos_nr_radio.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="ExynosServiceMode NR Radio", selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionExynosServiceMode_NR_Data_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/exynos_nr_data.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="ExynosServiceMode NR Data", selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionExynosServiceMode_NR_Reg_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/exynos_nr_rag.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="ExynosServiceMode NR Reg", selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionExynos_LTE_Radio_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/exynos_lte_radio.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="ExynosServiceMode LTE Radio", selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionExynosServiceMode_LTE_Data_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/exynos_lte_data.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="ExynosServiceMode LTE Data", selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionExynosServiceMode_LTE_Reg_triggered(self, selected_ue = None):
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/exynos_lte_reg.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="ExynosServiceMode LTE Reg", selected_ue=selected_ue)

    @pyqtSlot()
    def on_action5GNR_Serving_Neighbors_triggered(self, selected_ue = None):
        print("action nr serving neigh")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/nr_serv_neigh.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="NR Serving + Neighbors", selected_ue=selected_ue)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="ExynosServiceMode LTE Reg", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionNR_Pilot_Pollution_triggered(self, selected_ue = None):
        print("action nr pilot pollution")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        add_pilot_pollution_layer.add_layer(self.gc.databasePath, technology="nr", selected_ue=selected_ue, is_indoor=self.gc.is_indoor, device_configs=self.gc.device_configs)

    ############# LTE menu slots
    @pyqtSlot()
    def on_actionLTE_Radio_Parameters_triggered(self, selected_ue=None, col_min_size=40, col_default_size=70, resize_to_contents=False):
        print("action lte radio params")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/lte_radio.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(
                custom_df=custom_last_instant_table_param_list,
                custom_last_instant_table_param_list=custom_last_instant_table_param_list,
                title="LTE Radio Parameters",
                selected_ue=selected_ue,
                stretch_last_row=False,
                col_min_size=col_min_size,
                col_default_size=col_default_size,
                resize_to_contents=resize_to_contents,
                )

    @pyqtSlot()
    def on_actionLTE_Serving_Neighbors_triggered(self, selected_ue = None):
        print("action lte serving neigh")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/lte_serv_neigh.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="LTE Serving + Neighbors", selected_ue=selected_ue)
        
    @pyqtSlot()
    def on_actionLTE_Data_Params_triggered(self, selected_ue = None):
        print("action lte data param")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        with open(azq_utils.get_module_fp("custom_table/lte_data.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="LTE Data Parameters", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionLTE_PUCCH_PDSCH_Params_triggered(self, selected_ue = None):
        print("action lte pucch pdsch param")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import lte_sql_query
        # self.add_param_window(lte_sql_query.LTE_PUCCH_PDSCH_SQL_LIST_DICT, title="PUCCH/PDSCH Params", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/lte_pucch_pdsch.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="LTE PUCCH/PDSCH", selected_ue=selected_ue)
        
    @pyqtSlot()
    def on_actionLTE_RRC_SIB_States_triggered(self, selected_ue = None):
        print("action lte rrc sib states")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import lte_sql_query
        # self.add_param_window(lte_sql_query.LTE_RRC_SIB_SQL_LIST, title="LTE RRC/SIB States", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/lte_rrc_sib.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="LTE RRC/SIB States", selected_ue=selected_ue)
        
    @pyqtSlot()
    def on_actionLTE_RLC_triggered(self, selected_ue = None):
        print("action lte rlc")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import lte_sql_query
        # self.add_param_window(lte_sql_query.LTE_RLC_SQL_LIST_DICT, title="LTE RLC", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/lte_rlc.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="LTE RLC", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionLTE_VoLTE_triggered(self, selected_ue = None):
        print("action lte volte")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import lte_sql_query
        # self.add_param_window(lte_sql_query.LTE_VOLTE_SQL_LIST, title="LTE VoLTE", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/lte_volte.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="LTE VoLTE", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionLTE_Pilot_Pollution_triggered(self, selected_ue = None):
        print("action lte pilot pollution")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        add_pilot_pollution_layer.add_layer(self.gc.databasePath, technology="lte", selected_ue=selected_ue, is_indoor=self.gc.is_indoor, device_configs=self.gc.device_configs)

    @pyqtSlot()
    def on_actionLTE_Pilot_Pollution_All_Frequency_triggered(self, selected_ue = None):
        print("action lte pilot pollution")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        add_pilot_pollution_layer.add_layer(self.gc.databasePath, technology="lte", filter_freq=False, selected_ue=selected_ue, is_indoor=self.gc.is_indoor, device_configs=self.gc.device_configs)

    ############# WCDMA menu slots

    @pyqtSlot()
    def on_actionWCDMA_Radio_Parameters_triggered(self, selected_ue = None):
        print("action wcdma radio params")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import wcdma_sql_query
        # self.add_param_window(wcdma_sql_query.WCDMA_RADIO_PARAMS_SQL_LIST, title="WCDMA Radio Parameters", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/wcdma_radio.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="WCDMA Radio Parameters", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionWCDMA_Active_Monitored_sets_triggered(self, selected_ue = None):
        print("action wcdma active monitored")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import wcdma_sql_query
        # self.add_param_window(wcdma_sql_query.WCDMA_ACTIVE_MONITORED_SQL_LIST_DICT, title="WCDMA Active + Monitored sets", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/wcdma_aset_mset.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="WCDMA Active + Monitored sets", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionWCDMA_BLER_Summary_triggered(self, selected_ue = None):
        print("action wcdma bler summary")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import wcdma_sql_query
        # self.add_param_window(wcdma_sql_query.WCDMA_BLER_SQL_LIST, title="WCDMA BLER Summary", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/wcdma_bler.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="WCDMA BLER Summary", selected_ue=selected_ue)
        
    @pyqtSlot()
    def on_actionWCDMA_Bearers_triggered(self, selected_ue = None):
        print("action wcdma bearers")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import wcdma_sql_query
        # self.add_param_window(wcdma_sql_query.WCDMA_BLER_SQL_LIST_DICT, title="WCDMA Bearers", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/wcdma_bearer.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="WCDMA Bearers", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionWCDMA_Pilot_Pollution_triggered(self, selected_ue = None):
        print("action wcdma pilot pollution")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        add_pilot_pollution_layer.add_layer(self.gc.databasePath, technology="wcdma", selected_ue=selected_ue, is_indoor=self.gc.is_indoor, device_configs=self.gc.device_configs)

    ############# GSM menu slots

    @pyqtSlot()
    def on_actionGSM_Physical_Parameters_triggered(self, selected_ue = None):
        print("action gsm radio params")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import gsm_sql_query
        # self.add_param_window(gsm_sql_query.GSM_RADIO_PARAMS_SQL_LIST, title="GSM Radio Parameters", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/gsm_radio.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="GSM Radio Parameters", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionGSM_Serving_Neighbors_triggered(self, selected_ue = None):
        print("action gsm serving neigh")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import gsm_sql_query
        # self.add_param_window(gsm_sql_query.GSM_SERV_AND_NEIGH_SQL_LIST_DICT, title="GSM Serving + Neighbors", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/gsm_serv_neigh.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="GSM Serving + Neighbors", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionGSM_Current_Channel_triggered(self, selected_ue = None):
        print("action gsm current channel")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import gsm_sql_query
        # self.add_param_window(gsm_sql_query.GSM_CURRENT_CHANNEL_SQL_LIST, title="GSM Current Channel", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/gsm_current_channel.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="GSM Current Channel", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionGSM_C_I_triggered(self, selected_ue = None):
        print("action gsm coi")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import gsm_sql_query
        # self.add_param_window(gsm_sql_query.GSM_COI_SQL_LIST_DICT, title="GSM C/I", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/gsm_c_i.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="GSM C/I", selected_ue=selected_ue)


    ############# PCAP menu slots

    @pyqtSlot()
    def on_actionPCAP_triggered(self, selected_ue = None):
        print("action pcap")
        title = "PCAP"
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
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
            title,
            pcap_window.new_get_all_pcap_content(azq_utils.tmp_gen_path(), self.gc, selected_ue=selected_ue),
            tableHeader=headers,
            time_list_mode=True,
            selected_ue=selected_ue,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# OTT menu slots

    @pyqtSlot()
    def on_actionVideo_Streaming_triggered(self):
        print("action action video streaming")

        has_video_mos = False
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            try:
                pp_video_mos_df = pd.read_sql("select * from pp_statement_sum_ott_video_streaming_mos", dbcon)
                if len(pp_video_mos_df) > 0:
                    has_video_mos = True
            except:
                pass
        if has_video_mos:
            self.add_param_window('''pd.read_sql("select ott_vdo.log_hash, ott_vdo.time, ott_vdo.ott_video_streaming_start_time, ott_vdo.ott_video_streaming_end_time, ott_vdo.ott_video_streaming_session_id, ott_vdo.ott_video_streaming_video_url, ott_vdo.ott_video_streaming_mos_enabled, ott_vdo.ott_video_streaming_end_result, ott_vdo.ott_video_streaming_end_result_detail, pp_ott_vdo.ott_video_streaming_mos_score from ott_video_streaming as ott_vdo left join pp_statement_sum_ott_video_streaming_mos as pp_ott_vdo on ott_vdo.log_hash = pp_ott_vdo.log_hash and ott_vdo.ott_video_streaming_session_id = pp_ott_vdo.ott_video_streaming_session_id",dbcon).sort_values(by='time')''', title="OTT Video Streaming", time_list_mode=True, func_key=inspect.currentframe().f_code.co_name)
        else:
            self.add_param_window('''pd.read_sql("select log_hash, time, ott_video_streaming_start_time, ott_video_streaming_end_time, ott_video_streaming_session_id, ott_video_streaming_video_url, ott_video_streaming_mos_enabled, ott_video_streaming_end_result, ott_video_streaming_end_result_detail, 'requires server processing' as ott_video_streaming_mos_score from ott_video_streaming",dbcon).sort_values(by='time')''', title="OTT Video Streaming", time_list_mode=True, func_key=inspect.currentframe().f_code.co_name)
            

    ############# Add Layer menu slots

    @pyqtSlot()
    def on_actionAdd_Layer_triggered(self):
        print("action add layer")
        has_voice_report = False
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            try:
                pp_voice_report_df = pd.read_sql("select * from pp_voice_report", dbcon)
                if len(pp_voice_report_df) > 0:
                    has_voice_report = True
            except:
                pass
        elm_df = preprocess_azm.get_elm_df_from_csv()
        elm_df = elm_df[["var_name", "name", "n_arg_max"]].reset_index(drop=True)
        call_types = ["call_init", "call_setup", "call_established", "call_end", "call_block", "call_drop"]
        if has_voice_report:
            for call_type in call_types:
                elm_df = elm_df.append({"var_name":call_type , "name":"", "n_arg_max":1}, ignore_index=True)
        swa = SubWindowArea(self.mdi, self.gc)

        widget = TableWindow(
            swa,
            "Add Layer",
            elm_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# Add Event Layer menu slots

    @pyqtSlot()
    def on_actionAdd_Event_Layer_triggered(self):
        print("action add event layer")
        import add_event_layer_dialog
        event_list = []
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            event_list = pd.read_sql("select distinct name from events", dbcon).name.tolist()
        dlg = add_event_layer_dialog.add_event_layer_dialog(event_list, self.gc)
        dlg.show()

    ############# Add POI Layer menu slots

    @pyqtSlot()
    def on_actionAdd_POI_Layer_triggered(self):
        print("action add poi layer")
        from pathlib import Path
        import qgis_layers_gen
        pot_file_name = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open POI file ...", os.path.join(Path.home(),""), "POI file(*.csv *.kml *.mif *.tab);;All file(*)"
        )
        if pot_file_name:
            if pot_file_name[0]:
                pot_file_path = pot_file_name[0]
                try:
                    qgis_layers_gen.check_poi_file(self.gc, pot_file_path)
                except:
                    pass

    ############# Add POI Layer menu slots

    
    @pyqtSlot()
    def on_actionCalculate_POI_Coverage_triggered(self):
        print("action calculate poi coverage")
        # result_signal = pyqtSignal(object, object)
        import calculate_poi_dialog
        dlg = calculate_poi_dialog.calculate_poi(self.gc, self.poi_result_signal, self.poi_progress_signal, self.poi_open_signal)
        dlg.show()
    ############# Add POI Layer menu slots

    
    @pyqtSlot()
    def on_actionCalculate_KPI_from_exclusion_by_polygon_triggered(self):
        print("action calculate kpi exclusion")
        import polygon_kpi_exclusion_widget
        widget = polygon_kpi_exclusion_widget.polygon_kpi_exclusion(self, self.gc)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, widget, allow_no_log_opened=True, w=None, h=None)
    ############# Add POI Layer menu slots

    
    @pyqtSlot()
    def on_actionLayer_Distance_Binning_triggered(self):
        print("action distance bin")
        import distance_bin
        widget = distance_bin.distance_bin(self, self.gc)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, widget, allow_no_log_opened=True, w=None, h=None)


    ############# Data menu slots

    @pyqtSlot()
    def on_actionWiFi_Active_triggered(self, selected_ue = None):
        print("action wifi active")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import data_sql_query
        self.add_param_window(data_sql_query.WIFI_ACTIVE_SQL_LIST, title="WiFi Active", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/wifi_active.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="WiFi Active", selected_ue=selected_ue)


    @pyqtSlot()
    def on_actionWiFi_Scan_triggered(self, selected_ue = None):
        print("action wifi scan")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        import data_query
        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "WiFi Scan",
            data_query.get_wifi_scan_df,
            func_key=inspect.currentframe().f_code.co_name,
            selected_ue = selected_ue
        )
        self.add_subwindow_with_widget(swa, widget)
    
    @pyqtSlot()
    def on_action2_4_GHz_triggered(self, selected_ue=None, mode="2.4"):
        print("action wifi scan chart 2.4 GHz")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        title = "WiFi Scan 2.4 GHz"
        linechart_window = wifi_scan_chart.wifi_scan_chart(
            self.gc,
            mode=mode,
        )

        swa = SubWindowArea(self.mdi, self.gc)
        if self.add_subwindow_with_widget(swa, linechart_window):
            linechart_window.open()
            linechart_window.setWindowTitle(title)
    
    @pyqtSlot()
    def on_action5_GHz_triggered(self, selected_ue=None, mode="5l"):
        print("action wifi scan chart 5 GHz")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        title = "WiFi Scan 5 GHz Low Frequencies"
        linechart_window = wifi_scan_chart.wifi_scan_chart(
            self.gc,
            mode=mode,
        )

        swa = SubWindowArea(self.mdi, self.gc)
        if self.add_subwindow_with_widget(swa, linechart_window):
            linechart_window.open()
            linechart_window.setWindowTitle(title)

    @pyqtSlot()
    def on_action5_GHz_High_triggered(self, selected_ue=None, mode="5h"):
        print("action wifi scan chart 5 GHz")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        title = "WiFi Scan 5 GHz High Frequencies"
        linechart_window = wifi_scan_chart.wifi_scan_chart(
            self.gc,
            mode=mode,
        )

        swa = SubWindowArea(self.mdi, self.gc)
        if self.add_subwindow_with_widget(swa, linechart_window):
            linechart_window.open()
            linechart_window.setWindowTitle(title)

    @pyqtSlot()
    def on_actionGPRS_EDGE_Information_triggered(self, selected_ue = None):
        print("action gprs edge info")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import data_sql_query
        # self.add_param_window(data_sql_query.GPRS_EDGE_SQL_LIST, title="GPRS/EDGE Information", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/gprs_edge.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="GPRS/EDGE Information", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionHSDPA_Statistics_triggered(self, selected_ue = None):
        print("action hadpa statistics")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import data_sql_query
        # self.add_param_window(data_sql_query.HSDPA_STATISTICS_SQL_LIST, title="HSDPA Statistics", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/hsdpa_stat.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="HSDPA Statistics", selected_ue=selected_ue)

    @pyqtSlot()
    def on_actionHSUPA_Statistics_triggered(self, selected_ue = None):
        print("action haupa statistics")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        # import data_sql_query
        # self.add_param_window(data_sql_query.HSUPA_STATISTICS_SQL_LIST, title="HSUPA Statistics", selected_ue=selected_ue)
        with open(azq_utils.get_module_fp("custom_table/hsupa_stat.json"), 'r') as f:
            custom_last_instant_table_param_list = json.load(f)
            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title="HSUPA Statistics", selected_ue=selected_ue)

    
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
        self.add_param_window("pd.read_sql('select * from datasession',dbcon)", title="datasession", time_list_mode=True)

    @pyqtSlot()
    def on_actionline_mo_triggered(self):
        print("action line session")
        self.add_param_window("pd.read_sql('select * from line_mo',dbcon)", title="line_mo", time_list_mode=True)

    @pyqtSlot()
    def on_actionpingsession_triggered(self):
        print("action ping session")
        self.add_param_window("pd.read_sql('select * from pingsession',dbcon)", title="pingsession", time_list_mode=True)

    @pyqtSlot()
    def on_actionspeedtestsession_triggered(self):
        print("action speedtest session")
        self.add_param_window("pd.read_sql('select * from speedtestsession',dbcon)", title="speedtestsession", time_list_mode=True)

    @pyqtSlot()
    def on_actionyoutube_triggered(self):
        print("action youtube session")
        self.add_param_window("pd.read_sql('select * from youtube',dbcon)", title="youtube", time_list_mode=True)

    @pyqtSlot()
    def on_actionyoutube_buffer_duration_triggered(self):
        print("action youtube buffer duration session")
        self.add_param_window("pd.read_sql('select * from youtube_buffer_duration',dbcon)", title="youtube_buffer_duration", time_list_mode=True)

    ############# Line Chart Custom

    @pyqtSlot()
    def on_actionCustom_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action line chart custom")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        title = "Line Chart Custom"
        linechart_window = linechart_custom.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        if self.add_subwindow_with_widget(swa, linechart_window):
            linechart_window.open()
            linechart_window.setWindowTitle(title)

    ############# Line Chart NR

    @pyqtSlot()
    def on_actionNR_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action nr line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "nr_servingbeam_ss_rsrp_1", "selected_ue": selected_ue},
                {"name": "nr_servingbeam_ss_rsrq_1", "selected_ue": selected_ue},
                {"name": "nr_servingbeam_ss_sinr_1", "selected_ue": selected_ue},
            ]
        title = "NR Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)

    @pyqtSlot()
    def on_actionNR_DATA_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action nr data line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "data_trafficstat_dl/1000", "data": True, "selected_ue": selected_ue},
                {"name": "data_trafficstat_ul/1000", "data": True, "selected_ue": selected_ue},
                {"name": "nr_p_plus_scell_nr_pdsch_tput_mbps", "data": True, "selected_ue": selected_ue},
                {"name": "nr_p_plus_scell_nr_pusch_tput_mbps", "data": True, "selected_ue": selected_ue},
                {"name": "nr_p_plus_scell_lte_dl_pdcp_tput_mbps", "data": True, "selected_ue": selected_ue},
                {"name": "nr_p_plus_scell_lte_ul_pdcp_tput_mbps", "data": True, "selected_ue": selected_ue},
            ]
        title="NR Data Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)

    ############# Line Chart LTE

    @pyqtSlot()
    def on_actionLTE_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action lte line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "lte_sinr_1", "selected_ue": selected_ue},
                {"name": "lte_inst_rsrp_1", "selected_ue": selected_ue},
                {"name": "lte_inst_rsrq_1", "selected_ue": selected_ue},
                {"name": "lte_inst_rssi_1", "selected_ue": selected_ue},
            ]
        title="LTE Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)

    @pyqtSlot()
    def on_actionLTE_DATA_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action lte data line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "data_trafficstat_dl/1000", "data": True, "selected_ue": selected_ue},
                {"name": "data_trafficstat_ul/1000", "data": True, "selected_ue": selected_ue},
                {"name": "lte_l1_dl_throughput_all_carriers_mbps", "data": True, "selected_ue": selected_ue},
                {"name": "lte_bler_1", "data": True, "selected_ue": selected_ue},
            ]
        title="LTE Data Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)

    ############# Line Chart WCDMA

    @pyqtSlot()
    def on_actionWCDMA_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action wcdma line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "wcdma_aset_ecio_1", "selected_ue": selected_ue},
                {"name": "wcdma_aset_rscp_1", "selected_ue": selected_ue},
                {"name": "wcdma_rssi", "selected_ue": selected_ue},
                {"name": "wcdma_bler_average_percent_all_channels", "selected_ue": selected_ue},
            ]
        title="WCDMA Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)

    @pyqtSlot()
    def on_actionWCDMA_DATA_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action wcdma data line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "data_wcdma_rlc_dl_throughput", "data": True, "selected_ue": selected_ue},
                {"name": "data_app_dl_throughput_1", "data": True, "selected_ue": selected_ue},
                {"name": "data_hsdpa_thoughput", "data": True, "selected_ue": selected_ue},
            ]
        title="WCDMA Data Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )
        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)

    ############# Line Chart GSM

    @pyqtSlot()
    def on_actionGSM_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action gsm line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "gsm_rxlev_sub_dbm", "selected_ue": selected_ue},
                {"name": "gsm_rxqual_sub", "selected_ue": selected_ue},
            ]
        title="GSM Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)

    @pyqtSlot()
    def on_actionGSM_DATA_Line_Chart_triggered(self, selected_ue=None, paramList=[], eventList=[]):
        print("action gsm data line chart")
        if selected_ue is None and len(self.gc.device_configs) > 1:
            import select_log_dialog
            dlg = select_log_dialog.select_log_dialog(self.gc.device_configs)
            result = dlg.exec_()
            if not result:
                return
            selected_ue = dlg.log
        if len(paramList) == 0:
            paramList=[
                {"name": "data_gsm_rlc_dl_throughput", "data": True, "selected_ue": selected_ue},
                {"name": "data_app_dl_throughput_1", "data": True, "selected_ue": selected_ue},
            ]
        title="GSM Data Line Chart"
        linechart_window = linechart_multi_y_axis.LineChart(
            self.gc,
            paramList=paramList,
            eventList=eventList,
            title=title,
            func_key=inspect.currentframe().f_code.co_name
        )

        def updateTime(epoch):
            timestampValue = epoch - self.gc.minTimeValue
            print(timestampValue)
            self.setTimeValue(timestampValue)

        linechart_window.timeSelected.connect(updateTime)
        swa = SubWindowArea(self.mdi, self.gc)
        self.add_subwindow_with_widget(swa, linechart_window)
        linechart_window.open()
        linechart_window.setWindowTitle(title)


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
            self.gc.timeSlider.setPageStep(1)  # 1 second for pageup/down, use neg for pgup to go backwards
            self.gc.timeSlider.setSingleStep(1)  # 1 second for pageup/down
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
            self.timeEdit.setObjectName("timeEdit")
            self.timeEdit.setDisplayFormat("hh:mm:ss.zzz")
            self.timeEdit.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
            self.timeEdit.setReadOnly(True)

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

            # refresh connected phone button
            self.live_button = QToolButton()
            self.live_button.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "stoplive.png")))
            )
            self.live_button.setObjectName("live_button")
            self.live_button.setToolTip(
                "<b>Live</b><br>..."
            )
            self.live_button.setEnabled(False)

            self.gc.timeSlider.valueChanged.connect(self.timeChange)
            self.saveBtn.clicked.connect(self.saveDbAs)
            self.layerSelect.clicked.connect(self.on_button_selectLayer)
            self.cellsSelect.clicked.connect(self.selectCells)
            self.importDatabaseBtn.clicked.connect(self.open_logs)
            self.maptool.clicked.connect(self.setMapTool)
            self.sync_connected_phone_button.clicked.connect(self.sync_connected_phone)
            self.live_button.clicked.connect(self.switch_live_mode)
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
        self.toolbar.addWidget(self.live_button)
        self.toolbar.addSeparator()
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
        self.playButton = QToolButton()
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.setToolTip(
            "<b>Play</b><br><i>Start</i> or <i>Resume</i> log replay."
        )
        self.pauseButton = QToolButton()
        self.pauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
        self.pauseButton.setToolTip("<b>Pause</b><br> <i>Pause</i> log replay")
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
        if self.timeSliderThread.getCurrentValue() < self.gc.timeSlider._value_range:
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
            
            self.open_cellfile_progress.show()
            self.open_cellfile_progress.set_value(0)
            self.open_cellfile_progress_signal.emit(0)
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
            print("selectCells add_cell_layers()")
            worker = Worker(self.add_cell_layers)
            self.gc.threadpool.start(worker)
            # self.add_cell_layers()  # this will set cellfiles
            if self.gc.db_fp:
                print("selectCells add_spider_layer()")
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


    def updateTime_str(self, time_str: str):
        epoch = azq_utils.datetimeStringtoTimestamp(time_str)
        timestampValue = epoch - self.gc.minTimeValue
        print("updateTime_str: timestampValue:", timestampValue)
        self.setTimeValue(timestampValue)

    def run_alg_block_print_progress(self, alg_name, alg_params):
        from qgis import processing
        def progress_changed(progress):
            print(f"proc progress: {progress}")
        feedback = QgsProcessingFeedback()
        feedback.progressChanged.connect(progress_changed)
        ret_dict = processing.run(alg_name, alg_params, feedback=feedback)
        print(f"proc result {ret_dict}")
        return ret_dict

    def _gen_xyz_tiles_done(self):
        print("_gen_xyz_tiles_done")

    def setTimeValue(self, value):
        print("%s: setTimeValue %s" % (os.path.basename(__file__), value))
        print(value)
        self.gc.timeSlider.setValue(value)
        print("mw self.gc.timeSlider.value()", self.gc.timeSlider.value())
        self.gc.timeSlider.update()
        if value >= self.gc.timeSlider._value_range:
            self.pauseTime()

    def task_done_slot(self, msg):
        print("main_window task_done_slot msg:", msg)
        if msg == "cell_layer_task.py":
            self.cell_layer_task.add_layers_from_ui_thread()
        elif msg == "db_layer_task.py":
            self.db_layer_task.add_layers_from_ui_thread()
        elif msg == "init":
            print("task_done_slot init start")
            self.set_project_crs()
            #ss = azq_utils.take_screenshot_pil_obj()
            #print("task_done_slot save ss start")
            #ss.save("/host_shared_dir/tmp_gen/ss.png")
            #print("task_done_slot save ss")
            print("task_done_slot init done")
            #print("os.environ:", os.environ)
            if AZQ_REPLAY_ENV_ACTIONS_KEY in os.environ and os.environ[AZQ_REPLAY_ENV_ACTIONS_KEY]:
                try:
                    print("AZQ_REPLAY_ENV_ACTIONS_KEY actions START")
                    import server_overview_widget
                    env_val = os.environ[AZQ_REPLAY_ENV_ACTIONS_KEY]
                    if os.path.isfile(env_val):
                        with open(env_val, "r") as f:
                            action_list = json.load(f)
                    else:
                        action_list = json.loads(
                            env_val
                        )
                    for action in action_list:
                        print("action START:", action)
                        assert isinstance(action, str)
                        main_window.curInstance = self
                        if " = " in action:
                            action_ret = exec(textwrap.dedent(action))
                        else:
                            action_ret = eval(textwrap.dedent(action))
                        print("action DONE: action_ret", action_ret)
                    print("AZQ_REPLAY_ENV_ACTIONS_KEY actions DONE")
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(
                        traceback.format_exception(type_, value_, traceback_)
                    )
                    print(
                        "ABORT: AZQ_REPLAY_ENV_ACTIONS_KEY - exception: {}".format(
                            exstr
                        )
                    )
                    os._exit(os.EX_TEMPFAIL)

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
            timeSliderValue = selectedTimestamp - self.gc.minTimeValue
            timeSliderValue = round(timeSliderValue, 3)
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


    def set_default_font_size_override(self, font_size):
        self.gc.default_font_size_override = font_size

    def set_default_top_params_font_size_override(self, font_size):
        self.gc.default_top_params_font_size_override = font_size


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

    def switch_live_mode(self):
        dirname = os.path.dirname(__file__)
        self.gc.live_mode_update_time = not self.gc.live_mode_update_time
        if self.gc.live_mode_update_time:
            self.live_button.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "live.png")))
            )
        else:
            self.live_button.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "stoplive.png")))
            )


    def open_logs(self, connected_mode_refresh=False, ask_close_all_layers=True, multi_ue_mode=False, auto_mode_azm=None, auto_mode_theme=None, auto_mode_cellfiles=[]):
        print("open_logs: START")
        if auto_mode_azm:
            print("auto_mode_azm START:", auto_mode_azm)
            assert os.path.isfile(auto_mode_azm)
            if auto_mode_theme:
                assert os.path.isfile(auto_mode_theme)
                print("auto_mode_azm import theme")
                azq_theme_manager.set_default_theme_file(auto_mode_theme)
            '''
            if auto_mode_cellfiles:
                print("auto_mode_azm import cellfiles")
                azq_cell_file.check_cell_files(auto_mode_cellfiles)
                self.gc.cell_files = auto_mode_cellfiles
            '''

            importer = import_db_dialog.import_db_dialog(self, self.gc, auto_mode=True)
            importer.import_azm(auto_mode_azm)
            importer.addDatabase()
            print("auto_mode_azm DONE:", auto_mode_azm)
        else:
            if self.gc.databasePath:
                if ask_close_all_layers:
                    reply = qt_utils.ask_yes_no(None, "Open log", "Close all layers?", question=True)

                    if reply == QMessageBox.Cancel:
                        return
                    self.close_all_layers = False
                    if reply == QMessageBox.Yes:
                        self.close_all_layers = True
                self.gc.databasePath = None
                self.gc.db_fp = None
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
            if not multi_ue_mode:
                dlg = import_db_dialog.import_db_dialog(self, self.gc, connected_mode_refresh=connected_mode_refresh)
                dlg.show()
                ret = dlg.exec()
                print("import_db_dialog ret: {}".format(ret))
            else:
                dlg = open_multiple_ue_dialog.open_multiple_ue_dialog(self, self.gc)
                dlg.show()
                ret = dlg.exec()

            if self.gc.log_mode == "adb":
                self.sync_connected_phone_button.setEnabled(True)
                self.live_button.setEnabled(True)
            else:
                self.sync_connected_phone_button.setEnabled(False)
                self.live_button.setEnabled(False)
        if not self.gc.databasePath:
            print("not self.gc.databasePath so return")
            # dialog not completed successfully
            return
        if self.gc.db_fp:
            if self.qgis_iface:
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
            self.gc.timeSlider.setValue(0)
        if self.gc.databasePath:
            if not auto_mode_azm:
                self.load_current_workspace()
            self.ui.statusbar.showMessage(
                "Opened log: {}".format(self.gc.azm_name if self.gc.azm_name else self.gc.databasePath)
            )
            if connected_mode_refresh:
                if self.gc.sliderLength:
                    self.gc.timeSlider.setValue(self.gc.sliderLength - 1)
        else:
            self.ui.statusbar.showMessage("Log not opened...")
        self.updateUi()
        self.is_leg_nr_tables = preprocess_azm.is_leg_nr_tables()
        if self.gc.log_mode == "adb":
            for device in self.gc.device_configs:
                ret = azq_utils.call_no_shell((azq_utils.get_adb_command(), "-s", device["key"], "shell", "ls",  "/sdcard/azq_db_live"))
                if ret != 0:
                    qt_utils.msgbox("please enable QGIS Replay LIVE mode from Azenqos application", title="Live mode is not enabled on {}".format(device["name"]), parent=self)
                    return
            if not self.gc.live_mode_update_time:
                self.switch_live_mode()
            import queue
            self.gc.live_mode = True
            db_queue = queue.Queue()
            worker = Worker(azq_utils.live_mode_db_insert(self.gc, self.refresh_signal, db_queue))
            self.gc.threadpool.start(worker)
            for device in self.gc.device_configs:
                worker = Worker(azq_utils.live_mode(self.gc, device, db_queue))
                self.gc.threadpool.start(worker)
        self.ui.top_label.setText("")
        print("open_logs: DONE")

    def timeChange(self):

        ######### this change comes from the timeslider so set selected_row_log_hash
        self.gc.selected_row_log_hash = None
        if self.gc.selected_point_match_dict is not None:
            self.gc.selected_point_match_dict["log_hash"] = None
        #################

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

        self.gc.currentDateTimeString = "%s" % (
            datetime.datetime.fromtimestamp(self.gc.currentTimestamp).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3]
        )
        print("%s: timeChange6 set self.gc.currentTimestamp:", self.gc.currentTimestamp, "self.gc.currentDateTimeString", self.gc.currentDateTimeString)
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
                window_title = ""
                try:
                    window_title = window.title
                except:
                    pass
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
                elif isinstance(window, wifi_scan_chart.wifi_scan_chart):
                    window.update_time(sampledate)
                elif not window_title in self.gc.linechartWindowname:
                    print(
                        "%s: timeChange7 hilightrow window %s"
                        % (os.path.basename(__file__), window_title)
                    )
                    if window != self.update_from_data_table:
                        try:
                            window.hilightRow(sampledate)
                        except:
                            type_, value_, traceback_ = sys.exc_info()
                            exstr = str(traceback.format_exception(type_, value_, traceback_))
                            print(
                                "WARNING: window.hilightRow(sampledate) exception: {}".format(
                                    exstr
                                )
                            )
                else:
                    print(
                        "%s: timeChange7 movechart window %s"
                        % (os.path.basename(__file__), window_title)
                    )
                    window.moveChart(sampledate)
            self.update_from_data_table = None
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
        tt = f"Synced: {self.gc.currentDateTimeString}"
        # get last lat/lon df
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            sql = sql_utils.sql_lh_time_match_for_select_from_part(
                "select log_hash, time, positioning_lat as lat, positioning_lon as lon from location",
                self.gc.selected_row_log_hash,
                self.gc.currentDateTimeString,
                lookback_secs=5)
            loc_df = pd.read_sql(sql, dbcon).dropna()
            if len(loc_df):
                loc_df = loc_df.sort_values("time", ascending=False)
                tt += f" @ {'%.05f' % float(loc_df.lat.iloc[0])}, {'%.05f' % float(loc_df.lon.iloc[0])}"
        gp = self.get_global_top_params()
        if gp:
            tt += "\n"+gp
        if self.gc.default_top_params_font_size_override is not None:
            self.ui.top_label.setStyleSheet(
                """
                * {
                font-size: %dpt;
                }                
                """ % self.gc.default_top_params_font_size_override
            )
        self.ui.top_label.setText(tt)


    def get_global_top_params(self):
        ret = ""
        with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
            try:
                rat_to_params_to_col_dict = {
                    "NR": [
                        {
                            "RSRP": "nr_servingbeam_ss_rsrp_1",
                            "SINR": "nr_servingbeam_ss_sinr_1",
                        },
                        {
                            "Band": "nr_band_1",
                            "ARFCN": "nr_dl_arfcn_1",
                            "PCI": "nr_servingbeam_pci_1",
                        }
                    ],
                    "LTE": [
                        {
                        "RSRP": "lte_inst_rsrp_1",
                        "SINR": "lte_sinr_1",
                        },
                        {
                        "Band": "lte_band_1",
                        "EARFCN": "lte_earfcn_1",
                        "PCI": "lte_physical_cell_id_1",
                        "Enb": "lte_sib1_enb_id",
                        "lci": "lte_sib1_local_cell_id",
                        }
                    ],
                    "WCDMA": [
                        {
                        "RSCP": "wcdma_aset_rscp_1",
                        "Ec/Io": "wcdma_aset_ecio_1",
                        },
                        {
                        "UARFCN": "wcdma_aset_cellfreq_1",
                        "PSC": "wcdma_aset_sc_1",
                        }
                    ],
                    "GSM": [
                        {
                        "RxLev": "gsm_rxlev_sub_dbm",
                        "RxQual": "gsm_rxqual_sub",
                        },
                        {
                        "ARFCN": "gsm_arfcn_bcch",
                        "BSIC": "gsm_bsic",
                        }
                    ]
                }
                for rat, params_to_col_dict_list in rat_to_params_to_col_dict.items():
                    this_rat_got_vals = False
                    rows = []
                    for params_to_col_dict in params_to_col_dict_list:
                        row_ret = ""
                        for pname, col in params_to_col_dict.items():
                            try:
                                table = preprocess_azm.get_table_for_column(col)
                                sql = f"SELECT time, {col} FROM {table}"
                                import azq_theme_manager
                                is_id = azq_theme_manager.is_param_col_an_id(col)
                                lookback_secs = 3600*24 if is_id else 5
                                print("top_params lookback_secs:", lookback_secs)
                                sql = sql_utils.sql_lh_time_match_for_select_from_part(sql, self.gc.selected_row_log_hash, self.gc.currentDateTimeString, lookback_secs=lookback_secs)
                                sql += f"and {col} is not null"
                                print("top_params sql:", sql)
                                df = pd.read_sql(sql, dbcon).sort_values("time", ascending=False)
                                print("top_params df:", df)
                                if not df.empty and df.last_valid_index() is not None:
                                    val = df.iloc[0, 1]
                                    if pd.notnull(val):
                                        try:
                                            if "." in str(val):
                                                val = "%.02f" % float(val)
                                            else:
                                                val = int(val)
                                        except:
                                            pass
                                        row_ret += f" {pname}: {val}"
                                        if not is_id:
                                            print("top_params this_rat_got_vals")
                                            this_rat_got_vals = True
                            except:
                                type_, value_, traceback_ = sys.exc_info()
                                exstr = str(traceback.format_exception(type_, value_, traceback_))
                                print(
                                    "WARNING: get_global_top_params inner sql exception: {}".format(
                                        exstr
                                    )
                                )
                        if row_ret:
                            rows.append(row_ret)
                    if this_rat_got_vals:
                        ret = rat + ":"+"\n".join(rows)
                        print("this_rat_got_vals ret", ret)
                        break
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print(
                    "WARNING: get_global_top_params exception: {}".format(
                        exstr
                    )
                )
        return ret


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
            if self.gc.live_mode:
                self.gc.live_mode = False
                if self.gc.live_mode_update_time:
                    self.switch_live_mode()
                for process in self.gc.live_process_list:
                    os.kill(process.pid, signal.SIGTERM)
                    # os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                self.gc.live_process_list = []
            self.save_current_workspace()
            self.pauseTime()

            # remove selected features:
            self.clear_highlights()
            self.gc.device_configs = []
            
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

    def showLayer(self, layer_name, show=True):
        layer = QgsProject.instance().mapLayersByName(layer_name)[0]
        QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(show)

    def hideAllLayers(self):
        project = QgsProject.instance()
        for layer in project.mapLayers().values():
            QgsProject.instance().layerTreeRoot().findLayer(layer.id()).setItemVisibilityChecked(False)

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
                        if "Line Chart" not in window.widget().title:
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_custom_df".format(i),
                                window.widget().custom_df,
                            )
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_custom_table_param_list".format(i),
                                window.widget().custom_table_param_list,
                            )
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_custom_last_instant_table_param_list".format(i),
                                window.widget().custom_last_instant_table_param_list,
                            )
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_refresh_df_func_or_py_eval_str".format(i),
                            window.widget().refresh_data_from_dbcon_and_time_func,
                            )
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_options".format(i),
                                json.dumps(window.widget().options),
                            )
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_selected_ue".format(i),
                                window.widget().selected_ue,
                            )
                        else:
                            print(window.widget().paramList, window.widget().eventList)
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_linechart_param_list".format(i),
                                json.dumps(window.widget().paramList),
                            )
                            self.current_workspace_settings.setValue(
                                GUI_SETTING_NAME_PREFIX + "window_{}_linechart_event_list".format(i),
                                json.dumps(window.widget().eventList),
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
                self.on_actionServer_overview_layers_triggered()
                self.on_actionServerAIPrediction_triggered()
                print("load POI layer")
                self.pre_load_poi_layer()

    def pre_load_poi_layer(self):
        import qgis_layers_gen
        print("load POI layer start")
        qgis_poi_preload_path = "/host_shared_dir/resource/viewPreference/qgis_poi_preload/"
        if os.path.exists(qgis_poi_preload_path):
            for root, dirs, files in os.walk(qgis_poi_preload_path):
                for file in files:
                    poi_path = os.path.join(root,file)
                    qgis_layers_gen.create_qgis_poi_layer(self.gc, poi_path)


    
    def add_spider_layer(self):
        import spider_plot
        import azq_cell_file
        print("add_spider_layer self.gc.cell_files:", self.gc.cell_files)
        if not self.gc.cell_files:
            print("add_spider_layer self.gc.cell_files no cellfiles so omit")
            return
        if self.gc.overview_opened:  # dont add spider in overview mode
            print("add_spider_layer overview_opened so omit otherwise will draw too many lines")
            return
        # try:
        #     azq_cell_file.read_cellfiles(self.gc.cell_files, "lte", add_cell_lat_lon_sector_distance_meters=0.001)
        # except Exception as e:
        #     qt_utils.msgbox("Failed to load the sepcified cellfiles: {}".format(str(e)), title="Invalid cellfiles", parent=self)
        #     return
        for rat in azq_cell_file.CELL_FILE_RATS:
            options_dict = {"distance_limit_m": int(self.gc.pref["spider_match_max_distance_meters"])}
            pref_key = "cell_{}_sector_size_meters".format(rat)
            sector_size_meters = float(self.gc.pref[pref_key])
            options_dict["sector_size_meters"] = sector_size_meters
            freq_code_match_mode = self.gc.pref["spider_match_cgi"] == "0"
            spider_plot.plot_rat_spider(self.gc.cell_files, self.gc.databasePath, rat, options_dict=options_dict, freq_code_match_mode=freq_code_match_mode)

    def add_indoor_map_layers(self):
        ue = 1
        for log_hash in self.gc.log_list:
            rotate_indoor_map_path = os.path.join(self.gc.logPath, str(log_hash), "map_rotated.png")
            indoor_map_path = os.path.join(self.gc.logPath, str(log_hash), "map.jpg")
            tif_map_path = os.path.join(self.gc.logPath, str(log_hash), "map_rotated.tif")
            indoor_map_layer_name = "indoor_map"
            if len(self.gc.log_list) > 1:
                 indoor_map_layer_name = indoor_map_layer_name + "_" + str(ue)
            from PIL import Image
            is_rotate_indoor_map = False
            if os.path.isfile(rotate_indoor_map_path) and self.gc.real_world_indoor == True:
                indoor_map_path = rotate_indoor_map_path
                is_rotate_indoor_map = True
            if os.path.isfile(indoor_map_path):
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
                        indoor_bg_df = pd.read_sql("select * from indoor_background_img where log_hash = {}".format(log_hash), dbcon)
                        if len(indoor_bg_df) > 0 and self.gc.real_world_indoor == True:
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
                self.qgis_iface.addRasterLayer(tif_map_path, indoor_map_layer_name)
            ue += 1
            
        return

    def add_cell_layers(self):
        print("add_cell_layers self.gc.cell_files:", self.gc.cell_files)
        if not self.gc.cell_files:
            return
        if self.gc.cell_files:
            import azq_cell_file
            import azq_utils
            import cell_layer_task
            rrv = azq_cell_file.CELL_FILE_RATS.copy()
            rrv.reverse()  # by default gsm is biggest so put it at the bottom
            rat_count = len(rrv)
            current_rat_index = 0
            load_cellfile_progress = 100 / rat_count
            for rat in rrv:
                try:
                    layer_name = rat.upper() + "_cells"
                    pref_key = "cell_{}_sector_size_meters".format(rat)
                    sector_size_meters = float(self.gc.pref[pref_key])
                    df = azq_cell_file.read_cellfiles(self.gc.cell_files, rat, add_sector_polygon_wkt_sector_size_meters=sector_size_meters)
                    self.open_cellfile_progress_signal.emit(load_cellfile_progress*(current_rat_index) + (load_cellfile_progress * 0.4))
                    if len(df) > 20000:
                        df = df.reset_index()

                        create_cellfile_sql_str = azq_utils.get_create_cellfile_spatialite_header(rat)
                        create_cellfile_sql_str += azq_utils.get_create_cellfile_spatialite_create_table(rat,
                                                                                                         list(df.columns))
                        create_cellfile_sql_str += azq_utils.get_create_cellfile_spatialite_insert_cell(rat, df)
                        create_cellfile_sql_str += azq_utils.get_create_cellfile_spatialite_footer()
                        cell_sql_fp = os.path.join(azq_utils.tmp_gen_path(), "cell_file_sectors_{}_".format(uuid.uuid4()) + rat + ".sql")
                        f = open(cell_sql_fp, 'w')
                        f.write(create_cellfile_sql_str)
                        f.close()
                        spatialite_bin = azq_utils.get_spatialite_bin()
                        self.open_cellfile_progress_signal.emit(load_cellfile_progress*(current_rat_index) + (load_cellfile_progress * 0.5))
                        cel_spatial_db_fp = cell_sql_fp[:-3]+"db"
                        if os.path.isfile(cel_spatial_db_fp):
                            os.remove(cel_spatial_db_fp)
                        cmd = [spatialite_bin, "-init", cell_sql_fp, cel_spatial_db_fp, ".quit"]
                        azq_utils.call_no_shell(cmd)
                        if len(df):
                            uri = QgsDataSourceUri()
                            uri.setDatabase(cel_spatial_db_fp)
                            schema = ''
                            table = rat
                            geom_column = 'geometry'
                            uri.setDataSource(schema, table, geom_column)
                            layer = QgsVectorLayer(uri.uri(), layer_name, 'spatialite')
                    else:
                        layer_name = rat.upper() + "_cells"
                        pref_key = "cell_{}_sector_size_meters".format(rat)
                        sector_size_meters = float(self.gc.pref[pref_key])
                        df = azq_cell_file.read_cellfiles(self.gc.cell_files, rat,
                                                          add_sector_polygon_wkt_sector_size_meters=sector_size_meters)
                        csv_fp = os.path.join(azq_utils.tmp_gen_path(), "cell_file_sectors_" + rat + ".csv")
                        if len(df):
                            df.to_csv(csv_fp, encoding='utf-8')
                            uri = pathlib.Path(csv_fp).as_uri()
                            uri += "?crs=epsg:4326&wktField={}".format('sector_polygon_wkt')
                            print("csv uri: {}".format(uri))
                            layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
                    self.open_cellfile_progress_signal.emit(load_cellfile_progress*(current_rat_index) + (load_cellfile_progress * 0.6))

                    if len(df):
                        try:
                            param_att_rat = {'gsm': 'bcch', 'wcdma': 'psc', 'lte': 'pci', 'nr': 'pci'}
                            param_db_rat = {'gsm': 'gsm_arfcn_bcch', 'wcdma': 'wcdma_aset_sc_1', 'lte': 'lte_physical_cell_id_1', 'nr': 'nr_servingbeam_pci_1'}
                            param_name_in_cell = param_att_rat[rat]
                            param_name_in_db = param_db_rat[rat]
                            color_range_list = []
                            if not self.gc.db_fp:
                                raise Exception(
                                    "not self.gc.db_fp so raise exception here to omit cell color/spider match as it will fail")
                            if self.gc.overview_opened:
                                raise Exception("self.gc.overview_opened so raise exception here to omit cell color/spider match as it will fail")
                            param_with_color_df = cell_layer_task.cell_in_logs_with_color(self.gc.cell_files, self.gc.databasePath, rat)
                            param_with_color_df[param_name_in_db] = param_with_color_df[param_name_in_db].astype(int)
                            self.open_cellfile_progress_signal.emit(load_cellfile_progress*(current_rat_index) + (load_cellfile_progress * 0.7))
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
                            self.open_cellfile_progress_signal.emit(load_cellfile_progress*(current_rat_index) + (load_cellfile_progress * 0.8))
                        except:
                            type_, value_, traceback_ = sys.exc_info()
                            exstr = str(traceback.format_exception(type_, value_, traceback_))
                            print("WARNING: add cell file color for rat {} - exception: {}".format(rat, exstr))
                        self.cellfile_layer_created_signal.emit(layer)
                        pass
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: add cell file for rat {} - exception: {}".format(rat, exstr))
                self.open_cellfile_progress_signal.emit(load_cellfile_progress*(current_rat_index) + (load_cellfile_progress * 1))
                current_rat_index += 1
            self.open_cellfile_complete_signal.emit()
            return
        else:
            self.on_load_cellfile_error_signal.emit("No cell-files specified")


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
                        custom_df = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_custom_df".format(i)
                        )

                        custom_table_param_list = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_custom_table_param_list".format(i)
                        )

                        custom_last_instant_table_param_list = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_custom_last_instant_table_param_list".format(i)
                        )

                        hh_state = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_table_horizontal_headerview_state".format(i)
                        )

                        refresh_df_func_or_py_eval_str = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_refresh_df_func_or_py_eval_str".format(i)
                        )

                        selected_ue = self.current_workspace_settings.value(
                            GUI_SETTING_NAME_PREFIX + "window_{}_selected_ue".format(i)
                        )

                        if "Line Chart" not in title:
                            options = json.loads(self.current_workspace_settings.value(
                                GUI_SETTING_NAME_PREFIX + "window_{}_options".format(i)
                            ))
                        else:
                            linechart_event_list =  json.loads(self.current_workspace_settings.value(
                                GUI_SETTING_NAME_PREFIX + "window_{}_linechart_event_list".format(i)
                            ))

                            linechart_param_list =  json.loads(self.current_workspace_settings.value(
                                GUI_SETTING_NAME_PREFIX + "window_{}_linechart_param_list".format(i)
                            ))


                        print("load_current_workspace() window i: {} title: {}".format(i, title))
                        
                        if func is not None:
                            # on..._triggered func like on L3 triggered etc
                            func_key = "self." + func
                            if selected_ue is not None:
                                func_key = func_key + "(selected_ue = {})".format(selected_ue)
                            elif len(linechart_param_list) > 0 or len(linechart_event_list) > 0 :
                                func_key = func_key + "(paramList = {}, eventList = {})".format(linechart_param_list, linechart_event_list)
                            else:
                                func_key = func_key + "()"
                            print(func_key)
                            eval(func_key)
                        elif custom_df is not None and custom_table_param_list is not None:
                            self.add_param_window(custom_df = custom_df, custom_table_param_list=custom_table_param_list, title=title, options=options, selected_ue=selected_ue)
                        elif custom_last_instant_table_param_list is not None:
                            self.add_param_window(custom_df = custom_last_instant_table_param_list, custom_last_instant_table_param_list=custom_last_instant_table_param_list, title=title, options=options, selected_ue=selected_ue)
                        else:
                            # like for custom windows - newer style
                            self.add_param_window(refresh_df_func_or_py_eval_str, title=title, options=options, selected_ue=selected_ue)

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
