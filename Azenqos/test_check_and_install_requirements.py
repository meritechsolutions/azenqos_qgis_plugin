import check_and_install_requirements
import os

def test():
    os.system("python -m pip uninstall -y pyqtgraph")
    # if not check_and_install_requirements.check_and_install_requirements():
    assert False == check_and_install_requirements.check_and_install_requirements()
    assert True == check_and_install_requirements.check_and_install_requirements()
    

if __name__ == "__main__":
    test()
