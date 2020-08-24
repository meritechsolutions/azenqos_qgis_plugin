import xml.etree.ElementTree as xet
import pandas as pd
import random
import math
import os
import sys
import traceback

import preprocess_azm
import azq_cell_file
from dprint import dprint

ELM_OVERRIDE_DICT = {
    "lte_volte_rtp_jitter_dl_millis":"lte_volte_rtp_jitter_dl_ms",  # see note on this in azq_global_element_info_list.csv
    "wcdma_ecio":"wcdma_aset_ecio",
    "wcdma_rscp":"wcdma_aset_rscp",
}

DYN_PARAM_THEME_FROM_EXISTING_PARAM_DICT = {
    "rssi":"lte_inst_rssi",
}

def get_module_path():
    return os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__))
    )

g_default_theme_file = os.path.join(get_module_path(),"default_theme.xml")
g_ori_default_theme_file = g_default_theme_file

g_var_name_legacy_to_new_dict = {
"android_cellid_from_cellfile":"android_cellid_from_cellref",
"gsm_cellfile_matched_cellname":"gsm_cellname",
"gsm_cellfile_matched_sitename":"gsm_sitename",
"gsm_cellfile_matched_neighbor_cellname":"gsm_neighbor_cellname",
"gsm_cellfile_matched_neighbor_sitename":"gsm_neighbor_sitename",
"gsm_cellfile_matched_neighbor_lac":"gsm_neighbor_lac",
"gsm_cellfile_matched_neighbor_cellid":"gsm_neighbor_cellid",
"lte_cqi_n_subbands":"lte_n_subbands",
"lte_prb_alloc_in_bandwidth_percent_latest":"lte_prb_util_latest_percent",
"lte_prb_alloc_in_bandwidth_percent_avg":"lte_prb_util_avg_percent",
"wcdma_cellfile_matched_cellname":"wcdma_cellname",
"wcdma_aset_cellfile_matched_cellid":"wcdma_aset_cellid",
"wcdma_mset_cellfile_matched_cellid":"wcdma_mset_cellid",
"wcdma_dset_cellfile_matched_cellid":"wcdma_dset_cellid",
"wcdma_aset_cellfile_matched_cellname":"wcdma_aset_cellname",
"wcdma_mset_cellfile_matched_cellname":"wcdma_mset_cellname",
"wcdma_dset_cellfile_matched_cellname":"wcdma_dset_cellname",
"data_hsdpa_cqi_number_avg":"data_hsdpa_cqi_number_avg",
"gsm_ci":"gsm_coi",
"gsm_ci_arfcn":"gsm_coi_arfcn",
"gsm_ci_avg":"gsm_coi_avg",
"data_hsdpa_mac_layer_rate":"data_hsdpa_thoughput",
"emm_state_state":"mm_state_state",
"emm_state_substate":"mm_state_substate",
"emm_state_update_status":"mm_state_update_status",
"emm_characteristics_network_operation_mode":"mm_characteristics_network_operation_mode",
"emm_characteristics_service_type":"mm_characteristics_service_type",
"mm_characteristics_mcc":"mm_characteristics_mcc",
"mm_characteristics_mnc":"mm_characteristics_mnc",
"mm_characteristics_lac":"mm_characteristics_lac",
"mm_characteristics_rai":"mm_characteristics_rai",
"ereg_state_state":"reg_state_state",
"ereg_state_ue_operation_mode":"reg_state_ue_operation_mode",
"lte_rank_indicator":"lte_rank_indication",
"lte_serv_cell_info_psc":"lte_serv_cell_info_pci",
"lte_serv_cell_info_cell_id":"lte_serv_cell_info_eci"
}


def is_reverse_layer_plot_order(param_col):
    if "_rxqual" in param_col or "_bler" in param_col or "_fer" in param_col:
        return True
    return False


def is_param_col_an_id(param_col, table_name=None):

    dprint("is_param_col_an_id table_name:",table_name)
    id_params = [
        "log_hash",
        "log_ori_file_name",        
        "lte_physical_cell_id",
        "lte_neigh_physical_cell_id",
        "scan_lte_ch_topn_result_cell_pci",        
        "lte_earfcn",
        "lte_band",
        "lte_pdsch_spatial_rank",
        "lte_rank_indication",        
        "lte_pdsch_transmission_mode_current",
        "lte_pdsch_serving_n_tx_antennas",
        "lte_pdsch_serving_n_rx_antennas",
        "lte_pdsch_stream0_modulation",
        "lte_pdsch_stream1_modulation",
        "lte_transmission_mode_l3",
        "lte_transmission_mode_info",
        "lte_nb1_physical_cell_id",
        "lte_pdsch_serving_cell_id",
        "lte_pdsch_rnti_id",
        "lte_pdsch_rnti_type",
        "lte_volte_frame_type_tx",
        "lte_volte_frame_type_rx",
        
        "wcdma_band",
        "wcdma_dl_uarfcn",
        "wcdma_ul_uarfcn",
        "wcdma_cellid",
        "wcdma_cellfreq",
        "wcdma_aset_cellfreq",
        "wcdma_mset_cellfreq",
        "wcdma_dset_cellfreq",
        
        "wcdma_sc",
        "scan_wcdma_ch_topn_result_cell_sc",
        "wcdma_aset_sc",
        "wcdma_mset_sc",
        "wcdma_dset_sc",
        
        "gsm_speechcodecrx",
        "gsm_speechcodectx",
        "gsm_lac",
        "gsm_cellid",
        "gsm_arfcn_bcch",
        "gsm_cgi",

        "scan_rssi_channel",
        "scan_nr_topn_result_ci",
        
        "data_gprs_dl_coding_scheme",
        "handover",
        "android_cellid",
        "cm_system_mode",
        "cm_system_mode_index",
        "technology",
        "android_e_node_b_id",
        "rat",

        "nr_dl_frequency",
        "nr_dl_arfcn",
        "nr_servingbeam_pci",
        "nr_servingbeam_ssb_index",

        "wifi_active_bssid",
        "wifi_active_ssid",
        "wifi_active_ipaddr",
        "wifi_active_macaddr",
        "wifi_active_encryption",
        "wifi_active_freq",
        "wifi_active_channel",
        "wifi_active_isp"

        
    ]
    

    id_tables = [
        "logs",
        "log_info",
        "events",
        "signalling",
        "vocoder_info",
        "lte_serv_cell_info",
        "lte_sib1_info",
        "lte_rrc_transmode_info"
    ]

    print("param_col0:", param_col)
    param_col = preprocess_azm.get_elm_name_from_param_col_with_arg(param_col)
    
    print(("check is_param_col_an_id:",param_col))

    if not table_name is None:
        if table_name in id_tables:
            print(("check is_param_col_an_id:",param_col, "ret true"))
            return True

    if param_col in id_params:
        print(("check is_param_col_an_id:",param_col, "ret true"))
        return True

    print(("check is_param_col_an_id:",param_col, "ret false"))
    return False


