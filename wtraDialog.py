import json
import numpy as np
from datetime import datetime
from PySide6.QtWidgets import QDialog, QAbstractItemView
from PySide6.QtCore import QDate
from ui_wtraDialog import Ui_wtraDialog

class wtraDialog(QDialog):
    def __init__(self, shMatrix, shAreas):
        super(wtraDialog, self).__init__()
        self.shAreas = shAreas
        self.apply = False
        self.ui = Ui_wtraDialog()
        self.ui.setupUi(self)
        self.ui.emitterList.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.matrix = shMatrix
        self.selected = np.zeros(len(shMatrix[0]), dtype = bool)
        self.forbidden = np.zeros(self.shAreas, dtype = bool)
        self.forbiddenAreas = []

        actFile = open('activities.txt', 'r')
        activities = actFile.read()
        actList = activities.split('\n')
        actFile.close()

        year = datetime.now().year
        month = datetime.now().month
        self.ui.dtgPTTX.setDateRange(QDate(year, month-1, 1), QDate(year, month+1, 1))
        self.ui.dtgExpiry.setDateRange(QDate(year, month-1, 1), QDate(year, month+1, 1))

        i=1
        while i<len(actList):
            string = actList[i-1]
            self.ui.shActivities.addItem(str(i) + ". " + string)
            i=i+1

        self.listHazards()

    def listHazards(self):
        self.ui.emitterList.clear()
        index = self.ui.shActivities.currentIndex()
        hazFile = open('transmitters.txt', 'r')
        hazards = hazFile.read()
        hazList = hazards.split('\n')
        hazFile.close()
        if hazList[-1] == "":
            hazList.pop()

        i=0
        while i<len(hazList):
            if self.matrix[index][i]:
                string = hazList[i]
                self.ui.emitterList.addItem(string)
            i=i+1


    def accept(self):
        self.apply = True
        i=0
        j=0
        while i<len(self.selected):
            if self.matrix[self.ui.shActivities.currentIndex()][i]:
                if self.ui.emitterList.item(j).isSelected():
                    self.selected[i] = True
                j=j+1
            if self.selected[i]:
                self.forbidden = np.logical_or(self.forbidden, self.matrix[0:self.shAreas,i])
            i=i+1

        i=0
        while i<len(self.forbidden):
            if self.forbidden[i]:
                self.forbiddenAreas.append(i+1)
            i=i+1
        self.close()
