import contextlib
import datetime
import sqlite3
import sys
import copy
from functools import partial

import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMenu
# from qgis.gui import QgsColorButton
from PyQt5.uic import loadUi

import add_param_dialog
import linechart_event_dialog
import azq_utils
import color_dialog
import dataframe_model
from azq_utils import get_default_color_for_index
from worker import Worker


def epochToDateString(epoch):
    try:
        return datetime.datetime.fromtimestamp(epoch).strftime("%m-%d-%Y %H:%M:%S")
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
        self.paramList = paramList
        pg.setConfigOptions(background="w", useOpenGL=True)
        pg.TickSliderItem(orientation="bottom", allowAdd=True)
        self.paramListDict = {}
        self.eventList = eventList
        
        for paramDict in self.paramList:
            param_alias_name = paramDict["name"]
            if "selected_ue" in paramDict:
                if paramDict["selected_ue"] is not None:
                    ue_suffix = "(" + self.gc.device_configs[paramDict["selected_ue"]]["name"] + ")"
                    if ue_suffix not in param_alias_name:
                        param_alias_name = param_alias_name + ue_suffix
            self.paramListDict[param_alias_name] = paramDict
        self.viewBoxList = []
        self.colorDict = {}
        self.colorindex = 0
        for paramDict in self.paramListDict:
            color = get_default_color_for_index(self.colorindex)
            self.colorDict[paramDict] = color
            self.colorindex += 1
        self.lastChartParamList = None
        self.lastEventList = None
        self.eventViewBox = None
        self.minX = None
        self.maxX = None
        self.mousecoordinatesdisplay = None
        self.moveFromChart = False
        self.ui = loadUi(azq_utils.get_module_fp("linechart3.ui"), self)
        self.axisDict = {}
        self.lineDict = {}
        self.graphWidget = None
        self.graphWidget = pg.GraphicsWindow()
        self.graphWidget.axes = self.graphWidget.addPlot(
            axisItems={"bottom": TimeAxisItem(orientation="bottom")}
        )
        self.vLine = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen("k", width=4)
        )
        self.graphWidget.axes.hideButtons()
        self.graphWidget.axes.showGrid(x=False, y=True)
        self.graphWidget.axes.setMouseEnabled(x=True, y=False)
        self.graphWidget.scene().sigMouseClicked.connect(self.onClick)
        self.ui.verticalLayout_3.addWidget(self.graphWidget)
        self.graphWidget.axes.sigXRangeChanged.connect(self.chartXRangeChanged)
        self.ui.horizontalScrollBar.valueChanged.connect(lambda: self.onScrollBarMove())
        self.updateChart.connect(self.onUpdateChart)
        self.updateTable.connect(self.onUpdateTable)

        self.tick_font = QFont()
        self.tick_font.setPixelSize(10)
        self.graphWidget.axes.getAxis("bottom").setStyle(tickFont=self.tick_font)
        #self.graphWidget.getAxis("bottom").setStyle(tickTextOffset=20)

        self.ui.tableView.customContextMenuRequested.connect(self.onTableRightClick)
        self.ui.tableView.clicked.connect(self.onTableClick)
        self.enable_slot = partial(self.enable_zoom, self.ui.checkBox_2)
        self.disable_slot = partial(self.disable_zoom, self.ui.checkBox_2)
        self.ui.checkBox_2.stateChanged.connect(
            lambda x: self.enable_slot() if x else self.disable_slot()
        )
        self.ui.checkBox_2.setChecked(False)
        self.zoom_enabled = False
        self.ui.addEvent.clicked.connect(self.onEventParameterButtonClick)
        self.ui.addParam.clicked.connect(self.onAddParameterButtonClick)
        #self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        if self.gc.currentDateTimeString is not None:
            self.updateTime(datetime.datetime.strptime(self.gc.currentDateTimeString, "%Y-%m-%d %H:%M:%S.%f"))
        self.ui.tableView.setStyleSheet(
            """
            * {
            font-size: 11px;
            }
            QTableCornerButton::section{border-width: 0px; border-color: #BABABA; border-style:solid;}
            """
        )

    def plot(self, dfList):
        self.graphWidget.axes.clear()
        self.graphWidget.clear()
        for viewBox in self.viewBoxList:
            viewBox.clear()
        self.viewBoxList.clear()
        self.graphWidget.axes.hideAxis("left")
        self.graphWidget.axes.showGrid(x=False, y=True)
        viewBox1 = None
        prevViewBox = None
        colIndex = len(dfList) + 1
        self.graphWidget.addItem(
            self.graphWidget.axes, row=2, col=colIndex, rowspan=1, colspan=1
        )
        colIndex -= 1
        
        self.minX = None
        self.maxX = None
        for df in dfList:
            if len(df) == 0:
                continue
            df["Time"] = df["Time"].apply(
                lambda x: self.unixTimeMillis(x.to_pydatetime())
            )
            minX = df["Time"].min()
            maxX = df["Time"].max()
            if self.minX is None or self.minX > minX:
                self.minX = minX
            if self.maxX is None or self.maxX < maxX:
                self.maxX = maxX
        for df in dfList:
            if len(df) == 0:
                continue
            axis = pg.AxisItem("left")
            axis.setStyle(tickFont=self.tick_font)
            viewBox = None
            if viewBox1 == None:
                viewBox1 = self.graphWidget.axes.vb
                viewBox = viewBox1
            else:
                viewBox = pg.ViewBox()
            self.viewBoxList.append(viewBox)
            self.graphWidget.addItem(axis, row=2, col=colIndex, rowspan=1, colspan=1)
            viewBox.setMouseEnabled(x=True, y=False)
            colIndex -= 1
            self.graphWidget.scene().addItem(viewBox)
            axis.linkToView(viewBox)
            if prevViewBox != None:
                viewBox.setXLink(prevViewBox)
            prevViewBox = viewBox
            minY = None
            maxY = None
            colorindex = 0
            for col in df.columns:
                print(col)
                if col in ["log_hash", "Time"]:
                    continue
                color = self.colorDict[col]
                axis.setLabel(col, **{'font-size': '10pt'})
                axis.setPen(color, width=2)
                self.axisDict[col] = axis
                df = df.fillna(np.NaN)
                dfNotNa = df.loc[df[col].notna()]
                if len(dfNotNa) > 0:
                    if minY is None:
                        minY = dfNotNa[col].min()
                    elif minY > dfNotNa[col].min():
                        minY = dfNotNa[col].min()
                    if maxY is None:
                        maxY = dfNotNa[col].max()
                    elif maxY < dfNotNa[col].max():
                        maxY = dfNotNa[col].max()
                newline = pg.PlotCurveItem(
                    x=df["Time"].to_list(),
                    y=df[col].to_list(),
                    stepMode = "right",
                    connect="finite",
                    pen=pg.mkPen(color, width=2),
                )
                self.lineDict[col] = newline
                viewBox.addItem(newline)
                colorindex += 1
            viewBox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)
            if minY is not None:
                viewBox.setLimits(
                    xMin=self.minX,
                    xMax=self.maxX,
                    yMin=minY - 4,
                    yMax=maxY + 10,
                    minXRange=20,
                    maxXRange=20,
                    minYRange=1,
                )
            self.ui.horizontalScrollBar.setMaximum(self.maxX - self.minX - 20)
            self.drawCursor(self.minX)
            self.moveChart(self.minX)
        if len(self.eventList) > 0:
            self.eventViewBox = pg.ViewBox()
            self.viewBoxList.append(self.eventViewBox)
            self.graphWidget.addItem(axis, row=2, col=colIndex-1, rowspan=1, colspan=1)
            self.graphWidget.scene().addItem(self.eventViewBox)
            self.eventViewBox.setMouseEnabled(x=True, y=False)
            if prevViewBox != None:
                self.eventViewBox.setXLink(prevViewBox)
            if minY is not None:
                self.eventViewBox.setLimits(
                    xMin=self.minX,
                    xMax=self.maxX,
                    yMin=minY - 4,
                    yMax=maxY + 10,
                    minXRange=20,
                    maxXRange=20,
                    minYRange=1,
                )
            for event in self.eventList:
                eventName = event["event name"]
                color = event["color"]
                with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                    eventDF = pd.read_sql("select time from events where name = '{}'".format(eventName), dbcon, parse_dates=['time'])
                    eventDF["time"] = eventDF["time"].apply(
                        lambda x: self.unixTimeMillis(x.to_pydatetime())
                    )
                    firstRow = []
                    firstRow.insert(0, {'event name': 'first', 'value': -200000, 'time': eventDF["time"][0]-10, 'index': 0})
                    eventDF = eventDF.reset_index()
                    eventDF["value"] = None
                    eventDF.loc[eventDF["index"]%2 == 0, "value"] = 200000
                    eventDF.loc[eventDF["index"]%2 != 0, "value"] = -200000
                    pd.concat([pd.DataFrame(firstRow), eventDF], ignore_index=True)
                    eventLine = pg.PlotCurveItem(
                        x=eventDF["time"].to_list(),
                        y=eventDF["value"].to_list(),
                        stepMode = "right",
                        connect="finite",
                        pen=pg.mkPen(color, width=1),
                    )
                    self.eventViewBox.addItem(eventLine)
            
            self.eventViewBox.enableAutoRange(axis=pg.ViewBox.XYAxes, enable=True)

        def updateViews():
            for viewBox in self.viewBoxList:
                if viewBox != viewBox1:
                    viewBox.setGeometry(viewBox1.sceneBoundingRect())

        if viewBox1:
            viewBox1.sigResized.connect(updateViews)
            viewBox1.addItem(self.vLine, ignoreBounds=True)
        updateViews()

    def chartXRangeChanged(self):
        x1 = self.getCurrentX()
        print("chartXRangeChanged")
        if not self.moveFromChart:
            self.moveFromChart = True
            newScrollVal = x1 - self.minX
            print("move scroll bar", newScrollVal)
            if (
                newScrollVal >= 0
                or newScrollVal <= self.ui.horizontalScrollBar.maximum()
            ):
                self.ui.horizontalScrollBar.setValue(x1 - self.minX)
            self.moveFromChart = False

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
            self.graphWidget.scene().items(event.scenePos())
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
        if self.lastChartParamList == self.paramListDict and self.lastEventList == self.eventList:
            return
        self.lastChartParamList = {}
        self.lastChartParamList.update(self.paramListDict)
        self.lastEventList = copy.deepcopy(self.eventList)
        chartDFList = linechart_query.get_chart_df(dbcon, self.paramListDict, self.gc)
        self.updateChart.emit(chartDFList)

    def reQueryTableData(self, dbcon, time):
        import linechart_query

        df = linechart_query.get_table_df_by_time(dbcon, time, self.paramListDict, self.gc)
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

    def onTableClick(self,item):
        if item.column() == 2: 
            name = self.tableViewDF.iloc[item.row(), 0]
            color = self.tableViewDF.iloc[item.row(), 2]
            dlg = color_dialog.ColorDialog(name, color, self.onColorSet)
            dlg.show()

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
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.show()

    def onEventParameterButtonClick(self):
        dlg = linechart_event_dialog.linechart_event_dialog(self.gc, self.onEventAdded, self.eventList)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.show()

    def onEventAdded(self, eventList):
        self.eventList = eventList
        self.updateTime(self.newTime)

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
        self.axisDict[name].setPen(color, width=2)

    def enable_zoom(self, checkbox):
        self.zoom_enabled = True
        for viewBox in self.viewBoxList:
            if viewBox == self.eventViewBox:
                viewBox.setLimits(
                    minXRange=None, maxXRange=None
                )
            else:
                viewBox.setMouseEnabled(x=True, y=True)
                viewBox.setLimits(
                    minXRange=None, maxXRange=None, maxYRange=None, yMin=None, yMax=None,
                )

    def disable_zoom(self, checkbox):
        self.zoom_enabled = False
        for viewBox in self.viewBoxList:
            viewBox.setMouseEnabled(x=True, y=False)
            x_range = viewBox.viewRange()[0]
            x_diff = x_range[1] - x_range[0]
            viewBox.setLimits(
                minXRange=x_diff, maxXRange=x_diff, minYRange=1,
            )


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = LineChart()
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
