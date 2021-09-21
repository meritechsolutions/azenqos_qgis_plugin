import pandas as pd


import params_disp_df



def get_Wifi_active_df(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"], "wifi_active"),
        (
            [
                "BSSID",
                "SSID",
                "RSSI",
                "IP Addr",
                "Link Speed (Mbps.)",
                "MAC Addr",
                "Encryption",
                "Ch.",
                "Freq",
                "ISP",
            ],
            [
                "wifi_active_bssid",
                "wifi_active_ssid",
                "wifi_active_rssi",
                "wifi_active_ipaddr",
                "wifi_active_linkspeed",
                "wifi_active_macaddr",
                "wifi_active_encryption",
                "wifi_active_channel",
                "wifi_active_freq",
                "wifi_active_isp",
            ],
            "wifi_active",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_wifi_scan_df(dbcon, time_before):
    dt_before = time_before["time"]
    sql = "select * from wifi_scanned_info where time between DATETIME('{}','-4 seconds') and '{}'".format(
        dt_before, dt_before
    )
    drop_col_list = ['log_hash','time','modem_time','posid','seqid','netid','geom']
    df = pd.read_sql(sql, dbcon)
    if len(df) == 0:
        for i in range(300):
            df = df.append(pd.Series(), ignore_index=True)
    df = df.drop(columns=drop_col_list)
    return df


def get_gprs_edge_info(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"], "umts_data_activation_stats"),
        (
            ["GPRS Attach Duration", "PDP Context Activation Duration",],
            ["data_gprs_attach_duration", "data_pdp_context_activation_duration",],
            "umts_data_activation_stats",
        ),
        (
            [
                "RLC DL Throughput (kbit/s)",
                "RLC UL Throughput (kbit/s)",
                "DL Coding Scheme",
                "UL Coding Scheme",
                "DL Timeslot Used",
                "Ul Timeslot Used",
                "GPRS C/I",
            ],
            [
                "data_gsm_rlc_ul_throughput",
                "data_gsm_rlc_dl_throughput",
                "data_egprs_dl_coding_scheme_index",
                "data_egprs_ul_coding_scheme_index",
                "data_gprs_timeslot_used_dl",
                "data_gprs_timeslot_used_ul",
                "data_gprs_ci",
            ],
            "data_egprs_stats",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_hsdpa_statistics(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"], "wcdma_hsdpa_stats"),
        (
            [
                "HSDPA Scheduled Rate",
                "HSDPA Served Rate",
                "HS-DSCH Throughput",
                "HSDPA SBLER on 1st transmission",
                "HSDPA SBLER",
                "HSDPA Num Codes Used Avg.",
                "HSDPA MOD QPSK Percent",
                "HSDPA MOD 16QAM Percent",
                "HSDPA MOD 64QAM Percent",
                "HSDPA Meas from num 2MS slots",
                "HSDPA Num SCCH DEMOD Attempts",
                "HSDPA Num DEMOD Valid",
                "Data HSPAP Dual Carrier Enabled",
                "Data HSPAP 64QAM Configured",
                "Data_HSPAP_DUAL_CARRIER_ENABLED_PERCENT",
                "Data_HSPAP_MIMO_ENABLED",
                "Data_HSPAP_UE_CATEGORY",
                "Data_HSPAP_2TB_REQUESTED_PERCENT",
                "Data_HSPAP_1TB_REQUESTED_PERCENT",
                "HSDPA HS-SCCH Usage Percent",
            ],
            [
                "data_hsdpa_scheduled_rate",
                "data_hsdpa_served_rate",
                "data_hsdpa_thoughput",
                "data_hsdpa_sbler_on_1st_transmission",
                "data_hsdpa_sbler",
                "data_hsdpa_num_codes_used_avg",
                "data_hsdpa_mod_qpsk_percent",
                "data_hsdpa_mod_16qam_percent",
                "data_hspap_mod_64qam_percent",
                "data_hsdpa_meas_from_num_2ms_slots",
                "data_hsdpa_num_scch_demod_attempts",
                "data_hsdpa_num_demod_valid",
                "data_hspap_dual_carrier_enabled",
                "data_hspap_64qam_configured",
                "data_hspap_dual_carrier_enabled_percent",
                "data_hspap_mimo_enabled",
                "data_hspap_ue_category",
                "data_hspap_2tb_requested_percent",
                "data_hspap_1tb_requested_percent",
                "data_hsdpa_hs_scch_usage_percent",
            ],
            "wcdma_hsdpa_stats",
        ),
        (
            [
                "data_hsdpa_cqi_number_avg",
                "data_hspap_cqi_b",
                "data_hspap_cqi_a",
                "data_hspap_cqi_dc_primary_carrier",
                "data_hspap_cqi_dc_secondary_carrier",
            ],
            [
                "HSDPA CQI number avg.",
                "Data HSPAP CQI B",
                "Data HSPAP CQI A",
                "Data HSPAP CQI DC Primary Carrier",
                "Data HSPAP CQI DC Secondary Carrier",
            ],
            "wcdma_hsdpa_cqi",
        ),
        (
            ["WCDMA RLC DL Throughput",],
            ["data_wcdma_rlc_dl_throughput",],
            "data_wcdma_rlc_stats",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


def get_hsupa_statistics(dbcon, time_before):
    parameter_to_columns_list = [
        ("Time", ["time"], "wcdma_hsupa_stats"),
        (
            [
                "HSUPA Sample duration",
                "HSUPA TTI",
                "HSUPA Sample frames",
                "HSUPA Happy bit TTIs (%)",
                "HSUPA Serving RGCH Up (%)",
                "HSUPA Serving RGCH Down (%)",
                "HSUPA Serving RGCH Hold (%)",
                "HSUPA NonServing RGCH Down (%)",
                "HSUPA NonServing RGCH Hold (%)",
                "HSUPA N AGCH Receive success",
                "HSUPA Average AGCH",
                "HSUPA Average SGI",
                "HSUPA new transmission (%)",
                "HSUPA retransmission (%)",
                "HSUPA DTX (%)",
                "HSUPA N NACK after max retrans",
                "HSUPA N MAC e Resets",
                "HSUPA Power Limited TTIs (%)",
                "HSUPA Serving Grant Limited TTIs (%)",
                "HSUPA SBLER (%)",
                "HSUPA Avg Raw Throughput",
                "HSUPA Avg Scheduled Throughput",
                "HSUPA Total E DPDCH Throughput",
            ],
            [
                "data_hsupa_sample_duration",
                "data_hsupa_tti",
                "data_hsupa_sample_frames",
                "data_hsupa_p_happy_bit_ttis",
                "data_hsupa_p_serving_rgch_up",
                "data_hsupa_p_serving_rgch_down",
                "data_hsupa_p_serving_rgch_hold",
                "data_hsupa_p_nonserving_rgch_down",
                "data_hsupa_p_nonserving_rgch_hold",
                "data_hsupa_n_agch_receive_success",
                "data_hsupa_average_agch",
                "data_hsupa_average_sgi",
                "data_hsupa_p_new_transmission",
                "data_hsupa_p_retransmission",
                "data_hsupa_p_dtx",
                "data_hsupa_n_nack_after_max_retrans",
                "data_hsupa_n_mac_e_resets",
                "data_hsupa_n_power_limited_ttis",
                "data_hsupa_n_serving_grant_limited_ttis",
                "data_hsupa_p_sbler",
                "data_hsupa_avg_raw_throughput",
                "data_hsupa_avg_scheduled_throughput",
                "data_hsupa_total_e_dpdch_throughput",
            ],
            "wcdma_hsupa_stats",
        ),
        (
            ["WCDMA RLC UL Throughput",],
            ["data_wcdma_rlc_ul_throughput",],
            "data_wcdma_rlc_stats",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
