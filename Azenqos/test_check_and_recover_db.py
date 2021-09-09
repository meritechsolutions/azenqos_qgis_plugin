import azq_utils
import os
import uuid


def test():
    dbfp = "../example_logs/test_check_and_recover_db/adb_log_snapshot_e6acfe45-d512-4054-95bb-0b67686321c1.db"
    tmp_path = os.path.join(azq_utils.get_module_path(), "tmp_gen", "test_check_and_recover_db")
    check_db_exist = False
    if os.path.isfile(dbfp):
        check_db_exist = True

    if check_db_exist:
        if not os.path.isdir(tmp_path):
            os.makedirs(tmp_path)
        dump_dbfp = azq_utils.check_and_recover_db(dbfp, tmp_path, "test")
        print(dump_dbfp)
        assert dump_dbfp != dbfp


if __name__ == "__main__":
    test()
