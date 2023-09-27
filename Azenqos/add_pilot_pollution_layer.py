import azq_utils
import sql_utils
import db_preprocess

import pandas as pd
import os
import sqlite3
import contextlib
import qt_utils

def get_nr_pilot_pollution_df(dbcon, where, diff_range):
    sql_str = 'select log_hash, time, nr_servingbeam_ss_rsrp_1 as main, nr_band_1 as b_main, nr_servingbeam_ss_rsrp_2 as c0, nr_band_2 as b0,' \
              ' nr_servingbeam_ss_rsrp_3 as c1, nr_band_3 as b1, nr_servingbeam_ss_rsrp_4 as c2, nr_band_4 as b2, ' \
              ' nr_servingbeam_ss_rsrp_5 as c3, nr_band_5 as b3, nr_servingbeam_ss_rsrp_6 as c4, nr_band_6 as b4,' \
              ' nr_servingbeam_ss_rsrp_7 as c5, nr_band_7 as b5, nr_servingbeam_ss_rsrp_8 as c6, nr_band_8 as b6' \
              ' from nr_cell_meas where nr_servingbeam_ss_rsrp_1 is not null order by time'
    sql_str = sql_utils.add_first_where_filt(sql_str, where)
    df = pd.read_sql(sql_str, dbcon, parse_dates='time')

    beam_sql = 'select log_hash, time, nr_detectedbeam1_ss_rsrp_1 as c7, nr_detectedbeam1_dl_arfcn_1 as f7, ' \
                'nr_detectedbeam1_ss_rsrp_2 as c8, nr_detectedbeam1_dl_arfcn_2 as f8,' \
                'nr_detectedbeam1_ss_rsrp_3 as c9, nr_detectedbeam1_dl_arfcn_3 as f9,' \
                'nr_detectedbeam1_ss_rsrp_4 as c10, nr_detectedbeam1_dl_arfcn_4 as f10,' \
                'nr_detectedbeam1_ss_rsrp_5 as c11, nr_detectedbeam1_dl_arfcn_5 as f11,' \
                'nr_detectedbeam1_ss_rsrp_6 as c12, nr_detectedbeam1_dl_arfcn_6 as f12,' \
                'nr_detectedbeam1_ss_rsrp_7 as c13, nr_detectedbeam1_dl_arfcn_7 as f13,' \
                'nr_detectedbeam1_ss_rsrp_8 as c14, nr_detectedbeam1_dl_arfcn_8 as f14,' \
                '' \
                'nr_detectedbeam2_ss_rsrp_1 as c15, nr_detectedbeam2_dl_arfcn_1 as f15, ' \
                'nr_detectedbeam2_ss_rsrp_2 as c16, nr_detectedbeam2_dl_arfcn_2 as f16,' \
                'nr_detectedbeam2_ss_rsrp_3 as c17, nr_detectedbeam2_dl_arfcn_3 as f17,' \
                'nr_detectedbeam2_ss_rsrp_4 as c18, nr_detectedbeam2_dl_arfcn_4 as f18,' \
                'nr_detectedbeam2_ss_rsrp_5 as c19, nr_detectedbeam2_dl_arfcn_5 as f19,' \
                'nr_detectedbeam2_ss_rsrp_6 as c20, nr_detectedbeam2_dl_arfcn_6 as f20,' \
                'nr_detectedbeam2_ss_rsrp_7 as c21, nr_detectedbeam2_dl_arfcn_7 as f21,' \
                'nr_detectedbeam2_ss_rsrp_8 as c22, nr_detectedbeam2_dl_arfcn_8 as f22,' \
                '' \
                'nr_detectedbeam3_ss_rsrp_1 as c23, nr_detectedbeam3_dl_arfcn_1 as f23, ' \
                'nr_detectedbeam3_ss_rsrp_2 as c24, nr_detectedbeam3_dl_arfcn_2 as f24,' \
                'nr_detectedbeam3_ss_rsrp_3 as c25, nr_detectedbeam3_dl_arfcn_3 as f25,' \
                'nr_detectedbeam3_ss_rsrp_4 as c26, nr_detectedbeam3_dl_arfcn_4 as f26,' \
                'nr_detectedbeam3_ss_rsrp_5 as c27, nr_detectedbeam3_dl_arfcn_5 as f27,' \
                'nr_detectedbeam3_ss_rsrp_6 as c28, nr_detectedbeam3_dl_arfcn_6 as f28,' \
                'nr_detectedbeam3_ss_rsrp_7 as c29, nr_detectedbeam3_dl_arfcn_7 as f29,' \
                'nr_detectedbeam3_ss_rsrp_8 as c30, nr_detectedbeam3_dl_arfcn_8 as f30,' \
                '' \
                'nr_detectedbeam4_ss_rsrp_1 as c31, nr_detectedbeam4_dl_arfcn_1 as f31, ' \
                'nr_detectedbeam4_ss_rsrp_2 as c32, nr_detectedbeam4_dl_arfcn_2 as f32,' \
                'nr_detectedbeam4_ss_rsrp_3 as c33, nr_detectedbeam4_dl_arfcn_3 as f33,' \
                'nr_detectedbeam4_ss_rsrp_4 as c34, nr_detectedbeam4_dl_arfcn_4 as f34,' \
                'nr_detectedbeam4_ss_rsrp_5 as c35, nr_detectedbeam4_dl_arfcn_5 as f35,' \
                'nr_detectedbeam4_ss_rsrp_6 as c36, nr_detectedbeam4_dl_arfcn_6 as f36,' \
                'nr_detectedbeam4_ss_rsrp_7 as c37, nr_detectedbeam4_dl_arfcn_7 as f37,' \
                'nr_detectedbeam4_ss_rsrp_8 as c38, nr_detectedbeam4_dl_arfcn_8 as f38,' \
                '' \
                'nr_detectedbeam5_ss_rsrp_1 as c39, nr_detectedbeam5_dl_arfcn_1 as f39, ' \
                'nr_detectedbeam5_ss_rsrp_2 as c40, nr_detectedbeam5_dl_arfcn_2 as f40,' \
                'nr_detectedbeam5_ss_rsrp_3 as c41, nr_detectedbeam5_dl_arfcn_3 as f41,' \
                'nr_detectedbeam5_ss_rsrp_4 as c42, nr_detectedbeam5_dl_arfcn_4 as f42,' \
                'nr_detectedbeam5_ss_rsrp_5 as c43, nr_detectedbeam5_dl_arfcn_5 as f43,' \
                'nr_detectedbeam5_ss_rsrp_6 as c44, nr_detectedbeam5_dl_arfcn_6 as f44,' \
                'nr_detectedbeam5_ss_rsrp_7 as c45, nr_detectedbeam5_dl_arfcn_7 as f45,' \
                'nr_detectedbeam5_ss_rsrp_8 as c46, nr_detectedbeam5_dl_arfcn_8 as f46,' \
                '' \
                'nr_detectedbeam6_ss_rsrp_1 as c47, nr_detectedbeam6_dl_arfcn_1 as f47, ' \
                'nr_detectedbeam6_ss_rsrp_2 as c48, nr_detectedbeam6_dl_arfcn_2 as f48,' \
                'nr_detectedbeam6_ss_rsrp_3 as c49, nr_detectedbeam6_dl_arfcn_3 as f49,' \
                'nr_detectedbeam6_ss_rsrp_4 as c50, nr_detectedbeam6_dl_arfcn_4 as f50,' \
                'nr_detectedbeam6_ss_rsrp_5 as c51, nr_detectedbeam6_dl_arfcn_5 as f51,' \
                'nr_detectedbeam6_ss_rsrp_6 as c52, nr_detectedbeam6_dl_arfcn_6 as f52,' \
                'nr_detectedbeam6_ss_rsrp_7 as c53, nr_detectedbeam6_dl_arfcn_7 as f53,' \
                'nr_detectedbeam6_ss_rsrp_8 as c54, nr_detectedbeam6_dl_arfcn_8 as f54' \
                ' from nr_intra_neighbor order by time'
    beam_sql = sql_utils.add_first_where_filt(beam_sql, where)
    beam_df = pd.read_sql(beam_sql, dbcon, parse_dates='time')

    ref_df = pd.read_csv(
            os.path.join(
                azq_utils.get_module_path(),
                "nr_band_arfcn_range_proc.csv"
            )
        )
    
    for index, row in ref_df.iterrows():
        arfcn_start = row["arfcn_start"]
        arfcn_end = row["arfcn_end"]
        band = row["band_n"]
    
        for i in range(7,55):
            beam_df.loc[(beam_df["f{}".format(i)] >= arfcn_start) & (beam_df['f{}'.format(i)] <= arfcn_end), "b{}".format(i)] = band

    df = pd.merge_asof(df, beam_df, on='time', by='log_hash')

    df['pilot_pollution'] = 1
    for i in range(55):
        df['main'] = df['main'].astype(float)
        df['c{}'.format(i)] = df['c{}'.format(i)].astype(float)
        df['d{}'.format(i)] = df['main'] - df['c{}'.format(i)]
        df.loc[(df['d{}'.format(i)].abs() < diff_range) & (df['b_main'].astype(float) == df['b{}'.format(i)].astype(float)), "pilot_pollution"] += 1

    df = df[['log_hash', 'time', 'pilot_pollution']]

    return df

