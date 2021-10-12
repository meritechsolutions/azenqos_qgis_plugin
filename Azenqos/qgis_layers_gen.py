import contextlib
import os
import sqlite3

from PyQt5.QtCore import QVariant

try:
    from qgis.core import (
        QgsProject,
        QgsFeature,
        QgsField,
        QgsFields,
        QgsPointXY,
        QgsGeometry,
        QgsVectorLayer,
        QgsDataSourceUri
    )
except:
    pass
import pathlib
import db_preprocess
import fill_geom_in_location_df
import azq_utils


def dump_df_to_spatialite_db(df, dbfp, table, is_indoor=False):
    assert df is not None
    assert "log_hash" in df.columns
    assert "time" in df.columns

    if "lat" not in df.columns:
        if "positioning_lat" in df.columns:
            df["lat"] = df["positioning_lat"]
    if "lon" not in df.columns:
        if "positioning_lon" in df.columns:
            df["lon"] = df["positioning_lon"]

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        assert "lat" in df.columns and "lon" in df.columns
        if is_indoor:
            idf = df[["log_hash", "time", "lat", "lon"]]
            idf = idf.dropna(subset=["time"])
            idf = idf.drop_duplicates(subset='time').set_index('time')
            idf = idf.groupby('log_hash').apply(lambda sdf: sdf.interpolate(method='time'))
            idf = idf.reset_index()
            df["lat"] = idf["lat"]
            df["lon"] = idf["lon"]
            if "geom" in df.columns:
                del df["geom"]
        if 'geom' not in df.columns:
            df = fill_geom_in_location_df.fill_geom_in_location_df(df)
        assert 'geom' in df
        print("to_sql dbfp:", dbfp)
        df.to_sql(table, dbcon, dtype=db_preprocess.elm_table_main_col_types)
        sqlstr = """insert into geometry_columns values ('{}', 'geom', 'POINT', '2', 4326, 0);""".format(
            table
        )
        db_preprocess.prepare_spatialite_required_tables(dbcon)
        print("insert into geometry_columns view {} sqlstr: {}".format(table, sqlstr))
        dbcon.execute(sqlstr)
        dbcon.commit()
    assert os.path.isfile(dbfp)


def create_qgis_layer_from_spatialite_db(dbfp, table, label_col=None):
    '''
    # now we create from spatialite dbcon instead
    tmp_csv_fp = os.path.join(
        azq_utils.tmp_gen_path(), "tmp_csv_{}.csv".format(uuid.uuid4())
    )
<<<<<<< HEAD
    df.to_csv(tmp_csv_fp, index=False, quoting=csv.QUOTE_ALL)
    create_qgis_layer_csv(tmp_csv_fp, layer_name=layer_name, label_col=label_col)
    '''
    # https://qgis-docs.readthedocs.io/en/latest/docs/pyqgis_developer_cookbook/loadlayer.html
    schema = ''
    table = table
    uri = QgsDataSourceUri()
    uri.setDatabase(dbfp)
    uri.setDataSource(schema, table, 'geom')
    display_name = table
    layer = QgsVectorLayer(uri.uri(), display_name, 'spatialite')
    QgsProject.instance().addMapLayer(layer)


def create_qgis_layer_csv(csv_fp, layer_name="layer", x_field="lon", y_field="lat", label_col=None):
    print("create_qgis_layer_csv() label_col: {} START".format(label_col))
    uri = pathlib.Path(csv_fp).as_uri()
    uri += "?crs=epsg:4326&xField={}&yField={}".format(x_field, y_field)
    print("csv uri: {}".format(uri))
    layer = QgsVectorLayer(uri, layer_name, "delimitedtext")
    if label_col:
        layer.setCustomProperty("labeling", "pal")
        layer.setCustomProperty("labeling/enabled", "true")
        layer.setCustomProperty("labeling/fontFamily", "Arial")
        layer.setCustomProperty("labeling/fontSize", "10")
        layer.setCustomProperty("labeling/fieldName", label_col)
        layer.setCustomProperty("labeling/placement", "2")
    QgsProject.instance().addMapLayers([layer])
    print("create_qgis_layer_csv() DONE")


