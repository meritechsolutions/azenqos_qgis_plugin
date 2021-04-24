import datetime
import shutil
import threading
import traceback

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QSettings, pyqtSlot, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QPixmap, QIcon
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

import qt_utils, azq_utils
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
        QgsRectangle,
        QgsGeometry,
        QgsMessageLog,
        QgsFeatureRequest,
        QgsApplication,
    )

    # from qgis.utils import
    from qgis.gui import QgsMapToolEmitPoint, QgsHighlight

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
    import tasks
except:
    pass
from atomic_int import atomic_int
import import_db_dialog
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


class main_window(QMainWindow):

    signal_ui_thread_emit_time_slider_updated = pyqtSignal(float)

    def __init__(self, qgis_iface):
        super(main_window, self).__init__(None)

        azq_utils.cleanup_died_processes_tmp_folders()

        ######## instance vars
        self.closed = False
        self.gc = analyzer_vars.analyzer_vars()
        self.gc.qgis_iface = qgis_iface
        self.timechange_service_thread = None
        self.timechange_to_service_counter = atomic_int(0)
        self.signal_ui_thread_emit_time_slider_updated.connect(
            self.ui_thread_emit_time_slider_updated
        )
        self.dbfp = None
        self.qgis_iface = qgis_iface
        self.timeSliderThread = timeSliderThread(self.gc)
        self.settings = QSettings(
            azq_utils.get_local_fp("settings.ini"), QSettings.IniFormat
        )
        ########################

        self.setupUi()

        if self.qgis_iface is None:
            print("analyzer_window: standalone mode")
        else:
            print("analyzer_window: qgis mode")
            self.canvas = qgis_iface.mapCanvas()
            self.clickTool = QgsMapToolEmitPoint(self.canvas)
            self.canvas.setMapTool(self.clickTool)
            self.clickTool.canvasClicked.connect(self.clickCanvas)
            self.canvas.selectionChanged.connect(self.selectChanged)
            QgsProject.instance().layersAdded.connect(self.renamingLayers)
            root = QgsProject.instance().layerTreeRoot()
            root.addedChildren.connect(self.mergeLayerGroup)
            QgsProject.instance().layerWillBeRemoved.connect(self.removingTreeLayer)

        self.timechange_service_thread = Worker(self.timeChangedWorkerFunc)
        self.gc.threadpool.start(self.timechange_service_thread)

        print("main_window __init__() done")

    @pyqtSlot()
    def on_actionExit_triggered(self):
        print("exit")
        self.close()

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
        return self.gc.login_dialog and self.gc.login_dialog.token

    ############# system menu slots
    @pyqtSlot()
    def on_actionTechnology_triggered(self):
        print("technology")
        import system_query

        headers = ["log_hash", "time", "main_param", "rat"]
        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "Technology",
            system_query.get_technology_df,
            tableHeader=headers,
            time_list_mode=True,
            l3_alt_wireshark_decode=True,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# signalling menu slots
    @pyqtSlot()
    def on_actionLayer_3_Messages_triggered(self):
        print("action l3")
        import signalling_query

        headers = ["log_hash", "time", "name", "dir", "protocol", "detail"]
        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "Layer-3 Messages",
            signalling_query.get_signalling,
            tableHeader=headers,
            time_list_mode=True,
            l3_alt_wireshark_decode=True,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionEvents_triggered(self):
        print("action events")
        import signalling_query

        headers = ["log_hash", "time", "name", "info"]
        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "Events",
            signalling_query.get_events,
            tableHeader=headers,
            time_list_mode=True,
            event_mos_score=True,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# NR menu slots

    @pyqtSlot()
    def on_action5GNR_Radio_Parameters_triggered(self):
        print("action nr radio params")
        import nr_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "5GNR Radio Parameters",
            nr_query.get_nr_radio_params_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_action5GNR_Serving_Neighbors_triggered(self):
        print("action nr serving neigh")
        import nr_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "5GNR Serving + Neighbors",
            nr_query.get_nr_serv_and_neigh_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# LTE menu slots
    @pyqtSlot()
    def on_actionLTE_Radio_Parameters_triggered(self):
        print("action lte radio params")
        import lte_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "LTE Radio Parameters",
            lte_query.get_lte_radio_params_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionLTE_Serving_Neighbors_triggered(self):
        print("action lte serving neigh")
        import lte_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "LTE Serving + Neighbors",
            lte_query.get_lte_serv_and_neigh_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionLTE_Data_Params_triggered(self):
        print("action lte data param")
        import lte_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "LTE Data Params",
            lte_query.get_lte_data_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionLTE_PUCCH_PDSCH_Params_triggered(self):
        print("action lte pucch pdsch param")
        import lte_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "LTE PUCCH/PDSCH Params",
            lte_query.get_lte_pucch_pdsch_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionLTE_RRC_SIB_States_triggered(self):
        print("action lte rrc sib states")
        import lte_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "LTE RRC/SIB States",
            lte_query.get_lte_rrc_sib_states_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionLTE_RLC_triggered(self):
        print("action lte rlc")
        import lte_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "LTE RLC",
            lte_query.get_lte_rlc_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionLTE_VoLTE_triggered(self):
        print("action lte volte")
        import lte_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "LTE VoLTE",
            lte_query.get_volte_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# WCDMA menu slots

    @pyqtSlot()
    def on_actionWCDMA_Radio_Parameters_triggered(self):
        print("action wcdma radio params")
        import wcdma_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "WCDMA Radio Parameters",
            wcdma_query.get_wcdma_radio_params_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionWCDMA_Active_Monitored_sets_triggered(self):
        print("action wcdma active monitored")
        import wcdma_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "WCDMA Active + Monitored sets",
            wcdma_query.get_wcdma_acive_monitored_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionWCDMA_BLER_Summary_triggered(self):
        print("action wcdma bler summary")
        import wcdma_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "WCDMA BLER Summary",
            wcdma_query.get_bler_sum_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionWCDMA_Bearers_triggered(self):
        print("action wcdma bearers")
        import wcdma_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "WCDMA Bearers",
            wcdma_query.get_wcdma_bearers_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    ############# GSM menu slots

    @pyqtSlot()
    def on_actionGSM_Physical_Parameters_triggered(self):
        print("action gsm radio params")
        import gsm_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "GSM Radio Parameters",
            gsm_query.get_gsm_radio_params_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionGSM_Serving_Neighbors_triggered(self):
        print("action gsm serving neigh")
        import gsm_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "GSM Serving + Neighbors",
            gsm_query.get_gsm_serv_and_neigh__df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionGSM_Current_Channel_triggered(self):
        print("action gsm current channel")
        import gsm_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "GSM Current Channel",
            gsm_query.get_gsm_current_channel_disp_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionGSM_C_I_triggered(self):
        print("action gsm coi")
        import gsm_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "GSM C/I",
            gsm_query.get_coi_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

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

    ############# Data menu slots

    @pyqtSlot()
    def on_actionWiFi_Active_triggered(self):
        print("action wifi active")
        import data_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "WiFi Active",
            data_query.get_Wifi_active_df,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

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
        import data_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "GPRS/EDGE Information",
            data_query.get_gprs_edge_info,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionHSDPA_Statistics_triggered(self):
        print("action hadpa statistics")
        import data_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "HSDPA Statistics",
            data_query.get_hsdpa_statistics,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    @pyqtSlot()
    def on_actionHSUPA_Statistics_triggered(self):
        print("action haupa statistics")
        import data_query

        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(
            swa,
            "HSUPA Statistics",
            data_query.get_hsupa_statistics,
            func_key=inspect.currentframe().f_code.co_name,
        )
        self.add_subwindow_with_widget(swa, widget)

    def show_line_chart_dialog(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Question)
        msgBox.setText("Use Multiple Y-Axis")
        msgBox.setWindowTitle("Line Chart")
        msgBox.setStandardButtons(
            QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel
        )

        returnValue = msgBox.exec()
        return returnValue == QtWidgets.QMessageBox.Ok

    ############# Line Chart NR

    @pyqtSlot()
    def on_actionNR_Line_Chart_triggered(self):
        print("action nr line chart")
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "nr_servingbeam_ss_rsrp_1", "null": True, "data": False},
                {"name": "nr_servingbeam_ss_rsrq_1", "null": True, "data": False},
                {"name": "nr_servingbeam_ss_sinr_1", "null": True, "data": False},
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
        linechart_window.setWindowTitle("NR Line Chart")

    @pyqtSlot()
    def on_actionNR_DATA_Line_Chart_triggered(self):
        print("action nr data line chart")
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "data_trafficstat_dl/1000", "null": True, "data": True},
                {"name": "data_trafficstat_ul/1000", "null": True, "data": True},
                {
                    "name": "nr_p_plus_scell_nr_pdsch_tput_mbps",
                    "null": True,
                    "data": True,
                },
                {
                    "name": "nr_p_plus_scell_nr_pusch_tput_mbps",
                    "null": True,
                    "data": True,
                },
                {
                    "name": "nr_p_plus_scell_lte_dl_pdcp_tput_mbps",
                    "null": True,
                    "data": True,
                },
                {
                    "name": "nr_p_plus_scell_lte_ul_pdcp_tput_mbps",
                    "null": True,
                    "data": True,
                },
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
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "lte_sinr_1", "null": False, "data": False},
                {"name": "lte_inst_rsrp_1", "null": False, "data": False},
                {"name": "lte_inst_rsrq_1", "null": False, "data": False},
                {"name": "lte_inst_rssi_1", "null": False, "data": False},
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
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "data_trafficstat_dl/1000", "null": False, "data": True},
                {"name": "data_trafficstat_ul/1000", "null": False, "data": True},
                {"name": "lte_l1_throughput_mbps_1", "null": False, "data": True},
                {"name": "lte_bler_1", "null": False, "data": True},
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
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "wcdma_aset_ecio_avg", "null": False, "data": False},
                {"name": "wcdma_aset_rscp_avg", "null": False, "data": False},
                {"name": "wcdma_rssi", "null": False, "data": False},
                {
                    "name": "wcdma_bler_average_percent_all_channels",
                    "null": False,
                    "data": False,
                },
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
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "data_wcdma_rlc_dl_throughput", "null": False, "data": True},
                {"name": "data_app_dl_throughput_1", "null": False, "data": True},
                {"name": "data_hsdpa_thoughput", "null": False, "data": True},
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
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "gsm_rxlev_sub_dbm", "null": False, "data": False},
                {"name": "gsm_rxqual_sub", "null": False, "data": False},
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
        is_use_multi_y = self.show_line_chart_dialog()
        linechart_file_name = linechart_custom
        if is_use_multi_y:
            linechart_file_name = linechart_multi_y_axis
        linechart_window = linechart_file_name.LineChart(
            self.gc,
            paramList=[
                {"name": "data_gsm_rlc_dl_throughput", "null": False, "data": True},
                {"name": "data_app_dl_throughput_1", "null": False, "data": True},
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

    def add_subwindow_with_widget(self, swa, widget):
        swa.setWidget(widget)
        self.mdi.addSubWindow(swa)
        swa.show()
        self.gc.openedWindows.append(widget)

    def setupUi(self):
        self.ui = loadUi(azq_utils.get_local_fp("main_window.ui"), self)
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
            self.gc.timeSlider.setPageStep(1)
            self.gc.timeSlider.setSliderPosition(0)
            self.gc.timeSlider.setOrientation(QtCore.Qt.Horizontal)
            self.gc.timeSlider.setObjectName("timeSlider")
            self.gc.timeSlider.setTracking(True)

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
            # Load Button
            self.loadBtn = QToolButton()
            self.loadBtn.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "folder.png")))
            )
            self.loadBtn.setObjectName("loadBtn")
            self.loadBtn.setToolTip(
                "<b>Load workspace</b><br>Change the workspace windows from a saved setting"
            )

            # Save Button
            self.saveBtn = QToolButton()
            self.saveBtn.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "save.png")))
            )
            self.saveBtn.setObjectName("saveBtn")
            self.saveBtn.setToolTip(
                "<b>Save workspace</b><br>Save current workspace windows to a workspace setting file."
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

            # caused duplicated calls to pyqtslots funcs above so not using: QtCore.QMetaObject.connectSlotsByName(self)

            self.gc.timeSlider.valueChanged.connect(self.timeChange)
            self.loadBtn.clicked.connect(self.loadWorkspaceFile)
            self.saveBtn.clicked.connect(self.saveWorkspaceFile)
            self.layerSelect.clicked.connect(self.selectLayer)
            self.importDatabaseBtn.clicked.connect(self.open_logs)
            self.maptool.clicked.connect(self.setMapTool)
            self.setupToolBar()

            # self._gui_restore()

            self.setWindowTitle(
                "AZENQOS Log Replay & Analyzer tool      v.%.03f" % VERSION
            )
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: setupUi failed - exception: {}".format(exstr))

    def setupToolBar(self):
        self.toolbar.setFloatable(False)
        self.toolbar.setMovable(False)
        self.toolbar.addWidget(self.importDatabaseBtn)
        self.toolbar.addWidget(self.loadBtn)
        self.toolbar.addWidget(self.saveBtn)
        self.toolbar.addWidget(self.maptool)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.layerSelect)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.timeSliderLabel)
        self.toolbar.addWidget(self.playButton)
        self.toolbar.addWidget(self.pauseButton)
        self.toolbar.addWidget(self.gc.timeSlider)
        self.toolbar.addWidget(self.timeEdit)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.speedLabel)
        self.toolbar.addWidget(self.playSpeed)

    def renamingLayers(self, layers):

        # Configure layers data source + rename layers
        # uri = QgsDataSourceUri()
        # uri.setDatabase(self.databaseUi.databasePath)
        # root = QgsProject.instance().layerTreeRoot()
        for layer in layers:
            print("renamingLayers: ", layer.name())
            name = layer.name().split(" ")
            if name[0] == "azqdata":

                # Handle duplicate layers
                if " ".join(name[1:]) in self.gc.activeLayers:
                    toBeRemoved = QgsProject.instance().mapLayersByName(
                        " ".join(name[1:])
                    )
                    if len(toBeRemoved) > 0:
                        QgsProject.instance().removeMapLayer(toBeRemoved[0])
                        self.gc.activeLayers.remove(" ".join(name[1:]))

                # Setting up layer data source
                layer.setName(" ".join(name[1:]))
                self.gc.activeLayers.append(" ".join(name[1:]))
                # uri.setDataSource("", " ".join(name[1:]), geom_column)
                # layer.setDataSource(uri.uri(), " ".join(name[1:]), "spatialite")

                # Force adding layer to root node
                # cloneLayer = layer.clone()
                # root.insertChildNode(0, cloneLayer)
        pass

        # self.zoomToActiveLayer()

    def mergeLayerGroup(self, node, iFrom=None, iTo=None):
        if type(node) is QgsLayerTreeGroup:
            rootNode = QgsProject.instance().layerTreeRoot()
            treeGroups = rootNode.findGroups()
            layerOrder = rootNode.customLayerOrder()
            if len(treeGroups) > 0:
                for group in treeGroups:
                    groupLayers = group.findLayers()
                    for gl in groupLayers:
                        cloneLayer = gl.clone()
                        rootNode.insertChildNode(0, cloneLayer)
                    group.removeAllChildren()
            if len(self.gc.activeLayers) + 1 == len(layerOrder):
                rootNode.removeChildrenGroupWithoutLayers()

        pass

    def removingTreeLayer(self, id):
        try:
            layer = QgsProject.instance().mapLayer(id)
            self.gc.activeLayers.remove(layer.name())
        except:
            pass

    def selectChanged(self):
        if self.gc.h_list:
            for hi in self.gc.h_list:
                hi.hide()
        self.gc.h_list = []
        layer = self.qgis_iface.activeLayer()

        # layer = QgsProject.instance().mapLayersByName(layerName)[0]
        if not layer:
            return False
        if layer.type() == layer.VectorLayer:
            for i in layer.selectedFeatures():
                h = QgsHighlight(self.qgis_iface.mapCanvas(), i.geometry(), layer)

                # set highlight symbol properties
                from PyQt5.QtGui import QColor

                h.setColor(QColor(255, 0, 0, 255))
                h.setWidth(2)
                h.setFillColor(QColor(255, 255, 255, 0))

                # write the object to the list
                self.gc.h_list.append(h)

        self.qgis_iface.mapCanvas().refresh()

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
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        self.canvas.setMapTool(self.clickTool)
        self.clickTool.canvasClicked.connect(self.clickCanvas)

    def selectLayer(self):
        if self.qgis_iface:
            print("%s: selectLayer" % os.path.basename(__file__))
            self.qgis_iface.addVectorLayer(self.dbfp, None, "ogr")
            # Setting CRS
            my_crs = QgsCoordinateReferenceSystem(4326)
            QgsProject.instance().setCrs(my_crs)

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

    def ui_thread_emit_time_slider_updated(self, timestamp):
        print("ui_thread_emit_time_slider_updated")
        import datetime

        sampledate = datetime.datetime.fromtimestamp(timestamp)
        self.timeEdit.setDateTime(sampledate)

    def clickCanvas(self, point, button):
        layerData = []
        selectedTime = None
        self.clearAllSelectedFeatures()

        for layerName in self.gc.activeLayers:
            layer = None
            root = QgsProject.instance().layerTreeRoot()
            layers = root.findLayers()
            for la in layers:
                if la.name() == layerName:
                    layer = la.layer()
                    break

            if not layer:
                continue

            if layer.type() == layer.VectorLayer:
                if layer.featureCount() == 0:
                    # There are no features - skip
                    continue
                print("layer.name()", layer.name())

                # Loop through all features in a rect near point xy
                offset = 0.0005
                p1 = QgsPointXY(point.x() - offset, point.y() - offset)
                p2 = QgsPointXY(point.x() + offset, point.y() + offset)
                rect = QgsRectangle(p1, p2)
                nearby_features = layer.getFeatures(rect)
                for f in nearby_features:
                    distance = f.geometry().distance(QgsGeometry.fromPointXY(point))
                    if distance != -1.0 and distance <= 0.001:
                        closestFeatureId = f.id()
                        time = layer.getFeature(closestFeatureId).attribute("time")
                        info = (layer, closestFeatureId, distance, time)
                        layerData.append(info)

                """
                # Loop through all features in the layer
                for f in layer.getFeatures():
                    distance = f.geometry().distance(QgsGeometry.fromPointXY(point))
                    if distance != -1.0 and distance <= 0.001:
                        closestFeatureId = f.id()
                        cf = layer.getFeature(closestFeatureId)
                        print("cf.attributes:", cf.attributes())
                        print("cf.fields:", cf.fields().toList())
                        time = cf.attribute("time")
                        info = (layer, closestFeatureId, distance, time)
                        layerData.append(info)
                """

        if not len(layerData) > 0:
            # Looks like no vector layers were found - do nothing
            return

        # Sort the layer information by shortest distance
        layerData.sort(key=lambda element: element[2])

        for (layer, closestFeatureId, distance, time) in layerData:
            # layer.select(closestFeatureId)
            selectedTime = time
            break
        try:
            selectedTimestamp = azq_utils.datetimeStringtoTimestamp(
                selectedTime.toString("yyyy-MM-dd HH:mm:ss.zzz")
            )
        except:
            selectedTimestamp = azq_utils.datetimeStringtoTimestamp(selectedTime)
        if selectedTimestamp:
            timeSliderValue = self.gc.sliderLength - (
                self.gc.maxTimeValue - selectedTimestamp
            )
            self.gc.timeSlider.setValue(timeSliderValue)
            self.gc.timeSlider.update()

            # self.canvas.refreshself.gc.tableList()

    def clickCanvasWorker(self, point, button):
        print("%s: clickCanvasWorker" % os.path.basename(__file__))
        worker = Worker(self.clickCanvas, point, button)
        self.gc.threadpool.start(worker)

    def useCustomMapTool(self):
        currentTool = self.canvas.mapTool()
        if currentTool != self.clickTool:
            self.canvas.setMapTool(self.clickTool)

    def loadAllMessages(self):
        getSelected = self.presentationTreeWidget.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            if baseNode.text(0) is not None:
                getChildNode = baseNode.text(0)
                getParentNode = baseNode.parent().text(0)
                self.classifySelectedItems(getParentNode, getChildNode)

    def open_logs(self):
        if self.gc.databasePath:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Log already open")
            msgBox.setText("To open a new log, please close/exit first...")
            msgBox.addButton(QPushButton("OK"), QMessageBox.YesRole)
            msgBox.exec_()
            return

        dlg = import_db_dialog.import_db_dialog(self, self.gc)
        dlg.show()
        ret = dlg.exec()
        print("import_db_dialog ret: {}".format(ret))
        if self.gc.sliderLength:
            self.gc.timeSlider.setRange(0, self.gc.sliderLength)
        if self.gc.databasePath:
            self.ui.statusbar.showMessage(
                "Opened log db: {}".format(self.gc.databasePath)
            )
        else:
            self.ui.statusbar.showMessage("Log not opened...")
        self.updateUi()

    def timeChange(self):
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
                    self.timeChangeImpl()
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

        if len(self.gc.activeLayers) > 0:
            QgsMessageLog.logMessage("[-- have self.gc.tableList --]")
            self.hilightFeature()

        # print("%s: timeChange8" % os.path.basename(__file__))

        if len(self.gc.openedWindows) > 0:
            for window in self.gc.openedWindows:
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

    # def threadComplete(self):
    #     QgsMessageLog.logMessage('[-- THREAD COMPLETE --]')
    #     iface.mapCanvas().refresh()

    def hilightFeature(self, time_mode=True):
        if time_mode:
            self.selectFeatureOnLayersByTime()
        else:
            print("%s: hilightFeature" % os.path.basename(__file__))
            QgsMessageLog.logMessage("[-- Start hilight features --]")
            self.getPosIdsByTable()
            if len(self.posIds) > 0 and len(self.posObjs) > 0:
                self.usePosIdsSelectedFeatures()
            QgsMessageLog.logMessage("[-- End hilight features --]")

    def selectFeatureOnLayersByTime(self):
        root = QgsProject.instance().layerTreeRoot()
        layers = root.findLayers()
        for layer in layers:
            if layer.name() not in self.gc.activeLayers:
                continue
            try:
                # print("selectFeatureOnLayersByTime layer: %s" % layer.name())
                end_dt = datetime.datetime.fromtimestamp(self.gc.currentTimestamp)
                start_dt = end_dt - datetime.timedelta(
                    seconds=(params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS / 1000.0)
                )
                # 2020-10-08 15:35:55.431000
                filt_expr = "time >= '%s' and time <= '%s'" % (start_dt, end_dt)
                # print("filt_expr:", filt_expr)
                request = (
                    QgsFeatureRequest()
                    .setFilterExpression(filt_expr)
                    .setFlags(QgsFeatureRequest.NoGeometry)
                )

                layerFeatures = layer.layer().getFeatures(request)
                # print("filt request ret:", layerFeatures)
                lc = 0
                fids = []
                time_list = []
                for lf in layerFeatures:
                    lc += 1
                    fids.append(lf.id())
                    time_list.append(lf.attribute("time"))
                if len(fids):
                    sr = pd.Series(time_list, index=fids, dtype="datetime64[ns]")
                    sids = [sr.idxmax()]
                    # print("sr:", sr)
                    # print("select ids:", sids)
                    layer.layer().selectByIds(sids)
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print(
                    "WARNING: selectFeatureOnLayersByTime layer.name() {} exception: {}".format(
                        layer.name(), exstr
                    )
                )
            """
            root = QgsProject.instance().layerTreeRoot()
            root.setHasCustomLayerOrder(True)
            order = root.customLayerOrder()
            order.insert(0, order.pop(order.index(layer)))  # vlayer to the top
            root.setCustomLayerOrder(order)
            iface.setActiveLayer(layer)

            for feature in layerFeatures:
                posid = feature["posid"]
                if self.currentMaxPosId == posid:
                    selected_ids.append(feature.id())
            QgsMessageLog.logMessage("selected_ids: {0}".format(str(selected_ids)))

            if layer is not None:
                if len(selected_ids) > 0:
                    layer.selectByIds(selected_ids, QgsVectorLayer.SetSelection)
            """

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
            shutil.copyfile(fp, azq_utils.get_local_fp("settings.ini"))
            self.settings.sync()  # load changes
            self._gui_restore()
            self.settings.sync()

    def saveWorkspaceFile(self):
        from PyQt5 import QtCore

        fp, _ = QFileDialog.getSaveFileName(
            self, "Save workspace file", QtCore.QDir.rootPath(), "*.ini"
        )
        if fp:
            print("saveWorkspaceFile:", fp)
            self._gui_save()
            self.settings.sync()  # save changes
            shutil.copyfile(azq_utils.get_local_fp("settings.ini"), fp)

    def closeEvent(self, event):
        print("analyzer_window: closeEvent:", event)
        # just close it as it might be ordered by qgis close (unload()) too
        self.cleanup()
        event.accept()

        """
        reply = None
        if self.newImport is False:
            reply = QMessageBox.question(
                self,
                "Quit Azenqos",
                "Do you want to quit?",
                QMessageBox.Yes|QMessageBox.No,
                QMessageBox.Yes,
            )

        if reply == QMessageBox.Yes or self.newImport is True:
            self.cleanup()
            event.accept()
        else:
            event.ignore()
        """

    def cleanup(self):
        try:
            # self._gui_save()
            # saving = Utils().saveState(self.gc.CURRENT_PATH)
            if self.qgis_iface:
                self.qgis_iface.actionPan().trigger()
            self.pauseTime()
            self.timeSliderThread.exit()
            # self.removeToolBarActions()
            if self.qgis_iface:
                self.quitTask = tasks.QuitTask(u"Quiting Plugin", self)
                QgsApplication.taskManager().addTask(self.quitTask)

            # Begin removing layer (which cause db issue)
            if self.qgis_iface:
                project = QgsProject.instance()
                for (id_l, layer) in project.mapLayers().items():
                    if layer.type() == layer.VectorLayer:
                        layer.removeSelection()
                    to_be_deleted = project.mapLayersByName(layer.name())[0]
                    project.removeMapLayer(to_be_deleted.id())
                    layer = None

                QgsProject.instance().reloadAllLayers()
                QgsProject.instance().clear()
                # self.gc.tableList = []
                self.gc.activeLayers = []
                QgsProject.removeAllMapLayers(QgsProject.instance())

            if len(self.gc.openedWindows) > 0:
                for window in self.gc.openedWindows:
                    window.close()
                self.gc.openedWindows = []

            # End removing layer
            self.removeAzenqosGroup()
            for mdiwindow in self.mdi.subWindowList():
                print("mdiwindow close ", mdiwindow)
                mdiwindow.close()
            self.mdi.close()
            self.settings.clear()
            print("Close App")
            try:
                self.gc.close_db()
                shutil.rmtree(azq_utils.tmp_gen_path())
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: cleanup_tmp_dir() exception: %s" % exstr)
            self.closed = True
            print("cleanup done")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: cleanup() exception:", exstr)

    def removeToolBarActions(self):
        actions = self.toolbar.actions()
        for action in actions:
            self.toolbar.removeAction(action)

    def clearAllSelectedFeatures(self):
        if self.qgis_iface:
            mc = self.qgis_iface.mapCanvas()
            for layer in mc.layers():
                if layer.type() == layer.VectorLayer:
                    layer.removeSelection()
            mc.refresh()
            print("[-- Clear selected features --]")

    def removeAzenqosGroup(self):
        if self.qgis_iface:
            root = QgsProject.instance().layerTreeRoot()
            azqGroup = root.findGroup("Azenqos")
            if azqGroup:
                root.removeChildNode(azqGroup)

    def _gui_save(self):
        # mod from https://stackoverflow.com/questions/23279125/python-pyqt4-functions-to-save-and-restore-ui-widget-values
        """
        save "ui" controls and values to registry "setting"
        :return:
        """
        try:
            print("_gui_save() START")
            print("_gui_save() geom")
            self.settings.setValue(
                GUI_SETTING_NAME_PREFIX + "geom", self.saveGeometry()
            )
            print("_gui_save() state")
            self.settings.setValue(GUI_SETTING_NAME_PREFIX + "state", self.saveState())

            swl = self.mdi.subWindowList()
            swl = [w for w in swl if (w is not None and w.widget() is not None)]
            print(
                "_gui_save() len(swl)",
                len(swl),
                "len(gc.openedWindows)",
                len(self.gc.openedWindows),
            )
            self.settings.setValue(GUI_SETTING_NAME_PREFIX + "n_windows", len(swl))
            if swl:
                self.settings.setValue(GUI_SETTING_NAME_PREFIX + "n_windows", len(swl))
                i = -1
                for window in swl:
                    # window here is a subwindow: class SubWindowArea(QMdiSubWindow)
                    if not window.widget():
                        continue
                    print(
                        "_gui_save() window_{}_title".format(i), window.widget().title
                    )
                    i += 1
                    self.settings.setValue(
                        GUI_SETTING_NAME_PREFIX + "window_{}_title".format(i),
                        window.widget().title,
                    )
                    self.settings.setValue(
                        GUI_SETTING_NAME_PREFIX + "window_{}_func_key".format(i),
                        window.widget().func_key,
                    )
                    self.settings.setValue(
                        GUI_SETTING_NAME_PREFIX + "window_{}_geom".format(i),
                        window.saveGeometry(),
                    )
                    # tablewindows dont have saveState() self.settings.setValue(GUI_SETTING_NAME_PREFIX + "window_{}_state".format(i), window.saveState())

            self.settings.sync()  # save to disk
            print("_gui_save() DONE")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: _gui_save() - exception: {}".format(exstr))

    def _gui_restore(self):
        """
        restore "ui" controls with values stored in registry "settings"
        :return:
        """
        try:
            print("_gui_restore() START")
            self.settings.sync()  # load from disk
            window_geom = self.settings.value(GUI_SETTING_NAME_PREFIX + "geom")
            if window_geom:
                print("_gui_restore() geom")
                self.restoreGeometry(window_geom)
            """
            state_value = self.settings.value(GUI_SETTING_NAME_PREFIX + "state")
            if state_value:
                print("_gui_restore() state")
                self.restoreState(state_value)
            """
            n_windows = self.settings.value(GUI_SETTING_NAME_PREFIX + "n_windows")
            if n_windows:
                n_windows = int(n_windows)
                for i in range(n_windows):
                    title = self.settings.value(
                        GUI_SETTING_NAME_PREFIX + "window_{}_title".format(i)
                    )
                    geom = self.settings.value(
                        GUI_SETTING_NAME_PREFIX + "window_{}_geom".format(i)
                    )
                    func = self.settings.value(
                        GUI_SETTING_NAME_PREFIX + "window_{}_func_key".format(i)
                    )
                    print("_gui_restore() window i {} title {}".format(i, title))
                    func_key = "self." + func + "()"
                    print(func_key)
                    eval(func_key)
                    if geom:
                        for window in self.mdi.subWindowList():
                            if not window.widget():
                                continue
                            if window.widget().title == title:
                                print(
                                    "_gui_restore() window i {} title {} setgeom".format(
                                        i, title
                                    )
                                )
                                window.restoreGeometry(geom)
                                break

            print("_gui_restore() DONE")
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: _gui_restore() - exception: {}".format(exstr))
            try:
                print("doing qsettings clear()")
                self.settings.clear()
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