from PyQt5.QtWidgets import QApplication
import analyzer_vars
import login_dialog
import azq_server_api
import datatable
import sys


def test(server, user, passwd, lhl):
    app = QApplication([])

    token = azq_server_api.api_login_get_token(server, user, passwd)
    assert token
    gc = analyzer_vars.analyzer_vars()
    gc.login_dialog = login_dialog.login_dialog(None, gc, download_db_zip=False)
    gc.login_dialog.token = token
    gc.login_dialog.server = server
    gc.login_dialog.lhl = lhl

    azq_report_gen_expression = "list_modules_with_process_cell_func.run()"
    window = datatable.create_table_window_from_api_expression_ret(
        None,
        "title",
        gc,
        server,
        token,
        lhl,
        azq_report_gen_expression,
        list_module=True,
    )
    window.show()
    app.exec_()


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("argc too short so using defaults")
        # 474974357483649200 is log_hash for ../example_logs/nr_exynos_drive1/354569110588585-18_08_2020-13_54_22.azm
        # 345757788188057704 is log_hash for ../example_logs/lte_benchmark/357008080503008-26_08_2020-16_18_08.azm
        # test(server="https://test0.azenqos.com", user="trial_admin", passwd="3.14isnotpina", lhl="474974357483649200,345757788188057704" )
        test(
            server="https://test0.azenqos.com",
            user="azq",
            passwd="azenqostest0798",
            lhl="1419904400023234500",
        )
    else:
        test(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
