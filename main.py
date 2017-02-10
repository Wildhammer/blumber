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
from enum import Enum
import re

class mode(Enum):
	WRITE = 1
	EDIT = 2
	REMOVE = 3

# The default mode is WRITE
cmd = mode.WRITE;


if len(sys.argv) > 1:
	if sys.argv[1] == '-r':
		cmd = mode.REMOVE
		if len(sys.argv) < 3:
			print "The post number must be given\nTry -h option for help"
			sys.exit()
		permission = raw_input("\nAre you sure you want to delete post number "+str(sys.argv[2])+"?(y/n)")
		if permission is 'n':
			sys.exit()
	elif sys.argv[1] == '-e':
		cmd = mode.EDIT
		if len(sys.argv) < 3:
			print "The post number must be given\nTry -h option for help"
			sys.exit()	
	elif sys.argv[1] == '-h':
		print "To write a new post:\n\tpython main"
		print "To edit a post:\n\tpython main -e __post#__"
		print "To delete a post:\n\tpython main -r __post#__"
		sys.exit()
	else :
		print "%s is not a valid option\nusage: python main [-r #| -e #| -h]" % sys.argv[1]
		sys.exit()


#I personally use alias for pythong main.py command but don't worry about if you don't have it
try:
	os.chdir(os.path.expanduser(os.environ['BLUMBER']))
except:
	pass



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

# SFTP for renaming and deleting files
sftp = ssh.open_sftp()

try:#Get the list of current posts on the server
	scp.get('public_html/posts.php','./') 
except:#If the file doesn't exist on server then make one
	with open('posts.php','w') as data_file:
		json.dump({"records":[]}, data_file)
		data_file.close()
		scp = SCPClient(ssh.get_transport())
	pass

#Updating the posts.json file locally(if it's edit mode there's no need for touching this file)
with open('posts.php','r+') as data_file:
    data = json.load(data_file)
    if cmd == mode.REMOVE:
    	#First delete the old post file if it exists, otherwise return error
    	if not len(data['records']) > int(sys.argv[2])-1:
    		print "ERROR: \n\tThere are only %s post(s) available, try to find the post number again" % str(len(data['records']))
    		os.remove("posts.php")
    		sys.exit()
    	data['records'].remove('post'+str(sys.argv[2])+'.htm')	
    	sftp.remove('public_html/'+'post'+str(sys.argv[2])+'.htm')
    	#Then reorder the posts number
    	for i in range(int(sys.argv[2])-1,len(data['records'])):
    		data['records'][i] = 'post'+str(i+1)+'.htm'
    		sftp.rename('public_html/post'+str(i+2)+'.htm', 'public_html/post'+str(i+1)+'.htm')	
    	data_file.seek(0)		
    	data_file.truncate()
    elif cmd == mode.WRITE :
    	#Just add the name of the new post to the list
    	next_post_num = str(len(data["records"])+1)
    	data['records'].append('post'+next_post_num+'.htm')
    	data_file.seek(0)
    elif cmd == mode.EDIT:
    	next_post_num = str(sys.argv[2])
    if not cmd == mode.EDIT: 
    	#No need for touching the list if it is edit mode
	    json.dump(data, data_file)
	    data_file.close()
	    scp.put('posts.php', 'public_html/')
	    os.remove("posts.php")

if cmd == mode.WRITE or cmd == mode.EDIT:
	#if edit mode then get the old data from server and place it into the file
	if cmd == mode.EDIT : 
		try:#Get the old post
			scp.get('public_html/post'+str(sys.argv[2])+'.htm','./') 
		except:#If the post doesn't exist on server then print error
			print "ERROR: \n\tPost "+str(sys.argv[2])+" doesn't exist. \n\tThere are only "+str(len(data['records']))+" post(s) available."
			os.remove("posts.php")
			sys.exit()
			pass
		with open('post'+str(sys.argv[2])+'.htm') as __file:
			#Getting the old title, tags, and body
			old_file = __file.read()
			regex = r"<h2>.*</h2>"
			old_title = re.findall(regex, old_file)[0].replace('<h2>','').replace('</h2>','')

			regex = r"<span[^<]*</span>"
			old_array = [x.replace('</span>','') for x in [re.sub(r'<span[^<]*>','',x) for x in re.findall(regex, old_file)]]
			old_array.pop(0)

			regex = r"<p>.*</p>"
			old_body = re.findall(regex, old_file)[0].replace('<br>','\n').replace('<p>','').replace('</p>','')


	#The file including instructions to write a post
	f = open("temp","w")
	f.write("################THIS PART WILL BE IGNORED##################\n")
	f.write("Fill out each section with relevant information about your post.\n")
	f.write(" - Separate multiple tags with \',\' character.\n")
	f.write(" - In order to include a code snippet use <pre></pre> tag (feel free to use other HTML phrase elements).\n")
	f.write(" - Do not make any changes to above lines.\n")
	f.write("###########################################################\n")
	f.write("-------------TITLE--------------\n")
	if cmd == mode.EDIT:
		f.write(old_title)
	f.write("\n-------------TAGS---------------\n")
	if cmd == mode.EDIT:
		for x in old_array:
			f.write(x+',')
	f.write("\n-------------BODY---------------\n")
	if cmd == mode.EDIT:
		f.write(old_body)
	else :
		f.write("\n")
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

	#New post is sent to the server
	scp.put('post'+next_post_num+'.htm','public_html/')
	os.remove("post"+next_post_num+".htm")

	scp.close()
	sftp.close()
	ssh.close()

	if cmd == mode.WRITE:
		print "Your recent post with \"%s\" title has been posted on your website successfully!" % title
	else :
		print "Your recent post with \"%s\" title has been updated on your website successfully!" % title

else:
	sftp.close()
	scp.close()
	ssh.close()