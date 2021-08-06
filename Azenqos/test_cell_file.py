import azq_cell_file


def test():
    cell_files = ["../example_logs/4g_cellfile_bad_gps/4G_cellfile_test_demo.txt"]
    df = azq_cell_file.read_cellfiles(cell_files, "lte")    
    assert len(df)
    assert 'cell_lat' not in df.columns
    azq_cell_file.add_cell_lat_lon_to_cellfile_df(df, distance=0.001)
    assert 'cell_lat' in df.columns
    assert "pci" in df.columns
    assert "earfcn" in df.columns
    print("df.head()\n", df.head())

    cell_files = ["../example_logs/4g_cellfile_bad_gps/4G_cellfile_test_demo_earfcn_as_ch.txt"]
    df = azq_cell_file.read_cellfiles(cell_files, "lte")
    assert len(df)
    assert 'cell_lat' not in df.columns
    azq_cell_file.add_cell_lat_lon_to_cellfile_df(df, distance=0.001)
    assert 'cell_lat' in df.columns
    assert "pci" in df.columns
    assert "earfcn" in df.columns
    print("df.head()\n", df.head())

    df = azq_cell_file.read_cellfiles(cell_files, "lte", add_cell_lat_lon_sector_distance=0.001)    
    assert len(df)
    assert 'cell_lat' in df.columns
    print("df.head()\n", df.head())
    assert abs(df.cell_lat.iloc[0] - 13.727946) < 0.000001
    assert abs(df.cell_lon.iloc[0] - 100.77660) < 0.000001
    assert "pci" in df.columns
    assert "earfcn" in df.columns

    wrong_cell_files = ["../example_logs/4g_cellfile_bad_gps/4G_cellfile_test_demo_missing_cols.txt"]
    caught = False
    df = None
    try:
        df = azq_cell_file.read_cellfiles(wrong_cell_files, "lte")
    except Exception as e:
        if "does not have the required column" in str(e):
            caught = True
    assert caught
    assert df is None
    print("success")

    cell_files = ["../example_logs/4g_cellfile_bad_gps/3G_cellfile.txt"]
    df = azq_cell_file.read_cellfiles(cell_files, "wcdma", add_cell_lat_lon_sector_distance=0.001)
    assert len(df)
    assert 'cell_lat' in df.columns
    print("df.head()\n", df.head())
    assert "psc" in df.columns
    assert "uarfcn" in df.columns
        


if __name__ == "__main__":
    test()
