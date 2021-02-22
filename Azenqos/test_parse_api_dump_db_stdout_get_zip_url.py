import azq_server_api


def test():

    proc_stdout_str = """=== gen module  py_eval  DONE total duration: 1.501236 seconds
=== all processing modules DONE...
timer: main to now: 1.60929 seconds
timer: process to now: 1.501334 seconds
process_sha_cols_generic process duration all sum(): 1.492797
process_sha_cols_generic process duration summary head():

rank: 0 duration: 1.492797 secs - mod-params: py_eval << dump_db.process_cell(dbcon, '')
===== sql_to_duration_stats df.head(30):
                            code  duration
0  select * from logs             0.269005
4  select * from wcdma_cell_meas  0.090377
5  select * from gsm_cell_meas    0.073223
2  select * from signalling       0.068086
3  select * from lte_cell_meas    0.064096
1  select * from events           0.054653
azq_output stage START - duration from main start:
timer: main to now: 1.616815 seconds

---### GET_PYPROCESS_OUTPUT ORI ###---
{'py_eval': {'6588e8d5b1eb452f061271099275b65a30a92aa5': '/host_shared_dir/tmp_gen/tmp_dump_db_66f22df0-30ba-4520-84a2-c79b914dd22f.db.zip'}}
---### GET_PYPROCESS_OUTPUT ORI ###---
---### GET_PYPROCESS_OUTPUT JSON ###---
{
 "ret_type": "<type 'str'>", 
 "ret_dump": "/tmp_gen/tmp_dump_db_66f22df0-30ba-4520-84a2-c79b914dd22f.db.zip", 
 "ret": "/host_shared_dir/tmp_gen/tmp_dump_db_66f22df0-30ba-4520-84a2-c79b914dd22f.db.zip"
}
---### GET_PYPROCESS_OUTPUT JSON ###---
azq_output stage DONE - duration from main start:
timer: main to now: 1.616971 seconds
timer: output to now: 0.000211 seconds
successfully closed dbcon
pg_engine dispose() successful
successfully closed all pg dbcons
SUCCESS == please visit us again soon
"""
    
    server = "https://localhost/"
    ret_dict = azq_server_api.parse_py_eval_ret_dict_from_stdout_log(proc_stdout_str)
    url = azq_server_api.api_relative_path_to_url(server, ret_dict['ret_dump'])
    print("url:", url)
    assert url == "https://localhost/tmp_gen/tmp_dump_db_66f22df0-30ba-4520-84a2-c79b914dd22f.db.zip"
    
    
if __name__ == "__main__":
    test()


