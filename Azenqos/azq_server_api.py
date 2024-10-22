import json
import os
import sys
import time
import traceback
import uuid
from urllib.parse import urlparse

import pandas as pd
import requests

import azq_utils
from azq_utils import signal_emit


def api_login_get_token(server, user, passwd, https=True):
    host = urlparse(server).netloc
    print("api_login_get_token server: %s host: %s" % (server, host))
    scheme = "https"
    if server == "localhost":
        https = False
    if not https:
        scheme = "http"
    resp = requests.post(
        "{}://{}/uapi/login".format(scheme, host),
        data=json.dumps(
            {"Username": user, "Password": passwd}
        ),
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
        headers={"Authorization": "Bearer {}".format(token),},
        json={
            "process_type": "azq_report_gen",
            "pg_host": "azq_pg",
            "pg_port": "5432",
            "sqlite_db_file": "PG_AZM_DB_MERGE",
            "pg_log_hash_list": lhl,
            "GET_PYPROCESS_OUTPUT": "PY_EVAL {}".format(azq_report_gen_expression),
            "_post_back_tar_file_list": [],
        },
        verify=False,
    )
    # print("resp.status_code", resp.status_code)
    # print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code, resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict

def api_device_list_df(server, token):
    resp = call_api_get_resp(server, token, "uapi/list_devices", {}, method="get")
    #print("api_device_list_df resp:", resp)
    df = pd.DataFrame(resp)
    print("api_device_list_df df:", df)
    if len(df) == 0:
        raise Exception("No devices added for this account")
    df["imei_number"] = df["imei_number"].astype(str)
    return df

def api_overview_db_list_df(server, token):
    resp = call_api_get_resp(server, token, "uapi/overview_db", {}, method="get")
    return pd.DataFrame(resp)

def api_predict_models_list_df(server, token):
    resp = call_api_get_resp(server, token, "uapi/predict", {}, method="get")
    return pd.DataFrame(resp)

def api_predict_df(server, token, body_dict):
    resp = call_api_get_resp(server, token, "uapi/predict", body_dict)
    return pd.DataFrame(resp)

def api_overview_db_download(server, token, target_fp, req_body, signal_to_emit_stats=None):
    ret_fp = call_api_get_resp(server, token, "uapi/overview_db", req_body, resp_content_to_fp=target_fp, signal_to_emit_stats=signal_to_emit_stats)
    return ret_fp

def call_api_get_resp(server, token, path, body_dict, method='post', resp_content_to_fp=None, signal_to_emit_stats=None):
    host = urlparse(server).netloc
    url = "https://{}/{}".format(host, path)
    headers={"Authorization": "Bearer {}".format(token),}
    resp = None
    def update_stat(s):
        print("call_api_get_resp update_stat:", s)
        signal_to_emit_stats.emit(s) if signal_to_emit_stats is not None else None

    update_stat("Sending/waiting for server process...")
    ts = time.time()
    if method == "post":
        resp = requests.post(
            url,
            headers=headers,
            json=body_dict,
            verify=False,
            stream=resp_content_to_fp is not None
        )
    elif method == "get":
        assert not body_dict
        resp = requests.get(
            url,
            headers=headers,
            verify=False,
            stream=resp_content_to_fp is not None
        )
    else:
        raise Exception("unsupported method: {}".format(method))
    with resp:
        update_stat("Got response... server process duration: %.02f secs" %(time.time() - ts))
        print("resp.headers:", resp.headers)
        if resp.status_code != 200:
            raise Exception(
                "Got failed status_code: {} resp.text: {}".format(
                    resp.status_code, resp.text,
                )
            )
        if resp_content_to_fp:
            ts = time.time()
            resp.raise_for_status()
            with open(resp_content_to_fp, "wb") as f:
                total_len = 0
                last_update = 0.0
                last_report_bytes = 0
                for chunk in resp.iter_content(chunk_size=4*1024*1024):
                    if chunk is None or len(chunk) == 0:
                        break
                    total_len += len(chunk)
                    now = time.time()
                    dur = now - last_update
                    if dur >= 1.0:
                        bytes_rx_last_loop = total_len - last_report_bytes
                        bits_per_sec = (bytes_rx_last_loop*8)/dur
                        k_bits_per_sec = bits_per_sec / 1000.0
                        m_bits_per_sec = bits_per_sec / (1000.0*1000.0)
                        last_report_bytes = total_len
                        update_stat("Downloading: %.02f MB" % (float(total_len/(1000*1000))) + (" (speed %.02f Mbps)" % m_bits_per_sec if m_bits_per_sec > 1 else "(speed %.02f Kbps)" % k_bits_per_sec))
                        last_update = now
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)
            update_stat("Download completed in %.02f secs" % (time.time()-ts))

            assert os.path.isfile(resp_content_to_fp)
            return resp_content_to_fp
        else:
            resp_dict = resp.json()
            return resp_dict


