import integration_test_helpers
import nr_data_query
import contextlib

def test():
    azmfp = "../example_logs/nr_nsa_exynos_s21/354505623113016-19_08_2021-16_45_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(integration_test_helpers.get_dbcon(dbfp)) as dbcon:
        df = nr_data_query.get_nr_data_params_disp_df(dbcon, "2021-08-19 16:44:47.186")
        print("df.head():\n %s" % df.head(200))


if __name__ == "__main__":
    test()
