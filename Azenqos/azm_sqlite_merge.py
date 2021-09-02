import sqlite3
import subprocess

import preprocess_azm
import azq_utils
import uuid
import os
import contextlib


def merge(in_azm_list, out_db_fp):
    if os.path.isfile(out_db_fp):
        os.remove(out_db_fp)
    assert not os.path.exists(out_db_fp)
    tmp_dirs = []
    i = -1
    n = len(in_azm_list)
    sqlite_bin = os.path.join(
        azq_utils.get_module_path(),
        os.path.join(
            "sqlite_" + os.name,
            "sqlite3" + ("" if os.name == "posix" else ".exe"),
        ),
    )
    assert os.path.isfile(sqlite_bin)
    combine_uuid = uuid.uuid4()
    is_last_azm = False
    with contextlib.closing(sqlite3.connect(out_db_fp)) as out_dbcon:
        for i in range(n):
            is_last_azm = i == n-1
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
                cmd = [sqlite_bin, dbfp, ".dump"]
                print("dumping db file:", dbfp, "cmd:", cmd)
                sql_script = subprocess.check_output(cmd, encoding="utf-8")
                sql_script = sql_script.replace('CREATE TABLE IF NOT EXISTS ', 'CREATE TABLE ')
                sql_script = sql_script.replace('CREATE TABLE ','CREATE TABLE IF NOT EXISTS ')
                sql_script +=" delete from spatial_ref_sys;\n"
                if is_last_azm:
                    sql_script += "INSERT INTO spatial_ref_sys VALUES(4326,'epsg',4326,'WGS 84','+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs');\n"
                assert sql_script
                with open("out.sql", "w") as f:
                    f.write(sql_script)
                #print("sql_script:", sql_script)
                print("merginng to target db file:", out_db_fp)
                out_dbcon.executescript(sql_script)
        out_dbcon.commit()





    