insert_list = [
    '''INSERT INTO "main"."nr_cell_meas" ("log_hash", "time", "modem_time", "posid", "seqid", "netid", "geom", "nr_band_1", "nr_band_2", "nr_band_3", "nr_band_4", "nr_band_5", "nr_band_6", "nr_band_7", "nr_band_8", "nr_band_type_1", "nr_band_type_2", "nr_band_type_3", "nr_band_type_4", "nr_band_type_5", "nr_band_type_6", "nr_band_type_7", "nr_band_type_8", "nr_bw_1", "nr_bw_2", "nr_bw_3", "nr_bw_4", "nr_bw_5", "nr_bw_6", "nr_bw_7", "nr_bw_8", "nr_ssb_scs_1", "nr_ssb_scs_2", "nr_ssb_scs_3", "nr_ssb_scs_4", "nr_ssb_scs_5", "nr_ssb_scs_6", "nr_ssb_scs_7", "nr_ssb_scs_8", "nr_dl_frequency_1", "nr_dl_frequency_2", "nr_dl_frequency_3", "nr_dl_frequency_4", "nr_dl_frequency_5", "nr_dl_frequency_6", "nr_dl_frequency_7", "nr_dl_frequency_8", "nr_dl_arfcn_1", "nr_dl_arfcn_2", "nr_dl_arfcn_3", "nr_dl_arfcn_4", "nr_dl_arfcn_5", "nr_dl_arfcn_6", "nr_dl_arfcn_7", "nr_dl_arfcn_8", "nr_servingbeam_pci_1", "nr_servingbeam_pci_2", "nr_servingbeam_pci_3", "nr_servingbeam_pci_4", "nr_servingbeam_pci_5", "nr_servingbeam_pci_6", "nr_servingbeam_pci_7", "nr_servingbeam_pci_8", "nr_servingbeam_ssb_index_1", "nr_servingbeam_ssb_index_2", "nr_servingbeam_ssb_index_3", "nr_servingbeam_ssb_index_4", "nr_servingbeam_ssb_index_5", "nr_servingbeam_ssb_index_6", "nr_servingbeam_ssb_index_7", "nr_servingbeam_ssb_index_8", "nr_servingbeam_ss_rsrp_1", "nr_servingbeam_ss_rsrp_2", "nr_servingbeam_ss_rsrp_3", "nr_servingbeam_ss_rsrp_4", "nr_servingbeam_ss_rsrp_5", "nr_servingbeam_ss_rsrp_6", "nr_servingbeam_ss_rsrp_7", "nr_servingbeam_ss_rsrp_8", "nr_servingbeam_ss_rsrq_1", "nr_servingbeam_ss_rsrq_2", "nr_servingbeam_ss_rsrq_3", "nr_servingbeam_ss_rsrq_4", "nr_servingbeam_ss_rsrq_5", "nr_servingbeam_ss_rsrq_6", "nr_servingbeam_ss_rsrq_7", "nr_servingbeam_ss_rsrq_8", "nr_servingbeam_ss_sinr_1", "nr_servingbeam_ss_sinr_2", "nr_servingbeam_ss_sinr_3", "nr_servingbeam_ss_sinr_4", "nr_servingbeam_ss_sinr_5", "nr_servingbeam_ss_sinr_6", "nr_servingbeam_ss_sinr_7", "nr_servingbeam_ss_sinr_8", "nr_numerology_scs_1", "nr_numerology_scs_2", "nr_numerology_scs_3", "nr_numerology_scs_4", "nr_numerology_scs_5", "nr_numerology_scs_6", "nr_numerology_scs_7", "nr_numerology_scs_8", "nr_servingbeam_csi_rsrq_1", "nr_servingbeam_csi_rsrq_2", "nr_servingbeam_csi_rsrq_3", "nr_servingbeam_csi_rsrq_4", "nr_servingbeam_csi_rsrq_5", "nr_servingbeam_csi_rsrq_6", "nr_servingbeam_csi_rsrq_7", "nr_servingbeam_csi_rsrq_8", "nr_servingbeam_csi_sinr_1", "nr_servingbeam_csi_sinr_2", "nr_servingbeam_csi_sinr_3", "nr_servingbeam_csi_sinr_4", "nr_servingbeam_csi_sinr_5", "nr_servingbeam_csi_sinr_6", "nr_servingbeam_csi_sinr_7", "nr_servingbeam_csi_sinr_8", "nr_servingbeam_csi_rssi_1", "nr_servingbeam_csi_rssi_2", "nr_servingbeam_csi_rssi_3", "nr_servingbeam_csi_rssi_4", "nr_servingbeam_csi_rssi_5", "nr_servingbeam_csi_rssi_6", "nr_servingbeam_csi_rssi_7", "nr_servingbeam_csi_rssi_8", "nr_pdsch_assign_num_1", "nr_pdsch_assign_num_2", "nr_pdsch_assign_num_3", "nr_pdsch_assign_num_4", "nr_pdsch_assign_num_5", "nr_pdsch_assign_num_6", "nr_pdsch_assign_num_7", "nr_pdsch_assign_num_8", "nr_pusch_assign_num_1", "nr_pusch_assign_num_2", "nr_pusch_assign_num_3", "nr_pusch_assign_num_4", "nr_pusch_assign_num_5", "nr_pusch_assign_num_6", "nr_pusch_assign_num_7", "nr_pusch_assign_num_8", "nr_dl_rb_1", "nr_dl_rb_2", "nr_dl_rb_3", "nr_dl_rb_4", "nr_dl_rb_5", "nr_dl_rb_6", "nr_dl_rb_7", "nr_dl_rb_8", "nr_dl_mcs_mode_1", "nr_dl_mcs_mode_2", "nr_dl_mcs_mode_3", "nr_dl_mcs_mode_4", "nr_dl_mcs_mode_5", "nr_dl_mcs_mode_6", "nr_dl_mcs_mode_7", "nr_dl_mcs_mode_8", "nr_pusch_dl_pathloss_1", "nr_pusch_dl_pathloss_2", "nr_pusch_dl_pathloss_3", "nr_pusch_dl_pathloss_4", "nr_pusch_dl_pathloss_5", "nr_pusch_dl_pathloss_6", "nr_pusch_dl_pathloss_7", "nr_pusch_dl_pathloss_8", "nr_pusch_mtpl_1", "nr_pusch_mtpl_2", "nr_pusch_mtpl_3", "nr_pusch_mtpl_4", "nr_pusch_mtpl_5", "nr_pusch_mtpl_6", "nr_pusch_mtpl_7", "nr_pusch_mtpl_8", "nr_pusch_f_i_1", "nr_pusch_f_i_2", "nr_pusch_f_i_3", "nr_pusch_f_i_4", "nr_pusch_f_i_5", "nr_pusch_f_i_6", "nr_pusch_f_i_7", "nr_pusch_f_i_8", "nr_pucch_dl_pathloss_1", "nr_pucch_dl_pathloss_2", "nr_pucch_dl_pathloss_3", "nr_pucch_dl_pathloss_4", "nr_pucch_dl_pathloss_5", "nr_pucch_dl_pathloss_6", "nr_pucch_dl_pathloss_7", "nr_pucch_dl_pathloss_8", "nr_pucch_mtpl_1", "nr_pucch_mtpl_2", "nr_pucch_mtpl_3", "nr_pucch_mtpl_4", "nr_pucch_mtpl_5", "nr_pucch_mtpl_6", "nr_pucch_mtpl_7", "nr_pucch_mtpl_8", "nr_pucch_tpc_command_1", "nr_pucch_tpc_command_2", "nr_pucch_tpc_command_3", "nr_pucch_tpc_command_4", "nr_pucch_tpc_command_5", "nr_pucch_tpc_command_6", "nr_pucch_tpc_command_7", "nr_pucch_tpc_command_8", "nr_pucch_g_i_1", "nr_pucch_g_i_2", "nr_pucch_g_i_3", "nr_pucch_g_i_4", "nr_pucch_g_i_5", "nr_pucch_g_i_6", "nr_pucch_g_i_7", "nr_pucch_g_i_8", "nr_pdsch_tx_mode_1", "nr_pdsch_tx_mode_2", "nr_pdsch_tx_mode_3", "nr_pdsch_tx_mode_4", "nr_pdsch_tx_mode_5", "nr_pdsch_tx_mode_6", "nr_pdsch_tx_mode_7", "nr_pdsch_tx_mode_8", "nr_srs_pc_adj_state_1", "nr_srs_pc_adj_state_2", "nr_srs_pc_adj_state_3", "nr_srs_pc_adj_state_4", "nr_srs_pc_adj_state_5", "nr_srs_pc_adj_state_6", "nr_srs_pc_adj_state_7", "nr_srs_pc_adj_state_8", "nr_srs_dl_pathloss_1", "nr_srs_dl_pathloss_2", "nr_srs_dl_pathloss_3", "nr_srs_dl_pathloss_4", "nr_srs_dl_pathloss_5", "nr_srs_dl_pathloss_6", "nr_srs_dl_pathloss_7", "nr_srs_dl_pathloss_8", "nr_ul_mcs_mode_1", "nr_ul_mcs_mode_2", "nr_ul_mcs_mode_3", "nr_ul_mcs_mode_4", "nr_ul_mcs_mode_5", "nr_ul_mcs_mode_6", "nr_ul_mcs_mode_7", "nr_ul_mcs_mode_8", "nr_ul_modulation_1", "nr_ul_modulation_2", "nr_ul_modulation_3", "nr_ul_modulation_4", "nr_ul_modulation_5", "nr_ul_modulation_6", "nr_ul_modulation_7", "nr_ul_modulation_8", "nr_ul_p2_bpsk_1", "nr_ul_p2_bpsk_2", "nr_ul_p2_bpsk_3", "nr_ul_p2_bpsk_4", "nr_ul_p2_bpsk_5", "nr_ul_p2_bpsk_6", "nr_ul_p2_bpsk_7", "nr_ul_p2_bpsk_8", "nr_ul_qpsk_1", "nr_ul_qpsk_2", "nr_ul_qpsk_3", "nr_ul_qpsk_4", "nr_ul_qpsk_5", "nr_ul_qpsk_6", "nr_ul_qpsk_7", "nr_ul_qpsk_8", "nr_ul_16qam_1", "nr_ul_16qam_2", "nr_ul_16qam_3", "nr_ul_16qam_4", "nr_ul_16qam_5", "nr_ul_16qam_6", "nr_ul_16qam_7", "nr_ul_16qam_8", "nr_ul_64qam_1", "nr_ul_64qam_2", "nr_ul_64qam_3", "nr_ul_64qam_4", "nr_ul_64qam_5", "nr_ul_64qam_6", "nr_ul_64qam_7", "nr_ul_64qam_8", "nr_ul_256qam_1", "nr_ul_256qam_2", "nr_ul_256qam_3", "nr_ul_256qam_4", "nr_ul_256qam_5", "nr_ul_256qam_6", "nr_ul_256qam_7", "nr_ul_256qam_8", "nr_ul_1024qam_1", "nr_ul_1024qam_2", "nr_ul_1024qam_3", "nr_ul_1024qam_4", "nr_ul_1024qam_5", "nr_ul_1024qam_6", "nr_ul_1024qam_7", "nr_ul_1024qam_8", "nr_ul_tx_mode_1", "nr_ul_tx_mode_2", "nr_ul_tx_mode_3", "nr_ul_tx_mode_4", "nr_ul_tx_mode_5", "nr_ul_tx_mode_6", "nr_ul_tx_mode_7", "nr_ul_tx_mode_8", "nr_wb_coi_1", "nr_wb_coi_2", "nr_wb_coi_3", "nr_wb_coi_4", "nr_wb_coi_5", "nr_wb_coi_6", "nr_wb_coi_7", "nr_wb_coi_8", "nr_num_rx_ant_1", "nr_num_rx_ant_2", "nr_num_rx_ant_3", "nr_num_rx_ant_4", "nr_num_rx_ant_5", "nr_num_rx_ant_6", "nr_num_rx_ant_7", "nr_num_rx_ant_8", "nr_num_ul_crc_pass_tb_1", "nr_num_ul_crc_pass_tb_2", "nr_num_ul_crc_pass_tb_3", "nr_num_ul_crc_pass_tb_4", "nr_num_ul_crc_pass_tb_5", "nr_num_ul_crc_pass_tb_6", "nr_num_ul_crc_pass_tb_7", "nr_num_ul_crc_pass_tb_8", "nr_num_ul_crc_fail_tb_1", "nr_num_ul_crc_fail_tb_2", "nr_num_ul_crc_fail_tb_3", "nr_num_ul_crc_fail_tb_4", "nr_num_ul_crc_fail_tb_5", "nr_num_ul_crc_fail_tb_6", "nr_num_ul_crc_fail_tb_7", "nr_num_ul_crc_fail_tb_8", "nr_ul_arfcn_1", "nr_ul_arfcn_2", "nr_ul_arfcn_3", "nr_ul_arfcn_4", "nr_ul_arfcn_5", "nr_ul_arfcn_6", "nr_ul_arfcn_7", "nr_ul_arfcn_8", "nr_ul_bw_1", "nr_ul_bw_2", "nr_ul_bw_3", "nr_ul_bw_4", "nr_ul_bw_5", "nr_ul_bw_6", "nr_ul_bw_7", "nr_ul_bw_8", "nr_num_ul_all_tx_type_1", "nr_num_ul_all_tx_type_2", "nr_num_ul_all_tx_type_3", "nr_num_ul_all_tx_type_4", "nr_num_ul_all_tx_type_5", "nr_num_ul_all_tx_type_6", "nr_num_ul_all_tx_type_7", "nr_num_ul_all_tx_type_8", "nr_num_ul_re_tx_type_1", "nr_num_ul_re_tx_type_2", "nr_num_ul_re_tx_type_3", "nr_num_ul_re_tx_type_4", "nr_num_ul_re_tx_type_5", "nr_num_ul_re_tx_type_6", "nr_num_ul_re_tx_type_7", "nr_num_ul_re_tx_type_8", "nr_p_plus_scell_nr_rach_num_success", "nr_p_plus_scell_nr_rach_num_fail", "nr_p_plus_scell_nr_rach_num_abort", "nr_p_plus_scell_nr_rach_num_other_result", "nr_p_plus_scell_nr_rach_num_first_attempt_success", "nr_p_plus_scell_nr_rach_num_multiple_attempt_success", "nr_p_plus_scell_nr_rach_num_fail_msg2", "nr_p_plus_scell_nr_rach_num_fail_msg4", "nr_serv_cell_info_band_id", "nr_serv_cell_info_rsrp", "nr_serv_cell_info_rsrq", "nr_serv_cell_info_rs_sinr", "nr_serv_cell_info_rssi", "nr_serv_cell_info_best_rs_index_rsrp", "nr_serv_cell_info_rsrp_rx1_1", "nr_serv_cell_info_rsrp_rx1_2", "nr_serv_cell_info_rsrp_rx1_3", "nr_serv_cell_info_rsrp_rx1_4", "nr_serv_cell_info_rsrp_rx2_1", "nr_serv_cell_info_rsrp_rx2_2", "nr_serv_cell_info_rsrp_rx2_3", "nr_serv_cell_info_rsrp_rx2_4", "nr_serv_cell_info_rsrp_rx3_1", "nr_serv_cell_info_rsrp_rx3_2", "nr_serv_cell_info_rsrp_rx3_3", "nr_serv_cell_info_rsrp_rx3_4", "nr_serv_cell_info_rsrp_rx4_1", "nr_serv_cell_info_rsrp_rx4_2", "nr_serv_cell_info_rsrp_rx4_3", "nr_serv_cell_info_rsrp_rx4_4", "nr_serv_cell_info_rsrq_rx1_1", "nr_serv_cell_info_rsrq_rx1_2", "nr_serv_cell_info_rsrq_rx1_3", "nr_serv_cell_info_rsrq_rx1_4", "nr_serv_cell_info_rsrq_rx2_1", "nr_serv_cell_info_rsrq_rx2_2", "nr_serv_cell_info_rsrq_rx2_3", "nr_serv_cell_info_rsrq_rx2_4", "nr_serv_cell_info_rsrq_rx3_1", "nr_serv_cell_info_rsrq_rx3_2", "nr_serv_cell_info_rsrq_rx3_3", "nr_serv_cell_info_rsrq_rx3_4", "nr_serv_cell_info_rsrq_rx4_1", "nr_serv_cell_info_rsrq_rx4_2", "nr_serv_cell_info_rsrq_rx4_3", "nr_serv_cell_info_rsrq_rx4_4", "nr_serv_cell_info_rs_sinr_rx1_1", "nr_serv_cell_info_rs_sinr_rx1_2", "nr_serv_cell_info_rs_sinr_rx1_3", "nr_serv_cell_info_rs_sinr_rx1_4", "nr_serv_cell_info_rs_sinr_rx2_1", "nr_serv_cell_info_rs_sinr_rx2_2", "nr_serv_cell_info_rs_sinr_rx2_3", "nr_serv_cell_info_rs_sinr_rx2_4", "nr_serv_cell_info_rs_sinr_rx3_1", "nr_serv_cell_info_rs_sinr_rx3_2", "nr_serv_cell_info_rs_sinr_rx3_3", "nr_serv_cell_info_rs_sinr_rx3_4", "nr_serv_cell_info_rs_sinr_rx4_1", "nr_serv_cell_info_rs_sinr_rx4_2", "nr_serv_cell_info_rs_sinr_rx4_3", "nr_serv_cell_info_rs_sinr_rx4_4", "nr_serv_cell_info_rs_rssi_rx1_1", "nr_serv_cell_info_rs_rssi_rx1_2", "nr_serv_cell_info_rs_rssi_rx1_3", "nr_serv_cell_info_rs_rssi_rx1_4", "nr_serv_cell_info_rs_rssi_rx2_1", "nr_serv_cell_info_rs_rssi_rx2_2", "nr_serv_cell_info_rs_rssi_rx2_3", "nr_serv_cell_info_rs_rssi_rx2_4", "nr_serv_cell_info_rs_rssi_rx3_1", "nr_serv_cell_info_rs_rssi_rx3_2", "nr_serv_cell_info_rs_rssi_rx3_3", "nr_serv_cell_info_rs_rssi_rx3_4", "nr_serv_cell_info_rs_rssi_rx4_1", "nr_serv_cell_info_rs_rssi_rx4_2", "nr_serv_cell_info_rs_rssi_rx4_3", "nr_serv_cell_info_rs_rssi_rx4_4") VALUES ('4052794578802011452', '2021-08-20 15:55:04.145', '2021-08-20 15:55:04.961', '171', '125174', '173', X'0001e6100000c7cee6805e4e59405fc915f8ff6a1b40c7cee6805e4e59405fc915f8ff6a1b407c01000000c7cee6805e4e59405fc915f8ff6a1b40fe', '41', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '2559.75', '', '', '', '', '', '', '', '511951', '', '', '', '', '', '', '', '176', '', '', '', '', '', '', '', '2', '', '', '', '', '', '', '', '-91.775', '', '', '', '', '', '', '', '-4.03', '', '', '', '', '', '', '', '7.05', '', '', '', '', '', '', '', '30', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '2', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '-73.255', '-91.775', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '');''',
]

