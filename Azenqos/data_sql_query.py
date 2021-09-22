WIFI_ACTIVE_SQL_LIST = [
    '''
    select time as 'Time',
    wifi_active_bssid as 'BSSID',
    wifi_active_ssid as 'SSID',
    wifi_active_rssi as 'RSSI',
    wifi_active_ipaddr as 'IP Addr',
    wifi_active_linkspeed as 'Link Speed (Mbps.)',
    wifi_active_macaddr as 'MAC Addr',
    wifi_active_encryption as 'Encryption',
    wifi_active_channel as 'Ch.',
    wifi_active_freq as 'Freq',
    wifi_active_isp as 'ISP' 
    from wifi_active
    '''
]

GPRS_EDGE_SQL_LIST = [
    '''
    select time as 'Time',
    data_gprs_attach_duration as 'GPRS Attach Duration',
    data_pdp_context_activation_duration as 'PDP Context Activation Duration' 
    from umts_data_activation_stats
    ''',
    '''
    select data_gsm_rlc_ul_throughput as 'RLC DL Throughput (kbit/s)',
    data_gsm_rlc_dl_throughput as 'RLC UL Throughput (kbit/s)',
    data_egprs_dl_coding_scheme_index as 'DL Coding Scheme',
    data_egprs_ul_coding_scheme_index as 'UL Coding Scheme',
    data_gprs_timeslot_used_dl as 'DL Timeslot Used',
    data_gprs_timeslot_used_ul as 'Ul Timeslot Used',
    data_gprs_ci as 'GPRS C/I' 
    from data_egprs_stats
    '''
]

HSDPA_STATISTICS_SQL_LIST = [
    '''
    select time as 'Time',
    data_hsdpa_scheduled_rate as 'HSDPA Scheduled Rate',
    data_hsdpa_served_rate as 'HSDPA Served Rate',
    data_hsdpa_thoughput as 'HS-DSCH Throughput',
    data_hsdpa_sbler_on_1st_transmission as 'HSDPA SBLER on 1st transmission',
    data_hsdpa_sbler as 'HSDPA SBLER',
    data_hsdpa_num_codes_used_avg as 'HSDPA Num Codes Used Avg.',
    data_hsdpa_mod_qpsk_percent as 'HSDPA MOD QPSK Percent',
    data_hsdpa_mod_16qam_percent as 'HSDPA MOD 16QAM Percent',
    data_hspap_mod_64qam_percent as 'HSDPA MOD 64QAM Percent',
    data_hsdpa_meas_from_num_2ms_slots as 'HSDPA Meas from num 2MS slots',
    data_hsdpa_num_scch_demod_attempts as 'HSDPA Num SCCH DEMOD Attempts',
    data_hsdpa_num_demod_valid as 'HSDPA Num DEMOD Valid',
    data_hspap_dual_carrier_enabled as 'Data HSPAP Dual Carrier Enabled',
    data_hspap_64qam_configured as 'Data HSPAP 64QAM Configured',
    data_hspap_dual_carrier_enabled_percent as 'Data_HSPAP_DUAL_CARRIER_ENABLED_PERCENT',
    data_hspap_mimo_enabled as 'Data_HSPAP_MIMO_ENABLED',
    data_hspap_ue_category as 'Data_HSPAP_UE_CATEGORY',
    data_hspap_2tb_requested_percent as 'Data_HSPAP_2TB_REQUESTED_PERCENT',
    data_hspap_1tb_requested_percent as 'Data_HSPAP_1TB_REQUESTED_PERCENT',
    data_hsdpa_hs_scch_usage_percent as 'HSDPA HS-SCCH Usage Percent' 
    from wcdma_hsdpa_stats
    ''',
    '''
    select HSDPA CQI number avg. as 'data_hsdpa_cqi_number_avg',
    Data HSPAP CQI B as 'data_hspap_cqi_b',
    Data HSPAP CQI A as 'data_hspap_cqi_a',
    Data HSPAP CQI DC Primary Carrier as 'data_hspap_cqi_dc_primary_carrier',
    Data HSPAP CQI DC Secondary Carrier as 'data_hspap_cqi_dc_secondary_carrier' 
    from wcdma_hsdpa_cqi
    ''',
    '''
    select data_wcdma_rlc_dl_throughput as 'WCDMA RLC DL Throughput' 
    from data_wcdma_rlc_stats
    '''
]

HSUPA_STATISTICS_SQL_LIST = [
    '''
    select time as 'Time',
    data_hsupa_sample_duration as 'HSUPA Sample duration',
    data_hsupa_tti as 'HSUPA TTI',
    data_hsupa_sample_frames as 'HSUPA Sample frames',
    data_hsupa_p_happy_bit_ttis as 'HSUPA Happy bit TTIs (%)',
    data_hsupa_p_serving_rgch_up as 'HSUPA Serving RGCH Up (%)',
    data_hsupa_p_serving_rgch_down as 'HSUPA Serving RGCH Down (%)',
    data_hsupa_p_serving_rgch_hold as 'HSUPA Serving RGCH Hold (%)',
    data_hsupa_p_nonserving_rgch_down as 'HSUPA NonServing RGCH Down (%)',
    data_hsupa_p_nonserving_rgch_hold as 'HSUPA NonServing RGCH Hold (%)',
    data_hsupa_n_agch_receive_success as 'HSUPA N AGCH Receive success',
    data_hsupa_average_agch as 'HSUPA Average AGCH',
    data_hsupa_average_sgi as 'HSUPA Average SGI',
    data_hsupa_p_new_transmission as 'HSUPA new transmission (%)',
    data_hsupa_p_retransmission as 'HSUPA retransmission (%)',
    data_hsupa_p_dtx as 'HSUPA DTX (%)',
    data_hsupa_n_nack_after_max_retrans as 'HSUPA N NACK after max retrans',
    data_hsupa_n_mac_e_resets as 'HSUPA N MAC e Resets',
    data_hsupa_n_power_limited_ttis as 'HSUPA Power Limited TTIs (%)',
    data_hsupa_n_serving_grant_limited_ttis as 'HSUPA Serving Grant Limited TTIs (%)',
    data_hsupa_p_sbler as 'HSUPA SBLER (%)',
    data_hsupa_avg_raw_throughput as 'HSUPA Avg Raw Throughput',
    data_hsupa_avg_scheduled_throughput as 'HSUPA Avg Scheduled Throughput',
    data_hsupa_total_e_dpdch_throughput as 'HSUPA Total E DPDCH Throughput' 
    from wcdma_hsupa_stats''',
    '''
    select data_wcdma_rlc_ul_throughput as 'WCDMA RLC UL Throughput' 
    from data_wcdma_rlc_stats'''
]