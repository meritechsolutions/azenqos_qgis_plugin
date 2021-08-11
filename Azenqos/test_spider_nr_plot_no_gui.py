import integration_test_helpers
import spider_plot


def test():
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp("../example_logs/nr_spider/353495110813164-30_07_2021-18_48_42 (222521 VINITA HOTEL B66 POST).azm")
    cell_files = ["../example_logs/nr_spider/5G_cellfile.txt"]

    df = spider_plot.gen_spider_df(cell_files, dbfp, "nr", "nr_detectedbeam1_pci_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":5000})
    print("neigh df:", df[["time", "nr_detectedbeam1_pci_1", "param_lat", "cell_lat", "pci", "arfcn", "distance_m"]].head())
    print("neigh df len:", len(df))
    assert len(df) == 73
    assert 0 == len(spider_plot.gen_spider_df(cell_files, dbfp, "nr", "nr_detectedbeam1_pci_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":50}))
    
    wkt_multiline_string = spider_plot.gen_wkt_lines_plot_rat_spider(cell_files, dbfp, "nr", "nr_servingbeam_pci_1", freq_code_match_mode=True, )
    assert wkt_multiline_string
    assert "-95.155332" in wkt_multiline_string
    
    df = spider_plot.gen_spider_df(cell_files, dbfp, "nr", "nr_servingbeam_pci_1", freq_code_match_mode=True, single_point_match_dict={"log_hash":475938916973971550, "time":'2021-07-30 18:20:31.105', "posid":223, "seqid":327865, "selected_lat":1, "selected_lon": 1})
    print("match df:\n", df)
    assert len(df) == 1


if __name__ == "__main__":
    test()
