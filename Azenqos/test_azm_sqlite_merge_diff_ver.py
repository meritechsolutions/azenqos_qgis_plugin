import sqlite3
import os
import contextlib

import pandas as pd
import azm_sqlite_merge


def test():
    azm_list = [
        "../example_logs/debug_merge_fail/866407030949242-26_08_2021-17_47_15.azm",
        "../example_logs/debug_merge_fail/869796041564553-31_08_2021-15_47_03.azm",
    ]
    for azm in azm_list:
        if not os.path.isfile(azm):
            print("file not found: {} - abort test".format(azm))
            return

    out_dbfp = azm_sqlite_merge.merge(azm_list)
    assert os.path.isfile(out_dbfp)
    with contextlib.closing(sqlite3.connect(out_dbfp)) as dbcon:
        df = pd.read_sql("select count(distinct(log_hash)) from logs union select count(distinct(log_hash)) from signalling union select count(distinct(log_hash)) from events", dbcon);
        assert (df.iloc[:, 0] == len(azm_list)).all()  # all rows of first col equal n logs: having distinct log_hashes per log merged in successfully
    

if __name__ == "__main__":
    test()
