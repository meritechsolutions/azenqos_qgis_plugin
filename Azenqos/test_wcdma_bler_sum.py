import zipfile
import os
import shutil
import params_disp_df
import sqlite3
import pandas as pd
import wcdma_query
import integration_test_helpers
import numpy as np


def test():
    azmfp = (
        "../example_logs/wcdma_log/357008080503008-02_09_2020-12_25_26 (wcdma log).azm"
    )
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = wcdma_query.get_bler_sum_disp_df(dbcon, "2020-09-02 12:17:08.567")
        print("df.head():\n %s" % df.head(20))
        np.testing.assert_almost_equal(df.iloc[1, 1], 0.0, 2)
        assert len(df) == 4
        assert len(df.columns) == 2


if __name__ == "__main__":
    test()
