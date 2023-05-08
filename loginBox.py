import os
import cusFunct as cf
from ui_Login import Ui_loginBox
from PySide6.QtWidgets import QDialog, QMessageBox, QGridLayout, QLabel, QLineEdit

class loginBox(QDialog):
    def __init__(self, saveDirectory):
        super(loginBox, self).__init__()
        self.continueLogin = False
        self.ui = Ui_loginBox()
        self.ui.setupUi(self)
        self.userList = []
        self.scp = False
        self.ui.loginButton.setDefault(True)
        self.ui.pwBox.setEchoMode(QLineEdit.EchoMode(2))
        if os.path.isfile(saveDirectory + 'authorisers.csv'):
            userFile = open(saveDirectory + 'authorisers.csv', 'r')
            users = userFile.read()
            self.userList = users.split('\n')
            userFile.close()
            i=0
            while i<len(self.userList)-1:
                self.userList[i] = self.userList[i].split('|')
                i=i+1

    def login(self):
        found = False
        i=0
        while i<len(self.userList)-1:
            if str(self.ui.userBox.text()) == self.userList[i][0]:
                found = True
                if cf.hashPassword(str(self.ui.pwBox.text())) == self.userList[i][1]:
                    self.user = self.userList[i][0]
                    self.password = self.ui.pwBox.text()
                    self.scp = self.userList[i][2] != 0
                    self.continueLogin = True
                    self.close()

                else:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Error: Password not Recognised")
                    msg.setInformativeText("You have enterred an invalid password")
                    msg.setWindowTitle("Error")
                    msg.exec()
            i=i+1
        if not found:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: Username not Recognised")
            msg.setInformativeText("You have enterred an invalid username")
            msg.setWindowTitle("Error")
            msg.exec()

    def guest(self):
        self.user = "Guest"
        self.continueLogin = True
        self.close()
