import integration_test_helpers
import sql_utils


def test():
    azmfp = "../example_logs/nr_nsa_exynos_s21/354505623113016-19_08_2021-16_45_22.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with integration_test_helpers.get_dbcon(dbfp) as dbcon:
        import pandas as pd
        time = "2021-08-19 16:44:47.186"
        log_hash_actual = pd.read_sql('select log_hash from logs', dbcon).iloc[0, 0]

        for log_hash in [log_hash_actual, None]:  # must work both with and without a valid log_hash
            evalstr = sql_utils.get_ex_eval_str_for_select_from_part(sql_utils.LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_SELECT_FROM_PART)
            print("eval_str:", evalstr)
            df = eval(evalstr)
            print("eval ex df.head():\n %s" % df.head(200))
            assert df.T.iloc[1,7] == 60

            df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon, sql_utils.LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_SELECT_FROM_PART, log_hash, time)
            print("get_lh_time_match_df_for_select_from_part df.head():\n %s" % df.head(200))
            assert df.T.iloc[1, 7] == 60

            df = sql_utils.get_lh_time_match_df_for_select_from_part(dbcon,
                                                                     sql_utils.LOG_HASH_TIME_MATCH_EVAL_STR_EXAMPLE_SELECT_FROM_PART,
                                                                     log_hash, "9999-08-18 16:44:34.430")
            print("get_lh_time_match_df_for_select_from_part df.head():\n %s" % df.head(200))
            assert pd.isnull(df.T.iloc[1, 7])


if __name__ == "__main__":
    test()
