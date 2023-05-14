import os
import json
from PySide6.QtWidgets import QDialog, QTableWidgetItem
from ui_wtraProposed import Ui_proposedWTRA

class wtraProposed(QDialog):
    def __init__(self, emitters, areas, prohibits, selected):
        super(wtraProposed, self).__init__()
        self.apply = False
        self.ui = Ui_proposedWTRA()
        self.ui.setupUi(self)

        for x in prohibits:
            self.ui.forbiddenAreaList.addItem(str(x) + ". " + areas[x-1])

        mitFile = open('risksandmitigations.json', 'r')
        mitDict = json.load(mitFile)
        mitFile.close()

        i=0
        j=0
        while i<len(selected):
            if selected[i]:
                self.ui.wtraLines.setRowCount(j+1)
                self.ui.wtraLines.setItem(j, 0, QTableWidgetItem(str(i+1)))
                self.ui.wtraLines.setItem(j, 1, QTableWidgetItem(emitters[i]))
                if type(mitDict[emitters[i]]["Risk Factor"]) is list:
                    riskString = ""
                    for x in mitDict[emitters[i]]["Risk Factor"]:
                        riskString = riskString + x + "\n\n"
                else:
                    riskString = mitDict[emitters[i]]["Risk Factor"]
                self.ui.wtraLines.setItem(j, 2, QTableWidgetItem(riskString))

                if type(mitDict[emitters[i]]["Proposed Mitigation Measure"]) is list:
                    mitString = ""
                    for x in mitDict[emitters[i]]["Proposed Mitigation Measure"]:
                        mitString = mitString + x + "\n\n"

                else:
                    mitString = mitDict[emitters[i]]["Proposed Mitigation Measure"]
                self.ui.wtraLines.setItem(j, 3, QTableWidgetItem(mitString))

                if type(mitDict[emitters[i]]["Mitigation Owner"]) is list:
                    ownerString = ""
                    for x in mitDict[emitters[i]]["Mitigation Owner"]:
                        ownerString = ownerString + x + "\n\n"

                else:
                    ownerString = mitDict[emitters[i]]["Mitigation Owner"]
                self.ui.wtraLines.setItem(j, 4, QTableWidgetItem(ownerString))
                j=j+1
            i=i+1
    def accept(self):
        self.apply = True
        self.close()

