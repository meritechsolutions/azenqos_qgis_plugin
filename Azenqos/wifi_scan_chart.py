import contextlib
import sqlite3
import os
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from worker import Worker
from PyQt5.uic import loadUi
import azq_utils
import datetime
from matplotlib.backends.qt_compat import  QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from scipy import interpolate

import data_query


freq_definitions_dict_5GHz_low = {
"4915" : {"channel": 183, "width": 10 },
"4920" : {"channel": 184, "width": 20 },
"4925" : {"channel": 185, "width": 10 },
"4935" : {"channel": 187, "width": 10 },
"4940" : {"channel": 188, "width": 20 },
"4945" : {"channel": 189, "width": 10 },
"4960" : {"channel": 192, "width": 20 },
"4980" : {"channel": 196, "width": 20 },
"5035" : {"channel": 7, "width": 10 },
"5040" : {"channel": 8, "width": 20 },
"5045" : {"channel": 9, "width": 10 },
"5055" : {"channel": 11, "width": 10 },
"5060" : {"channel": 12, "width": 20 },
"5080" : {"channel": 16, "width": 20 },
"5160" : {"channel": 32, "width": 20 },
"5170" : {"channel": 34, "width": 40 },
"5180" : {"channel": 36, "width": 20 },
"5190" : {"channel": 38, "width": 40 },
"5200" : {"channel": 40, "width": 20 },
"5210" : {"channel": 42, "width": 80 },
"5220" : {"channel": 44, "width": 20 },
"5230" : {"channel": 46, "width": 40 },
"5240" : {"channel": 48, "width": 20 },
"5250" : {"channel": 50, "width": 160},
"5260" : {"channel": 52, "width": 20 },
"5270" : {"channel": 54, "width": 40 },
"5280" : {"channel": 56, "width": 20 },
"5290" : {"channel": 58, "width": 80 },
"5300" : {"channel": 60, "width": 20 },
"5310" : {"channel": 62, "width": 40 },
"5320" : {"channel": 64, "width": 20 },
"5340" : {"channel": 68, "width": 20 },
}

freq_definitions_dict_5GHz_high = {
"5480" : {"channel": 96, "width": 20 },
"5500" : {"channel": 100, "width": 20 },
"5510" : {"channel": 102, "width": 40 },
"5520" : {"channel": 104, "width": 20 },
"5530" : {"channel": 106, "width": 80 },
"5540" : {"channel": 108, "width": 20 },
"5550" : {"channel": 110, "width": 40 },
"5560" : {"channel": 112, "width": 20 },
"5570" : {"channel": 114, "width": 160},
"5580" : {"channel": 116, "width": 20 },
"5590" : {"channel": 118, "width": 40 },
"5600" : {"channel": 120, "width": 20 },
"5610" : {"channel": 122, "width": 80 },
"5620" : {"channel": 124, "width": 20 },
"5630" : {"channel": 126, "width": 40 },
"5640" : {"channel": 128, "width": 20 },
"5660" : {"channel": 132, "width": 20 },
"5670" : {"channel": 134, "width": 40 },
"5680" : {"channel": 136, "width": 20 },
"5690" : {"channel": 138, "width": 80 },
"5700" : {"channel": 140, "width": 20 },
"5710" : {"channel": 142, "width": 40 },
"5720" : {"channel": 144, "width": 20 },
"5745" : {"channel": 149, "width": 20 },
"5755" : {"channel": 151, "width": 40 },
"5765" : {"channel": 153, "width": 20 },
"5775" : {"channel": 155, "width": 80 },
"5785" : {"channel": 157, "width": 20 },
"5795" : {"channel": 159, "width": 40 },
"5805" : {"channel": 161, "width": 20 },
"5825" : {"channel": 165, "width": 20 },
"5845" : {"channel": 169, "width": 20 },
"5865" : {"channel": 173, "width": 20 },
}

freq_definitions_dict_2_4GHz = {
"2412" : {"channel": 1 , "width": 22 },
"2417" : {"channel": 2 , "width": 22 },
"2422" : {"channel": 3 , "width": 22 },
"2427" : {"channel": 4 , "width": 22 },
"2432" : {"channel": 5 , "width": 22 },
"2437" : {"channel": 6 , "width": 22 },
"2442" : {"channel": 7 , "width": 22 },
"2447" : {"channel": 8 , "width": 22 },
"2452" : {"channel": 9 , "width": 22 },
"2457" : {"channel": 10, "width": 22 },
"2462" : {"channel": 11, "width": 22 },
"2467" : {"channel": 12, "width": 22 },
"2472" : {"channel": 13, "width": 22 },
"2484" : {"channel": 14, "width": 22 },
}

