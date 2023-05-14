import os
import csv
import sys
import time
import pytz
import json
import numpy as np
import PySide6.QtGui as QtGui
import cusFunct as cf
from datetime import datetime
from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem, QMessageBox
from ui_MainWindow import Ui_MainWindow
from loginBox import loginBox
from newUser import newUser
from shActivity import shActivity
from shError import shError
from reqKeys import reqKeys
from wtraDialog import wtraDialog
from wtraProposed import wtraProposed

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.nextWEWTRA = 1
        self.nextMEWTRA = 1
        self.currentUser = "Guest"
        self.currentPassword = "Password"
        self.access = 16
        self.weScp = True
        self.meScp = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.saveDirectory = "./SavedData/"
        self.shMatrix = np.genfromtxt('SHMatrix.csv', delimiter=',')
        self.shMatrix = self.shMatrix != 0
        self.activeWTRA = []
        self.timeZone = datetime.now().hour - datetime.now(pytz.utc).hour
        if self.timeZone < 0:
            self.timeZone = -1*self.timeZone + 12
        self.zoneCode = ['Z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y']

        actFile = open('activities.txt', 'r')
        activities = actFile.read()
        actList = activities.split('\n')
        actFile.close()

        hazFile = open('transmitters.txt', 'r')
        hazards = hazFile.read()
        hazList = hazards.split('\n')
        hazFile.close()

        self.hazList = hazList
        self.actList = actList

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

        if os.path.isfile(self.saveDirectory + "persistWTRA.csv"):
            self.wtraEmitters = np.genfromtxt(self.saveDirectory + "persistWTRA.csv", delimiter='|')
            self.setWTRAs()

        else:
            self.wtraEmitters = np.zeros(self.shMatrix.shape, dtype=bool)

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

        self.loadPersistData()

    def keySwap(self):
        if self.currentUser == "Guest":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: You do not have permission")
            msg.setInformativeText("Guest access does not permit swapping of keys/tallies")
            msg.setWindowTitle("Error")
            msg.exec()
            return
        idxRow = self.ui.keyBoard.currentRow()
        idxCol = self.ui.keyBoard.currentColumn()
        idxKey = idxRow*self.columns + idxCol

        if(self.ui.activityTable.rowCount() != 0):
            currentLines = []
            currentSpons = []
            currentWTRA = []
            i=0
            while i < self.ui.activityTable.rowCount():
                line = int(self.ui.activityTable.item(i, 0).text())
                if(self.shMatrix[line-1][idxKey]):
                    currentLines.append(line)
                    currentSpons.append(str(self.ui.activityTable.item(i, 2).text()))
                i = i+1

            if(len(currentLines) != 0):
                for x in currentLines:
                    if(self.wtraEmitters[x-1][idxKey]):
                        currentWTRA.append(x)
                        currentLines.remove(x)

                if(len(currentLines) != 0):
                    dialog = shError(currentLines, currentSpons)
                    dialog.exec()
                    return

        if(len(currentWTRA) != 0):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Active White Tally")
            infoString = "WTRA " + "NUMBER" + "/" + "YEAR" + " has allowed this to go ahead despite ShipHaz lines:\n"
            for x in currentWTRA:
                infoString = infoString + str(x) + "\n"
            infoString = infoString + "being in force"
            msg.setInformativeText(infoString)
            msg.exec()

        self.keyMatrix[idxKey] = not self.keyMatrix[idxKey]
        self.setKeyColours()

    def newActivity(self):
        ''''
        # Commented out for debugging purposes
        if self.currentUser == "Guest":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error: You do not have permission")
            msg.setInformativeText("Guest access does not permit addition or removal of ShipHaz activities")
            msg.setWindowTitle("Error")
            msg.exec()
            return
        '''
        dialog = shActivity(self.currentUser)
        self.ui.tabWidget.setCurrentIndex(0)
        dialog.exec()

        if(dialog.apply):
            for i in range(self.ui.shBoardMatrix.columnCount()):
                self.ui.shBoardMatrix.item(dialog.shLine, i).setBackground(QtGui.QColor("yellow"))

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
            self.ui.activityTable.setItem(newRow, 3, QTableWidgetItem(self.currentUser))
            item = self.ui.shAreas.item(dialog.shLine-1)
            item.setBackground(QtGui.QColor("green"))

            for i in range(self.ui.shBoardMatrix.columnCount()):
                self.ui.shBoardMatrix.item(dialog.shLine, i).setBackground(QtGui.QColor(0,0,0,0))

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
            # self.weScp = dialog.weScp
            self.meScp = dialog.meScp
            self.currentPassword = dialog.password
            self.ui.currentAccount.setText("Logged in as: " + self.currentUser)
        return dialog.continueLogin

    def newUser(self):
        dialog = newUser(self.saveDirectory)
        dialog.exec()
        return

    def changeSCP(self):
        return

    def changePassword(self):
        return

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

        wtraFile = open(self.saveDirectory + "persistWTRA.csv", 'w')
        np.savetxt(wtraFile, self.wtraEmitters, delimiter='|')
        wtraFile.close()

        if self.ui.wtraTable.rowCount() != 0:
            saveFile = open(self.saveDirectory + "activeWTRA.csv", 'w')
            for x in range(self.ui.wtraTable.rowCount()):
                string = str(self.ui.wtraTable.item(x, 0).text()) + '|'
                string = string + str(self.ui.wtraTable.item(x, 1).text()) + '|'
                string = string + str(self.ui.wtraTable.item(x, 2).text()) + '|'
                saveFile.write(string)
            saveFile.close()
        elif self.ui.wtraTable.rowCount() == 0:
            if os.path.isfile(self.saveDirectory + "activeWTRA.csv"):
                os.remove(self.saveDirectory + "activeWTRA.csv")
        self.close()

    def loadPersistData(self):
        if os.path.isfile(self.saveDirectory + "activeWTRA.csv"):
            wtraFile = open(self.saveDirectory + "activeWTRA.csv", 'r')
            currentWTRA = wtraFile.read()
            wtraList = currentWTRA.split('\n')
            wtraFile.close()

            for x in wtraList:
                wtraDetails = x.split('|')
                wtraDetailFile = open(self.saveDirectory + "WTRAArchive/" + wtraDetails[0] + "/20" + wtraDetails[2] + "-" + wtraDetails[1] + ".json", 'r')
                wtraDict = json.load(wtraDetailFile)

                for key in wtraDict:
                    if type(wtraDict[key]) is list:
                        string = ''
                        for x in wtraDict[key]:
                            if type(x) is not string:
                                string = string + str(x)
                            else:
                                string = string + x
                        wtraDict[key] = string
                row = self.ui.wtraTable.rowCount()
                self.ui.wtraTable.setRowCount(row+1)
                self.ui.wtraTable.setItem(row, 0, QTableWidgetItem(wtraDict["Department"]))
                self.ui.wtraTable.setItem(row, 1, QTableWidgetItem(wtraDict["WTRA Number"]))
                self.ui.wtraTable.setItem(row, 2, QTableWidgetItem(wtraDict["Year"]))
                self.ui.wtraTable.setItem(row, 3, QTableWidgetItem(wtraDict["Equipment Columns"]))
                self.ui.wtraTable.setItem(row, 4, QTableWidgetItem(wtraDict["Equipment Names"]))
                self.ui.wtraTable.setItem(row, 5, QTableWidgetItem(wtraDict["ShipHaz Line"]))
                self.ui.wtraTable.setItem(row, 6, QTableWidgetItem(wtraDict["Issued By"]))
                self.ui.wtraTable.setItem(row, 7, QTableWidgetItem(wtraDict["PTTX"]))
                self.ui.wtraTable.setItem(row, 8, QTableWidgetItem(wtraDict["Expiry"]))


    def setWTRAs(self):
        for ix, iy in np.ndindex(self.wtraEmitters.shape):
            if self.wtraEmitters[ix][iy]:
                self.ui.shBoardMatrix.item(ix+1, iy+1).setBackground(QtGui.QColor(255,255,255,255))

            else:
                self.ui.shBoardMatrix.item(ix+1, iy+1).setBackground(QtGui.QColor(0,0,0,0))

    def newWTRA(self):
        if not (self.weScp or self.meScp):
             msg = QMessageBox()
             msg.setIcon(QMessageBox.Critical)
             msg.setText("Error: You do not have permission")
             msg.setInformativeText("Non SCP'd personnel do not have access to making new White Tally Risk Assessments")
             msg.setWindowTitle("Error")
             msg.exec()
             return

        dialog = wtraDialog(self.shMatrix, self.access)
        dialog.exec()
        if dialog.apply:
            proposed = wtraProposed(self.hazList, self.actList[0:self.access], dialog.forbiddenAreas, dialog.selected)
            proposed.exec()
            if proposed.apply:
                self.wtraEmitters[dialog.ui.shActivities.currentIndex()] = np.logical_or(self.wtraEmitters[dialog.ui.shActivities.currentIndex()], dialog.selected)
                self.setWTRAs()
                ''''
                for x in dialog.forbiddenAreas:
                    item = self.ui.shAreas.item(x-1)
                    item.setBackground(QtGui.QColor("red"))
                '''
                row = self.ui.wtraTable.rowCount()
                self.ui.wtraTable.setRowCount(row+1)
                wtraNumber = ''

                if self.weScp:
                    self.ui.wtraTable.setItem(row, 0, QTableWidgetItem("WE"))
                    if self.nextWEWTRA < 10:
                        wtraNumber = '00' + str(self.nextWEWTRA)

                    elif self.nextWEWTRA < 100:
                        wtraNumber = '0' + str(self.nextWEWTRA)
                    self.nextWEWTRA = self.nextWEWTRA + 1

                elif self.meScp:
                    self.ui.wtraTable.setItem(row, 0, QTableWidgetItem("ME"))
                    if self.nextMEWTRA < 10:
                        wtraNumber = '00' + str(self.nextMEWTRA)

                    elif self.nextMEWTRA < 100:
                        wtraNumber = '0' + str(self.nextMEWTRA)
                    self.nextMEWTRA = self.nextMEWTRA + 1

                self.ui.wtraTable.setItem(row, 1, QTableWidgetItem(wtraNumber))
                self.ui.wtraTable.setItem(row, 2, QTableWidgetItem(str(datetime.now().year)[-2:]))
                columnString = ""
                equipString = ""
                i=0
                while i<len(dialog.selected):
                    if dialog.selected[i]:
                        columnString = columnString + str(i+1) + "\n"
                        equipString = equipString + self.hazList[i] + "\n"
                    i=i+1
                self.ui.wtraTable.setItem(row, 3, QTableWidgetItem(columnString))
                self.ui.wtraTable.setItem(row, 4, QTableWidgetItem(equipString))
                self.ui.wtraTable.setItem(row, 5, QTableWidgetItem(str(dialog.ui.shActivities.currentIndex()+1)))
                self.ui.wtraTable.setItem(row, 6, QTableWidgetItem(self.currentUser))
                pttx = cf.milDTG(dialog.ui.dtgPTTX.date().day(), dialog.ui.dtgPTTX.date().month(), dialog.ui.dtgPTTX.date().year(), dialog.ui.dtgPTTX.time().hour(), dialog.ui.dtgPTTX.time().minute(), self.timeZone)
                self.ui.wtraTable.setItem(row, 7, QTableWidgetItem(pttx))

                expiry = cf.milDTG(dialog.ui.dtgExpiry.date().day(), dialog.ui.dtgExpiry.date().month(), dialog.ui.dtgExpiry.date().year(), dialog.ui.dtgExpiry.time().hour(), dialog.ui.dtgExpiry.time().minute(), self.timeZone)
                self.ui.wtraTable.setItem(row, 8, QTableWidgetItem(expiry))

                wtraDict = {
                    "Department" : str(self.ui.wtraTable.item(row, 0).text()),
                    "WTRA Number" : wtraNumber,
                    "Year" : str(datetime.now().year)[-2:],
                    "Equipment Columns" : columnString.split("\n"),
                    "Equipment Names" : equipString.split("\n"),
                    "ShipHaz Line" : str(dialog.ui.shActivities.currentIndex()+1),
                    "Justification" : str(dialog.ui.justificationBox.text()),
                    "Forbidden Areas" : dialog.forbiddenAreas,
                    "Issued By" : self.currentUser,
                    "PTTX" : pttx,
                    "Expiry" : expiry
                }

                directory = self.saveDirectory + "WTRAArchive/"

                if not os.path.isdir(directory):
                    os.makedirs(directory)

                directory = directory + wtraDict["Department"] + "/"

                if not os.path.isdir(directory):
                    os.makedirs(directory)

                fileText = json.dumps(wtraDict)

                wtraFile = open(directory + str(datetime.now().year) + "-" + wtraDict["WTRA Number"] + ".json", 'w')
                wtraFile.write(fileText)
                wtraFile.close()

            else:
                print("Nope!")

        else:
            print("Stil Nope!")

        return

    def openWTRA(self):
        return

    def rmWTRA(self):
        row = self.ui.wtraTable.currentRow()
        rmBy = self.currentUser
        equipString = self.ui.wtraTable.item(row, 3).text().split("\n")
        shLine = int(self.ui.wtraTable.item(row, 5).text())
        equipLines = []
        if type(equipString) is list:
            for x in equipString:
                if x != '':
                    equipLines.append(int(x))
        for x in equipLines:
            self.wtraEmitters[shLine-1][x-1] = False
        self.setWTRAs()
        self.ui.wtraTable.removeRow(row)
        return

    def testExtantWTRA(self):
        if self.ui.boardSection.currentIndex() == 3:
            i=0
            while i<self.ui.wtraTable.rowCount():
                expiry = str(self.ui.wtraTable.item(i, 8).text())
                day = int(expiry[0:2])
                hour = int(expiry[2:4])
                minute = int(expiry[4:6])
                zone = self.zoneCode.index(expiry[6])
                month = cf.reverseMonth(expiry[7:10])
                year = int(expiry[10:14])

                hour = hour - zone
                if hour < 0:
                    hour = hour + 24
                    day = day - 1
                if datetime(year, month, day, hour, minute) < datetime.now():
                    for x in range(self.ui.wtraTable.columnCount()):
                        self.ui.wtraTable.item(i, x).setBackground(QtGui.QColor("red"))
                i=i+1