def get_lte_pilot_pollution_df(dbcon, where, filter_freq=True, diff_range=5):
    sql_str = 'select log_hash, time, lte_inst_rsrp_1 as main, lte_band_1 as b_main, lte_earfcn_1 as f_main, lte_inst_rsrp_2 as c0, lte_band_2 as b0, lte_earfcn_2 as f0,' \
              ' lte_inst_rsrp_3 as c1, lte_band_3 as b1, lte_earfcn_3 as f1, lte_inst_rsrp_4 as c2, lte_band_4 as b2, lte_earfcn_4 as f2 from lte_cell_meas where lte_inst_rsrp_1 is not null order by time'
    sql_str = sql_utils.add_first_where_filt(sql_str, where)
    df = pd.read_sql(sql_str, dbcon, parse_dates='time')

    neigh_sql = 'select log_hash, time, lte_neigh_rsrp_1 as c3, lte_neigh_earfcn_1 as f3, lte_neigh_rsrp_2 as c4, lte_neigh_earfcn_2 as f4,' \
                ' lte_neigh_rsrp_3 as c5, lte_neigh_earfcn_3 as f5, lte_neigh_rsrp_4 as c6, lte_neigh_earfcn_4 as f6, lte_neigh_rsrp_5 as c7, lte_neigh_earfcn_5 as f7,' \
                ' lte_neigh_rsrp_6 as c8, lte_neigh_earfcn_6 as f8, lte_neigh_rsrp_7 as c9, lte_neigh_earfcn_7 as f9, lte_neigh_rsrp_8 as c10, lte_neigh_earfcn_8 as f10,' \
                ' lte_neigh_rsrp_9 as c11, lte_neigh_earfcn_9 as f11, lte_neigh_rsrp_10 as c12, lte_neigh_earfcn_10 as f12, lte_neigh_rsrp_11 as c13, lte_neigh_earfcn_11 as f13,' \
                ' lte_neigh_rsrp_12 as c14, lte_neigh_earfcn_12 as f14, lte_neigh_rsrp_13 as c15, lte_neigh_earfcn_13 as f15, lte_neigh_rsrp_14 as c16, lte_neigh_earfcn_14 as f16,' \
                ' lte_neigh_rsrp_15 as c17, lte_neigh_earfcn_15 as f17, lte_neigh_rsrp_16 as c18, lte_neigh_earfcn_16 as f18 from lte_neigh_meas order by time'
    neigh_sql = sql_utils.add_first_where_filt(neigh_sql, where)
    neigh_df = pd.read_sql(neigh_sql, dbcon, parse_dates='time')
    ref_df = pd.read_csv(
            os.path.join(
                azq_utils.get_module_path(),
                "lte_band_freq_earfcn_3gpp_36_101.csv"
            )
        )
    
    for index, row in ref_df.iterrows():
        earfcn_start = row["earfcn_start"]
        earfcn_end = row["earfcn_end"]
        band = row["band"]
        for i in range(3, 19):
            neigh_df.loc[(neigh_df["f{}".format(i)] >= earfcn_start) & (neigh_df['f{}'.format(i)] <= earfcn_end), "b{}".format(i)] = band

    df = pd.merge_asof(df, neigh_df, on='time', by='log_hash')

    df['pilot_pollution'] = 1
    for i in range(18):
        df['d{}'.format(i)] = df['main'] - df['c{}'.format(i)]
        if filter_freq:
            df.loc[(df['d{}'.format(i)].abs() < diff_range) & (df['f_main'] == df['f{}'.format(i)]), "pilot_pollution"] += 1
        else:
            df.loc[(df['d{}'.format(i)].abs() < diff_range) & (df['b_main'] == df['b{}'.format(i)]), "pilot_pollution"] += 1

    df = df[['log_hash', 'time', 'pilot_pollution']]

    return df



