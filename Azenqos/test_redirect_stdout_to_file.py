import azq_utils
import os


def test():
    fp = azq_utils.get_last_run_log_fp()
    if os.path.isfile(fp):
        os.remove(fp)
    assert not os.path.isfile(fp)
    azq_utils.open_and_redirect_stdout_to_last_run_log()
    assert os.path.isfile(fp)
    azq_utils.close_last_run_log()
    assert os.path.isfile(fp)
    print("last_run_log fp:", fp)
    with open(fp, 'r') as f:
        contents = f.read()        
        print("last_run_log contents:\n", contents)
        assert "new stdout log start version" in contents
    

if __name__ == "__main__":
    test()
