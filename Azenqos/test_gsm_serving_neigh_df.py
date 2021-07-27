import sqlite3
import contextlib

import gsm_query
import integration_test_helpers


def test():
    azmfp = "../example_logs/gsm_log/357008080503008-02_09_2020-13_21_59 (GSM log).azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        df = gsm_query.get_gsm_serv_and_neigh__df(dbcon, "2020-09-02 12:27:26.333")
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[1, 4] == 710
        assert len(df) == 33
        assert len(df.columns) == 10


if __name__ == "__main__":
    test()
