import os

import black
import pyflakes.api


def test_formatting(fp):
    mode = black.FileMode()
    fast = False
    file_contents = None
    with open(fp, "r") as f:
        file_contents = f.read()
    needs_change = False
    try:
        black.format_file_contents(file_contents, fast=fast, mode=mode)
        needs_change = True
    except black.NothingChanged:
        needs_change = False
    if needs_change:
        raise Exception("test_formatting FAILED: try run command: black .")


def test_pyflakes(fp):
    print(("TEST pyflakes:", fp, "start"))
    ret = pyflakes.api.checkPath(fp)
    print(("TEST pyflakes:", fp, "done ret:", ret))
    assert ret == 0


def test():
    files = sorted(os.listdir("."))    
    files = [fn for fn in files if fn.endswith(".py") and not fn.startswith(".#")]

    for test_func in [test_pyflakes, test_formatting]:
        for fp in files:
            test_func(fp)

    print("SUCCESS")


if __name__ == "__main__":
    test()
