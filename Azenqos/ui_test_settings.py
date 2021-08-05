from PyQt5.QtWidgets import QApplication
import analyzer_vars
import settings_dialog


def test():
    gc = analyzer_vars.analyzer_vars()
    app = QApplication([])
    print("app: {}".format(app))
    dlg = settings_dialog.settings_dialog(None, gc)
    dlg.show()
    ret = dlg.exec()
    print("ret:", ret)


if __name__ == "__main__":
    test()
