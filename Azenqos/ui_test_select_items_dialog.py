import qt_utils
from PyQt5.QtWidgets import QApplication


def test():
    app = QApplication([])  # app var required otherwise would segfualt - likely because no ref to qapplication remaining at runtime
    print("app:", app)
    parent = None
    selection_mask = qt_utils.ask_selection(parent, ["u1", "u2"], [False, True], "Device selection", "Please select imeis:")
    print("selection_mask: {}".format(selection_mask))


if __name__ == "__main__":
    test()
