LTE_RRC_SIB_SQL_LIST = [
    '''
    select log_hash, time,
    lte_sib1_mcc as 'SIB1 MCC',
    lte_sib1_mnc as 'SIB1 MNC',
    lte_sib1_tac as 'SIB1 TAC',
    lte_sib1_eci as 'SIB1 ECI (Cell ID)',
    lte_sib1_enb_id as 'SIB1 eNodeB ID',
    lte_sib1_local_cell_id as 'SIB1 LCI'
    from lte_sib1_info
    ''',
    '''
    select 
    lte_transmission_mode_l3 as 'Transmission Mode (RRC-tm)' 
    from lte_rrc_transmode_info''',
    '''
    select 
    lte_rrc_state as 'RRC State' 
    from lte_rrc_state
    '''
    ]

LTE_RADIO_PARAMS_SQL_LIST_DICT = {
    "1":[
        '''
        select log_hash, time as Time,
        lte_band_1 as Band,
        lte_earfcn_1 as EARFCN,
        lte_physical_cell_id_1 as PCI,
        lte_inst_rsrp_1 as RSRP,
        lte_inst_rsrq_1 as RSRQ,
        lte_sinr_1 as SINR,
        lte_inst_rssi_1 as RSSI
        from lte_cell_meas
        ''',
        '''select lte_tx_power as 'TxPower' from lte_tx_power''',
        '''select lte_pusch_tx_power as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select lte_pucch_tx_power as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select lte_ta as 'TA' from lte_frame_timing'''
    ],
    "2":[
        '''
        select '' as log_hash, '' as Time,
        lte_band_2 as Band,
        lte_earfcn_2 as EARFCN,
        lte_physical_cell_id_2 as PCI,
        lte_inst_rsrp_2 as RSRP,
        lte_inst_rsrq_2 as RSRQ,
        lte_sinr_2 as SINR,
        lte_inst_rssi_2 as RSSI
        from lte_cell_meas
        ''',
        '''select '' as 'TxPower' from lte_tx_power''',
        '''select '' as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select '' as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select '' as 'TA' from lte_frame_timing'''
    ],
    "3":[
        '''
        select '' as log_hash, '' as Time,
        lte_band_3 as Band,
        lte_earfcn_3 as EARFCN,
        lte_physical_cell_id_3 as PCI,
        lte_inst_rsrp_3 as RSRP,
        lte_inst_rsrq_3 as RSRQ,
        lte_sinr_3 as SINR,
        lte_inst_rssi_3 as RSSI
        from lte_cell_meas
        ''',
        '''select '' as 'TxPower' from lte_tx_power''',
        '''select '' as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select '' as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select '' as 'TA' from lte_frame_timing'''
    ],
    "4":[
        '''
        select '' as log_hash, '' as Time,
        lte_band_4 as Band,
        lte_earfcn_4 as EARFCN,
        lte_physical_cell_id_4 as PCI,
        lte_inst_rsrp_4 as RSRP,
        lte_inst_rsrq_4 as RSRQ,
        lte_sinr_4 as SINR,
        lte_inst_rssi_4 as RSSI
        from lte_cell_meas
        ''',
        '''select '' as 'TxPower' from lte_tx_power''',
        '''select '' as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select '' as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select '' as 'TA' from lte_frame_timing'''
    ],
}

