NR_RADIO_PARAMS_SQL_LIST = [
    '''
    select log_hash, time,
    '' as '--- PCell ---'
    from nr_cell_meas
    ''' ,
    '''
    select nr_dl_frequency_1 as 'NR DL FREQ',
    nr_dl_arfcn_1 as 'NR ARFCN', 
    nr_band_1 as 'NR Band', 
    nr_servingbeam_pci_1 as 'NR PCI', 
    nr_servingbeam_ssb_index_1 as 'NR SSB Index', 
    nr_servingbeam_ss_rsrp_1 as 'NR SS RSRP', 
    nr_servingbeam_ss_rsrq_1 as 'NR SS RSRQ', 
    nr_servingbeam_ss_sinr_1 as 'NR SS SINR', 
    nr_numerology_scs_1 as 'NR SubCarrier Size', 
    nr_num_rx_ant_1 as 'NR N Rx Ant'
    from nr_cell_meas
    ''' ,
    '''
    select nr_num_tx_ant_1 as 'NR N Tx Ant'
    from nr_deb_stat
    ''' ,
    '''
    select nr_numerology_scs_1 as 'NR SubCarrier Size'
    from nr_cell_meas
    ''' ,
    '''
    select nr_dl_rb_1 as 'NR DL RB'
    from nr_cell_meas
    ''' ,
    '''
    select nr_bw_1 as 'NR DL Bandwidth'
    from nr_cell_meas
    ''' ,
    '''
    select nr_ul_rb_1 as 'NR UL RB'
    from nr_ul_rb
    ''' ,
    '''
    select nr_ul_bw_1 as '"NR UL Bandwidth'
    from nr_cell_meas
    ''' ,
    '''
    select nr_cri_1 as 'NR CRI'
    from nr_csi_report
    ''' ,
    '''
    select nr_ri_1 as 'NR RI'
    from nr_deb_stat
    ''' ,
    '''
    select nr_numlayers_1 as 'NR NumLayers'
    from nr_deb_stat
    ''' ,
    '''
    select nr_pdsch_tx_mode_1 as 'NR DL TxMode',
    nr_ul_tx_mode_1 as 'NR UL TxMode'
    from nr_cell_meas
    ''' ,
    '''
    select nr_endc_total_tx_power as 'NR ENDC Total Tx Power',
    '' as '--- PUSCH ---',
    nr_pusch_tx_power_1 as 'NR PUSCH Tx Power'
    from nr_deb_stat
    ''' ,
    '''
    select nr_pusch_mtpl_1 as 'NR PUSCH MTPL',
    nr_pusch_dl_pathloss_1 as 'NR PUSCH DL Ploss',
    nr_pusch_f_i_1 as 'NR PUSCH f(i)'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- PUCCH ---',
    nr_pucch_tx_power_1 as 'NR PUCCH Tx Power'
    from nr_deb_stat
    ''' ,
    '''
    select nr_pucch_mtpl_1 as 'NR PUCCH MTPL',
    nr_pucch_dl_pathloss_1 as 'NR PUCCH DL Ploss',
    nr_pucch_g_i_1 as 'NR PUCCH f(i)'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- SRS ---',
    nr_srs_tx_power_1 as 'NR SRX Tx Power'
    from nr_tx_srs_status
    ''' ,
    '''
    select nr_srs_mtpl_1 as 'NR SRX MTPL'
    from nr_deb_stat
    ''' ,
    '''
    select nr_srs_dl_pathloss_1 as 'NR SRX DL PLoss',
    nr_srs_pc_adj_state_1 as 'NR SRX PC Adj State'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- RACH ---',
    nr_prach_tx_power as 'NR PRACH Tx Power'
    from nr_deb_stat
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_pathloss_1 as 'RACH PLoss',
    nr_p_plus_scell_nr_rach_reason_1 as 'RACH Reason'
    from nr_prach_status
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_crnti as 'RACH CRNTI',
    nr_p_plus_scell_nr_rach_contention_type as 'RACH CNType',
    nr_p_plus_scell_nr_rach_attempt_number as 'RACH AttNum'
    from nr_rach_stat
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_result as 'RACH Result'
    from nr_rach_stat
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_num_success as 'RACH N Success'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_num_fail as 'RACH N Fail'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_num_abort as 'RACH N Abort'
    from nr_cell_meas
    ''' ,
    '''
    select
    nr_p_plus_scell_nr_rach_num_other_result as 'RACH N OthRslt',
    nr_p_plus_scell_nr_rach_num_first_attempt_success as 'RACH N 1stAttScss',
    nr_p_plus_scell_nr_rach_num_multiple_attempt_success as 'RACH N MltAttScss'
    from nr_cell_meas
    ''' ,
    '''
    select
    nr_p_plus_scell_nr_rach_num_fail_msg2 as 'RACH N FailMsg2',
    nr_p_plus_scell_nr_rach_num_fail_msg4 as 'RACH N FailMsg4'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- ReconfigWithSync params ---',
    nr_reconfigwithsync_target_arfcn as 'target_arfcn',
    nr_reconfigwithsync_carrier_offset_to_carrier_1 as 'offset_to_carrier',
    nr_reconfigwithsync_carrier_bandwidth_rbs_1 as 'carrier_bandwidth_rbs',
    nr_reconfigwithsync_carrier_bandwidth_mhz_1 as 'carrier_bandwidth_mhz'
    from nr_reconfigwithsync_params
    ''' ,
    ]

