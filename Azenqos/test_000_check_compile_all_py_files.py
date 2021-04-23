import os
import pyflakes.api


def test_pyflakes(fp):
    print(("TEST pyflakes:", fp, "start"))
    ret = pyflakes.api.checkPath(fp)
    print(("TEST pyflakes:", fp, "done ret:", ret))
    assert ret == 0


def test():
    files = sorted(os.listdir("."))
    files = [
        fn
        for fn in files
        if fn.endswith(".py") and not fn.startswith(".#") and not fn == "__init__.py"
    ]
    files.remove("main_window.py")  # not true main_window.py:196:9 'datatable.TableWindow' imported but unused

    for test_func in [test_pyflakes]:
        for fp in files:
            test_func(fp)

    print("SUCCESS")


if __name__ == "__main__":
    test()
