import subprocess
import os
import sys
from functools import cmp_to_key

import qt_utils

def get_module_path():
    return os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def get_local_fp(fn):
    return os.path.join(get_module_path(), fn)

priority_whl_list = ["six", "pytz", "certifi", "urllib3", "chardet", "idna", "requests", "python_dateutil", "packaging", "numpy", "pandas", "scipy", "pyarrow", "psutil", "fsspec", "cramjam", "fastparquet", "pyqtgraph", "spatialite"]
def compare(item1, item2):
    item1_index = 999
    item2_index = 999
    index = 0
    for whl in priority_whl_list:
        if whl+"-" in item1:
            item1_index = index
        if whl+"-" in item2:
            item2_index = index
        index += 1    
    return item1_index - item2_index

def check_and_install_requirements():
    needs_install = False
    import version
    module_path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    current_plugin_version_path = os.path.join(module_path,"current_plugin_version")

    if os.name == "nt":
        try:
            with open(current_plugin_version_path, "r") as f:
                ret = f.readline()
                if str(version.VERSION) == ret.strip():
                    return True
        except:
            pass

    # pkg_list = [x.strip() for x in pkg_list]
    wheel_dp = get_local_fp('wheel')
    assert os.path.isdir(wheel_dp)
    cp_pattern = "cp{}{}".format(sys.version_info.major, sys.version_info.minor)
    compat_wheel_pattern = "*-*-{}*.whl".format(cp_pattern)
    any_wheel_pattern = "*-any.whl"
    
    import glob
    whl_list = glob.glob(os.path.join(wheel_dp, compat_wheel_pattern))
    whl_list.extend(glob.glob(os.path.join(wheel_dp, any_wheel_pattern)))
    whl_list = sorted(whl_list, key=cmp_to_key(compare)) #install numpy before scipy

    requirement_fp = get_local_fp('requirements.txt')
    requirement_list = None
    not_exist_whl_list = []
    if os.name == "nt":
        output = subprocess.check_output(["pip", "freeze"]).decode("utf-8")
        for whl in whl_list:
            whl_basename = os.path.basename(whl)
            if whl_basename not in output:
                not_exist_whl_list.append(whl)
        if len(not_exist_whl_list) > 0:
            needs_install = True
    else:
        with open(requirement_fp,"r") as f:
            requirement_list = f.read().splitlines()
        for requirement in requirement_list:
            requirement = requirement.lower().strip()
            sub_index = requirement.index('==')
            lib_name = requirement[0:sub_index]
            lib_version = requirement[sub_index+2:]
            try:
                exec("import {}".format(lib_name))
                existing_version = eval("{}.__version__".format(lib_name))
                if lib_version != existing_version:
                    raise Exception
            except:
                needs_install = True
                print("not found:", requirement)
                break

    if needs_install:
        print("need_to_restart")
        
        if os.name == "nt":
            for whl in not_exist_whl_list:
                try:
                    subprocess.check_call(['pip', 'uninstall', '-y', whl])
                except:
                    pass
                subprocess.call(['python', '-m', 'pip', 'install', '--no-dependencies', whl])
            with open(current_plugin_version_path, "w") as f:
                ret = f.write(str(version.VERSION))
        else:
            try:
                subprocess.check_output(['python', '-m', 'pip', 'install', '-r', requirement_fp], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                outstr = e.output
                qt_utils.msgbox("Azenqos plugin failed to install required dependencies, please email below error msg to support@azenqos.com:\n\n" + outstr.decode("utf-8"), title="AZENQOS Dependency Install Fail")
        
        
        return False 
    
    if os.name == "nt":
        with open(current_plugin_version_path, "w") as f:
            ret = f.write(str(version.VERSION))

    return True