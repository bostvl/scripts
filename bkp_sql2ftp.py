#!/usr/local/bin/python
#*********************************** Version 0.1  ***************************
import datetime,os,sys,gzip,shutil,ConfigParser
from ftplib import FTP

config = ConfigParser.ConfigParser()
config.read("./bkp_sql.conf")

LocalDIR=config.get('conf','LocalDIR')
RemoteDIR=config.get('conf','RemoteDIR')
DBHOST=config.get('conf','DBHOST')
DBUSER=config.get('conf','DBUSER')
DBPASSWORD=config.get('conf','DBPASSWORD')
FTPHost=config.get('conf','FTPHost')
FTPUser=config.get('conf','FTPUser')
FTPPassword=config.get('conf','FTPPassword')

mysqldump_cmd=config.get('conf','mysqldump_cmd')
mysql_cmd=config.get('conf','mysql_cmd')

#*************************   Start Script ****************************************
#Check OS name
if not sys.platform.startswith('freebsd'):
        print "OS "+sys.platform+" is not checked for correct work!!!"

#Setting dated file and dir name
now = datetime.datetime.now()
Y=str(now.year)
M=str(now.month)
D=str(now.day)
DIR=LocalDIR+Y+"/"+M+"/"+D+"/"

#Creating RemoteDIR structure ******************************************************
ftp=FTP(FTPHost,FTPUser,FTPPassword)
ftp.cwd(RemoteDIR)
try:
	ftp.mkd(RemoteDIR+Y)
except Exception,e:
	print e
try:
	ftp.mkd(RemoteDIR+Y+"/"+M)
except Exception,e:
	print e
try:
	ftp.mkd(RemoteDIR+Y+"/"+M+"/"+D)
except Exception,e:
	print e

DBlist_cmd=mysql_cmd+" -u %s -p%s -h %s --silent -N -e 'show databases'" % (DBUSER,DBPASSWORD,DBHOST)
DBList=os.popen(DBlist_cmd).readlines()
for DBNAME in DBList:
        DBNAME=DBNAME.strip()
        if DBNAME in ['information_schema','performance_schema','test']:
                continue #Skip system databases
	FILE=DBNAME+"_"+now.strftime("%Y%m%d_%H%M")+".sql"
	if not os.path.exists(DIR):
		os.makedirs(DIR)
	dumpcmd = mysqldump_cmd+" -u "+DBUSER+" -p"+DBPASSWORD+" -h "+DBHOST+" "+DBNAME+" > "+DIR+FILE
	result=os.system(dumpcmd)
	if result<>0:
		print "SQL dump ERROR: "+str(result)
	with open(DIR+FILE, 'rb') as f_in, gzip.open(DIR+FILE+".gz", 'wb') as f_out:  #gzip file
		shutil.copyfileobj(f_in, f_out)
	os.remove(DIR+FILE) #Delete old file
	FILE=FILE+".gz"
	rDIR=RemoteDIR+Y+"/"+M+"/"+D+"/"
	ftp.cwd(rDIR)
	ftp.storbinary('STOR '+FILE, open(DIR+FILE, 'rb'))

ftp.quit()

print "OK"



#/usr/bin/ssh univer@194.44.10.35 /home/univer/make_dir.sh
#/usr/bin/scp $DIR/$FILE univer@194.44.10.35:/home/univer/bkp/sql/$Y/$M/$D
