#!/usr/local/bin/python
#*********************************** Version 0.1  ***************************
import datetime,os,sys,gzip,shutil,ConfigParser,tarfile
from ftplib import FTP

config = ConfigParser.ConfigParser()
config.read("/root/scripts/bkp_dir.conf")

LocalDIR=os.path.abspath(config.get('conf','LocalDIR'))
RemoteDIR=os.path.abspath(config.get('conf','RemoteDIR'))
DaysForBkp=-1
FILE=""
if len(sys.argv)==1:
	BackupDIR=os.path.abspath(config.get('conf','BackupDIR'))
elif len(sys.argv)==2:
	BackupDIR=os.path.abspath(sys.argv[1])
elif len(sys.argv)==3:
	BackupDIR=os.path.abspath(sys.argv[1])
	DaysForBkp=int(sys.argv[2])
elif len(sys.argv)==4:
        BackupDIR=os.path.abspath(sys.argv[1])
        DaysForBkp=int(sys.argv[2])
	FILE=sys.argv[3]
else:
	print "Incorrect number of parameters!!!"
	print "Please try: "+__file__+" dir_to_backup [number_of_days_to_backup]" 
	sys.exit(1)

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



#*********************************************************************************
def GetFilesFromDir(dir):
        files=[]
        for root, directories, filenames in os.walk(dir):
           for filename in filenames:
                files.append(os.path.join(root,filename))
        return files
#*************************   Start Script ****************************************
#Check OS name
if not sys.platform.startswith('freebsd'):
        print "OS "+sys.platform+" is not checked for correct work!!!"

#Setting dated file and dir name
now = datetime.datetime.now()
Y=str(now.year)
M=str(now.month)
D=str(now.day)

if DaysForBkp==-1:      #Automatic increment level based on weekday number
	DaysForBkp=now.weekday() 
print "It`s going to backup files modified for ",  DaysForBkp, " day/days"

DIR=os.path.join(LocalDIR,Y,M,D)
if FILE=="":
	FILE=os.path.basename(BackupDIR)+"_"+str(DaysForBkp)+"_"+now.strftime("%Y%m%d_%H%M")+".tgz"
else:
	FILE=FILE+"_"+str(DaysForBkp)+"_"+now.strftime("%Y%m%d_%H%M")+".tgz"
	
TARFILE=os.path.join(DIR,FILE)

#*********    Creating local copy *************************************************

if not os.path.exists(DIR):
        os.makedirs(DIR)
files=GetFilesFromDir(BackupDIR)
try:
        tarGZ = tarfile.open(TARFILE,'w:gz')
	FileCount=0
        for file in files:
		if DaysForBkp==0:
                	tarGZ.add(file)
			FileCount+=1
#			print "adding:", file, os.stat(file)
		else:
			filetime=datetime.datetime.fromtimestamp(os.path.getmtime(file))
		 	delta=datetime.timedelta(days=DaysForBkp)
			differ=now-filetime
			if differ<delta:
				print "adding:", file
				tarGZ.add(file)
				FileCount+=1
except tarfile.TarError, tarexc:
        print tarexc
finally:
        tarGZ.close()
	print "The are ", FileCount," files backuped"


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
if KeepLocal=='NO': 
	os.remove(TARFILE) #Delete local file
ftp.quit()

print "OK"

