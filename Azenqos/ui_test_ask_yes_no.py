import qt_utils
from PyQt5.QtWidgets import QApplication, QMessageBox


def test():
    app = QApplication([])  # app var required otherwise would segfualt - likely because no ref to qapplication remaining at runtime
    print("app:", app)
    reply = qt_utils.ask_yes_no(None, 'title', 'msg', question=True)
    print("reply: {}".format(reply))
    if reply == QMessageBox.Yes:
        print("got yes")
    if reply == QMessageBox.No:
        print("got no")
    if reply == QMessageBox.Cancel:
        print("got cancel")


if __name__ == "__main__":
    test()