def get_wcdma_pilot_pollution_df(dbcon, where, diff_range):
    sql_str = 'select log_hash, time, wcdma_aset_rscp_1 as main, wcdma_aset_rscp_2 as c0, wcdma_aset_rscp_3 as c1, wcdma_mset_rscp_1 as c2,' \
              ' wcdma_mset_rscp_2 as c3, wcdma_mset_rscp_3 as c4, wcdma_mset_rscp_4 as c5, wcdma_mset_rscp_5 as c6,' \
              ' wcdma_mset_rscp_6 as c7, wcdma_mset_rscp_7 as c8, wcdma_mset_rscp_8 as c9, wcdma_mset_rscp_9 as c10,' \
              ' wcdma_mset_rscp_10 as c11, wcdma_mset_rscp_11 as c12, wcdma_mset_rscp_12 as c13, wcdma_mset_rscp_13 as c14,' \
              ' wcdma_mset_rscp_14 as c15, wcdma_mset_rscp_15 as c16, wcdma_mset_rscp_16 as c17 from wcdma_cell_meas'
    sql_str = sql_utils.add_first_where_filt(sql_str, where)
    df = pd.read_sql(sql_str, dbcon, parse_dates='time')
    df['pilot_pollution'] = 1
    for i in range(18):
        df['d{}'.format(i)] = df['main'] - df['c{}'.format(i)]
        df.loc[ df['d{}'.format(i)].abs() < diff_range, "pilot_pollution"] +=1

    df = df[['log_hash', 'time', 'pilot_pollution']]

    return df


