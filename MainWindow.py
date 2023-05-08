import os
import csv
import sys
import time
import numpy as np
import PySide6.QtGui as QtGui
import cusFunct as cf
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox
from ui_MainWindow import Ui_MainWindow
from loginBox import loginBox
from shActivity import shActivity
from shError import shError
from reqKeys import reqKeys

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.currentUser = "Guest"
        self.currentPassword = ""
        self.scp = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.saveDirectory = "./SavedData/"
        self.shMatrix = np.genfromtxt('SHMatrix.csv', delimiter=',')
        self.shMatrix = self.shMatrix != 0

        actFile = open('activities.txt', 'r')
        activities = actFile.read()
        actList = activities.split('\n')
        actFile.close()

        hazFile = open('transmitters.txt', 'r')
        hazards = hazFile.read()
        hazList = hazards.split('\n')
        hazFile.close()

        if not os.path.isdir(self.saveDirectory):
            os.makedirs(self.saveDirectory)

        self.ui.shBoardMatrix.setRowCount(len(actList))
        self.ui.shBoardMatrix.setColumnCount(len(hazList))
        i = 1
        while i < len(actList):
            string = actList[i-1]
            self.ui.shAreas.addItem(str(i) + ". " + string)
            self.ui.shBoardMatrix.setItem(i,0, QTableWidgetItem(string))
            i = i + 1

        continueLogin = self.changeUser()
        if not continueLogin:
            sys.exit()
        self.columns = 4
        self.ui.keyBoard.setColumnCount(self.columns)
        self.ui.keyBoard.setRowCount(len(hazList)/self.columns)
        self.keyMatrix = np.zeros(len(hazList)-1, dtype=bool)

        hazList.pop()
        i=0
        j=0
        while i<len(hazList):
            self.ui.keyBoard.setItem(j,i%self.columns, QTableWidgetItem(hazList[i%self.columns+self.columns*j]))
            self.ui.shBoardMatrix.setItem(0, i+1, QTableWidgetItem(hazList[i]))
            i=i+1
            if(i%self.columns == 0):
                j=j+1

        for ix, iy in np.ndindex(self.shMatrix.shape):
            if self.shMatrix[ix, iy]:
                self.ui.shBoardMatrix.setItem(ix+1, iy+1, QTableWidgetItem("X"))
            else:
                self.ui.shBoardMatrix.setItem(ix+1, iy+1, QTableWidgetItem(""))

        if(os.path.isfile(self.saveDirectory + 'persistMatrix.csv')):
            importMatrix = np.genfromtxt(self.saveDirectory + 'persistMatrix.csv', delimiter ='|')
            importMatrix = importMatrix != 0
            self.keyMatrix = importMatrix
        self.setKeyColours()

        if os.path.isfile(self.saveDirectory + 'persistActivities.csv'):
            restoreFile = open(self.saveDirectory + 'persistActivities.csv', 'r')
            currentActs = restoreFile.read()
            currentActList = currentActs.split('\n')
            print(currentActList)
            restoreFile.close()
            i=0
            while i < len(currentActList)-1:
                newLine = currentActList[i].split('|')
                newRow = self.ui.activityTable.rowCount()
                self.ui.activityTable.setRowCount(newRow+1)
                self.ui.activityTable.setItem(newRow, 0, QTableWidgetItem(newLine[0]))
                self.ui.activityTable.setItem(newRow, 1, QTableWidgetItem(newLine[1]))
                self.ui.activityTable.setItem(newRow, 2, QTableWidgetItem(newLine[2]))
                self.ui.activityTable.setItem(newRow, 3, QTableWidgetItem(newLine[3]))
                item = self.ui.shAreas.item(int(newLine[0])-1)
                item.setBackground(QtGui.QColor("green"))
                i=i+1


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
        if self.currentUser == "Guest":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: You do not have permission")
            msg.setInformativeText("Guest access does not permit addition or removal of ShipHaz activities")
            msg.setWindowTitle("Error")
            msg.exec()
            return

        dialog = shActivity(self.currentUser)
        self.ui.tabWidget.setCurrentIndex(0)
        dialog.exec()

        if(dialog.apply):
            for i in range(self.ui.shBoardMatrix.columnCount()):
                self.ui.shBoardMatrix.item(dialog.shLine-1, i).setBackground(QtGui.QColor("yellow"))
            keyDialog = reqKeys(self.shMatrix[dialog.shLine-1], self.keyMatrix)
            keyDialog.exec()
            if(not keyDialog.apply):
                for i in range(self.ui.shBoardMatrix.columnCount()):
                    self.ui.shBoardMatrix.item(dialog.shLine-1, i).setBackground(QtGui.QColor(0,0,0,0))
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

            for i in range(self.ui.shBoardMatrix.columnCount()):
                self.ui.shBoardMatrix.item(dialog.shLine-1, i).setBackground(QtGui.QColor(0,0,0,0))

    def rmActivity(self):
        if self.currentUser == "Guest":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: You do not have permission")
            msg.setInformativeText("Guest access does not permit addition or removal of ShipHaz activities")
            msg.setWindowTitle("Error")
            msg.exec()
            return
        row = self.ui.activityTable.currentRow()
        rmBy = self.currentUser
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

    def changeUser(self):
        dialog = loginBox(self.saveDirectory)
        dialog.exec()
        if dialog.continueLogin:
            self.currentUser = dialog.user
            self.scp = dialog.scp
            self.currentPassword = dialog.password
            self.ui.currentAccount.setText("Logged in as: " + self.currentUser)
        return dialog.continueLogin

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

    def closeApp(self):
        saveFile = open(self.saveDirectory + "persistMatrix.csv", 'w')
        np.savetxt(saveFile, self.keyMatrix, delimiter='|')
        saveFile.close()

        if self.ui.activityTable.rowCount() != 0:
            saveFile = open(self.saveDirectory + "persistActivities.csv", 'w')
            i=0
            while i < self.ui.activityTable.rowCount():
                string = str(self.ui.activityTable.item(i, 0).text()) + '|'
                string = string + str(self.ui.activityTable.item(i, 1).text()) + '|'
                string = string + str(self.ui.activityTable.item(i, 2).text()) + '|'
                string = string + str(self.ui.activityTable.item(i, 3).text()) + '\n'
                saveFile.write(string)
                i=i+1
            saveFile.close()
        self.close()

    def newWTRA(self):
        if not self.scp:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: You do not have permission")
            msg.setInformativeText("Non SCP'd personnel do not have access to making new White Tally Risk Assessments")
            msg.setWindowTitle("Error")
            msg.exec()
            return

        return

    def openWTRA(self):
        return
