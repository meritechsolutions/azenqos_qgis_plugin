from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *
try:
    from qgis.core import *
    from qgis.utils import *
    from qgis.gui import *
except:
    pass
import datetime
import sys
import traceback
import os
import sqlite3
import threading
import time

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

from globalutils import Utils
try:
    from tasks import *
except:
    pass
from datatable import *
from version import VERSION
import db_preprocess
import azq_utils
import azq_theme_manager
import login_dialog
try:
    from cell_layer_task import *
except:
    pass


class import_db_dialog(QDialog):

    import_done_signal = pyqtSignal(str)
    
    def __init__(self, gc):
        super(import_db_dialog, self).__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.import_thread = None
        self.import_done_signal.connect(
            self.ui_handler_import_done
        )
        self.setupUi(self)


    def setupUi(self, DatabaseDialog):
        dirname = os.path.dirname(__file__)
        DatabaseDialog.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        DatabaseDialog.setObjectName("DatabaseDialog")
        DatabaseDialog.resize(640, 300)

        vbox = QVBoxLayout()
        DatabaseDialog.setLayout(vbox)
        vbox.addStretch()

        mode_gb = QGroupBox(
            "Logs access mode"
        )
        vbox.addWidget(mode_gb)
        vbox.addStretch()
        
        ########
        layout = QGridLayout()
        radiobutton = QRadioButton("AZENQOS Server login")
        self.radioButtonServer = radiobutton
        radiobutton.setChecked(True)
        radiobutton.mode = "server"
        radiobutton.toggled.connect(self.onRadioClicked)
        layout.addWidget(radiobutton, 0, 0)

        radiobutton = QRadioButton("Local .azm log file")
        radiobutton.mode = "local"
        radiobutton.toggled.connect(self.onRadioClicked)
        layout.addWidget(radiobutton, 0, 1)
        mode_gb.setLayout(layout)
        #####################

        #######################
        azm_gb = QGroupBox(
            "Log file (.azm from Server > Download > Processed AZM file)"
        )
        vbox.addWidget(azm_gb)
        vbox.addStretch()
        azm_gb.setEnabled(False)
        self.azm_gb = azm_gb

        theme_gb = QGroupBox(
            "Theme file (.xml from Server > Manage theme) - params/colors to create QGIS layers"
        )
        vbox.addWidget(theme_gb)
        vbox.addStretch()

        cell_gb = QGroupBox("Cell files - select one for each RAT (2G,3G,4G,5G) to appear as QGIS layers")
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

        ############ theme_gb setup
        tmp_box = QVBoxLayout()
        cell_gb.setLayout(tmp_box)

        self.cellPathLineEdit = QtWidgets.QLineEdit()
        self.cellPathLineEdit.setObjectName("cellPath")
        tmp_box.addWidget(self.cellPathLineEdit)

        self.browseButtonCell = QtWidgets.QPushButton()
        self.browseButtonCell.setObjectName("browseButtonCell")
        tmp_box.addWidget(self.browseButtonCell)
        ##################################

        ################ config/connect
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
            _translate("DatabaseDialog", "Choose log file to replay...")
        )
        self.browseButton.setText(_translate("DatabaseDialog", "Choose Log..."))
        self.browseButtonTheme.setText(_translate("DatabaseDialog", "Choose Theme..."))
        self.browseButtonCell.setText(
            _translate("DatabaseDialog", "Choose Cell file...")
        )

        self.dbPathLineEdit.setText(azq_utils.read_local_file("config_prev_azm"))
        self.cellPathLineEdit.setText(
            azq_utils.read_local_file("config_prev_cell_file")
        )

        tp = azq_utils.read_local_file("config_prev_theme")
        self.themePathLineEdit.setText(tp) if tp else self.themePathLineEdit.setText(
            "Default"
        )

    def clearCurrentProject(self):
        for hi in self.gc.h_list:
            hi.hide()
        self.gc.h_list = []
        clearAllSelectedFeatures()

        project = QgsProject.instance()
        for (id_l, layer) in project.mapLayers().items():
            to_be_deleted = project.mapLayersByName(layer.name())[0]
            project.removeMapLayer(to_be_deleted.id())
            layer = None

        QgsProject.instance().reloadAllLayers()
        QgsProject.instance().clear()
        self.gc.tableList = []

    def choose_azm(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Single File", QtCore.QDir.rootPath(), "*.azm"
        )
        self.dbPathLineEdit.setText(fileName) if fileName else None

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

        
    def check_and_start_import(self):
        if self.radioButtonServer.isChecked() == False:
            if not self.dbPathLineEdit.text():
                QtWidgets.QMessageBox.critical(
                    None,
                    "No log chosen",
                    "Please choose a log to open...",
                    QtWidgets.QMessageBox.Cancel,
                )
                return False

            if not os.path.isfile(self.dbPathLineEdit.text()):
                QtWidgets.QMessageBox.critical(
                    None,
                    "File not found",
                    "Failed to find specified azm file...",
                    QtWidgets.QMessageBox.Cancel,
                )
                return False

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

        try:
            self.gc.close_db()
            """
            if hasattr(self, "azenqosMainMenu") is True:
                self.azenqosMainMenu.newImport = True
                self.azenqosMainMenu.killMainWindow()
                self.clearCurrentProject()
            """

            print("self.radioButtonServer.isChecked() %s", self.radioButtonServer.isChecked())
            zip_fp = self.dbPathLineEdit.text()
            self.gc.login_ret_dict = None
            if self.radioButtonServer.isChecked():
                dlg = login_dialog.login_dialog(self, self.gc)
                dlg.show()
                dlg.raise_()
                ret = dlg.exec()
                if ret == 0:  # dismissed
                    return
                # ok we have a successful login and downloaded the db zip
                zip_fp = dlg.downloaded_zip_fp                
                if (not zip_fp) or (not os.path.isfile(zip_fp)):
                    raise Exception("Failed to get downloaded data from server login process...")
                self.gc.login_dialog = dlg  # so others can access server/token when needed for other api calls                
            
            if self.import_thread is None or (self.import_thread.is_alive() == False):
                self.zip_fp = zip_fp
                self.buttonBox.setEnabled(False)
                print("start import db zip thread...")
                self.import_thread = threading.Thread(target=self.import_selection, args=())
                self.import_thread.start()
            else:
                print("already importing - please wait...")
                QtWidgets.QMessageBox.critical(
                    None,
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
                None,
                "Open log failed",
                "Error: {}\n\nTrace:\n{}".format(ex, exstr),
                QtWidgets.QMessageBox.Cancel,
            )
            return False

        raise Exception("invalid state")


    def ui_handler_import_done(self, error):
        if error:
            print("ui_handler_import_done() error: %s" % error)        
            QtWidgets.QMessageBox.critical(
                None,
                "Failed",
                error,
                QtWidgets.QMessageBox.Cancel,
            )
            self.buttonBox.setEnabled(True)
            return False        
        else:
            print("ui_handler_import_done() success")
            import azq_utils

            azq_utils.write_local_file(
                "config_prev_azm", self.dbPathLineEdit.text()
            )
            self.getTimeForSlider()
            print("getTimeForSlider() done")

            if self.gc.qgis_iface:
                print("starting layertask")
                self.layerTask = LayerTask(u"Add layers", self.databasePath, self.gc)
                QgsApplication.taskManager().addTask(self.layerTask)
                self.longTask = CellLayerTask(
                    "Load cell file", self.cellPathLineEdit.text().split(","),
                    self.gc
                )
                QgsApplication.taskManager().addTask(self.longTask)
            else:
                print("NOT starting layertask because no self.gc.qgis_iface")

            self.close()

    
    def import_selection(self):
        zip_fp = self.zip_fp
        try:
            import preprocess_azm
            
            assert os.path.isfile(zip_fp)
            azq_utils.cleanup_died_processes_tmp_folders()
            assert os.path.isfile(zip_fp)
            self.databasePath = preprocess_azm.extract_entry_from_zip(zip_fp, "azqdata.db", azq_utils.tmp_gen_path())
            assert os.path.isfile(self.databasePath)
            dbcon = self.addDatabase() # this will create views/tables per param as per specified theme so must check theme before here        
            if not dbcon:
                raise Exception("Failed to open azqdata.db file inside the unzipped supplied azm file")
            else:
                self.import_done_signal.emit("")                
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: import_selection() failed exception:", exstr)
            self.import_done_signal.emit(exstr)

    
    def getTimeForSlider(self):
        startTime = None
        endTime = None
        with sqlite3.connect(self.databasePath) as dbcon:
            df = pd.read_sql("select min(log_start_time) as startTime, max(log_end_time) as endTime from logs", dbcon)
            assert len(df) == 1
            startTime = df.iloc[0].startTime
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
        dbcon = sqlite3.connect(self.databasePath)
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
        azq_utils.write_local_file("config_prev_theme", theme_fp)

        db_preprocess.prepare_spatialite_views(dbcon)
        dbcon.close()  # in some rare cases 'with' doesnt flush dbcon correctly as close()
        assert self.databasePath
        dbcon = sqlite3.connect(self.databasePath)        
        self.gc.databasePath = self.databasePath
        self.gc.db_fp = self.gc.databasePath
        self.gc.azenqosDatabase = QSqlDatabase.addDatabase("QSQLITE")
        assert self.gc.azenqosDatabase

        self.gc.azenqosDatabase.setDatabaseName(self.databasePath)
        self.gc.dbcon = dbcon
        return dbcon

    def setIncrementValue(self):
        self.gc.sliderLength = self.gc.maxTimeValue - self.gc.minTimeValue
        self.gc.sliderLength = round(self.gc.sliderLength, 3)

    def removeMainMenu(self):
        if hasattr(self, "azenqosMainMenu") is True:
            del self.azenqosMainMenu

    def reject(self):
        super().reject()
