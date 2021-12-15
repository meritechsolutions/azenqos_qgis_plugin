import sqlite3
import contextlib
from types import prepare_class
import integration_test_helpers
import calculate_poi_dialog
import research_poi_list
import azq_cell_file
import pandas as pd
import timeit

def test():
    azmfp = "../example_logs/test_poi/overview_d32802a6-895f-4954-be1a-3fd840408678.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(sqlite3.connect(dbfp)) as dbcon:
        start = timeit.default_timer()
        cov_column_name_list = []
        cov_df, cov_column_name_list = calculate_poi_dialog.get_technology_df(dbcon, cov_column_name_list)
        cov_df["lat"] = cov_df["geom"].apply(lambda x: calculate_poi_dialog.geomToLatLon(x)[0])
        cov_df["lon"] = cov_df["geom"].apply(lambda x: calculate_poi_dialog.geomToLatLon(x)[1])
        prepare_cov_df_time = timeit.default_timer()
        print('prepare_cov_df_time: ', prepare_cov_df_time - start) 
        offset = azq_cell_file.METER_IN_WGS84 * 1000.0
        poi_list = research_poi_list.poi_list
        if len(poi_list) > 0:
            row_df_list = calculate_poi_dialog.calculate_poi_cov(poi_list, cov_df, cov_column_name_list, "lat", "long", offset )
        df = pd.DataFrame(row_df_list)
        stop = timeit.default_timer()
        print('Time: ', stop - start) 
        print(df)


if __name__ == "__main__":
    test()
