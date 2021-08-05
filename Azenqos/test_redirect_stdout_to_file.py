import azq_utils
import os


def test():
    fp = azq_utils.get_last_run_log_fp()
    if os.path.isfile(fp):
        os.remove(fp)
    assert not os.path.isfile(fp)
    assert azq_utils.g_tee_stdout_obj is None
    azq_utils.open_and_redirect_stdout_to_last_run_log()
    print("hello")
    assert azq_utils.g_tee_stdout_obj is not None
    assert azq_utils.g_tee_stdout_obj.file is not None
    assert os.path.isfile(fp)
    azq_utils.close_last_run_log()
    assert azq_utils.g_tee_stdout_obj is not None
    assert azq_utils.g_tee_stdout_obj.file is None
    assert os.path.isfile(fp)
    print("last_run_log fp:", fp)
    with open(fp, 'r') as f:
        contents = f.read()        
        print("last_run_log contents:\n", contents)
        assert "new stdout log start version" in contents
        assert "hello" in contents
    

if __name__ == "__main__":
    test()