def get_default_theme_file():
    global g_default_theme_file
    print("current theme's file :"+g_default_theme_file)
    return g_default_theme_file


def set_default_theme_file(f):
    print("set theme: "+f)
    global g_default_theme_file
    g_default_theme_file = f


def get_matching_col_names_list_from_theme_rgs_elm():
    global g_var_name_legacy_to_new_dict
    ret = []
    rgs_list = get_theme_report_generator_setting_list()
    print("rgs_list:", rgs_list)
    elm_ref_df = preprocess_azm.get_elm_df_from_csv()

    dprint("rgs_list len", len(rgs_list))
    for rgs in rgs_list:
        print("rgs type:", type(rgs))
        # check if this rgs exists and is not empty in the log/db
        eid = None
        arg_id = None
        col_name = None
        try:
            try:
                eid = rgs.find("elementID").text.lower()
            except:
                eid = rgs.lower()
                
            if eid in g_var_name_legacy_to_new_dict:
                print("this eid {} is a legacy var name - get matching new var name".format(eid))
                eid = g_var_name_legacy_to_new_dict[eid]
                print("matching new var name: {}".format(eid))
            print("eid:", eid)
            arg_id = 1
            try:
                arg_id = rgs.find("argument").text
            except:
                pass
            col_name = eid+"_"+str(arg_id)
            #print "col_name:", col_name
            try:
                matched_rows = elm_ref_df.query("var_name == '{}'".format(eid))
                dprint("search elm_ref_df for [{}] match got len: {}".format(eid, len(matched_rows)))
                if len(matched_rows) == 0:
                    raise Exception("failed to find matching row in azq_global elm csv list")
                dprint("matched_rows.iloc[0].n_arg_max:", matched_rows.iloc[0].n_arg_max)
                if int(matched_rows.iloc[0].n_arg_max) == 1:
                    dprint("got n_arg_max_1 so set col_name to not have _arg suffix")
                    col_name = eid
                if not col_name in ret:
                    ret.append(col_name)
                dprint("col_name for this rgs: [", col_name, "]")
            except Exception as qe:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("elm_ref_df query for matching var_name exception: " + exstr)
        except Exception as e:
            type_, value_, traceback_ = sys.exc_info()
            exstr = str(traceback.format_exception(type_, value_, traceback_))
            print("rgs parse/check exception: " + exstr)

    ret_series = pd.Series(ret)    
    """
        if param_col == "wcdma_ecio_1":
            print "plot_param_engine - override wcdma_ecio_1 to wcdma_aset_ecio_1"
            param_col = "wcdma_aset_ecio_1"  # wcdma_ecio_1 has too many invalid values when it is not aset

    """
    print("get_matching_col_names_list_from_theme_rgs_elm(): ret_series0:", ret_series)
    if len(ret_series):
        ret_series = ret_series.str.replace("wcdma_ecio_1","wcdma_aset_ecio_1")
        ret_series = ret_series.drop_duplicates()
    print("get_matching_col_names_list_from_theme_rgs_elm(): ret_series:", ret_series)
    return list(ret_series.values)


g_csv_theme_df_cache = {}
def get_csv_theme_df_for_csv_file(theme_csv_file):
    if theme_csv_file in g_csv_theme_df_cache:
        return g_csv_theme_df_cache[theme_csv_file]
    theme_df = pd.read_csv(theme_csv_file).dropna(how="all")  # drop rows where all cols are empty
    g_csv_theme_df_cache[theme_csv_file] = theme_df
    return theme_df

def get_theme_report_generator_setting_list():

    theme_xml_file=g_default_theme_file

    if theme_xml_file.endswith(".csv"):
        theme_df = get_csv_theme_df_for_csv_file(theme_xml_file)
        return theme_df.element.unique()

    print("theme_xml_file :"+theme_xml_file)
    root = None
    ret = []
    try:
        tree = xet.parse(theme_xml_file)
        root = tree.getroot()
        dprint("xml parse elements setting")
        for elm in root.iter("ReportGeneratorSetting"):
            if elm in ELM_OVERRIDE_DICT:
                elm = ELM_OVERRIDE_DICT[elm]
            ret.append(elm)
    except Exception as e:
        print("get_theme_list_of_elements: exception: "+str(e))
    return ret


