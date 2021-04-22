import os
import sys
import subprocess

def runcommand (cmd):
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True,
                            universal_newlines=True)
    std_out, std_err = proc.communicate()
    return proc.returncode, std_out, std_err

htmlString = "<html>"
htmlString += "<body>"

files = []
for file in os.listdir("./"):
    if file.startswith("test_") and file.endswith(".py"):
        (ret, out, err) = runcommand(sys.executable + " " + file)
        if ret == 0:
            htmlString += "&#9989; " + file
        else:
            htmlString += "&#9940; " + file
            htmlString += "<br /><span style='color:red'>============<pre><code>"
            htmlString += err
            htmlString += "============</code></pre></span>"
        htmlString += "<br />"

htmlString += "</body>"
htmlString += "</html>"

if not os.path.exists('build'):
    os.makedirs('build')

f = open("build/index.html", "w")
f.write(htmlString)
f.close()