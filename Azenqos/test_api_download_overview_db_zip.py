import contextlib
import glob
import os
import sqlite3
import sys
import zipfile

import pandas as pd
from PyQt5.QtWidgets import QApplication

import azm_sqlite_merge
import azq_server_api
import azq_utils
import integration_test_helpers


def _test(server, user, passwd, lhl):
    app = QApplication([])
    print("app: ", app)  # use it so pyflakes wont complain - we need a ref to qapplicaiton otherwise we'll get segfault
    print("server", server)
    print("user", user)
    print("passwd", passwd)
    overview_db_list_df = azq_server_api.api_overview_db_list_df(server, azq_server_api.api_login_get_token(server, user, passwd))
    print("overview_db_list_df:", overview_db_list_df.head(10))
    assert len(overview_db_list_df)
    gv = integration_test_helpers.get_global_vars()

    ################# api func test
    req_body = {
    "start_date": "2021-8-03",
    "end_date": "2021-10-15",
    "bin": 60,
    "filters_dict": {},
    }
    target_fp = azq_utils.tmp_gen_fp("o.zip")
    if os.path.isfile(target_fp):
        os.remove(target_fp)
    assert not os.path.isfile(target_fp)
    ret = azq_server_api.api_overview_db_download(
        gv.login_dialog.server,
        gv.login_dialog.token,
        target_fp,
        req_body
    )
    print("ret:", ret)
    assert os.path.isfile(ret)
    assert os.path.isfile(target_fp)
    multi_db_zip_fp = ret

    tmpdir = azq_utils.tmp_gen_new_subdir()
    with zipfile.ZipFile(multi_db_zip_fp, "r") as zip_file:
        zip_file.extractall(tmpdir)

    db_files = glob.glob(os.path.join(tmpdir, "*.db"))
    assert len(db_files)

    # combined all the db_files in the zip
    dbfp = azm_sqlite_merge.merge(db_files)

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        df = pd.read_sql("select * from lte_cell_meas", dbcon)
        assert "geom" in df.columns
        print("len df rsrp:", len(df))

    print("SUCCESS")


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