def get_theme_df_for_column(param_col_with_arg, data_df=None, dbcon=None, table_name=None,
                            override_xml_file=None):
    global g_ori_default_theme_file
    global g_default_theme_file

    # check custom theme by cosmetic_option
    try:
        custom_theme_dict = eval(azq_cosmetic_map_option_setting.get_cosmetic_option('custom_theme'))
        custom_theme_element_list = list(custom_theme_dict.keys())
        if param_col_with_arg in custom_theme_element_list:
            retdf = pd.read_json(custom_theme_dict[param_col_with_arg])
            return retdf
    except:
        print("Warning!! custom theme json invalid, try normal step")

    theme_xml_file=g_default_theme_file
    if override_xml_file is not None:
        theme_xml_file = override_xml_file

    print("theme_xml_file :"+theme_xml_file)

    if theme_xml_file.endswith(".csv"): # not support reverse_cum
        theme_for_param_col = None

        try:
            theme_df = get_csv_theme_df_for_csv_file(theme_xml_file)
            param_col = preprocess_azm.get_elm_name_from_param_col_with_arg(param_col_with_arg)

            theme_for_param_col = theme_df.query("element == '{}'".format(param_col))
            del theme_for_param_col["element"]
            # gsheets csv header: element	color_rgb_hex	lower	upper	match_value

            theme_for_param_col["color_rgb_hex"] = theme_for_param_col["color_rgb_hex"].astype(str)

            theme_for_param_col.columns = ['ColorXml', 'Lower', 'Upper', "match_value"]
            if theme_for_param_col.match_value.isnull().all():
                del theme_for_param_col["match_value"]

            # add # prefix to ColorXml
            theme_for_param_col.ColorXml = '#' + (theme_for_param_col.ColorXml.astype(str).replace('#',''))

            #print "get_theme_df_for_column: col: {} csv theme file ret: {}".format(param_col, theme_for_param_col)

            if theme_for_param_col is None or len(theme_for_param_col) == 0:            
                raise Exception("csv theme_for_param_col ret len 0 - try gen from data instead...")

            print('csv theme:', theme_for_param_col)
            if pd.isnan(theme_for_param_col.Lower).all():
                raise Exception("csv theme all empty - raise exception to gen from data instead...")
            return theme_for_param_col
        except Exception as cte:
            print("WARNING: get_theme_df_for_column [{}] - csv theme mode get exception: {}".format(param_col, str(cte)))

    root = None
    try:

        if theme_xml_file.endswith(".csv"):
            raise Exception("theme file is csv and got 0 len case fallback to gen from data instead...")
        
        # TODO: separate param_col_with_arg into param_col and param_arg_number
        dprint("param_col_with_arg: " , param_col_with_arg)
        param_col = preprocess_azm.get_elm_name_from_param_col_with_arg(param_col_with_arg)
        if param_col in DYN_PARAM_THEME_FROM_EXISTING_PARAM_DICT:
            param_col = DYN_PARAM_THEME_FROM_EXISTING_PARAM_DICT[param_col]
        print(("param_col:" , param_col))
        tree = xet.parse(theme_xml_file)
        root = tree.getroot()
        print("xml parse elements setting")
        foud_elm = False
        for elm in root.iter("ReportGeneratorSetting"):
            eid = elm.find("elementID")
            #print "eid.text", eid.text
            if eid.text == param_col:
                found_elm = True
                print(("got matching eid for param_col ",param_col))
                is_reverse_cum = False
                try:
                    is_reverse_cum = elm.find("isReverseComulative").text.strip() == "true"
                except Exception as e:
                    print("is_reverse_cum check exception:",str(e))
                all_records = []
                headers = []
                rl = elm.find("rangeList")
                dprint("found rangeList - extract ranges:")
                for ctb in rl.findall("ColorTheme.Bin"):
                    #print "ctb: ",ctb
                    record = []
                    for ctb_child in ctb:
                        #print "ctb_child.text: ",ctb_child.text
                        record.append(ctb_child.text)
                        if ctb_child.tag not in headers:
                            headers.append(ctb_child.tag)

                    all_records.append(record)
                if is_reverse_cum:
                    all_records.reverse()
                print("total records: ",len(all_records))
                #print all_records
                print("total cols: ",len(headers))
                #print headers
                retdf = pd.DataFrame(all_records, columns=headers)
                print("total cols0")
                #print "precheckretdf empty retdf ",retdf

                retdfempty = True
                try:
                    if retdf.size > 0:
                        retdfempty = False
                except:
                    pass

                print("total cols1")
                
                if retdfempty and theme_xml_file != g_ori_default_theme_file:
                    print("retdf.size 0 in non-default theme try get from default_theme.xml: theme_xml_file {} g_ori_default_theme_file {}".format(theme_xml_file, g_ori_default_theme_file))
                    retdf = get_theme_df_for_column(param_col_with_arg, data_df=data_df, dbcon=dbcon, table_name=table_name, override_xml_file=g_ori_default_theme_file)

                if retdf is None:                    
                        raise Exception("retdf == None - fall back to generate theme from data insted...")
                    
                if retdf.size == 0:                    
                        raise Exception("No ranges for this element - fall back to generate theme from data insted...")


                print("total cols2")
                """
                now we do recursive calls and this breaks match_values that was already populated
                col_is_id = False
                try:
                    col_is_id = is_param_col_an_id(param_col)
                    if col_is_id:                    
                        retdf['match_value'] = retdf.Lower
                except giside:
                    print "WARNING: read xml theme check if param_col is id exception:", giside
                """
                print("return now")
                return retdf

        
        if foud_elm == False and theme_xml_file != g_ori_default_theme_file:
            print("case found_elm false try get from g_ori_default_theme_file")
            retdf = get_theme_df_for_column(param_col, data_df=data_df, dbcon=dbcon, table_name=table_name, override_xml_file=g_ori_default_theme_file)
                
            if retdf is None:                    
                raise Exception("case found_elm false retdf == None - fall back to generate theme from data insted...")
                    
            if retdf.size == 0:                    
                raise Exception("case found_elm false No ranges for this element - fall back to generate theme from data insted...")
            
            return retdf

    except Exception as e:
        print("WARNING: parse theme file: {} param_col: {} exception: {}".format(theme_xml_file, param_col, str(e)))

    # if control reaches here means failed to get theme for param_col - will gen from data
    if param_col_with_arg == "wcdma_aset_ecio_1":
        print("azq_theme_manager failed to get theme for wcdma_aset_ecio_1 - try get from xml/csv with name wcdma_ecio_1 instead...")
        return get_theme_df_for_column("wcdma_ecio_1", data_df=None, dbcon=None, table_name=None, override_xml_file=None)

    print("Get theme from xml file failed - falling back to generate_theme_from_data...")

    if data_df is None and dbcon is None:
        print("data_df and dbcon not specified - cannot do fallback method... ABORT")
        return None

    # restore param_col from param_col_ori because its arg might have got cut already above
    param_col = param_col_with_arg

    print("generate theme_df from data 0")

    if data_df is None:
        elm_info = None
        dprint("data_df is None - get it from dbcon...")
        #print "get table name"
        if table_name is None:
            table_name = preprocess_azm.get_table_for_column(param_col)
            elm_info = preprocess_azm.get_elm_info(param_col)
        #print "got table name:", table_name
        #print "get col df"
        col_to_select = preprocess_azm.get_elm_name_from_param_col_with_arg(param_col)
        if elm_info is not None:
            #print "elm_info:", elm_info
            try:
                if elm_info.n_arg_max.strip() == "1":
                    pass
                else:
                    col_to_select += "_1"
            except:
                pass
        
        datadfsql = "select {} from {}".format(col_to_select, table_name)
        print("col_to_select:", col_to_select, "start sql:", datadfsql)
        data_df = sql_helpers.query(dbcon, datadfsql)
        if data_df is not None:
            print("col_to_select:", col_to_select, "done - data_df len:", len(data_df))
        else:
            print("col_to_select:", col_to_select, "done - data_df is None")
        param_col = col_to_select
        
    #print "generate_theme_from_data for param_col {} and ret".format(param_col)

    if table_name is None:
        try:
            table_name = preprocess_azm.get_table_for_column(param_col)
        except:
            pass
    
    print("check col_is_id table_name: ", table_name)    
    
    col_is_id = is_param_col_an_id(param_col,table_name=table_name) # like pci, psc, bcch arfcn

    param_col_is_str = False
    try:
        if pd.api.types.is_string_dtype(data_df[param_col]):
            print("azq_theme_manager: param_col is_string_dtype so set is_param_col_an_id")
            param_col_is_str = True
            col_is_id = True
        else:
            print("azq_theme_manager: param_col not is_string_dtype")

    except Exception as se:
        print("WARNING: azq_theme_manager: check col is_string_dtype exception: ", se)

    print("col_is_id:", col_is_id, "param_col_is_str:", param_col_is_str)
    
    gdret = generate_theme_from_data(data_df, param_col, all_unique_vals_per_theme = col_is_id)
                
    # print "gdret:\n", gdret
    return gdret


