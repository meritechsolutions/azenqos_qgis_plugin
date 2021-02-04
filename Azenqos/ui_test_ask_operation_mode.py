import azenqos_plugin
from PyQt5.QtWidgets import *


def test():
    app = QApplication([])
    reply = azenqos_plugin.ask_operation_mode()
    print("reply: {}".format(reply))
    

if __name__ == "__main__":
    test()
