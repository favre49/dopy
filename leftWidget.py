from PyQt5 import QtCore, QtWidgets, QtGui
import sys, os


class customComboBox(QtWidgets.QComboBox):

    def __init__(self, name, parent=None): 

        QtWidgets.QComboBox.__init__(self)

        self.parent = parent
        self.name = name
        self.model = QtCore.QStringListModel()
        self.deptList = ["DoPy", "A1 Assoc", "A2 Assoc", "A3 Assoc", "A4 Assoc/MEA", "A5 Assoc", "A7 Assoc/CSA", "A8 Assoc", "ACM", "AcYut", "ADP",
                         "ArBITS", "AstroClub", "AudiForce", "B1 Assoc ", "B2 Assoc", "B3 Assoc/ EFA", "B5 Assoc", "BAJA", "B4 Assoc", "Backstage",
                         "BITSMUN", "BOSM Sponz", "CrAC", "Dance Club", "DebSoc", "DoT", "DVM", "EDC", "ELAS", "EPC", "Film Making Club", "Firewallz",
                         "FS", "HAS", "HDC", "HPC", "Informalz", "Jhankar" "Lights", "Matrix", "MIMEs", "Music Club", "Nirmaan", "NSS", "PCr", "PCr APOGEE",
                         "Photog", "Poetry Club", "Raagmalika", "RC", "PEP", "Rec N Acc", "Soundz", "Sponz", "Wall Street Club"]


        self.IDsList = []

        try:
            list_ = os.listdir(os.getcwd() + os.sep + "WorkForce Lists")
            for entry in list_:
                self.IDsList.append(entry)
        except:
            print("error in Load IDs combo")

        if self.name == "departmentComboBox": 
            self.model.setStringList(self.deptList)
            self.addItems(self.deptList)

        elif self.name == "loadIDsComboBox":
            self.model.setStringList(self.IDsList)
            self.addItems(self.IDsList)
        
        self.setEditable(True)
        
        self.completer = CustomQCompleter(self)
        self.completer.setModel(self.model)
        

        self.setCompleter(self.completer)
        self.setEditText('')

        self.setGeometry(200, 100, 400, 300)

    def updateDeptList(self):
        try:
            list_ = os.listdir("\\".join(self.parent.parent.roll.path.split("\\")[:-2]) + "\\Departments")
            #print(list_)
            for entry in list_:
                tag = 1
                for dept in self.deptList:
                    if dept.lower() == entry.lower(): tag = 0
                if tag == 1: self.deptList.append(entry)
            self.clear()
            self.model.setStringList(self.deptList)
            self.addItems(self.deptList)
            self.setEditText('')
        except:
            print("error in department combo")

    def addToDeptList(self, entry):
        if entry == "": return None
        for dept in self.deptList:
            if dept.lower() == entry.lower(): return None
        self.deptList.append(entry)
        self.model.setStringList(self.deptList)
        self.addItem(entry)
        self.setEditText('')
        

class CustomQCompleter(QtWidgets.QCompleter):
    def __init__(self, parent=None):
        super(CustomQCompleter, self).__init__(parent)
        self.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.setCompletionMode(QtWidgets.QCompleter.UnfilteredPopupCompletion)
        self.setWrapAround(False)                                                        
        self.local_completion_prefix = ""
        self.source_model = None
                                                        
    def setModel(self, model):
        self.source_model = model
        super(CustomQCompleter, self).setModel(self.source_model)

    def updateModel(self):
        local_completion_prefix = self.local_completion_prefix
        class InnerProxyModel(QtWidgets.QSortFilterProxyModel):
            def filterAcceptsRow(self, sourceRow, sourceParent):
                index0 = self.sourceModel().index(sourceRow, 0, sourceParent)
                searchStr = local_completion_prefix.lower()
                modelStr = str(self.sourceModel().data(index0,QtCore.Qt.DisplayRole)).lower()
                return searchStr in modelStr
        proxy_model = InnerProxyModel()
        proxy_model.setSourceModel(self.source_model)

        super(CustomQCompleter, self).setModel(proxy_model)
        cr=QtCore.QRect(QtCore.QPoint(1, 1), QtCore.QSize(1, 1))
        self.complete(cr)


    def splitPath(self, path):
        self.local_completion_prefix = str(path)
        self.updateModel()
        return ""


class leftWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        self.setupWidget()

    def setupWidget(self):

        #Constants
        edgeSize = self.parent.parent.configurator.leftWidgetSnapViewerSize
        self.snapViewerSize = QtCore.QSize(edgeSize,edgeSize)
        self.textureImagePath = self.parent.parent.configurator.displayWidgetBackgroundTexture

