import zipfile
import os
import shutil
import params_disp_df
import sqlite3
import pandas as pd
import gsm_query
import integration_test_helpers
import numpy as np


def test():
    azmfp = "../example_logs/gsm_log/357008080503008-02_09_2020-13_21_59 (GSM log).azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = gsm_query.get_gsm_current_channel_disp_df(dbcon, "2020-09-02 12:27:26.333")
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[13, 1] == 691
        assert len(df) == 16
        assert len(df.columns) == 2


if __name__ == "__main__":
    test()