def api_get_process(server, token, proc_uuid):
    host = urlparse(server).netloc
    resp = requests.get(
        "https://{}/api_livegen/livegen_process/{}".format(host, proc_uuid),
        headers={"Authorization": "Bearer {}".format(token),},
        verify=False,
    )
    # print("resp.status_code", resp.status_code)
    # print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code, resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_resp_get_stdout(server, token, resp_dict):
    host = urlparse(server).netloc
    resp = requests.get(
        "https://{}/{}".format(host, resp_dict["stdout_log_url"]),
        headers={"Authorization": "Bearer {}".format(token),},
        verify=False,
    )
    # print("resp.status_code", resp.status_code)
    # print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code, resp.text,
            )
        )
    return resp.text


def api_delete_process(server, token, proc_uuid):
    host = urlparse(server).netloc
    resp = requests.delete(
        "https://{}/api_livegen/livegen_process/{}".format(host, proc_uuid),
        headers={"Authorization": "Bearer {}".format(token),},
        verify=False,
    )
    # print("resp.status_code", resp.status_code)
    # print("resp.text:", resp.text)
    if resp.status_code != 200:
        raise Exception(
            "Got failed status_code: {} resp.text: {}".format(
                resp.status_code, resp.text,
            )
        )
    resp_dict = resp.json()
    return resp_dict


