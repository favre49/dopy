from PyQt5 import QtWidgets, QtCore, QtGui
import os, re

class propertiesWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        self.setupWidget()

    def setupWidget(self):

        self.database = self.parent.database
        self.numFields = self.parent.parent.configurator.propertiesWidgetNumFields
        self.setFixedHeight(self.parent.parent.configurator.propertiesWidgetHeight)
#############Gui Components
        self.doneButton = QtWidgets.QPushButton("Done")
        self.idHeader = QtWidgets.QLabel("ID No/Email")
        self.quantityHeader = QtWidgets.QLabel("Quantity")
        self.idFields = [QtWidgets.QLineEdit("") for i in range(self.numFields)]
        self.quantityFields = [QtWidgets.QSpinBox() for i in range(self.numFields)]
        for i in range(self.numFields): self.quantityFields[i].setMinimum(1)
        for i in range(self.numFields): self.quantityFields[i].setValue(1)

#validity = -1,0,1 and 2 for invalid,empty,validID,validEmail respectively
        self.validity = [0 for i in range(self.numFields)]
        self.nameLabel = QtWidgets.QLabel()
        self.nameLabel.setWordWrap(True)
        self.roomLabel = QtWidgets.QLabel()
        hboxes = [QtWidgets.QHBoxLayout() for i in range(self.numFields)]
        vbox = QtWidgets.QVBoxLayout(self)
        widget = QtWidgets.QWidget(self)
        widget.setLayout(vbox)
        scrollableArea = QtWidgets.QScrollArea(self)
        scrollableArea.setWidget(widget)
        scrollableArea.setWidgetResizable(True)

        for i in range(self.numFields):
            hboxes[i].addWidget(self.idFields[i])
            hboxes[i].addWidget(self.quantityFields[i])
            vbox.addLayout(hboxes[i])

        hbox0 = QtWidgets.QHBoxLayout()
        hbox0.addStretch(True)
        hbox0.addWidget(self.doneButton)

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.idHeader)
        hbox1.addWidget(self.quantityHeader)

        widgetLayout = QtWidgets.QVBoxLayout(self)
        widgetLayout.addLayout(hbox0)
        widgetLayout.addLayout(hbox1)
        widgetLayout.addWidget(scrollableArea)

        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addWidget(self.nameLabel)
        hbox3.addWidget(self.roomLabel)
        widgetLayout.addLayout(hbox3)

        self.setLayout(widgetLayout)

        ########tab order
        self.setTabOrder()

################Non Gui

        self.connectDataFields()
        QtWidgets.QApplication.instance().focusChanged.connect(self.onFocusUpdateLabels)

##############Keyboard shortcuts
        quantityIncreaseShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Up'), self)
        quantityDecreaseShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Down'), self)
        quantityIncreaseShortcut.activated.connect(self.quantityShortcutHandler(1))
        quantityDecreaseShortcut.activated.connect(self.quantityShortcutHandler(-1))

    def quantityShortcutHandler(self, change):
        def function():
            try:
                index = self.idFields.index(self.focusWidget())
            except:
                try:
                    index = self.quantityFields.index(self.focusWidget())
                except:
                    return None
            if change == 1:
                self.quantityFields[index].setValue(self.quantityFields[index].value() + 1)
            else:
                if self.quantityFields[index].value() > 1:
                    self.quantityFields[index].setValue(self.quantityFields[index].value() - 1)

        return function


#Upadate name and room labels, on focus change
    def onFocusUpdateLabels(self):
        try:
            widget = QtWidgets.QApplication.instance().focusWidget()
            if widget in self.idFields:
                index = self.idFields.index(widget)
            if widget in self.quantityFields:
                index = self.quantityFields.index(widget)
            widget = self.idFields[index]
            rec = self.database.idValid(widget.text())
            print(rec)
            if rec:
                name = rec[2]
                room = rec[4] + " " + rec[5]
                self.nameLabel.setText("{}".format(name))
                self.roomLabel.setText("{}".format(room))
            else:
                self.nameLabel.setText("")
                self.roomLabel.setText("")
        except:
            #happens when other widgets get focus
            pass