OLD_NR_RADIO_PARAMS_SQL_LIST = [
    '''
    select log_hash, time,
    '' as '--- PCell ---'
    from nr_cell_meas
    ''' ,
    '''
    select
    nr_dl_frequency_1 as 'NR DL FREQ',
    nr_dl_arfcn_1 as 'NR ARFCN', 
    nr_band_1 as 'NR Band', 
    nr_servingbeam_pci_1 as 'NR PCI',
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ssb_index_1 as 'NR SSB Index'
    from nr_cell_meas
    ''' ,
    '''
    select
    nr_servingbeam_ss_rsrp_1 as 'NR SS RSRP', 
    nr_servingbeam_ss_rsrq_1 as 'NR SS RSRQ', 
    nr_servingbeam_ss_sinr_1 as 'NR SS SINR', 
    nr_numerology_scs_1 as 'NR SubCarrier Size', 
    nr_num_rx_ant_1 as 'NR N Rx Ant'
    from nr_cell_meas
    ''' ,
    '''
    select nr_num_tx_ant_1 as 'NR N Tx Ant'
    from nr_cell_meas
    ''' ,
    '''
    select nr_numerology_scs_1 as 'NR SubCarrier Size'
    from nr_cell_meas
    ''' ,
    '''
    select nr_dl_rb_1 as 'NR DL RB'
    from nr_cell_meas
    ''' ,
    '''
    select nr_bw_1 as 'NR DL Bandwidth'
    from nr_cell_meas
    ''' ,
    '''
    select nr_ul_rb_1 as 'NR UL RB'
    from nr_cell_meas
    ''' ,
    '''
    select nr_ul_bw_1 as '"NR UL Bandwidth'
    from nr_cell_meas
    ''' ,
    '''
    select nr_numlayers_1 as 'NR NumLayers'
    from nr_cell_meas
    ''' ,
    '''
    select nr_pdsch_tx_mode_1 as 'NR DL TxMode',
    nr_ul_tx_mode_1 as 'NR UL TxMode'
    from nr_cell_meas
    ''' ,
    '''
    select nr_endc_total_tx_power as 'NR ENDC Total Tx Power',
    '' as '--- PUSCH ---',
    nr_pusch_tx_power_1 as 'NR PUSCH Tx Power'
    from nr_cell_meas
    ''' ,
    '''
    select nr_pusch_mtpl_1 as 'NR PUSCH MTPL',
    nr_pusch_dl_pathloss_1 as 'NR PUSCH DL Ploss',
    nr_pusch_f_i_1 as 'NR PUSCH f(i)'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- PUCCH ---',
    nr_pucch_tx_power_1 as 'NR PUCCH Tx Power'
    from nr_cell_meas
    ''' ,
    '''
    select nr_pucch_mtpl_1 as 'NR PUCCH MTPL',
    nr_pucch_dl_pathloss_1 as 'NR PUCCH DL Ploss',
    nr_pucch_g_i_1 as 'NR PUCCH f(i)'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- SRS ---',
    nr_srs_tx_power_1 as 'NR SRX Tx Power'
    from nr_cell_meas
    ''' ,
    '''
    select nr_srs_mtpl_1 as 'NR SRX MTPL'
    from nr_cell_meas
    ''' ,
    '''
    select nr_srs_dl_pathloss_1 as 'NR SRX DL PLoss',
    nr_srs_pc_adj_state_1 as 'NR SRX PC Adj State'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- RACH ---',
    nr_prach_tx_power as 'NR PRACH Tx Power'
    from nr_deb_stat
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_pathloss as 'RACH PLoss',
    nr_p_plus_scell_nr_rach_reason as 'RACH Reason'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_crnti as 'RACH CRNTI',
    nr_p_plus_scell_nr_rach_contention_type as 'RACH CNType',
    nr_p_plus_scell_nr_rach_attempt_number as 'RACH AttNum'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_result as 'RACH Result'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_num_success as 'RACH N Success'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_num_fail as 'RACH N Fail'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_p_plus_scell_nr_rach_num_abort as 'RACH N Abort'
    from nr_cell_meas
    ''' ,
    '''
    select
    nr_p_plus_scell_nr_rach_num_other_result as 'RACH N OthRslt',
    nr_p_plus_scell_nr_rach_num_first_attempt_success as 'RACH N 1stAttScss',
    nr_p_plus_scell_nr_rach_num_multiple_attempt_success as 'RACH N MltAttScss'
    from nr_cell_meas
    ''' ,
    '''
    select
    nr_p_plus_scell_nr_rach_num_fail_msg2 as 'RACH N FailMsg2',
    nr_p_plus_scell_nr_rach_num_fail_msg4 as 'RACH N FailMsg4'
    from nr_cell_meas
    ''' ,
    '''
    select '' as '--- ReconfigWithSync params ---',
    nr_reconfigwithsync_target_arfcn as 'target_arfcn',
    nr_reconfigwithsync_carrier_offset_to_carrier_1 as 'offset_to_carrier',
    nr_reconfigwithsync_carrier_bandwidth_rbs_1 as 'carrier_bandwidth_rbs',
    nr_reconfigwithsync_carrier_bandwidth_mhz_1 as 'carrier_bandwidth_mhz'
    from nr_reconfigwithsync_params
    ''' ,
    ]

