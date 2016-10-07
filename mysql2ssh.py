#!/usr/local/bin/python
#*********************************** Version 0.1  ***************************
import datetime,os,sys,gzip,shutil
#,ConfigParser


DB_HOST="localhost"
DB_USER="mybackup"
DB_PASSWORD="1qa2ws3ed."
LOCAL_DIR="/home/bkp/"

#REMOTE_USER="nixuser"
#REMOTE_PASSWORD="Gfhjkm2016."
#REMOTE_HOST="192.168.102.61"
#REMOTE_DIR="/usr/share/ftp/bkp_nix_srv/www3/mysql/"

REMOTE_USER="lnu"
REMOTE_HOST="194.44.15.26"
REMOTE_DIR="/home/lnu/moodle/mysql/"

mysqldump_cmd="/usr/local/bin/mysqldump"
mysql_cmd="/usr/local/bin/mysql"
###########################################################################


# Check REMOTE_HOST
result=os.system("/sbin/ping -c 1 "+REMOTE_HOST+"|2>&1")
if result!=0:
        print "SSH host is died !!!"
        sys.exit()


#*************************   Start Script ****************************************
#Check OS name
if not sys.platform.startswith('freebsd'):
        print "OS "+sys.platform+" is not checked for correct work!!!"

#Setting dated file and dir name
now = datetime.datetime.now()
Y=str(now.year)
M=str(now.month)
D=str(now.day)
DIR=LOCAL_DIR+Y+"/"+M+"/"+D+"/"
REMOTE_DIR=REMOTE_DIR+Y+"/"+M+"/"+D+"/"

#Creating RemoteDIR structure ******************************************************
ssh_cmd="/usr/bin/ssh "+REMOTE_USER+"@"+REMOTE_HOST+" /bin/mkdir -p "+REMOTE_DIR
result=os.system(ssh_cmd)
if result!=0:
	print "Error while creating remote dir: "+ssh_cmd

#DBlist_cmd=mysql_cmd+" -u %s -p%s -h %s --silent -N -e 'show databases'" % (DB_USER,DB_PASSWORD,DB_HOST)
#DBList=os.popen(DBlist_cmd).readlines()
DBList=['moodle','mysql']
for DB_NAME in DBList:
#	print DB_NAME
        DB_NAME=DB_NAME.strip()
        if DB_NAME in ['information_schema','performance_schema','test']:
                continue #Skip system databases
	FILE=DB_NAME+"_"+now.strftime("%Y%m%d_%H%M")+".sql"
	if not os.path.exists(DIR):
		os.makedirs(DIR)
	dumpcmd = mysqldump_cmd+" -u "+DB_USER+" -p"+DB_PASSWORD+" -h "+DB_HOST+" "+DB_NAME+" > "+DIR+FILE
	result=os.system(dumpcmd)
	if result<>0:
		print "SQL dump ERROR: "+str(result)
	with open(DIR+FILE, 'rb') as f_in, gzip.open(DIR+FILE+".gz", 'wb') as f_out:  #gzip file
		shutil.copyfileobj(f_in, f_out)
	os.remove(DIR+FILE) #Delete old unzipped file
	FILE=FILE+".gz"
	scp_cmd="/usr/bin/scp "+DIR+FILE+" "+REMOTE_USER+"@"+REMOTE_HOST+":"+REMOTE_DIR+FILE
	result=os.system(scp_cmd)
	if result!=0:
		print "Error while coping file to remote host "+REMOTE_HOST

print "OK?"
