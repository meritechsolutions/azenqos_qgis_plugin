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
        self.vLine = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('k', width=4))
        self.graphWidget.axes.addItem(self.vLine, ignoreBounds=True)
        
        # self.setLayout(vertical_layout)
        self.graphWidget.axes.hideButtons()
        self.graphWidget.axes.showGrid(x=True, y=False)
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
            color = get_default_color_for_index(colorindex)
            newline = self.graphWidget.axes.plot(x=df["Time"].to_list(), y=df[col].to_list(), pen = pg.mkPen(color, width=2))
            # newline.setPen(pg.mkPen(color, width=2))
            self.lines.append(newline)
            self.color_dict[col] =  color
            colorindex+=1
        print(self.color_dict)
        self.graphWidget.axes.setLimits(
            xMin=min_x,
            xMax=max_x,
            minXRange=60*1000,
            maxXRange=60*1000,
        )
        self.ui.tmp2.addWidget(self.graphWidget)
        self.draw_cursor(min_x)
        self.move_chart(min_x)
        self.min_x = min_x
        self.max_x = max_x
        self.move_from_chart = False
        self.ui.horizontalScrollBar.setMaximum(self.max_x - self.min_x)
        self.ui.horizontalScrollBar.valueChanged.connect(lambda: self.on_scroll_bar_move()) 
        self.graphWidget.scene().sigMouseClicked.connect(self.onClick)
        self.graphWidget.axes.sigXRangeChanged.connect(self.chart_x_range_changed)

    
    def chart_x_range_changed(self):
        x1 = self.get_current_x()
        # x_diff = self.max_x - self.min_x
        # p_pos = (x1 - self.min_x) / x_diff * 100
        # self.ui.horizontalScrollBar.setValue(p_pos)
        # print(self.graphWidget.axes.viewRange())
        if not self.move_from_chart:
            self.move_from_chart = True
            self.ui.horizontalScrollBar.setValue(x1 - self.min_x)


    def get_current_x(self):
        x1 = self.graphWidget.axes.viewRange()[0][0]
        return x1


    def on_scroll_bar_move(self):
        print("on_scroll_bar_move")
        value = self.ui.horizontalScrollBar.value() 
        # x_diff = self.max_x - self.min_x
        # pos = self.min_x + (x_diff * value / 100)
        # self.move_chart(pos)
        x = self.min_x + value
        if not self.move_from_chart :
            self.move_chart(self.min_x + value)
        self.move_from_chart = False

    def onClick(self, event):
        items = self.graphWidget.scene().items(event.scenePos())
        x = self.graphWidget.axes.vb.mapSceneToView(event.scenePos()).x()
        self.draw_cursor(x)
        self.move_chart(x)

    def draw_cursor(self, x):
        #cross hair
        self.vLine.setPos(x)
        # self.vb = self.graphWidget.axes.vb

        # # set mouse event
        # self.graphWidget.setMouseTracking(True)
        # self.graphWidget.viewport().installEventFilter(self)

    def update_time(self, df, time):
        x = self.unix_time_millis(time)
        self.move_chart(x)
        # df = df.loc[df["param"]!="Time"]
        # df["color"] = None
        # df["color"] = df.apply(lambda x: self.color_dict[x["param"]], axis=1)
        # df.columns = ['Element', 'Value', "color"]
        # print(df)
        # # for i,row in df.iterrows():
        # #     print(row)
        # newitem = QTableWidgetItem("ttttttttttt")
        # self.ui.tableWidget.setItem(0, 0, newitem)
        # self.ui.tableWidget.setHorizontalHeaderLabels(df.columns)
        
        # self.ui.tableWidget.horizontalHeader().setVisible(True)
        # self.ui.tableWidget.horizontalHeader().setHighlightSections(True)
        # # self.ui.tableWidget

    def move_chart(self, x):
        self.graphWidget.axes.setXRange(x, x)




def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Linechart()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()