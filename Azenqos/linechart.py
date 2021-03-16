from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.uic import loadUi
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import numpy as np
import datetime
import math

import azq_utils
from azq_utils import get_default_color_for_index

class TimeAxisItem(pg.AxisItem):
    """Internal timestamp for x-axis"""
    def __init__(self, *args, **kwargs):
        super(TimeAxisItem, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """Function overloading the weak default version to provide timestamp"""
        return [datetime.datetime.fromtimestamp(value/1000.0, tz=datetime.timezone.utc).strftime("%m-%d-%Y %H:%M:%S") for value in values]

class Linechart(QtWidgets.QDialog):

    epoch = datetime.datetime.utcfromtimestamp(0)
    def unix_time_millis(self, dt):
        return (dt - self.epoch).total_seconds() * 1000.0

    def __init__(self, *args, **kwargs):
        super(Linechart, self).__init__(*args, **kwargs)
        pg.setConfigOptions(background="w", antialias=True)
        pg.TickSliderItem(orientation="bottom", allowAdd=True)
        self.ui = loadUi(azq_utils.get_local_fp("linechart.ui"), self)
        self.lines = []
        self.color_dict = {}

    def plot(self, df):
        df["Time"] = df["Time"].apply(lambda x: self.unix_time_millis(x.to_pydatetime()))
        min_y = None
        max_y = None
        min_x = df["Time"].min()
        max_x = df["Time"].max()
        self.graphWidget = pg.GraphicsWindow()
        # self.stringaxis = pg.AxisItem(orientation="bottom")
        self.graphWidget.axes = self.graphWidget.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        
        # self.setLayout(vertical_layout)
        self.graphWidget.axes.hideButtons()
        self.graphWidget.axes.showGrid(x=False, y=True)
        self.graphWidget.axes.setMouseEnabled(x=True, y=False)
        # self.graphWidget.axes.scene().sigMouseClicked.connect(self.get_table_data)
        colorindex = 0
        for col in df.columns:
            print(col)
            if col in ["log_hash", "Time"]:
                continue
            if min_y is None:
                min_y = df[col].min()
            elif min_y > df[col].min():
                min_y = df[col].min()
            if max_y is None:
                max_y = df[col].max()
            elif max_y < df[col].max():
                max_y = df[col].max()
            newline = self.graphWidget.axes.plot(x=df["Time"].to_list(), y=df[col].to_list())
            color = get_default_color_for_index(colorindex)
            newline.setPen(pg.mkPen(color, width=2))
            self.lines.append(newline)
            self.color_dict[col] =  color
            colorindex+=1
        print(self.color_dict)
        self.graphWidget.axes.setLimits(
            xMin=min_x,
            xMax=max_x+1000,
            minXRange=60*1000,
            maxXRange=60*1000,
        )
        self.graphWidget.scene().sigMouseClicked.connect(self.onClick)
        self.draw_cursor(min_x)
        self.ui.tmp2.addWidget(self.graphWidget)

    def onClick(self, event):
        items = self.graphWidget.scene().items(event.scenePos())
        self.draw_cursor(self.graphWidget.axes.vb.mapSceneToView(event.scenePos()).x())

    def draw_cursor(self, x):
        #cross hair
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('k', width=4))
        self.graphWidget.axes.addItem(self.vLine, ignoreBounds=True)
        self.vLine.setPos(x)
        # self.vb = self.graphWidget.axes.vb

        # # set mouse event
        # self.graphWidget.setMouseTracking(True)
        # self.graphWidget.viewport().installEventFilter(self)

    def update_time(self, df, time):
        df = df.loc[df["param"]!="Time"]
        df["color"] = None
        df["color"] = df.apply(lambda x: self.color_dict[x["param"]], axis=1)
        df.columns = ['Element', 'Value', "color"]
        print(df)
        # for i,row in df.iterrows():
        #     print(row)
        newitem = QTableWidgetItem("ttttttttttt")
        self.ui.tableWidget.setItem(0, 0, newitem)
        self.ui.tableWidget.setHorizontalHeaderLabels(df.columns)
        
        self.ui.tableWidget.horizontalHeader().setVisible(True)
        self.ui.tableWidget.horizontalHeader().setHighlightSections(True)
        # self.ui.tableWidget




def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Linechart()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()