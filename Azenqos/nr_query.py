import pandas as pd

import params_disp_df
import preprocess_azm


################################## df get functions

def get_nr_radio_params_disp_df(dbcon, time_before):
    if preprocess_azm.is_leg_nr_tables():
        parameter_to_columns_list = get_nr_radio_params_list_old()
    else:
        parameter_to_columns_list = get_nr_radio_params_list()

    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )

def get_nr_radio_params_list():
    params_list = [
        (
            [
                "---- PCell ----",
                "NR DL FREQ",
                "NR ARFCN",
            ],
            [
                '"" as unused1',
                "nr_dl_frequency_1",
                "nr_dl_arfcn_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR Band",
                "NR PCI",
                "NR SSB Index",
            ],
            [
                "nr_band_1",
                "nr_servingbeam_pci_1",
                "nr_servingbeam_ssb_index_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR SS RSRP",
                "NR SS RSRQ",
                "NR SS SINR",
            ],
            [
                "nr_servingbeam_ss_rsrp_1",
                "nr_servingbeam_ss_rsrq_1",
                "nr_servingbeam_ss_sinr_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR N Rx Ant",
            ],
            [
                "nr_num_rx_ant_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR N Tx Ant",
            ],
            [
                "nr_num_tx_ant_1",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "NR SubCarrier Size",
            ],
            [
                "nr_numerology_scs_1",
            ],
            "nr_cell_meas",
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
                "NR DL Bandwidth",
            ],
            [
                "nr_bw_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR UL RB",
            ],
            [
                "nr_ul_rb_1",
            ],
            "nr_ul_rb"
        ),
        (
            [
                "NR UL Bandwidth",
            ],
            [
                "nr_ul_bw_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "NR Num Layers",
                "   ",
            ],
            [
                "nr_numlayers_1",
                '"" as unused2',
            ],
            "nr_deb_stat"
        ),
        (
            [
                "NR DL TxMode",
                "NR UL TxMode",
            ],
            [
                "nr_pdsch_tx_mode_1",
                "nr_ul_tx_mode_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "NR ENDC Total Tx Power",
                "---- PUSCH ----",
                "NR PUSCH Tx Power",
            ],
            [
                "nr_endc_total_tx_power",
                '"" as unused3',
                "nr_pusch_tx_power_1",
            ],
            "nr_deb_stat"
        ),
        (
            [
                "NR PUSCH MTPL",
                "NR PUSCH DL Ploss",
                "NR PUSCH f(i)",
            ],
            [
                "nr_pusch_mtpl_1",
                "nr_pusch_dl_pathloss_1",
                "nr_pusch_f_i_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- PUSCH ----",
                "NR PUCCH Tx Power",
            ],
            [
                '"" as unused4',
                "nr_pucch_tx_power_1",
            ],
            "nr_deb_stat"
        ),
        (
            [
                "NR PUCCH MTPL",
                "NR PUCCH DL PLoss",
                "NR PUCCH g(i)",
            ],
            [
                "nr_pucch_mtpl_1",
                "nr_pucch_dl_pathloss_1",
                "nr_pucch_g_i_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- SRS ----",
                "NR SRX Tx Power",
            ],
            [
                '"" as unused5',
                "nr_srs_tx_power_1",
            ],
            "nr_tx_srs_status"
        ),
        (
            [
                "NR SRX MTPL",
            ],
            [
                "nr_srs_mtpl_1",
            ],
            "nr_deb_stat"
        ),
        (
            [
                "NR SRX DL PLoss",
                "NR SRX PC Adj State",
            ],
            [
                "nr_srs_dl_pathloss_1",
                "nr_srs_pc_adj_state_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- RACH ----",
                "NR PRACH Tx Power",
            ],
            [
                '"" as unused6',
                "nr_prach_tx_power",
            ],
            "nr_deb_stat"
        ),
        (
            [
                "RACH PLoss",
                "RACH Reason",
            ],
            [
                "nr_p_plus_scell_nr_rach_pathloss_1",
                "nr_p_plus_scell_nr_rach_reason_1",
            ],
            "nr_prach_status"
        ),
        (
            [
                "RACH CRNTI",
                "RACH CNType",
                "RACH AttNum",
                "RACH Result",
            ],
            [
                "nr_p_plus_scell_nr_rach_crnti",
                "nr_p_plus_scell_nr_rach_contention_type",
                "nr_p_plus_scell_nr_rach_attempt_number",
                "nr_p_plus_scell_nr_rach_result",
            ],
            "nr_rach_stat"
        ),
        (
            [
                "RACH N Success",
                "RACH N Fail",
                "RACH N Abort",
                "RACH N OthRslt",
                "RACH N 1stAttScss",
                "RACH N MltAttScss",
                "RACH N FailMsg2",
                "RACH N FailMsg4",
            ],
            [
                "nr_p_plus_scell_nr_rach_num_success",
                "nr_p_plus_scell_nr_rach_num_fail",
                "nr_p_plus_scell_nr_rach_num_abort",
                "nr_p_plus_scell_nr_rach_num_other_result",
                "nr_p_plus_scell_nr_rach_num_first_attempt_success",
                "nr_p_plus_scell_nr_rach_num_multiple_attempt_success",
                "nr_p_plus_scell_nr_rach_num_fail_msg2",
                "nr_p_plus_scell_nr_rach_num_fail_msg4",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- ReconfigWithSync params ----",
                "target_arfcn",
            ],
            [
                '"" as unused6',
                "nr_reconfigwithsync_target_arfcn",
            ],
            "nr_reconfigwithsync_params"
        ),
        (
            [
                "offset_to_carrier",
            ],
            [
                "nr_reconfigwithsync_carrier_offset_to_carrier_1",
            ],
            "nr_reconfigwithsync_params"
        ),
        (
            [
                "carrier_bandwidth_rbs",
            ],
            [
                "nr_reconfigwithsync_carrier_bandwidth_rbs_1",
            ],
            "nr_reconfigwithsync_params"
        ),
        (
            [
                "carrier_bandwidth_mhz",
            ],
            [
                "nr_reconfigwithsync_carrier_bandwidth_mhz_1",
            ],
            "nr_reconfigwithsync_params"
        ),
    ]
    return params_list

