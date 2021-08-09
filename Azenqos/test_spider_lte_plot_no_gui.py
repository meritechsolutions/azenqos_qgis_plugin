import sqlite3

import pandas as pd

import integration_test_helpers
import spider_plot


def test():
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp("../example_logs/4g_cellfile_bad_gps/354569110523269 30_7_2021 14.52.10.azm")
    cell_files = ["../example_logs/4g_cellfile_bad_gps/4G_cellfile_test_demo.txt"]

    with sqlite3.connect(dbfp) as dbcon:
        npci_df = pd.read_sql("select time, lte_neigh_physical_cell_id_1 from lte_neigh_meas", dbcon)
        print("npci_df:", npci_df.head())
        df = spider_plot.gen_spider_df(cell_files, dbfp, "lte", "lte_neigh_physical_cell_id_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":5000})
        print("neigh df:", df[["time", "lte_neigh_physical_cell_id_1", "param_lat", "cell_lat", "pci", "earfcn", "distance_m"]].head())
        print("neigh df len:", len(df))
        assert len(df) == 13
        assert 0 == len(spider_plot.gen_spider_df(cell_files, dbfp, "lte", "lte_neigh_physical_cell_id_1", single_point_match_dict=None, freq_code_match_mode=True, options_dict={"distance_limit_m":50}))


    df = spider_plot.gen_spider_df(cell_files, dbfp, "lte", "lte_physical_cell_id_1", single_point_match_dict=None)
    assert len(df) == 2
    assert abs(df.cell_lat.iloc[0] - 13.6695) < 0.000001
    assert abs(df.param_lat.iloc[0] - 13.668644) < 0.000001

    wkt_multiline_string = spider_plot.gen_wkt_lines_plot_rat_spider(cell_files, dbfp, "lte", "lte_physical_cell_id_1")
    assert wkt_multiline_string
    assert "100.7099" in wkt_multiline_string

    df = spider_plot.gen_spider_df(cell_files, dbfp, "lte", "lte_physical_cell_id_1", single_point_match_dict={"log_hash":474693827429639429, "time":'2021-07-30 14:33:58.440', "posid":1521, "seqid":904781, "selected_lat":1, "selected_lon": 1})
    print("match df:\n", df)
    assert len(df) == 1

    ''' todo add test that has same posid
    df = spider_plot.gen_spider_df(cell_files, dbfp, "lte", "lte_neigh_physical_cell_id_1",
                                   single_point_match_dict={"log_hash": 474693827429639429,
                                                            "time": '2021-07-30 14:33:58.440', "posid": 1521,
                                                            "seqid": 904781, "selected_lat": 1, "selected_lon": 1})
    print("match df:\n", df)
    assert len(df) == 1
    '''



if __name__ == "__main__":
    test()
