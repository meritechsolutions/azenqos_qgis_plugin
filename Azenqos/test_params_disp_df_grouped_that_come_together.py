import zipfile
import os
import shutil
import params_disp_df
import sqlite3
import sqlite3
import integration_test_helpers

def test():
    azmfp = "example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    n_param_args = 8
    parameter_to_columns_list = [
        (
            [
                "Band",
                "ARFCN",
                "PCI"
            ],
            list(map(lambda x: "nr_band_{}".format(x+1), range(n_param_args))) +
            list(map(lambda x: "nr_dl_arfcn_{}".format(x+1), range(n_param_args))) +
            list(map(lambda x: "nr_servingbeam_pci_{}".format(x+1), range(n_param_args)))
        )
    ]
    with sqlite3.connect(dbfp) as dbcon:
        # valid time
        time_before = "2020-08-18 13:47:42.382"
        df_pdd = params_disp_df.get(dbcon, parameter_to_columns_list, time_before, default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=4000)
        print("df_pdd.head():\n",df_pdd.head())
        assert df_pdd.iloc[0, 1] == 41

        # invalid time
        df_pdd = params_disp_df.get(dbcon, parameter_to_columns_list, '2020-08-05 18:51:38.000', default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=4000)
        print("empty df_pdd.head():\n",df_pdd.head())

if __name__ == "__main__":
    test()
