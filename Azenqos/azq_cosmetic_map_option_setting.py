# set dashboard at azq_web_dashboard/resource/map_plot_info.txt
cosmetic_option = dict()
cosmetic_option["scatter_point_size"] = 25
cosmetic_option["figsize_max"] = 12.0
cosmetic_option["force_ant_bw"] = None
cosmetic_option["cell_arm_length"] = 70
cosmetic_option["sequential_plot"] = True
cosmetic_option["groupby_posid_val_pandas_method"] = "mean()"
cosmetic_option["use_satellite_map"] = False
cosmetic_option["show_legends"] = True
cosmetic_option["max_legend_text_size"] = 16
cosmetic_option["min_legend_text_size"] = 6
cosmetic_option["cell_custom_label_format"] = None
cosmetic_option["site_detail_label_format"] = "#SITE"
cosmetic_option["lat_add_crop_if_less_than"] = 0  # no add crop by default - now 0.003
cosmetic_option["lat_add_crop_percent"] = 40.0
cosmetic_option["lon_add_crop_if_less_than"] = 0  # no add crop by default - 0.003
cosmetic_option["lon_add_crop_percent"] = 50.0
cosmetic_option["grid_color"] = "#707070"
cosmetic_option["use_white_background"] = False
cosmetic_option["cell_on_top"] = True
cosmetic_option["full_grid_on_fig"] = False
cosmetic_option["continuous_plot_resample_element_list"] = [
    "wifi_active_",
    "wifi_scanned_",
    "lte_transmission_mode_l3",
]
cosmetic_option["continuous_plot_resample_forward_fill"] = True
cosmetic_option["continuous_plot_resample_ignore_expired"] = True
cosmetic_option["fig_w"] = None
cosmetic_option["fig_h"] = None
cosmetic_option["site_label_offset"] = 0
cosmetic_option["lock_password"] = None
cosmetic_option["legend_location"] = 4
cosmetic_option["crop_map_to_plot_only"] = False
cosmetic_option["site_font_size"] = None
cosmetic_option["cell_font_size"] = None
cosmetic_option["treat_some_id_as_range"] = False
cosmetic_option[
    "custom_theme"
] = """{
                                        'modulation':'{"ColorXml":{"0":"#ffff00","1":"#00ff00","2":"#ff0000"},"Lower":{"0":null,"1":null,"2":null},"Upper":{"0":null,"1":null,"2":null},"PointSize":{"0":6,"1":6,"2":6},"match_value":{"0":"16QAM","1":"64QAM","2":"QPSK"}}',
                                        'rat_band_wise':'{"ColorXml":{"00":"#674ea7","01":"#999999","02":"#990000","03":"#ff0000","04":"#ff9900","05":"#ffff00","06":"#00ff00","07":"#38761d","08":"#00ffff","09":"#3d85c6","10":"#0000ff"},"Lower":{"00":null,"01":null,"02":null,"03":null,"04":null,"05":null,"06":null,"07":null,"08":null,"09":null,"10":null},"Upper":{"00":null,"01":null,"02":null,"03":null,"04":null,"05":null,"06":null,"07":null,"08":null,"09":null,"10":null},"PointSize":{"00":6,"01":6,"02":6,"03":6,"04":6,"05":6,"06":6,"07":6,"08":6,"09":6,"10":6},"match_value":{"00":"GSM: 8","01":"GSM: 3","02":"WCDMA: 5","03":"WCDMA: 8","04":"WCDMA: 3","05":"WCDMA: 1","06":"LTE: 8","07":"LTE: 3","08":"LTE: 1","09":"LTE: 40","10":"LTE: 38"}}',
                                        'technology':'{"ColorXml":{"0":"#CD5C5C","1":"#556B2F","2":"#9400D3","3":"#00FA9A","4":"#000080","5":"#C71585","6":"#FF8C00","7":"#20B2AA","8":"#DAA520","9":"#00FFFF"},"Lower":{"0":null,"1":null,"2":null,"3":null,"4":null,"5":null,"6":null,"7":null,"8":null,"9":null},"PointSize":{"0":6,"1":6,"2":6,"3":6,"4":6,"5":6,"6":6,"7":6,"8":6,"9":6},"Upper":{"0":null,"1":null,"2":null,"3":null,"4":null,"5":null,"6":null,"7":null,"8":null,"9":null},"match_value":{"0":"GPRS","1":"HSDPA","2":"HSPA","3":"HSPA+","4":"HSUPA","5":"LTE","6":"UMTS","7":"UNKNOWN","8":"EDGE","9":"WIFI"}}',
                                        'gsm_speechcodecrx':'{"ColorXml":{"0":"#CD5C5C","1":"#556B2F","2":"#9400D3","3":"#00FA9A","4":"#000080","5":"#C71585","6":"#FF8C00","7":"#20B2AA","8":"#DAA520","9":"#00FFFF","10":"#228B22","11":"#DA70D6","12":"#2F4F4F","13":"#8B4513","14":"#BDB76B","15":"#FFE4C4","16":"#DB7093","17":"#8FBC8F"},"Lower":{"0":null,"1":null,"2":null,"3":null,"4":null,"5":null,"6":null,"7":null,"8":null,"9":null,"10":null,"11":null,"12":null,"13":null,"14":null,"15":null,"16":null,"17":null},"Upper":{"0":null,"1":null,"2":null,"3":null,"4":null,"5":null,"6":null,"7":null,"8":null,"9":null,"10":null,"11":null,"12":null,"13":null,"14":null,"15":null,"16":null,"17":null},"PointSize":{"0":6,"1":6,"2":6,"3":6,"4":6,"5":6,"6":6,"7":6,"8":6,"9":6,"10":6,"11":6,"12":6,"13":6,"14":6,"15":6,"16":6,"17":6},"match_value":{"0":"AMR:4.75 Kbps","1":"AMR:5.15 Kbps","2":"AMR:5.90 Kbps","3":"AMR:6.70 Kbps","4":"AMR:7.40 Kbps","5":"AMR:7.95 Kbps","6":"AMR:10.20 Kbps","7":"AMR:12.20 Kbps","8":"AMR-WB:6.60 Kbps","9":"AMR-WB:8.85 Kbps","10":"AMR-WB:12.65 Kbps","11":"AMR-WB:14.25 Kbps","12":"AMR-WB:15.85 Kbps","13":"AMR-WB:18.25 Kbps","14":"AMR-WB:19.85 Kbps","15":"AMR-WB:23.05 Kbps","16":"AMR-WB:23.85 Kbps","17":"AMR-WB:AMR-WB SID (Comfort Noise Frame)"}}'
                                    }"""


def get_cosmetic_option_keys():
    global cosmetic_option
    return cosmetic_option.keys()


def get_cosmetic_option(key):
    global cosmetic_option
    return cosmetic_option[key]


def set_cosmetic_option(key, value):
    global cosmetic_option
    cosmetic_option[key] = value