def get_nr_radio_params_list_old():
    params_list = [
        (
            [
                "---- PCell ----",
                "NR DL FREQ",
                "NR ARFCN",
                "NR Band",
                "NR PCI",
            ],
            [
                '"" as unused1',
                "nr_dl_frequency_1",
                "nr_dl_arfcn_1",
                "nr_band_1",
                "nr_servingbeam_pci_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR SS RSRP",
                "NR SS RSRQ",
                "NR SS SINR",
            ],
            [
                "nr_servingbeam_ss_rsrp_1",
                "nr_servingbeam_ss_rsrq_1",
                "nr_servingbeam_ss_sinr_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR N Rx Ant",
            ],
            [
                "nr_num_rx_ant_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR N Tx Ant",
            ],
            [
                "nr_num_tx_ant_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR SubCarrier Size",
            ],
            [
                "nr_numerology_scs_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR DL RB",
                "NR DL Bandwidth",
                "NR UL RB",
                "NR UL Bandwidth",
            ],
            [
                "nr_dl_rb_1",
                "nr_bw_1",
                "nr_ul_rb_1",
                "nr_ul_bw_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR Num Layers",
                "   ",
                "NR DL TxMode",
                "NR UL TxMode",
            ],
            [
                "nr_numlayers_1",
                '"" as unused2',
                "nr_pdsch_tx_mode_1",
                "nr_ul_tx_mode_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR ENDC Total Tx Power"
            ],
            [
                "nr_endc_total_tx_power"
            ],
            "nr_deb_stat"
        ),
        (
            [
                "---- PUSCH ----",
                "NR PUSCH Tx Power",
                "NR PUSCH MTPL",
                "NR PUSCH DL Ploss",
                "NR PUSCH f(i)",
            ],
            [
                '"" as unused3',
                "nr_pusch_tx_power_1",
                "nr_pusch_mtpl_1",
                "nr_pusch_dl_pathloss_1",
                "nr_pusch_f_i_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- PUSCH ----",
                "NR PUCCH Tx Power",
                "NR PUCCH MTPL",
                "NR PUCCH DL PLoss",
                "NR PUCCH g(i)",
            ],
            [
                '"" as unused4',
                "nr_pucch_tx_power_1",
                "nr_pucch_mtpl_1",
                "nr_pucch_dl_pathloss_1",
                "nr_pucch_g_i_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- SRS ----",
                "NR SRX Tx Power",
                "NR SRX MTPL",
                "NR SRX DL PLoss",
                "NR SRX PC Adj State",
            ],
            [
                '"" as unused5',
                "nr_srs_tx_power_1",
                "nr_srs_mtpl_1",
                "nr_srs_dl_pathloss_1",
                "nr_srs_pc_adj_state_1",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- RACH ----",
                "NR PRACH Tx Power",
            ],
            [
                '"" as unused6',
                "nr_prach_tx_power",
            ],
            "nr_deb_stat"
        ),
        (
            [
                "RACH PLoss",
                "RACH Reason",
                "RACH CRNTI",
                "RACH CNType",
                "RACH AttNum",
                "RACH Result",
                "RACH N Success",
                "RACH N Fail",
                "RACH N Abort",
                "RACH N OthRslt",
                "RACH N 1stAttScss",
                "RACH N MltAttScss",
                "RACH N FailMsg2",
                "RACH N FailMsg4",
            ],
            [
                "nr_p_plus_scell_nr_rach_pathloss",
                "nr_p_plus_scell_nr_rach_reason",
                "nr_p_plus_scell_nr_rach_crnti",
                "nr_p_plus_scell_nr_rach_contention_type",
                "nr_p_plus_scell_nr_rach_attempt_number",
                "nr_p_plus_scell_nr_rach_result",
                "nr_p_plus_scell_nr_rach_num_success",
                "nr_p_plus_scell_nr_rach_num_fail",
                "nr_p_plus_scell_nr_rach_num_abort",
                "nr_p_plus_scell_nr_rach_num_other_result",
                "nr_p_plus_scell_nr_rach_num_first_attempt_success",
                "nr_p_plus_scell_nr_rach_num_multiple_attempt_success",
                "nr_p_plus_scell_nr_rach_num_fail_msg2",
                "nr_p_plus_scell_nr_rach_num_fail_msg4",
            ],
            "nr_cell_meas"
        ),
        (
            [
                "---- ReconfigWithSync params ----",
                "target_arfcn",
                "offset_to_carrier",
                "carrier_bandwidth_rbs",
                "carrier_bandwidth_mhz",
            ],
            [
                '"" as unused6',
                "nr_reconfigwithsync_target_arfcn",
                "nr_reconfigwithsync_carrier_offset_to_carrier_1",
                "nr_reconfigwithsync_carrier_bandwidth_rbs_1",
                "nr_reconfigwithsync_carrier_bandwidth_mhz_1",
            ],
            "nr_reconfigwithsync_params"
        ),
    ]
    return params_list
    

