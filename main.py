#paramiko must be installed beforehand
import paramiko
from scp import SCPClient
import json
from pprint import pprint
import sys

if len(sys.argv) < 6 :
	print "username password hostname port key_path"
	sys.exit()

uname = sys.argv[1]
pswrd = sys.argv[2]
hst = sys.argv[3]
prt = int(sys.argv[4])
key_path = sys.argv[5]


k = paramiko.dsskey.DSSKey(filename=key_path,password=pswrd)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#ssh.load_system_host_keys()
ssh.connect(hostname = hst, username = uname,  pkey = k, port=prt)

# SCPCLient takes a paramiko transport as its only argument
scp = SCPClient(ssh.get_transport())

#scp.put('main.py', 'public_html/main.py')
scp.get('public_html/posts.json','./')

with open('posts.json') as data_file:
    data = json.load(data_file)

data.append('post'+str(len(data)+1)+'.htm')



scp.close()
