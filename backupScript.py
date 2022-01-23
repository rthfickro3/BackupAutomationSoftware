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
from PyQt5 import QtCore
from PyQt5.QtCore import *

backupDir = ''
backupFileWithDir = ''
email = ''
emailAppPw = ''

fileName = ''
filePath = ''

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        

    def initUI(self):
        grid = QGridLayout()
        self.setLayout(grid)

        label1 = QLabel('Choose Backup Directory:', self)
        self.backupDirInput = QLineEdit(self)
        self.findBackupDirBtn = QPushButton('Find', self)

        label2 = QLabel('Choose Backup File:', self)
        self.backupFileInput = QLineEdit(self)
        self.findBackupFileBtn = QPushButton('Find', self)

        label3 = QLabel('Input Your Email:', self)
        self.emailInput = QLineEdit(email, self)

        label4 = QLabel('Input Your Email App Password:', self)
        self.emailAppPwInput = QLineEdit(emailAppPw, self)

        self.execBackupBtn = QPushButton('Run', self)

        self.logTextBox = QTextEdit()

        grid.addWidget(label1, 0, 0)
        grid.addWidget(self.backupDirInput, 0, 1)
        grid.addWidget(self.findBackupDirBtn, 0, 2)
        grid.addWidget(label2, 1, 0)
        grid.addWidget(self.backupFileInput, 1, 1)
        grid.addWidget(self.findBackupFileBtn, 1, 2)
        grid.addWidget(label3, 2, 0)
        grid.addWidget(self.emailInput, 2, 1)
        grid.addWidget(label4, 3, 0)
        grid.addWidget(self.emailAppPwInput, 3, 1)
        grid.addWidget(self.logTextBox, 4, 0, 4, 2)
        grid.addWidget(self.execBackupBtn, 5, 2)

        self.findBackupDirBtn.clicked.connect(self.findBackupDir)
        self.findBackupFileBtn.clicked.connect(self.findBackupFile)
        self.execBackupBtn.clicked.connect(self.execBackup)

        self.setWindowTitle('QGridLayout')
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


    def execBackup(self):
        global email
        global emailAppPw
        email = self.emailInput.text()
        emailAppPw = self.emailAppPwInput.text()


        self.logTextBox.append('----------------------BackupScript Started,,,----------------------')
        self.backup()
    

    def backup(self):
        self.makeBackupDir()
        self.copyInBackupDir()
        self.sendMailBackupFile()
        print("ddd")



    def makeBackupDir(self):
        os.chdir(backupDir)

        if(not os.path.isdir('backup')):
            os.mkdir('backup')
            self.logTextBox.append('Backup Directory Created Success!')


                   
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
            self.logTextBox.append('File Copy and Paste Success!')



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
                self.logTextBox.append(e)
            finally:
                self.logTextBox.append('Mail Send Success!')
                self.logTextBox.append('----------------------BackupScript Closed,,,----------------------')
                s.quit()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())
