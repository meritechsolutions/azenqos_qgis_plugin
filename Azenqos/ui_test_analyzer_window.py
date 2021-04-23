from PyQt5.QtWidgets import QApplication
import analyzer_window


def test():
    app = QApplication([])
    mw = analyzer_window.analyzer_window()
    mw.show()
    app.exec()


if __name__ == "__main__":
    test()
