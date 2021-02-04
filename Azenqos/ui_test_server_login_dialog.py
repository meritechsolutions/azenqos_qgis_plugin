import azenqos_plugin
from PyQt5.QtWidgets import *
from server_login_dialog import server_login_dialog


def test():
    app = QApplication([])

    dlg = server_login_dialog()
    dlg.show()

    result = dlg.exec_()
    print("result: {}".format(result))



if __name__ == "__main__":
    test()