def add_layer(databasePath, technology, selected_ue=None, filter_freq=True, diff_range=5, is_indoor=False, device_configs=None, show_msg_box=True):
    
    with contextlib.closing(sqlite3.connect(databasePath)) as dbcon:
        technology = technology.lower()
        theme_param = "pilot_pollution"
        layer_name = technology+"_"+theme_param
        if not filter_freq:
            layer_name = layer_name+"_all_frequency"
        df = None
        where = ""
        
        if selected_ue is not None:
            title_ue_suffix = "(" + device_configs[selected_ue]["name"] + ")"
            if title_ue_suffix not in layer_name:
                layer_name = layer_name + title_ue_suffix 
                selected_logs = device_configs[selected_ue]["log_hash"]
                where = "where log_hash in ({})".format(','.join([str(selected_log) for selected_log in selected_logs]))

        if technology == "nr":
            df = get_nr_pilot_pollution_df(dbcon, where, diff_range)
        elif technology == "lte":
            df = get_lte_pilot_pollution_df(dbcon, where, filter_freq, diff_range)
        elif technology == "wcdma":
            df = get_wcdma_pilot_pollution_df(dbcon, where, diff_range)

        if df is not None and len(df) > 0:
            location_sqlstr = "select time, log_hash, positioning_lat, positioning_lon from location where positioning_lat is not null and positioning_lon is not null"
            location_sqlstr = sql_utils.add_first_where_filt(location_sqlstr, where)
            df_location = pd.read_sql(location_sqlstr, dbcon, parse_dates=['time'])
            if is_indoor:
                df = db_preprocess.add_pos_lat_lon_to_indoor_df(df, df_location).rename(
                columns={"positioning_lat": "lat", "positioning_lon": "lon"}).reset_index(drop=True)
                if "geom" in df.columns:
                    del df["geom"]
            azq_utils.create_layer_in_qgis(databasePath, df, layer_name=layer_name, theme_param=theme_param, data_df=df)
            if show_msg_box:
                qt_utils.msgbox("Add pilot pollution success", title="Info")
        else:
            if show_msg_box:
                qt_utils.msgbox("No pilot pollution detected", title="Info")