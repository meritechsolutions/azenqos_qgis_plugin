import sqlite3
import preprocess_azm
import azq_utils
import uuid
import os
import contextlib


def merge(in_azm_list, out_db_fp):
    tmp_dirs = []
    i = -1
    n = len(in_azm_list)
    combine_uuid = uuid.uuid4()
    with contextlib.closing(sqlite3.connect(out_db_fp)) as out_dbcon:
        for i in range(n):
            tmp_dir = os.path.join(azq_utils.tmp_gen_path(), "tmp_combine_{}_azm_{}".format(combine_uuid, i))
            os.makedirs(tmp_dir)
            assert os.path.isdir(tmp_dir)
            azm = in_azm_list[i]
            print("=== merging data from azm: "+azm+" [{}/{}] ===".format(i, n))
            preprocess_azm.extract_entry_from_zip(azm, "azqdata.db", tmp_dir)
            tmp_dirs.append(tmp_dir)

            dbfp = os.path.join(tmp_dir, "azqdata.db")
            assert os.path.isfile(dbfp)
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                print("dumping db file:", dbfp)
                sql_lines = []
                for sql_line in dbcon.iterdump():
                    sql_line = sql_line.replace("CREATE TABLE android_metadata (locale TEXT);", "", 1)
                    sql_line = sql_line.replace('CREATE TABLE "', 'CREATE TABLE IF NOT EXISTS "', 1)
                    sql_lines.append(sql_line)
                assert sql_lines
                sql_script = "\n".join(sql_lines)
                assert sql_script
                print("merginng to target db file:", out_db_fp)
                out_dbcon.executescript(sql_script)
        out_dbcon.commit()





    
