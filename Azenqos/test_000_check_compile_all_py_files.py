import os
import shutil
import subprocess
import pandas as pd
import multiprocessing as mp
import sys
import traceback
import time

test_compile = False


def test_compile(f):    
    print(("TEST compile:", f))
    cmd = '''python3 -c "import ast; ast.parse(open('%s').read())"''' % f
    ret = os.system(cmd)
    assert ret == 0
    ret_q.put(0)
    

def test_pyflakes(f):    
    print(("TEST pyflakes:", f, 'start'))
    cmd = '''python3 -m pyflakes '%s' ''' % (f)
    print("cmd:", cmd)
    outstr = None
    ex = None
    try:
        outstr = subprocess.check_output(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        # pyflakes failed but check if we want to ignore its cases
        outstr = e.output.decode()
        outstr = outstr.strip()
        error_lines = outstr.split("\n")
        #print "error_lines:", error_lines
        allowed_endswith_cases = [
            "is assigned to but never used",
            "imported but unused",
        ]
        allowed_contains_cases = [
            "redefinition of unused",
        ]
        error_lines_wo_waived = list(error_lines)                    
        for error_line in list(error_lines_wo_waived):
            #print "check error_line:", error_line
            for allowed_endswith_case in allowed_endswith_cases:
                if error_line.endswith(allowed_endswith_case):
                    #print "ignoring error_line:", error_line
                    error_lines_wo_waived.remove(error_line)
                else:
                    pass
                    #print "keeping error_line:", error_line
            for allowed_contains_case in allowed_contains_cases:
                if allowed_contains_case in error_line:
                    #print "ignoring error_line:", error_line
                    error_lines_wo_waived.remove(error_line)
                else:
                    pass
                    #print "keeping error_line:", error_line

        #print "error_lines len:", len(error_lines)                    
        #print "error_lines_wo_waived len:", len(error_lines_wo_waived)                    
        if len(error_lines_wo_waived) > 0:
            raise Exception("pyflakes error_lines_wo_waived: {}".format(error_lines_wo_waived))
    print(("TEST pyflakes:", f, 'pyflakes success'))            


def test():

    assert 0 == os.system("python3 -m pyflakes version.py")
    files = os.listdir('.')    
    p_list = []
    files = [f for f in files if f.endswith('.py') and not f.startswith(".#")]

    for test_func in [test_pyflakes, test_compile]:
        for f in files:
            test_func(f)

    print("SUCCESS")
    
    
if __name__ == '__main__':
    test()
    try:
        sys.stdout.close()
    except:
        pass
    try:
        sys.stderr.close()
    except:
        pass
