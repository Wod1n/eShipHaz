import sys
import PySide6.QtGui as QtGui
from PySide6.QtWidgets import QApplication, QTableWidgetItem, QDialog

from ui_shError import Ui_shError

class shError(QDialog):
    def __init__(self, currentLines, currentSpons):
        super(shError, self).__init__()
        self.apply = False
        self.ui = Ui_shError()
        self.ui.setupUi(self)

        i=0
        self.ui.shActList.setRowCount(len(currentLines))
        while i < len(currentLines):
            self.ui.shActList.setItem(i, 0, QTableWidgetItem(str(currentLines[i])))
            self.ui.shActList.setItem(i, 1, QTableWidgetItem(currentSpons[i]))
            i=i+1

