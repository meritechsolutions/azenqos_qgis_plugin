from PyQt5.QtWidgets import QApplication
from datatable import DetailWidget
import analyzer_vars


def test():
    app = QApplication([])
    print("app: ", app)  # use it so pyflakes wont complain - we need a ref to qapplicaiton otherwise we'll get segfault
    gc = analyzer_vars.analyzer_vars()
    detail = ""
    for i in range(10000):
        detail += "What is REAL{}\n".format(i)
    dw = DetailWidget(gc, None, detail)
    dw.show()
    result = app.exec()
    print("result: {}".format(result))


if __name__ == "__main__":
    test()
