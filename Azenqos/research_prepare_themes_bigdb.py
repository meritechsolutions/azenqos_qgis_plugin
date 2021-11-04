import sqlite3
import contextlib
import db_preprocess
import shutil
import os
import azq_utils
import datetime

def test():
    ori_dbfp = "/data/overview_db_optimize/o_ori.db"
    dbfp = "research_prepare_views.db"
    if os.path.isfile(dbfp):
        os.remove(dbfp)
    print("copy ori db to tmp")
    assert 0 == os.system("cat {} > {}".format(ori_dbfp, dbfp))
    assert os.path.isfile(dbfp)
    print("open dbcon")
    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        assert "lte_inst_rsrp_1" not in db_preprocess.get_geom_cols_df(dbcon).f_table_name.values
        print("call func START")
        azq_utils.timer_start("prepare_spatialite_views")
        db_preprocess.prepare_spatialite_views(dbcon, cre_table=False, start_date=datetime.datetime(2021, 1, 1), end_date=datetime.datetime(2021, 6, 1))
        print("call func DONE")
        azq_utils.timer_print("prepare_spatialite_views")

if __name__ == "__main__":
    test()
