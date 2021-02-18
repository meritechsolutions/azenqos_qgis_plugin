import requests
import os
import sys
import traceback
from urllib.parse import urlparse
import time
import re
import pandas as pd

import azq_utils
from azq_utils import signal_emit


def api_login_get_token(server, user, passwd, passwd_sha=None):
    host = urlparse(server).netloc
    auth_token = azq_utils.calc_sha(user) + (azq_utils.calc_sha(passwd) if passwd_sha is None else passwd_sha)
    #print("send auth_token: %s" % auth_token)    
    resp = requests.get(
        "https://{}/api/login".format(host),
        headers={
            "Authorization": "Bearer {}".format(auth_token),
        },
        verify=False,
    )
    if resp.status_code == 200:
        if resp.text:
            return resp.text
        else:
            raise Exception("Got empty response")
    else:
        from http.client import responses
        raise Exception("Got response status: %s" % responses[resp.status_code])


def api_create_process(server, token, lhl, azq_report_gen_expression):
    host = urlparse(server).netloc
    resp = requests.post(
        "https://{}/api_livegen/livegen_process".format(host),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        json={
            "process_type": "azq_report_gen",
            "pg_host": "azq_pg",
            "pg_port": "5432",
            "sqlite_db_file": "PG_AZM_DB_MERGE",
            "pg_log_hash_list": lhl,
            "GET_PYPROCESS_OUTPUT": "PY_EVAL {}".format(azq_report_gen_expression),
            "_post_back_tar_file_list": []
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_get_process(server, token, proc_uuid):
    host = urlparse(server).netloc
    resp = requests.get(
        "https://{}/api_livegen/livegen_process/{}".format(host, proc_uuid),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_resp_get_stdout(server, token, resp_dict):
    host = urlparse(server).netloc
    resp = requests.get(
        "https://{}/{}".format(host, resp_dict["stdout_log_url"]),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    return resp.text


def api_delete_process(server, token, proc_uuid):
    host = urlparse(server).netloc
    resp = requests.delete(
        "https://{}/api_livegen/livegen_process/{}".format(host, proc_uuid),
        headers={
            "Authorization": "Bearer {}".format(token),
        },
        verify=False,
    )    
    #print("resp.status_code", resp.status_code)
    #print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code,
                resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_dump_db_get_proc_uuid(
        server,
        token,
        lhl,
        tables=[
            "logs",
            "location",
            "events",
            "signalling",

            "nr_cell_meas",
            
            "lte_cell_meas",
            "lte_frame_timing",
            "lte_cqi",
            "lte_pdsch_meas",
            "lte_l1_dl_tp",
            "lte_l1_ul_tp",
            "lte_pdcch_dec_result",
            "lte_mib_info",
            
            "wcdma_cell_meas",
            
            "gsm_cell_meas",
            
        ],
):
    proc_uuid = api_create_process(server, token, lhl, "dump_db.process_cell(dbcon, '', tables=[{}])".format(",".join("'"+pd.Series(tables)+"'")))["proc_uuid"]
    print("task_uuid:", proc_uuid)
    assert proc_uuid
    return proc_uuid


def api_wait_until_process_completed(server, token, proc_uuid):
    resp_dict = None    
    # loop check task status until success
    while True:
        time.sleep(3)
        resp_dict = api_get_process(server, token, proc_uuid)
        print('resp_dict["returncode"]:', resp_dict["returncode"])
        if resp_dict["returncode"] is not None:        
            break
    return resp_dict


def parse_api_dump_db_stdout_get_zip_url(server, proc_stdout_str):
    host = urlparse(server).netloc
    match_list = re.findall(r"GET_PYPROCESS_OUTPUT result:\n{'py_eval': {'\w+': '(.+)'", proc_stdout_str)
    if match_list:
        fp = match_list[0]
        url = "https://{}/{}".format(
            host,
            fp.replace("/host_shared_dir", "", 1)
        )
        return url
    return None


def api_login_and_dl_db_zip(server, user, passwd, lhl, progress_update_signal=None, status_update_signal=None, done_signal=None, on_zip_downloaded_func=None):

    # for cleanup
    proc_uuid = None
    
    try:
        # the emit() below would fail/raise if login_dialog/ui was closed as signal would be invalid and raise and trigger finally cleanup - so no need to check dialog closed flag etc
        
        # login
        signal_emit(progress_update_signal, 0)
        signal_emit(status_update_signal, "Connecting to server...")        
        token = api_login_get_token(server, user, passwd)        
        signal_emit(status_update_signal, "Login success...")
        signal_emit(progress_update_signal, 10)

        # create dump db process on server
        proc_uuid = api_dump_db_get_proc_uuid(server, token, lhl)
        signal_emit(status_update_signal, "Requested server for specifed log_hash list data...")
        signal_emit(progress_update_signal, 15)


        # loop check server process until success
        resp_dict = None
        loop_count = 0        
        while True:
            loop_count += 1
            time.sleep(1)
            resp_dict = api_get_process(server, token, proc_uuid)
            print('resp_dict["returncode"]:', resp_dict["returncode"])
            if resp_dict["returncode"] is not None:        
                break
            signal_emit(status_update_signal, "Server dumping data - loop_count: {}".format(loop_count))        
        signal_emit(status_update_signal, "Server dump data process completed...")
        print('server process complete - resp_dict:', resp_dict)
        signal_emit(progress_update_signal, 50)

        # cleanup server process immediately and set proc_uuid as None so no need re-cleanup in finally block
        signal_emit(status_update_signal, "Server process cleanup...")
        cret = api_delete_process(server, token, proc_uuid)
        proc_uuid = None # as process was already cleanedup...                
        signal_emit(progress_update_signal, 55)
        
        # check that server process succeeded
        signal_emit(status_update_signal, "Check server response for db zip...")
        if resp_dict["returncode"] != 0:
            raise Exception('Server process failed with code: {}, stdout_log_tail: {}'.format(resp_dict["returncode"], resp_dict["stdout_log_tail"]))
        # get server process resp_dicts' stdout
        proc_stdout_str = api_resp_get_stdout(server, token, resp_dict)        
        # parse for zip url
        zip_url = parse_api_dump_db_stdout_get_zip_url(server, proc_stdout_str)
        print("zip_url:", zip_url)
        signal_emit(progress_update_signal, 60)

        # download db zip from server
        azq_utils.cleanup_died_processes_tmp_folders()
        signal_emit(status_update_signal, "Downloading db zip from server...")
        tmp_dir = azq_utils.tmp_gen_path()
        target_fp = os.path.join(tmp_dir, "server_db.zip")
        assert os.path.isfile(target_fp) == False
        azq_utils.download_file(zip_url, target_fp)
        assert os.path.isfile(target_fp) == True
        signal_emit(progress_update_signal, 80)
        signal_emit(status_update_signal, "Download complete...")

        if on_zip_downloaded_func:
            signal_emit(status_update_signal, "Processing downloaded zip/data...")
            on_zip_downloaded_func(target_fp)
        
        signal_emit(done_signal, "")  # empty string means success
        return target_fp
    except:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: api_login_and_dl_db_zip exception: {}", exstr)
        try:
            signal_emit(done_signal, exstr)
        except:
            pass
    finally:
        if proc_uuid:
            print("api_login_and_dl_db_zip: cleanup server proc_uuid as we had exception above - START")
            try:
                cret = api_delete_process(server, token, proc_uuid)
                print("login_and_dl_db_zip: cleanup server proc_uuid as we had exception above - DONE ret: {}".format(cret))
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print("WARNING: api_login_and_dl_db_zip api_delte_process failed exception: {}", exstr)

    return None

