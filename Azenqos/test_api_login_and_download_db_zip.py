import login_dialog
import sys
import traceback
import time


def test(server, user, passwd, lhl):
    print("server", server)
    print("user", user)
    print("passwd", passwd)
    token = login_dialog.login(
        {
            "server_url": server,
            "login": user,
            "pass": passwd,
        }
    )
    print("got token:", token)
    assert token

    proc_uuid = login_dialog.api_dump_db_get_proc_uuid(server, token, lhl)
    resp_dict = login_dialog.api_wait_until_process_completed(server, token, proc_uuid)
    print("process completed with code:", resp_dict["returncode"])
    print("process completed resp_dict:", resp_dict)
    proc_stdout_str = login_dialog.api_resp_get_stdout(server, token, resp_dict)
    print("proc_stdout_str: %s" % proc_stdout_str)
    
    delte_resp_dict = login_dialog.api_delete_process(server, token, proc_uuid)
    print("delete_resp_dict:", delte_resp_dict)
    assert delte_resp_dict["ret"] == 0

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
