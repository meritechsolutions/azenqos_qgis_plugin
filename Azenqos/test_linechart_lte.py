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


def test():
    azmfp = "../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = linechart_query.get_lte_df(dbcon)
        print("df.head():\n %s" % df.head(20))
        
        df_by_time = linechart_query.get_lte_df_by_time(dbcon,"2020-08-26 15:42:30.687")
        # print("df.head():\n %s" % df_by_time.head(20))
        # print(type(df["lte_sinr_rx0_1"].astype(float).to_list())

        # df_data = linechart_query.get_lte_data_df(dbcon, "2020-08-26 15:55:17.284")
        # print("df.head():\n %s" % df_data.head(20))
        # np.testing.assert_almost_equal(df.iloc[1, 1], 72.50, 2)
        # assert len(df) == 9
        # assert len(df.columns) == 5

        app = QtWidgets.QApplication(sys.argv)
        main = linechart.Linechart()
        main.plot(df)
        main.updateTime(df_by_time, datetime.datetime.strptime("2020-08-26 16:16:30.687", '%Y-%m-%d %H:%M:%S.%f'))
        def updateTime(epoch):
            print(epoch)
            sampledate = datetime.datetime.fromtimestamp(epoch,tz=datetime.timezone.utc)
            print(sampledate)
            df_by_time = linechart_query.get_lte_df_by_time(dbcon, sampledate)
            main.updateTime(df_by_time, sampledate)

        main.timeSelected.connect(updateTime)
        main.show()
        sys.exit(app.exec_())


if __name__ == "__main__":
    test()
