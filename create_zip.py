import subprocess
from Azenqos import version
import os

files = [f for f in os.listdir('.') if os.path.isfile(f)]
for f in files:
    if f.startswith("azenqos_qgis_plugin_release") and f.endswith(".zip"):
        os.remove(f)
branch = subprocess.check_output("git branch --show-current", shell=True).decode('utf8').splitlines()[0]
commit = subprocess.check_output("git rev-parse --short HEAD", shell=True).decode('utf8').splitlines()[0]
subprocess.check_output("git archive -o azenqos_qgis_plugin_release_branch_{}_version_{}_commit_{}.zip HEAD:Azenqos".format(branch, version.VERSION, commit), shell=True)



