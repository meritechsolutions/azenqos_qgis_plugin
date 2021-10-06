import sqlite3
import contextlib
import integration_test_helpers
import lte_query
import pandas as pd
import numpy as np


def test():
    azmfp = "../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        lh = pd.read_sql_query("select log_hash from logs", dbcon).log_hash.astype(np.int64).iloc[0]
        df = lte_query.get_lte_serv_and_neigh_disp_df(dbcon, "2020-08-26 15:42:29.132")
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[1+1, 1] == 1450
        assert df.iloc[5+1, 1] == 1450
        assert len(df) == 13+1
        assert len(df.columns) == 6

        df = lte_query.get_lte_serv_and_neigh_disp_df(dbcon, {'log_hash':lh, 'time':"2020-08-26 15:42:29.132"})
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[1+1, 1] == 1450
        assert df.iloc[5+1, 1] == 1450
        assert len(df) == 13+1
        assert len(df.columns) == 6


if __name__ == "__main__":
    test()
