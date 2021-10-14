from PyQt5.QtWidgets import QApplication
import contextlib
import sys
import os
import azq_server_api
import db_preprocess
import pandas as pd
import sqlite3
import integration_test_helpers
import azq_utils
import datetime


def _test(server, user, passwd, lhl):
    return # restructuring on server
    app = QApplication([])
    print("app: ", app)  # use it so pyflakes wont complain - we need a ref to qapplicaiton otherwise we'll get segfault
    print("server", server)
    print("user", user)
    print("passwd", passwd)
    overview_db_list = azq_server_api.api_overview_db_list(server, azq_server_api.api_login_get_token(server, user, passwd))
    print("overview_db_list:", overview_db_list)
    assert overview_db_list
    gv = integration_test_helpers.get_global_vars()

    ################# api func test
    target_fp = azq_utils.tmp_gen_fp("o.zip")
    if os.path.isfile(target_fp):
        os.remove(target_fp)
    assert not os.path.isfile(target_fp)
    ret = azq_server_api.api_overview_db_download(gv.login_dialog.server, gv.login_dialog.token, target_fp, overview_mode_params_dict={"y": 2021, "m": 9, "bin": 60})
    print("ret:", ret)
    assert os.path.isfile(ret)
    assert os.path.isfile(target_fp)
    azmfp = ret
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        db_preprocess.prepare_spatialite_views(dbcon)
        df = pd.read_sql("select * from lte_inst_rsrp_1", dbcon)
        assert "geom" in df.columns
        print("len df rsrp:", len(df))
        df = pd.read_sql("select * from layer_styles", dbcon)
        print("df.head() %s" % df)

    ############# widget func test
    # test ui download and prepare db func
    import server_overview_widget
    sow = server_overview_widget.server_overview_widget(None, gv)
    sow.config = {"start_date": datetime.date(2021, 8, 30), "end_date": datetime.date(2021, 9, 30), "bin": 60}
    ret = sow.apply_worker_func()
    assert ret == 0




if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("argc too short so using defaults")
        # 474974357483649200 is log_hash for ../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm
        # 345757788188057704 is log_hash for ../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm
        _test(
            server="https://test0.azenqos.com",
            user="trial_admin",
            passwd="3.14isnotpina",
            lhl="",
        )
    else:
        _test(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
