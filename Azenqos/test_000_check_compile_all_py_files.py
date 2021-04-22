import os
import shutil
import subprocess
import pandas as pd
import multiprocessing as mp
import psutil
import sys
import traceback
import time

ret_q = mp.Queue()
err_q = mp.Queue()
test_compile = False


def test_compile(f):    
    print(("TEST compile:", f))
    cmd = '''python3 -c "import ast; ast.parse(open('%s').read())"''' % f
    ret = os.system(cmd)
    assert ret == 0
    ret_q.put(0)
    

def test_pyflakes(f):    
    print(("TEST pyflakes:", f, 'start'))
    try:
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
        ret_q.put(0)
        print(("TEST pyflakes:", f, 'pyflakes success'))            
    except Exception as ex:
        type_, value_, traceback_ = sys.exc_info()
        #exstr = str(traceback.format_exception(type_, value_, traceback_))
        msg = "ERROR: test_pyflakes failed for file: {} with exception: {}".format(f, ex)
        print(msg)
        err_q.put(msg)
    print(("TEST pyflakes:", f, 'pyflakes completed'))


def test():

    assert 0 == os.system("python3 -m pyflakes version.py")
    files = os.listdir('.')    
    p_list = []
    files = [f for f in files if f.endswith('.py') and not f.startswith(".#")]

    for test_func in [test_pyflakes, test_compile]:        
        pool = mp.Pool(psutil.cpu_count())
        results = pool.map(test_func, files)
        pool.close()

        n_err = err_q.qsize()
        for i in range(err_q.qsize()):
            print((err_q.get()))
            exit(1)  # print only first one and exit so can fix one by one
        assert n_err == 0

        all_completed = ret_q.qsize() == len(files)
        print("ret_q.qsize():", ret_q.qsize())
        print("len(files):", len(files))
        print("all_completed:", all_completed)
        assert all_completed
        
        result_list = []
        for i in range(ret_q.qsize()):
            result_list.append(ret_q.get())
        all_passed = (pd.Series(result_list) == 0).all()
        print("all_passed:", all_passed)
        assert all_passed


    # detect 'not like' - must not use as pd direct query would fail
    cmd = '''find . -not -path './{}' -name "*.py" -type f -exec grep -nH -e "not like" {{}} + '''.format(__file__)
    if 0 == os.system(cmd):
        raise Exception("Please change all 'not like' into 'not <var> like' in your SQLs - as the former is not compatible with our sql to pandas query engine... example: change:\ndetail_str not like '%%haha%%'\nto:\nnot detail_str like '%%haha%%'")

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
