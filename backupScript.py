import os
import schedule
import time
import smtplib
from tkinter import filedialog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from shutil import copyfile
from datetime import datetime



print('---------------BackupScript Started,,,---------------')

print("choose your backup directory")
backupDir = filedialog.askdirectory(initialdir = "C:/",title = "choose your backup directory")
print("choose your backup file with directory")
backupFileWithDir = filedialog.askopenfilename(initialdir = "C:/", title = "choose your backup file with directory")    
email = input('input your email address : ')
emailAppPw = input('input your application password : ')

fileName = ""
filePath = ""



def backup():

    makeBackupDir()

    copyInBackupDir()

    sendMailBackupFile()



def getFileInfo():
    global fileName
    global filePath

    fileName = backupFileWithDir[backupFileWithDir.rindex('/') + 1:]
    filePath = backupFileWithDir[:backupFileWithDir.rfind('/')]



def makeBackupDir():
    os.chdir(backupDir)

    if(not os.path.isdir('backup')):
        os.mkdir('backup')
        print('Backup Directory Created!')



def copyInBackupDir():
    getFileInfo()

    todayDate = datetime.today().strftime('%Y-%m-%d')
    backupFileName = todayDate + ' B_' + fileName

    os.chdir(filePath)
    if(os.path.isfile(fileName)): 
        copyfile(backupFileWithDir, backupDir + '\\backup\\' + backupFileName)
        print('File Copy and Paste Success!')



def sendMailBackupFile():
    todayDate = datetime.today().strftime('%Y-%m-%d')
    backupFileName = todayDate + ' B_' + fileName

    os.chdir(backupDir)
    if(os.path.isdir('backup') and os.path.isfile('backup\\'+ backupFileName)):
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login(email, emailAppPw)

            msg = MIMEMultipart()
            msg['Subject'] = todayDate + 'Test Backup'
            msg.attach(MIMEText(todayDate + ' Backup success', 'plain'))

            attachment = open(backupDir + '\\backup\\' + backupFileName, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename = ' + backupFileName)
            msg.attach(part)

            s.sendmail(email, email, msg.as_string())
        except Exception as e:
            print(e)
        finally:
            print('Mail Send Success!')
            print('---------------BackupScript Closed,,,---------------')
            s.quit()



if(backupDir != '' and backupDir != '' and email != '' and emailAppPw != ''):
    schedule.every(5).seconds.do(backup)

    while True:
        schedule.run_pending()
        time.sleep(1)
else:
    exit()
        
    
