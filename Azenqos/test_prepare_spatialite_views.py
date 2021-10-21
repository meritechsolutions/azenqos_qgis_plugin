import sqlite3
import os

import pandas as pd

import db_preprocess
import integration_test_helpers
import contextlib
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

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        assert "lte_cell_meas" in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values
        assert "lte_inst_rsrp_1" not in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values
        db_preprocess.prepare_spatialite_views(dbcon)

        df = pd.read_sql("select * from lte_inst_rsrp_1", dbcon)
        assert "geom" in df.columns
        print("len df rsrp:", len(df))

        if not alt_mos_azm:
            pass
            # assert len(df) == 589
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

        assert "lte_inst_rsrp_1" in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values
        assert "lte_cell_meas" not in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values

        ls = pd.read_sql("select styleqml from layer_styles where f_table_name = 'lte_inst_rsrp_1'", dbcon).iloc[0,0]
        print("rsrp ls:", ls)

        # test gen theme range case
        param_table_view = "lte_inst_rsrp_1"
        qml_fp = db_preprocess.gen_style_qml_for_theme(
            None, param_table_view, None, param_table_view,
            dbcon,
            to_tmp_file=True
        )
        assert qml_fp is not None
        assert os.path.isfile(qml_fp)

        # test gen theme match_val case
        param_table_view = "lte_physical_cell_id_1"
        qml_fp = db_preprocess.gen_style_qml_for_theme(
            None, param_table_view, None, param_table_view,
            dbcon,
            to_tmp_file=True
        )
        assert qml_fp is not None
        assert os.path.isfile(qml_fp)







if __name__ == "__main__":
    test()
