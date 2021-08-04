import azq_utils


def test():
    mp = azq_utils.get_module_path()
    print("mp:", mp)
    mpp = azq_utils.get_module_parent_path()
    print("mpp:", mpp)
    assert mp.startswith(mpp)
    

if __name__ == "__main__":
    test()
