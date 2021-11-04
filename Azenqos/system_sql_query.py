SYSTEM_TECHNOLOGY_SQL_LIST = [

]
rat_to_table_and_primary_where_dict = {
    "NR": "nr_cell_meas",
    "LTE": "lte_cell_meas",
    "WCDMA": "wcdma_cell_meas",
    "GSM": "gsm_cell_meas",
}
rat_to_main_param_dict = {
    "NR": "nr_servingbeam_ss_rsrp_1",
    "LTE": "lte_inst_rsrp_1",
    "WCDMA": "wcdma_aset_rscp_1",
    "GSM": "gsm_rxlev_sub_dbm",
}
for rat in rat_to_table_and_primary_where_dict:
    sql = "pd.read_sql('''select log_hash, time, {} as main_param, '{}' as technology from {}''',dbcon)".format(
        rat_to_main_param_dict[rat], rat, rat_to_table_and_primary_where_dict[rat]
    )
    if rat == "NR":
        sql += ".ffill(limit=5)"
    SYSTEM_TECHNOLOGY_SQL_LIST.append(sql)

GSM_WCDMA_SYSTEM_INFO_SQL_LIST = [
    '''select serving_system_mcc as 'MCC',serving_system_mnc as 'MNC',serving_system_lac as 'LAC',cm_service_status as 'Service Status',cm_service_domain as 'Service Domain',cm_service_capability as 'Service Capability',cm_system_mode as 'System Mode',cm_roaming_status as 'Roaming Status',cm_system_id_type as 'System ID Type' from serving_system''',
    '''select wcdma_rrc_state as 'WCDMA RRC State' from wcdma_rrc_state'''
]

LTE_SYSTEM_INFO_SQL_LIST = [
    '''select lte_sib1_mcc as 'MCC',lte_sib1_mnc as 'MNC',lte_sib1_tac as 'TAC',lte_sib1_eci as 'ECI' from lte_sib1_info''','''select serving_system_lac as 'LAC',cm_service_status as 'Service Status',cm_service_domain as 'Service Domain',cm_service_capability as 'Service Capability',cm_system_mode as 'System Mode',cm_roaming_status as 'Roaming Status',cm_system_id_type as 'System ID Type' from serving_system''',
    '''select lte_rrc_state as 'LTE RRC State' from lte_rrc_state''',
    '''select lte_emm_state as 'LTE EMM State' from lte_emm_state'''
]