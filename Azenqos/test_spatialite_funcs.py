import integration_test_helpers
import spatialite as sqlite
import pandas as pd


def test():
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp("../example_logs/4g_cellfile_bad_gps/354569110523269 30_7_2021 14.52.10.azm")
    cell_files = ["../example_logs/4g_cellfile_bad_gps/4G_cellfile_test_demo.txt"]

    with sqlite.connect(dbfp) as dbcon:
        df = pd.read_sql("select st_x(geom) as lon, st_y(geom) as lat from lte_cell_meas where geom is not null", dbcon)
        print("df.head():\n", df.head())
        assert abs(df.lat.iloc[0] - 13.669310) < 0.000001
        assert abs(df.lon.iloc[0] - 100.709609) < 0.000001
        assert df.lat.notnull().all()
        assert df.lon.notnull().all()


if __name__ == "__main__":
    test()
