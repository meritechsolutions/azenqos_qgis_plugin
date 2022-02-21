import pandas as pd
import sqlite3
import contextlib
import os
import sys
import traceback
import threading
import shutil
import datetime
from PyQt5 import QtCore, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QProgressBar
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QRadioButton,
    QFileDialog,
)

import azq_utils
import qt_utils
import preprocess_azm

class open_multiple_ue_dialog(QDialog):
    import_done_signal = pyqtSignal(str)
    
    def __init__(self, parent_window, gc):
        super(open_multiple_ue_dialog, self).__init__(parent=parent_window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.import_done_signal.connect(self.ui_handler_import_done)
        self.gc = gc
        self.gc.device_configs = []
        self.parent_window = parent_window
        self.ue_list = []
        self.log_name_by_ue_list = []
        self.log_path_by_ue_list = []
        self.all_log_path_list = []
        self.import_thread = None
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("open_multiple_ue_dialog.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.load_settings()
        self.ui.remove_ue_button.setEnabled(False)
        self.ui.add_logs_button.setEnabled(False)
        self.ui.remove_log_button.setEnabled(False)
        self.ui.add_ue_button.clicked.connect(self.on_add_ue_button_click)
        self.ui.add_logs_button.clicked.connect(self.on_add_logs_button_click)
        self.ui.remove_ue_button.clicked.connect(self.on_remove_ue_button_click)
        self.ui.remove_log_button.clicked.connect(self.on_remove_log_button_click)
        self.ui.ue_list_widget.itemClicked.connect(self.on_ue_selected)
        self.ui.log_list_widget.itemClicked.connect(self.on_log_selected)
        self.ui.select_theme_button.clicked.connect(self.choose_theme)
        self.ui.open_log_button.clicked.connect(self.on_ok_button_click)

    def on_add_ue_button_click(self):
        ue_name = qt_utils.ask_text(
            self, "Add UE", "Please specify UE name:"
        )
        if ue_name:
            if ue_name in self.ue_list:
                qt_utils.msgbox("UE already exists")
                return
            self.gc.device_configs.append({"name":ue_name, "log_hash":[]})
            self.ui.ue_list_widget.addItem(ue_name)
            self.ue_list.append(ue_name)
            self.log_name_by_ue_list.append([])
            self.log_path_by_ue_list.append([])

    def on_add_logs_button_click(self):
        file_path_list, _ = QFileDialog.getOpenFileNames(
            self, "Select files", QtCore.QDir.rootPath(), "AZENQOS azm logs (*.azm);; SQLite db from azm (*.db)"
        )
        for file_path in file_path_list:
            file_basename = os.path.basename(file_path)
            if file_basename not in self.log_name_by_ue_list[self.ui.ue_list_widget.currentRow()]:
                reply = 0
                if file_path in self.all_log_path_list:
                    reply = qt_utils.ask_yes_no(None, "Add logs", "{} already exists in other UE, Do you want to add?".format(file_basename))
                if reply == 0:
                    self.log_name_by_ue_list[self.ui.ue_list_widget.currentRow()].append(file_basename)
                    self.log_path_by_ue_list[self.ui.ue_list_widget.currentRow()].append(file_path)
                    self.ui.log_list_widget.addItem(file_basename)
        self.all_log_path_list = [item for sublist in self.log_path_by_ue_list for item in sublist]

    def on_remove_ue_button_click(self):
        remove_index = self.ue_list_widget.currentRow()
        reply = qt_utils.ask_yes_no(None, "Romove UE", "Do you want to romove {}?".format(self.gc.device_configs[remove_index]["name"]))
        if reply == 0:
            self.ue_list_widget.takeItem(remove_index)
            self.log_name_by_ue_list.pop(remove_index)
            self.log_path_by_ue_list.pop(remove_index)
            self.gc.device_configs.pop(remove_index)
            self.all_log_path_list = [item for sublist in self.log_path_by_ue_list for item in sublist]
            self.ui.log_list_widget.clear()
    
    def on_remove_log_button_click(self):
        remove_index = self.log_list_widget.currentRow()
        self.log_list_widget.takeItem(remove_index)
        self.log_name_by_ue_list[self.ui.ue_list_widget.currentRow()].pop(remove_index)
        self.log_path_by_ue_list[self.ui.ue_list_widget.currentRow()].pop(remove_index)
        self.all_log_path_list = [item for sublist in self.log_path_by_ue_list for item in sublist]


    def on_ue_selected(self,item):
        self.ui.remove_ue_button.setEnabled(True)
        self.ui.remove_log_button.setEnabled(False)
        self.ui.add_logs_button.setEnabled(True)
        self.ui.log_list_widget.clear()
        self.ui.log_list_widget.addItems(list(set(self.log_name_by_ue_list[self.ui.ue_list_widget.currentRow()])))


    def on_log_selected(self,item):
        self.ui.remove_ue_button.setEnabled(False)
        self.ui.remove_log_button.setEnabled(True)
    
    def choose_theme(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Select file", QtCore.QDir.rootPath(), "*.xml"
        )
        self.ui.theme_line_edit.setText(
            fileName
        ) if fileName else self.ui.theme_line_edit.setText("Default")

    def save_settings(self):
        import azq_utils
        azq_utils.write_settings_file("config_prev_theme", self.ui.theme_line_edit.text())

    def load_settings(self):
        tp = azq_utils.read_settings_file("config_prev_theme")
        self.ui.theme_line_edit.setText(tp) if tp else self.ui.theme_line_edit.setText(
            "Default"
        )
    
    def on_ok_button_click(self):
        
        try:
            index = 0
            for path_list in self.log_path_by_ue_list:
                for db_path in path_list:
                    
                    tmp_dir = os.path.join(azq_utils.tmp_gen_path(), "tmp_combine_azm_{}".format(index))
                    if db_path.endswith(".azm") or db_path.endswith(".zip"):
                        new_dbfp = os.path.join(tmp_dir, "azqdata.db")
                        if os.path.exists(new_dbfp):
                            os.remove(new_dbfp)
                        preprocess_azm.extract_entry_from_zip(db_path, "azqdata.db", tmp_dir)
                        with contextlib.closing(sqlite3.connect(new_dbfp)) as dbcon:
                            log_hash = str(pd.read_sql("select log_hash from logs limit 1", dbcon)["log_hash"][0])
                            self.gc.device_configs[index]["log_hash"].append(log_hash)
                    elif db_path.endswith(".db"):
                        with contextlib.closing(sqlite3.connect(new_dbfp)) as db_path:
                            log_hash = str(pd.read_sql("select log_hash from logs limit 1", dbcon)["log_hash"][0])
                            self.gc.device_configs[index]["log_hash"].append(log_hash)
                index += 1
            self.setEnabled(False)
            ret = self.start_import_thread(self.all_log_path_list)
            if not ret:
                self.setEnabled(True) 
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: _check_and_start_import exception: {}".format(
                    exstr
                )
            )
            qt_utils.msgbox("Open failed: " + exstr, title="Failed", parent=self)
            self.setEnabled(True)
        print(self.gc.device_configs)
        
    def start_import_thread(self, zip_fp):
        try:
            self.save_settings()
            if not self.ui.theme_line_edit.text():
                QtWidgets.QMessageBox.critical(
                    None,
                    "No theme chosen",
                    "Please choose a theme xml to use...",
                    QtWidgets.QMessageBox.Cancel,
                )
                return

            if self.ui.theme_line_edit.text() != "Default" and not os.path.isfile(
                self.ui.theme_line_edit.text()
            ):
                QtWidgets.QMessageBox.critical(
                    None,
                    "Theme file not found",
                    "Please choose a theme xml to use...",
                    QtWidgets.QMessageBox.Cancel,
                )
                return
            self.setWindowTitle("Please wait... opening logs")
            self.setEnabled(False)
            if self.import_thread is None or (self.import_thread.is_alive() == False):
                self.zip_fp = list(set(zip_fp))
                # self.buttonBox.setEnabled(False)
                print("start import db zip thread...")
                # self.import_thread_run()
                self.import_thread = threading.Thread(
                    target=self.import_thread_run, args=(), daemon=True
                )
                self.import_thread.start()
            else:
                print("already importing - please wait...")
                QtWidgets.QMessageBox.critical(
                    self,
                    "Please wait...",
                    "Log import is still loading...",
                    QtWidgets.QMessageBox.Ok,
                )
            """
            self.azenqosMainMenu = AzenqosDialog(self)
            self.azenqosMainMenu.show()
            self.azenqosMainMenu.raise_()
            self.azenqosMainMenu.activateWindow()
            """
            return True
        except Exception as ex:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: open log failed exception:", exstr)
            QtWidgets.QMessageBox.critical(
                self,
                "Open log failed",
                "Error: {}\n\nTrace:\n{}".format(ex, exstr),
                QtWidgets.QMessageBox.Cancel,
            )
            return False

    def import_thread_run(self):
        zip_fp = self.zip_fp
        success = False
        try:
            import preprocess_azm
            azq_utils.cleanup_died_processes_tmp_folders()
            azq_utils.tmp_gen_new_instance()

            if isinstance(zip_fp, list):
                if len(zip_fp) == 1:
                    zip_fp = zip_fp[0]
                else:
                    print("zip_fp is list - merging them into one db first...")
                    import azm_sqlite_merge
                    zip_fp = azm_sqlite_merge.merge(zip_fp)
            print("using log:", zip_fp)
            assert isinstance(zip_fp, str)
            assert os.path.isfile(zip_fp)
            if zip_fp.endswith(".azm") or zip_fp.endswith(".zip"):
                self.databasePath = preprocess_azm.extract_entry_from_zip(
                    zip_fp, "azqdata.db", azq_utils.tmp_gen_path()
                )
                with contextlib.closing(sqlite3.connect(self.databasePath)) as dbcon:
                    log_hash = pd.read_sql("SELECT log_hash FROM logs LIMIT 1;",dbcon).log_hash[0]
                    out_tmp_each_log_dir = os.path.join(azq_utils.tmp_gen_path(), str(log_hash))
                    preprocess_azm.extract_all_from_zip(zip_fp, out_tmp_each_log_dir)
            elif zip_fp.endswith(".db"):
                databasePath = os.path.join(azq_utils.tmp_gen_path(), "azqdata.db")
                shutil.copy(zip_fp, databasePath)
                self.databasePath = databasePath
            else:
                raise Exception("unsupported file extension: {}".format(zip_fp))

            assert os.path.isfile(self.databasePath)
            
            ret = self.addDatabase()  # this will create views/tables per param as per specified theme so must check theme before here
            if not ret:
                raise Exception(
                    "Failed to open azqdata.db file inside the unzipped supplied azm file"
                )
            else:
                self.import_done_signal.emit("")
                success = True
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: import_selection() failed exception:", exstr)
            self.import_done_signal.emit(exstr)

    def ui_handler_import_done(self, error):
        if error:
            self.setEnabled(True)
            print("ui_handler_import_done() error: %s" % error)
            QtWidgets.QMessageBox.critical(
                None, "Failed", error, QtWidgets.QMessageBox.Cancel,
            )
            return False
        else:
            print("ui_handler_import_done() success")
            try:
                self.getTimeForSlider()
                print("getTimeForSlider() done")
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: getTimeForSlider() failed exception:", exstr)
            self.close()

    def getTimeForSlider(self):
        startTime = None
        endTime = None
        with contextlib.closing(sqlite3.connect(self.databasePath)) as dbcon:
            df = pd.read_sql(
                "select min(log_start_time) as startTime, max(log_end_time) as endTime from logs",
                dbcon,
            )
            assert len(df) == 1
            startTime = df.iloc[0].startTime
            endTime = df.iloc[0].endTime
            if not endTime:
                df = pd.read_sql(
                    "select max(time) as endTime from events",
                    dbcon,
                )
                endTime = df.iloc[0].endTime

        assert startTime
        assert endTime
        self.gc.minTimeValue = datetime.datetime.strptime(
            str(startTime), "%Y-%m-%d %H:%M:%S.%f"
        ).timestamp()
        self.gc.maxTimeValue = datetime.datetime.strptime(
            str(endTime), "%Y-%m-%d %H:%M:%S.%f"
        ).timestamp()
        self.gc.currentDateTimeString = "%s" % (
            datetime.datetime.fromtimestamp(self.gc.minTimeValue)
        )
        self.gc.currentTimestamp = self.gc.minTimeValue
        print("gettimeforslider self.gc.currentTimestamp", self.gc.currentTimestamp)
        self.setIncrementValue()
        return True

    def setIncrementValue(self):
        self.gc.sliderLength = self.gc.maxTimeValue - self.gc.minTimeValue
        self.gc.sliderLength = round(self.gc.sliderLength, 3)

    def addDatabase(self):
        # check db
        assert os.path.isfile(self.databasePath)
        with contextlib.closing(sqlite3.connect(self.databasePath)) as dbcon:
            try:
                try:
                    logs_df = pd.read_sql("select * from logs limit 1", dbcon)
                    if not len(logs_df):
                        print("warning: invalid log database - cant read log metadata")
                    log_hash = logs_df.iloc[0].log_hash
                    if not log_hash:
                        print("invalid log database - cant read log_hash")
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: check db failed exception:", exstr)

                self.gc.params_to_gen = {}
                # check theme
                import import_db_dialog
                import db_preprocess
                import_db_dialog.check_theme(theme_fp = self.ui.theme_line_edit.text())
                db_preprocess.prepare_spatialite_views(dbcon, gc = self.gc)
                dbcon.close()  # in some rare cases 'with' doesnt flush dbcon correctly as close()

                assert self.databasePath
                self.gc.databasePath = self.databasePath
                self.gc.logPath = azq_utils.tmp_gen_path()
                self.gc.db_fp = self.gc.databasePath

            finally:
                try:
                    dbcon.close()
                except:
                    pass
            return True

    def reject(self):
        super().reject()