############GUI components
        
        self.loadFolderButton = QtWidgets.QPushButton("Load Folder")
        self.loadFolderLabel = QtWidgets.QLabel(r"Choose folder to bill")
        self.loadFolderLabel.setWordWrap(True)

        self.snapInfoLabel = QtWidgets.QLabel()
        self.peopleInfoLabel = QtWidgets.QLabel()

        self.deptCheckBox = QtWidgets.QCheckBox("Dept")
        self.deptNameComboBox = customComboBox("departmentComboBox", self)
        self.sameAsButton = QtWidgets.QPushButton("Same As")
        self.sameAsField = QtWidgets.QLineEdit("")
        self.loadIDsComboBox = customComboBox("loadIDsComboBox")
        self.loadIDsButton = QtWidgets.QPushButton("Load IDs")
        self.outsiCheckBox = QtWidgets.QCheckBox("Outsi")
        self.outsiQuantity = QtWidgets.QSpinBox()
        self.outsiQuantity.setValue(1)
        self.outsiQuantity.setMinimum(1)

        self.previousSnapLabel = QtWidgets.QLabel("Previous:")
        self.nextSnapLabel = QtWidgets.QLabel("Next:")
        self.previousSnapViewer = QtWidgets.QLabel()
        self.nextSnapViewer = QtWidgets.QLabel()
        self.previousSnapViewer.setPixmap(QtGui.QPixmap().scaled(self.snapViewerSize))
        self.nextSnapViewer.setPixmap(QtGui.QPixmap().scaled(self.snapViewerSize))

###############Layouts
        
        widgetLayout = QtWidgets.QVBoxLayout()
        widgetLayout.addWidget(self.loadFolderButton)
        widgetLayout.addWidget(self.loadFolderLabel)
        widgetLayout.addStretch(True)
        widgetLayout.addWidget(self.snapInfoLabel)
        widgetLayout.addWidget(self.peopleInfoLabel)
        widgetLayout.addStretch(True)

        widgetLayout.addWidget(self.previousSnapLabel)
        widgetLayout.addWidget(self.previousSnapViewer)
        widgetLayout.addStretch(True)

        widgetLayout.addWidget(self.nextSnapLabel)
        widgetLayout.addWidget(self.nextSnapViewer)
        widgetLayout.addStretch(True)

        self.toolsBox = QtWidgets.QGroupBox("Tools")
        layout = QtWidgets.QVBoxLayout(self.toolsBox)

        hbox0 = QtWidgets.QHBoxLayout()
        hbox0.addWidget(self.outsiCheckBox)
        hbox0.addWidget(self.outsiQuantity)
        layout.addLayout(hbox0)
        layout.addStretch(True)
        
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.deptCheckBox)
        hbox1.addWidget(self.deptNameComboBox)
        layout.addLayout(hbox1)
        layout.addStretch(True)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.loadIDsComboBox)
        hbox2.addWidget(self.loadIDsButton)
        layout.addLayout(hbox2)
        layout.addStretch(True)
        
        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addWidget(self.sameAsField)
        hbox3.addWidget(self.sameAsButton)
        layout.addLayout(hbox3)
        layout.addStretch(True)
        widgetLayout.addWidget(self.toolsBox)
        
        self.setLayout(widgetLayout)

#######################NonGui
        
        self.loadFolderButton.clicked.connect(self.parent.loadNewFolder)
        self.deptNameComboBox.editTextChanged.connect(self.toggleDeptCheckBox)
        self.deptNameComboBox.editTextChanged.connect(self.isDeptHandler)
        self.sameAsButton.clicked.connect(self.sameAsButtonHandler)
        self.deptCheckBox.stateChanged.connect(self.isDeptHandler)
        self.outsiCheckBox.stateChanged.connect(self.isOutsiHandler)
        self.outsiQuantity.valueChanged.connect(self.isOutsiHandler)
        self.loadIDsButton.clicked.connect(self.loadIDsFromFile)

#Mark/unmark snap as dept. Store the dept name
    def isDeptHandler(self):
        dept = self.deptNameComboBox.currentText()
        if dept == "": dept = "misc"
        if self.deptCheckBox.isChecked(): self.parent.roll.getSnap().dept = dept
        else: self.parent.roll.getSnap().dept = False

#Mark/unmark snap as outsi. Store the quantity
    def isOutsiHandler(self):
        if self.outsiCheckBox.isChecked(): self.parent.roll.getSnap().outsi = self.outsiQuantity.value()
        else: self.parent.roll.getSnap().outsi = False
        print("outsi1006", self.parent.roll.getSnap().outsi)


