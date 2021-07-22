import subprocess
import os

def get_module_path():
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_local_fp(fn):
    return os.path.join(get_module_path(), fn)

def check_and_install_requirements():
    needs_install = False
    pkg_list = subprocess.check_output(['python', '-m', 'pip', 'freeze']).decode().split('\n')
    requirement_fp = get_local_fp('requirements.txt')
    requirement_list = None
    with open(requirement_fp,"r") as f:
        requirement_list = f.readlines()
    pkg_list = [x.strip() for x in pkg_list]
    for requirement in requirement_list:
        requirement = requirement.lower().strip()
        if requirement not in pkg_list:
            needs_install = True
            print("not found:", requirement)
            break
    if needs_install:
        print("need_to_restart")
        cmd = ['python', '-m', 'pip', 'install', '-r', requirement_fp]
        print("cmd:", cmd)
        subprocess.check_call(['python', '-m', 'pip', 'install', '-r', requirement_fp])
        return False
    return True