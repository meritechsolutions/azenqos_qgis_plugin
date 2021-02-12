from PyQt5.QtWidgets import *
import import_db_dialog
import analyzer_vars


def test():
    app = QApplication([])
    
    from import_db_dialog import import_db_dialog
    gc = analyzer_vars.analyzer_vars()
    dlg = import_db_dialog(gc)    
    dlg.show()
    
    result = dlg.exec_()
    print("result: {}".format(result))


if __name__ == "__main__":
    test()
