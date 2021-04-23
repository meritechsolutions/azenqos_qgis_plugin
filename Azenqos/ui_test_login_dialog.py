from PyQt5.QtWidgets import QApplication

import analyzer_vars
import login_dialog


def test():
    gc = analyzer_vars.analyzer_vars()
    QApplication([])
    dlg = login_dialog.login_dialog(None, gc)
    dlg.show()
    ret = dlg.exec()
    print("ret:", ret)


if __name__ == "__main__":
    test()
