import sqlite3
import os
import contextlib

import pandas as pd
import azm_sqlite_merge


def test():
    azm_list = [
        "../example_logs/nr_sa_exynos_s21_ex0/350299943614770-20_08_2021-15_55_05 (airplane then speedtest).azm",
        "../example_logs/nr_sa_exynos_s21_ex0/350299943614770-24_08_2021-16_13_20 (speedtest then airplane ramkomut).azm",
        "../example_logs/nr_nsa_exynos_s21/354505623113016-19_08_2021-16_45_22.azm"
    ]
    out_dbfp = azm_sqlite_merge.merge(azm_list)
    assert os.path.isfile(out_dbfp)
    with contextlib.closing(sqlite3.connect(out_dbfp)) as dbcon:
        n_lh = pd.read_sql("select count(distinct(log_hash)) from logs", dbcon).iloc[0, 0];
        print("n_lh:", n_lh)
        assert n_lh == len(azm_list)
    

if __name__ == "__main__":
    test()
