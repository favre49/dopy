from PyQt5 import QtWidgets, QtCore
import sys, os, re
from operator import itemgetter
import niggerFiles

class sendToPrinter(QtWidgets.QWidget):
    

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.setupWidget()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowFlags(QtCore.Qt.Window)
        self.show()
        
    def setupWidget(self):

###########GUI components
        self.setWindowTitle("Send 2 Printer")
        self.move(400,100)
        self.resize(400,500)
        self.availableRollsViewer = QtWidgets.QTableWidget(0,1)
        self.availableRollsViewer.setHorizontalHeaderLabels(["Available Rolls"])
        self.availableRollsViewer.horizontalHeader().setStretchLastSection(True)
        self.availableRollsViewer.setFixedWidth(300)
        
        self.sentRollsViewer = QtWidgets.QTableWidget(0,1)
        self.sentRollsViewer.setHorizontalHeaderLabels(["Rolls Sent Previously"])
        self.sentRollsViewer.horizontalHeader().setStretchLastSection(True)
        self.sentRollsViewer.setFixedWidth(300)
        
        self.availableRolls = []
        self.sentRolls = []
        self.loadFolderButton = QtWidgets.QPushButton("Load Folder")        
        self.saveButton = QtWidgets.QPushButton("Sort and Save")

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addStretch(True)
        hbox1.addWidget(self.availableRollsViewer)
        hbox1.addWidget(self.sentRollsViewer)
        hbox1.addStretch(True)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch(True)
        hbox2.addWidget(self.loadFolderButton)
        hbox2.addWidget(self.saveButton)
        hbox2.addStretch(True)
        widgetLayout = QtWidgets.QVBoxLayout(self)
        widgetLayout.addLayout(hbox1)
        widgetLayout.addLayout(hbox2)

################siganls

        self.saveButton.clicked.connect(self.sortAndSave)
        self.loadFolderButton.clicked.connect(self.loadNewFolder)

    def sortAndSave(self):
        try:
            folders = os.listdir(self.path)
        except:
            return None
        count = 0
        for i in range(self.availableRollsViewer.rowCount()):
            if self.availableRollsViewer.cellWidget(i,0).isChecked():
                count += 1
        if count == 0:
            return None
        path = os.sep.join(self.path.split(os.sep)[:-1]) + os.sep + "Sent for Printing"
        print(path)
        try:
            sentFolders = os.listdir(path)
        except:
            os.mkdir(path)
            sentFolders = []
        num = 0 
        for i in range(len(sentFolders)):
            num = max(num, int(sentFolders[i].split('S')[0]))
        num += 1
        path += os.sep + str(num) + "S"
        os.mkdir(path)
        
        snapList = []
        for i in range(self.availableRollsViewer.rowCount()):
            entry = self.availableRolls[i]
            widget = self.availableRollsViewer.cellWidget(i,0)
            print(widget)
            if widget.isChecked():
                snapList.extend([[snapName, entry[1]]for snapName in os.listdir(self.path + os.sep + entry[1])])
        hostelList = []
        self.progress = niggerFiles.customProgressWidget1()
        self.progress.headerLabel.setText("Copying Snaps")
        self.progress.bar.setRange(0,len(snapList))
        self.progress.messageLabel.setText("Copying snap {} of {}".format(0,len(snapList)))
        self.progress.bar.setValue(self.progress.bar.value() + 1)
        self.progress.show()
        for i,snap in enumerate(snapList):
            self.progress.messageLabel.setText("Copying snap {} of {}".format(i+1,len(snapList)))
            self.progress.bar.setValue(self.progress.bar.value() + 1)
            hostelName = snap[0].split('_')[0]
            if hostelName not in hostelList:
                print(hostelName, hostelList)
                
                hostelList.append(hostelName)
                os.mkdir(path + os.sep + hostelName)
            bufferSize = 1000000
            infile = open(self.path + os.sep + snap[1] + os.sep + snap[0], 'rb')
            outfile = open(path + os.sep + hostelName + os.sep + snap[0], 'wb')
            buffer = infile.read(bufferSize)
            while len(buffer):
                outfile.write(buffer)
                buffer = infile.read(bufferSize)
            infile.close()
            outfile.close()
            
        self.progress.close()
        if len(self.availableRolls) > 0:
            QtWidgets.QMessageBox.information(self, "Message", "Snaps successfilly copied", QtWidgets.QMessageBox.Ok)
            
            

    def loadNewFolder(self):
        tempPath = QtWidgets.QFileDialog.getExistingDirectory(self, "Locate the Billed Snaps Folder")
        if tempPath == "": return None #FileDialog closed
        else: self.path = tempPath
#####populating available rolls
        
        for i in range(self.availableRollsViewer.rowCount()):
            self.availableRollsViewer.removeRow(0)
        for i in range(self.sentRollsViewer.rowCount()):
            self.sentRollsViewer.removeRow(0)
        self.availableRolls = []


        pattern = re.compile('[0-9]+[Rr]')
        folders = os.listdir(self.path)
        
        for folderName in folders:
            if re.match(pattern, folderName):
                num = int(folderName.split('R')[0]) if 'R' in folderName else int(folderName.split('r')[0])
            #else:
                #num = 10000
            self.availableRolls.append((num, folderName))
        self.availableRolls.sort(key = itemgetter(0,1))

        for i,roll in enumerate(self.availableRolls):
            cellWidget = QtWidgets.QCheckBox(roll[1])
            self.availableRollsViewer.insertRow(i)
            #listWidgetItem.setFlags(QtCore.Qt.NoItemFlags)
            self.availableRollsViewer.setCellWidget(i,0,cellWidget)
#####populating sent rolls
        path = os.sep.join(self.path.split(os.sep)[:-1]) + os.sep + "Sent for Printing"
        self.sentRolls = []
        try:
            sentFolders = os.listdir(path)
        except:
            os.mkdir(path)
            sentFolders = os.listdir(path)
        
        billedFolders = os.listdir(self.path)
        for billedFolder in billedFolders:
            if not re.match(pattern, billedFolder):
                continue
            billedSnaps = os.listdir(self.path + os.sep + billedFolder)
            if len(billedSnaps):
                checkSnap = billedSnaps[0]
                sentFolders1 = os.listdir(path)
                try:
                    for folder1 in sentFolders1:
                        sentFolders2 = os.listdir(path + os.sep + folder1)
                        for folder2 in sentFolders2:
                            snapList = os.listdir(path + os.sep + folder1 + os.sep + folder2)
                            if checkSnap in snapList:
                                if re.match(pattern, billedFolder):
                                    num = int(billedFolder.split('R')[0]) if 'R' in billedFolder else int(billedFolder.split('r')[0])
                                else:
                                    num = 10000
                                self.sentRolls.append((num,billedFolder))
                                raise NameError
                except NameError:
                    pass
        
        self.sentRolls.sort(key = itemgetter(0,1))
        for i,roll in enumerate(self.sentRolls):
            cellWidget = QtWidgets.QLabel(roll[1])
            self.sentRollsViewer.insertRow(i)
            self.sentRollsViewer.setCellWidget(i,0,cellWidget)
                
        self.availableRollsViewer.setVerticalHeaderLabels(["" for i in range(self.availableRollsViewer.rowCount())])
        self.sentRollsViewer.setVerticalHeaderLabels(["" for i in range(self.sentRollsViewer.rowCount())])

#app = QtWidgets.QApplication(sys.argv)
#c = sendToPrinter()
#app.exec_()
