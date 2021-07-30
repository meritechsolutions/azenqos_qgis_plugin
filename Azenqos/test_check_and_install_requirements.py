import check_and_install_requirements
import os

def test():
    if os.name != "nt":
        return  # fails on some as needs sudo in gnu/linux
    os.system("python -m pip uninstall -y pyqtgraph")
    # if not check_and_install_requirements.check_and_install_requirements():
    assert False == check_and_install_requirements.check_and_install_requirements()
    assert True == check_and_install_requirements.check_and_install_requirements()
    

if __name__ == "__main__":
    test()
