import sqlite3
import integration_test_helpers
import lte_query


def test():
    azmfp = "../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = lte_query.get_lte_serv_and_neigh_disp_df(dbcon, "2020-08-26 15:42:29.132")
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[1, 1] == 1450
        assert len(df) == 13
        assert len(df.columns) == 7


if __name__ == "__main__":
    test()
