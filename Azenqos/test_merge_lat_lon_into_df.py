import sqlite3

import pandas as pd

import integration_test_helpers
import preprocess_azm


def test():
    azmfp = "../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        df = pd.read_sql(
            "select log_hash, time, positioning_lat as real_lat, positioning_lon as readl_lon from location",
            dbcon,
        )
        print("df.head():\n %s" % df.head(20))
        df_merged = preprocess_azm.merge_lat_lon_into_df(dbcon, df)
        print(
            "df_merged.head():\n %s"
            % df_merged[["positioning_lat", "real_lat"]].head(20)
        )


if __name__ == "__main__":
    test()
