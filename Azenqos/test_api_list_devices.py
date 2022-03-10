from PyQt5.QtWidgets import QApplication

import azq_server_api
import integration_test_helpers


def test():
    app = QApplication([])
    print("app: ", app)  # use it so pyflakes wont complain - we need a ref to qapplicaiton otherwise we'll get segfault
    gv = integration_test_helpers.get_global_vars(login=True)
    df = azq_server_api.api_device_list_df(gv.login_dialog.server, gv.login_dialog.token)
    print("devices:", df)


if __name__ == "__main__":
    test()
