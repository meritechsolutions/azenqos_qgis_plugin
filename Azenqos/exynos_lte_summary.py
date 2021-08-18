import params_disp_df


def get_disp_df(dbcon, time_before):
    parameter_to_columns_list = [
        (
            [
                "Time",
                "LTE Band",
                "LTE Bandwidth (MHz)"
            ],
            [
                "time",
                "exynos_basic_info_lte_band",
                "exynos_basic_info_lte_bw_mhz",
            ],
            "exynos_basic_info_lte",
        ),
    ]
    return params_disp_df.get(
        dbcon,
        parameter_to_columns_list,
        time_before,
        not_null_first_col=True,
        custom_lookback_dur_millis=params_disp_df.DEFAULT_LOOKBACK_DUR_MILLIS,
    )


