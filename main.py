#paramiko must be installed beforehand
import paramiko
from scp import SCPClient 
import json
from pprint import pprint
import sys
import datetime
import calendar
import random
import os
import subprocess


with open('auth.json') as data_file:    
    credentials = json.load(data_file)    

#getting the ssh login credentials from the file
uname = credentials['username']
pswrd = credentials['password']
hst = credentials['hostname']
prt = int(credentials['port'])
key_path = credentials['key_path']

#SSH stuff
k = paramiko.dsskey.DSSKey(filename=key_path,password=pswrd)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname = hst, username = uname,  pkey = k, port=prt)

# SCPCLient takes a paramiko transport as its only argument
scp = SCPClient(ssh.get_transport())

try:#Get the list of current posts on the server
	scp.get('public_html/posts.php','./') 
except:#If the file doesn't exist on server then make one
	with open('posts.php','w') as data_file:
		json.dump({"records":[]}, data_file)
		data_file.close()
		scp = SCPClient(ssh.get_transport())
	pass


#Updating the posts.json file on the server
with open('posts.php','r+') as data_file:
    data = json.load(data_file)
    next_post_num = str(len(data["records"])+1)
    data["records"].append('post'+next_post_num+'.htm')
    data_file.seek(0)
    json.dump(data, data_file)
    data_file.close()



#The file including instructions to write a post
f = open("temp","w")
f.write("################THIS PART WILL BE IGNORED##################\n")
f.write("Fill out each section with relevant information about your post.\n")
f.write(" - Separate multiple tags with \',\' character.\n")
f.write(" - In order to include a code snippet use <pre></pre> tag (feel free to use other HTML phrase elements).\n")
f.write(" - Do not make any changes to above lines.\n")
f.write("###########################################################\n")
f.write("-------------TITLE--------------\n")
f.write("\n-------------TAGS---------------\n")
f.write("\n-------------BODY---------------\n\n")
f.close()
#vi editor is used(every unix system has vi)
subprocess.call(["vi","temp"])
f = open("temp")
content = f.read().split("###########################################################")[1]
#retrieving information from the temp file
title = str(content[(content.find("TITLE--------------\n")+20):(content.find("\n-------------TAGS")-len(content))])
array = filter(None,content[(content.find("TAGS---------------\n")+20):(content.find("\n-------------BODY")-len(content))].replace("\n"," ").replace(","," ").split(" "))
body = str(content[(content.find("BODY---------------\n")+20):])
f.close()
#no longer need to have the file once processed
os.remove("temp")

#Generating random colors for tags
now = datetime.datetime.now()
r = lambda: random.randint(0,255)

#Making the htm file for the post
file = open("post"+next_post_num+".htm", "w")
file.write("<hr>\n")		
file.write("<h2>"+title+"</h2>\n")
file.write("<h5><span class=\"glyphicon glyphicon-time\"></span> Post by "+calendar.month_name[now.month]+" "+str(now.day)+", "+str(now.year)+".</h5>")
file.write("<h5>")
for x in array:
	file.write("<span class=\"label\" style=\"background-color:"+"#%02X%02X%02X" % (r(),r(),r()) +"\">"+x+"</span>")
file.write("</h5><br>\n")	
file.write("<p>")
file.write(body.replace("\n","<br>"))
file.write("</p>")
file.close()

#Update the json file on the server
scp.put('posts.php', 'public_html/')
os.remove("posts.php")

#New post is sent to the server
scp.put('post'+next_post_num+'.htm','public_html/')
os.remove("post"+next_post_num+".htm")

scp.close()

print "Your recent post with \"%s\" title has posted on your website successfully!" % title
