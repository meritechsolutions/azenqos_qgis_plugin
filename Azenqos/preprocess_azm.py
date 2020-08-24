import pandas as pd
import sys
import sqlite3

import numpy as np
import os
import subprocess
import zipfile
from datetime import datetime
import traceback
import shutil
import re

import db_id_events
from dprint import dprint
from dprint import debug_file_flag
import csv
import io

#pd.set_option('display.max_colwidth', -1)

# global constants
TIME_TO_POSID_DIV = 1000
g_recov_ver = "1.1"

# global data vars
g_dbfile = None
g_datfile = None
g_tmp_process_dir = None
g_dat_df = None
g_dat_df_start_ts = None
g_dat_df_end_ts = None
g_args = None

g_recalc_dfs_dict = {}

g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache = {}

def get_module_path():
    return os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )


def reset_global_dfs():
    global g_dbfile
    global g_datfile
    global g_tmp_process_dir
    global g_dat_df
    global g_recalc_dfs_dict
    global g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache
    global g_preprocess_info_append_list

    del g_preprocess_info_append_list[:]
    
    g_dbfile = None
    g_datfile = None
    g_tmp_process_dir = None
    g_dat_df = None
    g_recalc_dfs_dict = {}
    g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache.clear()


def set_tmp_process_dir(d):
    global g_tmp_process_dir
    reset_global_dfs()
    print(("set_tmp_process_dir:", d))
    g_tmp_process_dir = d


def get_tmp_process_dir():
    global g_tmp_process_dir
    return g_tmp_process_dir


def set_g_args(args):
    global g_args
    g_args = args


def get_g_args():
    global g_args
    return g_args


g_preprocess_info_append_list = []

def append_preprocess_info(logstr):
    global g_preprocess_info_append_list
    g_preprocess_info_append_list.append(logstr)


def get_preprocess_info_list():
    global g_preprocess_info_append_list
    return g_preprocess_info_append_list


def preprocess(tmp_process_dir, args, is_merge_azqml_mode=False, unit_testing_dont_preprocess=False):
    global g_dbfile
    global g_datfile

    '''
    preprocess_azm - flow summary:
    - fix_azqml_id_shift.fix_azqml_id_shift()
    - azq_report_gen.check_and_fix_malformed_sqlite_db()
    - gen_derived_tables.gen_sqlite_derived_tables(tmp_process_dir, args)
      - recover_azqdata_db_missing_data.check_and_recover_azqdata_db_missing_data()
        - azqml_parser.parse_azqml_and_append_to_db(tmp_process_dir, log_hash, posid_geom_df, dbcon, start_time=last_db_ts, end_time=log_end_time)
      - modem_lrm_ts_shift_fix.modem_lrm_ts_shift_fix(dbcon)
        - TODO: read azqml, fix time shift, write back to diag_log_1.qmdl_.azqml
        - TODO: read azqdata.dat, fix time shift, write back to diag_log_1.qmdl_.azqml
      - mos_wav_split.check_and_put_splitted_wav_for_cont_mos(tmp_process_dir, args, return_add_omit_file_list_dict=True, dbcon=dbcon, log_hash=log_hash)

    '''

    set_g_args(args)

    reset_global_dfs()
    set_tmp_process_dir(tmp_process_dir)

    print("preprocess_azm start: tmp_process_dir:", tmp_process_dir, "is_merge_azqml_mode:", is_merge_azqml_mode)
    
    g_dbfile = os.path.join(tmp_process_dir,"azqdata.db")
    g_datfile = os.path.join(tmp_process_dir,"azqdata.dat")

    if unit_testing_dont_preprocess:
        return

    
    # dont do in "MERGE_AZQML;;;" cases
    if is_merge_azqml_mode:
        print("is_merge_azqml_mode True dont continue azm preprocess tasks")    
    else:
        print("is_merge_azqml_mode False so doing azm preprocess tasks")
        # do required re-calculations or fixes here
        if not args is None:
            if 'recover_lost_azqml_azm_to_folder' in args and not args['recover_lost_azqml_azm_to_folder'] is None:
                print("recover_lost_azqml_azm_to_folder mode")
                # legacy ais case
                check_and_recover_no_azqml_case(tmp_process_dir, args['recover_lost_azqml_azm_to_folder'], args)
                print("preprocess_azm: recover_lost_azqml_azm_to_folder mode so return now after check_and_recover_no_azqml_case()")
                return True

            # split and re-insert splitted wav files to azm if not already present
            if os.name == 'nt':
                # for quick fixing check_and_put_splitted_wav_for_cont_mos
                # azm_precheck_add_file_list would have the azqml if the sinr and friends id shift apk ver detected and azqml fixed
                azm_precheck_add_file_list = []
                azm_precheck_add_file_list += fix_azqml_id_shift.fix_azqml_id_shift()
                import mos_wav_split
                mos_wav_split.check_and_put_splitted_wav_for_cont_mos(tmp_process_dir, args, windows_prev_add_to_proc_azm_list=azm_precheck_add_file_list)
            else:
                if args['target_processed_azm'] is None:
                    print("NOTE: --target_processed_azm not specified - not doing gen_derived_tables or any azm fixes in GNU/Linux mode as we don't replace default azm files in this mode. args:", args)
                else:

                    if gen_derived_tables.is_this_azm_a_processed_azm(tmp_process_dir):
                        raise Exception("ABORT: WARNING: NOTE: specified src azm is already a processed_azm - must specify original azm for preprocess stage")

                    azm_precheck_add_file_list = []
                    azm_precheck_add_file_list += fix_azqml_id_shift.fix_azqml_id_shift()    
                    
                    print("azm_precheck_add_file_list:", azm_precheck_add_file_list)
                    processed_azm_mod_list = {
                        "add_file_list": azm_precheck_add_file_list,
                        "omit_file_list": []
                    }
                    
                    # this would detect malformed sqlite db and fix it before gen_derived_tables uses the db
                    # always_do = True to adjust for QGIS auto detect type 'float' as 'real' easier, if 'double' sometimes it gets detected as QString
                    # now this mostly wont happen so disabling to reduce cpu usage - azq_report_gen.check_and_fix_malformed_sqlite_db(g_dbfile, args, connect_and_ret_dbcon=False, always_do=False)

                    #### calc derived tables - it also calls recover_azqdata_db_missing_data.check_and_recover_azqdata_db_missing_data first
                    ret = gen_derived_tables.gen_sqlite_derived_tables(tmp_process_dir, args)
                    processed_azm_mod_list["add_file_list"] += ret["add_file_list"]
                    processed_azm_mod_list["omit_file_list"] += ret["omit_file_list"]

                    #### save to processed_azm file
                    orifn = args['azm_file']
                    newfn = args['target_processed_azm']

                    # save some space, now we handle linux servers only, ori files are in ori azm already
                    processed_azm_mod_list["omit_file_list"].append("azqmldecoder_read.bk")
                    processed_azm_mod_list["omit_file_list"].append("azqdata.db-journal")
                    processed_azm_mod_list["omit_file_list"].append("diag_log_1.ori_pre_azqmlremap")
                    
                    if len(processed_azm_mod_list["add_file_list"]) == 0 and len(processed_azm_mod_list["omit_file_list"]) == 0:
                        print("WARNING: add_file_list and omit_file_list are both empty - omit creation of processed_azm")
                    else:
                        add_files_into_zip(processed_azm_mod_list["add_file_list"], orifn, newfn, omit_list=processed_azm_mod_list["omit_file_list"])
                    
    print("preprocess_azm done")
    return True

        
def file_cp_and_rm_src(src, dest):
    try:
        os.remove(dest)
    except:
        pass
    shutil.copy(src, dest)
    try:
        os.remove(src)
    except:
        pass


def direction_symbol_to_status_int(s):
    if s == "send":
        return 0
    return 1


