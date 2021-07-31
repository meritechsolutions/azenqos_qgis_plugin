import subprocess
from Azenqos import version
from datetime import date
import os

print("### run tests")
assert 0 == os.system("cd Azenqos && make clean && ./test.sh")

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
target_fp = "azenqos_qgis_plugin_{}_{}_{}_{}.zip".format(date_str, branch, version.VERSION, commit)
subprocess.check_output("git archive -o {} HEAD:Azenqos".format(target_fp), shell=True)
print("zip gen done at:\n{}".format(target_fp))

print("### push release to github")
cmd = "gh release create v{} {}".format(version.VERSION, target_fp)
print("push to github cmd:")
print(cmd)
ret = os.system(cmd)
assert ret == 0

print("SUCCESS")
