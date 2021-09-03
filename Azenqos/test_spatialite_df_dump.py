import contextlib

import integration_test_helpers
import azq_utils
import pandas as pd
import os
import sqlite3
import preprocess_azm


def test():
    azmfp = os.path.join(
        azq_utils.get_module_path(),
        "../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm",
    )
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        df = pd.read_sql("select log_hash, time from location", dbcon)
        df = preprocess_azm.merge_lat_lon_into_df(dbcon, df).rename(
        columns={"positioning_lat": "lat", "positioning_lon": "lon"}
        )
    import qgis_layers_gen
    qgis_layers_gen.dump_df_to_spatialite_db(df, dbfp, "gen_loc")


if __name__ == "__main__":
    test()