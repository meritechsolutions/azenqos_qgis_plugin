import integration_test_helpers
import db_preprocess
import pandas as pd
import sqlite3

pd.set_option("display.max_rows", 10)
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1000)


def test():
    azmfp = "../example_logs/server_merged_log/server_db.zip"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        db_preprocess.prepare_spatialite_views(dbcon)

        df = pd.read_sql("select * from lte_inst_rsrp_1", dbcon)
        assert "geom" in df.columns
        print("len df rsrp:", len(df))

        df = pd.read_sql("select * from layer_styles", dbcon)
        print("df.head() %s" % df)


if __name__ == "__main__":
    test()