def get_nr_serv_and_neigh_disp_df(dbcon, time_before):
    if preprocess_azm.is_leg_nr_tables():
        df_list = get_nr_serv_and_neigh_list_old(dbcon, time_before)
    else:
        df_list = get_nr_serv_and_neigh_list(dbcon, time_before)

    final_df = pd.concat(df_list, sort=False)
    return final_df

def get_nr_serv_and_neigh_list(dbcon, time_before):
    df_list = []
    pcell_scell_col_prefix_sr = pd.Series(
        [
            "nr_dl_arfcn_",
            "nr_servingbeam_pci_",
            "nr_servingbeam_ssb_index_",
            "nr_servingbeam_ss_rsrp_",
            "nr_servingbeam_ss_rsrq_",
            "nr_servingbeam_ss_sinr_",
        ]
    )
    pcell_scell_col_prefix_renamed = ["ARFCN", "PCI", "BmIdx", "RSRP", "RSRQ", "SINR"]
    parameter_to_columns_list = [
        ("Time", ["time"]),
        (
            [
                "PCell",
                "SCell1",
                "SCell2",
                "SCell3",
                "SCell4",
                "SCell5",
                "SCell6",
                "SCell7",
            ],
            list(pcell_scell_col_prefix_sr + "1")
            + list(pcell_scell_col_prefix_sr + "2")
            + list(pcell_scell_col_prefix_sr + "3")
            + list(pcell_scell_col_prefix_sr + "4")
            + list(pcell_scell_col_prefix_sr + "5")
            + list(pcell_scell_col_prefix_sr + "6")
            + list(pcell_scell_col_prefix_sr + "7")
            + list(pcell_scell_col_prefix_sr + "8"),
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="nr_cell_meas",
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + pcell_scell_col_prefix_renamed
    df_list.append(df)

    dcell_col_suffix_sr = pd.Series(
        ["_dl_arfcn_1", "_pci_1", "_ssb_index_1", "_ss_rsrp_1", "_ss_rsrq_1", "_ss_sinr_1"]
    )  # a mistake during elm sheets made this unnecessary _1 required
    dcell_col_renamed = ["ARFCN", "PCI", "BmIdx", "RSRP", "RSRQ", "SINR"]
    dparameter_to_columns_list = [
        (
            ["DCell1", "DCell2", "DCell3", "DCell4"],
            list("nr_detectedbeam1" + dcell_col_suffix_sr)
            + list("nr_detectedbeam2" + dcell_col_suffix_sr)
            + list("nr_detectedbeam3" + dcell_col_suffix_sr)
            + list("nr_detectedbeam4" + dcell_col_suffix_sr),
        )
    ]
    dcell_df = params_disp_df.get(
        dbcon,
        dparameter_to_columns_list,
        time_before,
        default_table="nr_intra_neighbor",
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    dcell_df.columns = ["CellGroup"] + dcell_col_renamed
    df_list.append(dcell_df)
    return df_list

def get_nr_serv_and_neigh_list_old(dbcon, time_before):
    df_list = []
    pcell_scell_col_prefix_sr = pd.Series(
        [
            "nr_dl_arfcn_",
            "nr_servingbeam_pci_",
            "nr_servingbeam_ssb_index_",
            "nr_servingbeam_ss_rsrp_",
            "nr_servingbeam_ss_rsrq_",
            "nr_servingbeam_ss_sinr_",
        ]
    )
    pcell_scell_col_prefix_renamed = ["ARFCN", "PCI", "BmIdx", "RSRP", "RSRQ", "SINR"]
    parameter_to_columns_list = [
        ("Time", ["time"]),
        (
            [
                "PCell",
                "SCell1",
                "SCell2",
                "SCell3",
                "SCell4",
                "SCell5",
                "SCell6",
                "SCell7",
            ],
            list(pcell_scell_col_prefix_sr + "1")
            + list(pcell_scell_col_prefix_sr + "2")
            + list(pcell_scell_col_prefix_sr + "3")
            + list(pcell_scell_col_prefix_sr + "4")
            + list(pcell_scell_col_prefix_sr + "5")
            + list(pcell_scell_col_prefix_sr + "6")
            + list(pcell_scell_col_prefix_sr + "7")
            + list(pcell_scell_col_prefix_sr + "8"),
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="nr_cell_meas",
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("df.head():\n%s" % df.head())
    df.columns = ["CellGroup"] + pcell_scell_col_prefix_renamed
    # print("df.head():\n%s" % df.head())
    df_list.append(df)

    dcell_col_suffix_sr = pd.Series(
        ["_dl_arfcn_1", "_pci_1", "_ssb_index_1", "_ss_rsrp_1", "_ss_rsrq_1", "_ss_sinr_1"]
    )  # a mistake during elm sheets made this unnecessary _1 required
    dcell_col_renamed = ["ARFCN", "PCI", "BmIdx", "RSRP", "RSRQ", "SINR"]
    dparameter_to_columns_list = [
        (
            ["DCell1", "DCell2", "DCell3", "DCell4"],
            list("nr_detectedbeam1" + dcell_col_suffix_sr)
            + list("nr_detectedbeam2" + dcell_col_suffix_sr)
            + list("nr_detectedbeam3" + dcell_col_suffix_sr)
            + list("nr_detectedbeam4" + dcell_col_suffix_sr),
        )
    ]
    dcell_df = params_disp_df.get(
        dbcon,
        dparameter_to_columns_list,
        time_before,
        default_table="nr_cell_meas",
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    # print("0dcell_df.head():\n%s" % dcell_df.head())
    dcell_df.columns = ["CellGroup"] + dcell_col_renamed
    # print("dcell_df.head():\n%s" % dcell_df.head())
    df_list.append(dcell_df)
    return df_list

def get_nr_beams_disp_df(dbcon, time_before):
    df_list = []
    pcell_scell_col_prefix_sr = pd.Series(
        [
            "nr_band_",
            "nr_dl_arfcn_",
            "nr_servingbeam_pci_",
            "nr_servingbeam_ssb_index_",
            "nr_servingbeam_ss_rsrp_",
            "nr_servingbeam_ss_rsrq_",
            "nr_servingbeam_ss_sinr_",
        ]
    )
    pcell_scell_col_prefix_renamed = ["BAND", "ARFCN", "PCI", "BmIdx", "RSRP", "RSRQ", "SINR"]
    parameter_to_columns_list = [
        (
            [
                "PCell",
                "SCell1",
                "SCell2",
                "SCell3",
                "SCell4",
                "SCell5",
                "SCell6",
                "SCell7",
            ],
            list(pcell_scell_col_prefix_sr + "1")
            + list(pcell_scell_col_prefix_sr + "2")
            + list(pcell_scell_col_prefix_sr + "3")
            + list(pcell_scell_col_prefix_sr + "4")
            + list(pcell_scell_col_prefix_sr + "5")
            + list(pcell_scell_col_prefix_sr + "6")
            + list(pcell_scell_col_prefix_sr + "7")
            + list(pcell_scell_col_prefix_sr + "8"),
        ),
    ]
    df = params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        default_table="nr_cell_meas",
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )
    df.columns = ["CellGroup"] + pcell_scell_col_prefix_renamed
    df_list.append(df)

    final_df = pd.concat(df_list, sort=False)
    return final_df


def get_nr_data_disp_df(dbcon, time_before):
    if preprocess_azm.is_leg_nr_tables():
        parameter_to_columns_list = get_nr_data_params_list_old()
    else:
        parameter_to_columns_list = get_nr_data_params_list()

    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=False,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )

def get_nr_data_params_list():
    params_list = [
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
                "DL LTE L1 TP (MBps)",
            ],
            [
                "lte_l1_dl_throughput_all_carriers_mbps",
            ],
            "lte_l1_dl_tp",
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
                "DL LTE PDCP TP (MBps)",
            ],
            [
                "nr_p_plus_scell_lte_dl_pdcp_tput_mbps",
            ],
            "nr_pdcp_throughput",
        ),
        (
            [
                " ",
                "UL APP TP (MBps)",
            ],
            [
                '"" as unused1',
                "data_trafficstat_ul_mbps",
            ],
            "android_info_1sec",
        ),
        (
            [
                "UL NR MAC TP (MBps)",
            ],
            [
                "nr_mac_tp_ul_mbps_1",
            ],
            "nr_mac_throughput",
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
                "NR CRI",
                "NR LI",
            ],
            [
                "nr_cri_1",
                "nr_li_1",
            ],
            "nr_csi_report",
        ),
        (
            [
                "NR RI",
            ],
            [
                "nr_ri_1",
            ],
            "nr_deb_stat",
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
        (
            [
                "NR CSI CQI",
                "NR CSI RI",
            ],
            [
                "nr_csi_cqi",
                "nr_csi_ri",
            ],
            "nr_csi_report",
        ),
        (
            [
                "NR DL N CRC Pass TB",
                "NR DL N CRC Fail TB",
            ],
            [
                "nr_num_crc_pass_tb_1",
                "nr_num_crc_fail_tb_1",
            ],
            "nr_pdsch_status",
        ),
        (
            [
                "NR UL N CRC Pass TB",
                "NR UL N CRC Fail TB",
                "NR UL N All Tx",
                "NR UL N Re Tx",
                "NR DL MCS",
            ],
            [
                "nr_num_ul_crc_pass_tb_1",
                "nr_num_ul_crc_fail_tb_1",
                "nr_num_ul_all_tx_type_1",
                "nr_num_ul_re_tx_type_1",
                "nr_dl_mcs_mode_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR DL MCS(Avg)",
            ],
            [
                "nr_dl_mcs_avg_1",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "NR DL Mod",
            ],
            [
                "nr_modulation_1",
            ],
            "nr_dci_11",
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
                "NR UL MCS(Avg)",
            ],
            [
                "nr_ul_mcs_avg_1",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "NR UL Mod",
                "Mod % last second:",
            ],
            [
                "nr_ul_modulation_1",
                '"" as unused2',
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
                "NR UL Modulation",
            ],
            [
                "nr_ul_modulation_order",
            ],
            "nr_pusch_status",
        ),
        (
            [
                "NR UL Mod QPSK %",
                "NR UL Mod 16QAM %",
                "NR UL Mod 64QAM %",
                "NR UL Mod 256QAM %",
                "NR UL Mod 1024QAM %",
            ],
            [
                "nr_ul_qpsk_1",
                "nr_ul_16qam_1",
                "nr_ul_64qam_1",
                "nr_ul_256qam_1",
                "nr_ul_1024qam_1",
            ],
            "nr_cell_meas",
        ),
    ]
    return params_list

