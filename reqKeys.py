import sys
import numpy as np
import PySide6.QtGui as QtGui
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog

from ui_reqKeys import Ui_reqKeys

class reqKeys(QDialog):
    def __init__(self, reqMatrix, keyMatrix):
        super(reqKeys, self).__init__()
        self.ui = Ui_reqKeys()
        self.ui.setupUi(self)
        self.apply = False

        hazFile = open('transmitters.txt', 'r')
        hazards = hazFile.read()
        hazList = hazards.split('\n')
        hazFile.close()

        i = 0
        while i < len(reqMatrix):
            if reqMatrix[i]:
                self.ui.keyList.addItem(hazList[i])
                if keyMatrix[i]:
                    item = self.ui.keyList.item(self.ui.keyList.count()-1)
                    item.setBackground(QtGui.QColor("red"))
            i = i + 1

    def accept(self):
        self.apply = True
        self.close()