LTE_SERV_AND_NEIGH_SQL_LIST_DICT = {
    "EARFCN":[
        '''
        select log_hash, time as Time,
        lte_earfcn_1 as PCell,
        lte_earfcn_2 as SCell1,
        lte_earfcn_3 as SCell2,
        lte_earfcn_4 as SCell3
        from lte_cell_meas
        ''',
        '''
        select
        lte_neigh_earfcn_1 as Neigh1,
        lte_neigh_earfcn_2 as Neigh2,
        lte_neigh_earfcn_3 as Neigh3,
        lte_neigh_earfcn_4 as Neigh4,
        lte_neigh_earfcn_5 as Neigh5,
        lte_neigh_earfcn_6 as Neigh6,
        lte_neigh_earfcn_7 as Neigh7,
        lte_neigh_earfcn_8 as Neigh8
        from lte_neigh_meas
        ''',
    ],
    "PCI":[
        '''
        select '' as log_hash, '' as Time,
        lte_physical_cell_id_1 as PCell,
        lte_physical_cell_id_2 as SCell1,
        lte_physical_cell_id_3 as SCell2,
        lte_physical_cell_id_4 as SCell3
        from lte_cell_meas
        ''',
        '''
        select
        lte_neigh_physical_cell_id_1 as Neigh1,
        lte_neigh_physical_cell_id_2 as Neigh2,
        lte_neigh_physical_cell_id_3 as Neigh3,
        lte_neigh_physical_cell_id_4 as Neigh4,
        lte_neigh_physical_cell_id_5 as Neigh5,
        lte_neigh_physical_cell_id_6 as Neigh6,
        lte_neigh_physical_cell_id_7 as Neigh7,
        lte_neigh_physical_cell_id_8 as Neigh8
        from lte_neigh_meas
        ''',
    ],
    "RSRP":[
        '''
        select '' as log_hash, '' as Time,
        lte_inst_rsrp_1 as PCell,
        lte_inst_rsrp_2 as SCell1,
        lte_inst_rsrp_3 as SCell2,
        lte_inst_rsrp_4 as SCell3
        from lte_cell_meas
        ''',
        '''
        select
        lte_neigh_rsrp_1 as Neigh1,
        lte_neigh_rsrp_2 as Neigh2,
        lte_neigh_rsrp_3 as Neigh3,
        lte_neigh_rsrp_4 as Neigh4,
        lte_neigh_rsrp_5 as Neigh5,
        lte_neigh_rsrp_6 as Neigh6,
        lte_neigh_rsrp_7 as Neigh7,
        lte_neigh_rsrp_8 as Neigh8
        from lte_neigh_meas
        ''',
    ],
    "RSRQ":[
        '''
        select '' as log_hash, '' as Time,
        lte_inst_rsrq_1 as PCell,
        lte_inst_rsrq_2 as SCell1,
        lte_inst_rsrq_3 as SCell2,
        lte_inst_rsrq_4 as SCell3
        from lte_cell_meas
        ''',
        '''
        select
        lte_neigh_rsrq_1 as Neigh1,
        lte_neigh_rsrq_2 as Neigh2,
        lte_neigh_rsrq_3 as Neigh3,
        lte_neigh_rsrq_4 as Neigh4,
        lte_neigh_rsrq_5 as Neigh5,
        lte_neigh_rsrq_6 as Neigh6,
        lte_neigh_rsrq_7 as Neigh7,
        lte_neigh_rsrq_8 as Neigh8
        from lte_neigh_meas
        ''',
    ],
    "SINR":[
        '''
        select '' as log_hash, '' as Time,
        lte_sinr_1 as PCell,
        lte_sinr_2 as SCell1,
        lte_sinr_3 as SCell2,
        lte_sinr_4 as SCell3
        from lte_cell_meas
        ''',
        '''
        select
        '' as Neigh1,
        '' as Neigh2,
        '' as Neigh3,
        '' as Neigh4,
        '' as Neigh5,
        '' as Neigh6,
        '' as Neigh7,
        '' as Neigh8
        from lte_neigh_meas
        ''',
    ],
}

LTE_RLC_SQL_LIST_DICT = {
    "1":[
        '''
        select log_hash, time as Time,
        lte_rlc_dl_tp_mbps as 'DL TP(Mbps)',
        lte_rlc_dl_tp as 'DL TP(Kbps)',
        lte_rlc_n_bearers as 'N Bearers',
        lte_rlc_per_rb_dl_rb_mode_1 as 'Mode',
        lte_rlc_per_rb_dl_rb_type_1 as 'Type',
        lte_rlc_per_rb_dl_rb_id_1 as 'RB-ID',
        lte_rlc_per_rb_cfg_index_1 as 'Index',
        lte_rlc_per_rb_dl_tp_1 as 'TP Mbps'
        from lte_rlc_stats
        ''',
        '''select lte_tx_power as 'TxPower' from lte_tx_power''',
        '''select lte_pusch_tx_power as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select lte_pucch_tx_power as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select lte_ta as 'TA' from lte_frame_timing'''
    ],
    "2":[
        '''
        select '' as log_hash, '' as Time,
        lte_rlc_dl_tp_mbps as 'DL TP(Mbps)',
        lte_rlc_dl_tp as 'DL TP(Kbps)',
        lte_rlc_n_bearers as 'N Bearers',
        lte_rlc_per_rb_dl_rb_mode_2 as 'Mode',
        lte_rlc_per_rb_dl_rb_type_2 as 'Type',
        lte_rlc_per_rb_dl_rb_id_2 as 'RB-ID',
        lte_rlc_per_rb_cfg_index_2 as 'Index',
        lte_rlc_per_rb_dl_tp_2 as 'TP Mbps'
        from lte_rlc_stats
        ''',
        '''select lte_tx_power as 'TxPower' from lte_tx_power''',
        '''select lte_pusch_tx_power as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select lte_pucch_tx_power as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select lte_ta as 'TA' from lte_frame_timing'''
    ],
    "3":[
        '''
        select '' as log_hash, '' as Time,
        lte_rlc_dl_tp_mbps as 'DL TP(Mbps)',
        lte_rlc_dl_tp as 'DL TP(Kbps)',
        lte_rlc_n_bearers as 'N Bearers',
        lte_rlc_per_rb_dl_rb_mode_3 as 'Mode',
        lte_rlc_per_rb_dl_rb_type_3 as 'Type',
        lte_rlc_per_rb_dl_rb_id_3 as 'RB-ID',
        lte_rlc_per_rb_cfg_index_3 as 'Index',
        lte_rlc_per_rb_dl_tp_3 as 'TP Mbps'
        from lte_rlc_stats
        ''',
        '''select lte_tx_power as 'TxPower' from lte_tx_power''',
        '''select lte_pusch_tx_power as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select lte_pucch_tx_power as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select lte_ta as 'TA' from lte_frame_timing'''
    ],
    "4":[
        '''
        select '' as log_hash, '' as Time,
        lte_rlc_dl_tp_mbps as 'DL TP(Mbps)',
        lte_rlc_dl_tp as 'DL TP(Kbps)',
        lte_rlc_n_bearers as 'N Bearers',
        lte_rlc_per_rb_dl_rb_mode_4 as 'Mode',
        lte_rlc_per_rb_dl_rb_type_4 as 'Type',
        lte_rlc_per_rb_dl_rb_id_4 as 'RB-ID',
        lte_rlc_per_rb_cfg_index_4 as 'Index',
        lte_rlc_per_rb_dl_tp_4 as 'TP Mbps'
        from lte_rlc_stats
        ''',
        '''select lte_tx_power as 'TxPower' from lte_tx_power''',
        '''select lte_pusch_tx_power as 'PUSCH TxPower' from lte_pusch_tx_info''',
        '''select lte_pucch_tx_power as 'PUCCH TxPower' from lte_pucch_tx_info''',
        '''select lte_ta as 'TA' from lte_frame_timing'''
    ],
}


