import contextlib
import datetime
import os
import shutil
import sqlite3
import sys
# Adding folder path
import threading
import traceback
import uuid

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
)

import azq_utils
import qt_utils

sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import db_preprocess
import azq_theme_manager
import login_dialog



class import_db_dialog(QDialog):
    import_done_signal = pyqtSignal(str)
    import_status_signal = pyqtSignal(str)

    def __init__(self, parent_window, gc, connected_mode_refresh=False):
        super(import_db_dialog, self).__init__(parent=parent_window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.parent_window = parent_window
        self.import_thread = None
        self.import_done_signal.connect(self.ui_handler_import_done)
        self.import_status_signal.connect(self.ui_handler_import_status)
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

        vbox.addStretch()
        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setEnabled(False)
        vbox.addWidget(self.statusLabel)

        ################ config/connect signals
        self.retranslateUi(DatabaseDialog)

        QtCore.QMetaObject.connectSlotsByName(DatabaseDialog)
        self.browseButton.clicked.connect(self.choose_azm)
        self.browseButtonTheme.clicked.connect(self.choose_theme)
        self.browseButtonCell.clicked.connect(self.choose_cell)

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
            self, "Single File", QtCore.QDir.rootPath(), "AZENQOS azm logs (*.azm);; SQLite db from azm (*.db)"
        )
        self.dbPathLineEdit.setText(",".join(fps)) if fps else None

    def choose_theme(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Single File", QtCore.QDir.rootPath(), "*.xml"
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

    def save_settings(self):
        import azq_utils
        azq_utils.write_settings_file("config_prev_azm", self.dbPathLineEdit.text())
        azq_utils.write_settings_file("config_prev_theme", self.themePathLineEdit.text())
        azq_utils.write_settings_file("config_prev_cell_file", self.cellPathLineEdit.text())


    def check_and_start_import(self):
        try:
            self.import_status_signal.emit("Opening log...")
            self.setEnabled(False)
            self._check_and_start_import()
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print(
                "WARNING: _check_and_start_import exception: {}".format(
                    exstr
                )
            )
            self.import_status_signal.emit("Opening log... failed")
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
                return False
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
                    return False
            assert logs
            self.gc.log_mode = "local"
            zip_fp = logs
        elif self.radioButtonPhone.isChecked():
            try:
                self.import_status_signal.emit("Trying to pull data from connected phone...")
                adb_db_fp = azq_utils.pull_latest_log_db_from_phone(self)
                if adb_db_fp is None:
                    return
                assert os.path.isfile(adb_db_fp)
                zip_fp = adb_db_fp
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
            return False

        if self.themePathLineEdit.text() != "Default" and not os.path.isfile(
            self.themePathLineEdit.text()
        ):
            QtWidgets.QMessageBox.critical(
                None,
                "Theme file not found",
                "Please choose a theme xml to use...",
                QtWidgets.QMessageBox.Cancel,
            )
            return False

        self.start_import_thread(zip_fp)



    def start_import_thread(self, zip_fp):
        try:
            self.setWindowTitle("Please wait... opening logs")
            self.setEnabled(False)
            if self.import_thread is None or (self.import_thread.is_alive() == False):
                self.zip_fp = zip_fp
                self.buttonBox.setEnabled(False)
                print("start import db zip thread...")
                self.import_thread = threading.Thread(
                    target=self.import_thread_run, args=()
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
            self.getTimeForSlider()
            print("getTimeForSlider() done")
            self.close()


    def ui_handler_import_status(self, status):
        try:
            self.statusLabel.setText(status)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: ui_handler_import_status() failed exception:", exstr)


    def import_thread_run(self):
        self.import_status_signal.emit("Import logs - START")
        zip_fp = self.zip_fp
        success = False
        try:
            import preprocess_azm
            azq_utils.cleanup_died_processes_tmp_folders()

            if isinstance(zip_fp, list):
                if len(zip_fp) == 1:
                    zip_fp = zip_fp[0]
                else:
                    print("zip_fp is list - merging them into one db first...")
                    import azm_sqlite_merge
                    self.import_status_signal.emit("Multiple logs specified - trying to merge them...")
                    zip_fp = azm_sqlite_merge.merge(zip_fp)  # zip_fp will now be assigned with the merged db file path
                    self.import_status_signal.emit("Multiple logs specified - trying to merge them... done")

            print("using log:", zip_fp)
            assert isinstance(zip_fp, str)
            assert os.path.isfile(zip_fp)
            azq_utils.tmp_gen_new_instance()  # so wont overwrite to old folders where db might be still in use
            if zip_fp.endswith(".azm") or zip_fp.endswith(".zip"):
                self.databasePath = preprocess_azm.extract_entry_from_zip(
                    zip_fp, "azqdata.db", azq_utils.tmp_gen_path()
                )
                preprocess_azm.extract_all_from_zip(zip_fp, azq_utils.tmp_gen_path())
            elif zip_fp.endswith(".db"):
                databasePath = os.path.join(azq_utils.tmp_gen_path(), "azqdata.db")
                shutil.copy(zip_fp, databasePath)
                self.databasePath = databasePath
            else:
                raise Exception("unsupported file extension: {}".format(zip_fp))

            assert os.path.isfile(self.databasePath)
            self.import_status_signal.emit("Preparing database... creating layers as per theme")
            ret = self.addDatabase()  # this will create views/tables per param as per specified theme so must check theme before here
            if not ret:
                self.import_status_signal.emit("Preparing database... FAILED")
                raise Exception(
                    "Failed to open azqdata.db file inside the unzipped supplied azm file"
                )
            else:
                self.import_status_signal.emit("Preparing database... done")
                self.import_done_signal.emit("")
                success = True
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: import_selection() failed exception:", exstr)
            self.import_done_signal.emit(exstr)
        self.import_status_signal.emit("Import logs - "+("SUCCESS" if success else "FAILED"))


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
        # check db
        assert os.path.isfile(self.databasePath)
        with contextlib.closing(sqlite3.connect(self.databasePath)) as dbcon:
            try:
                logs_df = pd.read_sql("select * from logs limit 1", dbcon)
                if not len(logs_df):
                    raise Exception("invalid log database - cant read log metadata")
                log_hash = logs_df.iloc[0].log_hash
                if not log_hash:
                    raise Exception("invalid log database - cant read log_hash")

                # check theme
                theme_fp = self.themePathLineEdit.text()
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
                db_preprocess.prepare_spatialite_views(dbcon)
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


    def setIncrementValue(self):
        self.gc.sliderLength = self.gc.maxTimeValue - self.gc.minTimeValue
        self.gc.sliderLength = round(self.gc.sliderLength, 3)

    def removeMainMenu(self):
        if hasattr(self, "azenqosMainMenu") is True:
            del self.azenqosMainMenu

    def reject(self):
        super().reject()
