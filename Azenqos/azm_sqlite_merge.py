import shutil
import sqlite3
import subprocess

import pandas as pd

import preprocess_azm
import azq_utils
import uuid
import os
import contextlib


def merge(in_azm_list):
    out_tmp_dir = os.path.join(azq_utils.tmp_gen_path(), "tmp_combine_db_result_{}".format(uuid.uuid4()))
    os.makedirs(out_tmp_dir)
    assert os.path.isdir(out_tmp_dir)
    out_db_fp = os.path.join(out_tmp_dir, "azqdata.db")
    assert not os.path.isfile(out_db_fp)
    assert not os.path.exists(out_db_fp)
    sqlite_bin = os.path.join(
        azq_utils.get_module_path(),
        os.path.join(
            "sqlite_" + os.name,
            "sqlite3" + ("" if os.name == "posix" else ".exe"),
        ),
    )
    assert os.path.isfile(sqlite_bin)
    combine_uuid = uuid.uuid4()

    with contextlib.closing(sqlite3.connect(out_db_fp)) as out_dbcon:
        tmp_dirs = []
        dbfps = []
        n = len(in_azm_list)

        # extract dbs of all azms to their own temp dirs
        for i in range(n):
            is_last_azm = i == n-1
            tmp_dir = os.path.join(azq_utils.tmp_gen_path(), "tmp_combine_{}_azm_{}".format(combine_uuid, i))
            os.makedirs(tmp_dir)
            assert os.path.isdir(tmp_dir)
            azm = in_azm_list[i]
            print("=== extracting db from azm: "+azm+" [{}/{}] ===".format(i, n))
            new_dbfp = os.path.join(tmp_dir, "azqdata.db")
            assert not os.path.isfile(new_dbfp)
            if azm.endswith(".azm") or azm.endswith(".zip"):
                preprocess_azm.extract_entry_from_zip(azm, "azqdata.db", tmp_dir)
            elif azm.endswith(".db"):
                shutil.copy(azm, new_dbfp)
            else:
                raise Exception("unsupported merge file extension: {}".format(azm))
            tmp_dirs.append(tmp_dir)
            assert os.path.isfile(new_dbfp)
            dbfps.append(new_dbfp)

        # get azm app versions of each
        azm_vers = map(preprocess_azm.get_azm_apk_ver_for_dbfp, dbfps)

        # sort azm apk vers, newest should be merged first as they might have more columns in same tables than older vers
        azm_df = pd.DataFrame({"azm": in_azm_list, "dbfp": dbfps, "azm_ver": azm_vers})
        assert azm_df["azm_ver"].dtype == int
        azm_df.sort_values("azm_ver", ascending=False, inplace=True)
        azm_df = azm_df.reset_index(drop=True)
        print("azm_df:\n", azm_df)

        # dump then import data of each db into target sqlite db
        for index, row in azm_df.iterrows():
            print("=== dumping db to merged azm [{}/{}] ===".format(index+1, len(azm_df)))
            is_last_azm = index == azm_df.index[-1]
            dbfp = row.dbfp
            assert os.path.isfile(dbfp)
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                cmd = [sqlite_bin, dbfp, ".dump"]
                print("dumping db file to ram:", dbfp, "cmd:", cmd)
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

        # commit new db conn
        out_dbcon.commit()

    # test merged dbfp
    with contextlib.closing(sqlite3.connect(out_db_fp)) as dbcon:
        df = pd.read_sql(
            "select count(distinct(log_hash)) from logs",
            dbcon
        );
        assert df.iloc[0, 0] == len(in_azm_list)

    return out_db_fp




    
