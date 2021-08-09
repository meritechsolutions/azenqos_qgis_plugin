import sqlite3

import pandas as pd

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



if __name__ == "__main__":
    test()
