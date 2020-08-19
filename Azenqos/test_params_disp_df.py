import zipfile
import os
import shutil
import params_disp_df
import sqlite3


def test():
    if os.path.isdir("tmp_test"):
        shutil.rmtree("tmp_test")
    os.mkdir("tmp_test")
    with zipfile.ZipFile("example_logs/nr_exynos_drive0/354569110529431-06_08_2020-18_59_45 (nrftp5).azm", 'r') as zip_ref:
        zip_ref.extract("azqdata.db", "tmp_test")
    dbfp = os.path.join("tmp_test","azqdata.db")
    assert os.path.isfile(dbfp)
    n_param_args = 8
    parameter_to_columns_list = [
        ("Band", map(lambda x: "nr_band_{}".format(x+1), range(n_param_args)) ),
        ("Band Type", map(lambda x: "nr_band_type_{}".format(x+1), range(n_param_args)) ),
        ("ARFCN", map(lambda x: "nr_dl_arfcn_{}".format(x+1), range(n_param_args)) ),
        ("Frequency", map(lambda x: "nr_dl_frequency_{}".format(x+1), range(n_param_args)) ),
        ("PCI", map(lambda x: "nr_servingbeam_pci_{}".format(x+1), range(n_param_args)) ),
        ("RSRP", map(lambda x: "nr_servingbeam_ss_rsrp_{}".format(x+1), range(n_param_args)) ),
        ("RSRQ", map(lambda x: "nr_servingbeam_ss_rsrq_{}".format(x+1), range(n_param_args)) ),
        ("SINR", map(lambda x: "nr_servingbeam_ss_sinr_{}".format(x+1), range(n_param_args)) ),
        ("Bandwidth", map(lambda x: "nr_bw_{}".format(x+1), range(n_param_args)) ),
        ("SSB SCS", map(lambda x: "nr_ssb_scs_{}".format(x+1), range(n_param_args)) ),
        ("SCS", map(lambda x: "nr_numerology_scs_{}".format(x+1), range(n_param_args)) ),
        ("PUSCH Power", map(lambda x: "nr_pusch_tx_power_{}".format(x+1), range(n_param_args)) ),
        ("PUCCH Power", map(lambda x: "nr_pucch_tx_power_{}".format(x+1), range(n_param_args)) ),
        ("SRS Power", map(lambda x: "nr_srs_tx_power_{}".format(x+1), range(n_param_args)) ),
    ]
    with sqlite3.connect(dbfp) as dbcon:
        # valid time
        ret = params_disp_df.get(dbcon, parameter_to_columns_list, '2020-08-06 18:51:38.000', default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=4000)
        print("ret.head():\n",ret.head())

        # invalid time must ret empty df
        ret = params_disp_df.get(dbcon, parameter_to_columns_list, '2020-08-05 18:51:38.000', default_table="nr_cell_meas", not_null_first_col=True, custom_lookback_dur_millis=4000)
        print("ret.head():\n",ret.head())
    

if __name__ == "__main__":
    test()
