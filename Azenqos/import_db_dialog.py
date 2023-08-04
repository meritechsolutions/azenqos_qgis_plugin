import contextlib
import datetime
import os
import shutil
import sqlite3
import sys
# Adding folder path
import threading
import traceback
from functools import partial

import pandas as pd
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QGroupBox,
    QGridLayout,
    QRadioButton,
    QFileDialog,
    QProgressBar
)

import azq_utils
import qt_utils

sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import db_preprocess
import azq_theme_manager
import login_dialog

def check_theme(theme_fp):
    if theme_fp == "Default":
        theme_fp = azq_theme_manager.get_ori_default_theme()
    azq_theme_manager.set_default_theme_file(theme_fp)
    params_in_theme = (
        azq_theme_manager.get_matching_col_names_list_from_theme_rgs_elm()
    )
    if not params_in_theme:
        raise Exception(
            "Invalid theme file: failed to read any params from theme file: {}".format(
                theme_fp
            )
        )
    print("params_in_theme:", params_in_theme)

class import_db_dialog(QDialog):
    import_done_signal = pyqtSignal(str)
    import_status_signal = pyqtSignal(str)
    progress_update_signal = pyqtSignal(int)

    def __init__(self, parent_window, gc, connected_mode_refresh=False):
        super(import_db_dialog, self).__init__(parent=parent_window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.parent_window = parent_window
        self.import_thread = None
        self.real_world_indoor = True
        self.import_done_signal.connect(self.ui_handler_import_done)
        self.import_status_signal.connect(self.ui_handler_import_status)
        self.progress_update_signal.connect(self.progress)
        self.setupUi(self)
        self.connected_mode_refresh = connected_mode_refresh
        if self.connected_mode_refresh:
            self.setEnabled(False)
            self.radioButtonPhone.setChecked(True)
            self.check_and_start_import()

    def setupUi(self, DatabaseDialog):
        dirname = os.path.dirname(__file__)
        DatabaseDialog.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        DatabaseDialog.setObjectName("DatabaseDialog")
        DatabaseDialog.resize(640, 300)

        vbox = QVBoxLayout()
        DatabaseDialog.setLayout(vbox)
        vbox.addStretch()

        mode_gb = QGroupBox("Logs access mode")
        vbox.addWidget(mode_gb)
        vbox.addStretch()

        ########
        layout = QGridLayout()

        radiobutton = QRadioButton("Log files (.azm)")
        self.radioButtonAZM = radiobutton
        radiobutton.setChecked(True)
        radiobutton.mode = "local"
        radiobutton.toggled.connect(self.onRadioClicked)
        layout.addWidget(radiobutton, 0, 0)

        radiobutton = QRadioButton("Server log_hash list")
        self.radioButtonServer = radiobutton
        radiobutton.setChecked(False)
        radiobutton.mode = "server"
        radiobutton.toggled.connect(self.onRadioClicked)
        layout.addWidget(radiobutton, 0, 1)

        radiobutton = QRadioButton("Connected phone mode")
        self.radioButtonPhone = radiobutton
        radiobutton.setChecked(False)
        radiobutton.mode = "adb"
        radiobutton.toggled.connect(self.onRadioClicked)
        layout.addWidget(radiobutton, 0, 2)

        mode_gb.setLayout(layout)
        #####################

        #######################
        azm_gb = QGroupBox(
            "Log file (.azm from Server > Download > Processed AZM file)"
        )
        vbox.addWidget(azm_gb)
        vbox.addStretch()
        azm_gb.setEnabled(True)
        self.azm_gb = azm_gb

        theme_gb = QGroupBox(
            "Theme file (.xml from Server > Manage theme) - params/colors to create QGIS layers"
        )
        vbox.addWidget(theme_gb)
        vbox.addStretch()

        cell_gb = QGroupBox(
            "Cell files - select one for each RAT (2G,3G,4G,5G) to appear as QGIS layers"
        )
        vbox.addWidget(cell_gb)
        vbox.addStretch()

        optional_gb = QGroupBox(
            "Optional"
        )
        vbox.addWidget(optional_gb)
        vbox.addStretch()

        self.buttonBox = QtWidgets.QDialogButtonBox(DatabaseDialog)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttonBox.setObjectName("buttonBox")
        vbox.addWidget(self.buttonBox)

        ########### azm_gb setup
        tmp_box = QVBoxLayout()
        azm_gb.setLayout(tmp_box)

        self.dbPathLineEdit = QtWidgets.QLineEdit()
        self.dbPathLineEdit.setObjectName("dbPath")
        tmp_box.addWidget(self.dbPathLineEdit)

        self.browseButton = QtWidgets.QPushButton()
        self.browseButton.setObjectName("browseButton")
        tmp_box.addWidget(self.browseButton)
        ############################

        ############ theme_gb setup
        tmp_box = QVBoxLayout()
        theme_gb.setLayout(tmp_box)

        self.themePathLineEdit = QtWidgets.QLineEdit(DatabaseDialog)
        self.themePathLineEdit.setObjectName("themePath")
        tmp_box.addWidget(self.themePathLineEdit)

        self.browseButtonTheme = QtWidgets.QPushButton()
        self.browseButtonTheme.setObjectName("browseButtonTheme")
        tmp_box.addWidget(self.browseButtonTheme)
        ##################################

        ############ cell_gb setup
        tmp_box = QVBoxLayout()
        cell_gb.setLayout(tmp_box)

        self.cellPathLineEdit = QtWidgets.QLineEdit()
        self.cellPathLineEdit.setObjectName("cellPath")
        tmp_box.addWidget(self.cellPathLineEdit)

        self.browseButtonCell = QtWidgets.QPushButton()
        self.browseButtonCell.setObjectName("browseButtonCell")
        tmp_box.addWidget(self.browseButtonCell)
        ##################################

        ############ optional setup
        tmp_box = QVBoxLayout()
        optional_gb.setLayout(tmp_box)

        self.realWorldIndoorCheckBox = QtWidgets.QCheckBox()
        self.realWorldIndoorCheckBox.setText("Real world indoor")
        self.realWorldIndoorCheckBox.setChecked(True)
        self.realWorldIndoorCheckBox.setObjectName("realWorldIndoorCheckBox")
        tmp_box.addWidget(self.realWorldIndoorCheckBox)
        ##################################

        vbox.addStretch()
        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setEnabled(False)
        vbox.addWidget(self.statusLabel)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        vbox.addWidget(self.progress_bar)

        ################ config/connect signals
        self.retranslateUi(DatabaseDialog)

        QtCore.QMetaObject.connectSlotsByName(DatabaseDialog)
        self.browseButton.clicked.connect(self.choose_azm)
        self.browseButtonTheme.clicked.connect(self.choose_theme)
        self.browseButtonCell.clicked.connect(self.choose_cell)
        
        enable_real_world_indoor_slot = partial(self.real_world_indoor_enable, self.realWorldIndoorCheckBox)
        disable_real_world_indoor_slot = partial(self.real_world_indoor_disable, self.realWorldIndoorCheckBox)
        self.realWorldIndoorCheckBox.stateChanged.connect(
            lambda x: enable_real_world_indoor_slot() if x else disable_real_world_indoor_slot()
        )

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(
            self.check_and_start_import
        )
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(
            self.reject
        )
        #################################

    def onRadioClicked(self):
        radioButton = self.sender()
        if radioButton.isChecked():
            print("log access mode is %s" % (radioButton.mode))
            self.azm_gb.setEnabled(radioButton.mode == "local")

    def retranslateUi(self, DatabaseDialog):
        _translate = QtCore.QCoreApplication.translate
        DatabaseDialog.setWindowTitle(
            "Open logs"
        )
        self.browseButton.setText(_translate("DatabaseDialog", "Select Logs..."))
        self.browseButtonTheme.setText(_translate("DatabaseDialog", "Select Theme..."))
        self.browseButtonCell.setText(
            _translate("DatabaseDialog", "Select Cell-files...")
        )

        self.dbPathLineEdit.setText(azq_utils.read_settings_file("config_prev_azm"))
        self.cellPathLineEdit.setText(
            azq_utils.read_settings_file("config_prev_cell_file")
        )

        tp = azq_utils.read_settings_file("config_prev_theme")
        self.themePathLineEdit.setText(tp) if tp else self.themePathLineEdit.setText(
            "Default"
        )


    def choose_azm(self):
        fps, _ = QFileDialog.getOpenFileNames(
            self, "Select files", QtCore.QDir.rootPath(), "AZENQOS azm logs (*.azm);; SQLite db from azm (*.db)"
        )
        self.dbPathLineEdit.setText(",".join(fps)) if fps else None

    def choose_theme(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Select file", QtCore.QDir.rootPath(), "*.xml"
        )
        self.themePathLineEdit.setText(
            fileName
        ) if fileName else self.themePathLineEdit.setText("Default")

    def choose_cell(self):
        fileNames, _ = QFileDialog.getOpenFileNames(
            self, "Select cell files", QtCore.QDir.rootPath(), "*.*"
        )
        self.cellPathLineEdit.setText(
            ",".join(fileNames)
        ) if fileNames else self.cellPathLineEdit.setText("")

    def real_world_indoor_enable(self, checkbox):
        self.real_world_indoor = True

    def real_world_indoor_disable(self, checkbox):
        self.real_world_indoor = False

    def save_settings(self):
        import azq_utils
        azq_utils.write_settings_file("config_prev_azm", self.dbPathLineEdit.text())
        azq_utils.write_settings_file("config_prev_theme", self.themePathLineEdit.text())
        azq_utils.write_settings_file("config_prev_cell_file", self.cellPathLineEdit.text())


    def check_and_start_import(self):
        try:
            self.import_status_signal.emit("Opening log...")
            self.progress(0)
            self.progress_bar.setVisible(True)
            self.setEnabled(False)
            ret = self._check_and_start_import()
            if not ret:
                self.setEnabled(True)  # something failed so let user edit in the ui again
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: _check_and_start_import exception: {}".format(
                    exstr
                )
            )
            self.import_status_signal.emit("Opening log... failed")
            self.progress_bar.setVisible(False)
            qt_utils.msgbox("Open failed: " + exstr, title="Failed", parent=self)
            self.setEnabled(True)


    def _check_and_start_import(self):
        self.save_settings()

        cell_files = []
        cft = self.cellPathLineEdit.text()
        if cft:
            cell_files = cft.split(",")
        self.gc.cell_files = cell_files
        if self.gc.cell_files:
            try:
                import azq_cell_file
                azq_cell_file.check_cell_files(cell_files)
            except Exception as e:
                qt_utils.msgbox("Failed to load the sepcified cellfiles:\n\n{}".format(str(e)), title="Invalid cellfiles", parent=self)
                self.gc.cell_files = []
                return
        logs = []
        zip_fp = None
        if self.radioButtonAZM.isChecked():
            if not self.dbPathLineEdit.text():
                QtWidgets.QMessageBox.critical(
                    None,
                    "No log chosen",
                    "Please choose a log to open...",
                    QtWidgets.QMessageBox.Cancel,
                )
                return
            logs = self.dbPathLineEdit.text()
            if "," in logs:
                logs = logs.split(",")
            else:
                logs = [logs]
            for file in logs:
                if not os.path.isfile(file):
                    QtWidgets.QMessageBox.critical(
                        None,
                        "File not found",
                        "Failed to find the specified file: {}".format(file),
                        QtWidgets.QMessageBox.Cancel,
                    )
                    return
            assert logs
            self.gc.log_mode = "local"
            zip_fp = logs
        elif self.radioButtonPhone.isChecked():
            try:
                self.import_status_signal.emit("Trying to pull data from connected phone...")
                logs = azq_utils.pull_latest_log_db_from_phone(self, self.gc)
                if logs is None:
                    return
                # assert os.path.isfile(adb_db_fp)
                zip_fp = logs
                self.gc.log_mode = "adb"
                self.import_status_signal.emit("Trying to pull data from connected phone... done")
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print(
                    "WARNING: adb mode init exception: {}".format(
                        exstr
                    )
                )
                self.import_status_signal.emit("Trying to pull data from connected phone... failed")
                qt_utils.msgbox("Connected phone mode failed: " + exstr, title="Failed", parent=self)
                return

        elif self.radioButtonServer.isChecked():
            self.gc.login_ret_dict = None
            if self.radioButtonServer.isChecked():
                # server logs mode
                dlg = login_dialog.login_dialog(self, self.gc)
                dlg.show()
                dlg.raise_()
                ret = dlg.exec()
                if ret == 0:  # dismissed
                    return

                # ok we have a successful login and downloaded the db zip
                zip_fp = dlg.downloaded_zip_fp
                self.gc.log_mode = "server"
                if (not zip_fp) or (not os.path.isfile(zip_fp)):
                    raise Exception(
                        "Failed to get downloaded data from server login process..."
                    )
                self.gc.login_dialog = dlg  # so others can access server/token when needed for other api calls
        else:
             raise Exception("unknown/unhandled mode")

        if not self.themePathLineEdit.text():
            QtWidgets.QMessageBox.critical(
                None,
                "No theme chosen",
                "Please choose a theme xml to use...",
                QtWidgets.QMessageBox.Cancel,
            )
            return

        if self.themePathLineEdit.text() != "Default" and not os.path.isfile(
            self.themePathLineEdit.text()
        ):
            QtWidgets.QMessageBox.critical(
                None,
                "Theme file not found",
                "Please choose a theme xml to use...",
                QtWidgets.QMessageBox.Cancel,
            )
            return

        self.start_import_thread(zip_fp)
        return True



    def start_import_thread(self, zip_fp):
        try:
            self.setWindowTitle("Please wait... opening logs")
            self.setEnabled(False)
            if self.import_thread is None or (self.import_thread.is_alive() == False):
                self.zip_fp = zip_fp
                self.buttonBox.setEnabled(False)
                print("start import db zip thread...")
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


    def ui_handler_import_done(self, error):
        if error:
            self.setEnabled(True)
            print("ui_handler_import_done() error: %s" % error)
            QtWidgets.QMessageBox.critical(
                None, "Failed", error, QtWidgets.QMessageBox.Cancel,
            )
            self.buttonBox.setEnabled(True)
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


    def ui_handler_import_status(self, status):
        try:
            self.statusLabel.setText(status)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: ui_handler_import_status() failed exception:", exstr)

    def progress(self, val):
        self.progress_bar.setValue(val)

    def import_thread_run(self):
        self.import_status_signal.emit("Import logs - START")
        zip_fp = self.zip_fp
        success = False
        try:
            import preprocess_azm
            azq_utils.cleanup_died_processes_tmp_folders()
            azq_utils.tmp_gen_new_instance()  # so wont overwrite to old folders where db might be still in use

            if isinstance(zip_fp, list):
                if len(zip_fp) == 1:
                    zip_fp = zip_fp[0]
                    self.progress_update_signal.emit(20)
                else:
                    print("zip_fp is list - merging them into one db first...")
                    import azm_sqlite_merge
                    self.import_status_signal.emit("Multiple logs specified - trying to merge them...")
                    zip_fp = azm_sqlite_merge.merge(zip_fp, progress_update_signal = self.progress_update_signal)  # zip_fp will now be assigned with the merged db file path
                    self.import_status_signal.emit("Multiple logs specified - trying to merge them... done")
            self.progress_update_signal.emit(50)
            print("using log:", zip_fp)
            assert isinstance(zip_fp, str)
            assert os.path.isfile(zip_fp)
            if zip_fp.endswith(".azm") or zip_fp.endswith(".zip"):
                self.import_azm(zip_fp)
            elif zip_fp.endswith(".db"):
                databasePath = os.path.join(azq_utils.tmp_gen_path(), "azqdata.db")
                shutil.copy(zip_fp, databasePath)
                self.databasePath = databasePath
            else:
                raise Exception("unsupported file extension: {}".format(zip_fp))

            assert os.path.isfile(self.databasePath)
            
            self.progress_update_signal.emit(70)
            self.import_status_signal.emit("Preparing database... creating layers as per theme")
            ret = self.addDatabase()  # this will create views/tables per param as per specified theme so must check theme before here
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: import_selection() failed exception:", exstr)
            self.import_done_signal.emit(exstr)
        self.progress_update_signal.emit(100)
        self.import_status_signal.emit("Import logs - "+("SUCCESS" if success else "FAILED"))

    def import_azm(self, zip_fp):
        import preprocess_azm
        self.gc.azm_name = os.path.basename(zip_fp)
        self.databasePath = preprocess_azm.extract_entry_from_zip(
            zip_fp, "azqdata.db", azq_utils.tmp_gen_path()
        )
        with contextlib.closing(sqlite3.connect(self.databasePath)) as dbcon:
            log_hash = pd.read_sql("SELECT log_hash FROM logs LIMIT 1;", dbcon).log_hash[0]
            out_tmp_each_log_dir = os.path.join(azq_utils.tmp_gen_path(), str(log_hash))
            preprocess_azm.extract_all_from_zip(zip_fp, out_tmp_each_log_dir)

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

    def addDatabase(self):
        print("addDatabase START")
        ret = False
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
                self.gc.logPath = azq_utils.tmp_gen_path()
                # check theme
                check_theme(theme_fp = self.themePathLineEdit.text())
                db_preprocess.prepare_spatialite_views(dbcon, gc = self.gc, real_world_indoor=self.real_world_indoor)
                dbcon.close()  # in some rare cases 'with' doesnt flush dbcon correctly as close()

                assert self.databasePath
                self.gc.databasePath = self.databasePath
                self.gc.db_fp = self.gc.databasePath
                print("addDatabase DONE SUCCESS")
            finally:
                try:
                    dbcon.close()
                except:
                    pass
                print("addDatabase DONE")
            ret = True
        if not ret:
            self.import_status_signal.emit("Preparing database... FAILED")
            raise Exception(
                "Failed to open azqdata.db file inside the unzipped supplied azm file"
            )
        else:
            self.progress_update_signal.emit(90)
            self.import_status_signal.emit("Preparing database... done")
            self.import_done_signal.emit("")
            success = True


    def setIncrementValue(self):
        self.gc.sliderLength = 2147483647
        self.gc.sliderLength = round(self.gc.sliderLength, 3)

    def removeMainMenu(self):
        if hasattr(self, "azenqosMainMenu") is True:
            del self.azenqosMainMenu

    def reject(self):
        super().reject()
