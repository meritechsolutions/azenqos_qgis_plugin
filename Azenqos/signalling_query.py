import pandas as pd
import sys
import traceback
import numpy as np


def get_signalling(dbcon, time_before):
    L3_SQL = "SELECT log_hash, time, name, symbol as dir, protocol, detail_str FROM signalling order by time"    
    df = pd.read_sql(
        L3_SQL,
        dbcon,
        parse_dates=["time"]
    )
    df["log_hash"] = df["log_hash"].astype(np.int64)
    return df


def get_events(dbcon, time_before):
    sqls = [
        "select log_hash, time, name, info, '' as wave_file from events",
        "select log_hash, time, 'MOS Score' as name, polqa_mos as info, wav_filename as wave_file from polqa_mos"
    ]
    df_list = []
    for sql in sqls:
        try:            
            df = pd.read_sql(sql, dbcon, parse_dates=["time"])
            df_list.append(df)
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            if "no such table" in exstr or "no such column" in exstr:  # some dbs dont have polqa_mos table, some dont have polqa_output_text col...
                continue
            else:
                print("ERROR: get_events exception: %s", exstr)
                raise e
    df = pd.concat(df_list, ignore_index=True)
    df["log_hash"] = df["log_hash"].astype(np.int64)
    df = df.sort_values(by="time")
    return df

