#!/usr/local/bin/python
#*********************************** Version 0.1  ***************************
import datetime,os,sys,gzip,shutil,ConfigParser,tarfile
from ftplib import FTP

config = ConfigParser.ConfigParser()
config.read("/root/scripts/bkp_dir.conf")

LocalDIR=config.get('conf','LocalDIR')
RemoteDIR=config.get('conf','RemoteDIR')
if len(sys.argv)==1:
	BackupDIR=os.path.abspath(config.get('conf','BackupDIR'))
else:
	BackupDIR=os.path.abspath(sys.argv[1])

if not os.path.exists(BackupDIR):
	print "ERROR!!! Directory not exixts:"+BackupDIR
	sys.exit(1)
if not os.path.isdir(BackupDIR)
	print "ERROR!!! It is not a directory: "+BackupDIR
	sys.exit(1)







FTPHost=config.get('conf','FTPHost')
FTPUser=config.get('conf','FTPUser')
FTPPassword=config.get('conf','FTPPassword')


#*************************   Start Script ****************************************
#Check OS name
if not sys.platform.startswith('freebsd'):
        print "OS "+sys.platform+" is not checked for correct work!!!"

#Setting dated file and dir name
now = datetime.datetime.now()
Y=str(now.year)
M=str(now.month)
D=str(now.day)
DIR=os.path.join(LocalDIR,Y,M,D)
FILE=os.path.basename(BackupDIR)+"_"+now.strftime("%Y%m%d_%H%M")

print DIR
print FILE

sys.exit()
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

if not os.path.exists(DIR):
	os.makedirs(DIR)
#with open(DIR+FILE, 'rb') as f_in, gzip.open(DIR+FILE+".gz", 'wb') as f_out:  #gzip file
#	shutil.copyfileobj(f_in, f_out)
os.remove(DIR+FILE) #Delete old file
FILE=FILE+".gz"


rDIR=RemoteDIR+Y+"/"+M+"/"+D+"/"
ftp.cwd(rDIR)
ftp.storbinary('STOR '+FILE, open(DIR+FILE, 'rb'))

ftp.quit()

print "OK"



#/usr/bin/ssh univer@194.44.10.35 /home/univer/make_dir.sh
#/usr/bin/scp $DIR/$FILE univer@194.44.10.35:/home/univer/bkp/sql/$Y/$M/$D