def get_nr_data_params_list_old():
    params_list = [
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
                "DL NR RLC TP (MBps)",
                "DL NR MAC TP (MBps)",
            ],
            [
                "nr_pdcp_dl_tp_mbps",
                "nr_rlc_dl_tp_mbps",
                "nr_mac_dl_tp_mbps",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "DL LTE L1 TP (MBps)",
            ],
            [
                "lte_l1_dl_throughput_all_carriers_mbps",
            ],
            "lte_l1_dl_tp",
        ),
        (
            [
                "DL NR PDSCH TP (MBps)",
                "DL LTE PDCP TP (MBps)",
            ],
            [
                "nr_p_plus_scell_nr_pdsch_tput_mbps",
                "nr_p_plus_scell_lte_dl_pdcp_tput_mbps",
            ],
            "nr_cell_meas",
        ),(
            [
                " ",
                "UL APP TP (MBps)",
            ],
            [
                '"" as unused1',
                "data_trafficstat_ul_mbps",
            ],
            "android_info_1sec",
        ),
        (
            [
                "UL NR MAC TP (MBps)",
            ],
            [
                "nr_mac_ul_tp_mbps",
            ],
            "nr_deb_stat",
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
            "nr_cell_meas",
        ),
        (
            [
                "NR CQI",
                "NR CRI",
                "NR LI",
                "NR RI",
                "NR PMI I1 1",
                "NR PMI I1 2",
                "NR PMI I1 3",
                "NR PMI I2",
            ],
            [
                "nr_cqi",
                "nr_cri_1",
                "nr_li_1",
                "nr_ri_1",
                "nr_wb_pmi_i1_1_1",
                "nr_wb_pmi_i1_2_1",
                "nr_wb_pmi_i1_3_1",
                "nr_wb_pmi_i2_1",
            ],
            "nr_cell_meas",
        ),
        (
            [
                "NR CSI CQI",
                "NR CSI CRI",
                "NR CSI RI",
                "NR CSI LI",
            ],
            [
                "nr_csi_cqi",
                "nr_csi_cri",
                "nr_csi_ri",
                "nr_csi_li",
            ],
            "nr_csi_report",
        ),
        (
            [
                "NR DL N CRC Pass TB",
                "NR DL N CRC Fail TB",
                "NR UL N CRC Pass TB",
                "NR UL N CRC Fail TB",
                "NR UL N All Tx",
                "NR UL N Re Tx",
                "NR DL MCS",
                "NR DL MCS(Avg)",
                "NR DL Mod",
                "NR UL MCS",
                "NR UL MCS(Avg)",
                "NR UL Mod",
                "Mod % last second:",
            ],
            [
                "nr_num_crc_pass_tb_1",
                "nr_num_crc_fail_tb_1",
                "nr_num_ul_crc_pass_tb_1",
                "nr_num_ul_crc_fail_tb_1",
                "nr_num_ul_all_tx_type_1",
                "nr_num_ul_re_tx_type_1",
                "nr_dl_mcs_mode_1",
                "nr_dl_mcs_avg_1",
                "nr_modulation_1",
                "nr_ul_mcs_mode_1",
                "nr_ul_mcs_avg_1",
                "nr_ul_modulation_1",
                '"" as unused2',
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
            "nr_cell_meas",
        ),
        (
            [
                "NR UL Num RB",
                "NR UL Modulation",
            ],
            [
                "nr_ul_num_rb",
                "nr_ul_modulation_order",
            ],
            "nr_deb_stat",
        ),
        (
            [
                "NR UL Mod QPSK %",
                "NR UL Mod 16QAM %",
                "NR UL Mod 64QAM %",
                "NR UL Mod 256QAM %",
                "NR UL Mod 1024QAM %",
            ],
            [
                "nr_ul_qpsk_1",
                "nr_ul_16qam_1",
                "nr_ul_64qam_1",
                "nr_ul_256qam_1",
                "nr_ul_1024qam_1",
            ],
            "nr_cell_meas",
        ),
    ]
    return params_list