class wifi_scan_chart(QtWidgets.QDialog):
    update_chart = pyqtSignal(object)

    def __init__(self, gc, selected_ue=None, title="WiFi Scan Chart", mode = "2.4"):
        super(wifi_scan_chart, self).__init__(None)
        self.gc = gc
        self.title = title
        self.selected_ue = selected_ue
        if mode == "2.4":
            self.freq_definitions_dict = freq_definitions_dict_2_4GHz
        elif mode == "5l":
            self.freq_definitions_dict = freq_definitions_dict_5GHz_low
        elif mode == "5h":
            self.freq_definitions_dict = freq_definitions_dict_5GHz_high
        self.selected_logs = None
        if self.selected_ue is not None:
            self.selected_logs = self.gc.device_configs[self.selected_ue]["log_hash"]
        self.setupUi()

    def setupUi(self):
        dirname = os.path.dirname(__file__)
        self.ui = loadUi(azq_utils.get_module_fp("wifi_scan_chart.ui"), self)
        self.setWindowIcon(QIcon(QPixmap(os.path.join(dirname, "icon.png"))))
        self.setWindowTitle("WiFi Scan Chart")
        self.setGeometry(300, 300, 800, 400)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self._ax_ = self.figure.subplots()
        self.ui.chartLayout.addWidget(self.canvas)
        self.last_df = None
        
        self.update_chart.connect(self.on_update_chart)
        if self.gc.currentDateTimeString is not None:
            self.update_time(datetime.datetime.strptime(self.gc.currentDateTimeString, "%Y-%m-%d %H:%M:%S.%f"))
        
    def update_time(self, time):
        self.newTime = time
        worker = Worker(self.update_internal)
        self.gc.threadpool.start(worker)
    
    def update_internal(self):
        print("updateInternal")
        time = self.newTime
        if self.gc.databasePath is not None:
            with contextlib.closing(sqlite3.connect(self.gc.databasePath)) as dbcon:
                self.re_query_chart_data(dbcon, time)

    def re_query_chart_data(self, dbcon, time):
        df = data_query.get_wifi_scan_df(dbcon, time, self.selected_logs)
        self.update_chart.emit(df)

    def on_update_chart(self, df):
        print("onUpdateChart")
        self.plot(df)

    def plot(self, df, **kwargs):
        self._ax_.clear()
        x_ticks = [int(key) for key in self.freq_definitions_dict.keys()]
        self._ax_.axis(xmin=x_ticks[0]-4, xmax=x_ticks[-1]+4)
        self._ax_.set_xticks(x_ticks)
        x_tick_labels = [int(self.freq_definitions_dict[key]["channel"]) for key in self.freq_definitions_dict.keys()]
        self._ax_.set_xticklabels(x_tick_labels)
        if len(df) > 0:
            if not df.equals(self.last_df):
                self.last_df = df
                max_x = int(max(self.freq_definitions_dict.keys()))
                min_x = int(min(self.freq_definitions_dict.keys()))
                df = df.loc[(df["wifi_scanned_info_freq"]>=min_x) & (df["wifi_scanned_info_freq"]<=max_x)]
                for index, row in df.iterrows():
                    freq_list = []
                    level_list = []
                    freq = row.wifi_scanned_info_freq
                    level = row.wifi_scanned_info_level
                    name = row.wifi_scanned_info_ssid
                    width = self.freq_definitions_dict[str(freq)]["width"] / 2
                    freq_list.append(freq-width)
                    freq_list.append(freq)
                    freq_list.append(freq+width)
                    level_list.append(-100)
                    level_list.append(level)
                    level_list.append(-100)
                    self._x_ = np.linspace(freq_list[0], freq_list[-1], 100)
                    self._y_ = interpolate.pchip_interpolate(freq_list, level_list, self._x_)
                    line = self._ax_.plot(self._x_, self._y_)
                    kwargs['color'] = line[0].get_color()
                    kwargs['ha'] = 'center'
                    kwargs['va'] = 'bottom'
                    self._ax_.text(freq_list[1], level_list[1], name, kwargs)
                self.canvas.draw()
