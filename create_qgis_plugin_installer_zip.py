import subprocess
from Azenqos import version
from datetime import date
import os

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if f.startswith("azenqos_qgis_plugin") and f.endswith(".zip"):
        os.remove(f)
today = date.today()
date_str = today.strftime("%Y-%m-%d")
branch = subprocess.check_output("git branch --show-current", shell=True).decode('utf8').splitlines()[0]
commit = subprocess.check_output("git rev-parse --short HEAD", shell=True).decode('utf8').splitlines()[0]
target_fp = "azenqos_qgis_plugin_{}_{}_{}_{}.zip".format(date_str, branch, version.VERSION, commit)
subprocess.check_output("git archive -o {} HEAD:Azenqos".format(target_fp), shell=True)
print("SUCCESS zip gen done at:\n{}".format(target_fp))
