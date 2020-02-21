from PyQt5 import QtCore, QtWidgets
import sys, os, re
import bill, propertiesWidget, niggerFiles


class leftWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        self.setupWidget()
        self.database = self.parent.database

    def setupWidget(self):

############GUI components
        
        self.loadFolderButton = QtWidgets.QPushButton("Load Folder")
        self.loadFolderLabel = QtWidgets.QLabel(r"Choose folder to bill")
        self.loadFolderLabel.setWordWrap(True)
        self.snapInfoLabel = QtWidgets.QLabel()
        self.peopleInfoLabel = QtWidgets.QLabel()
        self.navigatorLabel = QtWidgets.QLabel("Find snaps by ID/Roll No")
        self.navigatorField = QtWidgets.QLineEdit()
        self.navigatorButton = QtWidgets.QPushButton("Find")
        self.navigator = QtWidgets.QTreeWidget()
        self.navigator.setFixedHeight(self.parent.parent.configurator.unbillingTableHeight)
        self.loadSnapsButton = QtWidgets.QPushButton("Load Snap(s)")

        self.navigator.setColumnCount(1)
        self.navigatorHeaderItem = QtWidgets.QTreeWidgetItem()
        self.navigatorHeaderItem.setText(0, "Snaps")
        self.navigator.setHeaderItem(self.navigatorHeaderItem)

        
#################Layout
        widgetLayout = QtWidgets.QVBoxLayout()
        widgetLayout.addWidget(self.loadFolderButton)
        widgetLayout.addWidget(self.loadFolderLabel)
        widgetLayout.addStretch(True)
        widgetLayout.addWidget(self.snapInfoLabel)
        widgetLayout.addStretch(True)
        widgetLayout.addWidget(self.peopleInfoLabel)
        widgetLayout.addStretch(True)
        widgetLayout.addWidget(self.navigatorLabel)
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.navigatorField)
        hbox.addWidget(self.navigatorButton)
        widgetLayout.addLayout(hbox)
        widgetLayout.addWidget(self.navigator)
        widgetLayout.addWidget(self.loadSnapsButton)
        self.setLayout(widgetLayout)
        self.show()

