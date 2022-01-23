import os
from pickle import TRUE
from turtle import back
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
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QTextEdit, QPushButton)
from PyQt5.QtCore import *

backupDir = ''
backupFileWithDir = ''
email = ''
emailAppPw = ''

fileName = ''
filePath = ''

class WorkThread(QThread):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        global email
        global emailAppPw
        email = self.parent.emailInput.text()
        emailAppPw = self.parent.emailAppPwInput.text()

 
    def run(self):
        while True:
            self.parent.logTextBox.append('----------------------BackupScript Started,,,----------------------')

            schedule.every(5).seconds.do(self.backup)

            while True:
                schedule.run_pending()
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


                   
    def getFileInfo(self):
        global fileName
        global filePath

        fileName = backupFileWithDir[backupFileWithDir.rindex('/') + 1:]
        filePath = backupFileWithDir[:backupFileWithDir.rfind('/')]


         
    def copyInBackupDir(self):
        self.getFileInfo()

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

        grid.addWidget(self.logTextBox, 4, 0, 4, 2)
        
        grid.addWidget(self.execBackupBtn, 5, 2)

        self.workThread = WorkThread(self)

        self.findBackupDirBtn.clicked.connect(self.findBackupDir)
        self.findBackupFileBtn.clicked.connect(self.findBackupFile)
        self.execBackupBtn.clicked.connect(self.workThread.start)

        self.setWindowTitle('BackupAutomationSoftware')
        self.resize(800, 400)
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


 
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = Main()
   sys.exit(app.exec_())
