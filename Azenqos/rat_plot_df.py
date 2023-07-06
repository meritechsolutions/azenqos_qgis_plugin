import pandas as pd
import sys
import traceback
import azq_utils
import sql_utils


def get(dbcon, where = "", drop_dup=True, nr_ffill_limit=10):

    # get point where RAT has changed and log_hash is same

    rat_to_table_and_primary_where_dict = {
        "GSM":"gsm_cell_meas",# where gsm_rxlev_sub_dbm is not null",
        "LTE":"lte_cell_meas",# where lte_inst_rsrp_1 is not null",
        "NR":"nr_cell_meas",# nr_servingbeam_ss_rsrp_1 is not null",
        "WCDMA":"wcdma_cell_meas",# where wcdma_aset_ecio_1 is not null",        
    }

    rat_to_main_param_dict = {
        "GSM":"gsm_rxlev_sub_dbm",
        "LTE":"lte_inst_rsrp_1",
        "NR":"nr_servingbeam_ss_rsrp_1",
        "WCDMA":"wcdma_aset_ecio_1",
    }


    per_rat_df_list = []
    
    for rat in rat_to_table_and_primary_where_dict:
        try:
            sqlstr = "select log_hash, time, {} as main_param from {}".format(rat_to_main_param_dict[rat], rat_to_table_and_primary_where_dict[rat])
            sqlstr = sql_utils.add_first_where_filt(sqlstr, where)
            df = pd.read_sql(sqlstr, dbcon, parse_dates=["time"])

            df["rat"] = rat        
            if rat == 'NR':
                df_copy = df.copy()
                df_copy = df_copy.dropna(subset=["main_param"])
                df_merge = pd.merge_asof(left=df.sort_values(by="time").reset_index(drop=True), right=df_copy.sort_values(by="time").reset_index(drop=True), left_on=['time'], right_on=['time'],by='log_hash',direction="backward", allow_exact_matches=True, tolerance=pd.Timedelta('10s'), suffixes=('_not_use', '')) 
                cols = [c for c in df_merge.columns if c.lower()[-7:] != 'not_use']
                df=df_merge[cols]
                df = df.ffill(limit=nr_ffill_limit) # To handle many duplicate nulls in nr_cell_meas table
            if len(df) > 0:
                per_rat_df_list.append(df)

        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("WARNING: gen per_rat_df failed exception:", exstr)

    if len(per_rat_df_list) == 0:
        return None

    df = pd.concat(per_rat_df_list, ignore_index=True)
    # handle nr and lte at same time use nr (endc)
    df = df.sort_values(["log_hash", "time", "rat"]).reset_index(drop=True)
    df = set_rat_to_nr_if_prev_were_near_nr(df)
    df = azq_utils.df_log_hash_time_resample(df, "1000ms")
    df = set_rat_to_nr_if_prev_were_near_nr(df)
    df = df[~pd.isnull(df.main_param)]
    df = df[["log_hash", "time", "rat"]]
    if drop_dup:
        df.drop_duplicates(["log_hash", "time"], keep='last', inplace=True) # so NR would be on top of lte

    return df


def set_rat_to_nr_if_prev_were_near_nr(df, lookback_n_rows=4):
    prev_rat_nr_mask = [False] * len(df)
    for i in range(lookback_n_rows):
        prev_rat_nr_mask |= (df.rat.shift(i+1)  == "NR")
    df.loc[prev_rat_nr_mask, "rat"] = "NR"
    if "rat_band" in df.columns:
        df.loc[prev_rat_nr_mask, "rat_band"] = "NR"
        df.loc[df.rat_band.str.startswith("NR"), "rat_band"] = "NR"
    return df