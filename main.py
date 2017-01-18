#paramiko must be installed beforehand
import paramiko
from scp import SCPClient
import json
from pprint import pprint
import sys
import datetime
import calendar
import random

if len(sys.argv) < 2 :
	print "ssh credentials are needed"
	sys.exit()

with open(sys.argv[1]) as data_file:    
    credentials = json.load(data_file)    

uname = credentials['username']
pswrd = credentials['password']
hst = credentials['hostname']
prt = int(credentials['port'])
key_path = credentials['key_path']


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

next_post_num = str(len(data)+1)
data.append('post'+next_post_num+'.htm')

file = open("post"+next_post_num+".htm", "w")

now = datetime.datetime.now()
r = lambda: random.randint(0,255)

title = raw_input("What's this post about?\n")
file.write("<hr>\n")		
file.write("<h2>"+title+"</h2>\n")
file.write("<h5><span class=\"glyphicon glyphicon-time\"></span> Post by "+calendar.month_name[now.month]+" "+str(now.day)+", "+str(now.year)+".</h5>")
tags = raw_input("What kind of tags do you think this post is related to?\nSeprate tags with \',\' character.\n")
array = filter(None, tags.replace(",", " ").split(' '))
file.write("<h5>")
for x in array:
	file.write("<span class=\"label\" style=\"background-color:"+"#%02X%02X%02X" % (r(),r(),r()) +"\">"+x+"</span>")
file.write("</h5><br>\n")	
body = raw_input("Now type in the body of your post:\n(Remember this is plain html so feel free to use any phrase element you want.\ne.g. <pre> for code snippet, <code> for a command, <br> for new line etc.)\n")
file.write("<p>")
file.write(body)
file.write("</p>")

file.close()


scp.close()
