from PyQt5 import QtWidgets, QtCore, QtGui
import sys, os, re
import chorePlay, niggerFiles, propertiesWidget, leftWidget, displayWidget
from operator import itemgetter


#Class for snaps
class Snap:

    def __init__(self, name, path = None):
        self.name = name #name plus extension of image file
        self.path = path  #not used in billing
        self.numCopies = 0
        self.numFemales = 0
        self.idList = [] #(index,(id(shorthand notation), copies, gender) )
        self.emailList = [] #(index, emailID)
        self.outsi = False #holds no of outsi snaps, if snap is marked outsi
        self.dept = False #holds dept name if snap is marked dept
        self.history = [None, None]#Keeps track of deletions and insertions

    def idExists(self, id):
        return True if id in [self.idList[i][1] for i in range(len(self.idList))] else False

    #append entry the end of idList
    def insertID(self, index, id,  copies, gender):
        self.idList.append((index,id,copies, gender))
        self.numCopies+=copies
        if gender == 'F':
            self.numFemales+=copies
        self.history[1] = (index,id,copies, gender)

    #delete entry from idList, with given index, if it exists
    def deleteID(self, index):
        #print("deleting")
        for i in range(len(self.idList)):
            if index == self.idList[i][0]:
                if self.idList[i][3] == 'F':
                    self.numFemales-=self.idList[i][2]
                self.numCopies-=self.idList[i][2]
                self.history[0] = self.idList.pop(i)
                return None

    def emailExists(self, email):
        return True if email in self.emailList else False

    def insertEmail(self, index, email):
        self.emailList.append((index,email))

    def deleteEmail(self, index):
        #print("deleting email")
        for i in range(len(self.emailList)):
            print(index, self.emailList[i][0])
            if index == self.emailList[i][0]:
                self.emailList.pop(i)
                return None

#iterator class for a collection of snaps
#initialize it with the path of the folder or a list of image paths
class Roll:

    def __init__(self, path = None, listName = None, snapList = None):
        self.path = path # Not to be used if the snaps are in different folders
        self.snapList = []

        #Option 1 of 2: folder path is provided
        try:
            self.name = "N/A" if path == None else path.split("\\")[-1] #folder name
            #print("123", path, self.name)
            if path != None:
            #Load all snaps to snapList. Note that unsupported formats, text files and folders will all be loaded
                self.snapList = [Snap(_file) for _file in os.listdir(path)]

            else:
                #print("else")
                self.snapList = []
        except:
            self.name = "invalid path"
        #Option 2 of 2: If list of snap paths is provided
        try:
            if listName != None: self.name = listName
            if snapList != None:
                #print(listName, snapList)
                self.snapList = []
                for entry in snapList:
                    snapName = entry[0]
                    snapPath = entry[1]
                    self.snapList.append(Snap(snapName, snapPath))
        except:
            self.name = "invalid path"

        self.numSnaps = len(self.snapList)
        self.currentPos = 0 #current snap no

    def reset(self):
        self.currentPos = 0

    def hasPrevious(self):
        return True if 0 < self.currentPos else False

    def hasNext(self):
        return True if self.currentPos < self.numSnaps - 1 else False

    def getSnap(self, difference = 0):
        return self.snapList[self.currentPos + difference]


class billingWidget(QtWidgets.QWidget):


    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.roll = Roll()
        self.database = parent.database
        self.setupWidget()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)


    def setupWidget(self):

###########GUI components
        self.propertiesWidget = propertiesWidget.propertiesWidget(self)
        self.leftWidget = leftWidget.leftWidget(self)
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

#############Signals
        self.propertiesWidget.doneButton.clicked.connect(self.doneButtonHandler)

#############Keyboard shortcuts
        returnKeyShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Return'), self)
        returnKeyShortcut.activated.connect(self.returnKeyShortcutHandler)

    def returnKeyShortcutHandler(self):
        if self.focusWidget() == self.searchWidget.searchField:
            self.searchWidget.populate()
        elif self.focusWidget() == self.leftWidget.sameAsField:
            self.leftWidget.sameAsButtonHandler()
        elif self.focusWidget() == self.leftWidget.loadIDsComboBox:
            self.leftWidget.loadIDsFromFile()
        else:
            return None

    def doneButtonHandler(self):
        result = chorePlay.resizeAndSave(self)
        if result:
            self.loadNewFolder()

    def loadNewFolder(self):
            trackedPathFile = open(os.getcwd() + os.sep + "resources" + os.sep
                               + "trackedPath.txt", "r+")
            openFolder = os.path.expanduser('~')
            for line in trackedPathFile: openFolder = os.sep.join(line.split(os.sep)[:-1])
            path = QtWidgets.QFileDialog.getExistingDirectory(self, "Locate the Folder to bill", openFolder)
            if path == "": return None #FileDialog closed
            trackedPathFile.seek(0)
            trackedPathFile.write(path)
            trackedPathFile.truncate()
            trackedPathFile.close()
            
            chorePlay.rename(self, path)

            self.leftWidget.loadFolderLabel.setText(path)
            self.roll = Roll(path)
            self.displayWidget.loadSnap()
            self.propertiesWidget.refresh()
            self.searchWidget.refresh()
            self.leftWidget.refresh()
            self.leftWidget.deptNameComboBox.updateDeptList()

    def closeEvent(self, event):

        reply = QtWidgets.QMessageBox.question(self, 'Quit?',
            "Unsaved data will be lost.\nSure about it?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
