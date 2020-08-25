import integration_test_helpers
import db_preprocess
import pandas as pd
import sqlite3
pd.set_option('display.max_rows', 10)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width', 1000)


def test():
    azmfp = "example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    
    with sqlite3.connect(dbfp) as dbcon:
        db_preprocess.prepare_spatialite_views(dbcon)

        df = pd.read_sql("select * from lte_inst_rsrp_1", dbcon)
        assert "geom" in df.columns
        print("len df rsrp:", len(df))
        assert len(df) == 589
        
        df = pd.read_sql('select * from layer_styles', dbcon)
        print("df.head() %s" % df)
        assert len(df[df.f_table_name == 'nr_cqi']) == 1
        assert df.f_table_catalog.notnull().all()  # required for qgis to apply theme autmomatically by default
        assert df.f_table_schema.notnull().all()  # required for qgis to apply theme autmomatically by default
        assert df.styleqml.notnull().all()
        
        

if __name__ == "__main__":
    test()