##################Signals
        self.navigatorButton.clicked.connect(self.populateTreeWidget)
        self.loadSnapsButton.clicked.connect(self.loadSnaps)
        self.navigator.itemDoubleClicked.connect(self.loadSnaps)


    def refresh(self):
        self.updateSnapInfo()
        self.updatePeopleInfo()
        print(self.parent.roll.getSnap().numFemales, self.parent.roll.getSnap().numCopies)
    
    def updateSnapInfo(self):
        self.snapInfoLabel.setText("{}\n\nDisplaying: {} of {}\n".format(self.parent.roll.name,self.parent.roll.currentPos + 1, self.parent.roll.numSnaps))

    def updatePeopleInfo(self):
        numPeople = self.parent.roll.getSnap().numCopies
        numFemales = self.parent.roll.getSnap().numFemales
        numMales = numPeople - numFemales
        self.peopleInfoLabel.setText("People: {}\n{}-M | {}-F\n".format(numPeople, numMales, numFemales))
    
    def populateTreeWidget(self):

        #print("populating")

        def getFormat(text):
            print(self.database.idValid(text))

            if self.database.hostelValid(text):
                #print("check1")
                #print("len1", len(self.database.hostelValid(text)))
                return -1

            if self.database.roomValid(text):
                return 0
            
            if self.database.idValid(text):
                return 1

            elif re.match('[0-9]+[Rr]', text):
                return 2

            else: return 3

        text = self.navigatorField.text()
        format_ = getFormat(text)
        print("format=", format_)

        list_ = []

        if format_ == -1 or format_ == 0 :
            #print("???!!", format_)
            if format_ == -1:
                idNos = self.database.hostelValid(text)
                #print("check2")
                #print("len2", len(idNos))
            else:
                idNos = self.database.roomValid(text)
            #print(idNos)
            for id_ in idNos:
                idNo = id_[0]
                for rec in self.parent.billingList:
                    if idNo == rec[2]:
                        try:
                            i = [tempRec[0] for tempRec in list_].index(rec[1])
                            list_[i][1].append(rec[0])
                        except:
                            list_.append((rec[1],[rec[0],]))
        
        if format_ == 1:
            idNo = self.database.idValid(text)[0]
            for rec in self.parent.billingList:
                if idNo == rec[2]:
                    try:
                        i = [tempRec[0] for tempRec in list_].index(rec[1])
                        list_[i][1].append(rec[0])
                    except:
                        list_.append((rec[1],[rec[0],]))


        else:
            print("else loop")
            if format_ == 2:
                text = (text.split('R')[0]) if 'R' in text else (text.split('r')[0])
                print(55555555)
            #print(self.parent.billingList)
            for rec in self.parent.billingList:
                if text == rec[1] or (text+'R' == rec[1]) or (text+'r' == rec[1]):
                    try:
                        #print("try")
                        i = [tempRec[0] for tempRec in list_].index(rec[1])
                        if rec[0] not in list_[i][1]: list_[i][1].append(rec[0])
                    except:
                        #print("except")
                        list_.append((rec[1],[rec[0],]))

        if not list_:
            for rec in self.parent.billingList:
                if text == rec[0]:
                    try:
                        i = [tempRec[0] for tempRec in list_].index(rec[1])
                        if rec[0] not in list_[i][1]: list_[i][1].append(rec[0])
                    except:
                        list_.append((rec[1],[rec[0],]))

                
        self.navigator.clear()
        #print(list_)

        for folderName in list_:
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, folderName[0])
            for snapName in folderName[1]:
                childItem = QtWidgets.QTreeWidgetItem()
                childItem.setText(0, snapName)
                item.addChild(childItem)
                item.sortChildren(0, QtCore.Qt.AscendingOrder)
            self.navigator.addTopLevelItem(item)

    

    def loadSnaps(self):
        def loadRoll():
            #Sprint("loading Roll")
            try:
                item = self.navigator.currentItem()
                collectionName = item.text(0)
                #print("collectionName", collectionName)
                list_ = []
                parent = item.parent()
                if parent == None:
                    for i in range(item.childCount()):
                        index = [tempRec[0] for tempRec in self.parent.billingList].index(item.child(i).text(0))
                        list_.append((self.parent.billingList[index][0],self.parent.billingList[index][5]))
                    
                else:
                    index = [tempRec[0] for tempRec in self.parent.billingList].index(item.text(0))
                    list_.append((self.parent.billingList[index][0],self.parent.billingList[index][5]))
                #print("list: ",list_)
            except:
                #print("exceptionnnnnnnnnnnnnnhagu")
                collectionName = self.navigatorField.text()
                list_ = []
                for i in range(self.navigator.topLevelItemCount()):
                    for j in range(self.navigator.topLevelItem(i).childCount()):
                        index = [tempRec[0] for tempRec in self.parent.billingList].index(self.navigator.topLevelItem(i).child(j).text(0))
                        list_.append((self.parent.billingList[index][0],self.parent.billingList[index][5]))
                

            #print("roll assign start")
            self.parent.roll = bill.Roll(None, collectionName, list_)
            #print("roll assign over")

        progress = niggerFiles.customProgressWidget1()
        progress.headerLabel.setText("Loading Snaps")
        progress.bar.setRange(0,self.parent.roll.numSnaps)
        progress.messageLabel.setText("Loading {} of {} snaps".format(0,self.parent.roll.numSnaps))
        progress.bar.setValue(0)
        progress.show()
        loadRoll()
        progress.bar.setRange(0,self.parent.roll.numSnaps)
        progress.messageLabel.setText("Loading {} of {} snaps".format(1,self.parent.roll.numSnaps))

        for i, snap in enumerate(self.parent.roll.snapList):
            for rec in self.parent.billingList:
                if snap.name == rec[0]:
                    rec2 = self.database.idValid(rec[2])
                    gender = rec2[3]
                    id = rec2[0]
                    quantity = rec[4]
                    snap.insertID(len(snap.idList),id,quantity, gender)
            progress.bar.setValue(progress.bar.value() + 1)
            progress.messageLabel.setText("Loading {} of {} snaps".format(i+2,self.parent.roll.numSnaps))       
                    
        #self.parent.propertiesWidget.refresh()

        #print(self.parent.roll.currentPos,self.parent.roll.snapList)
        #print("checking..............")
        #for i,snap in enumerate(self.parent.roll.snapList):
            #print("Total:", snap.numCopies)
            #print("Females:", snap.numFemales)
            #for id in snap.idList: print(id)
        self.parent.displayWidget.loadSnap()
        self.parent.propertiesWidget.refresh()
        self.refresh()
        
            
            
            
        

        
        
            
        

#app = QtWidgets.QApplication(sys.argv)
#s = leftWidget()
#app.exec_()
