import integration_test_helpers
import linechart_query
import contextlib
import time

def test():
    azmfp = "../example_logs/line_chart/354505624002242-13_09_2021-14_32_00_processed.azm"
    dbfp = integration_test_helpers.unzip_azm_to_tmp_get_dbfp(azmfp)

    with contextlib.closing(integration_test_helpers.get_dbcon(dbfp)) as dbcon:
        start_time = time.time()
        df_iter = linechart_query.get_chart_df(dbcon, {'nr_servingbeam_ss_rsrp_1': {'name': 'nr_servingbeam_ss_rsrp_1'}, 'nr_servingbeam_ss_rsrq_1': {'name': 'nr_servingbeam_ss_rsrq_1'}, 'nr_servingbeam_ss_sinr_1': {'name': 'nr_servingbeam_ss_sinr_1'}}, apply_mode =True)
        
        print("--- apply_mode ---" , (time.time() - start_time))
        
        start_time = time.time()
        df = linechart_query.get_chart_df(dbcon, {'nr_servingbeam_ss_rsrp_1': {'name': 'nr_servingbeam_ss_rsrp_1'}, 'nr_servingbeam_ss_rsrq_1': {'name': 'nr_servingbeam_ss_rsrq_1'}, 'nr_servingbeam_ss_sinr_1': {'name': 'nr_servingbeam_ss_sinr_1'}},)
        print("--- merge ---" , (time.time() - start_time))
        
        assert df_iter[0].equals(df[0])


if __name__ == "__main__":
    test()