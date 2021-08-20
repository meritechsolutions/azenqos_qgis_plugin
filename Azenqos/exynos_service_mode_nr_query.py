RADIO_SELECT_FROM_PART = '''
select log_hash, time,
exynos_basic_info_nr_mode_sa as 'SA Status',
exynos_basic_info_nr_endc_status as 'NSA ENDC Status',
exynos_basic_info_nr_band as 'NR Band',
exynos_basic_info_nr_arfcn as 'NR ARFCN',
exynos_basic_info_nr_pci as 'NR PCI',
exynos_basic_info_nr_ssb_index as 'NR SSB Index',
exynos_basic_info_nr_ssb_rsrp as 'NR SSB RSRP',
exynos_basic_info_nr_rsrp as 'NR RSRP',
exynos_basic_info_nr_rsrq as 'NR RSRQ',
exynos_basic_info_nr_rssi as 'NR RSSI',
exynos_basic_info_nr_sinr as 'NR SINR',
exynos_basic_info_nr_pdsch_sinr_1 as 'NR PDSCH SINR',
exynos_basic_info_nr_ch_bw as 'NR Bandwidth (MHz)',
exynos_basic_info_nr_scs as 'NR SCS',
exynos_basic_info_nr_bwp as 'NR BWP',
exynos_basic_info_nr_dss_status as 'NR DSS Status',
exynos_basic_info_nr_best_serving_ssb_index as 'Best Serv-SSB-Index',
exynos_basic_info_nr_best_serving_ssb_rsrp as 'Best Serv-SSB-RSRP',
exynos_basic_info_nr_no_sec_serv_cell as 'Num Sec-Serv-Cells',
exynos_basic_info_nr_txpwr as 'NR TxPwr',
exynos_basic_info_nr_endc_total_txpwr as 'NR ENDC TotalTxPwr',
'--- SA-only params ---',
exynos_basic_info_nr_rrc_state as 'NR RRC State'
from exynos_basic_info_nr
'''


DATA_SELECT_FROM_PART = '''
select log_hash, time,
exynos_basic_info_nr_sa_tp_dl_mbps as 'SA TP DL (MBps)',
exynos_basic_info_nr_sa_tp_ul_mbps as 'SA TP UL (MBps)',
exynos_basic_info_nr_endc_tp_combined_dl_mbps as 'ENDC Combined TP DL (MBps)',
exynos_basic_info_nr_endc_tp_nr_dl_mbps as 'ENDC NR TP DL (MBps)',
exynos_basic_info_nr_endc_tp_lte_dl_mbps as 'ENDC LTE TP DL (MBps)',
exynos_basic_info_nr_endc_tp_combined_ul_mbps as 'ENDC Combined TP UL (MBps)',
exynos_basic_info_nr_endc_tp_nr_ul_mbps as 'ENDC NR TP UL (MBps)',
exynos_basic_info_nr_endc_tp_lte_ul_mbps as 'ENDC LTE TP UL (MBps)',
exynos_basic_info_nr_cqi as 'NR CQI',
exynos_basic_info_nr_ri as 'NR RI',
exynos_basic_info_nr_num_layers as 'NR NumLayers',
exynos_basic_info_nr_mcs_dl as 'NR MCS DL',
exynos_basic_info_nr_mcs_ul as 'NR MCS UL',
exynos_basic_info_nr_bler_dl as 'NR BLER DL',
'--- SA-only params ---',
exynos_basic_info_nr_n_dl_rb as 'NR DL N RB',
exynos_basic_info_nr_n_dl_rb_max as 'NR DL N RB max',
exynos_basic_info_nr_n_ul_rb as 'NR UL N RB',
exynos_basic_info_nr_n_ul_rb_max as 'NR UL N RB max'
from exynos_basic_info_nr
'''


REG_SELECT_FROM_PART = '''
select log_hash, time,
'--- SA-only params ---',
exynos_basic_info_nr_mcc as 'NR MCC',
exynos_basic_info_nr_mnc as 'NR MNC',
exynos_basic_info_nr_tac as 'NR TAC',
exynos_basic_info_nr_cellid as 'NR CELLID',
exynos_basic_info_nr_cp as 'NR CP',
exynos_basic_info_nr_po as 'NR PO',
exynos_basic_info_nr_cdrx as 'NR CDRX'
from exynos_basic_info_nr
'''


QUERY_LIST = [
RADIO_SELECT_FROM_PART,
DATA_SELECT_FROM_PART,
REG_SELECT_FROM_PART,
]