import azq_utils
import os
import uuid


def test():

    invalid_pid = -1
    invalid_pid_tmp_dp = os.path.join(
        azq_utils.tmp_gen_path_parent(), str(invalid_pid), "instance_{}".format(uuid.uuid4())
    )  # pid 0 is invalid so never exists...
    os.makedirs(invalid_pid_tmp_dp, exist_ok=True)
    assert os.path.isdir(invalid_pid_tmp_dp)
    azq_utils.cleanup_died_processes_tmp_folders()
    assert not os.path.isdir(invalid_pid_tmp_dp)


if __name__ == "__main__":
    test()
