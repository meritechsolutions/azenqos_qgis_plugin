import zipfile
import os
import shutil
import params_disp_df
import sqlite3
import pandas as pd
import lte_query
import integration_test_helpers


def test():
    azmfp = "example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)
    
    with sqlite3.connect(dbfp) as dbcon:
        df = lte_query.get_lte_serv_and_neigh_disp_df(dbcon, "2020-08-18 13:47:42.382")
        print("df.head():\n %s" % df.head(20))
        

if __name__ == "__main__":
    test()
