import pandas as pd
import numpy as np

def get_logs_info_df(dbcon, time_before):
    sqlstr = "select log_hash, time, max(script_name) as script_name, max(script)as script, max(phonemodel) as phonemodel, max(imsi) as imsi, max(imei) as imei from log_info group by log_hash"
    df = pd.read_sql(
        sqlstr,
        dbcon,
        parse_dates=["time"]
    )
    df["log_hash"] = df["log_hash"].astype(np.int64)
    return df

def get_logs_df(dbcon, time_before):
    sqlstr = "select log_hash, time, log_start_time, log_end_time, log_tag, log_ori_file_name, log_app_version, log_license_edition, log_required_pc_version, log_timezone_offset from logs group by log_hash"
    df = pd.read_sql(
        sqlstr,
        dbcon,
        parse_dates=["time"]
    )
    df["log_hash"] = df["log_hash"].astype(np.int64)
    return df

