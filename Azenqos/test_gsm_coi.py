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
    azmfp = "../example_logs/gsm_log/868263034952973-31_08_2020-18_08_49.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)
    
    with sqlite3.connect(dbfp) as dbcon:
        df = gsm_query.get_coi_df(dbcon, "2020-08-31 18:04:13.538")
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[1,1] == 31
        assert len(df) == 35
        assert len(df.columns) == 3

        

if __name__ == "__main__":
    test()