#Connect each field to the the corresponding slot
    def connectDataFields(self):
        for i in range(len(self.idFields)):
            self.idFields[i].textChanged.connect(self.dataEntryHandler(i))
            self.quantityFields[i].valueChanged.connect(self.dataEntryHandler(i))

    def setTabOrder(self):
        for i in range(len(self.idFields)-1): QtWidgets.QWidget.setTabOrder(self.idFields[i],self.idFields[i+1])

#refresh and update the contents of the widget
    def refresh(self):
        idList,self.parent.roll.getSnap().idList = self.parent.roll.getSnap().idList,[] #Backing up the idList for the snap
        self.parent.roll.getSnap().numCopies = 0
        self.parent.roll.getSnap().numFemales = 0
        emailList,self.parent.roll.getSnap().emailList = self.parent.roll.getSnap().emailList,[]
        for idField in self.idFields: idField.setText("")  #clearing all idfields
        for quantityField in self.quantityFields: quantityField.setValue(1)
        for validity in self.validity: validity = 0
        #add ids back to their respective indices
        for entry in idList:
            index = entry[0]
            id = entry[1]
            quantity = entry[2]
            self.idFields[index].setText(id)
            #print(index, id, quantity, self.validity[index])
            self.quantityFields[index].setValue(quantity)
            #print(index, id, quantity, self.validity[index])
        #add emails back to their respective indices
        for entry in emailList:
            index = entry[0]
            email = entry[1]
            self.idFields[index].setText(email)

#every time the feilds are manipulated, id/email lists are updated
    def dataEntryHandler(self, index):
        def function():
            self.idEntryHandler(index)
            self.emailEntryHandler(index)

            self.parent.leftWidget.updatePeopleInfo()  #As no of people/males/females can change here

            #mark as invalid, if not empty
            if self.validity[index] == 0 or self.validity[index] == -1:
                self.validity[index] = 0 if self.idFields[index].text() == "" else -1

            #change color
            if self.validity[index] == 0:
                #self.idFields[index].setStyleSheet(self.parent.parent.configurator.idFieldEmptyColour)#change to grey
                self.idFields[index].setStyleSheet("background-color:#3F4038")#change to grey
            elif self.validity[index] == -1:
                #self.idFields[index].setStyleSheet(self.parent.parent.configurator.idFieldInvalidColour)
                self.idFields[index].setStyleSheet("background-color:#C20417")#change to red
            else:
                #self.idFields[index].setStyleSheet(self.parent.parent.configurator.idFieldValidColour)
                self.idFields[index].setStyleSheet("background-color:#40a348")#change to green

        return function


    def idEntryHandler(self, index):

        #delete from idList if previously valid
        if self.validity[index] == 1:
            self.parent.roll.getSnap().deleteID(index)
            self.validity[index] = 0

        rec = self.database.idValid(self.idFields[index].text()) #get the details of the id
        if rec: #if valid id
            name = rec[2]
            room = rec[4] + " " + rec[5]
            gender = rec[3]

        if rec and not self.parent.roll.getSnap().idExists(rec[0]): #if id valid and not repeated
            self.validity[index] = 1
            self.nameLabel.setText("{}".format(name))
            self.roomLabel.setText("{}".format(room))
            self.parent.roll.getSnap().insertID(index, rec[0], self.quantityFields[index].value(), gender) #insert
            self.idFields[index].setStyleSheet("background-color:#40a348")#change colour of idField
        else:
            #change colour if idField
            if rec: #if id valid but repeated
                self.nameLabel.setText("{}".format(name))
                self.roomLabel.setText("{}".format(room))
            else: #if id invalid
                self.nameLabel.setText("")
                self.roomLabel.setText("")


    def emailEntryHandler(self, index):
        if self.parent.__class__.__name__ != "billingWidget":
            return None
        #print("check",self.validity)
        #delete from idList if previously valid
        #print("test", index, self.validity[index])
        if self.validity[index] == 2:
            self.parent.roll.getSnap().deleteEmail(index)
            self.validity[index] = 0

        email = self.idFields[index].text()
        #if email valid and not repeated, add to emailList
        if re.match('.+@.+\..+', email) and not self.parent.roll.getSnap().emailExists(email):
            self.validity[index] = 2
            self.parent.roll.getSnap().insertEmail(index, email)

        #Check outsiCheckBox for valid entry
        if(self.validity[index] == 2):
            self.parent.leftWidget.outsiCheckBox.setCheckState(QtCore.Qt.Checked)
