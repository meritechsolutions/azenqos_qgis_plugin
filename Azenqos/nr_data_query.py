import params_disp_df
NR_DATA_PARAMS_SQL_LIST = [
    '''select data_trafficstat_dl_mbps as 'DL APP TP (MBps)' from android_info_1sec''',
    '''select nr_pdcp_dl_tp_mbps as 'DL NR PDCP TP (MBps)' from nr_pdcp_throughput''',
    '''select nr_rlc_dl_tp_mbps as 'DL NR RLC TP (MBps)' from nr_deb_stat''',
    '''select nr_mac_tp_dl_mbps_1 as 'DL NR MAC TP (MBps)' from nr_mac_throughput''',
    '''select nr_p_plus_scell_nr_pdsch_tput_mbps as 'DL NR PDSCH TP (MBps)' from nr_throughput''',
    '''select lte_l1_dl_throughput_all_carriers_mbps as 'DL LTE PDSCH TP (MBps)' from lte_l1_dl_tp''',
    '''select data_trafficstat_ul_mbps as 'UL APP TP (MBps)' from android_info_1sec''',
    '''select lte_l1_ul_throughput_all_carriers_mbps_1 as 'UL LTE L1 TP (MBps)' from lte_l1_ul_tp''',
    '''select nr_p_plus_scell_nr_pusch_tput_mbps as 'UL NR PDSCH TP (MBps)' from nr_throughput''',
    '''select nr_cqi as 'NR CQI' from nr_deb_stat''',
    '''select nr_dl_rb_1 as 'NR DL RB' from nr_cell_meas''',
    '''select nr_pdsch_assign_num_1 as 'NR DL Assign count' from nr_cell_meas''',
    '''select nr_pdcch_dl_grant_percent_avg_1 as 'NR DL Grant util %' from nr_pdcch_stat''',
    '''select nr_dl_mcs_mode_1 as 'NR DL MCS' from nr_cell_meas''',
    '''select nr_dl_bler as 'NR DL BLER' from nr_deb_stat''',
    '''select nr_ul_rb_1 as 'NR UL RB' from nr_ul_rb''',
    '''select nr_pusch_assign_num_1 as 'NR UL Assign count' from nr_cell_meas''',
    '''select nr_pdcch_ul_grant_percent_avg_1 as 'NR UL Grant util %' from nr_pdcch_stat''',
    '''select nr_ul_mcs_mode_1 as 'NR UL MCS' from nr_cell_meas''',
    '''select nr_qpsk_1 as 'NR DL Mod QPSK %',nr_16qam_1 as 'NR DL Mod 16QAM %',nr_64qam_1 as 'NR DL Mod 64QAM %',nr_256qam_1 as 'NR DL Mod 256QAM %',nr_1024qam_1 as 'NR DL Mod 1024QAM %' from nr_pdsch_stat''',
    '''select nr_dl_modulation_order_1 as 'NR DL Modulation' from nr_pdsch_stat''',
    '''select nr_ul_modulation_order as 'NR UL Modulation' from nr_pusch_status''',
    '''select nr_wb_pmi_i1_1_1 as 'NR PMI I1 1',nr_wb_pmi_i1_2_1 as 'NR PMI I1 2',nr_wb_pmi_i1_3_1 as 'NR PMI I1 3',nr_wb_pmi_i2_1 as 'NR PMI I2' from nr_csi_report'''
]

def get_nr_data_params_disp_df(dbcon, time_before):
    parameter_to_columns_list = [
        (
            [
                "DL APP TP (MBps)",
            ],
            [
                "data_trafficstat_dl_mbps",
            ],
            "android_info_1sec",
        ),
        (
            [
                "DL NR PDCP TP (MBps)",
            ],
            [
                "nr_pdcp_dl_tp_mbps",
            ],
            "nr_pdcp_throughput",
        ),
        (
            [
                "DL NR RLC TP (MBps)",
            ],
            [
                "nr_rlc_dl_tp_mbps",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "DL NR MAC TP (MBps)",
            ],
            [
                "nr_mac_tp_dl_mbps_1",
            ],
            "nr_mac_throughput",
        ),
        (
            [
                "DL NR PDSCH TP (MBps)",
            ],
            [
                "nr_p_plus_scell_nr_pdsch_tput_mbps",
            ],
            "nr_throughput",
        ),
        (
            [
                "DL LTE PDSCH TP (MBps)",
            ],
            [
                "lte_l1_dl_throughput_all_carriers_mbps",
            ],
            "lte_l1_dl_tp",
        ),
        (
            [
                "UL APP TP (MBps)",
            ],
            [
                "data_trafficstat_ul_mbps",
            ],
            "android_info_1sec",
        ),
        (
            [
                "UL LTE L1 TP (MBps)",
            ],
            [
                "lte_l1_ul_throughput_all_carriers_mbps_1",
            ],
            "lte_l1_ul_tp",
        ),
        (
            [
                "UL NR PDSCH TP (MBps)",
            ],
            [
                "nr_p_plus_scell_nr_pusch_tput_mbps",
            ],
            "nr_throughput",
        ),
        (
            [
                "NR CQI",
            ],
            [
                "nr_cqi",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "NR DL RB",
            ],
            [
                "nr_dl_rb_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR DL Assign count",
            ],
            [
                "nr_pdsch_assign_num_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR DL Grant util %",
            ],
            [
                "nr_pdcch_dl_grant_percent_avg_1",
            ],
            "nr_pdcch_stat",
        ),
        (
            [
                "NR DL MCS",
            ],
            [
                "nr_dl_mcs_mode_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR DL BLER",
            ],
            [
                "nr_dl_bler",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "NR UL RB",
            ],
            [
                "nr_ul_rb_1",
            ],
            "nr_ul_rb",
        ),
        (
            [
                "NR UL Assign count",
            ],
            [
                "nr_pusch_assign_num_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR UL Grant util %",
            ],
            [
                "nr_pdcch_ul_grant_percent_avg_1",
            ],
            "nr_pdcch_stat",
        ),
        (
            [
                "NR UL MCS",
            ],
            [
                "nr_ul_mcs_mode_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR DL Mod QPSK %",
                "NR DL Mod 16QAM %",
                "NR DL Mod 64QAM %",
                "NR DL Mod 256QAM %",
                "NR DL Mod 1024QAM %",
            ],
            [
                "nr_qpsk_1",
                "nr_16qam_1",
                "nr_64qam_1",
                "nr_256qam_1",
                "nr_1024qam_1",
            ],
            "nr_pdsch_stat",
        ),
        (
            [
                "NR DL Modulation",
            ],
            [
                "nr_dl_modulation_order_1",
            ],
            "nr_pdsch_stat",
        ),
        (
            [
                "NR UL Modulation",
            ],
            [
                "nr_ul_modulation_order",
            ],
            "nr_pusch_status",
        ),
        (
            [
                "NR PMI I1 1",
                "NR PMI I1 2",
                "NR PMI I1 3",
                "NR PMI I2",
            ],
            [
                "nr_wb_pmi_i1_1_1",
                "nr_wb_pmi_i1_2_1",
                "nr_wb_pmi_i1_3_1",
                "nr_wb_pmi_i2_1",
            ],
            "nr_csi_report",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
