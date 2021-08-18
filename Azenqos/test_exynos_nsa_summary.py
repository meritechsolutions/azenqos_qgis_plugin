import integration_test_helpers
import exynos_nr_summary
import exynos_lte_summary


def test():
    azmfp = "../example_logs/nr_exynos_s21/354505623113016-17_08_2021-17_32_44.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with integration_test_helpers.get_dbcon(dbfp) as dbcon:
        ts = "2021-08-17 17:31:59.482"
        df = exynos_nr_summary.get_disp_df(dbcon, ts)
        print("nr df.head():\n %s" % df.head(200))

        df = exynos_lte_summary.get_disp_df(dbcon, ts)
        print("lte df.head():\n %s" % df.head(200))

if __name__ == "__main__":
    test()