LTE_PUCCH_PDSCH_SQL_LIST_DICT = {
    "1":[
        '''
        select log_hash, time as Time,
        '' as '--- PUCCH ---',
        lte_cqi_cw0_1 as 'CQI CW 0',
        lte_cqi_cw1_1 as 'CQI CW 1',
        lte_cqi_n_subbands_1 as 'CQI N Sub-bands',
        lte_rank_indication_1 as 'Rank Indicator'
        from lte_cqi
        ''',
        '''
        select
        '' as '--- PDSCH ---',
        lte_pdsch_serving_cell_id_1 as 'PDSCH Serving Cell ID',
        lte_pdsch_rnti_id_1 as 'PDSCH RNTI ID',
        lte_pdsch_rnti_type_1 as 'PDSCH RNTI Type',
        lte_pdsch_serving_n_tx_antennas_1 as 'PDSCH Serving N Tx Antennas',
        lte_pdsch_serving_n_rx_antennas_1 as 'PDSCH Serving N Rx Antennas',
        lte_pdsch_transmission_mode_current_1 as 'PDSCH Transmission Mode Current',
        lte_pdsch_spatial_rank_1 as 'PDSCH Spatial Rank',
        lte_pdsch_rb_allocation_slot0_1 as 'PDSCH Rb Allocation Slot 0',
        lte_pdsch_rb_allocation_slot1_1 as 'PDSCH Rb Allocation Slot 1',
        lte_pdsch_pmi_type_1 as 'PDSCH PMI Type',
        lte_pdsch_pmi_index_1 as 'PDSCH PMI Index',
        lte_pdsch_stream0_transport_block_size_bits_1 as 'PDSCH Stream_0 Block Size',
        lte_pdsch_stream0_modulation_1 as 'PDSCH Stream_0 Modulation',
        lte_pdsch_traffic_to_pilot_ratio_1 as 'PDSCH Traffic To Pilot Ratio',
        lte_pdsch_stream1_transport_block_size_bits_1 as 'PDSCH Stream_1 Block Size',
        lte_pdsch_stream1_modulation_1 as 'PDSCH Stream_1 Modulation'
        from lte_pdsch_meas
        '''
    ],
    "2":[
        '''
        select '' as log_hash, '' as Time,
        '' as '--- PUCCH ---',
        lte_cqi_cw0_2 as 'CQI CW 0',
        lte_cqi_cw1_2 as 'CQI CW 1',
        lte_cqi_n_subbands_2 as 'CQI N Sub-bands',
        lte_rank_indication_2 as 'Rank Indicator'
        from lte_cqi
        ''',
        '''
        select
        '' as '--- PDSCH ---',
        lte_pdsch_serving_cell_id_2 as 'PDSCH Serving Cell ID',
        lte_pdsch_rnti_id_2 as 'PDSCH RNTI ID',
        lte_pdsch_rnti_type_2 as 'PDSCH RNTI Type',
        lte_pdsch_serving_n_tx_antennas_2 as 'PDSCH Serving N Tx Antennas',
        lte_pdsch_serving_n_rx_antennas_2 as 'PDSCH Serving N Rx Antennas',
        lte_pdsch_transmission_mode_current_2 as 'PDSCH Transmission Mode Current',
        lte_pdsch_spatial_rank_2 as 'PDSCH Spatial Rank',
        lte_pdsch_rb_allocation_slot0_2 as 'PDSCH Rb Allocation Slot 0',
        lte_pdsch_rb_allocation_slot1_2 as 'PDSCH Rb Allocation Slot 1',
        lte_pdsch_pmi_type_2 as 'PDSCH PMI Type',
        lte_pdsch_pmi_index_2 as 'PDSCH PMI Index',
        lte_pdsch_stream0_transport_block_size_bits_2 as 'PDSCH Stream_0 Block Size',
        lte_pdsch_stream0_modulation_2 as 'PDSCH Stream_0 Modulation',
        lte_pdsch_traffic_to_pilot_ratio_2 as 'PDSCH Traffic To Pilot Ratio',
        lte_pdsch_stream1_transport_block_size_bits_2 as 'PDSCH Stream_1 Block Size',
        lte_pdsch_stream1_modulation_2 as 'PDSCH Stream_1 Modulation'
        from lte_pdsch_meas
        '''
    ],
    "3":[
        '''
        select '' as log_hash, '' as Time,
        '' as '--- PUCCH ---',
        lte_cqi_cw0_3 as 'CQI CW 0',
        lte_cqi_cw1_3 as 'CQI CW 1',
        lte_cqi_n_subbands_3 as 'CQI N Sub-bands',
        lte_rank_indication_3 as 'Rank Indicator'
        from lte_cqi
        ''',
        '''
        select
        '' as '--- PDSCH ---',
        lte_pdsch_serving_cell_id_3 as 'PDSCH Serving Cell ID',
        lte_pdsch_rnti_id_3 as 'PDSCH RNTI ID',
        lte_pdsch_rnti_type_3 as 'PDSCH RNTI Type',
        lte_pdsch_serving_n_tx_antennas_3 as 'PDSCH Serving N Tx Antennas',
        lte_pdsch_serving_n_rx_antennas_3 as 'PDSCH Serving N Rx Antennas',
        lte_pdsch_transmission_mode_current_3 as 'PDSCH Transmission Mode Current',
        lte_pdsch_spatial_rank_3 as 'PDSCH Spatial Rank',
        lte_pdsch_rb_allocation_slot0_3 as 'PDSCH Rb Allocation Slot 0',
        lte_pdsch_rb_allocation_slot1_3 as 'PDSCH Rb Allocation Slot 1',
        lte_pdsch_pmi_type_3 as 'PDSCH PMI Type',
        lte_pdsch_pmi_index_3 as 'PDSCH PMI Index',
        lte_pdsch_stream0_transport_block_size_bits_3 as 'PDSCH Stream_0 Block Size',
        lte_pdsch_stream0_modulation_3 as 'PDSCH Stream_0 Modulation',
        lte_pdsch_traffic_to_pilot_ratio_3 as 'PDSCH Traffic To Pilot Ratio',
        lte_pdsch_stream1_transport_block_size_bits_3 as 'PDSCH Stream_1 Block Size',
        lte_pdsch_stream1_modulation_3 as 'PDSCH Stream_1 Modulation'
        from lte_pdsch_meas
        '''
    ],
    "4":[
        '''
        select '' as log_hash, '' as Time,
        '' as '--- PUCCH ---',
        lte_cqi_cw0_4 as 'CQI CW 0',
        lte_cqi_cw1_4 as 'CQI CW 1',
        lte_cqi_n_subbands_4 as 'CQI N Sub-bands',
        lte_rank_indication_4 as 'Rank Indicator'
        from lte_cqi
        ''',
        '''
        select
        '' as '--- PDSCH ---',
        lte_pdsch_serving_cell_id_4 as 'PDSCH Serving Cell ID',
        lte_pdsch_rnti_id_4 as 'PDSCH RNTI ID',
        lte_pdsch_rnti_type_4 as 'PDSCH RNTI Type',
        lte_pdsch_serving_n_tx_antennas_4 as 'PDSCH Serving N Tx Antennas',
        lte_pdsch_serving_n_rx_antennas_4 as 'PDSCH Serving N Rx Antennas',
        lte_pdsch_transmission_mode_current_4 as 'PDSCH Transmission Mode Current',
        lte_pdsch_spatial_rank_4 as 'PDSCH Spatial Rank',
        lte_pdsch_rb_allocation_slot0_4 as 'PDSCH Rb Allocation Slot 0',
        lte_pdsch_rb_allocation_slot1_4 as 'PDSCH Rb Allocation Slot 1',
        lte_pdsch_pmi_type_4 as 'PDSCH PMI Type',
        lte_pdsch_pmi_index_4 as 'PDSCH PMI Index',
        lte_pdsch_stream0_transport_block_size_bits_4 as 'PDSCH Stream_0 Block Size',
        lte_pdsch_stream0_modulation_4 as 'PDSCH Stream_0 Modulation',
        lte_pdsch_traffic_to_pilot_ratio_4 as 'PDSCH Traffic To Pilot Ratio',
        lte_pdsch_stream1_transport_block_size_bits_4 as 'PDSCH Stream_1 Block Size',
        lte_pdsch_stream1_modulation_4 as 'PDSCH Stream_1 Modulation'
        from lte_pdsch_meas
        '''
    ],
}

