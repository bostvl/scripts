#!/usr/local/bin/python
#*********************************** Version 0.1  ***************************
import datetime,os,sys,gzip,shutil,ConfigParser,tarfile
from ftplib import FTP

config = ConfigParser.ConfigParser()
config.read("/root/scripts/bkp_dir.conf")

LocalDIR=os.path.abspath(config.get('conf','LocalDIR'))
RemoteDIR=os.path.abspath(config.get('conf','RemoteDIR'))

if len(sys.argv)==1:
	BackupDIR=os.path.abspath(config.get('conf','BackupDIR'))
else:
	BackupDIR=os.path.abspath(sys.argv[1])

if not os.path.exists(BackupDIR):
	print "ERROR!!! Directory not exixts:"+BackupDIR
	sys.exit(1)
if not os.path.isdir(BackupDIR):
	print "ERROR!!! It is not a directory: "+BackupDIR
	sys.exit(1)
KeepLocal=config.get('conf','KeepLocal')
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
FILE=os.path.basename(BackupDIR)+"_"+now.strftime("%Y%m%d_%H%M")+".tgz"
TARFILE=os.path.join(DIR,FILE)


#*********    Creating local copy *************************************************

if not os.path.exists(DIR):
        os.makedirs(DIR)
try:
	tarGZ = tarfile.open(TARFILE,'w:gz')
	tarGZ.add(BackupDIR)
	tarGZ.close()
except tarfile.TarError, tarexc:
	print tarexc


#Creating RemoteDIR structure ******************************************************
ftp=FTP(FTPHost,FTPUser,FTPPassword)
ftp.cwd(RemoteDIR)
try:
	ftp.mkd(os.path.join(RemoteDIR,Y))
except Exception,e:
	print e
try:
	ftp.mkd(os.path.join(RemoteDIR,Y,M))
except Exception,e:
	print e
try:
	ftp.mkd(os.path.join(RemoteDIR,Y,M,D))
except Exception,e:
	print e

rDIR=os.path.join(RemoteDIR,Y,M,D);
ftp.cwd(rDIR)
result=ftp.storbinary('STOR '+os.path.basename(TARFILE), open(TARFILE, 'rb'))
if result==0 and KeepLocal=='NO':  #delete local file only of file has copied to ftp
	        os.remove(TARFILE) #Delete local file
ftp.quit()

print "OK"

