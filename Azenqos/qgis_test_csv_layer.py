import integration_test_helpers
import azq_utils
import pandas as pd
import os
import sqlite3
import contextlib

azmfp = os.path.join(
    azq_utils.get_module_path(),
    "../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm",
)
dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
    df = pd.read_sql(
        "select log_hash, time, positioning_lat, positioning_lon from location", dbcon
    )
    csv_fp = os.path.join(azq_utils.tmp_gen_path(), "test_df.csv")
    df.to_csv(csv_fp, index=False)
    import qgis_layers_gen

    qgis_layers_gen.create_qgis_layer_csv(
        csv_fp, x_field="positioning_lon", y_field="positioning_lat"
    )
