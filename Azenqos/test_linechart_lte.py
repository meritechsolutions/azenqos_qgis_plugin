import zipfile
import os
import shutil
import sqlite3
from PyQt5 import QtWidgets, uic
from PyQt5.uic import loadUi
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import sys
import pandas as pd
import params_disp_df
import linechart_query
import linechart
import integration_test_helpers
import numpy as np
import datetime
import analyzer_vars

def test():
    azmfp = "../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)
    gc = analyzer_vars.analyzer_vars()
    gc.databasePath = dbfp

    app = QtWidgets.QApplication(sys.argv)
    main = linechart.Linechart(gc)
    def createChartFunc(dbcon):
        return linechart_query.get_lte_df(dbcon)
    def updateFunc(dbcon, time):
        return linechart_query.get_lte_df_by_time(dbcon, time)
    main.createChartFunc = createChartFunc
    main.updateFunc = updateFunc
    # main.updateTime(df_by_time, datetime.datetime.strptime("2020-08-26 16:16:30.687", '%Y-%m-%d %H:%M:%S.%f'))
    def updateTime(epoch):
        # print(epoch)
        time = datetime.datetime.fromtimestamp(epoch)
        # print(sampledate)
        # df_by_time = linechart_query.get_lte_df_by_time(dbcon, sampledate)
        main.updateTime(time)
    main.timeSelected.connect(updateTime)
    main.updateTime(datetime.datetime.strptime("2020-08-26 16:16:30.687", '%Y-%m-%d %H:%M:%S.%f'))
    main.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    test()