#copies all the ids of the specified snap to the properties widget of the current
#Incase there are less no of empty fields, it copies as many as possible
    def sameAsButtonHandler(self):
        try:
            idList = self.parent.roll.snapList[int(self.sameAsField.text()) - 1].idList #idList from source snap
            num = 0 #for iterating through idList
            for i, textField in enumerate(self.parent.propertiesWidget.idFields):
                    if textField.text() == "":
                        textField.setText(idList[num][1])
                        self.parent.propertiesWidget.quantityFields[i].setValue(1)
                        num += 1
        except:
            #happens on successful completion, and for invalid entry in text field
            pass

#When deptNameComboBox is edited toggle deptCheckBox
    def toggleDeptCheckBox(self):
        if self.deptNameComboBox.currentText() == "": self.deptCheckBox.setCheckState(QtCore.Qt.Unchecked)
        else: self.deptCheckBox.setCheckState(QtCore.Qt.Checked)

#refresh and update the widget contents
    def refresh(self):
        self.updateSnapInfo()
        self.updatePeopleInfo()

        #sameAsFeild set to default value: current snap - 1 
        if self.parent.roll.hasPrevious():self.sameAsField.setText(str(self.parent.roll.currentPos))
        else: self.sameAsField.setText("")
        snap = self.parent.roll.getSnap()

        #update outsi checkBox and quantity fields
        print("outsi1007", snap.outsi)
        if snap.outsi:
            print(snap.outsi)
            self.outsiQuantity.setValue(snap.outsi)
            print(snap.outsi)
            self.outsiCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.outsiCheckBox.setCheckState(QtCore.Qt.Unchecked)
            self.outsiQuantity.setValue(1)

        #add new keyword to dept List of deptNameComboBox
        self.deptNameComboBox.addToDeptList(self.deptNameComboBox.currentText())
        
        #update dept checkBox and combo fields
        if snap.dept:
            self.deptNameComboBox.setEditText(snap.dept)
            self.deptCheckBox.setCheckState(QtCore.Qt.Checked)
        else:
            self.deptNameComboBox.setEditText("")
            self.deptCheckBox.setCheckState(QtCore.Qt.Unchecked)

        
    

    def updateSnapInfo(self):
        
        self.snapInfoLabel.setText("{}\n\nDisplaying: {} of {}\n".format(self.parent.roll.name,self.parent.roll.currentPos + 1, self.parent.roll.numSnaps))

        if self.parent.roll.hasPrevious():
            self.previousSnapLabel.setText("Previous: {} people".format(self.parent.roll.getSnap(-1).numCopies))
            self.previousSnapViewer.setPixmap(QtGui.QPixmap(self.parent.roll.path + "\\" + self.parent.roll.getSnap(-1).name).scaled(self.snapViewerSize))
        else:
            self.previousSnapLabel.setText("Previous:")
            self.previousSnapViewer.setPixmap(QtGui.QPixmap(self.textureImagePath).scaled(self.snapViewerSize))

        if self.parent.roll.hasNext():
            self.nextSnapLabel.setText("Next: {} people".format(self.parent.roll.getSnap(1).numCopies))
            self.nextSnapViewer.setPixmap(QtGui.QPixmap(self.parent.roll.path + "\\" + self.parent.roll.getSnap(1).name).scaled(self.snapViewerSize))
        else:
            self.nextSnapLabel.setText("Next:")
            self.previousSnapViewer.setPixmap(QtGui.QPixmap(self.textureImagePath).scaled(self.snapViewerSize))                         
    

    def updatePeopleInfo(self):

        numPeople = self.parent.roll.getSnap().numCopies
        numFemales = self.parent.roll.getSnap().numFemales
        numMales = numPeople - numFemales
        self.peopleInfoLabel.setText("People: {}\n{}-M | {}-F\n".format(numPeople, numMales, numFemales))

#Read a text file a copy the ids onto the properties widget
    def loadIDsFromFile(self):
        try:
            idList = []
            
            infile = open(os.getcwd() + os.sep + "WorkForce Lists" + os.sep + self.loadIDsComboBox.currentText(), 'r')
            for id in infile: idList.append(id.strip())
            #print(idList)
            num = 0
            for i, textField in enumerate(self.parent.propertiesWidget.idFields):
                    if textField.text() == "":
                        textField.setText(idList[num])
                        self.parent.propertiesWidget.quantityFields[i].setValue(1)
                        num += 1
        except:
            #happens on successful completion, and file i/o errors
            pass
   
