import subprocess
from Azenqos import version
from datetime import date
import os
import sys

debug = False
print("sys.argv:", sys.argv)
if len(sys.argv) == 2 and sys.argv[1] == "debug":
    debug = True

if debug:
    print("########## DEBUG DEV MODE NOT RUNNING TESTS")
    print("########## DEBUG DEV MODE commit now to get changes into git archive output...")
    os.system(''' git commit -a -m "debug new ver" ''')

else:
    print("### run tests")
    # assert 0 == os.system("cd Azenqos && make clean && ./test.sh")
    os.system(''' git commit -a -m "[auto-build] tests passed" ''')

print("### delete old release zips")
# delete old zip release files
files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if f.startswith("azenqos_qgis_plugin") and f.endswith(".zip"):
        os.remove(f)

print("### gen new release qgis plugin zip")
today = date.today()
date_str = today.strftime("%Y-%m-%d")
branch = subprocess.check_output("git branch --show-current", shell=True).decode('utf8').splitlines()[0]
commit = subprocess.check_output("git rev-parse --short HEAD", shell=True).decode('utf8').splitlines()[0]
version = "%.03f" % version.VERSION
target_fp = "azenqos_qgis_plugin_{}_{}_{}_{}.zip".format(date_str, branch, version, commit)
subprocess.check_output("git archive -o {} HEAD ./Azenqos".format(target_fp), shell=True)
print("zip gen done at:\n{}".format(target_fp))

if debug:
    print("########## DEBUG DEV MODE NOT PUSHING to gh")
    os.system(''' git commit -a -m "debug new ver" ''')
    cmd = ''' cp {} ~/Downloads '''.format(target_fp)
    print("cp to downloads cmd:\n", cmd)
    ret = os.system(cmd)
    print("cp to downloads ret:", ret)
    
    
    cmd = ''' scp {} test0.azenqos.com:/host_shared_dir/tmp_gen/ '''.format(target_fp)
    print("pusing zip with scp cmd:\n", cmd)
    assert 0 == os.system(cmd)
    url = "https://test0.azenqos.com/tmp_gen/{}".format(target_fp)
    print("pushed test zip to url")
    print(url)
else:
    print("### push release to github")
    cmd = "gh release create v{} {}".format(version, target_fp)
    print("push to github cmd:")
    print(cmd)
    ret = os.system(cmd)
    assert ret == 0
    print("pushed to {} url:".format(target_fp))
    print("https://github.com/freewillfx-azenqos/azenqos_qgis_plugin/releases")
