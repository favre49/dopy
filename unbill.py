from PyQt5 import QtWidgets, QtCore
import sys, os, tempfile, csv

import niggerFiles, propertiesWidget, leftWidgetUnbilling, displayWidget
import bill, chorePlay

class unbillingWidget(QtWidgets.QWidget):
    

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.roll = bill.Roll()
        self.database = parent.database
        self.path = ''
        self.billingList = []
        self.setupWidget()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        

    def setupWidget(self):

###########GUI
        self.propertiesWidget = propertiesWidget.propertiesWidget(self)
        self.propertiesWidget.idHeader.setText("ID")
        self.propertiesWidget.doneButton.setText("Unbill")
        self.leftWidget = leftWidgetUnbilling.leftWidget(self)
        self.displayWidget = displayWidget.displayWidget(self)
        self.searchWidget = niggerFiles.searchWidget(self)

        widgetLayout = QtWidgets.QHBoxLayout()

        widgetLayout.addWidget(self.leftWidget)
        widgetLayout.addWidget(self.displayWidget)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(self.propertiesWidget)
        vbox.addWidget(self.searchWidget)
        widgetLayout.addLayout(vbox)

        self.setLayout(widgetLayout)

################siganls
        for i in range(len(self.propertiesWidget.idFields)):
            self.propertiesWidget.idFields[i].textChanged.connect(self.updateBillingList)
            self.propertiesWidget.quantityFields[i].valueChanged.connect(self.updateBillingList)

        self.propertiesWidget.doneButton.clicked.connect(self.unbill)
        self.leftWidget.loadFolderButton.clicked.connect(self.loadNewFolder)

###############Keyboard Shortcuts
        returnKeyShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Return'), self)
        returnKeyShortcut.activated.connect(self.returnKeyShortcutHandler)

    def returnKeyShortcutHandler(self):
        if self.focusWidget() == self.searchWidget.searchField:
            self.searchWidget.populate()
        elif self.focusWidget() == self.leftWidget.navigatorField:
            self.leftWidget.populateTreeWidget()
        else:
            return None


    def loadNewFolder(self):
        trackedPathFile = open(os.getcwd() + os.sep + "resources" + os.sep
                               + "trackedPath.txt", "r")
        openFolder = os.path.expanduser('~')
        for line in trackedPathFile: openFolder = os.sep.join(line.split(os.sep)[:-1])
        self.path = QtWidgets.QFileDialog.getExistingDirectory(self, "Locate the Billed Folder", openFolder)
        trackedPathFile.close()
        if self.path == "": return None #FileDialog closed
        
        
        self.leftWidget.loadFolderLabel.setText(self.path)
        #try:
        self.billingList = chorePlay.readSnaps(self.path)
        #except:
            #print("exception")
            #self.billingList = []
        QtWidgets.QMessageBox.information(self, "Done!!!","Loaded!!!", QtWidgets.QMessageBox.Ok) 
        #print(self.billingList)
        

    def unbill(self):

        #password, result = QtWidgets.QInputDialog.getText(self, "Password Protection", "Password:", QtWidgets.QLineEdit.Password)
        #if not result:
            #return None
        #if not self.database.isPasswordValid("unbilling", password):
            #QtWidgets.QMessageBox.information(self, "Incorrect!!!","Incorrect Password Entered", QtWidgets.QMessageBox.Ok)
            #return None
        for entry in self.billingList:
            before = entry[3]
            after = entry[4]

            if before == after:
                continue

            tempSnapFile = tempfile.TemporaryFile()
            infile = open(entry[5], 'rb')
            bufferSize = 1000000
            buffer = infile.read(bufferSize)
            while len(buffer):
                tempSnapFile.write(buffer)
                buffer = infile.read(bufferSize)
            tempSnapFile.seek(0)
            infile.close()

            folders = os.listdir(self.path)
            for folder in folders:
                snaps = os.listdir(self.path + os.sep + folder)
                for snap in snaps:
                    snapName = "".join(snap.split('.')[:-1]) if len(snap.split('.')) > 1 else snap
                    if [entry[0], entry[2]] == [snapName.split("_")[2], snapName.split("_")[4]]:
                        os.remove(self.path + os.sep + folder + os.sep + snap)

            for i in range(after):
                rec = self.database.idValid(entry[2])
                snapExtension = entry[5].split('.')[-1] if len(entry[5].split('.')) > 1 else ""
                roomDetails = rec[4] + "_" + rec[5]
                if snapExtension:
                    outfile = open(self.path + os.sep + entry[1] + os.sep + roomDetails + "_" + entry[0] + "_" + str(i+1) + "_" + entry[2] + "." + snapExtension, 'wb')
                else:
                    outfile = open(self.path + os.sep + entry[1] + os.sep + roomDetails + "_" + entry[0] + "_" + str(i+1) + "_" + entry[2], 'wb')
                bufferSize = 1000000
                buffer = tempSnapFile.read(bufferSize)
                while len(buffer):
                    outfile.write(buffer)
                    buffer = tempSnapFile.read(bufferSize)
                tempSnapFile.seek(0)
                outfile.close()

            tempSnapFile.close()

        QtWidgets.QMessageBox.information(self, "Done!!!","Unbilled!!!", QtWidgets.QMessageBox.Ok)      

                    

    def updateBillingList(self):

        snap = self.roll.getSnap()
        deletedItem = snap.history[0]
        insertedItem = snap.history[1]

        if (deletedItem,insertedItem) == (None, None):
            pass

        elif insertedItem == None:
            index = [(tempRec[0], tempRec[2]) for tempRec in self.billingList].index((snap.name, deletedItem[1]))
            self.billingList[index][4] = 0

        else:
            try:
                index = [(tempRec[0], tempRec[2]) for tempRec in self.billingList].index((snap.name, insertedItem[1]))
                self.billingList[index][4] = insertedItem[2]
            except:
                index = [tempRec[0] for tempRec in self.billingList].index(snap.name)
                folderName = self.billingList[index][1]
                self.billingList.append([snap.name, folderName, insertedItem[1], 0, insertedItem[2], snap.path])
                
        snap.history = [None, None]

    def closeEvent(self, event):

        reply = QtWidgets.QMessageBox.question(self, 'Quit?',
            "Unsaved data will be lost.\nSure about it?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

        
        
                       
                


