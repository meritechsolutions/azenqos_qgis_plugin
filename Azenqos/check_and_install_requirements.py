import subprocess
import os

def get_module_path():
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_local_fp(fn):
    return os.path.join(get_module_path(), fn)

def check_and_install_requirements():
    needs_install = False

    # pkg_list = [x.strip() for x in pkg_list]
    requirement_fp = get_local_fp('requirements.txt')
    requirement_list = None
    with open(requirement_fp,"r") as f:
        requirement_list = f.read().splitlines()
    for requirement in requirement_list:
        requirement = requirement.lower().strip()
        sub_index = requirement.index('==')
        lib_name = requirement[0:sub_index]
        version = requirement[sub_index+2:]
        try:
            exec("import {}".format(lib_name))
            existing_version = eval("{}.__version__".format(lib_name))
            if version != existing_version:
                raise Exception
        except:
            needs_install = True
            print("not found:", requirement)
            break

    if needs_install:
        print("need_to_restart")
        cmd = ['python', '-m', 'pip', 'install', '-r', requirement_fp]
        print("cmd:", cmd)
        process = subprocess.Popen(['python', '-m', 'pip', 'install', '-r', requirement_fp], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=0)
        (stdout, stderr) = process.communicate()

        if process.returncode != 0:
            raise Exception(stderr.decode("utf-8") )

        return False
    return True