from PyQt5.QtWidgets import QApplication

import analyzer_vars


def test():
    app = QApplication([])
    print("app: ", app)  # use it so pyflakes wont complain - we need a ref to qapplicaiton otherwise we'll get segfault

    from import_db_dialog import import_db_dialog

    gc = analyzer_vars.analyzer_vars()
    dlg = import_db_dialog(None, gc)
    dlg.show()
    result = dlg.exec()
    print("result: {}".format(result))


if __name__ == "__main__":
    test()