def conv_df_time_to_millis_since_epoch(df, tz_offset):
    df["time"] = pd.to_datetime(df["time"])
    # convert time to millis since epoch before write to csv
    df["time"] = df["time"] - datetime(1970,1,1)
    df["time"] = df["time"] - np.timedelta64(tz_offset,'ms')
    df["time"] = df["time"] / np.timedelta64(1,'ms')
    return df # actually changes are in-place inside the df so return isnt actually required


def py_zip_azm(merged_azqdata_dat_fp, recover_azm_fp, args):
    print("zip method: using standard py zip - in memory zip")
    # use merged_azqdata_dat_fp

    # http://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module

    zin = zipfile.ZipFile (args['azm_file'], 'r')
    zout = zipfile.ZipFile (recover_azm_fp, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
    #prev_item = None
    item_fn_written = []
    for item in zin.infolist():
        print("item.filename:",item.filename)
        if item.filename in item_fn_written: # omit dup azqml cases
            print("omit dup filename:",item.filename)
            continue
        #prev_item = item
        if (item.filename == 'azqdata.dat' in item.filename):
            print("omit azqdata.dat in new zip")
        else:
            buffer = zin.read(item.filename)
            zout.writestr(item, buffer)
        item_fn_written.append(item.filename)

    zout.write(merged_azqdata_dat_fp, "azqdata.dat") # write the new merged azqdata.dat
    zout.close()
    zin.close()


def add_files_into_zip(add_list, ori_zip, new_zip, omit_list=[]):

    # dont use native zip anymore now, as big slow down issues when adding multiple...
    try_native_zip=False

    # try make dir of new_zip if not yet created
    try:
        os.makedirs(os.path.dirname(new_zip))
    except:
        pass

    """
    print("add_files_into_zip: add_list:", add_list)
    print("add_files_into_zip: ori_zip:", ori_zip)
    print("add_files_into_zip: new_zip:", new_zip)
    print("add_files_into_zip: omit_list:", omit_list)
    print("add_files_into_zip: try_native_zip:", try_native_zip)
    """
    
    zip_found = False

    if try_native_zip:
        try:
            ret = subprocess.call("zip --help", shell=True)
            if ret == 0:
                zip_found = True
        except:
            pass

    if zip_found:

        try:
            print("zip method: native zip executable")

            cmd = 'zip -F "'+ori_zip+'" --out "'+new_zip+'"'
            print("fix zip cmd: "+cmd)
            ret = subprocess.call(cmd, shell=True)
            print("fix zip ret:",ret)
            if ret != 0:
                raise Exception("ABORT: fix/copy zip failed ret: "+str(ret))


            # replace existing file with new one
            for fp in add_list:                
                cmd = 'zip --junk-paths "'+new_zip+'" "'+fp+'"'
                print("add new entry cmd: "+cmd)
                ret = subprocess.call(cmd, shell=True)
                print("add new entry cmd ret: ",ret)
                if ret != 0:
                    raise Exception("ABORT: add new entry failed ret: "+str(ret))
            for ofp in omit_list:
                print("omit file from omit_list:", ofp)
                cmd = 'zip -d "'+new_zip+'" "{}"'.format(ofp)
                print("rm omit file in zip cmd:", cmd)
                ret = subprocess.call(cmd, shell=True)
                print("ret: ",ret)
            return 0
        except Exception as e:
            print("native zip exception: ",e)
            print("revert to py zip...")
            return py_zip_add(add_list, ori_zip, new_zip, omit_list)
    else:
        return py_zip_add(add_list, ori_zip, new_zip, omit_list)

    return -1


# use add_files_into_zip() instead of this - it would call this if required but will try native method first
def py_zip_add(add_list, ori_zip, new_zip, omit_list=[]):
    print("zip method: using standard py zip - in memory zip")

    # rm duplicates
    add_list = list(set(add_list))
    omit_list = list(set(omit_list))

    #print "add_list:", add_list
    #print "omit_list:", omit_list    
    
    # use merged_azqdata_dat_fp

    # http://stackoverflow.com/questions/513788/delete-file-from-zipfile-with-the-zipfile-module

    zin = zipfile.ZipFile (ori_zip, 'r')
    zout = zipfile.ZipFile (new_zip, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
    #prev_item = None
    item_fn_written = []

    # write new ones first in case it would replace an existing file (like new azqdata.db) so it would be in item_fn_written list
    for fp in add_list:
        fp_basename = os.path.basename(fp)
        print("add_list: adding file to zip:", fp_basename)
        zout.write(fp, fp_basename)
        item_fn_written.append(fp_basename)

    for item in zin.infolist():
        print("ori zip put item.filename:", item.filename)
        if item.filename in item_fn_written: # omit dup azqml cases
            print("omit dup filename:", item.filename)
            continue
        if item.filename in omit_list:
            print("omit file because it is in omit_list:", item.filename)
            continue
        #prev_item = item
        buffer = zin.read(item.filename)
        wret = zout.writestr(item.filename, buffer)
        print("buffer len {} wret {}".format(len(buffer), wret))
        item_fn_written.append(item.filename)
        
    zout.close()
    zin.close()
    
    return 0
    
    
def escape_str(str):
    try:
        str = str.replace("@","@@")
        str = str.replace(",","@c")
        str = str.replace("\r","@r")
        str = str.replace("\n","@n")
    except:
        pass
    return str


def unescape_str(str):
    try:
        str = str.replace("@c", ",")
        str = str.replace("@@", "@")
        str = str.replace("@r", "\r")
        str = str.replace("@n", "\n")
    except:
        pass
    return str

def unescape_row(row, col):
    row[col] = unescape_str(row[col])

    
def unescape_col(df, col):
    for id, row in df.iterrows():
        df.loc[id][col] = unescape_str(row[col])


def get_tz_offset_millis_from_azqdata_dat():
    global g_datfile

    # example: 1488181012233,2,AndroidLogStart,v3.0.602,2.0.7:15,28800000
    first_line = get_azqdata_dat_first_line()
    
    return int(first_line.split(",")[5].strip())

    

def get_tz_offset_timedelta_from_azqdata_dat():
    tz_offset_millis = get_tz_offset_millis_from_azqdata_dat()
    return np.timedelta64(tz_offset_millis,'ms')


def get_azqdata_dat_df(dont_filter_time=False):
    global g_datfile
    global g_dat_df
    global g_dat_df_start_ts
    global g_dat_df_end_ts
    

    if not g_dat_df is None and not dont_filter_time:
        dprint("get_azqdata_dat_df: ret existing instance")
        return g_dat_df.copy()
    
    #### read from azqdata.dat    
    # csv columns: java: writeLine(timeLong, type.getValue(), eventID.getValue(), escapedInfo, escapedDetail);
    dat_cols = ["ts","type","id","info","detail","status"]
    print("get_azqdata_dat_df: read_csv g_datfile:", g_datfile)
    # windows server having issues getting different results (lesser lines) than when using gnu. fixing this with pre-open with 'rb' flag then using that file obj

    if os.name == 'nt':
        with open(g_datfile, "rb") as pdfptr:
            g_dat_df = pd.read_csv(pdfptr, names=dat_cols, dtype='object')
    else:
        g_dat_df = pd.read_csv(g_datfile, names=dat_cols, dtype='object')
        
    print("get_azqdata_dat_df: read_csv done len", len(g_dat_df))
    g_dat_df_ori = g_dat_df
    try:
        # filter for rows that are between start log time and end time only
        print(("filtering azqdata.dat for rows between start and end ts - avoid huge time jumps - start - ori len:", len(g_dat_df)))
        #g_dat_df.ts = pd.to_numeric(g_dat_df.ts)
        g_dat_df = g_dat_df.dropna(subset=["ts"])  # next line conv to uint64 will fail if has empty val for ts
        g_dat_df.ts = g_dat_df.ts.astype(np.uint64)
        
        """ 
        5
        6
        1
        2
        3
        4

        get start_ts and end_ts
             - we must handle merged azqdata.dat cases
             - we must handle 'recovery' log cases where last line is not the time when the log actually ended like below: 
1499773864028,2,20204,T:1 throughput avg.=944.07kbps : time=3617.76s : totalbytes=437175306 : max throughput=7278.00kbps,script stopped
1499855314455,2,SetTagName,(recovery)

             - start_ts: need to find all 'AndroidLogStart' instances, sort then take first
             - end_ts:
               - get all end_ts for matching 'AndroidLogStart' rows:
                 - if this is the first one then the matching is the last row
                 - else treat the row before this 'AndroidLogStart' as the last row
                   - check the 'last row' - if it's like"...SetTagName,(recovery)" then use the one before that

        """
        # DONT SORT YET! WE NEED TO FIND THE MATCHING END BEFORE NEXT START FIRST
        log_start_rows = g_dat_df[g_dat_df.id == "AndroidLogStart"] 
        pd.set_option('display.float_format', lambda x: '%.3f' % x)
        print("log_start_rows:", log_start_rows)
        start_list = log_start_rows.index.tolist()
        print("start_indices:", start_list)
        end_list = []
        start_len = len(start_list)
        # fill end_list
        for i in range(0, start_len):
            if i + 1 < start_len: # if there is more 'AndroidLogStart' rows in the list
                end_list.append(start_list[i+1] - 1) # the row index before the next AndroidLogStart
            else:
                end_list.append(len(g_dat_df) - 1) # the last row
        print("end_list:", end_list)
        
        # re-check the 'last row' - if it's like"...SetTagName,(recovery)" then use the one before that
        for i in range(0, start_len):
            print("recheck: g_dat_df.iloc[end_list[i]].info:", g_dat_df.iloc[end_list[i]].info)
            if "(recovery)" in ""+str(g_dat_df.iloc[end_list[i]].info):
                print("found (recovery) in end_list[i].info - use prev instead...")
                end_list[i] = end_list[i] - 1
        print("end_list after recheck recov:", end_list)

        log_end_rows = g_dat_df.iloc[end_list]
        print("log_end_rows:", log_end_rows)
        
        start_ts = log_start_rows.sort_values("ts").iloc[0].ts
        end_ts = log_end_rows.sort_values("ts", ascending=False).iloc[0].ts
        g_dat_df_start_ts = start_ts
        g_dat_df_end_ts = end_ts
        print(("g_dat_dfstart_ts", start_ts))
        print(("g_dat_df_end_ts", end_ts))
        if not dont_filter_time:
            g_dat_df = g_dat_df[g_dat_df.ts >= start_ts]
            g_dat_df = g_dat_df[g_dat_df.ts <= end_ts]
            dprint("filtering azqdata.dat for rows between start and end ts - avoid huge time jumps - done - refilt len:", len(g_dat_df))
    except Exception:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        g_dat_df = g_dat_df_ori
        print("WARNING: filtering azqdata.dat for rows between start and end ts - avoid huge time jumps - FAILED - restored non-filtered df len {} - CAN CAUSE HUGE JUMPS AND HUGE DATA IF RESAMPLED - exception: ".format(len(g_dat_df)), exstr)

    """ not used
    print "add timezone offset to the ts column: {}".format(g_dat_df.iloc[0].status)
    # first line: 1488181012233,2,AndroidLogStart,v3.0.602,2.0.7:15,28800000
    
    tz_offset_millis = int(g_dat_df.iloc[0].status)

    print "tz_offset_millis",tz_offset_millis
    g_dat_df['ts'] = pd.to_numeric(g_dat_df['ts'])
    g_dat_df['ts'] += tz_offset_millis
    """
    
    #print "g_dat_df:",g_dat_df

    """ dont unescape now - takes too long - do later before query if required
    print "get_azqdata_dat_df: unescape info"
    unescape_col(g_dat_df, "info")
    print "get_azqdata_dat_df: unescape detail"
    unescape_col(g_dat_df, "detail")
    print "get_azqdata_dat_df: unescape status"
    unescape_col(g_dat_df, "status")
    """

    return g_dat_df


def get_azqdata_dat_location_df(drop_ts_dup=False):
    print("get_azqdata_dat_location_df")
    dat_df = get_azqdata_dat_df()
    print("dat_df len", len(dat_df))

    loc_df = dat_df[dat_df.type == "AddGpsStatus"].copy()  # fix pandas modify slice setting with copy warning

    # drop unused cols
    del loc_df["type"]
    del loc_df["detail"]
    del loc_df["status"]

    loc_df.columns = ["ts","positioning_lon","positioning_lat"]

    loc_df.positioning_lat = pd.to_numeric(loc_df.positioning_lat)
    loc_df.positioning_lon = pd.to_numeric(loc_df.positioning_lon)

    loc_df = loc_df.dropna(how='any')

    # otherwise geom bytes dont exactly match - see tests like: test_fill_geom_for_lat_lon_from_azqdata_dat.py: assert dat_location_df.loc[0, "positioning_lat"] == np.float64(28.6447976)
    loc_df = loc_df.round(
        {
            "positioning_lon":8,
            "positioning_lat":8
        }
    )
    
    if drop_ts_dup:
        loc_df.drop_duplicates("ts", keep='last', inplace=True)
    #print "loc_df:",loc_df
    print("get_azqdata_dat_location_df len:", len(loc_df))
    print("get_azqdata_dat_location_df head ret:", loc_df.head())
    return loc_df


g_db_id_events_df = None


def get_db_id_events_df():
    global g_db_id_events_df
    if g_db_id_events_df is not None:
        return g_db_id_events_df
    mp = get_module_path()
    g_db_id_events_df = pd.read_csv(        
        os.path.join(
            mp,
            "db_id_events.py"
        ),
        sep="=",
        names=["name","event_id"]
    )
    g_db_id_events_df["name"] = g_db_id_events_df["name"].str.strip()
    g_db_id_events_df["event_id"] = pd.to_numeric(g_db_id_events_df["event_id"], errors="coerce")

    return g_db_id_events_df


def get_azqdata_dat_events_df(drop_ts_dup=False):
    print("get_azqdata_dat_location_df")
    dat_df = get_azqdata_dat_df()
    print("dat_df len", len(dat_df))

    events_df = dat_df[dat_df.type == "2"].copy()  # fix pandas modify slice setting with copy warning

    # drop unused cols
    del events_df["type"]
    del events_df["status"]
    events_df.columns = ["ts","event_id","info","detail"]
    events_df["event_id"] = events_df["event_id"].str.replace("AndroidLogStart", "36")
    events_df["event_id"] = events_df["event_id"].str.replace("AndroidLogStop", "37")
    events_df["event_id"] = pd.to_numeric(events_df["event_id"], errors="coerce")
    events_df.dropna(subset=["event_id"], inplace=True)
    events_df["event_id"] = events_df["event_id"].astype(int)

    # prepare to join 'name' from get_db_id_events_df()
    dbide_df = get_db_id_events_df()
    events_df = events_df.merge(dbide_df, on="event_id", how="left")

    return events_df


def get_azqdata_dat_message_df(drop_ts_dup=False):
    dat_df = get_azqdata_dat_df()
    
    msg_df = dat_df[dat_df.type == "13"].copy()  # fix pandas modify slice setting with copy warning

    # drop unused cols
    del msg_df["type"]
    msg_df.columns = ["ts","msg_id","name","detail_str","direction_send_0"]
    msg_df["msg_id"] = pd.to_numeric(msg_df["msg_id"], errors="coerce")
    msg_df.dropna(subset=["msg_id"], inplace=True)
    msg_df["msg_id"] = msg_df["msg_id"].astype(int)
    msg_df["symbol"] = "recv"
    msg_df["direction_send_0"] = pd.to_numeric(msg_df["direction_send_0"])
    msg_df.loc[msg_df["direction_send_0"] == 0, "symbol"] = "send"

    return msg_df


def get_azqdata_dat_script_log_info_df(drop_ts_dup=False):
    dat_df = get_azqdata_dat_df()
    
    sn_df = dat_df[(dat_df.type == "1") & (dat_df.id == "202")].copy()  # fix pandas modify slice setting with copy warning

    script_name = None
    if len(sn_df):
        script_name = sn_df.iloc[0].info
    
    s_df = dat_df[(dat_df.type == "1") & (dat_df.id == "205")].copy()  # fix pandas modify slice setting with copy warning
    if len(s_df):
        s_df.iloc[0].info
        # drop unused cols
        s_df = s_df[['ts','info']].copy()
        s_df.columns = ["ts","script"]
        s_df['script_name'] = script_name
        
        return s_df



def do_azm_ts_convert_df(df, keep_ts=False, set_time_as_index=True):
    df = df.copy()  # prevent cases where we're modifying a slice of an existing df
    tz_offset_timedelta = get_tz_offset_timedelta_from_azqdata_dat()
    col = "ts"
    if keep_ts:
        col = "time"
    df[col] = pd.to_datetime(df["ts"], unit='ms') + tz_offset_timedelta
    if set_time_as_index:
        df = df.set_index(col)
        df = df.sort_index()
    else:
        df = df.reset_index()
        try:
            del df["index"]
        except:
            pass
        print("do_azm_ts_convert_df: cols", df.columns)
    return  df


def get_azqdata_dat_location_df_ts_converted(drop_ts_dup=False, set_time_as_index=True):
    location_df = get_azqdata_dat_location_df(drop_ts_dup)
    return do_azm_ts_convert_df(location_df, keep_ts=True, set_time_as_index=set_time_as_index)


def get_azqdata_dat_events_df_ts_converted(drop_ts_dup=False, set_time_as_index=True):
    events_df = get_azqdata_dat_events_df(drop_ts_dup)
    return do_azm_ts_convert_df(events_df, keep_ts=True, set_time_as_index=set_time_as_index)


def get_azqdata_dat_message_df_ts_converted(drop_ts_dup=False, set_time_as_index=True):
    msg_df = get_azqdata_dat_message_df(drop_ts_dup)
    return do_azm_ts_convert_df(msg_df, keep_ts=True, set_time_as_index=set_time_as_index)


def get_azqdata_dat_df_ts_converted():
    return do_azm_ts_convert_df(get_azqdata_dat_df())


def get_azqdata_dat_location_df_ts_secs_as_posid():
    global TIME_TO_POSID_DIV
    
    print("get_azqdata_dat_location_df_ts_secs_as_posid: enter")
    loc_df = get_azqdata_dat_location_df()
    try:
        print("get_azqdata_dat_location_df_ts_secs_as_posid: len loc_df ",len(loc_df))
    except:
        pass
    if loc_df is None:
        return loc_df
    print("ts dtype",loc_df.ts.dtype)
    loc_df.ts = loc_df.ts / TIME_TO_POSID_DIV
    loc_df.ts = loc_df.ts.astype(int)
    print("post div ts dtype",loc_df.ts.dtype)
    loc_df.columns = ["posid","positioning_lon","positioning_lat"]
    return loc_df



def check_and_recalc_if_required(elm_id, elm_type, arg, val_col_name, just_check_if_exists):
    global g_wcdma_missing_neigh_elm
    global g_recalc_dfs_dict

    # wcdma missing neighbor calculation:
    
    if elm_id == g_wcdma_missing_neigh_elm["id"]:
        # val_col_name: wcdma_missing_neighbor_1
        dprint("check_and_recalc_if_required: enter wcdma_missing_neighbor case - val_col_name:", val_col_name)
        
        # get df: wcdma L3 rrc measrep where there is e1a and e1c
        # select * from signalling where msg_id = 30109 and detail_str like "%(e1a)%"

        # get df: sc of all detected cells found
        # select time, wcdma_n_dset_cells, wcdma_dset_sc_1, wcdma_dset_sc_2, wcdma_dset_sc_3, wcdma_dset_sc_4, wcdma_dset_sc_5, wcdma_dset_sc_6, wcdma_dset_sc_7, wcdma_dset_sc_8 from wcdma_cell_meas where wcdma_n_dset_cells > 0

    return None

g_azl_elm_csv_dict = {}

def get_azl_elm_csv_dict():
    global g_azl_elm_csv_dict
    return g_azl_elm_csv_dict

def set_azl_elm_csv(csvs):
    global g_azl_elm_csv_dict

    if csvs is None:
        g_azl_elm_csv_dict = {}
        return

    azl_elm_csv_list = None
    
    if ";;;" in csvs:
        azl_elm_csv_list = csvs.split(";;;")
    else:
        azl_elm_csv_list = [csvs]

    # check and warn if not exists
    for csvfp in azl_elm_csv_list:
        if os.path.isfile(csvfp):
            fn = os.path.basename(csvfp)
            elm_id = fn.split("azl_")[1].split(".")[0]
            g_azl_elm_csv_dict[elm_id] = csvfp
        else:
            print("WARNING: specified azl csv file does not exist:", csvfp)

    print("set_azl_elm_csv done: g_azl_elm_csv_dict:", g_azl_elm_csv_dict)
    return


g_prev_azqml_csv_df = {}
def get_azqml_elm_df(elm_id, elm_type, arg=1, val_col_name="val", just_check_if_exists=False):
    global g_tmp_process_dir
    global g_dat_df
    global g_dat_df_start_ts
    global g_dat_df_end_ts
    global g_prev_azqml_csv_df
    
    get_azqdata_dat_df() # make g_dat_df valid
    
    # for some elements, they dont exist in the azqml or db - it needs to be recalculated from other elements check those cases
    recalc_df = check_and_recalc_if_required(elm_id, elm_type, arg, val_col_name, just_check_if_exists)
    if not recalc_df is None:
        return recalc_df
    
    # example ./azqml_to_csv "/home/kasidit/azq_docker_containers/azqgen_ondemand/azq_report_gen/existing_report/359600061716407 27_2_2017 16.5.13.azm_FILES/diag_log_1.qmdl_.azqml" out.csv "double" --azqml_index 1 --azqml_id 5607
    mp = get_module_path()

    exec_name = "azqml_to_csv"
    exec_folder = None
    
    if os.name == 'posix':
        exec_folder = os.path.join("azqml_to_csv","gnu_exec")
        dprint("I'm running on GNU!")
    elif os.name == 'nt':
        exec_folder = os.path.join("azqml_to_csv","win_exec")
        dprint("I'm running on Windows")
        exec_name += ".exe"

    exec_path = os.path.join(mp,exec_folder,exec_name)
    azqml_path = os.path.join(g_tmp_process_dir, "diag_log_1.qmdl_.azqml")
    out_csv_path = azqml_path+("_{}_{}_{}.csv".format(elm_id,arg,just_check_if_exists))

    # check if this elm_id is in the azl csv list:

    # adj azl replace: if 5027,cm_system_mode_index then use 5021,cm_system_mode instead

    # dont allow this cm_system_mode - casues conflict with cm_system_mode_index
    if elm_id == 5021:
        return pd.DataFrame(columns=["ts","type","id","cm_system_mode","arg"])
    
    ori_elm_id = elm_id
    print("ori_elm_id:", ori_elm_id)

    is_cm_system_mode_index = False # this shall be calc by legacy engine and shall provide csv to us only
    if elm_id == 5027:
        is_cm_system_mode_index = True
        elm_id = 5021
        print("is_cm_system_mode_index:", is_cm_system_mode_index)
        print("ori_elm_id:", ori_elm_id)
        
    is_azl_csv = False
    if str(elm_id) in get_azl_elm_csv_dict():
        out_csv_path = get_azl_elm_csv_dict()[str(elm_id)]
        print("elm_id:", elm_id, "shall be provided by --azl_exported_csv file:", out_csv_path, "just_check_if_exists:", just_check_if_exists)
        is_azl_csv = True
    else:
        print("elm_id:", elm_id, "shall NOT be provided azl_exported_csv","just_check_if_exists:", just_check_if_exists)
        if is_cm_system_mode_index:
            # cm_system_mode_index shall come from azl csv only
            return pd.DataFrame(columns=["ts","type","id","cm_system_mode_index","arg"])
        
    cmdret = None
    cmd = None
    if is_azl_csv or (os.path.isfile(out_csv_path) and just_check_if_exists == False):
        print("azml_to_csv: file already exists - no need to regen...")
        cmdret = 0
    else:

        cmd = [
            exec_path,
            azqml_path,
            out_csv_path,
            elm_type,
            "--azqml_id",str(elm_id)
        ]

        if just_check_if_exists:
            cmd += ["--check_if_exist_exit_on_first_match"]

        if arg > 0:
            cmd += ["--azqml_index",str(arg)]

        print(("get_azqml_dat_elm: cmd:",cmd))
        cmdret = subprocess.call(cmd)

        if just_check_if_exists:
            if cmdret>=1:
                return True
            else:
                return False

    dat_cols = ["ts","type","id",val_col_name,"arg"]


    if cmdret == 0:
        ret_df = None
        dprint("gen csv complete - read it start...")
        if out_csv_path in g_prev_azqml_csv_df:
            print("using azqml ret_df from prev df cache...")
            ret_df = g_prev_azqml_csv_df[out_csv_path]
        else:
            print("read from csv...")
            ret_df = pd.read_csv(out_csv_path, names=dat_cols)

            ret_df.ts = pd.to_numeric(ret_df.ts)
            print("ret_df_head:", ret_df.head())

            if is_azl_csv:
                try:
                    # handle tz offset for azl csv
                    tz_offset = get_tz_offset_millis_from_azqdata_dat()
                    print("is_azl_csv mode substract tz_offset:", tz_offset)
                    ret_df["ts_with_tz"] = ret_df.ts
                    ret_df.ts = ret_df.ts - tz_offset                    
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: azl csv convert rm tz offset exception:", exstr)
            else:
                try:
                    # handle tz offset for azqml csv
                    tz_offset = get_tz_offset_millis_from_azqdata_dat()
                    print("is_azqml_csv mode addd tz_offset:", tz_offset)
                    ret_df["ts_with_tz"] = ret_df.ts + tz_offset
                except:
                    type_, value_, traceback_ = sys.exc_info()
                    exstr = str(traceback.format_exception(type_, value_, traceback_))
                    print("WARNING: azqml csv convert rm tz offset exception:", exstr)
            print("ret_df_head after tz offset, pre time ", ret_df.head())
            try:
                ret_df["time"] = pd.to_datetime(ret_df.ts_with_tz, unit='ms')
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("azqml mode create ret_df.time exception:", exstr)

            print("ret_df_head after add time ", ret_df.head())

            # adj for cm_system_mode_index
            if ori_elm_id == 5027 and is_cm_system_mode_index: # cm_system_mode_index
                # legacy code: static string[] systemModeTable = { "No Service", "GSM", "WCDMA","LTE","CDMA","HDR" };
                print("5027 replace start - ori df:", ret_df, "val_col_name:", val_col_name)
                val_col_name = "cm_system_mode_index"            
                #ret_df[val_col_name] = ret_df[ori_val_col_name]
                ret_df[val_col_name] = ret_df[val_col_name].str.replace("No Service", "0")
                ret_df[val_col_name] = ret_df[val_col_name].str.replace("GSM", "1")
                ret_df[val_col_name] = ret_df[val_col_name].str.replace("WCDMA", "2")
                ret_df[val_col_name] = ret_df[val_col_name].str.replace("LTE", "3")
                ret_df[val_col_name] = ret_df[val_col_name].str.replace("CDMA", "4")
                ret_df[val_col_name] = ret_df[val_col_name].str.replace("HDR", "5")
                ret_df[val_col_name] = ret_df[val_col_name].fillna("0")

                ret_df[val_col_name] = pd.to_numeric(ret_df[val_col_name])

                print("5027 ret_df:", ret_df)

                    
            g_prev_azqml_csv_df[out_csv_path] = ret_df
            print("len(g_prev_azqml_csv_df):", len(g_prev_azqml_csv_df))
            dprint("gen azqml csv complete - read it... done")


        dprint("csv ret_df head:", ret_df.head())

        g_dat_df_is_none = g_dat_df is None
        g_dat_df_len = 0
        if not g_dat_df_is_none:
            g_dat_df_len = len(g_dat_df)
        
        dprint("g_dat_df is none:", g_dat_df is None)
        if not g_dat_df is None:
            dprint("g_dat_df is none:", g_dat_df is None)
            
        try:
            # filter for rows that are between start log time and end time only
            print(("filtering azqml val_col_name [{}] for rows between start and end ts - avoid huge time jumps - start - nrows {}".format(val_col_name, len(ret_df))))
            if not g_dat_df_is_none and g_dat_df_len > 0:
                start_ts = g_dat_df_start_ts
                end_ts = g_dat_df_end_ts

                ret_df.ts = pd.to_numeric(ret_df.ts)
                ret_df = ret_df[ret_df.ts > start_ts]
                ret_df = ret_df[ret_df.ts < end_ts]
            print(("filtering azqml val_col_name [{}] for rows between start and end ts - avoid huge time jumps - done - nrows {}".format(val_col_name, len(ret_df))))
        except Exception as e:
            print("filtering azqml val_col_name [{}] for rows between start and end ts - avoid huge time jumps - exception: {}".format(
                val_col_name,
                str(e)
            ))

        if just_check_if_exists: # azl csv case will enter here
            return len(ret_df) > 0
        
        return ret_df
    
    emsg = "WARNING: gen_csv from azqml ret code not 0 - cmd {} - ret {}".format(cmd, cmdret)
    print(emsg)

    # ret empty df in this case
    return pd.DataFrame(columns=dat_cols)


def filter_db_df_with_log_start_end_time(ret_df):
    global g_dat_df_start_ts
    global g_dat_df_end_ts
    global g_dat_df

    get_azqdata_dat_df() # make g_dat_df valid
    
    try:
        # filter for rows that are between start log time and end time only
        print(("filtering df for rows between start and end ts - avoid huge time jumps - start - nrows {}".format( len(ret_df))))

        tz_offset = get_tz_offset_millis_from_azqdata_dat()
    
        #g_dat_df_is_none = g_dat_df is None
        g_dat_df_len = 0
        
        if g_dat_df is not None:
            g_dat_df_len = len(g_dat_df)
        if g_dat_df_len > 0:
            start_ts = g_dat_df_start_ts
            end_ts = g_dat_df_end_ts

            # handle cases where minor timeshift

            ret_df["ts"] = ret_df["time"]
            ret_df["ts"] = ret_df["ts"] - datetime(1970,1,1)
            ret_df["ts"] = ret_df["ts"] - np.timedelta64(tz_offset,'ms')
            ret_df["ts"] = ret_df["ts"] / np.timedelta64(1,'ms')

            try:
                print("filter_db_df_with_log_start_end_time: ret_df.ts.min():", ret_df.ts.min())
                print("filter_db_df_with_log_start_end_time: start_ts:", start_ts)
                print("filter_db_df_with_log_start_end_time: ret_df.ts.max():", ret_df.ts.max())            
                print("filter_db_df_with_log_start_end_time: end_ts:", end_ts)
            except:
                pass

            ret_df = ret_df[ret_df.ts >= start_ts]
            ret_df = ret_df[ret_df.ts <= end_ts]
            del ret_df["ts"]
        print(("filtering df for rows between start and end ts - avoid huge time jumps - done - nrows {}".format(len(ret_df))))
    except Exception as e:
        print("filtering ret_df for rows between start and end ts - avoid huge time jumps - exception: {}".format(
            str(e)
        ))

    return ret_df



g_time_cloned_location_df = None


def clear_g_time_cloned_location_df():
    global g_time_cloned_location_df
    g_time_cloned_location_df = None


def prepare_time_cloned_location_df(primary_dbcon):
    global g_time_cloned_location_df
    
    print("prepare_time_cloned_location_df() START")
    g_time_cloned_location_df = None
    g_time_cloned_location_df = get_dbcon_location_df(primary_dbcon)
    # if multiple logs are used and gps_clone feature is used, especially in benchmarks, there might be too many at same timing in location_df xN of good gps used in bechmark - so round to 1 sec then drop the dups
    g_time_cloned_location_df["time"] = g_time_cloned_location_df["time"].dt.round('1s')    
    g_time_cloned_location_df.drop_duplicates(subset=["time"], inplace=True)
    print("prepare_time_cloned_location_df() DONE")


def is_using_time_cloned_location_df():
    global g_time_cloned_location_df    
    return (g_time_cloned_location_df is not None)


def fix_pandas() -> None:
    # https://github.com/pandas-dev/pandas/issues/33827
    import pathlib
    from pandas.io.common import  _expand_user
    import pandas
    def _stringify_path(filepath_or_buffer):
        """Attempt to convert a path-like object to a string.

        Parameters
        ----------
        filepath_or_buffer : object to be converted

        Returns
        -------
        str_filepath_or_buffer : maybe a string version of the object

        Notes
        -----
        Objects supporting the fspath protocol (python 3.6+) are coerced
        according to its __fspath__ method.

        For backwards compatibility with older pythons, pathlib.Path and
        py.path objects are specially coerced.

        Any other object is passed through unchanged, which includes bytes,
        strings, buffers, or anything else that's not even path-like.
        """
        if hasattr(filepath_or_buffer, "__fspath__"):
            return filepath_or_buffer.__fspath__()
        elif isinstance(filepath_or_buffer, type(pathlib.Path)):
            return str(filepath_or_buffer)
        return _expand_user(filepath_or_buffer)
    pandas.io.common._stringify_path = _stringify_path
    return



g_azq_global_elm_info_df = None
def get_elm_df_from_csv():
    global g_azq_global_elm_info_df
    
    if g_azq_global_elm_info_df is not None:
        return g_azq_global_elm_info_df
    cols = ["id","var_name","csharp_oldname","db_table","var_type","db_type","val_min","val_max","n_arg_max","name","expiry","definition"]
    csvfp = os.path.join(get_module_path(),"azq_global_element_info_list.csv")
    fix_pandas()
    g_azq_global_elm_info_df = pd.read_csv(csvfp, compression=None, names=cols).iloc[3:]  # first two rows are comments

    g_azq_global_elm_info_df["n_arg_max"].fillna(value="1", inplace=True)

    return g_azq_global_elm_info_df


gei_df_n_max_arg_1_elm = None
def get_gei_df_n_max_arg_1_elm():
    global gei_df_n_max_arg_1_elm
    if gei_df_n_max_arg_1_elm is None:        
        gei_df_n_max_arg_1_elm = get_elm_df_from_csv()
        gei_df_n_max_arg_1_elm["n_arg_max"] = pd.to_numeric(gei_df_n_max_arg_1_elm.n_arg_max)
        gei_df_n_max_arg_1_elm = gei_df_n_max_arg_1_elm[gei_df_n_max_arg_1_elm["n_arg_max"] == 1]
    return gei_df_n_max_arg_1_elm

    
def check_azqdata_db_col_name_n_arg_max_1_cases(table, columns):

    gei_nam_df = get_gei_df_n_max_arg_1_elm()
    
    max_arg_1_elm_cols = gei_nam_df[gei_nam_df.db_table == table].var_name
    max_arg_1_elm_cols += "_1"
    max_arg_1_elm_cols_str_list = max_arg_1_elm_cols.values

    new_col_names = []
    # first is "time" so omit - use range(1, n) instead
    for i in range(len(columns)):
        col = columns[i]
        #print "check_azqdata_db_col_name_n_arg_max_1_cases: check col:", col, "max_arg_1_elm_cols:", max_arg_1_elm_cols_str_list
        if col in max_arg_1_elm_cols_str_list:
            #print "check_azqdata_db_col_name_n_arg_max_1_cases: got col case: {}".format(col)
            name_no_arg = str(columns[i])[:-2]  # remove _1
            new_col_names.append(name_no_arg)
        else:
            new_col_names.append(col)

    return new_col_names


def get_azqdata_db_col_name_invalid_arg_n_cols(cols):
    gei_nam_df = get_elm_df_from_csv()
    var_name_list = gei_nam_df.var_name.values
    inv_cols = []
    for col in cols:
        try:
            print("type(col)", type(col))
            match = re.search(r'_\d{0,3}$', col)
            arg_n = None
            var_name = None
            if match is not None:
                match = match.group()
                match_val = match.replace("_","",1)
                arg_n = int(match_val)
                #print "match:", match
                reversed_match = match[::-1]
                var_name = col[::-1].replace(reversed_match,"",1)[::-1] # https://stackoverflow.com/questions/9943504/right-to-left-string-replace-in-python
                #print "var_name:", var_name
                #print "arg_n:", arg_n

            if arg_n is not None and var_name is not None:
                # check against gei_nam_df
                if var_name in var_name_list:
                    n_arg_max = gei_nam_df[gei_nam_df.var_name == var_name].iloc[0].n_arg_max
                    #print "n_arg_max:", n_arg_max
                    if arg_n <= n_arg_max:
                        pass
                    else:
                        #print "get_azqdata_db_col_name_invalid_arg_n_cols: col {} invalid arg_n {} add to invalid_cols list...".format(col, arg_n)
                        inv_cols.append(col)                    
        except:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: get_azqdata_db_col_name_invalid_cols check_col {} exception: {}".format(col, exstr))
            
    return inv_cols


def get_table_for_column(param_col_with_arg):

    # plot log_hash to show where each log ends
    if param_col_with_arg == "log_hash":
        return "location"
    
    row = get_elm_info(param_col_with_arg)
    if row is None:
        return None
    return row.db_table.strip()



def get_elm_info(param_col_with_arg):
    elm_type = "double"
    #elm_id = None

    # handle cases where there is really _n in var_name already too
    param_col_no_arg = get_elm_name_from_param_col_with_arg(param_col_with_arg)

    for elm_name in [param_col_with_arg, param_col_no_arg]:
        dprint("check get_elm_info: elm_type:", elm_type, "elm_name:", elm_name)

        # now get elm_id
        elm_df = get_elm_df_from_csv()
        matched_rows = elm_df.query("var_name == '{}'".format(elm_name))
        dprint("match for elm_name result nrows:", len(matched_rows))
        if len(matched_rows) > 0:
            row = matched_rows.iloc[0].copy()
            #elm_id = row.id
            row.var_type = row.var_type.strip().lower()
            dprint("precheck row.var_type:", row.var_type)
            if row.var_type == "integer":
                row.var_type = "int"
            return row
        
    return None



def is_param_from_azqdata_dat(param_col_no_arg):
    if param_col_no_arg == "positioning_lat" or param_col_no_arg == "positioning_lon":
        return True
    return False


def get_elm_name_from_param_col_with_arg(param_col_with_arg, return_arg_too=False):
    
    elm_name = param_col_with_arg
    arg = 1
    try:
        splitted = param_col_with_arg.rsplit("_", 1)
        arg_int = int(splitted[1]) # should fail here if last part of _ is not an argument like: wcdma_n_aset_cells
        #print("note: detected int after last _ in elm_name, resetting elm_name to parts before last _ as:", splitted[0])
        elm_name = splitted[0]
        arg = int(splitted[1])
    except:
        pass

    if return_arg_too:
        return elm_name, arg
    
    return elm_name



def get_azqml_elm_df_from_param_col(param_col_with_arg, just_check_if_exists=False, drop_ts_dup=False):


    elm_type = "double"
    elm_id = None
    arg = 1
    elm_name, arg = get_elm_name_from_param_col_with_arg(param_col_with_arg, return_arg_too=True)
    

    dprint("get_azqml_elm_df_from_param_col: elm_name:",elm_name,"arg",arg)

    # now get elm_id
    elm_df = get_elm_df_from_csv()
    matched_rows = elm_df.query("var_name == '{}'".format(elm_name))
    dprint("match for elm_name result nrows:",len(matched_rows))
    if len(matched_rows) == 0:
        estr = "ABORT: can't get matching row for elm_name:", elm_name
        raise Exception(estr)

    row = matched_rows.iloc[0]
    elm_id = row["id"]
    try:
        elm_id = int(elm_id)
    except:
        pass
    row.var_type = row.var_type.strip().lower()
    dprint("precheck row.var_type:",row.var_type)
    if row.var_type == "integer":
        row.var_type = "int"
    elm_type = row.var_type
    dprint("postcheck row.var_type:",row.var_type)

    if is_param_from_azqdata_dat(param_col_with_arg):
        return None # TODO get_azqdata_dat_df().query("...")

    dprint("pre-get_azqml_elm_df: elm_id:",elm_id,"elm_type:",elm_type)
    ret = get_azqml_elm_df(elm_id, elm_type, arg, val_col_name = param_col_with_arg, just_check_if_exists = just_check_if_exists)

    print(("get_azqml_elm_df len:", len(ret)))
    
    if drop_ts_dup:
        ret.drop_duplicates("ts", keep='last', inplace=True)

    #ret["time"]
    """
    if not ret is None and isinstance(ret, bool):
        print "var dtype in df:", ret[param_col_with_arg].dtype
    """
    # TODO: read_csv force type in read_csv - this crashes na case if (not ret is None) and row.var_type == "int":  ret[param_col_with_arg] = ret[param_col_with_arg].astype(int)
    #print "ret col names:",ret.columns



    return ret
    

def get_azqml_elm_df_from_param_col_ts_secs_as_pos_id(param_col_with_arg):
    global TIME_TO_POSID_DIV
    global g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache

    if param_col_with_arg in g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache:
        print("get_azqml_elm_df_from_param_col_ts_secs_as_pos_id() param_col_with_arg:", param_col_with_arg, " - return cached df")
        return g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache[param_col_with_arg]

    print("get_azqml_elm_df_from_param_col_ts_secs_as_pos_id() param_col_with_arg:", param_col_with_arg, " - retrieve df")
    
    ret_df = get_azqml_elm_df_from_param_col(param_col_with_arg)
    if ret_df is None:
        g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache[param_col_with_arg] = None
        return None
    
    print("adj cols and make posid - ori ret_df len", len(ret_df))

    del ret_df["type"]
    ret_df.ts = ret_df.ts / TIME_TO_POSID_DIV
    ret_df.ts = ret_df.ts.astype(int)
    ret_df["posid"] = ret_df.ts
    del ret_df["ts"]
    print("adj cols and make posid... done - ret the df now - len", len(ret_df))
    g_azqml_elm_df_from_param_col_ts_secs_as_pos_id_cache[param_col_with_arg] = ret_df
    return ret_df


def get_azqml_elm_df_ts_secs_as_posid(elm_id, elm_type, arg=1):
    global TIME_TO_POSID_DIV
    
    ret_df = get_azqml_elm_df(elm_id, elm_type, arg)
    if ret_df is None:
        return None
    
    print("adj cols and make posid")
    del ret_df["type"]
    ret_df.ts = ret_df.ts / TIME_TO_POSID_DIV
    ret_df.ts = ret_df.ts.astype(int)
    ret_df.columns = ["posid","id","val","arg"]
    print("adj cols and make posid... done - ret the df now")
    return ret_df


def merge_files_into(fp_merged, files):

    print("merge_files_into: ori files list len:", len(files))
    valid_files = []
    for f in files:
        if os.path.exists(f):
            valid_files.append(f)
        else:
            print("merge_files_into: omit non-existing file: ", f)
    print("merge_files_into: valid (exists) files len:", len(valid_files))

    if len(valid_files) == 0:
        raise Exception("merge_files_into: ABORT - no valid files to merge...")
    
    files = valid_files
    
    cmd = ""

    shell_mode = True

    try:
        os.remove(fp_merged)
    except:
        pass
    
    if os.name == 'posix':
        cmd += "cat"
    elif os.name == 'nt':
        # getting the windows command line length limit: The command line is too long. - use direct call to "copy" instead
        shell_mode = False
        cmd = ["cmd.exe","/c"]
        cmd.append("copy")
        cmd.append("/b")

    print("merge_files_into: shell_mode:", shell_mode)
    
    first = True
    for f in files:
        if first:
            first = False
        else:
            if os.name == 'nt':
                cmd.append("+")
                
        if shell_mode:
            cmd += ' "'+f+'"'
        else:
            cmd.append(f)


    if os.name == 'posix':
        cmd += " >"

    if shell_mode:
        cmd += ' "'+str(fp_merged)+'"'
    else:
        cmd.append(fp_merged)
        
    print("merge_files_into: cmd: ", cmd)
    ret = subprocess.call(cmd, shell=shell_mode)
    print("merge_files_into: ret: ", ret)

    if ret != 0:
        print("ret not 0 - try alternate py merge method instead...")
        with open(fp_merged, "wb") as merged_file:
            print("alt merge_file: opened target:", fp_merged)
            for f in files:
                try:
                    with open(f, "rb") as part_file:
                        print("alt merge_file: writing part:", f)
                        merged_file.write(part_file.read())
                except Exception as e:
                    print("WARNING: merge file exception likely invalid azm: "+f+" exception: "+str(e))
        ret = 0
        print("alt merge_files_into: ret: ", ret)

    if ret != 0:
        raise Exception("merge_files_into exception: ret "+str(ret)+" for merge_files_into: cmd: " + str(cmd))
    
    return ret


def copy_file(f, t):
    cmd = ""
    if os.name == 'posix':
        cmd += "cp"
    elif os.name == 'nt':
        cmd += "copy /b"

    cmd += ' "'+f+'" "'+t+'"'
    print("copy file cmd:"+cmd)
    ret = subprocess.call(cmd, shell=True)
    print("ret",ret)
    if ret != 0:
        raise Exception("ABORT: failed to copy file ret: "+str(ret))


def zip_files_into(target_zip_fp, files):
    print("zipping files {} into: {}".format(files, target_zip_fp))
    try:
        os.makedirs(os.path.dirname(target_zip_fp))
    except:
        pass

    try:
        os.remove(target_zip_fp)
    except:
        pass
    zf = zipfile.ZipFile(target_zip_fp, 'w', zipfile.ZIP_DEFLATED, allowZip64=True)
    for f in files:
        zf.write(f, os.path.basename(f))
    zf.close()
    print("zipping files done - saved at:", target_zip_fp)

    
def extract_entry_from_zip(zip_fp, entry_name, target_folder, try_7za_first=False):

    try:
        os.remove(os.path.join(target_folder, entry_name))
    except:
        pass

    print("target_folder isdir:", os.path.isdir(target_folder))
    
    if try_7za_first:
        # requires 7zip v16.02 - can recover badly damaged azm/zip cases well
        unzip_cmd = '7za e "{}" "{}" -y -o"{}"'.format(zip_fp, entry_name, target_folder)
        print("unzip_cmd:", unzip_cmd)
        ret = subprocess.call(unzip_cmd, shell=True)
        newfp = os.path.join(target_folder, entry_name)
        print("extract_entry_from_zip native: ret {} - checking if entry exists".format(ret))
        if os.path.isfile(newfp) and os.stat(newfp).st_size > 0:
            print("extract_entry_from_zip native: ret {} size {} - file exist and size > 0 so don't raise exception - can help in corrupted azm".format(ret, os.stat(newfp).st_size))
            return ret
        print("extract_entry_from_zip native: ret {} - file doesnt exist or size is 0 - try py unzip this entry instead".format(ret))

    print("extract_entry_from_zip py: start")
    # below is py unzip code - would raise exception on failure
    with zipfile.ZipFile(zip_fp,'r') as zf:
        zf.extract(entry_name, target_folder) 


def apk_verstr_to_ver_int(ver):
    ver = ver.replace("v","")
    ver = ver.replace(".","")
    print("apk_verstr_to_ver_int ver str:", ver)
    ver = int(ver)
    ret = ver
    return ret


def get_azqdata_dat_apk_ver(ret_ori_str=False):
    global g_datfile

    try:
        first_line = get_azqdata_dat_first_line()
        # example: 1488181012233,2,AndroidLogStart,v3.0.602,2.0.7:15,28800000
        verstr = first_line.split(",")[3].strip()
        if ret_ori_str:
            return verstr
        ret = apk_verstr_to_ver_int(verstr)
        return ret
    except Exception as ve:
        print("WARNING: get_azqdata_dat_apk_ver failed probably no azqdata.dat: try get from db if exists next - exception:", ve)
        db_path = os.path.join(get_tmp_process_dir(), "azqdata.db")
        if not os.path.isfile(db_path):
            raise ve
        else:
            with sqlite3.connect(db_path) as dbcon:
                return get_sqlite_apk_ver(dbcon)
            
    raise Exception("invalid state")



def get_azqdata_dat_first_line(contains=",2,AndroidLogStart,"):
    global g_datfile
    
    with open(g_datfile, 'rb') as f:
        for i in range(100):
            first_line = f.readline()

            # when EOF, readline() would return an empty string
            if first_line == "": 
                break
            
            # handle recov log cases where first line is not AndroidLogStart...
            if contains in first_line:
                return first_line
            
    print("WARNING: get_azqdata_dat_first_line(): failed to read {} line from azqdata.dat - returning None".format(contains))    
    return None


def get_azqdata_dat_phone_model():
    global g_datfile

    # 1533876818066,1,206,MI MAX 2,1
    first_line = get_azqdata_dat_first_line(contains=",1,206,")
    
    model = first_line.split(",")[3].strip()
    return model


def is_model_uses_os_timestamp_sip():
    model = get_azqdata_dat_phone_model()
    if model and model.startswith("SM-") or model.startswith("LG"):
        return True
    return False


def get_azqdata_dat_log_start_ts():
    global g_datfile

    first_line = get_azqdata_dat_first_line()
    start_ts = first_line.split(",")[0].strip()    
    return start_ts


def get_azqdata_dat_log_edition():
    global g_datfile

    # AIS: 1535932551643,1,237,2,1
    line = get_azqdata_dat_first_line(contains=",1,237,")
    part = line.split(",")[3].strip()
    ed = 99  # default edition
    try:
        ed = int(part)
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: get_azqdata_dat_log_edition() exception:", exstr)

    return ed


def is_azm_process_mode():
    return 'azm_file' in get_g_args() and get_g_args()['azm_file'].endswith(".azm")


def get_azm_file():
    if 'azm_file' in get_g_args() and get_g_args()['azm_file'].endswith(".azm"):
        return get_g_args()['azm_file']
    

def is_azm_file_indoor():
    return is_zipfile_contains_file_named(get_g_args()['azm_file'], "map.jpg")


def is_zipfile_contains_file_named(zfp, file_name):
    zf = zipfile.ZipFile(zfp, 'r')
    found = False
    with zf:
        for zit in zf.infolist():
            if file_name == zit.filename:
                found = True
    return found


def get_zipfile_entry_list(zfp):
    zf = zipfile.ZipFile(zfp, 'r')
    ret = []
    
    with zf:
        for zit in zf.infolist():
            ret.append(zit.filename)
            
    return ret

# merge using log_hash/time
def merge_lat_lon_into_df(dbcon, df, merge_by="log_hash", is_indoor=False, within_millis_of_gps=30*1000, asof_lat_lon_direction="nearest"):
    df["time"] = pd.to_datetime(df["time"])
    df["log_hash"] = df["log_hash"].astype(np.int64)
    df = df.sort_values("time")
    if debug_file_flag:
        df.to_csv('tmp/merge_lat_lon_into_df_df.csv', quoting=csv.QUOTE_ALL)
    
    location_df = get_dbcon_location_df(dbcon, is_indoor=is_indoor)
    location_df = location_df[["log_hash", "time", "positioning_lat", "positioning_lon"]]
    location_df["time"] = pd.to_datetime(location_df["time"])
    location_df["log_hash"] = location_df["log_hash"].astype(np.int64)
    location_df = location_df.sort_values("time")
    if debug_file_flag:
        location_df.to_csv('tmp/merge_lat_lon_into_df_location_df.csv', quoting=csv.QUOTE_ALL)


    if is_using_time_cloned_location_df():
        # if gps clone so merge by time only - not log_hash
        merge_by = None
    df = pd.merge_asof(df, location_df, on="time", by=merge_by, direction=asof_lat_lon_direction, allow_exact_matches=True, tolerance=pd.Timedelta('{}ms'.format(within_millis_of_gps)))
    if debug_file_flag:        
        df.to_csv('tmp/merge_lat_lon_into_df_merged_df.csv', quoting=csv.QUOTE_ALL)

    if "log_hash" not in df.columns and "log_hash_x" in df.columns:
        df["log_hash"] = df["log_hash_x"]
    
    return df


def get_azqdata_dat_first_azqml_flow_ts():
    ret = None
    try:
        dat_df = get_azqdata_dat_df(dont_filter_time=True)
        dat_df = do_azm_ts_convert_df(dat_df, keep_ts=True, set_time_as_index=False)        
        azqml_update_df = dat_df.query("type == '2' and id == '100'")
        azqml_update_df = azqml_update_df[azqml_update_df['info'].str.contains('dtInfo.azqmlFileSize ')]
        azqml_update_df['azqml_size'] = azqml_update_df['info'].str.extract('dtInfo.azqmlFileSize (\d+)', expand=False)
        azqml_update_df['azqml_size'] = pd.to_numeric(azqml_update_df['azqml_size'])
        azqml_update_df = azqml_update_df.query('azqml_size > 0').sort_values('azqml_size')
        print("azqml_update_df head:", azqml_update_df.head())

        if len(azqml_update_df) == 0:
            print("len(azqml_update_df) == 0 case so set start flow ts as +15 secs from start")
            ret = dat_df.iloc[0].time + np.timedelta64(15, 's')
        else:            
            ret = azqml_update_df.iloc[0].time
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: get_azqdata_dat_first_azqml_flow_ts() exception:", exstr)
        
    return ret


def get_azqdata_max_sip_and_qmdl_flush_ts_diff_millis():
    ret = None
    try:
        dat_df = get_azqdata_dat_df(dont_filter_time=True)
        dat_df = do_azm_ts_convert_df(dat_df, keep_ts=True, set_time_as_index=False)

        dat_df_azqml_update_and_sip = dat_df.query("(type == '2' and id == '100') or (type == '13' and id == '40001')").copy()
        dat_df_azqml_update_and_sip["prev_id"] = dat_df_azqml_update_and_sip["id"].shift(1)
        dat_df_azqml_update_and_sip["tdiff_millis"] = (dat_df_azqml_update_and_sip.time - dat_df_azqml_update_and_sip.time.shift(1)) / np.timedelta64(1,'ms')
        dat_df_azqml_update_and_sip["tdiff_millis_abs"] = dat_df_azqml_update_and_sip["tdiff_millis"].abs()
                
        # take only rows where it is sip (we want to see diff from prev non-sip row)
        dat_df_azqml_update_and_sip = dat_df_azqml_update_and_sip.query("(type == '13' and id == '40001') and (prev_id == '100')")


        # sort for highest abs val then return the tdiff non abs of that row
        dat_df_azqml_update_and_sip = dat_df_azqml_update_and_sip.sort_values("tdiff_millis_abs", ascending=False)
        ret = dat_df_azqml_update_and_sip.iloc[0].tdiff_millis

        #dat_df_azqml_update_and_sip.to_csv("tmp/dat_df_azqml_update_and_sip.csv")
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: get_azqdata_max_sip_and_qmdl_flush_ts_diff_millis() exception:", exstr)        
    return ret

    

