import azq_server_api


def test():

    proc_stdout_str = """azq_report_gen version 2.45 Copyright (C) 2010-2020 Freewill FX Co., Ltd. All rights reserved.
not LIVE_CMD_REQUEST_STR or not WEB_DOMAIN_NAME
starting command-line GET_PYPROCESS_OUTPUT process_module mode...
dbfile: PG_AZM_DB_MERGE
NOT MERGE_AZQML;;; mode
('set_tmp_process_dir:', None)
('set_tmp_process_dir:', '/host_shared_dir/tmp_gen/tmp_azq_report_gen_pg_ecc127ae-44e4-4401-811a-704dd578ef7c')
get_pg_engine1
get_pg_engine1
get_pg_engine final log_hash_list: ['475966451990630998', '475966451990873852']
get_existing_dbcon_for_pg_log_hash_list NOT found matching dbcon
pg_engine: dbcon: <sqlalchemy.engine.base.Connection object at 0x7f900c28b710> log_hash_list: ['475966451990630998', '475966451990873852']
len(log_hash_list) > 1: check and omit indoor logs
get_indoor_log_hash_df dbcon in g_dbcon_to_uploaded_logs_df_dict
indoor_log_hash_df: Empty DataFrame
Columns: [log_hash]
Index: []
log_hash_list: ['475966451990630998', '475966451990873852']
not totally indoor logs, filter out indoor logs...
lhdf:
             log_hash
0  475966451990873852
1  475966451990630998
not_in_db_sr: Series([], Name: log_hash, dtype: object)
timespan_sql: select (min(log_start_time) - INTERVAL '3000 min') as log_start_time, (max(log_end_time) + INTERVAL '3000 min') as log_end_time from all_logs.logs where log_hash in (475966451990630998,475966451990873852)
timespan_df:            log_start_time            log_end_time
0 2020-12-24 12:43:18.176 2020-12-31 12:51:41.457
###### create_temp_view_for_table with log_hash_list start
timer: pg_create_temp_views to now: 0.025665 seconds
###### create_temp_view_for_table with log_hash_list done
timer: get_dbcon_for_pg_log_hash_list to done: 0.103476 seconds
get_log_hash_list_for_pg_dbcon <sqlalchemy.engine.base.Connection object at 0x7f900c28b710> ret ['475966451990630998', '475966451990873852']
get_indoor_log_hash_df dbcon in g_dbcon_to_uploaded_logs_df_dict
azq_reprort_gen log_hash_list is_indoor: 0
not doing pg combined_time_clone_gps
main start: dbfile: PG_AZM_DB_MERGE dbcon: <sqlalchemy.engine.base.Connection object at 0x7f900c28b710>
extracting module name and params from --GET_PYPROCESS_OUTPUT value specified...
=== all processing modules START...
timer: main to now: 0.109534 seconds
## list and process all listed modules for template_xlsx or GET_PYPROCESS_OUTPUT modes
list of all modules to process:  set(['py_eval'])
no cellfiles specified - skip pre-populate color matching for lte/wcdma/gsm cellfiles step
timer: process to now: 5.7e-05 seconds
=== gen module [ py_eval ] START
module:  py_eval  process_cell func found - supplying module_params 
timer: process to now: 0.387633 seconds
process_sha_cols_generic: mod_name: py_eval n args_sets: 1
get_log_hash_list_for_pg_dbcon <sqlalchemy.engine.base.Connection object at 0x7f900c28b710> ret ['475966451990630998', '475966451990873852']
is_pg_dbcon - log_hash_list len: 2
len(log_hash_list) >= N_LOGS_TRIGGER_ONLY_SPARK_MODE 2 so set SPARK_MODE_DISABLE_DIRECT_PANDAS_SQL_ENGINE True
pscg start gevent_mode: False
pscg start multiprocess_mode: False
prepare_async_args: False
prepare job in same parent process arg set [0/1]: py_eval dump_db.process_cell(dbcon, '')
args_str: dump_db.process_cell(dbcon, '')
not legacy_mod_import_mode
check module already imported or not: dump_db
already_imported: False
try import module: dump_db
('### dumping to target_db_fp:', '/host_shared_dir/tmp_gen/tmp_dump_db_4cc941c9-b76c-4a99-ac59-c9d54c8f4c1f.db')
('### reading table to df:', 'logs')
creating a new spark session...
== session_url:  http://spark:8998/sessions/0
waiting for session to enter idle state...
waiting for session to enter idle state... done
=== running pyspark work...
output: {u'status': u'ok', u'execution_count': 0, u'data': {u'text/plain': u'sc: <SparkContext master=local appName=livy-session-0>'}}
=== running pyspark work... done in 3.093833 seconds
== pyspark_livy session created and initialized in 19.751751 seconds
done_create_spark_session_alone_decr_counter decr_ret: -1
to_replace_list: []
to_replace_list: []
pyspark ori sql: select * from logs
pyspark final sql: select * from logs
pp_table_in_table_list: False
start pyspark read mode...
=== running pyspark work...
raise_if_no_pq_files: True
cache_key: (<pyspark_livy_engine.pyspark_session instance at 0x7f8ff74dcea8>, 'logs', True)
gen_pyspark_temp_view_code_for_table start table: logs
need to try download n files: 2
dl done ret_list: [0, 0]
output: {u'status': u'ok', u'execution_count': 1, u'data': {u'text/plain': u''}}
=== running pyspark work... done in 4.425675 seconds
dpl dur spark: 24.286052
dump_db table: logs df len: 2
('### dumping table df to db:', 'logs')
('### reading table to df:', 'events')
df[is_pause_filtered]: 0    1
1    1
Name: is_pause_filtered, dtype: int64
note: get_where_for_pause_recording omit because pg_engine.is_pause_filterd() flagged
g_flag_no_pause: True
to_replace_list: []
to_replace_list: []
pyspark ori sql: select * from events
pyspark final sql: select * from events
pp_table_in_table_list: False
start pyspark read mode...
=== running pyspark work...
raise_if_no_pq_files: True
cache_key: (<pyspark_livy_engine.pyspark_session instance at 0x7f8ff74dcea8>, 'events', True)
gen_pyspark_temp_view_code_for_table start table: events
need to try download n files: 2
dl done ret_list: [0, 0]
output: {u'status': u'ok', u'execution_count': 2, u'data': {u'text/plain': u''}}
=== running pyspark work... done in 1.300112 seconds
dpl dur spark: 1.387027
dump_db table: events df len: 38132
('### dumping table df to db:', 'events')
('### reading table to df:', 'signalling')
to_replace_list: []
to_replace_list: []
pyspark ori sql: select * from signalling
pyspark final sql: select * from signalling
pp_table_in_table_list: False
start pyspark read mode...
=== running pyspark work...
raise_if_no_pq_files: True
cache_key: (<pyspark_livy_engine.pyspark_session instance at 0x7f8ff74dcea8>, 'signalling', True)
gen_pyspark_temp_view_code_for_table start table: signalling
need to try download n files: 2
dl done ret_list: [0, 0]
output: {u'status': u'ok', u'execution_count': 3, u'data': {u'text/plain': u''}}
=== running pyspark work... done in 0.632147 seconds
dpl dur spark: 0.70605
dump_db table: signalling df len: 2252
('### dumping table df to db:', 'signalling')
('### reading table to df:', 'lte_cell_meas')
to_replace_list: []
to_replace_list: []
pyspark ori sql: select * from lte_cell_meas
pyspark final sql: select * from lte_cell_meas
pp_table_in_table_list: False
start pyspark read mode...
=== running pyspark work...
raise_if_no_pq_files: True
cache_key: (<pyspark_livy_engine.pyspark_session instance at 0x7f8ff74dcea8>, 'lte_cell_meas', True)
gen_pyspark_temp_view_code_for_table start table: lte_cell_meas
need to try download n files: 2
dl done ret_list: [0, 0]
output: {u'status': u'ok', u'execution_count': 4, u'data': {u'text/plain': u''}}
=== running pyspark work... done in 2.049411 seconds
dpl dur spark: 2.16856
dump_db table: lte_cell_meas df len: 18746
('### dumping table df to db:', 'lte_cell_meas')
('### reading table to df:', 'wcdma_cell_meas')
to_replace_list: []
to_replace_list: []
pyspark ori sql: select * from wcdma_cell_meas
pyspark final sql: select * from wcdma_cell_meas
pp_table_in_table_list: False
start pyspark read mode...
=== running pyspark work...
raise_if_no_pq_files: True
cache_key: (<pyspark_livy_engine.pyspark_session instance at 0x7f8ff74dcea8>, 'wcdma_cell_meas', True)
gen_pyspark_temp_view_code_for_table start table: wcdma_cell_meas
need to try download n files: 2
dl done ret_list: [8, 8]
dump_db table: wcdma_cell_meas df len: 0
('### dumping table df to db:', 'wcdma_cell_meas')
('### reading table to df:', 'gsm_cell_meas')
to_replace_list: []
to_replace_list: []
pyspark ori sql: select * from gsm_cell_meas
pyspark final sql: select * from gsm_cell_meas
pp_table_in_table_list: False
start pyspark read mode...
=== running pyspark work...
raise_if_no_pq_files: True
cache_key: (<pyspark_livy_engine.pyspark_session instance at 0x7f8ff74dcea8>, 'gsm_cell_meas', True)
gen_pyspark_temp_view_code_for_table start table: gsm_cell_meas
need to try download n files: 2
dl done ret_list: [8, 8]
dump_db table: gsm_cell_meas df len: 0
('### dumping table df to db:', 'gsm_cell_meas')
('### zipping dumped db to target_db_fp_zip:', '/host_shared_dir/tmp_gen/tmp_dump_db_4cc941c9-b76c-4a99-ac59-c9d54c8f4c1f.db.zip')
=== module arg run completed in seconds: 33.541819
moutput_pil_conv_to_openpyxl_jpg_image not none so set it
timer: process to now: 33.929665 seconds
module:  py_eval  process_cell func ret type:  <type 'dict'>
=== gen module  py_eval  DONE total duration: 33.929614 seconds
=== all processing modules DONE...
timer: main to now: 34.03929 seconds
timer: process to now: 33.929723 seconds
process_sha_cols_generic process duration all sum(): 33.541819
process_sha_cols_generic process duration summary head():

rank: 0 duration: 33.541819 secs - mod-params: py_eval << dump_db.process_cell(dbcon, '')
===== sql_to_duration_stats df.head(30):
                            code   duration
0  select * from logs             24.287157
3  select * from lte_cell_meas    2.170577 
1  select * from events           1.389763 
2  select * from signalling       0.707202 
4  select * from wcdma_cell_meas  0.161249 
5  select * from gsm_cell_meas    0.078157 
azq_output stage START - duration from main start:
timer: main to now: 34.048218 seconds

GET_PYPROCESS_OUTPUT result:
{'py_eval': {'6588e8d5b1eb452f061271099275b65a30a92aa5': '/host_shared_dir/tmp_gen/tmp_dump_db_4cc941c9-b76c-4a99-ac59-c9d54c8f4c1f.db.zip'}}
azq_output stage DONE - duration from main start:
timer: main to now: 34.048246 seconds
timer: output to now: 7.8e-05 seconds
successfully closed dbcon
pg_engine dispose() successful
successfully closed all pg dbcons
SUCCESS == please visit us again soon"""
    
    server = "https://localhost/"
    url = azq_server_api.parse_api_dump_db_stdout_get_zip_url(server, proc_stdout_str)
    print("url:", url)
    assert url == "https://localhost//tmp_gen/tmp_dump_db_4cc941c9-b76c-4a99-ac59-c9d54c8f4c1f.db.zip"
    
    
if __name__ == "__main__":
    test()