NR_BEAMS_SQL_LIST_DICT = {
    "BAND":[
        '''
        select log_hash, time as Time
        from nr_cell_meas
        ''' ,
        '''
        select
        nr_band_1 as PCell,
        nr_band_2 as SCell1,
        nr_band_3 as SCell2,
        nr_band_4 as SCell3,
        nr_band_5 as SCell4,
        nr_band_6 as SCell5,
        nr_band_7 as SCell6,
        nr_band_8 as SCell7
        from nr_cell_meas
        '''
    ],
    "ARFCN":[
        '''
        select "" as log_hash, "" as Time
        from nr_cell_meas
        ''' ,
        '''
        select
        nr_dl_arfcn_1 as PCell,
        nr_dl_arfcn_2 as SCell1,
        nr_dl_arfcn_3 as SCell2,
        nr_dl_arfcn_4 as SCell3,
        nr_dl_arfcn_5 as SCell4,
        nr_dl_arfcn_6 as SCell5,
        nr_dl_arfcn_7 as SCell6,
        nr_dl_arfcn_8 as SCell7
        from nr_cell_meas
        '''
    ],
    "PCI":[
        '''
        select "" as log_hash, "" as Time
        from nr_cell_meas
        ''' ,
        '''
        select
        nr_servingbeam_pci_1 as PCell,
        nr_servingbeam_pci_2 as SCell1,
        nr_servingbeam_pci_3 as SCell2,
        nr_servingbeam_pci_4 as SCell3,
        nr_servingbeam_pci_5 as SCell4,
        nr_servingbeam_pci_6 as SCell5,
        nr_servingbeam_pci_7 as SCell6,
        nr_servingbeam_pci_8 as SCell7
        from nr_cell_meas
        '''
    ],
    "BmIdx":[
        '''
        select "" as log_hash, "" as Time
        from nr_cell_meas
        ''' ,
        '''
        select
        nr_servingbeam_ssb_index_1 as PCell,
        nr_servingbeam_ssb_index_2 as SCell1,
        nr_servingbeam_ssb_index_3 as SCell2,
        nr_servingbeam_ssb_index_4 as SCell3,
        nr_servingbeam_ssb_index_5 as SCell4,
        nr_servingbeam_ssb_index_6 as SCell5,
        nr_servingbeam_ssb_index_7 as SCell6,
        nr_servingbeam_ssb_index_8 as SCell7
        from nr_cell_meas
        '''
    ],
    "RSRP":[
        '''
        select "" as log_hash, "" as Time
        from nr_cell_meas
        ''' ,
        '''
        select
        nr_servingbeam_ss_rsrp_1 as PCell,
        nr_servingbeam_ss_rsrp_2 as SCell1,
        nr_servingbeam_ss_rsrp_3 as SCell2,
        nr_servingbeam_ss_rsrp_4 as SCell3,
        nr_servingbeam_ss_rsrp_5 as SCell4,
        nr_servingbeam_ss_rsrp_6 as SCell5,
        nr_servingbeam_ss_rsrp_7 as SCell6,
        nr_servingbeam_ss_rsrp_8 as SCell7
        from nr_cell_meas
        '''
    ],
    "RSRQ":[
        '''
        select "" as log_hash, "" as Time
        from nr_cell_meas
        ''' ,
        '''
        select
        nr_servingbeam_ss_rsrq_1 as PCell,
        nr_servingbeam_ss_rsrq_2 as SCell1,
        nr_servingbeam_ss_rsrq_3 as SCell2,
        nr_servingbeam_ss_rsrq_4 as SCell3,
        nr_servingbeam_ss_rsrq_5 as SCell4,
        nr_servingbeam_ss_rsrq_6 as SCell5,
        nr_servingbeam_ss_rsrq_7 as SCell6,
        nr_servingbeam_ss_rsrq_8 as SCell7
        from nr_cell_meas
        '''
    ],
    "SINR":[
        '''
        select "" as log_hash, "" as Time
        from nr_cell_meas
        ''' ,
        '''
        select
        nr_servingbeam_ss_sinr_1 as PCell,
        nr_servingbeam_ss_sinr_2 as SCell1,
        nr_servingbeam_ss_sinr_3 as SCell2,
        nr_servingbeam_ss_sinr_4 as SCell3,
        nr_servingbeam_ss_sinr_5 as SCell4,
        nr_servingbeam_ss_sinr_6 as SCell5,
        nr_servingbeam_ss_sinr_7 as SCell6,
        nr_servingbeam_ss_sinr_8 as SCell7
        from nr_cell_meas
        '''
    ],
}

