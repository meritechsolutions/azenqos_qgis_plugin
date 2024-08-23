import contextlib
import datetime
import sqlite3
import sys
from functools import partial

import numpy as np
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, Qt
# from qgis.gui import QgsColorButton
from PyQt5.QtWidgets import QMenu
from PyQt5.uic import loadUi

import add_param_dialog
import azq_utils
import color_dialog
import dataframe_model
from azq_utils import get_default_color_for_index
from worker import Worker


def epochToDateString(epoch):
    try:
        return datetime.datetime.fromtimestamp(epoch).strftime("%H:%M:%S")
    except:
        return ""


class TimeAxisItem(pg.AxisItem):
    """Internal timestamp for x-axis"""

    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """Function overloading the weak default version to provide timestamp"""
        return [epochToDateString(value) for value in values]


class LineChart(QtWidgets.QDialog):
    timeSelected = pyqtSignal(float)
    updateChart = pyqtSignal(object)
    updateTable = pyqtSignal(object)

    def unixTimeMillis(self, dt):
        return azq_utils.datetimeStringtoTimestamp(dt.strftime("%Y-%m-%d %H:%M:%S.%f"))

    def __init__(self, gc, paramList=[], eventList=[], title="Line Chart", func_key=None):
        super(LineChart, self).__init__(None)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.gc = gc
        self.title = title
        self.func_key = func_key
        # pg.setConfigOptions(background="w", antialias=True)
        pg.setConfigOptions(background="w", useOpenGL=True)
        pg.TickSliderItem(orientation="bottom", allowAdd=True)
        self.paramList = paramList
        self.eventList = eventList
        self.paramListDict = {}
        self.colorDict = {}
        self.colorindex = 0

        for paramDict in self.paramList:
            param_alias_name = paramDict["name"]
            if "selected_ue" in paramDict:
                if paramDict["selected_ue"] is not None:
                    ue_suffix = "(" + self.gc.device_configs[paramDict["selected_ue"]]["name"] + ")"
                    if ue_suffix not in param_alias_name:
                        param_alias_name = param_alias_name + ue_suffix
            self.paramListDict[param_alias_name] = paramDict

        for paramDict in self.paramListDict:
            color = get_default_color_for_index(self.colorindex)
            self.colorDict[paramDict] = color
            self.colorindex += 1


        self.lastChartParamList = None
        self.minX = None
        self.maxX = None
        self.minY = None
        self.maxY = None
        self.zoom_enabled = False
        self.mousecoordinatesdisplay = None
        self.moveFromChart = False
        self.ui = loadUi(azq_utils.get_module_fp("linechart3.ui"), self)
        self.lineDict = {}
        self.graphWidget = None
        self.graphWidget = pg.GraphicsLayoutWidget()
        self.graphWidget.axes = self.graphWidget.addPlot(
            axisItems={"bottom": TimeAxisItem(orientation="bottom")}
        )
        self.vLine = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen("k", width=4)
        )
        self.cursorVLine = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen("k", width=1)
        )
        self.cursorHLine = pg.InfiniteLine(
            angle=0, movable=False, pen=pg.mkPen("k", width=1)
        )
        self.graphWidget.axes.hideButtons()
        self.graphWidget.axes.showGrid(x=False, y=True)
        self.graphWidget.axes.setMouseEnabled(x=True, y=False)
        self.graphWidget.scene().sigMouseClicked.connect(self.onClick)
        # self.graphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
        self.ui.verticalLayout_3.addWidget(self.graphWidget)
        self.graphWidget.axes.sigXRangeChanged.connect(self.chartXRangeChanged)
        self.ui.horizontalScrollBar.valueChanged.connect(lambda: self.onScrollBarMove())
        self.updateChart.connect(self.onUpdateChart)
        self.updateTable.connect(self.onUpdateTable)

        self.ui.tableView.customContextMenuRequested.connect(self.onTableRightClick)
        self.enable_slot = partial(self.enable_zoom, self.ui.checkBox_2)
        self.disable_slot = partial(self.disable_zoom, self.ui.checkBox_2)
        self.ui.checkBox_2.stateChanged.connect(
            lambda x: self.enable_slot() if x else self.disable_slot()
        )
        self.ui.checkBox_2.setChecked(False)
        
        
        self.ui.useOpenGLCheckBox.stateChanged.connect(
            lambda x: self.graphWidget.useOpenGL(x)
        )
        
        self.ui.addEvent.hide()
        self.ui.addParam.clicked.connect(self.onAddParameterButtonClick)
        #self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.updateTime(datetime.datetime.strptime(self.gc.currentDateTimeString, "%Y-%m-%d %H:%M:%S.%f"))
        self.tableView.setStyleSheet(
            """
            * {
            font-size: 8pt;
            }
            QTableCornerButton::section{border-width: 0px; border-color: #BABABA; border-style:solid;}
            """
        )

    def plot(self, dfList):
        self.graphWidget.axes.clear()
        if not dfList or len(dfList) == 0:
            return
        all_param_list = [] 
        for df in dfList:
            all_param_list.append([col for col in df.columns if col not in ["Time", "log_hash"]])
            if len(df) == 0:
                continue
            df["Time"] = df["Time"].apply(
                lambda x: self.unixTimeMillis(x.to_pydatetime())
            )
            self.minX = df["Time"].min()
            self.maxX = df["Time"].max()
            colorindex = 0
            for col in df.columns:

                print(col)
                if col in ["log_hash", "Time"]:
                    continue
                df = df.fillna(np.NaN)
                dfNotNa = df.loc[df[col].notna()]
                if len(dfNotNa) > 0:
                    if self.minY is None:
                        self.minY = dfNotNa[col].min()
                    elif self.minY > dfNotNa[col].min():
                        self.minY = dfNotNa[col].min()
                    if self.maxY is None:
                        self.maxY = dfNotNa[col].max()
                    elif self.maxY < dfNotNa[col].max():
                        self.maxY = dfNotNa[col].max()
                color = self.colorDict[col]
                newline = self.graphWidget.axes.plot(
                    x=df["Time"].to_list(),
                    y=df[col].to_list(),
                    connect="finite",
                    stepMode = "right",
                    pen=pg.mkPen(color, width=1),
                )
                self.lineDict[col] = newline
                colorindex += 1
            self.graphWidget.axes.setLimits(
                xMin=self.minX,
                xMax=self.maxX,
                yMin=self.minY - 4,
                yMax=self.maxY,
                minXRange=30,
                maxXRange=30,
                minYRange=1,
            )
            self.graphWidget.axes.addItem(self.vLine, ignoreBounds=True)
            self.graphWidget.axes.addItem(self.cursorVLine, ignoreBounds=True)
            self.graphWidget.axes.addItem(self.cursorHLine, ignoreBounds=True)
            self.ui.horizontalScrollBar.setMaximum(int(self.maxX - self.minX - 30))
            self.drawCursor(self.minX)
            self.moveChart(self.minX)
        all_param_list = [item for sublist in all_param_list for item in sublist]
        plot_title = "{}".format(", ".join(all_param_list))
        self.graphWidget.axes.setTitle(plot_title)

    def chartXRangeChanged(self):
        x1 = self.getCurrentX()
        print("chartXRangeChanged")
        if not self.moveFromChart:
            self.moveFromChart = True
            newScrollVal = int(x1 - self.minX)
            print("move scroll bar", newScrollVal)
            if (
                newScrollVal >= 0
                or newScrollVal <= self.ui.horizontalScrollBar.maximum()
            ):
                self.ui.horizontalScrollBar.setValue(newScrollVal)
            self.moveFromChart = False

    def mouseMoved(self, pos):
        mousePoint = self.graphWidget.axes.vb.mapSceneToView(pos)
        self.graphWidget.axes.setTitle(
            "<span style='font-size: 10pt'>x=%s, <span style='font-size: 10pt'>y=%0.1f</span>"
            % (epochToDateString(mousePoint.x()), mousePoint.y())
        )
        self.cursorVLine.setPos(mousePoint.x())
        self.cursorHLine.setPos(mousePoint.y())

    def getCurrentX(self):
        x1 = self.graphWidget.axes.viewRange()[0][0]
        return x1

    def onScrollBarMove(self):
        value = self.ui.horizontalScrollBar.value()
        x = self.minX + value
        zoom_state_before_disable_slot = self.zoom_enabled
        if not self.moveFromChart:
            if self.zoom_enabled == True:
                self.disable_slot()
            self.moveChart(x)
            if zoom_state_before_disable_slot == True:
                self.enable_slot()
        self.moveFromChart = False

    def onClick(self, event):
        if event.button() == Qt.LeftButton:
            x = self.graphWidget.axes.vb.mapSceneToView(event.scenePos()).x()
            self.timeSelected.emit(x)

    def drawCursor(self, x):
        self.vLine.setPos(x) 

    def updateInternal(self):
        print("updateInternal")
        time = self.newTime
        if self.gc.databasePath is not None:
            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                self.reQueryChartData(dbcon)
                self.reQueryTableData(dbcon, time)

    def reQueryChartData(self, dbcon):
        import linechart_query
        if self.lastChartParamList == self.paramListDict:
            return
        self.lastChartParamList = {}
        self.lastChartParamList.update(self.paramListDict)
        chartDFList = linechart_query.get_chart_df(dbcon, self.paramListDict, self.gc)
        if chartDFList is None:
            return
        self.updateChart.emit(chartDFList)

    def reQueryTableData(self, dbcon, time):
        import linechart_query
        df = linechart_query.get_table_df_by_time(dbcon, time, self.paramListDict, self.gc)
        if df is None:
            return
        df = df.loc[df["param"] != "Time"]
        df["color"] = None
        df["color"] = df.apply(lambda x: self.colorDict[x["param"]], axis=1)
        df.columns = ["Element", "Value", "color"]
        df = df.reset_index(drop=True)
        dm = df[df.columns].apply(lambda x: x.duplicated())
        df[df.columns] = df[df.columns].mask(dm, "")
        self.tableViewDF = df
        model = dataframe_model.DataFrameModel(df)
        self.updateTable.emit(model)

    def onUpdateChart(self, df):
        print("onUpdateChart")
        self.plot(df)

    def onUpdateTable(self, model):
        print("onUpdateTable")
        self.ui.tableView.setModel(model)
        if self.minX is not None:
            x = self.unixTimeMillis(self.newTime)
            self.moveChart(x)
            self.drawCursor(x)

    def updateTime(self, time):
        self.newTime = time
        worker = Worker(self.updateInternal)
        self.gc.threadpool.start(worker)

    def moveChart(self, x):
        try:
            self.graphWidget.axes.setXRange(x, x)
        except:
            pass

    def closeEvent(self, event):
        indices = [i for i, x in enumerate(self.gc.openedWindows) if x == self]
        for index in indices:
            self.gc.openedWindows.pop(index)
        self.close()
        event.accept()

    def onTableRightClick(self, QPos=None):
        index = self.ui.tableView.indexAt(QPos)
        if index.isValid():
            name = self.tableViewDF.iloc[index.row(), 0]
            color = self.tableViewDF.iloc[index.row(), 2]
            menu = QMenu()
            changeColor = menu.addAction("Change Color")
            removeParam = menu.addAction("Remove Param")
            action = menu.exec_(self.ui.tableView.mapToGlobal(QPos))
            if action == changeColor:
                dlg = color_dialog.ColorDialog(name, color, self.onColorSet)
                dlg.show()
            elif action == removeParam:
                remove_index = list(self.paramListDict.keys()).index(name)
                del self.paramList[remove_index]
                del self.paramListDict[name]
                self.updateTime(self.newTime)

    def onAddParameterButtonClick(self):
        dlg = add_param_dialog.AddParamDialog(self.onParamAdded, self.gc)
        dlg.show()

    def onParamAdded(self, paramDict):
        param_alias_name = paramDict["name"]
        if "selected_ue" in paramDict:
            if paramDict["selected_ue"] is not None:
                ue_suffix = "(" + self.gc.device_configs[paramDict["selected_ue"]]["name"] + ")"
                if ue_suffix not in param_alias_name:
                    param_alias_name = param_alias_name + ue_suffix
        if param_alias_name not in self.paramListDict:
            dict = {"name":param_alias_name, "selected_ue":paramDict["selected_ue"]}
            self.paramList.append(dict)
            self.paramListDict[param_alias_name] = paramDict
            color = get_default_color_for_index(self.colorindex)
            self.colorDict[param_alias_name] = color
            self.colorindex += 1
            self.updateTime(self.newTime)
        # print( self.paramList)

    def onColorSet(self, name, color):
        self.colorDict[name] = color
        self.updateInternal()
        self.lineDict[name].setPen(color, width=2)

    def enable_zoom(self, checkbox):
        self.zoom_enabled = True
        self.graphWidget.axes.setMouseEnabled(x=True, y=True)
        self.graphWidget.axes.setLimits(
            minXRange=None, maxXRange=None, maxYRange=None, yMin=None, yMax=None,
        )

    def disable_zoom(self, checkbox):
        self.zoom_enabled = False
        self.graphWidget.axes.setMouseEnabled(x=True, y=False)
        x_range = self.graphWidget.axes.viewRange()[0]
        x_diff = x_range[1] - x_range[0]
        self.graphWidget.axes.setLimits(
            minXRange=x_diff, maxXRange=x_diff, minYRange=1,
        )


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = LineChart()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()