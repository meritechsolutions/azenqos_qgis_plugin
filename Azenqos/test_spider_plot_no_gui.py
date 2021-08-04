import spider_plot
import analyzer_vars
import azq_utils
import integration_test_helpers


def test():
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp("../example_logs/4g_cellfile_bad_gps/354569110523269 30_7_2021 14.52.10.azm")
    cell_files = ["../example_logs/4g_cellfile_bad_gps/4G_cellfile_test_demo.txt"]

    df = spider_plot.gen_spider_df(cell_files, dbfp, "lte", "lte_physical_cell_id_1", single_point_layer_time=None)
    assert len(df) == 2
    assert abs(df.cell_lat.iloc[0] - 13.6695) < 0.000001
    assert abs(df.param_lat.iloc[0] - 13.668644) < 0.000001

    wkt_multiline_string = spider_plot.gen_wkt_lines_plot_rat_spider(cell_files, dbfp, "lte", "lte_physical_cell_id_1")
    assert wkt_multiline_string
    assert "100.7099" in wkt_multiline_string


if __name__ == "__main__":
    test()
