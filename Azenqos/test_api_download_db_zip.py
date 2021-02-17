import login_dialog
import sys
import traceback
import time
import azq_utils
import os
import azq_server_api


def test(server, user, passwd, lhl):
    print("server", server)
    print("user", user)
    print("passwd", passwd)
    ret = azq_server_api.api_login_and_dl_db_zip(server, user, passwd, lhl)
    print("ret:", ret)
    assert ret == True


def test_alt_working(server, user, passwd, lhl):
    print("server", server)
    print("user", user)
    print("passwd", passwd)

    # login
    token = login_dialog.login(
        {
            "server_url": server,
            "login": user,
            "pass": passwd,
        }
    )
    print("got token:", token)
    assert token

    # dump db process start
    proc_uuid = login_dialog.api_dump_db_get_proc_uuid(server, token, lhl)
    exit(0)

    # dump db process wait
    resp_dict = login_dialog.api_wait_until_process_completed(server, token, proc_uuid)    
    print("process completed with code:", resp_dict["returncode"])
    print("process completed resp_dict:", resp_dict)

    # get stdout of dump db process
    proc_stdout_str = login_dialog.api_resp_get_stdout(server, token, resp_dict)
    print("proc_stdout_str: %s" % proc_stdout_str)

    # delete dump db process
    delte_resp_dict = login_dialog.api_delete_process(server, token, proc_uuid)
    print("delete_resp_dict:", delte_resp_dict)
    assert delte_resp_dict["ret"] == 0

    

    azq_utils.cleanup_died_processes_tmp_folders()
    tmp_dir = azq_utils.get_current_tmp_gen_dp()
    os.makedirs(tmp_dir)

    target_fp = os.path.join(tmp_dir, "server_db.zip")
    assert os.path.isfile(target_fp) == False
    azq_utils.download_file(zip_url, target_fp)

    assert os.path.isfile(target_fp) == True
    
    # process is now deleted so get status of process must fail
    raised = False
    try:
        status_dict_after_delete = login_dialog.api_get_process(server, token, proc_uuid)
    except:
        raised = True
        type_, value_, traceback_ = sys.exc_info()
        exstr = str(traceback.format_exception(type_, value_, traceback_))
        #print("exstr:", exstr)
        assert "invalid proc_uuid" in exstr
    assert raised


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("argc too short so omit this test")
        exit(0)
    else:
        test(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
