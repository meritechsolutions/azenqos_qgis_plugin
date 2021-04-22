import os
import shutil
import sqlite3
import pandas as pd
import params_disp_df
import linechart_query
import integration_test_helpers
import numpy as np


def test():
    azmfp = "../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = linechart_query.get_lte_data_df(dbcon)
        print("df.head():\n %s" % df[0].head(20))


if __name__ == "__main__":
    test()
