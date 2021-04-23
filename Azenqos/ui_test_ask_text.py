import qt_utils
from PyQt5.QtWidgets import QApplication


def test():
    app = QApplication([])  # app var required otherwise would segfualt - likely because no ref to qapplication remaining at runtime
    print("app:", app)
    reply = qt_utils.ask_text(None, "New layer", "Please specify layer name:")
    print("reply: {}".format(reply))


if __name__ == "__main__":
    test()
