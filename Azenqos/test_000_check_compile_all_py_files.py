import os
import pyflakes.api


def test_pyflakes(fp):    
    print(("TEST pyflakes:", fp, 'start'))
    ret = pyflakes.api.checkPath(fp)
    print(("TEST pyflakes:", fp, 'done ret:', ret))
    assert ret == 0


def test():
    files = os.listdir('.')    
    files = [fn for fn in files if fn.endswith('.py') and not fn.startswith(".#")]
    
    for test_func in [test_pyflakes]:
        for fp in files:
            test_func(fp)

    print("SUCCESS")
    
    
if __name__ == '__main__':
    test()
