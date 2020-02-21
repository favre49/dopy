from PyQt5 import QtWidgets, QtCore
import sys, os, re, json, socket
import chorePlay, niggerFiles, centralWidgetMerch, leftWidget, displayWidget, merchService
from operator import itemgetter

REMOTE_SERVER = 'www.google.com'

class Entry:
    pass

class Batch:
    pass

class merchWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.batch = Batch()
        self.database = parent.database
        self.setupWidget()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def setupWidget(self):

###########GUI components
        self.centralWidget = centralWidgetMerch.centralWidget(self)

        widgetLayout = QtWidgets.QHBoxLayout()
        widgetLayout.addWidget(self.centralWidget)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addLayout(widgetLayout)

        self.setLayout(vbox)

        self.centralWidget.doneButton.clicked.connect(self.doneButtonHandler)
        self.centralWidget.syncButton.clicked.connect(self.syncButtonHandler)

    def syncButtonHandler(self):
        if not self.connectedOnline():
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Not connected to internet. Connect and Try again!")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.buttonClicked.connect(self.closeDialog)
            msg.exec_()
            return
        res = merchService.syncDB()
        if res == 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Sync succesful! You can close the software now.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.buttonClicked.connect(self.closeDialog)
            msg.exec_()
            self.deleteDBFile()

    def connectedOnline(self):
        try:
            host = socket.gethostbyname(REMOTE_SERVER)
            s = socket.create_connection((host, 80), 2)
            return True
        except:
            pass
        return False

    def deleteDBFile(self):
        os.remove('data-entries.txt')

    def doneButtonHandler(self):
        result = self.updateEntries()
        if result == 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Entry added! Press OK to continue to the next.")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.buttonClicked.connect(self.closeDialog)
            msg.exec_()
            self.centralWidget.refresh()
        elif result == 2:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Entries are either empty or incomplete! Please be careful next time")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.buttonClicked.connect(self.closeDialog)
            msg.exec_()
            # self.centralWidget.refresh()
        elif result == 3:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Enter a number as quantity, not any other characters or letters")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.buttonClicked.connect(self.closeDialog)
            msg.exec_()                
        else:
            # Show error popup.
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("ID Number not in database!")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.buttonClicked.connect(self.closeDialog)
            msg.exec_()
            pass

    def makeIdCaps(self, ID):
        return ID.upper()

    def updateEntries(self):
        isOutsti = self.centralWidget.isOutstiField.isChecked()

        if isOutsti:
            idNum = "Outsti"
        else:
            idNum = self.centralWidget.idField.text()
            idNum = self.makeIdCaps(idNum)
            if not self.database.idValid(idNum):
                return 1

        tempDict = {
            "ID": idNum,
            "Clothes": [],
            "Rest": []
        }

        for entry in range(0, 5):
            itemName, itemSize = self.retrieveClothesItem(entry)
            if itemName and itemSize:
                fullItem = self.appendSizeToItem(itemName, itemSize)    
                tempDict["Clothes"].append(fullItem)
            try:
                itemName, itemQuantity = self.retrieveRestItem(entry)
            except ValueError:
                return 3
            if itemName and itemQuantity:
                fullItem = self.appendQuantityToItem(itemName, itemQuantity)    
                tempDict["Rest"].append(fullItem)
        if len(tempDict["Clothes"]) == 0 and len(tempDict["Rest"]) == 0:
            return 2
        self.appendToFile(tempDict)
        return 0

    def appendToFile(self, tempDict):
        file_path = 'data-entries.txt'
        with open(file_path, "a") as file:
            file.write(json.dumps(tempDict))

    def closeDialog(self):
        return

    def retrieveClothesItem(self, entry):
        try:
            itemName = self.centralWidget.clothesNameFields[entry].currentText()
            itemSize = self.centralWidget.clothesSizeFields[entry].currentText()
        except AttributeError as e:
            itemName = None
            itemSize = None
        return itemName, itemSize

    def retrieveRestItem(self, entry):
        try:
            itemName = self.centralWidget.restNameFields[entry].currentText()
            itemQuantity = self.centralWidget.quantityFields[entry].text()
        except AttributeError as e:
            itemName = None
            itemQuantity = None
        if itemQuantity == '':
            itemName = None
            itemQuantity = None
        if itemQuantity:
            val = int(itemQuantity)
        return itemName, itemQuantity

    def appendSizeToItem(self, item, size):
        itemSplit = item.split('-')
        itemSplit.insert(1, size)
        return '-'.join(itemSplit)
    
    def appendQuantityToItem(self, item, quantity):
        itemSplit = item.split('-')
        itemSplit.insert(1, quantity)
        return '-'.join(itemSplit)