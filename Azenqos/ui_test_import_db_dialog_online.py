from PyQt5.QtWidgets import *
import import_db_dialog


def test():
    app = QApplication([])
    
    from import_db_dialog import import_db_dialog
    dlg = import_db_dialog(online_mode=True)    
    dlg.show()
    
    result = dlg.exec_()
    print("result: {}".format(result))


if __name__ == "__main__":
    test()