# def get_nr_radio_params_disp_df(dbcon, time_before):
#     n_param_args = 8
#     parameter_to_columns_list = [
#         ("Time", ["time"]),
#         (  # these params below come together so query them all in one query
#             [
#                 "Beam ID",
#                 "Band",
#                 "Band Type",
#                 "ARFCN",
#                 "Frequency",
#                 "PCI",
#                 "RSRP",
#                 "RSRQ",
#                 "SINR",
#                 "Bandwidth",
#                 "SSB SCS",
#                 "Numerology SCS",
#             ],
#             list(
#                 map(
#                     lambda x: "nr_servingbeam_ssb_index_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(map(lambda x: "nr_band_{}".format(x + 1), range(n_param_args)))
#             + list(map(lambda x: "nr_band_type_{}".format(x + 1), range(n_param_args)))
#             + list(map(lambda x: "nr_dl_arfcn_{}".format(x + 1), range(n_param_args)))
#             + list(
#                 map(lambda x: "nr_dl_frequency_{}".format(x + 1), range(n_param_args))
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_pci_{}".format(x + 1), range(n_param_args)
#                 )
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_ss_rsrp_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_ss_rsrq_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(
#                 map(
#                     lambda x: "nr_servingbeam_ss_sinr_{}".format(x + 1),
#                     range(n_param_args),
#                 )
#             )
#             + list(map(lambda x: "nr_bw_{}".format(x + 1), range(n_param_args)))
#             + list(map(lambda x: "nr_ssb_scs_{}".format(x + 1), range(n_param_args)))
#             + list(
#                 map(lambda x: "nr_numerology_scs_{}".format(x + 1), range(n_param_args))
#             ),
#         ),
#         (  # these params below come together but not same row with rsrp etc above so query them all in their own set below
#             ["PUSCH TxPower", "PUCCH TxPower", "SRS TxPower"],
#             list(
#                 map(lambda x: "nr_pusch_tx_power_{}".format(x + 1), range(n_param_args))
#             )
#             + list(
#                 map(lambda x: "nr_pucch_tx_power_{}".format(x + 1), range(n_param_args))
#             )
#             + list(
#                 map(lambda x: "nr_srs_tx_power_{}".format(x + 1), range(n_param_args))
#             ),
#         ),
#     ]
#     return params_disp_df.get(
#         dbcon,
#         parameter_to_columns_list,
#         time_before,
#         default_table="nr_cell_meas",
#         custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
#     )

