import os
import sqlite3
import pandas as pd
import azq_utils


def test():
    dbfp = "../example_logs/test_check_and_recover_db/adb_log_snapshot_e6acfe45-d512-4054-95bb-0b67686321c1.db"
    tmp_path = os.path.join(azq_utils.get_module_path(), "tmp_gen", "test_check_and_recover_db")
    check_db_exist = False
    if os.path.isfile(dbfp):
        check_db_exist = True

    if check_db_exist:
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)
        dump_dbfp = azq_utils.check_and_recover_db(dbfp, tmp_path)
        assert dump_dbfp != dbfp
        with sqlite3.connect(dump_dbfp) as dbcon:
            df = pd.read_sql("select distinct(log_hash) from signalling", dbcon)
            assert len(df) == 1



if __name__ == "__main__":
    test()
