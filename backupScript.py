import os
from shutil import copyfile
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import schedule
import time

def backup(backupDir):
    print('---------------BackupScript Started,,,---------------')

    os.chdir(backupDir)

    if(not os.path.isdir('\\backup')):
        os.mkdir('\\backup')
        print('Backup Directory Created!')
    
    todayDate = datetime.today().strftime('%Y-%m-%d')
    backupFileName = todayDate + ' QA Work List Backup.xlsx'
    
    if(os.path.isfile('QA이슈 처리 리스트.xlsx')): 
        copyfile('F:\\QA이슈 처리 리스트.xlsx', 'F:\\backup\\' + backupFileName)
        print('File Copy and Paste Success!')

    if(os.path.isdir('\\backup') and os.path.isfile('\\backup\\' + backupFileName)):
        try:
            s = smtplib.SMTP('smtp.gmail.com', 587)
            s.starttls()
            s.login('rthfickro3@gmail.com', 'unjufjbcprzluchm')

            msg = MIMEMultipart()
            msg['Subject'] = todayDate + 'QA Work List Backup'
            msg.attach(MIMEText(todayDate + ' BackupFile', 'plain'))

            attachment = open('F:\\backup\\'+backupFileName, 'rb')
            part = MIMEBase('application', 'octet-stream')
            part.set_payload((attachment).read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename = ' + backupFileName)
            msg.attach(part)

            s.sendmail('rthfickro3@gmail.com', 'rthfickro3@gmail.com', msg.as_string())
        except Exception as e:
            print(e)
        finally:
            print('Mail Send Success!')
            print('---------------BackupScript Closed,,,---------------')
            s.quit()

schedule.every(30).seconds.do(backup, 'F:')

while True:
    schedule.run_pending()
    time.sleep(1)
