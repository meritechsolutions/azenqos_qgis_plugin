import sqlite3

import numpy as np

import integration_test_helpers
import wcdma_query


def test():
    azmfp = (
        "../example_logs/wcdma_log/357008080503008-02_09_2020-12_25_26 (wcdma log).azm"
    )
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = wcdma_query.get_wcdma_radio_params_disp_df(
            dbcon, "2020-09-02 12:15:29.547"
        )
        print("df.head():\n %s" % df.head(20))
        np.testing.assert_almost_equal(df.iloc[1, 1], -21.29, 2)
        assert len(df) == 10
        assert len(df.columns) == 2


if __name__ == "__main__":
    test()
