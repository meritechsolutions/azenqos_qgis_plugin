import integration_test_helpers
import db_preprocess
import pandas as pd
import sqlite3


def test():
    azmfp = "example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    
    with sqlite3.connect(dbfp) as dbcon:
        db_preprocess.prepare_spatialite_views(dbcon)
        

if __name__ == "__main__":
    test()