def api_dump_db_expression(
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
    return "dump_db.process_cell(dbcon, '', tables=[{}])".format(
        ",".join("'" + pd.Series(tables) + "'")
    )


def api_wait_until_process_completed(server, token, proc_uuid):
    resp_dict = None
    # loop check task status until success
    while True:
        time.sleep(1)
        resp_dict = api_get_process(server, token, proc_uuid)
        print('resp_dict["returncode"]:', resp_dict["returncode"])
        if resp_dict["returncode"] is not None:
            break
    return resp_dict


def parse_py_eval_ret_dict_from_stdout_log(proc_stdout_str):
    str_split_token = "---### GET_PYPROCESS_OUTPUT JSON ###---"
    if str_split_token not in proc_stdout_str:
        raise Exception(
            "failed to find str_split_token: {} in proc_stdout_str: {}".format(
                str_split_token, proc_stdout_str
            )
        )
    parts = proc_stdout_str.split(str_split_token)
    assert len(parts) >= 3
    json_resp = parts[1]
    ret_dict = json.loads(json_resp)
    return ret_dict


def api_relative_path_to_url(server, path):
    host = urlparse(server).netloc
    url = "https://{}{}".format(host, path)
    return url


def api_login_and_dl_db_zip(
    server,
    user,
    passwd,
    lhl,
    progress_update_signal=None,
    status_update_signal=None,
    done_signal=None,
    on_zip_downloaded_func=None,
    download_db_zip=True,
    overview_mode_params_dict = None, # dict
):

    try:
        # the emit() below would fail/raise if login_dialog/ui was closed as signal would be invalid and raise and trigger finally cleanup - so no need to check dialog closed flag etc

        # login
        signal_emit(progress_update_signal, 0)
        signal_emit(status_update_signal, "Connecting to server...")
        token = api_login_get_token(server, user, passwd)
        signal_emit(status_update_signal, "Login success...")
        signal_emit(progress_update_signal, 10)

        # prepare for download db zip from server
        azq_utils.cleanup_died_processes_tmp_folders()
        tmp_dir = azq_utils.tmp_gen_path()
        target_fp = os.path.join(tmp_dir, "server_db.zip")
        if os.path.isfile(target_fp):
            os.remove(target_fp)
        zip_url = None

        if overview_mode_params_dict:
            signal_emit(status_update_signal, "Downloading overview db zip from server...")
            target_fp = api_overview_db_download(server, token, target_fp, overview_mode_params_dict)
        else:
            py_eval_ret_dict = api_py_eval_get_parsed_ret_dict(
                server,
                token,
                lhl,
                "PY_EVAL sql_helpers.read_sql('select * from logs', dbcon)"
                if (not download_db_zip)
                else api_dump_db_expression(),
                progress_update_signal,
                status_update_signal,
            )
            print("login py_eval_ret_dict: {}".format(py_eval_ret_dict))
            assert py_eval_ret_dict is not None
            zip_url = api_relative_path_to_url(server, py_eval_ret_dict["ret_dump"])
            # check that server process succeeded
            signal_emit(status_update_signal, "Check server response for db zip...")
            print("zip_url:", zip_url)
            signal_emit(progress_update_signal, 60)
            signal_emit(status_update_signal, "Downloading db zip from server...")
            azq_utils.download_file(zip_url, target_fp, auth_token=token)

        if download_db_zip and zip_url:
            assert target_fp
            assert os.path.isfile(target_fp) == True
            signal_emit(progress_update_signal, 80)
            signal_emit(status_update_signal, "Download complete...")
            if on_zip_downloaded_func:
                signal_emit(status_update_signal, "Processing downloaded zip/data...")
                on_zip_downloaded_func(target_fp)

        signal_emit(
            done_signal, "SUCCESS,{}".format(token)
        )  # empty string means success
        return target_fp
    except Exception as ex:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: api_login_and_dl_db_zip exception: {}", exstr)
        try:
            signal_emit(done_signal, exstr)
        except:
            pass
        raise ex

    return None


def api_py_eval_get_parsed_ret_dict(
    server,
    token,
    lhl,
    azq_report_gen_expression,
    progress_update_signal=None,
    status_update_signal=None,
    done_signal=None,
    parse_stdout_log_for_py_eval_output_and_return=True,
):

    # for cleanup
    proc_uuid = None

    try:
        # the emit() below would fail/raise if login_dialog/ui was closed as signal would be invalid and raise and trigger finally cleanup - so no need to check dialog closed flag etc

        # create process on server
        print("azq_report_gen_expression:", azq_report_gen_expression)
        proc_uuid = api_create_process(server, token, lhl, azq_report_gen_expression)[
            "proc_uuid"
        ]
        print("servr proc_uuid:", proc_uuid)
        signal_emit(
            status_update_signal, "Requested server for specifed log_hash list data..."
        )
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
            signal_emit(
                status_update_signal,
                "Server dump/calculation process running - loop: {}".format(loop_count),
            )
        signal_emit(status_update_signal, "Server process completed...")
        print('server process complete - resp_dict:', resp_dict)
        signal_emit(progress_update_signal, 50)

        # cleanup server process immediately and set proc_uuid as None so no need re-cleanup in finally block
        signal_emit(status_update_signal, "Server process cleanup...")
        cret = api_delete_process(server, token, proc_uuid)
        proc_uuid = None  # as process was already cleanedup...
        signal_emit(progress_update_signal, 55)

        signal_emit(done_signal, "")  # empty string means success
        assert resp_dict

        if parse_stdout_log_for_py_eval_output_and_return:
            # get server process resp_dicts' stdout
            proc_stdout_str = api_resp_get_stdout(server, token, resp_dict)
            # parse for GET_PYPROCESS_OUTPUT json result
            py_eval_ret_dict = None
            try:
                py_eval_ret_dict = parse_py_eval_ret_dict_from_stdout_log(
                    proc_stdout_str
                )
            except Exception as pe:
                if (
                    resp_dict["stdout_log_tail"]
                    and "ERROR: likely invalid log_hash_list"
                    in resp_dict["stdout_log_tail"]
                ):
                    raise Exception(
                        "Server process failed: ERROR: likely invalid log_hash_list"
                    )
                raise pe
            return py_eval_ret_dict
        else:
            return resp_dict
    except Exception as ex:
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        print("WARNING: api_py_eval_and_wait_completion exception: {}", exstr)
        try:
            signal_emit(done_signal, exstr)
        except:
            pass
        raise ex
    finally:
        if proc_uuid:
            print(
                "api_py_eval_and_wait_completion: cleanup server proc_uuid as we had exception above - START"
            )
            try:
                cret = api_delete_process(server, token, proc_uuid)
                print(
                    "api_py_eval_and_wait_completion: cleanup server proc_uuid as we had exception above - DONE ret: {}".format(
                        cret
                    )
                )
            except:
                type_, value_, traceback_ = sys.exc_info()
                exstr = str(traceback.format_exception(type_, value_, traceback_))
                print(
                    "WARNING: api_py_eval_and_wait_completion api_delte_process failed exception: {}",
                    exstr,
                )

    return None


def parse_py_eval_ret_dict_for_df(server, token, py_eval_ret_dict: dict):
    if (
        py_eval_ret_dict["ret_dump"] is not None
        and py_eval_ret_dict["ret_type"] is not None
        and ("pandas.core.frame.DataFrame" in py_eval_ret_dict["ret_type"] 
        or "azq_output.OpenpyxlJpgImage" in py_eval_ret_dict["ret_type"] )
    ):
        pq_url = api_relative_path_to_url(server, py_eval_ret_dict["ret_dump"])
        tmp_dir = azq_utils.tmp_gen_path()
        target_fp = os.path.join(
            tmp_dir, "tmp_server_py_eval_df_{}.parquet".format(uuid.uuid4())
        )
        if "png" in py_eval_ret_dict["ret_dump"]:
            print("ret_dump is image")
            target_fp = os.path.join(
                tmp_dir, "tmp_server_py_eval_df_{}.png".format(uuid.uuid4())
            )
        azq_utils.download_file(pq_url, target_fp, auth_token=token)
        assert os.path.isfile(target_fp) == True
        return target_fp
        # df = pd.read_parquet(target_fp)
        # #df.columns = [x.decode("utf-8") for x in df.columns]
        # for col in df.columns:
        #     try:
        #         df[col] = df[col].apply(lambda x: x.decode("utf-8"))
        #     except:
        #         pass
        # return df
    else:
        return None
