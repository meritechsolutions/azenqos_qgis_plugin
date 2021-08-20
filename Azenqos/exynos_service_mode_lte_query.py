RADIO_SELECT_FROM_PART = '''
select log_hash, time,
exynos_basic_info_lte_band as 'LTE Band',
exynos_basic_info_lte_dl_earfcn as 'LTE EARFCN',
exynos_basic_info_lte_pci as 'LTE PCI',
exynos_basic_info_lte_rsrp as 'LTE RSRP',
exynos_basic_info_lte_rsrq as 'LTE RSRQ',
exynos_basic_info_lte_sinr as 'LTE SINR',
exynos_basic_info_lte_rssi as 'LTE RSSI',
exynos_basic_info_lte_rrc_state as 'LTE RRC State',
exynos_basic_info_lte_pcell_tm as "LTE PCell TM",
exynos_basic_info_lte_mimo_ri as 'LTE RI',
exynos_basic_info_lte_bw_mhz as 'LTE Bandwidth (MHz)',
exynos_basic_info_lte_ant_rsrp_diff as 'LTE Ant RSRP Diff',
exynos_basic_info_lte_ant_rsrp_diff_avg as 'LTE Ant RSRP Diff avg',
exynos_basic_info_lte_tx_power as 'LTE TxPower',
exynos_basic_info_lte_ul_earfcn as 'LTE UL EARFCN'
from exynos_basic_info_lte
'''


DATA_SELECT_FROM_PART = '''
select log_hash, time,
exynos_basic_info_lte_ca as 'LTE CA',
exynos_basic_info_lte_sc_num as 'LTE Sc num',
exynos_basic_info_lte_tp_combined_dl_mbps as 'LTE DL througput (MBps)',
exynos_basic_info_lte_tp_combined_ul_mbps as 'LTE UL througput (MBps)',
exynos_basic_info_lte_dl_mcs1 as 'LTE DL MCS1',
exynos_basic_info_lte_dl_mcs2 as 'LTE DL MCS2',
exynos_basic_info_lte_ul_mcs1 as 'LTE UL MCS1',
exynos_basic_info_lte_n_dl_rb as 'LTE DL N RB',
exynos_basic_info_lte_n_dl_rb_max as 'LTE DL N RB max',
exynos_basic_info_lte_n_ul_rb as 'LTE UL N RB',
exynos_basic_info_lte_n_dl_rb_max as 'LTE UL N RB max'
from exynos_basic_info_lte
'''


REG_SELECT_FROM_PART = '''
select log_hash, time,
exynos_basic_info_lte_home_plmn as 'Home PLMN',
exynos_basic_info_lte_reg_plmn as 'Reg PLMN',
exynos_basic_info_lte_tac as 'LTE TAC',
exynos_basic_info_lte_eci as 'LTE ECI',
exynos_basic_info_lte_ps_cause as 'LTE PS Cause',
exynos_basic_info_lte_cs_cause as 'LTE CS Cause',
exynos_basic_info_lte_wakeup_info as 'LTE WakeupInfo'
from exynos_basic_info_lte
'''

QUERY_LIST = [
RADIO_SELECT_FROM_PART,
DATA_SELECT_FROM_PART,
REG_SELECT_FROM_PART,
]