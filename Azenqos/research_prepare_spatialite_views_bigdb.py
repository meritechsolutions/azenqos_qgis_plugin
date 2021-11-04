import sqlite3
import contextlib
import db_preprocess
import shutil
import os
import azq_utils
import datetime
import db_layer_task
import analyzer_vars


def test():
    ori_dbfp = "/data/overview_db_optimize/o_ori.db"
    dbfp = "research_prepare_views.db"
    gvars = analyzer_vars.analyzer_vars()
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

        print("cre layers START")
        azq_utils.timer_start("prepare_layers")
        ret = db_layer_task.create_layers(
            gvars, dbfp, display_name_prefix="overview_", gen_theme_bucket_counts=False)
        print("cre layers DONE")
        table_to_layer_dict, layer_id_to_visible_flag_dict, last_visible_layer = ret
        azq_utils.timer_print("prepare_layers")

if __name__ == "__main__":
    test()
