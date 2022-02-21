import integration_test_helpers
import linechart_query
import contextlib
import analyzer_vars

def test():
    azmfp = "../example_logs/line_chart/354505624002242-13_09_2021-14_32_00_processed.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)
    gc = analyzer_vars.analyzer_vars()

    with contextlib.closing(integration_test_helpers.get_dbcon(dbfp)) as dbcon:
        df = linechart_query.get_chart_df(dbcon, {'nr_servingbeam_ss_rsrp_1': {'name': 'nr_servingbeam_ss_rsrp_1'}, 'nr_servingbeam_ss_rsrq_1': {'name': 'nr_servingbeam_ss_rsrq_1'}, 'nr_servingbeam_ss_sinr_1': {'name': 'nr_servingbeam_ss_sinr_1'}},gc)
        print(df)



if __name__ == "__main__":
    test()