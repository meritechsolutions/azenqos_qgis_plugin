from PyQt5.QtWidgets import *
import main_window
import analyzer_vars
import login_dialog


def test():
    gc = analyzer_vars.analyzer_vars()
    app = QApplication([])
    dlg = login_dialog.login_dialog(None, gc)
    dlg.show()    
    ret = dlg.exec()
    ret_dict = dlg.ret_dict
    print("ret:", ret)
    print("ret_dict: {}".format(ret_dict))

    

if __name__ == "__main__":
    test()
