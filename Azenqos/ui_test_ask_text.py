import qt_utils
from PyQt5.QtWidgets import *


def test():
    app = QApplication([])
    reply = qt_utils.ask_text(None, "New layer", "Please specify layer name:")
    print("reply: {}".format(reply))
    

if __name__ == "__main__":
    test()