def get_default_color_for_index(i):

    r = lambda: random.randint(0,255)
    color_list = ['CD5C5C', '556B2F', '9400D3', '00FA9A', '000080', 'C71585', 'FF8C00', '20B2AA', 'DAA520', '00FFFF', '228B22', 'DA70D6', '2F4F4F', '8B4513', 'BDB76B', 'FFE4C4', 'DB7093', '8FBC8F', '8B7D6B', 'B22222', 'FA8072', '00FF00', '3CB371', '00BFFF', '32CD32', '87CEEB', '5F9EA0', '4682B4', 'B0C4DE', 'E6E6FA', 'F4A460', 'BA55D3', '6A5ACD', '00FF7F', 'EED5B7', '7FFFD4', '98FB98', '7CFC00', 'FF69B4', 'BC8F8F', '1E90FF', '6B8E23', 'F5AAAA', '006400', '483D8B', '2E8B57', 'CDB79E', 'FFE4E1', '708090', '0000CD', 'FF4500', '6495ED', '4169E1', 'FFFF00',     'E30741','C896A1','8575DB','D16155','154B61','5556D9','89220D','392BF0','6D1DE7','30C8B3','918E86','80FB20','86AB19','B86D55','485111','4A2D9B','31B3DE','354D06','7CEE93','3DC9ED','A38D01','833460','3A6887','EF3CEC','F1ACA9',
'A4C32C','4B08F6','931FB9','699957','659023','AC86FA','2452D5','968A64','4CDD62','4D8DEA','187AE7','51BB49','0DF985','EC2BA9','EF66D4','0ED88B','FEDB91','4AF437','A14CDE','6BDC2A','139EB2','AA0769','8A38F7','099466','3C2094',
'BA7592','73D7B4','04F4CE','BC751E','B4AE53','21EA68','DDCB57','F6CEA9','C664B7','27CD52','18402B','8F85BE','DA498E','2548AF','0D6DAC','FC44C6','F568A1','67CA15','93AEC5','ED25AD','1A95E5','CEA365','5CC17D','6111FE','6DB926',
'641F9F','56E0A4','5F1109','F7A18A','0F7C8A','2EE3E8','33F139','6987B9','0A0BC8','5C7D8F','7AE6EC','E10E33','79DF08','8128DF','13B804','88E6ED','3DF3B2','73B42C','CBEF4C','E6FAFF','E77DE6','A24A5F','CD2815','5E14E6','0DCF7B',
'F53731','EE4289','1474D8','A27B75','273E7A','970CE3','ED12F9','C1E35B','CFE4B5','ADDDC4','75C82B','B18D47','71854E','11E059','5F72D3','7593DC','F9E763','EE4749','55A350','DB04ED','8622AF','F98E0F','1FD561','FB79ED','9B9907',
'79D9C8','9C12A1','1C0F26','1129A1','64C0ED','7575F4','D81FAC','0C81CA','8DCA77','BEC8EA','660EB0','398493','0908BC','34A0F2','7B033E','EA4F90','FCA803','B0DC98','9CC4DB','64668A','56596E','95B3DB','69C365','CF294F','4A4B1C',
'663BF9','A9F5DC','136D7C','24C4D0','32A7DB','4327F1','19B0F8','D0B3D3','0F7C45','C87704','3485C8','7D12E1','AB16FF','9FF1B3','77CEFC','321C7D','4FB61A','7B5814','8B47DF','A47626','369421','260EC1','83CECE','3597C6','77BEED',
'514E66','F8DF69','1FDDDA','C1F58B','CF27E1','532918','011D07','7174F4','FB6E1E','ADED4C','EAF131','942A13','284AD4','ECF5B0','35E233','E1DE21','FC5277','5AFA4D','E39E84','FBADDD','1CEEA1','09D6B5','D1FDB3','A9637E','879247',
'053F4E','058EB4','485360','609C41','BD850D','C03007','E1C6F8','B41077','0E8AAC','C6A4BA','27B58B','D7CAEC','290497','BA5440','116B52','68A1D2','CB9858','4814CB','C852DA','2EB991','BF9517','8D2258','AA0CED','7B6CD3','70129B',
'35BDBC','43A76F','0091C8','E34501','871AAB','6D12BC','F00976','986393','C870D8','16F319','E87FA3','C93C3B','2C39FC','CC44C2','CE8C1A','502D0C','0C649A','FB6256','F2246E','62CFFE','95EB2E','83BF84','9700A6','6A89EF','852541',
'3E62A9','13DC25','1CC2C7','8311DF','0543A9','4E7B02','4151D7','6F4310','AA4BC1','BD7002','9401F0','342850','0BF4E1','59CA48','C05305','59A6BA','7EE974','9709CF','A287CD','F9D5CD','B27593','001F99','3213BE','260BDD','8D6523',
'3D6B3F','E3F029','95CB98','9BE97C','7F9D5B','19974C','62F631','FD7B80','31C2B3','E33809','322D97','90A87D','A6A223','264F80','3736F4','036300','A91428','2DEDF1','027420','5578C7','CCA3FB','3A55E8','D15CE5','DE853A','58FD1C',
'4E9E18','A53FA2','773C31','21FA63','5BB59C','1DAACC','36165C','8C4C98','DC9D60','0CBB15','8222DE','F0407A','DF61B0','99C363','37FF20','4B36E0','5D0AE8','4B7BD3','B6D8A4','BDBBCE','C09077','0C4163','9AE16B','5122AC','659116',
'0E69EE','1EA6F1','99C7A2','30462E','294CB5','2B3951','7602C0','3690D4','214777','5A096C','F8731C','5825AF','6E5FE3','40598C','0D617D','D755A6','1FF45A','4B89B6','D0729F','FAD6B4','39B8E6','F06F4C','987123','8F3F2D','F17C83',
'1BDC4B','24B930','5D8DEA','07A46C','26EA26','D32B06','63A2CE','21BBFA','6F1148','D6EC01','3E4595','B08625','457F16','976A8B','261132','2617BA','C7A5DD','B13214','9ACF55','A8CC9F','FC5031','A08565','317748','CD38D8','D8194A',
'947E4A','0FB851','D93407','DD4052','93AADF','563C58','7573ED','5B6807','FD44EA','67E12B','072448','CCE4FC','2479C8','0C6504','07CE8E','A86CDA','4962E5','E0A696','FA2503','A0A6F2','49BB58','5A1CD0','2C0C2A','225575','816285',
'5DE084','8EFAAC','AC8B8B','5BDA05','0976CF','C2CB24','FB3E5D','B094C2','13328E','3D8A44','9066C9','BC4EAA','B6B5A7','7A9487','3B4B59','FFA656','F024FD','EA490E','178BC0','2FC7A1','190BF6','2F7536','2216B1','5D9E85','FB4B2E',
'C47DF7','327B7B','1AD319','566E4F','33A8FD','6B1E91','6C3D8A','8956D6','F2C611','5550D4','E30029','18656E','0F8555','B488AA','90FE0C','3F03F2','C0B361','1609C5','F7A805','296286','EB6FF5','2B6DEC','E03F9F','497F17','541B69',
'255844','D7044E','13F429','472C64','3B946F','E8531A','8F1835','74868A','FD1198','6D4F1B','F04445','EC4F47','5BCE25','912B3B','39889A','38B7DF','DCB1B0','91C5FE','A9FC43','88D106','C3F7BD','6892A5','336F86','D30D04','18CEAD',
'5615EC','255B7F','0A37AB','E7FE5F','368052','DA9E07','B2C0E4','0EF369','F51E37','E7E673','84E23E','9E16FF','B0EA34','43952D','D04B6B','FF0E13','CB1E21','DD1B74','0C8A2A','7FACA1','8A0882','B5DD3F','F0C0C4','5C1D63','8E22AD',
'3374B0','675459','449156','5B2688','A06C31','9741BF','12776D','0A29B7','F1228B','A2C1FF','2876A2','6B4E2B','B35DD1','5D27FB','2ADFBC','ED564F','8BBD9E','851E2E','F7B1FB','D25A10','70EC62','CEE8C7','64D82F','727346','E183BA',
'43A2F1','5C034C','BB1844','8C6FFA','6DBF17','95B47B','5D750C','1C824C','6C8DC7','725327','BBC6F4','1429A3','5BFDE4','A5122D','AA00E2','8AE51D','A22CCD','F28FF7','3AC4DF','28A388','512463','1064C2','1C5AB5','2EFF3C','E5489D',
'1EE325','745E92','1BE669','B88A7B','761CFA','90984C','DB12AB','4B631D','CD657E','1F42B3','D447D8','4B45EE','13986B','538B80','99FECA','2AF61D','F683C6','1D9B50','7A306B','0050F1','A1BA8D','7740A0','6CD082','00D403','F03402',
'6B426C','0E44EF','45C164','3740B5','4A58F6','B62F88','C870C5','00BC21','168573','ABE04E','7F49FC','2C49D1','FD2A94','CAA501','8BD7B1','5319C0','5FCA8A','B87E30','2FBD4B','FD7C43','D96F33','F82C3B','6F3DD6','E06ADA','6C8D9C',
'076669','A62C26','785B63','253801','36EB47','84FEB5','85BB2D','19675D','A73DF3','E2ADEE','46235E','9E4496','2B0925','7CDBAC','E9F86D','7B49F9','888CD2','30D3AF','92C6D6','2CF256','0C1450','EE96B6','8E7611','6B4211','94D872',
'F7E0B4','0A3A1E','09C80E','A69E8B','01FDA6','09EFAA','4B4755','56F2EF','085A7E','57055B','B5595F','39A80F','E65D83','D8C324','18B2D0','D8622B','264CF5','CDB1A3','58C2BE','6D61F4','2DC80F','4268F5','DB28DD','C25850','6BDDDD',
'10AE9A','EDD46C','A37DC5','A87F1D','088E56','B76560','05DDA3','947114','6CDECE','BC64BB','B632CA','2DFFA9','34EB60','FDCCB8','A750C0','C77094','AB1ABC','3F12A7','294E50','708C04','DCB4C5','87191D','65C776','E90386','4F6CC7',
'194DD1','2584FA','15FDD6','4C05F9','B48204','92DDFB','E11760','176054','7908F0','1A4AD5','E67C46','72899E','9A50BA','4245A3','5CE96B','E52616','C99422','2CD8D8','32B876','CD3A69','65E9B0','08A9CD','CFA988','2BAE42','50F8B6',
'12C0B7','1B0B4D','91C3A5','BD16B5','915891','FA3BBF','3CA38F','010D4B','209475','906F9F','08A436','362EAA','EABF80','BB14F8','998082','09AAEE','11430F','EEAAE2','A9DCEC','585E8E','088A36','848D88','C67705','9BE67C','3D49BD',
'8B5169','7EE0C6','89DF0D','499301','04E5E9','27588B','1FA0F6','78F48F','2D9B0A','C0EB5D','584A0C','52CF2C','5A45ED','40AECA','89B741','49983A','59C19F','EF9348','099A75','50E073','2CDC51','6AA3C4','3A3CD7','5D1E79','3C92D1',
'60D3C2','43CF79','4A3770','FCD1A5','AE2410','5702BD','5F12F8','B43EBA','FB6DC1','37F5B0','508633','4835B3','E77152','B5E22B','4524BD','41DD70','0C9315','60CD12','0D7E0A','94FC9B','9DC6B4','7B01E2','642323','521D11','7B677F',
'20DF78','3F3412','6879B9','D0BEEC','0587CF','7F04E7','D26168','4D0B6B','43C02A','C3F5AC','41C46B','C4D364','BA2B59','69D2AF','D62CBD','90E545','109F3F','3FA6AF','F09C33','C0AED6','B67ACB','FDC9D0','91F47A','36BD3E','1FFCEC',
'2A3A40','64E2EB','37C3B4','DFB8DE','7EE7BC','3E678B','7EF61D','245E81','261DFE','C6DAE8','616D9F','81D77E','593A8B','CB2D81','B589F6','268931','8C254A','49474C','3085E1','7A6F36','65CEE0','06C3C0','E0A28E','FCF72D','897F9A',
'5F01EF','2E6F22','F03A2C','82889A','524C1D','76D88B','7AAD9C','F9C34F','FC184B','2AE67F','4E616E','DD97B3','3BD0E1','0EE163','D9DB04','B4316A','038AA3','DEEBFC','CFBA11','DFBBBB','060386','D9A535','9147C3','483F35','014BCF',
'7C670F','DE884C','DDE14B','484877','D88235','2B2922','801185','E52C77','7B0B47','32FC43','17F401','7828AA','D80047','8C3877','FBAF7F','3862C7','44F6CA','1A21B7','933CBB','4B6FBD','EF6523','C67CD4','6EE80A','FAD379','FC55B1',
'3909E3','DA9467','9D5756','250097','983FEE','0181B7','482ED9','566BEB','10110A','9A3C91','BA23CE','B16DF3','659C08','828948','4D38AC','957C94','A45025','48AE4B','6DDE71','7CFA49','7EFFA9','35E960','FA999D','5FB3E2','55E402',
'E70E7B','7B0546','631FDA','D39867','BBD9FD','CE5DCD','8488AD','F0000E','AD1468','B139B3','771D4E','AD225C','F5D05D','F0B141','9F3C9E','0051DA','0872AD','FA2CB7','AA85CC','75CA25','826E44','84CF77','C71F3D','7E8F44','BB975C',
'DEE3D2','75735F','A26C1A','A9828C','6380BD','C8CBB9','E3F564','517BE9','582DAA','A1E22A','0F2DBE','6926F9','B4A2F9','B41E2C','9DE7F0','2004DB','3446A4','F58988','23D420','0BDE3D','F5D0AB','BDF039','43FDC7','5FB34D','34803B',
'E31C3B','7F96FD','04001D','77C2A0','0D59E9','4CC680','1FFA6F','773775','4FC117','2258B3','100E69','F79E1F','D9711E','65E370','B9201D','43E414','D0C6FE','6D7DE8','C5EA95','A4FD50','A949D5','DB6916','883F62','8286D2','C87B5C',
'C05093','57FC11','39968F','912270','438BFE','8BEEB8','1100D1','10BB74','A15D3D','D80640','4CB3A6','BC8CD6','DE78AE','C50223','FFC050','0ACBD7','293A50','03F7C9','69E6B1','AA16A7','7B146E','B98F3D','041FBD','927882','93DAA8',
'21436B','224A18','81C918','7ABF23','2C7F71','893CDA','7FCC9D','42F1C0','A4B53D','95A051','2EB6B8','027CF1','A34A50','AF4548','3DEDE4','F12A7D','280A50','BF3FA9','0485AD','EDACB9','0BA352','18A22F','2EF6E9','FFE748','5360F2',
'90D432','65B07E','09D00C','AFB870','1C38C3','A637A7','A1C523','42D13E','DDD965','972DFE','0A531F','AC0722','B65979','7564EC','A84C54','B6E090','04C1CE','475A0D','3729C1','67AB30','FE6EF0','E05B12','A69F0A','C42FEF','146CF9',
'CF83D8','4C898A','B21512','0E62E4','1F98B9','289BB7','3F3C9B','75E8BF','BBE1DC','6FB087','AAF35B','A9AE53','AC9854','80F62D','39DF95','63F675','11EB04','FA1936','DC7D39','A6375C','DC0D27','2491FA','5F5788','D64537','FEE263',
'F30F02','736156','BB602F','906E69','55748D','771872','AF610B','8C7FC9','E6A440','EA56EE','4655ED','79CDBC','938035','A1C460','45BAB9','8FFE5E','BC77A2','446D49','2EBE32','F87A23','3B23A7','2549DF','C133F8','D1790A','B023A5',
'6E192C','1415EF','5A18E0','1B2853','31364D','BBCD4E','952BB0','B0BC99','DA5F3A','26B6C0','38BF60','EF50B0','161C3B','505B09','63F19C','2D4DDA','DBA3B6','4DD590','0F16A1','F04F2D','B4A028','A0353F','C7C9D5','9E5B5F','C40033',
'EF79FA','1AA40E','4C6154','6F2BA7','B7CC70','F607FF','109C5A','BA61BC','62C9E7','09ED56','E5CECC','DED7A2','16D878','4EA078','882758','D3DA19','6F7372','688400','C5E766','FEE253','A377D9','149980','CF8539','6FE564','B63988',
'D2B5A9','FCD865','825178','BD793E','EE518D','A506AA','F97C2D','2AF7C7','075818','6F7B1F','9B491F','419BEC','906983','09B61C','F7C63D','6C9B6B','BAC46B','0FC784','B9E6FF','2F7F6A','DC778D','238F8E','A9E716','CC0A20','95F056',
'B2339B','0CE9C6','87F6E1','DADD40','ED6DEB','49E7C7','2D4070','708776','841625','603CE2','82C6A9','EC62DE','34EBC5','25A3BD','91EDEC','F7FBDA','4C6BE3','9288D5','DFA735','5C7396','09D04B','A97056','4F8D76','356DD9','326A50',
'059E5E','AF820D','85C134','769E36','768E1E','E24709','6B9EDA','B5F872','CF95DC','C43534','316797','1F2BDF','59551C','8DB138','D0D150','592C1B','32A6D8','531B82','810324','C04A19','B73D34','8763D4','B38CF1','F720B4','485926',
'3EE6B1','A49177','63BE0A','FF110C','654BE7','215081','235B4D','2A0D90','8809A1','606BB5','3E68EF','902FC7','CF1DDA','E53FFD','06E71A','C583D6','277473','B43D10','805CF5','90B87D'
    ]
    l = len(color_list)
    if i < l:
        return '#'+color_list[i]
    else:
        return '#%02x%02x%02x' % (r(),r(),r())


