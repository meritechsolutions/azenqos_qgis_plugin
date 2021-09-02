import azm_sqlite_merge
import azq_utils
import os

def test():
    azm_list = [
        "../example_logs/nr_sa_exynos_s21_ex0/350299943614770-20_08_2021-15_55_05 (airplane then speedtest).azm",
        "../example_logs/nr_sa_exynos_s21_ex0/350299943614770-24_08_2021-16_13_20 (speedtest then airplane ramkomut).azm"
    ]
    out_azm = os.path.join(azq_utils.tmp_gen_path(), "tmp_combined.azm")
    azm_sqlite_merge.merge(azm_list, out_azm)
    

if __name__ == "__main__":
    test()
