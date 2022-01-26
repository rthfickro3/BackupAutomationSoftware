import os
from pickle import TRUE
from turtle import back
import schedule
import time
import smtplib
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from tkinter import filedialog
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from shutil import copyfile
from datetime import datetime
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSpinBox, QCheckBox)
from PyQt5.QtCore import QThread

backupDir = ''
backupFileWithDir = ''
email = ''
emailAppPw = ''

fileName = ''
filePath = ''

hourVal = ''
minuteVal = ''
secondVal = ''

class WorkThread(QThread):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent
 
    def run(self):

        self.parent.logTextBox.append('----------------------BackupScript Started,,,----------------------')

        sched = BackgroundScheduler()
        sched.start()

        sched.add_job(self.backup, 'cron', hour = hourVal, minute = minuteVal, second = secondVal, id="test1")

        while True:
            time.sleep(1)


    def backup(self):
        self.makeBackupDir()
        self.copyInBackupDir()
        #self.sendMailBackupFile()



    def makeBackupDir(self):
        os.chdir(backupDir)

        if(not os.path.isdir('backup')):
            os.mkdir('backup')
            self.parent.logTextBox.append('Backup Directory Created Success!')
            QApplication.processEvents()


    def copyInBackupDir(self):

        todayDate = datetime.today().strftime('%Y-%m-%d')
        backupFileName = todayDate + ' B_' + fileName

        os.chdir(filePath)
        if(os.path.isfile(fileName)): 
            copyfile(backupFileWithDir, backupDir + '\\backup\\' + backupFileName)
            self.parent.logTextBox.append('File Copy and Paste Success!')
            QApplication.processEvents()



    def sendMailBackupFile(self):
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
                self.parent.logTextBox.append(e)
                QApplication.processEvents()
            finally:
                self.parent.logTextBox.append('Mail Send Success!')
                QApplication.processEvents()
                self.parent.logTextBox.append('----------------------BackupScript Closed,,,----------------------')
                QApplication.processEvents()
                s.quit()



class Main(QWidget):
    def __init__(self):
        super().__init__()
        self.configUi()

    def configUi(self):
        grid = QGridLayout()
        self.setLayout(grid)

        self.backupDirInput = QLineEdit(self)
        self.findBackupDirBtn = QPushButton('Find', self)

        self.backupFileInput = QLineEdit(self)
        self.findBackupFileBtn = QPushButton('Find', self)

        self.emailInput = QLineEdit(email, self)

        self.emailAppPwInput = QLineEdit(emailAppPw, self)

        self.execBackupBtn = QPushButton('Run', self)

        self.hourSelect = QSpinBox()
        self.hourSelect.setMinimum(0)
        self.hourSelect.setMaximum(23)
        self.hourSelect.setMaximumWidth(50)

        self.minuteSelect = QSpinBox()
        self.minuteSelect.setMinimum(0)
        self.minuteSelect.setMaximum(59)
        self.minuteSelect.setMaximumWidth(50)
        
        self.secondSelect = QSpinBox()
        self.secondSelect.setMinimum(0)
        self.secondSelect.setMaximum(59)
        self.secondSelect.setMaximumWidth(50)

        self.hourEvery = QCheckBox('every', self)
        self.minuteEvery = QCheckBox('every', self)
        self.secondEvery = QCheckBox('every', self)
        
    
        self.logTextBox = QTextEdit()

        grid.addWidget(QLabel('Choose Backup Directory:', self), 0, 0)
        grid.addWidget(self.backupDirInput, 0, 1)
        grid.addWidget(self.findBackupDirBtn, 0, 2)

        grid.addWidget(QLabel('Choose Backup File:', self), 1, 0)
        grid.addWidget(self.backupFileInput, 1, 1)
        grid.addWidget(self.findBackupFileBtn, 1, 2)

        grid.addWidget(QLabel('Input Your Email:', self), 2, 0)
        grid.addWidget(self.emailInput, 2, 1)

        grid.addWidget(QLabel('Input Your Email App Password:', self), 3, 0)
        grid.addWidget(self.emailAppPwInput, 3, 1)

        grid.addWidget(self.logTextBox, 5, 0, 5, 2)

        grid.addWidget(QLabel('HOUR (0~23)', self), 5, 2)
        grid.addWidget(self.hourSelect, 5, 3)
        grid.addWidget(self.hourEvery, 5, 4)
        grid.addWidget(QLabel('MINUTE (20~59)', self), 6, 2)
        grid.addWidget(self.minuteSelect, 6, 3)
        grid.addWidget(self.minuteEvery, 6, 4)
        grid.addWidget(QLabel('SECOND (0~59)', self), 7, 2)
        grid.addWidget(self.secondSelect, 7, 3)
        grid.addWidget(self.secondEvery, 7, 4)

        grid.addWidget(self.execBackupBtn, 8, 2, 6, 2)

        self.workThread = WorkThread(self)

        self.findBackupDirBtn.clicked.connect(self.findBackupDir)
        self.findBackupFileBtn.clicked.connect(self.findBackupFile)
        self.execBackupBtn.clicked.connect(self.initVal)

        self.setWindowTitle('BackupAutomationSoftware')
        self.resize(1200, 400)
        self.show()

    def findBackupDir(self):
        global backupDir 

        backupDir = filedialog.askdirectory(initialdir = "C:/",title = "choose your backup directory")
        if(backupDir != ''):
            self.backupDirInput.setText(backupDir)


        
    def findBackupFile(self):
        global backupFileWithDir

        backupFileWithDir = filedialog.askopenfilename(initialdir = "C:/", title = "choose your backup file with directory")
        if(backupFileWithDir != ''):
            self.backupFileInput.setText(backupFileWithDir)



    def initVal(self):
        global email
        global emailAppPw

        global hourVal
        global minuteVal
        global secondVal        

        global fileName
        global filePath



        email = self.emailInput.text()
        emailAppPw = self.emailAppPwInput.text()

        hourVal = str(self.hourSelect.value())
        minuteVal = str(self.minuteSelect.value())
        secondVal = str(self.secondSelect.value())

        fileName = backupFileWithDir[backupFileWithDir.rindex('/') + 1:]
        filePath = backupFileWithDir[:backupFileWithDir.rfind('/')]

        if(self.hourEvery.isChecked()):
            hourVal = '*/' + hourVal
        if(self.minuteEvery.isChecked()):
            minuteVal = '*/' + minuteVal
        if(self.secondEvery.isChecked()):
            secondVal = '*/' + secondVal

        print(hourVal)
        print(minuteVal)
        print(secondVal)

        self.workThread.start()


 
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = Main()
   sys.exit(app.exec_())
