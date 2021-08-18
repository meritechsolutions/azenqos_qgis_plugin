import integration_test_helpers
import nr_radio_query


def test():
    azmfp = "../example_logs/nr_exynos_s21/354505623113016-17_08_2021-11_32_40.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with integration_test_helpers.get_dbcon(dbfp) as dbcon:
        df = nr_radio_query.get_nr_radio_params_disp_df(dbcon, "2021-08-17 11:23:53.649")
        print("df.head():\n %s" % df.head(200))

if __name__ == "__main__":
    test()