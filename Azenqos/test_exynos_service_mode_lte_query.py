import contextlib

import integration_test_helpers
import sql_utils


def test():
    azmfp = "../example_logs/nr_nsa_exynos_s21/354505623113016-19_08_2021-16_45_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(integration_test_helpers.get_dbcon(dbfp)) as dbcon:
        import pandas as pd
        time = "2021-08-19 16:44:47.186"
        log_hash = pd.read_sql('select log_hash from logs', dbcon).iloc[0, 0]
        import exynos_service_mode_lte_query

        i = 0
        for sql in exynos_service_mode_lte_query.QUERY_LIST:
            df = sql_utils.get_lh_time_match_df_for_select_from_part(
            dbcon,
            sql,
            log_hash,
            time
            )
            print("lte df.head():\n %s" % df.head(200))
            if i == 0:
                assert df.iloc[3, 1] == 1450
            i += 1

if __name__ == "__main__":
    test()
