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
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QSpinBox, QCheckBox, QMessageBox, QComboBox)
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

todayDate = datetime.today().strftime('%Y-%m-%d')
backupFileName = ''

class WorkThread(QThread):
    def __init__(self, parent):
        super().__init__()

        self.parent = parent


 
    def run(self):
        self.isWork = True

        self.parent.logTextBox.append('----------------------BackupScript Started,,,----------------------')

        self.sched = BackgroundScheduler()
        self.sched.start()

        self.sched.add_job(self.backup, 'cron', hour = hourVal, minute = minuteVal, second = secondVal, id="backupScheduler")

        while self.isWork:
            time.sleep(1)



    def stopThread(self):
        self.isWork = False
        self.quit()
        self.sched.remove_job('backupScheduler')

        self.parent.logTextBox.append('----------------------BackupScript Closed,,,----------------------')     
        QApplication.processEvents()

        self.wait(3000)



    def backup(self):
        self.makeBackupDir()
        self.copyInBackupDir()
        #self.sendMailBackupFile()



    def makeBackupDir(self):
        os.chdir(backupDir)

        if(not os.path.isdir('backup')):
            os.mkdir('backup')
            self.parent.logTextBox.append('[' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '] Backup Directory Created Success!')
            QApplication.processEvents()



    def copyInBackupDir(self):
        os.chdir(filePath)

        if(os.path.isfile(fileName)): 
            copyfile(backupFileWithDir, backupDir + '\\backup\\' + backupFileName)
            self.parent.logTextBox.append('[' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '] File Copy and Paste Success!')
            QApplication.processEvents()



    def sendMailBackupFile(self):

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
                self.parent.logTextBox.append('[' + datetime.today().strftime('%Y-%m-%d %H:%M:%S') + '] Mail Send Success!')
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

        self.emailInput = QLineEdit(self)

        self.emailAppPwInput = QLineEdit(self)

        self.hourLabel = QLabel('HOUR (0~23)', self)
        self.hourCombo = QComboBox(self)
        
        for i in range(0, 24):
            self.hourCombo.addItem(str(i))

        self.minuteLabel = QLabel('MINUTE (0~59)', self)
        self.minuteCombo = QComboBox(self)
        
        for i in range(0, 60):
            self.minuteCombo.addItem(str(i))

        self.secondLabel = QLabel('SECOND (0~59)', self)
        self.secondCombo = QComboBox(self)
        
        for i in range(0, 60):
            self.secondCombo.addItem(str(i))

        self.hourEvery = QCheckBox('every', self)
        self.minuteEvery = QCheckBox('every', self)
        self.secondEvery = QCheckBox('every', self)
    
        self.logTextBox = QTextEdit()
        self.execBackupBtn = QPushButton('Run', self)
        self.stopThreadBtn = QPushButton('Stop', self)

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

        grid.addWidget(self.hourLabel, 5, 2)
        grid.addWidget(self.hourCombo, 5, 3)
        grid.addWidget(self.hourEvery, 5, 4)
        grid.addWidget(self.minuteLabel, 6, 2)
        grid.addWidget(self.minuteCombo, 6, 3)
        grid.addWidget(self.minuteEvery, 6, 4)
        grid.addWidget(self.secondLabel, 7, 2)
        grid.addWidget(self.secondCombo, 7, 3)
        grid.addWidget(self.secondEvery, 7, 4)

        grid.addWidget(self.execBackupBtn, 8, 2, 6, 1)
        grid.addWidget(self.stopThreadBtn, 8, 3, 6, 2)

        self.workThread = WorkThread(self)

        self.findBackupDirBtn.clicked.connect(self.findBackupDir)
        self.findBackupFileBtn.clicked.connect(self.findBackupFile)
        self.execBackupBtn.clicked.connect(self.initVal)
        self.stopThreadBtn.clicked.connect(self.workThread.stopThread)

        self.hourEvery.stateChanged.connect(self.checkHourEvery)
        self.minuteEvery.stateChanged.connect(self.checkMinuteEvery)
        self.secondEvery.stateChanged.connect(self.checkSecondEvery)

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



    def checkHourEvery(self):
        if(self.hourEvery.isChecked()):
            self.hourCombo.removeItem(0)
            self.hourLabel.setText('HOUR (1~23)')
        else:
            self.hourCombo.insertItem(0, '0')
            self.hourLabel.setText('HOUR (0~23)')



    def checkMinuteEvery(self):
        if(self.minuteEvery.isChecked()):
            self.minuteCombo.removeItem(0)
            self.minuteLabel.setText('MINUTE (1~59)')
        else:
            self.minuteCombo.insertItem(0, '0')
            self.minuteLabel.setText('MINUTE (0~59)')



    def checkSecondEvery(self):
        if(self.secondEvery.isChecked()):
            self.secondCombo.removeItem(0)
            self.secondLabel.setText('SECOND (1~59)')
        else:
            self.secondCombo.insertItem(0, '0')
            self.secondLabel.setText('SECOND (0~59)')



    def initVal(self):
        if(self.backupDirInput.text() == ''):
            QMessageBox.warning(self, 'Warning', 'Input Your Backup Directory!')
            self.backupDirInput.setFocus()
            return False

        if(self.backupFileInput.text() == ''):
            QMessageBox.warning(self, 'Warning', 'Input Your Backup File With Directory!')
            self.backupFileInput.setFocus()
            return False

        if(self.emailInput.text() == ''):
            QMessageBox.warning(self, 'Warning', 'Input Your Email')
            self.emailInput.setFocus()
            return False

        if(self.emailAppPwInput.text() == ''):
            QMessageBox.warning(self, 'Warning', 'Input Your Email App Password!')
            self.emailAppPwInput.setFocus()
            return False


        global backupDir
        global backupFileWithDir
        global email
        global emailAppPw

        global hourVal
        global minuteVal
        global secondVal        

        global fileName
        global filePath
        global backupFileName

        backupDir = self.backupDirInput.text()
        backupFileWithDir = self.backupFileInput.text()
        email = self.emailInput.text()
        emailAppPw = self.emailAppPwInput.text()

        hourVal = str(self.hourCombo.currentText())
        minuteVal = str(self.minuteCombo.currentText())
        secondVal = str(self.secondCombo.currentText())

        if(self.hourEvery.isChecked()):
            hourVal = '*/' + hourVal
        if(self.minuteEvery.isChecked()):
            minuteVal = '*/' + minuteVal
        if(self.secondEvery.isChecked()):
            secondVal = '*/' + secondVal

        fileName = backupFileWithDir[backupFileWithDir.rindex('/') + 1:]
        filePath = backupFileWithDir[:backupFileWithDir.rfind('/')]
        
        backupFileName = todayDate + ' B_' + fileName

        print(hourVal)
        print(minuteVal)
        print(secondVal)

        self.workThread.start()


 
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = Main()
   sys.exit(app.exec_())
