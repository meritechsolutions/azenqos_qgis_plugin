import contextlib
import multiprocessing as mp
import os
import shutil
import sqlite3
import sys
import traceback
import uuid
from multiprocessing.pool import ThreadPool
import collections
import io
import re

import numpy as np
import pandas as pd

import azq_utils
import preprocess_azm


def merge(in_azm_list, n_proc=5, progress_update_signal=None):
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
        check_col_dict = {}
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
                        tmp_df = pd.read_sql("SELECT * FROM {};".format(table),dbcon)
                        if table not in check_col_dict.keys():
                            check_col_dict[table] = []
                        check_col_dict[table] += tmp_df.columns.tolist()
                        check_len_table = len(tmp_df)
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

        drop_col_dict = {}
        copy_col_dict = {}
        for key in check_col_dict.keys():
            group_col_dict = dict(collections.Counter(check_col_dict[key]))
            for col in group_col_dict.keys():
                if group_col_dict[col] < n:
                    if key not in drop_col_dict.keys():
                        drop_col_dict[key] = []
                    drop_col_dict[key].append(col)
                elif group_col_dict[col] == n:
                    if key not in copy_col_dict.keys():
                        copy_col_dict[key] = []
                    copy_col_dict[key].append(col)
        
        for dbfp in dbfps:
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                for table in drop_col_dict.keys():
                    if "log_hash" in drop_col_dict[table]:
                        try:
                            dbcon.executescript("DROP TABLE {};".format(table))
                        except:
                            pass
                    else:
                        try:
                            dbcon.executescript("CREATE TABLE tmp_new_table  AS SELECT {} FROM {};".format(", ".join(copy_col_dict[table]), table))
                            dbcon.executescript("DROP TABLE {};".format(table))
                            dbcon.executescript("ALTER TABLE tmp_new_table RENAME TO {};".format(table))
                        except:
                            pass
                dbcon.commit()

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

        for index, row in azm_df.iterrows():
            if progress_update_signal is not None:

                progress_update_signal.emit(merge_progress*(index+1)+20)
            print("=== dumping db to merged azm [{}/{}] ===".format(index+1, len(azm_df)))
            is_last_azm = index == azm_df.index[-1]
            dbfp = row.dbfp
            assert os.path.isfile(dbfp)
            sql_script_fp = sql_scripts[index]
            with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
                print("... merginng to target db file:", out_db_fp)
                chunk_size = 8192
                sql_script_io = io.StringIO()
                regex_pattern = re.compile(r'CREATE TABLE(?: IF NOT EXISTS)?')

                with open(sql_script_fp, "r", encoding="utf-8", errors="replace") as f:
                    while True:
                        data = f.read(chunk_size)
                        if not data:
                            break 
                        sql_script_io.write(data)
                    
                    sql_script_io.write(" delete from spatial_ref_sys;\n")
                    if is_last_azm:
                        sql_script_io.write("INSERT INTO spatial_ref_sys VALUES(4326,'epsg',4326,'WGS 84','+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs');\n")

                sql_script = sql_script_io.getvalue()
                sql_script = regex_pattern.sub('CREATE TABLE IF NOT EXISTS', sql_script)
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
    return sql_script


    
