import sqlite3

import pandas as pd

import integration_test_helpers
import spider_plot


def test():
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp("../example_logs/gsm_spider/869796043831455-18_05_2021-20_35_00 (WJPT5 2 g idel drive).azm")
    cell_files = ["../example_logs/gsm_spider/2G_cellfile.txt"]

    df = spider_plot.gen_spider_df(cell_files, dbfp, "gsm", "gsm_neighbor_bsic_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":5000})
    print("neigh df:", df[["time", "gsm_neighbor_bsic_1", "param_lat", "cell_lat", "bsic", "bcch", "distance_m"]].head())
    print("neigh df len:", len(df))
    assert len(df) == 221
    assert 0 == len(spider_plot.gen_spider_df(cell_files, dbfp, "gsm", "gsm_neighbor_bsic_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":50}))
    
    wkt_multiline_string = spider_plot.gen_wkt_lines_plot_rat_spider(cell_files, dbfp, "gsm", "gsm_bsic", freq_code_match_mode=True, )
    assert wkt_multiline_string
    assert "79.371443" in wkt_multiline_string
    
    df = spider_plot.gen_spider_df(cell_files, dbfp, "gsm", "gsm_bsic", freq_code_match_mode=True, single_point_match_dict={"log_hash":188254667382442641, "time":'2021-05-18 20:04:18.140', "posid":1495, "seqid":174414, "selected_lat":1, "selected_lon": 1})
    print("match df:\n", df)
    assert len(df) == 1


if __name__ == "__main__":
    test()