LTE_VOLTE_SQL_LIST = [
    '''
    select 
    time as 'Time', 
    '' as 'Codec:' 
    from lte_volte_stats
    ''',
    '''
    select 
    gsm_speechcodecrx as 'AMR SpeechCodec-RX'
    from vocoder_info''',
    '''
    select
    gsm_speechcodectx as 'AMR SpeechCodec-TX'
    from vocoder_info''',
    '''
    select
    '' as 'Delay interval avg:',
    vocoder_amr_audio_packet_delay_avg as 'Audio Packet delay (ms.)' 
    from vocoder_info''',
    '''
    select 
    lte_volte_rtp_pkt_delay_avg as 'RTP Packet delay (ms.)'
    from lte_volte_stats''',
    '''
    select 
    '' as 'RTCP SR Params:',
    lte_volte_rtp_round_trip_time as 'RTCP Round trip time (ms.)'
    from lte_volte_stats''',
    '''
    select
    '' as 'RTCP SR Params - Jitter DL:',
    lte_volte_rtp_jitter_dl as 'RTCP SR Jitter DL (ts unit)'
    from lte_volte_stats''',
    '''
    select
    '' as 'RTCP SR Params - Jitter UL:',
    lte_volte_rtp_jitter_ul as 'RTCP SR Jitter UL (ts unit)'
    from lte_volte_stats''',
    '''
    select
    '' as 'RTCP SR Params - Packet loss rate:',
    lte_volte_rtp_packet_loss_rate_dl as 'RTCP SR Packet loss DL (%)'
    from lte_volte_stats''',
    '''
    select
    lte_volte_rtp_packet_loss_rate_ul as 'RTCP SR Packet loss UL (%)' 
    from lte_volte_stats''',
]

