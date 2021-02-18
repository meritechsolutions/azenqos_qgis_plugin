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
    assert os.path.isfile(ret)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("argc too short so using defaults")
        # 474974357483649200 is log_hash for ../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm
        # 345757788188057704 is log_hash for ../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm
        test(server="https://test0.azenqos.com", user="trial_admin", passwd="3.14isnotpina", lhl="474974357483649200,345757788188057704" )
    else:
        test(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
