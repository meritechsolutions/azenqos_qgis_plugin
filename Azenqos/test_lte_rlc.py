import zipfile
import os
import shutil
import sqlite3
import pandas as pd
import params_disp_df
import lte_query
import integration_test_helpers
import numpy as np


def test():
    azmfp = "../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = lte_query.get_lte_rlc_disp_df(dbcon, "2020-08-26 15:55:17.284")
        print("df.head():\n %s" % df.head(20))
        np.testing.assert_almost_equal(df.iloc[1, 1], 72.50, 2)
        assert len(df) == 9
        assert len(df.columns) == 5


if __name__ == "__main__":
    test()
