import paramiko
from datetime import date
from Azenqos import version
import pack_plugin
import os

host = 'files.azenqos.com'
port = 22
username = 'admin'
remote_directory = '/home/admin/public/plugin'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.load_system_host_keys()

ssh.connect(host, port, username)

stdin, stdout, stderr = ssh.exec_command('ls ' + remote_directory)

file_list = stdout.readlines()

file_list.sort()
n = 4

while True:
    if len(file_list) > n:
        file = file_list.pop(0)
        ssh.exec_command('rm ' + remote_directory + "/" + file)
    else:
        break

today = date.today()
date_str = today.strftime("%Y-%m-%d")
version = "%.03f" % version.VERSION
file_name = "azenqos_qgis_plugin_{}.zip".format(version)
remote_path = remote_directory + "/" + file_name

print("Pack Plugin Start")
pack_plugin.pack(file_name)
print("Pack Plugin Done")
local_path = os.path.abspath(file_name)
print(local_path)
assert os.path.exists(local_path)

print("Upload Plugin Start")
while True:
    try:
        sftp = ssh.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        break
    except:
        pass
print("Upload Plugin Done")

os.remove(local_path)
assert not os.path.exists(local_path)

ssh.close()