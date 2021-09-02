import azm_sqlite_merge
import azq_utils
import os

def test():
    azm_list = [
        "../example_logs/nr_sa_exynos_s21_ex0/350299943614770-20_08_2021-15_55_05 (airplane then speedtest).azm",
        "../example_logs/nr_sa_exynos_s21_ex0/350299943614770-24_08_2021-16_13_20 (speedtest then airplane ramkomut).azm",
        "../example_logs/nr_nsa_exynos_s21/354505623113016-19_08_2021-16_45_22.azm"
    ]
    out_db = os.path.join(azq_utils.get_module_path(), "test_combined.db")
    azm_sqlite_merge.merge(azm_list, out_db)
    

if __name__ == "__main__":
    test()
