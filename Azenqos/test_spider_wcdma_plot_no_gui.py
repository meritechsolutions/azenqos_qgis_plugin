import integration_test_helpers
import spider_plot


def test():
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp("../example_logs/wcdma_spider/354701091187224-30_07_2021-11_48_39.azm")
    cell_files = ["../example_logs/wcdma_spider/3G_cellfile_2.txt"]

    df = spider_plot.gen_spider_df(cell_files, dbfp, "wcdma", "wcdma_mset_sc_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":5000})
    print("neigh df:", df[["time", "wcdma_mset_sc_1", "param_lat", "cell_lat", "psc", "uarfcn", "distance_m"]].head())
    print("neigh df len:", len(df))
    assert len(df) == 464
    assert 0 == len(spider_plot.gen_spider_df(cell_files, dbfp, "wcdma", "wcdma_mset_sc_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":50}))
    
    wkt_multiline_string = spider_plot.gen_wkt_lines_plot_rat_spider(cell_files, dbfp, "wcdma", "wcdma_aset_sc_1", freq_code_match_mode=True, )
    assert wkt_multiline_string
    assert "101.57235" in wkt_multiline_string
    
    df = spider_plot.gen_spider_df(cell_files, dbfp, "wcdma", "wcdma_aset_sc_1", freq_code_match_mode=True, single_point_match_dict={"log_hash":391646146520643151, "time":'2021-07-30 11:33:56.979', "posid":1378, "seqid":1410709, "selected_lat":1, "selected_lon": 1})
    print("match df:\n", df)
    assert len(df) == 1


if __name__ == "__main__":
    test()
