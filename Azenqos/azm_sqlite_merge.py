import contextlib
import multiprocessing as mp
import os
import shutil
import sqlite3
import sys
import traceback
import uuid
from multiprocessing.pool import ThreadPool

import numpy as np
import pandas as pd

import azq_utils
import preprocess_azm


def merge(in_azm_list, n_proc=3, progress_update_signal=None):
    out_tmp_dir = os.path.join(azq_utils.tmp_gen_path(), "tmp_combine_db_result_{}".format(uuid.uuid4()))
    os.makedirs(out_tmp_dir)
    assert os.path.isdir(out_tmp_dir)
    out_db_fp = os.path.join(out_tmp_dir, "azqdata.db")
    assert not os.path.isfile(out_db_fp)
    assert not os.path.exists(out_db_fp)
    sqlite_bin = azq_utils.get_sqlite_bin()
    assert os.path.isfile(sqlite_bin)
    combine_uuid = uuid.uuid4()

    with contextlib.closing(sqlite3.connect(out_db_fp)) as out_dbcon:
        tmp_dirs = []
        dbfps = []
        n = len(in_azm_list)
        extract_progress = 15 / n

        # extract dbs of all azms to their own temp dirs
        for i in range(n):
            if progress_update_signal is not None:
                progress_update_signal.emit(extract_progress*(i+1))
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
                with contextlib.closing(sqlite3.connect(new_dbfp)) as dbcon:
                    log_hash = pd.read_sql("SELECT log_hash FROM logs LIMIT 1;",dbcon).log_hash[0]
                    out_tmp_each_log_dir = os.path.join(azq_utils.tmp_gen_path(), str(log_hash))
                    preprocess_azm.extract_all_from_zip(azm, out_tmp_each_log_dir)
                    tables = []
                    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' and name NOT LIKE 'sqlite_%' and name LIKE 'pp%';", dbcon).name.tolist()
                    tables.append("polqa_mos")
                    for table in tables:
                        check_len_table = len(pd.read_sql("SELECT * FROM {};".format(table),dbcon))
                        if check_len_table == 0:
                            dbcon.executescript("DROP TABLE {};".format(table))
                    dbcon.commit()

            elif azm.endswith(".db"):
                shutil.copy(azm, new_dbfp)
            else:
                raise Exception("unsupported merge file extension: {}".format(azm))
            tmp_dirs.append(tmp_dir)
            assert os.path.isfile(new_dbfp)
            dbfps.append(new_dbfp)

        # get azm app versions of each
        azm_vers = None
        try:
            azm_vers = list(map(preprocess_azm.get_azm_apk_ver_for_dbfp, dbfps))
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: get azm_vers exception (normal for server overview db):", exstr)

        # sort azm apk vers, newest should be merged first as they might have more columns in same tables than older vers
        azm_df = pd.DataFrame({"azm": in_azm_list, "dbfp": dbfps, "azm_ver": azm_vers})
        if azm_vers is not None:
            assert azm_df["azm_ver"].dtype == np.int64 or azm_df["azm_ver"].dtype == int
        azm_df.sort_values("azm_ver", ascending=False, inplace=True)
        azm_df = azm_df.reset_index(drop=True)
        print("azm_df:\n", azm_df)
        n_azm_vers = len(azm_df.azm_ver.unique())
        check_col_diff = n_azm_vers > 1
        print("n_azm_vers:", n_azm_vers)
        print("check_col_diff:", check_col_diff)
        if progress_update_signal is not None:
            progress_update_signal.emit(20)

        sql_scripts = None

        # dump then import data of each db into target sqlite db
        pool = mp.Pool(n_proc) if os.name == "posix" else ThreadPool(n_proc)  # windows qgis if mp it will open multiple instances of qgis
        print("=== dumping all sqlite logs concurrently...")
        azq_utils.timer_start("perf_dump_threaded")
        try:
            sql_scripts = pool.map(get_sql_script, azm_df.dbfp.values.tolist())
        finally:
            pool.close()
        azq_utils.timer_print("perf_dump_threaded")
        print("=== dumping all sqlite logs concurrently... done")
        merge_progress = 30 / len(azm_df)

        first_azm_table_to_cols_dict = {}
        for index, row in azm_df.iterrows():
            if progress_update_signal is not None:

                progress_update_signal.emit(merge_progress*(index+1)+20)
            print("=== dumping db to merged azm [{}/{}] ===".format(index+1, len(azm_df)))
            is_first_azm = index == azm_df.index[0]
            is_last_azm = index == azm_df.index[-1]
            dbfp = row.dbfp
            assert os.path.isfile(dbfp)
            sql_script = sql_scripts[index]
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                # iterdump somehow doesnt work in my system with these dbs, doing dump with sqlite3 cmd shell binaries instead
                if is_last_azm:
                    sql_script += "INSERT INTO spatial_ref_sys VALUES(4326,'epsg',4326,'WGS 84','+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs');\n"
                assert sql_script

                if check_col_diff:
                    print("... checking for schema/column differences need to specify columns in INSERT of dump")
                    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table' and name NOT LIKE 'sqlite_%';",
                                         dbcon).name
                    for table in tables:
                        cols = list(pd.read_sql("select * from {} where false".format(table), dbcon).columns)  # use list as we will compare this list next
                        if is_first_azm:
                            first_azm_table_to_cols_dict[table] = cols
                        else:
                            if table not in first_azm_table_to_cols_dict.keys():
                                print("table: {} not in first azm - no need adjust".format(table))
                                first_azm_table_to_cols_dict[table] = cols
                            else:
                                if cols == first_azm_table_to_cols_dict[table]:
                                    pass
                                    #print("table: {} same columns - no need adjust".format(table))
                                else:
                                    print("table: {} diff columns - need adjust to specify columns".format(table))
                                    sql_script = sql_script.replace("INSERT INTO {} VALUES".format(table),
                                                            "INSERT INTO {} ({}) VALUES".format(table, ",".join(cols)))

                #print("sql_script:", sql_script)
                print("... merginng to target db file:", out_db_fp)
                out_dbcon.executescript(sql_script)

        # commit new db conn
        out_dbcon.commit()

    # test merged dbfp
    with contextlib.closing(sqlite3.connect(out_db_fp)) as dbcon:
        try:
            df = pd.read_sql(
                "select count(distinct(log_hash)) from logs",
                dbcon
            )
            assert df.iloc[0, 0] == len(in_azm_list)
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: azm_sqlite_merge.merge() post merge check excception:", exstr)

    return out_db_fp


def get_sql_script(dbfp):
    sql_script = azq_utils.dump_sqlite(dbfp)
    # print("... modding sql for merging - schema")
    sql_script = sql_script.replace('CREATE TABLE IF NOT EXISTS ', 'CREATE TABLE ')
    sql_script = sql_script.replace('CREATE TABLE ', 'CREATE TABLE IF NOT EXISTS ')
    sql_script += " delete from spatial_ref_sys;\n"
    return sql_script


    
