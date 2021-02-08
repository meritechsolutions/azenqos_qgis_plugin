from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *  # QAbstractTableModel, QVariant, Qt, pyqtSignal, QThread
from PyQt5.QtSql import *  # QSqlQuery, QSqlDatabase
from PyQt5.QtGui import *
from PyQt5.uic import loadUi
try:
    from qgis.core import *
    from qgis.utils import *
    from qgis.gui import *
except:
    pass
import datetime
import threading
import sys
import traceback
import os
import csv
# Adding folder path
sys.path.insert(1, os.path.dirname(os.path.realpath(__file__)))
import pyqtgraph as pg
import numpy as np
import analyzer_vars
try:
    import tasks
except:
    pass
import azq_utils
import shutil
from cdma_evdo_query import CdmaEvdoQuery
from globalutils import Utils
from linechart import *
from worker import Worker
from timeslider import *
from datatable import *
from atomic_int import atomic_int
import import_db_dialog
GUI_SETTING_NAME_PREFIX = "{}/".format(os.path.basename(__file__))
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)  # exit upon ctrl-c


class main_window(QMainWindow):

    signal_ui_thread_emit_time_slider_updated = pyqtSignal(float)

    def __init__(self, qgis_iface):
        super(main_window, self).__init__(None)

        ######## instance vars
        self.closed = False        
        self.gc = analyzer_vars.analyzer_vars()
        self.timechange_service_thread = None
        self.timechange_to_service_counter = atomic_int(0)
        self.closed = False        
        self.signal_ui_thread_emit_time_slider_updated.connect(
            self.ui_thread_emit_time_slider_updated
        )
        self.gc = analyzer_vars.analyzer_vars()
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

    ############# signalling menu slots
    @pyqtSlot()
    def on_actionLayer_3_Messages_triggered(self):
        print("action l3")
        import signalling_query
        headers = ["Time", "", "Eq.", "Protocol", "Name", "Detail"]
        swa = SubWindowArea(self.mdi, self.gc)        
        widget = TableWindow(swa, "Layer-3 Messages", signalling_query.get_signalling, tableHeader=headers, tablename="signalling")
        self.add_subwindow_with_widget(swa, widget)
        
    @pyqtSlot()
    def on_actionEvents_triggered(self):
        print("action events")
        import signalling_query
        headers = ["Time", "", "Eq.", "Name", "Info."]
        swa = SubWindowArea(self.mdi, self.gc)        
        widget = TableWindow(swa, "Events", signalling_query.get_events, tableHeader=headers, tablename="events")
        self.add_subwindow_with_widget(swa, widget)

    ############# NR menu slots
    
    ############# LTE menu slots
    @pyqtSlot()
    def on_actionLTE_Radio_Parameters_triggered(self):
        print("action lte radio params0")
        import lte_query
        swa = SubWindowArea(self.mdi, self.gc)
        widget = TableWindow(swa, "LTE_Radio Parameters", lte_query.get_lte_radio_params_disp_df)
        self.add_subwindow_with_widget(swa, widget)

    ############# WCDMA menu slots
    ############# GSM menu slots
        
    def add_subwindow_with_widget(self, swa, widget):                
        swa.setWidget(widget)
        self.mdi.addSubWindow(swa)
        swa.show()
        self.gc.openedWindows.append(widget)    

    def setupUi(self):
        self.ui = loadUi("main_window.ui", self)
        self.toolbar = self.ui.toolBar        
        try:
            self.mdi = self.ui.mdi
            self.gc.mdi = self.mdi
            dirname = os.path.dirname(__file__)
            self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
            
            # Time Slider
            self.gc.timeSlider = timeSlider(self, self.gc)
            self.gc.timeSlider.setMinimumWidth(100)
            self.gc.timeSlider.setMaximumWidth(360)
            sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.gc.timeSlider.sizePolicy().hasHeightForWidth())
            self.gc.timeSlider.setSizePolicy(sizePolicy)
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

            # Load Button
            self.loadBtn = QToolButton()
            self.loadBtn.setIcon(QIcon(QPixmap(os.path.join(dirname, "res", "folder.png"))))
            self.loadBtn.setObjectName("loadBtn")

            # Save Button
            self.saveBtn = QToolButton()
            self.saveBtn.setIcon(QIcon(QPixmap(os.path.join(dirname, "res", "save.png"))))
            self.saveBtn.setObjectName("saveBtn")

            # Map tool Button
            resourcePath = os.path.join(dirname, "res", "crosshair.png")
            self.maptool = QToolButton()
            self.maptool.setIcon(QIcon(QPixmap(resourcePath)))
            self.importDatabaseBtn.setObjectName("importDatabaseBtn")

            # Layer Select Button
            self.layerSelect = QToolButton()
            self.layerSelect.setIcon(
                QIcon(QPixmap(os.path.join(dirname, "res", "layer.png")))
            )
            self.layerSelect.setObjectName("layerBtn")

            #caused duplicated calls to pyqtslots funcs above so not using: QtCore.QMetaObject.connectSlotsByName(self)

            self.gc.timeSlider.valueChanged.connect(self.timeChange)
            self.loadBtn.clicked.connect(self.loadWorkspaceFile)
            self.saveBtn.clicked.connect(self.saveWorkspaceFile)
            self.layerSelect.clicked.connect(self.selectLayer)
            self.importDatabaseBtn.clicked.connect(self.open_logs)
            self.maptool.clicked.connect(self.setMapTool)
            self.setupToolBar()

            self._gui_restore()
            
            self.setWindowTitle("AZENQOS Log Replay & Analyzer tool")
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


    def updateUi(self):        
        if not self.gc.slowDownValue == 1:
            self.playSpeed.setText("{:.2f}".format(self.gc.slowDownValue))
        elif not self.gc.fastForwardValue == 1:
            self.playSpeed.setText("{:.2f}".format(self.gc.fastForwardValue))
        else:
            self.playSpeed.setText("{:.2f}".format(1))
        print("updateui self.gc.currentTimestamp", self.gc.currentTimestamp)
        if self.gc.currentTimestamp:
            self.timeEdit.setDateTime(datetime.datetime.fromtimestamp(self.gc.currentTimestamp))

        
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
        self.pauseButton = QToolButton()
        self.pauseButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
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
        print("self.timeSliderThread.getCurrentValue()", self.timeSliderThread.getCurrentValue())
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
            vlayer = self.qgis_iface.addVectorLayer(self.dbfp, None, "ogr")
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
        self.gc.timeSlider.setValue(value)
        print("mw self.gc.timeSlider.value()", self.gc.timeSlider.value())
        self.gc.timeSlider.update()
        if value >= self.gc.sliderLength:
            self.pauseTime()

    def ui_thread_emit_time_slider_updated(self, timestamp):
        print("ui_thread_emit_time_slider_updated")
        sampledate = datetime.datetime.fromtimestamp(timestamp)
        self.timeEdit.setDateTime(sampledate)

            
    def clickCanvas(self, point, button):
        layerData = []
        selectedTime = None
        clearAllSelectedFeatures()

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
            selectedTimestamp = Utils(self.gc).datetimeStringtoTimestamp(
                selectedTime.toString("yyyy-MM-dd HH:mm:ss.zzz")
            )
        except:
            selectedTimestamp = Utils(self.gc).datetimeStringtoTimestamp(selectedTime)
        if selectedTimestamp:
            timeSliderValue = self.gc.sliderLength - (self.gc.maxTimeValue - selectedTimestamp)
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
        dlg = import_db_dialog.import_db_dialog(self.gc)
        dlg.show()
        ret = dlg.exec()
        print("import_db_dialog ret: {}".format(ret))
        self.gc.timeSlider.setRange(0, self.gc.sliderLength)
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
                #print(print("timeChangedWorkerFunc : {}", ret))
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
        # print("%s: timeChange1" % os.path.basename(__file__))
        timestampValue = self.gc.minTimeValue + value
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
                worker = None
                if not window.title in self.gc.linechartWindowname:
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
            start_time = time.time()
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
                    seconds=(self.params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS / 1000.0)
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

    def saveWorkspaceFile(self):
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
            self._gui_save()
            # saving = Utils().saveState(self.gc.CURRENT_PATH)
            if self.qgis_iface:
                self.qgis_iface.actionPan().trigger()
            self.pauseTime()
            self.timeSliderThread.exit()
            #self.removeToolBarActions()
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
            print("Close App")
            tasks.close_db(self.gc)
            try:
                shutil.rmtree(self.gc.logPath)
            except:
                pass
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
        if (self.qgis_iface):
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
                    print("_gui_restore() window i {} title {}".format(i, title))
                    if title and "_" in title:
                        parts = title.split("_", 1)
                        if len(parts) == 2:
                            print("")
                            print(
                                "_gui_restore() window i {} title {} openwindow".format(
                                    i, title
                                )
                            )
                            self.classifySelectedItems(parts[0], parts[1])
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
