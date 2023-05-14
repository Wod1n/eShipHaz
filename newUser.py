import os
import cusFunct as cf
from PySide6.QtWidgets import QDialog, QMessageBox
from ui_newUser import Ui_newUser

class newUser(QDialog):
    def __init__(self, saveDirectory):
        super(newUser, self).__init__()
        self.ui = Ui_newUser()
        self.ui.setupUi(self)
        self.saveDirectory = saveDirectory

        self.ui.passwordBox.setEchoMode(QLineEdit.EchoMode(2))
        self.ui.confirmPasswordBox.setEchoMode(QLineEdit.EchoMode(2))

    def boxChecked(self):
        scpType = self.sender()
        checked = scpType.isChecked()
        self.ui.meSCPButton.setChecked(False)
        self.ui.weSCPButton.setChecked(False)
        scpType.setChecked(checked)
        return

    def accept(self):
        if str(self.ui.passwordBox.text()) != str(self.ui.confirmPasswordBox.text()):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: Passwords do not match")
            msg.setInformativeText("You have enterred different passwords")
            msg.setWindowTitle("Error")
            msg.exec()
            return

        firstName = str(self.ui.firstNameBox.text())
        lastName = str(self.ui.surnameBox.text())
        serviceNo = str(self.ui.passwordBox.text())
        password = str(self.ui.passwordBox.text())
        meSCP = self.ui.meSCPButton.isChecked()
        weSCP = self.ui.weSCPButton.isChecked()

        if firstName == '' or lastName == '' or serviceNo == '' or password == '':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: Some boxes are incomplete")
            msg.setInformativeText("You have not completed all required information")
            msg.setWindowTitle("Error")
            msg.exec()
            return

        string = lastName + '|' + cf.hashPassword(password) + '|' + str(int(weSCP)) +'|' + str(int(meSCP)) +'\n'
        authFile = open(self.saveDirectory + "authorisers.csv", "a")
        authFile.write(string)
        authFile.close()
        self.close()
