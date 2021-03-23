from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.uic import loadUi
from PyQt5.QtCore import pyqtSignal
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import numpy as np
import datetime
import math
import sqlite3
import pandas as pd

import dataframe_model
import azq_utils
from azq_utils import get_default_color_for_index
from worker import Worker


def epochToDateString(epoch):
    return datetime.datetime.fromtimestamp(epoch).strftime("%m-%d-%Y %H:%M:%S")

class TimeAxisItem(pg.AxisItem):
    """Internal timestamp for x-axis"""

    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """Function overloading the weak default version to provide timestamp"""
        return [epochToDateString(value) for value in values]

class Linechart(QtWidgets.QDialog):
    timeSelected = pyqtSignal(float)
    updateChart = pyqtSignal(object)
    updateTable = pyqtSignal(object)

    def unixTimeMillis(self, dt):
        return azq_utils.datetimeStringtoTimestamp(dt.strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            ))

    def __init__(self, gc):
        super().__init__(None)
        self.gc = gc
        pg.setConfigOptions(background="w", antialias=True)
        pg.TickSliderItem(orientation="bottom", allowAdd=True)
        self.minX = None
        self.maxX = None
        self.minY = None
        self.maxY = None
        self.mousecoordinatesdisplay = None
        self.moveFromChart = False
        self.ui = loadUi(azq_utils.get_local_fp("linechart2.ui"), self)
        self.lines = []
        self.colorDict = {}
        self.createChartFunc = None
        self.updateFunc = None
        self.graphWidget = None
        self.graphWidget = pg.GraphicsWindow()
        self.graphWidget.axes = self.graphWidget.addPlot(
            axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.vLine = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen('k', width=4))
        self.graphWidget.axes.addItem(self.vLine, ignoreBounds=True)
        self.cursorVLine = pg.InfiniteLine(
            angle=90, movable=False, pen=pg.mkPen('k', width=1))
        self.cursorHLine = pg.InfiniteLine(
            angle=0, movable=False, pen=pg.mkPen('k', width=1))
        self.graphWidget.axes.addItem(self.cursorVLine, ignoreBounds=True)
        self.graphWidget.axes.addItem(self.cursorHLine, ignoreBounds=True)
        self.graphWidget.axes.hideButtons()
        self.graphWidget.axes.showGrid(x=False, y=True)
        self.graphWidget.axes.setMouseEnabled(x=True, y=True)
        self.graphWidget.scene().sigMouseClicked.connect(self.onClick)
        self.graphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
        self.ui.verticalLayout_3.addWidget(self.graphWidget)
        self.graphWidget.axes.sigXRangeChanged.connect(self.chartXRangeChanged)
        self.ui.horizontalScrollBar.valueChanged.connect(
            lambda: self.onScrollBarMove())
        self.updateChart.connect(self.onUpdateChart)
        self.updateTable.connect(self.onUpdateTable)
        
        # self.ui.tableView.setMaximumSize(16777215, 16777215)

    def plot(self, dfList):
        if not isinstance(dfList, list):
            dfList = [dfList]
        for df in dfList:
            if len(df) == 0:
                continue
            df["Time"] = df["Time"].apply(
                lambda x: self.unixTimeMillis(x.to_pydatetime()))
            self.minX = df["Time"].min()
            self.maxX = df["Time"].max()
            colorindex = 0
            for col in df.columns:
                
                print(col)
                if col in ["log_hash", "Time"]:
                    continue
                df=df.fillna(np.NaN)
                dfNotNa=df.loc[df[col].notna()]
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
                    x=df["Time"].to_list(), y=df[col].to_list(), connect="finite", pen=pg.mkPen(color, width=2))
                self.lines.append(newline)
                colorindex += 1
            self.graphWidget.axes.setLimits(
                xMin=self.minX,
                xMax=self.maxX,
                yMin=self.minY-4,
                yMax=self.maxY,
                minXRange=1,
                maxXRange=60,
                minYRange=1,
            )
            self.ui.horizontalScrollBar.setMaximum(self.maxX - self.minX - 30)
            self.drawCursor(self.minX)
            self.moveChart(self.minX)

    def chartXRangeChanged(self):
        x1 = self.getCurrentX()
        print('chartXRangeChanged')
        if not self.moveFromChart:
            self.moveFromChart = True
            newScrollVal = x1 - self.minX
            print('move scroll bar', newScrollVal)
            if newScrollVal >= 0 or newScrollVal <= self.ui.horizontalScrollBar.maximum():
                self.ui.horizontalScrollBar.setValue(x1 - self.minX)
            self.moveFromChart = False

    def mouseMoved(self, pos):
        mousePoint = self.graphWidget.axes.vb.mapSceneToView(pos)
        self.graphWidget.axes.setTitle("<span style='font-size: 10pt'>x=%s, <span style='font-size: 10pt'>y=%0.1f</span>" %
                                       (epochToDateString(mousePoint.x()), mousePoint.y()))
        self.cursorVLine.setPos(mousePoint.x())
        self.cursorHLine.setPos(mousePoint.y())

    def getCurrentX(self):
        x1 = self.graphWidget.axes.viewRange()[0][0]
        return x1

    def onScrollBarMove(self):
        value = self.ui.horizontalScrollBar.value()
        x = self.minX + value
        if not self.moveFromChart:
            self.moveChart(self.minX + value)
        self.moveFromChart = False

    def onClick(self, event):
        items = self.graphWidget.scene().items(event.scenePos())
        x = self.graphWidget.axes.vb.mapSceneToView(
            event.scenePos()).x()
        self.timeSelected.emit(x)

    def drawCursor(self, x):
        self.vLine.setPos(x)

    def updateInternal(self):
        print('updateInternal')
        time = self.newTime
        if self.gc.databasePath is not None and self.updateFunc is not None and self.createChartFunc is not None:
            with sqlite3.connect(self.gc.databasePath) as dbcon:
                if self.minX is None:
                    print('query chartDF')
                    chartDFList = self.createChartFunc(dbcon)
                    if not isinstance(chartDFList, list):
                        chartDFList = [chartDFList]
                    colorindex = 0
                    for chartDF in chartDFList:
                        for col in chartDF.columns:
                            if col in ["log_hash", "Time"]:
                                continue
                            color = get_default_color_for_index(colorindex)
                            self.colorDict[col] = color
                            colorindex += 1
                    self.updateChart.emit(chartDFList)
                df = self.updateFunc(dbcon, time)
                df = df.loc[df["param"] != "Time"]
                df["color"] = None
                df["color"] = df.apply(lambda x: self.colorDict[x["param"]], axis=1)
                df.columns = ['Element', 'Value', "color"]
                df = df.reset_index(drop=True)
                dm = df[df.columns].apply(lambda x: x.duplicated())
                df[df.columns] = df[df.columns].mask(dm, '')
                model = dataframe_model.DataFrameModel(df)
                self.updateTable.emit(model)

    def onUpdateChart(self, df):
        print('onUpdateChart')
        self.plot(df)
    
    def onUpdateTable(self, model):
        print('onUpdateTable')
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

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Linechart()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