NR_SERV_AND_NEIGH_SQL_LIST_DICT = {
    "ARFCN":[
    '''
    select log_hash, time as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_dl_arfcn_1 as 'PCell',
    nr_dl_arfcn_2 as 'SCell1',
    nr_dl_arfcn_3 as 'SCell2',
    nr_dl_arfcn_4 as 'SCell3',
    nr_dl_arfcn_5 as 'SCell4',
    nr_dl_arfcn_6 as 'SCell5',
    nr_dl_arfcn_7 as 'SCell6',
    nr_dl_arfcn_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_dl_arfcn_1 as 'DCell1',
    nr_detectedbeam2_dl_arfcn_1 as 'DCell2',
    nr_detectedbeam3_dl_arfcn_1 as 'DCell3',
    nr_detectedbeam4_dl_arfcn_1 as 'DCell4'
    from nr_intra_neighbor
    ''' ,
    ],
    "PCI":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_pci_1 as 'PCell',
    nr_servingbeam_pci_2 as 'SCell1',
    nr_servingbeam_pci_3 as 'SCell2',
    nr_servingbeam_pci_4 as 'SCell3',
    nr_servingbeam_pci_5 as 'SCell4',
    nr_servingbeam_pci_6 as 'SCell5',
    nr_servingbeam_pci_7 as 'SCell6',
    nr_servingbeam_pci_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_pci_1 as 'DCell1',
    nr_detectedbeam2_pci_1 as 'DCell2',
    nr_detectedbeam3_pci_1 as 'DCell3',
    nr_detectedbeam4_pci_1 as 'DCell4'
    from nr_intra_neighbor
    ''' ,
    ],
    "BmIdx":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ssb_index_1 as 'PCell',
    nr_servingbeam_ssb_index_2 as 'SCell1',
    nr_servingbeam_ssb_index_3 as 'SCell2',
    nr_servingbeam_ssb_index_4 as 'SCell3',
    nr_servingbeam_ssb_index_5 as 'SCell4',
    nr_servingbeam_ssb_index_6 as 'SCell5',
    nr_servingbeam_ssb_index_7 as 'SCell6',
    nr_servingbeam_ssb_index_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ssb_index_1 as 'DCell1',
    nr_detectedbeam2_ssb_index_1 as 'DCell2',
    nr_detectedbeam3_ssb_index_1 as 'DCell3',
    nr_detectedbeam4_ssb_index_1 as 'DCell4'
    from nr_intra_neighbor
    ''' ,
    ],
    "RSRP":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ss_rsrp_1 as 'PCell',
    nr_servingbeam_ss_rsrp_2 as 'SCell1',
    nr_servingbeam_ss_rsrp_3 as 'SCell2',
    nr_servingbeam_ss_rsrp_4 as 'SCell3',
    nr_servingbeam_ss_rsrp_5 as 'SCell4',
    nr_servingbeam_ss_rsrp_6 as 'SCell5',
    nr_servingbeam_ss_rsrp_7 as 'SCell6',
    nr_servingbeam_ss_rsrp_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ss_rsrp_1 as 'DCell1',
    nr_detectedbeam2_ss_rsrp_1 as 'DCell2',
    nr_detectedbeam3_ss_rsrp_1 as 'DCell3',
    nr_detectedbeam4_ss_rsrp_1 as 'DCell4'
    from nr_intra_neighbor
    ''' ,
    ],
    "RSRQ":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ss_rsrq_1 as 'PCell',
    nr_servingbeam_ss_rsrq_2 as 'SCell1',
    nr_servingbeam_ss_rsrq_3 as 'SCell2',
    nr_servingbeam_ss_rsrq_4 as 'SCell3',
    nr_servingbeam_ss_rsrq_5 as 'SCell4',
    nr_servingbeam_ss_rsrq_6 as 'SCell5',
    nr_servingbeam_ss_rsrq_7 as 'SCell6',
    nr_servingbeam_ss_rsrq_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ss_rsrq_1 as 'DCell1',
    nr_detectedbeam2_ss_rsrq_1 as 'DCell2',
    nr_detectedbeam3_ss_rsrq_1 as 'DCell3',
    nr_detectedbeam4_ss_rsrq_1 as 'DCell4'
    from nr_intra_neighbor
    ''' ,
    ],
    "SINR":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ss_sinr_1 as 'PCell',
    nr_servingbeam_ss_sinr_2 as 'SCell1',
    nr_servingbeam_ss_sinr_3 as 'SCell2',
    nr_servingbeam_ss_sinr_4 as 'SCell3',
    nr_servingbeam_ss_sinr_5 as 'SCell4',
    nr_servingbeam_ss_sinr_6 as 'SCell5',
    nr_servingbeam_ss_sinr_7 as 'SCell6',
    nr_servingbeam_ss_sinr_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ss_sinr_1 as 'DCell1',
    nr_detectedbeam2_ss_sinr_1 as 'DCell2',
    nr_detectedbeam3_ss_sinr_1 as 'DCell3',
    nr_detectedbeam4_ss_sinr_1 as 'DCell4'
    from nr_intra_neighbor
    ''' ,
    ]
    }

OLD_NR_SERV_AND_NEIGH_SQL_LIST_DICT = {
    "ARFCN":[
    '''
    select log_hash, time as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_dl_arfcn_1 as 'PCell',
    nr_dl_arfcn_2 as 'SCell1',
    nr_dl_arfcn_3 as 'SCell2',
    nr_dl_arfcn_4 as 'SCell3',
    nr_dl_arfcn_5 as 'SCell4',
    nr_dl_arfcn_6 as 'SCell5',
    nr_dl_arfcn_7 as 'SCell6',
    nr_dl_arfcn_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_dl_arfcn_1 as 'DCell1',
    nr_detectedbeam2_dl_arfcn_1 as 'DCell2',
    nr_detectedbeam3_dl_arfcn_1 as 'DCell3',
    nr_detectedbeam4_dl_arfcn_1 as 'DCell4'
    from nr_cell_meas
    ''' ,
    ],
    "PCI":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_pci_1 as 'PCell',
    nr_servingbeam_pci_2 as 'SCell1',
    nr_servingbeam_pci_3 as 'SCell2',
    nr_servingbeam_pci_4 as 'SCell3',
    nr_servingbeam_pci_5 as 'SCell4',
    nr_servingbeam_pci_6 as 'SCell5',
    nr_servingbeam_pci_7 as 'SCell6',
    nr_servingbeam_pci_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_pci_1 as 'DCell1',
    nr_detectedbeam2_pci_1 as 'DCell2',
    nr_detectedbeam3_pci_1 as 'DCell3',
    nr_detectedbeam4_pci_1 as 'DCell4'
    from nr_cell_meas
    ''' ,
    ],
    "BmIdx":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ssb_index_1 as 'PCell',
    nr_servingbeam_ssb_index_2 as 'SCell1',
    nr_servingbeam_ssb_index_3 as 'SCell2',
    nr_servingbeam_ssb_index_4 as 'SCell3',
    nr_servingbeam_ssb_index_5 as 'SCell4',
    nr_servingbeam_ssb_index_6 as 'SCell5',
    nr_servingbeam_ssb_index_7 as 'SCell6',
    nr_servingbeam_ssb_index_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ssb_index_1 as 'DCell1',
    nr_detectedbeam2_ssb_index_1 as 'DCell2',
    nr_detectedbeam3_ssb_index_1 as 'DCell3',
    nr_detectedbeam4_ssb_index_1 as 'DCell4'
    from nr_cell_meas
    ''' ,
    ],
    "RSRP":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ss_rsrp_1 as 'PCell',
    nr_servingbeam_ss_rsrp_2 as 'SCell1',
    nr_servingbeam_ss_rsrp_3 as 'SCell2',
    nr_servingbeam_ss_rsrp_4 as 'SCell3',
    nr_servingbeam_ss_rsrp_5 as 'SCell4',
    nr_servingbeam_ss_rsrp_6 as 'SCell5',
    nr_servingbeam_ss_rsrp_7 as 'SCell6',
    nr_servingbeam_ss_rsrp_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ss_rsrp_1 as 'DCell1',
    nr_detectedbeam2_ss_rsrp_1 as 'DCell2',
    nr_detectedbeam3_ss_rsrp_1 as 'DCell3',
    nr_detectedbeam4_ss_rsrp_1 as 'DCell4'
    from nr_cell_meas
    ''' ,
    ],
    "RSRQ":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ss_rsrq_1 as 'PCell',
    nr_servingbeam_ss_rsrq_2 as 'SCell1',
    nr_servingbeam_ss_rsrq_3 as 'SCell2',
    nr_servingbeam_ss_rsrq_4 as 'SCell3',
    nr_servingbeam_ss_rsrq_5 as 'SCell4',
    nr_servingbeam_ss_rsrq_6 as 'SCell5',
    nr_servingbeam_ss_rsrq_7 as 'SCell6',
    nr_servingbeam_ss_rsrq_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ss_rsrq_1 as 'DCell1',
    nr_detectedbeam2_ss_rsrq_1 as 'DCell2',
    nr_detectedbeam3_ss_rsrq_1 as 'DCell3',
    nr_detectedbeam4_ss_rsrq_1 as 'DCell4'
    from nr_cell_meas
    ''' ,
    ],
    "SINR":[
    '''
    select "" as log_hash, "" as Time
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_servingbeam_ss_sinr_1 as 'PCell',
    nr_servingbeam_ss_sinr_2 as 'SCell1',
    nr_servingbeam_ss_sinr_3 as 'SCell2',
    nr_servingbeam_ss_sinr_4 as 'SCell3',
    nr_servingbeam_ss_sinr_5 as 'SCell4',
    nr_servingbeam_ss_sinr_6 as 'SCell5',
    nr_servingbeam_ss_sinr_7 as 'SCell6',
    nr_servingbeam_ss_sinr_8 as 'SCell7'
    from nr_cell_meas
    ''' ,
    '''
    select 
    nr_detectedbeam1_ss_sinr_1 as 'DCell1',
    nr_detectedbeam2_ss_sinr_1 as 'DCell2',
    nr_detectedbeam3_ss_sinr_1 as 'DCell3',
    nr_detectedbeam4_ss_sinr_1 as 'DCell4'
    from nr_cell_meas
    ''' ,
    ]
    }

NR_DATA_PARAMS_SQL_LIST = [
    '''select data_trafficstat_dl_mbps as 'DL APP TP (MBps)' from android_info_1sec''',
    '''select nr_pdcp_dl_tp_mbps as 'DL NR PDCP TP (MBps)' from nr_pdcp_throughput''',
    '''select nr_rlc_dl_tp_mbps as 'DL NR RLC TP (MBps)' from nr_deb_stat''',
    '''select lte_l1_dl_throughput_all_carriers_mbps as 'DL LTE L1 TP (MBps)' from lte_l1_dl_tp''',
    '''select nr_p_plus_scell_nr_pdsch_tput_mbps as 'DL NR PDSCH TP (MBps)' from nr_throughput''',
    '''select nr_p_plus_scell_lte_dl_pdcp_tput_mbps as 'DL LTE PDCP TP (MBps)' from nr_pdcp_throughput''',
    '''select "" as ' ',data_trafficstat_ul_mbps as 'UL APP TP (MBps)' from android_info_1sec''',
    '''select lte_l1_ul_throughput_all_carriers_mbps_1 as 'UL LTE L1 TP (MBps)' from lte_l1_ul_tp''',
    '''select nr_p_plus_scell_nr_pusch_tput_mbps as 'UL NR PDSCH TP (MBps)' from nr_throughput''',
    '''select nr_cqi as 'NR CQI' from nr_deb_stat''',
    '''select nr_cri_1 as 'NR CRI' from nr_csi_report''',
    '''select nr_ri_1 as 'NR RI' from nr_deb_stat''',
    '''select nr_wb_pmi_i1_1_1 as 'NR PMI I1 1',nr_wb_pmi_i1_2_1 as 'NR PMI I1 2',nr_wb_pmi_i1_3_1 as 'NR PMI I1 3',nr_wb_pmi_i2_1 as 'NR PMI I2' from nr_csi_report''',
    '''select nr_csi_cqi as 'NR CSI CQI',nr_csi_ri as 'NR CSI RI' from nr_csi_report''',
    '''select nr_num_crc_pass_tb_1 as 'NR DL N CRC Pass TB',nr_num_crc_fail_tb_1 as 'NR DL N CRC Fail TB' from nr_pdsch_status''',
    '''select nr_num_ul_crc_pass_tb_1 as 'NR UL N CRC Pass TB',nr_num_ul_crc_fail_tb_1 as 'NR UL N CRC Fail TB',nr_num_ul_all_tx_type_1 as 'NR UL N All Tx',nr_num_ul_re_tx_type_1 as 'NR UL N Re Tx',nr_dl_mcs_mode_1 as 'NR DL MCS' from nr_cell_meas''',
    '''select nr_dl_mcs_avg_1 as 'NR DL MCS(Avg)' from nr_deb_stat''',
    '''select nr_modulation_1 as 'NR DL Mod' from nr_dci_11''',
    '''select nr_ul_mcs_mode_1 as 'NR UL MCS' from nr_cell_meas''',
    '''select nr_ul_mcs_avg_1 as 'NR UL MCS(Avg)' from nr_deb_stat''',
    '''select nr_ul_modulation_1 as 'NR UL Mod', '' as '--- Mod last second ---' from nr_cell_meas''',
    '''select nr_qpsk_1 as 'NR DL Mod QPSK %',nr_16qam_1 as 'NR DL Mod 16QAM %',nr_64qam_1 as 'NR DL Mod 64QAM %',nr_256qam_1 as 'NR DL Mod 256QAM %',nr_1024qam_1 as 'NR DL Mod 1024QAM %' from nr_pdsch_stat''',
    '''select nr_ul_modulation_order as 'NR UL Modulation' from nr_pusch_status''',
    '''select nr_ul_qpsk_1 as 'NR UL Mod QPSK %',nr_ul_16qam_1 as 'NR UL Mod 16QAM %',nr_ul_64qam_1 as 'NR UL Mod 64QAM %',nr_ul_256qam_1 as 'NR UL Mod 256QAM %',nr_ul_1024qam_1 as 'NR UL Mod 1024QAM %' from nr_cell_meas'''
    ]

OLD_NR_DATA_PARAMS_SQL_LIST = [
    '''select data_trafficstat_dl_mbps as 'DL APP TP (MBps)' from android_info_1sec''',
    '''select nr_pdcp_dl_tp_mbps as 'DL NR PDCP TP (MBps)',nr_rlc_dl_tp_mbps as 'DL NR RLC TP (MBps)' from nr_deb_stat''',
    '''select lte_l1_dl_throughput_all_carriers_mbps as 'DL LTE L1 TP (MBps)' from lte_l1_dl_tp''',
    '''select nr_p_plus_scell_nr_pdsch_tput_mbps as 'DL NR PDSCH TP (MBps)',nr_p_plus_scell_lte_dl_pdcp_tput_mbps as 'DL LTE PDCP TP (MBps)' from nr_cell_meas''',
    '''select "" as ' ',data_trafficstat_ul_mbps as 'UL APP TP (MBps)' from android_info_1sec''',
    '''select lte_l1_ul_throughput_all_carriers_mbps_1 as 'UL LTE L1 TP (MBps)' from lte_l1_ul_tp''',
    '''select nr_p_plus_scell_nr_pusch_tput_mbps as 'UL NR PDSCH TP (MBps)' from nr_cell_meas''',
    '''select nr_cqi as 'NR CQI',nr_cri_1 as 'NR CRI',nr_ri_1 as 'NR RI',nr_wb_pmi_i1_1_1 as 'NR PMI I1 1',nr_wb_pmi_i1_2_1 as 'NR PMI I1 2',nr_wb_pmi_i1_3_1 as 'NR PMI I1 3',nr_wb_pmi_i2_1 as 'NR PMI I2' from nr_cell_meas''',
    '''select nr_csi_cqi as 'NR CSI CQI',nr_csi_cri as 'NR CSI CRI',nr_csi_ri as 'NR CSI RI',nr_csi_li as 'NR CSI LI' from nr_csi_report''',
    '''select nr_num_crc_pass_tb_1 as 'NR DL N CRC Pass TB',nr_num_crc_fail_tb_1 as 'NR DL N CRC Fail TB',nr_num_ul_crc_pass_tb_1 as 'NR UL N CRC Pass TB',nr_num_ul_crc_fail_tb_1 as 'NR UL N CRC Fail TB',nr_num_ul_all_tx_type_1 as 'NR UL N All Tx',nr_num_ul_re_tx_type_1 as 'NR UL N Re Tx',nr_dl_mcs_mode_1 as 'NR DL MCS',nr_dl_mcs_avg_1 as 'NR DL MCS(Avg)',nr_modulation_1 as 'NR DL Mod',nr_ul_mcs_mode_1 as 'NR UL MCS',nr_ul_mcs_avg_1 as 'NR UL MCS(Avg)',nr_ul_modulation_1 as 'NR UL Mod', '' as '--- Mod last second ---' from nr_cell_meas''',
    '''select nr_qpsk_1 as 'NR DL Mod QPSK %',nr_16qam_1 as 'NR DL Mod 16QAM %',nr_64qam_1 as 'NR DL Mod 64QAM %',nr_256qam_1 as 'NR DL Mod 256QAM %',nr_1024qam_1 as 'NR DL Mod 1024QAM %' from nr_cell_meas''',
    '''select nr_ul_num_rb as 'NR UL Num RB',nr_ul_modulation_order as 'NR UL Modulation' from nr_deb_stat''',
    '''select nr_ul_qpsk_1 as 'NR UL Mod QPSK %',nr_ul_16qam_1 as 'NR UL Mod 16QAM %',nr_ul_64qam_1 as 'NR UL Mod 64QAM %',nr_ul_256qam_1 as 'NR UL Mod 256QAM %',nr_ul_1024qam_1 as 'NR UL Mod 1024QAM %' from nr_cell_meas'''
    ]