def create_test_qgis_layer_py_objs():
    print("create_test_qgis_layer_action() impl START")
    import re
    layer_name_dict = azq_utils.get_qgis_layers_dict()
    for insert_sql in insert_list:
        match = re.search(r"INSERT INTO.*\((.*)\) VALUES \((.*)\)\;", insert_sql)
        col_list = match.group(1).replace("\"","").split(", ")
        value_list = match.group(2).replace("\'","").split(", ")
        print(value_list)
        geom_index = col_list.index("geom")
        geom = bytearray.fromhex(value_list[geom_index].replace("X","").strip())
        print(geom)
        # featureList =[]
        for layer_name in layer_name_dict:
            if layer_name in col_list:
                layer = layer_name_dict[layer_name]
                
                pr = layer.dataProvider()
                fields = layer.fields()
                fet = QgsFeature()
                fet.setFields(fields)
                fet.setGeometry(geom)
                i = 0
                for param in col_list:
                    if param == "geom":
                        i += 1
                        continue
                    fet[param] = value_list[i]
                    i += 1
                    
                # featureList.append(fet)

                pr.addFeatures([fet])
                layer.updateExtents()

                # QgsProject.instance().addMapLayers([layer])
                print("add_feature_to_{}_layer DONE".format(layer))


    # fields = QgsFields()
    # fields.append(QgsField("cell_id", QVariant.Int))

    # layer = QgsVectorLayer("Point?crs=epsg:4326", "temporary_points", "memory")
    # pr = layer.dataProvider()
    # pr.addAttributes(fields)
    # layer.updateFields()

    # fet = QgsFeature()
    # fet.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(25.60278, -33.98113)))

    # pr.addFeatures([fet])
    # layer.updateExtents()

    # QgsProject.instance().addMapLayers([layer])
    # print("create_test_qgis_layer_action() impl DONE")
