from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *
from qgis.core import *
from qgis.utils import *
from qgis.gui import *
import datetime
import sys
import os

# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))

import global_config as gc
from .globalutils import Utils
from .tasks import *
from .timeslider import *
from .datatable import *
from .azenqos_plugin_dialog import *  # AzenqosDialog, clearAllSelectedFeatures


class Ui_DatabaseDialog(QDialog):
    def __init__(self):
        super(Ui_DatabaseDialog, self).__init__()
        self.setupUi(self)

    def setupUi(self, DatabaseDialog):
        dirname = os.path.dirname(__file__)
        DatabaseDialog.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        DatabaseDialog.setObjectName("DatabaseDialog")
        DatabaseDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        DatabaseDialog.resize(540, 90)
        DatabaseDialog.setMaximumSize(QtCore.QSize(540, 90))
        self.browseButton = QtWidgets.QPushButton(DatabaseDialog)
        self.browseButton.setGeometry(QtCore.QRect(454, 30, 80, 24))
        self.browseButton.setObjectName("browseButton")
        self.dbPath = QtWidgets.QLineEdit(DatabaseDialog)
        self.dbPath.setGeometry(QtCore.QRect(10, 30, 438, 24))
        self.dbPath.setObjectName("dbPath")
        self.buttonBox = QtWidgets.QDialogButtonBox(DatabaseDialog)
        self.buttonBox.setGeometry(QtCore.QRect(370, 60, 164, 24))
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        self.buttonBox.setObjectName("buttonBox")
        self.dbPathLabel = QtWidgets.QLabel(DatabaseDialog)
        self.dbPathLabel.setGeometry(QtCore.QRect(10, 10, 181, 16))
        self.dbPathLabel.setObjectName("dbPathLabel")

        self.retranslateUi(DatabaseDialog)
        QtCore.QMetaObject.connectSlotsByName(DatabaseDialog)

        self.browseButton.clicked.connect(self.getfiles)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(
            self.checkDatabase
        )
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(
            self.reject
        )

    def retranslateUi(self, DatabaseDialog):
        _translate = QtCore.QCoreApplication.translate
        DatabaseDialog.setWindowTitle(_translate("DatabaseDialog", "Azenqos"))
        self.browseButton.setText(_translate("DatabaseDialog", "Browse.."))
        self.dbPathLabel.setText(
            _translate("DatabaseDialog", "Database path: ( .azm )")
        )

    def clearCurrentProject(self):

        for hi in gc.h_list:
            hi.hide()
        gc.h_list = []
        clearAllSelectedFeatures()

        project = QgsProject.instance()
        for (id_l, layer) in project.mapLayers().items():
            to_be_deleted = project.mapLayersByName(layer.name())[0]
            project.removeMapLayer(to_be_deleted.id())
            layer = None

        QgsProject.instance().reloadAllLayers()
        QgsProject.instance().clear()
        gc.allLayers = []

    def getfiles(self):
        fileName, _ = QFileDialog.getOpenFileName(
            self, "Single File", QtCore.QDir.rootPath(), "*.azm"
        )
        if fileName != "":
            self.fileName = fileName
            self.dbPath.setText(fileName)
        else:
            if self.dbPath.text() != "":
                self.databasePath = self.dbPath.text()

    def checkDatabase(self):
        if self.dbPath.text() != "":
            if hasattr(self, "azenqosMainMenu") is True:
                self.azenqosMainMenu.newImport = True
                self.azenqosMainMenu.killMainWindow()
                self.clearCurrentProject()
            self.databasePath = Utils().unzipToFile(gc.CURRENT_PATH, self.fileName)
            self.addDatabase()
            if not gc.azenqosDatabase.open():
                QtWidgets.QMessageBox.critical(
                    None,
                    "Cannot open database",
                    "Unable to establish a database connection.\n"
                    "This example needs SQLite support. Please read "
                    "the Qt SQL driver documentation for information how "
                    "to build it.\n\n"
                    "Click Cancel to exit.",
                    QtWidgets.QMessageBox.Cancel,
                )
                return False
            else:
                self.getLayersFromDb()
                # if hasattr(self, "layerTask") is False:
                self.layerTask = LayerTask(u"Add layers", self.databasePath)
                QgsApplication.taskManager().addTask(self.layerTask)
                self.getTimeForSlider()
                self.hide()
                self.azenqosMainMenu = AzenqosDialog(self)
                self.azenqosMainMenu.show()
                self.azenqosMainMenu.raise_()
                self.azenqosMainMenu.activateWindow()
                self.loading = Utils().loadState(gc.CURRENT_PATH, self.azenqosMainMenu)
        else:
            QtWidgets.QMessageBox.critical(
                None,
                "Cannot open database",
                "Unable to establish a database connection.\n" "Click Cancel to exit.",
                QtWidgets.QMessageBox.Cancel,
            )
            return False

    def getTimeForSlider(self):
        dataList = []
        gc.azenqosDatabase.open()
        subQuery = QSqlQuery()
        queryString = "SELECT log_start_time, log_end_time FROM logs"
        subQuery.exec_(queryString)
        while subQuery.next():
            if subQuery.value(0).strip() and subQuery.value(1).strip():
                startTime = subQuery.value(0)
                endTime = subQuery.value(1)
        gc.azenqosDatabase.close()

        try:
            gc.minTimeValue = datetime.datetime.strptime(
                str(startTime), "%Y-%m-%d %H:%M:%S.%f"
            ).timestamp()
            gc.maxTimeValue = datetime.datetime.strptime(
                str(endTime), "%Y-%m-%d %H:%M:%S.%f"
            ).timestamp()
            gc.currentDateTimeString = "%s" % (
                datetime.datetime.fromtimestamp(gc.minTimeValue)
            )
        except:
            QtWidgets.QMessageBox.critical(
                None,
                "Cannot open database",
                "Unable to establish a database connection.\n"
                "This example needs SQLite support. Please read "
                "the Qt SQL driver documentation for information how "
                "to build it.\n\n"
                "Click Cancel to exit.",
                QtWidgets.QMessageBox.Cancel,
            )
            return False
        self.setIncrementValue()

    def addDatabase(self):
        gc.azenqosDatabase = QSqlDatabase.addDatabase("QSQLITE")
        gc.azenqosDatabase.setDatabaseName(self.databasePath)

    def getLayersFromDb(self):
        gc.azenqosDatabase.open()
        query = QSqlQuery()
        queryString = "select tbl_name from sqlite_master where sql LIKE '%\"geom\"%' and type = 'table' order by tbl_name"
        query.exec_(queryString)
        while query.next():
            tableName = query.value(0)
            subQueryString = "select count(*) from %s" % (tableName)
            subQuery = QSqlQuery()
            subQuery.exec_(subQueryString)
            while subQuery.next():
                if int(subQuery.value(0)) > 0:
                    gc.allLayers.append(tableName)
        gc.azenqosDatabase.close()

    def setIncrementValue(self):
        gc.sliderLength = gc.maxTimeValue - gc.minTimeValue
        gc.sliderLength = round(gc.sliderLength, 3)

    def removeMainMenu(self):
        if hasattr(self, "azenqosMainMenu") is True:
            del self.azenqosMainMenu

    def reject(self):
        super().reject()
