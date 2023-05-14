import sys
import PySide6.QtGui as QtGui
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog

from ui_shActivity import Ui_shActivity

class shActivity(QDialog):
    def __init__(self, authoriser):
        super(shActivity, self).__init__()
        self.apply = False
        self.ui = Ui_shActivity()
        self.ui.setupUi(self)
        actFile = open('activities.txt', 'r')
        activities = actFile.read()
        actList = activities.split('\n')
        actFile.close()

        i = 1
        while i < len(actList):
            string = actList[i-1]
            self.ui.shLine.addItem(str(i) + ". " + string)
            i = i + 1

        self.ui.authOff.setText(authoriser)

    def accept(self):
        self.apply = True
        self.shLine = self.ui.shLine.currentIndex() + 1
        self.wkSpon = str(self.ui.wkSpon.text())
        self.close()