LTE_DATA_PARAMS_SQL_LIST_DICT = {
    "1":[
        '''
        select 
        lte_rrc_state as 'RRC State'
        from lte_rrc_state
        ''',
        '''
        select
        'DL' as 'Throughput',
        lte_l1_dl_throughput_all_carriers_mbps as 'L1 Combined (Mbps)',
        lte_l1_dl_throughput_all_carriers as 'L1 Combined (Kbps)'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdcp_dl_throughput_mbps as 'PDCP (Mbps)',
        lte_pdcp_dl_throughput as 'PDCP (Kbps)'
        from lte_pdcp_stats
        ''',
        '''
        select
        lte_rlc_dl_tp_mbps as 'RLC (Mbps)',
        lte_rlc_dl_tp as 'RLC (Kbps)'
        from lte_rlc_stats
        ''',
        '''
        select
        lte_mac_dl_tp as 'MAC (Kbps)'
        from lte_mac_ul_tx_stat
        ''',
        '''
        select
        lte_transmission_mode_l3 as 'TransMode RRC tm'
        from lte_rrc_transmode_info
        ''',
        '''
        select
        'PCC' as '',
        lte_l1_throughput_mbps_1 as 'L1 DL TP (Mbps)'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_l1_ul_throughput_mbps_1 as 'L1 UL TP (Mbps)'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdsch_transmission_mode_current_1 as 'TransMode Cur'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_earfcn_1 as 'EARFCN'
        from lte_cell_meas
        ''',
        '''
        select
        lte_pdsch_serving_cell_id_1 as 'PCI'
        from lte_pdsch_meas
        ''',
        '''
        select
        '--- PUSCH Stats ---',
        lte_l1_ul_n_rbs_1 as 'PRB Alloc UL',
        lte_ul_mcs_index_1 as 'MCS Index UL',
        lte_pusch_modulation_1 as 'Modulation UL',
        lte_l1_ul_bler_1 as 'L1 UL Bler'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdcch_dci_1 as 'DCI'
        from lte_pdcch_dec_result
        ''',
        '''
        select
        '--- PDSCH Stats ---',
        lte_bler_1 as 'BLER'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_serving_n_tx_antennas_1 as 'Serv N Tx Ant',
        lte_pdsch_serving_n_rx_antennas_1 as 'Serv N Rx Ant',
        lte_pdsch_spatial_rank_1 as 'Spatial Rank'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_rank_indication_1 as 'Rank Ind',
        lte_cqi_cw0_1 as 'CQI CW0',
        lte_cqi_cw1_1 as 'CQI CW1'
        from lte_cqi
        ''',
        '''
        select
        lte_pdsch_n_rb_allocated_latest_1 as 'PRB Alloc'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_max_n_rb_1 as 'PRB Ma'
        from lte_mib_info
        ''',
        '''
        select
        lte_prb_alloc_in_bandwidth_percent_latest_1 as 'PRB Util (alloc/bw) %'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_dl_bandwidth_mhz_1 as 'DL Bandwidth (MHz)'
        from lte_mib_info
        ''',
        '''
        select
        lte_sib2_ul_bandwidth_mhz as 'PCC UL Bw (Mhz)'
        from lte_sib2_info
        ''',
        '''
        select
        lte_pdsch_sched_percent_1 as 'Time Scheduled %',
        lte_mcs_index_1 as 'MCS Index'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_stream0_transport_block_size_bits_1 as 'BlockSizeBits_0',
        lte_pdsch_stream0_modulation_1 as 'Modulation_0',
        lte_pdsch_stream1_transport_block_size_bits_1 as 'BlockSizeBits_1',
        lte_pdsch_stream1_modulation_1 as 'Modulation_1',
        lte_pdsch_traffic_to_pilot_ratio_1 as 'TrafficToPilot Ratio',
        lte_pdsch_rnti_type_1 as 'RNTI Type',
        lte_pdsch_rnti_id_1 as 'RNTI ID',
        lte_pdsch_pmi_type_1 as 'PMI Type',
        lte_pdsch_pmi_index_1 as 'PMI Index'
        from lte_pdsch_meas
        ''',
    ],
    "2":[
        '''
        select 
        '' as 'RRC State'
        from lte_rrc_state
        ''',
        '''
        select
        'UL' as 'Throughput',
        lte_l1_ul_throughput_all_carriers_mbps_1 as 'L1 Combined (Mbps)',
        lte_l1_ul_throughput_all_carriers_1 as 'L1 Combined (Kbps)'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdcp_ul_throughput_mbps as 'PDCP (Mbps)',
        lte_pdcp_ul_throughput as 'PDCP (Kbps)'
        from lte_pdcp_stats
        ''',
        '''
        select
        lte_rlc_ul_tp_mbps as 'RLC (Mbps)',
        lte_rlc_ul_tp as 'RLC (Kbps)'
        from lte_rlc_stats
        ''',
        '''
        select
        lte_mac_ul_tp as 'MAC (Kbps)'
        from lte_mac_ul_tx_stat
        ''',
        '''
        select
        '' as 'TransMode RRC tm'
        from lte_rrc_transmode_info
        ''',
        '''
        select
        'SCC0' as '',
        lte_l1_throughput_mbps_2 as 'L1 DL TP (Mbps)'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_l1_ul_throughput_mbps_2 as 'L1 UL TP (Mbps)'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdsch_transmission_mode_current_2 as 'TransMode Cur'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_earfcn_2 as 'EARFCN'
        from lte_cell_meas
        ''',
        '''
        select
        lte_pdsch_serving_cell_id_2 as 'PCI'
        from lte_pdsch_meas
        ''',
        '''
        select
        '--- PUSCH Stats ---',
        lte_l1_ul_n_rbs_2 as 'PRB Alloc UL',
        lte_ul_mcs_index_2 as 'MCS Index UL',
        lte_pusch_modulation_2 as 'Modulation UL',
        lte_l1_ul_bler_2 as 'L1 UL Bler'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdcch_dci_2 as 'DCI'
        from lte_pdcch_dec_result
        ''',
        '''
        select
        '--- PDSCH Stats ---',
        lte_bler_2 as 'BLER'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_serving_n_tx_antennas_2 as 'Serv N Tx Ant',
        lte_pdsch_serving_n_rx_antennas_2 as 'Serv N Rx Ant',
        lte_pdsch_spatial_rank_2 as 'Spatial Rank'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_rank_indication_2 as 'Rank Ind',
        lte_cqi_cw0_2 as 'CQI CW0',
        lte_cqi_cw1_2 as 'CQI CW1'
        from lte_cqi
        ''',
        '''
        select
        lte_pdsch_n_rb_allocated_latest_2 as 'PRB Alloc'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_max_n_rb_2 as 'PRB Ma'
        from lte_mib_info
        ''',
        '''
        select
        lte_prb_alloc_in_bandwidth_percent_latest_2 as 'PRB Util (alloc/bw) %'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_dl_bandwidth_mhz_2 as 'DL Bandwidth (MHz)'
        from lte_mib_info
        ''',
        '''
        select
        '' as 'PCC UL Bw (Mhz)'
        from lte_sib2_info
        ''',
        '''
        select
        lte_pdsch_sched_percent_2 as 'Time Scheduled %',
        lte_mcs_index_1 as 'MCS Index'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_stream0_transport_block_size_bits_2 as 'BlockSizeBits_0',
        lte_pdsch_stream0_modulation_2 as 'Modulation_0',
        lte_pdsch_stream1_transport_block_size_bits_2 as 'BlockSizeBits_1',
        lte_pdsch_stream1_modulation_2 as 'Modulation_1',
        lte_pdsch_traffic_to_pilot_ratio_2 as 'TrafficToPilot Ratio',
        lte_pdsch_rnti_type_2 as 'RNTI Type',
        lte_pdsch_rnti_id_2 as 'RNTI ID',
        lte_pdsch_pmi_type_2 as 'PMI Type',
        lte_pdsch_pmi_index_2 as 'PMI Index'
        from lte_pdsch_meas
        ''',
    ],
    "3":[
        '''
        select 
        '' as 'RRC State'
        from lte_rrc_state
        ''',
        '''
        select
        '' as 'Throughput',
        '' as 'L1 Combined (Mbps)',
        '' as 'L1 Combined (Kbps)'
        from lte_l1_ul_tp
        ''',
        '''
        select
        '' as 'PDCP (Mbps)',
        '' as 'PDCP (Kbps)'
        from lte_pdcp_stats
        ''',
        '''
        select
        '' as 'RLC (Mbps)',
        '' as 'RLC (Kbps)'
        from lte_rlc_stats
        ''',
        '''
        select
        '' as 'MAC (Kbps)'
        from lte_mac_ul_tx_stat
        ''',
        '''
        select
        '' as 'TransMode RRC tm'
        from lte_rrc_transmode_info
        ''',
        '''
        select
        'SCC1' as '',
        lte_l1_throughput_mbps_3 as 'L1 DL TP (Mbps)'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_l1_ul_throughput_mbps_3 as 'L1 UL TP (Mbps)'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdsch_transmission_mode_current_3 as 'TransMode Cur'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_earfcn_3 as 'EARFCN'
        from lte_cell_meas
        ''',
        '''
        select
        lte_pdsch_serving_cell_id_3 as 'PCI'
        from lte_pdsch_meas
        ''',
        '''
        select
        '--- PUSCH Stats ---',
        lte_l1_ul_n_rbs_3 as 'PRB Alloc UL',
        lte_ul_mcs_index_3 as 'MCS Index UL',
        lte_pusch_modulation_3 as 'Modulation UL',
        lte_l1_ul_bler_3 as 'L1 UL Bler'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdcch_dci_3 as 'DCI'
        from lte_pdcch_dec_result
        ''',
        '''
        select
        '--- PDSCH Stats ---',
        lte_bler_3 as 'BLER'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_serving_n_tx_antennas_3 as 'Serv N Tx Ant',
        lte_pdsch_serving_n_rx_antennas_3 as 'Serv N Rx Ant',
        lte_pdsch_spatial_rank_3 as 'Spatial Rank'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_rank_indication_3 as 'Rank Ind',
        lte_cqi_cw0_3 as 'CQI CW0',
        lte_cqi_cw1_3 as 'CQI CW1'
        from lte_cqi
        ''',
        '''
        select
        lte_pdsch_n_rb_allocated_latest_3 as 'PRB Alloc'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_max_n_rb_3 as 'PRB Ma'
        from lte_mib_info
        ''',
        '''
        select
        lte_prb_alloc_in_bandwidth_percent_latest_3 as 'PRB Util (alloc/bw) %'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_dl_bandwidth_mhz_3 as 'DL Bandwidth (MHz)'
        from lte_mib_info
        ''',
        '''
        select
        '' as 'PCC UL Bw (Mhz)'
        from lte_sib2_info
        ''',
        '''
        select
        lte_pdsch_sched_percent_3 as 'Time Scheduled %',
        lte_mcs_index_1 as 'MCS Index'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_stream0_transport_block_size_bits_3 as 'BlockSizeBits_0',
        lte_pdsch_stream0_modulation_3 as 'Modulation_0',
        lte_pdsch_stream1_transport_block_size_bits_3 as 'BlockSizeBits_1',
        lte_pdsch_stream1_modulation_3 as 'Modulation_1',
        lte_pdsch_traffic_to_pilot_ratio_3 as 'TrafficToPilot Ratio',
        lte_pdsch_rnti_type_3 as 'RNTI Type',
        lte_pdsch_rnti_id_3 as 'RNTI ID',
        lte_pdsch_pmi_type_3 as 'PMI Type',
        lte_pdsch_pmi_index_3 as 'PMI Index'
        from lte_pdsch_meas
        ''',
    ],
    "4":[
        '''
        select 
        '' as 'RRC State'
        from lte_rrc_state
        ''',
        '''
        select
        '' as 'Throughput',
        '' as 'L1 Combined (Mbps)',
        '' as 'L1 Combined (Kbps)'
        from lte_l1_ul_tp
        ''',
        '''
        select
        '' as 'PDCP (Mbps)',
        '' as 'PDCP (Kbps)'
        from lte_pdcp_stats
        ''',
        '''
        select
        '' as 'RLC (Mbps)',
        '' as 'RLC (Kbps)'
        from lte_rlc_stats
        ''',
        '''
        select
        '' as 'MAC (Kbps)'
        from lte_mac_ul_tx_stat
        ''',
        '''
        select
        '' as 'TransMode RRC tm'
        from lte_rrc_transmode_info
        ''',
        '''
        select
        'SCC2' as '',
        lte_l1_throughput_mbps_4 as 'L1 DL TP (Mbps)'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_l1_ul_throughput_mbps_4 as 'L1 UL TP (Mbps)'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdsch_transmission_mode_current_4 as 'TransMode Cur'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_earfcn_4 as 'EARFCN'
        from lte_cell_meas
        ''',
        '''
        select
        lte_pdsch_serving_cell_id_4 as 'PCI'
        from lte_pdsch_meas
        ''',
        '''
        select
        '--- PUSCH Stats ---',
        lte_l1_ul_n_rbs_4 as 'PRB Alloc UL',
        lte_ul_mcs_index_4 as 'MCS Index UL',
        lte_pusch_modulation_4 as 'Modulation UL',
        lte_l1_ul_bler_4 as 'L1 UL Bler'
        from lte_l1_ul_tp
        ''',
        '''
        select
        lte_pdcch_dci_4 as 'DCI'
        from lte_pdcch_dec_result
        ''',
        '''
        select
        '--- PDSCH Stats ---',
        lte_bler_4 as 'BLER'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_serving_n_tx_antennas_4 as 'Serv N Tx Ant',
        lte_pdsch_serving_n_rx_antennas_4 as 'Serv N Rx Ant',
        lte_pdsch_spatial_rank_4 as 'Spatial Rank'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_rank_indication_4 as 'Rank Ind',
        lte_cqi_cw0_4 as 'CQI CW0',
        lte_cqi_cw1_4 as 'CQI CW1'
        from lte_cqi
        ''',
        '''
        select
        lte_pdsch_n_rb_allocated_latest_4 as 'PRB Alloc'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_max_n_rb_4 as 'PRB Ma'
        from lte_mib_info
        ''',
        '''
        select
        lte_prb_alloc_in_bandwidth_percent_latest_4 as 'PRB Util (alloc/bw) %'
        from lte_pdsch_meas
        ''',
        '''
        select
        lte_mib_dl_bandwidth_mhz_4 as 'DL Bandwidth (MHz)'
        from lte_mib_info
        ''',
        '''
        select
        '' as 'PCC UL Bw (Mhz)'
        from lte_sib2_info
        ''',
        '''
        select
        lte_pdsch_sched_percent_4 as 'Time Scheduled %',
        lte_mcs_index_1 as 'MCS Index'
        from lte_l1_dl_tp
        ''',
        '''
        select
        lte_pdsch_stream0_transport_block_size_bits_4 as 'BlockSizeBits_0',
        lte_pdsch_stream0_modulation_4 as 'Modulation_0',
        lte_pdsch_stream1_transport_block_size_bits_4 as 'BlockSizeBits_1',
        lte_pdsch_stream1_modulation_4 as 'Modulation_1',
        lte_pdsch_traffic_to_pilot_ratio_4 as 'TrafficToPilot Ratio',
        lte_pdsch_rnti_type_4 as 'RNTI Type',
        lte_pdsch_rnti_id_4 as 'RNTI ID',
        lte_pdsch_pmi_type_4 as 'PMI Type',
        lte_pdsch_pmi_index_4 as 'PMI Index'
        from lte_pdsch_meas
        ''',
    ],
}