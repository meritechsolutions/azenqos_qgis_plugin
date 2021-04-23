import azq_utils
import os

def test():

    invalid_pid_tmp_dp = os.path.join(
        azq_utils.tmp_gen_path_parent(), "0"
    )  # pid 0 is invalid so never exists...
    os.makedirs(invalid_pid_tmp_dp, exist_ok=True)
    assert os.path.isdir(invalid_pid_tmp_dp)
    azq_utils.cleanup_died_processes_tmp_folders()
    if os.name == "posix":
        assert not os.path.isdir(invalid_pid_tmp_dp)


if __name__ == "__main__":
    test()
