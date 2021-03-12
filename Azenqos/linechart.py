from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.uic import loadUi
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import numpy as np
import azq_utils
import datetime
import math

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

    def plot(self, df):
        df["time"] = df["time"].apply(lambda x: self.unix_time_millis(x.to_pydatetime()))
        min_y = None
        max_y = None
        min_x = df["time"].min()
        max_x = df["time"].max()
        self.graphWidget = pg.GraphicsWindow()
        # self.stringaxis = pg.AxisItem(orientation="bottom")
        self.graphWidget.axes = self.graphWidget.addPlot(axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        
        # self.setLayout(vertical_layout)
        self.graphWidget.axes.hideButtons()
        # self.graphWidget.axes.showGrid(x=True, y=True)
        self.graphWidget.axes.setMouseEnabled(x=True, y=False)
        # self.graphWidget.axes.scene().sigMouseClicked.connect(self.get_table_data)
        
        for col in df.columns:
            print(col)
            if col in ["log_hash", "time"]:
                continue
            if min_y is None:
                min_y = df[col].min()
            elif min_y > df[col].min():
                min_y = df[col].min()
            if max_y is None:
                max_y = df[col].max()
            elif max_y < df[col].max():
                max_y = df[col].max()
            self.graphWidget.axes.plot(x=df["time"].to_list(), y=df[col].to_list(), pen=pg.mkPen('b'))
        self.graphWidget.axes.setLimits(
            xMin=min_x,
            xMax=max_x+1000,
            minXRange=1*1000,
            maxXRange=1*1000,
        )
        self.ui.tmp2.addWidget(self.graphWidget)

def main():
    app = QtWidgets.QApplication(sys.argv)
    main = Linechart()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':         
    main()