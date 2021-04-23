import sqlite3

import integration_test_helpers
import nr_query


def test():
    azmfp = "../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = nr_query.get_nr_radio_params_disp_df(dbcon, "2020-08-18 13:48:02.356")
        print("df.head():\n %s" % df.head(20))
        assert df.iloc[2, 1] == 41
        assert len(df) == 16
        assert len(df.columns) == 9


if __name__ == "__main__":
    test()
