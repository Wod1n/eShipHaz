import os
import sys
import time
import numpy as np
import PySide6.QtGui as QtGui
import cusFunct as cf
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from ui_MainWindow import Ui_MainWindow
from shActivity import shActivity
from shError import shError
from reqKeys import reqKeys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.shMatrix = np.genfromtxt('SHMatrix.csv', delimiter=',')
        self.shMatrix = self.shMatrix != 0

        actFile = open('activities.txt', 'r')
        activities = actFile.read()
        actList = activities.split('\n')
        actFile.close()

        i = 1
        while i < len(actList):
            string = actList[i-1]
            self.ui.shAreas.addItem(str(i) + ". " + string)
            i = i + 1

        hazFile = open('transmitters.txt', 'r')
        hazards = hazFile.read()
        hazList = hazards.split('\n')
        hazFile.close()

        self.columns = 4
        self.ui.keyBoard.setColumnCount(self.columns)
        self.ui.keyBoard.setRowCount(len(hazList)/self.columns)
        self.keyMatrix = np.zeros(len(hazList)-1, dtype=bool)

        i=0
        j=0
        while i<len(hazList):
            self.ui.keyBoard.setItem(j,i%self.columns, QTableWidgetItem(hazList[i%self.columns+self.columns*j]))
            i=i+1
            if(i%self.columns == 0):
                j=j+1
        self.setKeyColours()

    def keySwap(self):
        idxRow = self.ui.keyBoard.currentRow()
        idxCol = self.ui.keyBoard.currentColumn()
        idxKey = idxRow*self.columns + idxCol

        if(self.ui.activityTable.rowCount() != 0):
            currentLines = []
            currentSpons = []
            i=0
            while i < self.ui.activityTable.rowCount():
                line = int(self.ui.activityTable.item(i, 0).text())
                if(self.shMatrix[line-1][idxKey]):
                    currentLines.append(line)
                    currentSpons.append(str(self.ui.activityTable.item(i, 2).text()))
                i = i+1
            if(len(currentLines) != 0):
                dialog = shError(currentLines, currentSpons)
                dialog.exec()
                return

        self.keyMatrix[idxKey] = not self.keyMatrix[idxKey]
        self.setKeyColours()

    def newActivity(self):
        dialog = shActivity()
        dialog.exec()
        if(dialog.apply):
            keyDialog = reqKeys(self.shMatrix[dialog.shLine-1], self.keyMatrix)
            keyDialog.exec()
            if(not keyDialog.apply):
                return
            self.keyMatrix = np.logical_or(self.keyMatrix, self.shMatrix[dialog.shLine-1])
            self.setKeyColours()
            newRow = self.ui.activityTable.rowCount()
            self.ui.activityTable.setRowCount(newRow+1)
            self.ui.activityTable.setItem(newRow, 0, QTableWidgetItem(str(dialog.shLine)))
            self.ui.activityTable.setItem(newRow, 1, QTableWidgetItem(cf.milDTG()))
            self.ui.activityTable.setItem(newRow, 2, QTableWidgetItem(dialog.wkSpon))
            self.ui.activityTable.setItem(newRow, 3, QTableWidgetItem(dialog.authOff))
            item = self.ui.shAreas.item(dialog.shLine-1)
            item.setBackground(QtGui.QColor("green"))

    def rmActivity(self):
        row = self.ui.activityTable.currentRow()
        rmBy = "Gibby"
        shLine = int(self.ui.activityTable.item(row, 0).text())
        arcLine = str(shLine) + '|'
        i=1
        while i < 4:
            arcLine = arcLine + self.ui.activityTable.item(row, i).text() + '|'
            i = i+1
        arcLine = arcLine + cf.milDTG() + '|' + rmBy + '\n'
        cf.actArchive(arcLine)
        self.ui.activityTable.removeRow(row)
        item = self.ui.shAreas.item(shLine-1)
        item.setBackground(QtGui.QColor(0,0,0,0))

    def setKeyColours(self):
        i = 0
        j = 0
        while i < len(self.keyMatrix):
            if(self.keyMatrix[i]):
                item = self.ui.keyBoard.item(j, i%self.columns)
                item.setBackground(QtGui.QColor("red"))
            else:
                item = self.ui.keyBoard.item(j, i%self.columns)
                item.setBackground(QtGui.QColor(0,0,0,0))
            i = i + 1
            if(i%self.columns == 0):
                j = j + 1
