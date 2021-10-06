import integration_test_helpers
import cell_layer_task


def test():
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp("../example_logs/4g_cellfile_bad_gps/354569110523269 30_7_2021 14.52.10.azm")
    cell_files = ["../example_logs/4g_cellfile_bad_gps/4G_cellfile_test_demo.txt"]

    df = cell_layer_task.cell_in_logs_with_color(cell_files, dbfp, 'lte')
    assert  len(df) == 1

if __name__ == "__main__":
    test()
