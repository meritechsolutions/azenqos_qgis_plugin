import zipfile
import os
import shutil
import params_disp_df
import sqlite3
import integration_test_helpers
import global_config as gc
import pandas as pd


def test():
    azmfp = "example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    n_param_args = 8

    # below example RUNS ONE QUERY FOR EACH PARAM - WHICH MUST BE AVOIDED - HERE WE USE FOR TESTING ONLY - see better example in nr_query.get_nr_radio_params_disp_df() called from test_nr_radio_params.py
    
    parameter_to_columns_list = [
        ("Band",  list(map(lambda x: "nr_band_{}".format(x+1), range(n_param_args))) ),
        ("ARFCN", list(map(lambda x: "nr_dl_arfcn_{}".format(x+1), range(n_param_args))) ),
        ("PCI",   list(map(lambda x: "nr_servingbeam_pci_{}".format(x+1), range(n_param_args))) ),
        ("RSRP",  list(map(lambda x: "nr_servingbeam_ss_rsrp_{}".format(x+1), range(n_param_args))) ),
        ("RSRQ",  list(map(lambda x: "nr_servingbeam_ss_rsrq_{}".format(x+1), range(n_param_args))) ),
        ("SINR",  list(map(lambda x: "nr_servingbeam_ss_sinr_{}".format(x+1), range(n_param_args))) ),
                
        ("PUSCH Power", list(map(lambda x: "nr_pusch_tx_power_{}".format(x+1), range(n_param_args))) ),
        ("PUCCH Power", list(map(lambda x: "nr_pucch_tx_power_{}".format(x+1), range(n_param_args))) ),
        ("SRS Power", list(map(lambda x: "nr_srs_tx_power_{}".format(x+1), range(n_param_args))) ),
    ]
    with sqlite3.connect(dbfp) as dbcon:

        #################### test query separately
        # valid time
        time_before = "2020-08-18 13:47:42.382"
        ret = params_disp_df.get(dbcon, parameter_to_columns_list, time_before, default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=4000)
        print("valid time df ret.head():\n",ret.head())
        print("ret.iloc[0,1]:", ret.iloc[0,1])
        assert ret.iloc[0,1] == 41

        # invalid time must ret empty df
        ret = params_disp_df.get(dbcon, parameter_to_columns_list, '2018-08-05 18:51:38.000', default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=4000)
        print("invalid time df must be empty ret.head():\n",ret.head())
        assert ret.iloc[0,1] == None

        # invalid table must ret empty df
        ret = params_disp_df.get(dbcon, parameter_to_columns_list, '2018-08-05 18:51:38.000', default_table="some_non_existant_table", not_null_first_col=True, custom_lookback_dur_millis=4000)
        print("invalid time df must be empty ret.head():\n",ret.head())
        assert ret.iloc[0,1] == None


        ########################### test query together
        n_param_args = 8
        parameter_to_columns_list = [
            ("Time", ["time"] ),            
            (  # these params below come together so query them all in one query
                [
                    "Band",
                    "ARFCN",
                    "PCI",
                    "RSRP",
                    "RSRQ",
                    "SINR"
                ],
                list(map(lambda x: "nr_band_{}".format(x+1), range(n_param_args))) +
                list(map(lambda x: "nr_dl_arfcn_{}".format(x+1), range(n_param_args))) +
                list(map(lambda x: "nr_servingbeam_pci_{}".format(x+1), range(n_param_args))) +
                list(map(lambda x: "nr_servingbeam_ss_rsrp_{}".format(x+1), range(n_param_args))) +
                list(map(lambda x: "nr_servingbeam_ss_rsrq_{}".format(x+1), range(n_param_args))) +
                list(map(lambda x: "nr_servingbeam_ss_sinr_{}".format(x+1), range(n_param_args)))
            ),
            (  # these params below come together but not same row with rsrp etc above so query them all in their own set below
                [
                    "PUSCH TxPower",
                    "PUCCH TxPower",
                    "SRS TxPower"
                ],
                list(map(lambda x: "nr_pusch_tx_power_{}".format(x+1), range(n_param_args)))+
                list(map(lambda x: "nr_pucch_tx_power_{}".format(x+1), range(n_param_args)))+
                list(map(lambda x: "nr_srs_tx_power_{}".format(x+1), range(n_param_args)))
            )
        ]

        # existing table
        ret = params_disp_df.get(dbcon, parameter_to_columns_list, time_before, default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS)
        print("query together ret.head(10):\n",ret.head(10))
        df = ret
        assert df.iloc[1,1] == 41
        assert len(df) == 10
        assert len(df.columns) == 9

        # non-existing table
        ret = params_disp_df.get(dbcon, parameter_to_columns_list, time_before, default_table="non_existant_table", not_null_first_col=True, custom_lookback_dur_millis=gc.DEFAULT_LOOKBACK_DUR_MILLIS)
        df = ret
        print("query together ret.head(10):\n",ret.head(10))
        assert pd.isnull(ret.iloc[1,1])
        assert len(df) == 10
        assert len(df.columns) == 9

if __name__ == "__main__":
    test()