#g_generate_theme_from_data_dict = {}
def generate_theme_from_data(df, param_col, all_unique_vals_per_theme=False):
    #global g_generate_theme_from_data_dict

    if len(df) == 0:
        print("generate_theme_from_data got empty df - return None")
        return None
    
    color_header = ['ColorXml', 'Lower', 'Upper', 'PointSize']
    
    if all_unique_vals_per_theme:
        print("get unique vals for param_col:", param_col, "azq_cell_file.CELL_FILE_RATS:", azq_cell_file.CELL_FILE_RATS)
        cell_file_theme_df = None
        for rat in azq_cell_file.CELL_FILE_RATS:
            print("get unique vals for param_col:", param_col, "stage rat:", rat)
            cf_params = azq_cell_file.LOG_PARAMS_FOR_CELL_THEME_POPULATE[rat]
            print("get unique vals for param_col:", param_col, "stage rat:", rat, "cf_params:", cf_params)
            for cf_param in cf_params:
                print("get unique vals for param_col:", param_col, "stage rat:", rat, "cf_param:", cf_param)
                if param_col.startswith(cf_param):
                    cell_file_theme_df = azq_cell_file.get_theme(rat)
                    break
        print('cell_file_theme_df', cell_file_theme_df)
        #print "df head:", df.head(3)
        
        if param_col not in df.columns:
            raise Exception("ABORT param_col {} not in supplied df columns".format(param_col))

        param_col_vals = df[param_col]
        #print "param_col_vals:", param_col_vals.head(3)
        print("get unique_vals start")
        unique_vals = param_col_vals.unique()
        print("get unique_vals done")

        try:
            print("sort unique_vals start")
            unique_vals.sort()  # sorts in-place
            print("sort unique_vals done")
        except:
            pass

        print("filter out common invalid values start")
        try:
            # filter out common invalid values
            #print "filter out common invalid values 65534 65535 - values:", unique_vals
            unique_vals = unique_vals[unique_vals != 65534]
            unique_vals = unique_vals[unique_vals != 65535]
            #print "post filter common invalid - values:", unique_vals
        except:
            pass
        print("filter out common invalid values done")
        color_header.append('match_value')

        """
        if param_col in g_generate_theme_from_data_dict:
            retdf = g_generate_theme_from_data_dict[param_col]
        else:"""
        
        retdf = pd.DataFrame(columns=color_header)

        #print "generate_theme_from_data - start retdf:", retdf

        retlen = len(retdf)

        if cell_file_theme_df is not None:
            cell_file_theme_list = list(cell_file_theme_df.ColorXml)
        else:
            cell_file_theme_list = []

        dprint("check if param_col type is int")
        vt = None        
        einfo = preprocess_azm.get_elm_info(param_col)
        if einfo is not None:
            vt = einfo.var_type
        dprint("check if param_col type is int - vt:",vt)

        print("for uv in unique_vals start")
        for uv in unique_vals:
            if uv is None or pd.isnull(uv):
                continue

            if vt is not None:
                if isinstance(uv, float) and math.isnan(uv):
                    continue
                dprint("uv type", type(uv))
                try:
                    if "int" == vt:
                        dprint("is int yes")
                        uv = int(uv)
                    else:
                        dprint("is int no")
                except:
                    pass

            if uv in retdf.match_value.values:
                #print "unique value uv {} already in existing retdf.match_value.values - skip".format(uv)
                pass #
            else:
                #print "unique value uv {} NOT in existing retdf - add it at end".format(uv)
                retdf.loc[retlen] = None
                match_color = get_default_color_for_index(retlen)

                ##### override color for special params
                if isinstance(param_col, str):
                    if uv is not None:
                        if param_col == "rat":
                            try:
                                print("rat match_color override start ori match_color:", match_color)
                                if uv == "GSM":                            
                                    match_color = get_default_color_for_index(0)
                                elif uv == "WCDMA":                            
                                    match_color = get_default_color_for_index(1)
                                elif uv == "LTE":                            
                                    match_color = get_default_color_for_index(2)
                                else:
                                    raise Exception("invalid rat uv: {}".format(uv))
                                print("rat match_color override done:", match_color)
                            except:
                                type_, value_, traceback_ = sys.exc_info()
                                exstr = str(traceback.format_exception(type_, value_, traceback_))
                                print("WARNING: rat color override exception: " + exstr)
                                
                        elif ("_physical_cell_id" in param_col) or param_col.startswith("wcdma_aset_sc") or param_col.startswith("wcdma_sc") or param_col.startswith("gsm_arfcn_bcch"):
                            try:
                                #print "cell code match_color override start ori match_color:", match_color
                                match_color = get_default_color_for_index(int(uv))
                                #print "cell code match_color override done:", match_color, "uv:", uv
                            except:
                                type_, value_, traceback_ = sys.exc_info()
                                exstr = str(traceback.format_exception(type_, value_, traceback_))
                                print("WARNING: rat color override exception: " + exstr)
                else:
                    print("WANRING: param_col is not str - not doing override checks...")        
                #####
                
                if cell_file_theme_df is None:
                    retdf.loc[retlen].ColorXml = match_color
                    #print ("cell_file_theme_df is None")
                else:
                    # now we have unique color list for thousands of colors already - already set from psc/pci/bcch 
                    if False and match_color in cell_file_theme_list:
                        print("match_color is in cell_file_theme_df.ColorXml")
                        tmp_color_index = retlen+1
                        tmp_color = match_color
                        while tmp_color in cell_file_theme_list:
                            tmp_color = get_default_color_for_index(tmp_color_index)
                            print(('re-generate param color :', param_col))
                            dprint ('match_value :', uv)
                            tmp_color_index += 1

                        retdf.loc[retlen].ColorXml = tmp_color
                    else:
                        retdf.loc[retlen].ColorXml = match_color
                        #dprint ("match_color is not in cell_file_theme_df.ColorXml")
                        dprint (match_color)
                        dprint (list(cell_file_theme_df.ColorXml))
                    cell_file_theme_list.append(retdf.loc[retlen].ColorXml)
                retdf.loc[retlen].match_value = uv
                #print "retdf.loc[retlen].match_value type",type(retdf.loc[retlen].match_value)," uv type ",type(uv)
                retdf.loc[retlen].PointSize = 6
                retlen += 1

        print("for uv in unique_vals done")
        #print "generate_theme_from_data - final retdf:", retdf
        #g_generate_theme_from_data_dict[param_col] = retdf
        return retdf
    
    else:

        n_buckets = 5.0

        if len(df) == 0:
            print("azq_theme_manager df len 0 while trying to gen dyn rage - ret none")
            return None
            
        data_min = df[param_col].min()
        data_max = df[param_col].max()

        print("data max"+str(type(data_max)) + str(data_max))

        if math.isnan(data_min):
            print("azq_theme_manager data_min isnan - ret none")
            return None

        if math.isnan(data_max):
            print("azq_theme_manager data_max isnan - ret none")
            return None
        
        data_width = (data_max-data_min)/n_buckets
        if data_width == 0.0:
            n_buckets = 1
        #print "min :"+str(data_min)+" max :"+str(data_max)+" width :"+str(data_width)

        color_header = ['ColorXml', 'Lower', 'Upper', 'PointSize']
    
        retdf = pd.DataFrame(columns=color_header)
        retlen = 0

        r = lambda: random.randint(0,255)

        for i in range(int(n_buckets)):
            retdf.loc[i] = None
            retdf.loc[i].ColorXml = get_default_color_for_index(i)
            retdf.loc[i].Lower = str(data_min+((data_width)*i))
            retdf.loc[i].Upper = str(data_min+((data_width)*(i+1)))
            retdf.loc[i].PointSize = 6

        """
        color_data = [
            ['#b7b7b7', str(data_min), str(data_min+(data_width)*1), '1'],
            ['#ff00ff', str(data_min+(data_width)*1), str(data_min+(data_width)*2), '1'],
            ['#ff8000', str(data_min+(data_width)*2), str(data_min+(data_width)*3), '1'],
            ['#ffff00', str(data_min+(data_width)*3), str(data_min+(data_width)*4), '1'],
            ['#00ff00', str(data_min+(data_width)*4), str(data_max), '1']
        ]
        """        
        #print("generate_theme_from_data return retdf ", retdf)
        return retdf
    
    return None

def generate_theme_with_step(start, end, step):
    if None in [start, end, step]:
        raise Exception('generate_theme_with_step Exception start, end, step is invalid:', start, end, step)

    color_header = ['ColorXml', 'Lower', 'Upper', 'PointSize']
    retdf = pd.DataFrame(columns=color_header)
    n_buckets = int((end-start)/step+0.5)
    last_upper = start
    for i in range(n_buckets):
        retdf.loc[i] = None
        retdf.loc[i].ColorXml = get_default_color_for_index(i)
        retdf.loc[i].Lower = str(last_upper)
        last_upper += step
        retdf.loc[i].Upper = str(last_upper)
        retdf.loc[i].PointSize = 6

    return retdf
