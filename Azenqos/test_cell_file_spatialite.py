import azq_cell_file
import azq_utils
import os


def test():
    cell_files = ["../example_logs/large_cell/4g_large.csv"]
    for cell_file in cell_files:
        if not os.path.isfile(cell_file):
            print("file not found: {} - abort test".format(cell_file))
            return
            
    rat = 'lte'
    azq_utils.timer_start("cell_spatial")
    df = azq_cell_file.read_cellfiles(cell_files, "lte", add_sector_polygon_wkt_sector_size_meters=40)
    azq_utils.timer_print("cell_spatial")
    df = df.reset_index()
    azq_utils.timer_print("cell_spatial")
    # create .sql
    create_cellfile_sql_str = azq_utils.get_create_cellfile_spatialite_header(rat)
    create_cellfile_sql_str += azq_utils.get_create_cellfile_spatialite_create_table(rat, list(df.columns))
    create_cellfile_sql_str += azq_utils.get_create_cellfile_spatialite_insert_cell(rat, df)
    create_cellfile_sql_str += azq_utils.get_create_cellfile_spatialite_footer()
    azq_utils.timer_print("cell_spatial")
    print("create_cellfile_sql_str: ", create_cellfile_sql_str[-120:])

    cell_sql_fp = os.path.join('tmp_gen', "cell_file_sectors_" + rat + ".sql")
    if os.path.isfile(cell_sql_fp):
        os.remove(cell_sql_fp)

    f = open(cell_sql_fp, 'w')
    f.write(create_cellfile_sql_str)
    f.close()
    # run sql and create .db
    spatialite_bin = azq_utils.get_spatialite_bin()
    cel_spatial_db_fp = cell_sql_fp[:-3] + "db"
    if os.path.isfile(cel_spatial_db_fp):
        os.remove(cel_spatial_db_fp)
    print("cell_sql_fp:", cell_sql_fp)
    cmd = [spatialite_bin, "-init", cell_sql_fp, cel_spatial_db_fp, ".quit"]
    ret = azq_utils.call_no_shell(cmd)
    print("ret", ret)
    azq_utils.timer_print("cell_spatial")


if __name__ == "__main__":
    test()