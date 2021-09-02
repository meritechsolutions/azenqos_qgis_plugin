import sqlite3
import os

import pandas as pd

import db_preprocess
import integration_test_helpers

pd.set_option("display.max_rows", 10)
pd.set_option("display.max_columns", 10)
pd.set_option("display.width", 1000)


def test():
    azmfp = "../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    alt_azmfp = "../example_logs/tmp_mos/ex_processed_mos.azm"

    alt_mos_azm = False
    if os.path.isfile(alt_azmfp):
        azmfp = alt_azmfp
        alt_mos_azm = True



    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with sqlite3.connect(dbfp) as dbcon:
        assert "lte_cell_meas" in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values
        assert "lte_inst_rsrp_1" not in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values
        db_preprocess.prepare_spatialite_views(dbcon)

        df = pd.read_sql("select * from lte_inst_rsrp_1", dbcon)
        assert "geom" in df.columns
        print("len df rsrp:", len(df))

        if not alt_mos_azm:
            assert len(df) == 589
        else:
            df = pd.read_sql("select * from polqa_mos_1", dbcon)
            print("len df polqa_mos:", len(df))
            assert "geom" in df.columns

        df = pd.read_sql("select * from layer_styles", dbcon)
        print("df.head() %s" % df)

        assert (
            df.f_table_catalog.notnull().all()
        )  # required for qgis to apply theme autmomatically by default
        assert (
            df.f_table_schema.notnull().all()
        )  # required for qgis to apply theme autmomatically by default
        assert df.styleqml.notnull().all()

        assert "lte_inst_rsrp_1" in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values
        assert "lte_cell_meas" not in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values

        ls = pd.read_sql("select styleqml from layer_styles where f_table_name = 'lte_inst_rsrp_1'", dbcon).iloc[0,0]
        print("rsrp ls:", ls)
        assert '''<range symbol="7" label="-80 to 0 (4224: 44.15%)" render="true" lower="-80" upper="0" includeLower="true" includeUpper="false" />
<range symbol="6" label="-90 to -80 (2378: 24.86%)" render="true" lower="-90" upper="-80" includeLower="true" includeUpper="false" />''' in ls






if __name__ == "__main__":
    test()
