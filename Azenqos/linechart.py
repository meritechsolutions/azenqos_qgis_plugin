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

import dataframe_model
import azq_utils
from azq_utils import get_default_color_for_index


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
        self.ui = loadUi(azq_utils.get_local_fp("linechart.ui"), self)
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
        self.graphWidget.axes.setMouseEnabled(x=True, y=False)
        self.graphWidget.setMinimumSize(800, 400)
        self.graphWidget.scene().sigMouseClicked.connect(self.onClick)
        self.graphWidget.scene().sigMouseMoved.connect(self.mouseMoved)
        self.ui.tmp2.addWidget(self.graphWidget)
        self.graphWidget.axes.sigXRangeChanged.connect(self.chartXRangeChanged)
        self.ui.horizontalScrollBar.valueChanged.connect(
            lambda: self.onScrollBarMove())

    def plot(self, df):
        df["Time"] = df["Time"].apply(
            lambda x: self.unixTimeMillis(x.to_pydatetime()))
        self.minX = df["Time"].min()
        self.maxX = df["Time"].max()
        colorindex = 0
        for col in df.columns:
            print(col)
            if col in ["log_hash", "Time"]:
                continue
            if self.minY is None:
                self.minY = df[col].min()
            elif self.minY > df[col].min():
                self.minY = df[col].min()
            if self.maxY is None:
                self.maxY = df[col].max()
            elif self.maxY < df[col].max():
                self.maxY = df[col].max()
            color = get_default_color_for_index(colorindex)
            newline = self.graphWidget.axes.plot(
                x=df["Time"].to_list(), y=df[col].to_list(), pen=pg.mkPen(color, width=2))
            self.lines.append(newline)
            self.colorDict[col] = color
            colorindex += 1
        print(self.colorDict)
        self.graphWidget.axes.setLimits(
            xMin=self.minX,
            xMax=self.maxX,
            minXRange=30,
            maxXRange=30,
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

    def updateTime(self, time):
        x = self.unixTimeMillis(time)
        if self.gc.databasePath is not None and self.updateFunc is not None and self.createChartFunc is not None:
            try:
                with sqlite3.connect(self.gc.databasePath) as dbcon:
                    if self.minX is None:
                        try:
                            self.plot(self.createChartFunc(dbcon))
                        except:
                            pass
                    df = self.updateFunc(dbcon, time)
                    df = df.loc[df["param"] != "Time"]
                    df["color"] = None
                    df["color"] = df.apply(lambda x: self.colorDict[x["param"]], axis=1)
                    df.columns = ['Element', 'Value', "color"]
                    df = df.reset_index(drop=True)
                    dm = df[df.columns].apply(lambda x: x.duplicated())
                    df[df.columns] = df[df.columns].mask(dm, '')
                    model = dataframe_model.DataFrameModel(df)
                    self.ui.tableView.setModel(model)
            except:
                pass
        if self.graphWidget is not None:
            self.moveChart(x)
            self.drawCursor(x)

    def moveChart(self, x):
        self.graphWidget.axes.setXRange(x, x)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Linechart()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
