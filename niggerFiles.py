from PyQt5 import QtWidgets, QtCore, QtGui
import os, csv, sqlite3
import chorePlay


class Students:

    def __init__(self, databasefilepath):

        try:
            self.db = sqlite3.connect(databasefilepath)
            self.cursor = self.db.cursor()
            self.data = self.getData()
        except:
            print("error")
            self.data = {}

    def checkDatabase(self):
        try:
            self.cursor.execute("select * from studrec")
            num1 = len(self.cursor.fetchall())
            self.cursor.execute("select * from nicks")
            num2 = len(self.cursor.fetchall())
            self.cursor.execute("select * from passwords")
            boolean = True if len(self.cursor.fetchall()) == 2 else False
            return (num1, num2, boolean)
        except Exception as e:
            print("Database check failed:", str(e))
            return 0

    def getData(self):

        list = self.cursor.execute("select * from studrec")
        shorthandList = []
        idList = []
        dataList = []
        for rec in list:
            try:
                char = rec[1][4]
            except:
                continue
            sh = lambda record: str(record[1][2:4] + record[1][-4:])
            if "A" <= char <= "D":
                shorthand = sh(rec)
            elif char == "P":
                shorthand = "P"+sh(rec)
            else:
                shorthand = "M"+sh(rec)
            shorthandList.append(shorthand)
            idList.append(rec[1])
            dataList.append((shorthand, rec[1],rec[2],rec[3],rec[4],rec[5]))
        print("screw this")
        print(shorthandList)
        return dict(zip(shorthandList + idList, dataList + dataList))


    def idValid(self, id):
        try:
            return self.data[id.upper()]
        except:
            nick = self.getNick(id)
            if nick: return self.data[nick[1].upper()]
            else: return ()

    def roomValid(self, room):
        list_ = []
        for rec in self.data.values():
            if room.upper() == rec[4] + " " + rec[5]:
                if rec[0] not in [entry[0] for entry in list_]:
                    list_.append(self.idValid(rec[0]))
        return list_

    def hostelValid(self, hostel):
        list_ = []
        for rec in self.data.values():
            if hostel.upper() == rec[4]:
                if rec[0] not in [entry[0] for entry in list_]:
                    list_.append(self.idValid(rec[0]))
        return list_


    def search(self, text):
        text = text.upper()
        list = self.cursor.execute("select * from studrec")
        results = []
        for rec in list:
            SH = lambda record: str(record[1][2:4] + record[1][-3:])
            shorthand = None
            char = rec[1][4]
            if "A" <= char <= "D":
                shorthand = SH(rec)
            elif char == "P":
                shorthand = "P"+SH(rec)
            else:
                shorthand = "M"+SH(rec)
            if text in rec[1] or text in rec[2] or text in shorthand:
                results.append(self.data[rec[1]])
        return results

    def addNick(self, nick, idNo):
        try:
            self.cursor.execute("insert into nicks values(?,?)",(nick.upper(), idNo))
            self.db.commit()
            return 1
        except:
            return 0

    def clearAllNicks(self):
        self.cursor.execute("DELETE from nicks")

    def getNick(self, nick):
        self.cursor.execute("select * from nicks WHERE NICK = ?", (nick.upper(),))
        return self.cursor.fetchone()

    def getPassword(self, task):
        list_ = self.cursor.execute("select * from passwords WHERE TASK = ?", (task.upper(),))
        for rec in list_:
            return rec[1]

    def changePassword(self, task, password):
        if task.upper() == "UNBILLING":
            password = chorePlay.hashPassword(password)
        self.cursor.execute("update passwords set password = ? where task = ?", (password, task.upper()))
        self.db.commit()

    def isValidPassword(self, task, password):
        if task.upper() == "UNBILLING":
            return chorePlay.isValidPassword(password, self.getPassword("unbilling"))
        else:
            if password == self.getPassword("emailing"):
                return True
            else:
                return False

class passwordWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.database = parent.database
        self.setWindowTitle("Password Widget")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.move(400,100)
        self.resize(500,150)
        self.setupWidget()
        self.show()

    def setupWidget(self):
        self.unbillingPasswordOption = QtWidgets.QRadioButton("Unbilling")
        self.emailerPasswordOption = QtWidgets.QRadioButton("Emailer")
        self.oldPasswordLabel = QtWidgets.QLabel("Old Password:")
        self.oldPasswordField = QtWidgets.QLineEdit()
        self.newPasswordLabel = QtWidgets.QLabel("New Password:")
        self.newPasswordField = QtWidgets.QLineEdit()
        self.reEnterNewPasswordLabel = QtWidgets.QLabel("Re-Enter New Password:")
        self.reEnterNewPasswordField = QtWidgets.QLineEdit()
        self.changePasswordButton = QtWidgets.QPushButton("Change")
        self.validity = [0,0,0]

        self.unbillingPasswordOption.toggle()
        self.oldPasswordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.newPasswordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.reEnterNewPasswordField.setEchoMode(QtWidgets.QLineEdit.Password)

        #Layout
        widgetLayout = QtWidgets.QVBoxLayout(self)
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.unbillingPasswordOption)
        hbox1.addWidget(self.emailerPasswordOption)
        widgetLayout.addLayout(hbox1)
        widgetLayout.addStretch(True)
        widgetLayout.addWidget(self.oldPasswordLabel)
        widgetLayout.addWidget(self.oldPasswordField)
        widgetLayout.addStretch(True)
        widgetLayout.addWidget(self.newPasswordLabel)
        widgetLayout.addWidget(self.newPasswordField)
        widgetLayout.addStretch(True)
        widgetLayout.addWidget(self.reEnterNewPasswordLabel)
        widgetLayout.addWidget(self.reEnterNewPasswordField)
        widgetLayout.addStretch(True)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch(True)
        hbox2.addWidget(self.changePasswordButton)
        widgetLayout.addLayout(hbox2)

        #Signals
        self.unbillingPasswordOption.toggled.connect(self.validityUpdater)
        #self.emailerPasswordOption = QtWidgets.QRadioButton("Emailer")
        self.oldPasswordField.textChanged.connect(self.validityUpdater)
        self.newPasswordField.textChanged.connect(self.validityUpdater)
        self.reEnterNewPasswordField.textChanged.connect(self.validityUpdater)
        self.changePasswordButton.clicked.connect(self.changePassword)

        #Shortcut
        returnKeyShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Return'), self)
        returnKeyShortcut.activated.connect(self.changePassword)
        closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Escape'), self)
        closeShortcut.activated.connect(self.close)

    def validityUpdater(self):

        if self.unbillingPasswordOption.isChecked():
            task = "unbilling"
        else:
            task = "emailing"

        if self.oldPasswordField.text() == "":
            self.validity[0] = 0
            self.oldPasswordField.setStyleSheet("background-color:#3F4038")#change to grey
        elif self.database.isValidPassword(task, self.oldPasswordField.text()):
            self.validity[0] = 1
            self.oldPasswordField.setStyleSheet("background-color:#40a348")#change to green
        else:
            self.validity[0] = 0
            self.oldPasswordField.setStyleSheet("background-color:#C20417")#change to red

        if self.newPasswordField.text() == "":
            self.validity[1] = 0
            self.newPasswordField.setStyleSheet("background-color:#3F4038")#change to grey
        else:
            self.validity[1] = 1
            self.newPasswordField.setStyleSheet("background-color:#40a348")#change to green

        if self.reEnterNewPasswordField.text() == "":
            self.validity[2] = 0
            self.reEnterNewPasswordField.setStyleSheet("background-color:#3F4038")#change to grey
        elif self.reEnterNewPasswordField.text() == self.newPasswordField.text():
            self.validity[2] = 1
            self.reEnterNewPasswordField.setStyleSheet("background-color:#40a348")#change to green
        else:
            self.validity[2] = 0
            self.reEnterNewPasswordField.setStyleSheet("background-color:#C20417")#change to red

    def changePassword(self):
        if self.unbillingPasswordOption.isChecked():
            task = "unbilling"
        else:
            task = "emailing"
        if self.validity == [1,1,1]:
            self.database.changePassword(task, self.newPasswordField.text())
            QtWidgets.QMessageBox.information(self, "Yolo!!!","Password Changed!!!", QtWidgets.QMessageBox.Ok)
            self.oldPasswordField.setText("")
            self.newPasswordField.setText("")
            self.reEnterNewPasswordField.setText("")





class searchWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        self.setupWidget()
        self.setFixedHeight(self.parent.parent.configurator.searchWidgetHeight)
        self.show()

    def setupWidget(self):

        self.matchesLabel = QtWidgets.QLabel("")
        self.searchField = QtWidgets.QLineEdit("")
        self.searchButton = QtWidgets.QPushButton("Search")
        self.tableWidget = QtWidgets.QTableWidget(0,3)
        self.tableWidget.setHorizontalHeaderLabels(["ID", "NAME", "ROOM"])
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.setShowGrid(False)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.searchField)
        hbox.addWidget(self.searchButton)

        self.widgetLayout = QtWidgets.QVBoxLayout()
        self.widgetLayout.addWidget(self.matchesLabel)
        self.widgetLayout.addLayout(hbox)
        self.widgetLayout.addWidget(self.tableWidget)
        self.setLayout(self.widgetLayout)
        self.searchButton.clicked.connect(self.populate)
        self.tableWidget.cellDoubleClicked.connect(self.updateIdField)

###############Keyboard shortcuts
        #searchShortcut = QtWidgets.QShortcut(QtWidgets.QKeySequence('Return'), self)
        setFocusShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self)
        #searchShortcut.activated.connect(self.populateShortcutHandler)
        setFocusShortcut.activated.connect(self.setFocusHandler)

    def setFocusHandler(self):
        self.searchField.setFocus()

    def updateIdField(self):
        for field in self.parent.propertiesWidget.idFields:
            if field.text() == "":
                field.setText(self.parent.database.idValid(self.tableWidget.cellWidget(self.tableWidget.currentRow(), 0).text())[0])
                index = self.parent.propertiesWidget.idFields.index(field)
                self.parent.propertiesWidget.quantityFields[index].setValue(1)
                return None

    def refresh(self):
        self.searchField.setText("")
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)

    def populate(self):

        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)

        list_ = self.parent.database.search(self.searchField.text())
        for i, rec in enumerate(list_):
            self.tableWidget.insertRow(i)
            self.tableWidget.setCellWidget(i,0,QtWidgets.QLabel(rec[1]))
            self.tableWidget.setCellWidget(i,1,QtWidgets.QLabel(rec[2]))
            self.tableWidget.setCellWidget(i,2,QtWidgets.QLabel(str(rec[4] + " " + rec[5])))

class customProgressWidget1(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.bar = QtWidgets.QProgressBar()
        self.headerLabel = QtWidgets.QLabel()
        font = self.headerLabel.font()
        font.setBold(True)
        self.headerLabel.setFont(font)
        self.headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.messageLabel = QtWidgets.QLabel()
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.headerLabel)
        layout.addWidget(self.messageLabel)
        layout.addWidget(self.bar)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.resize(400,100)

class fullScreenViewer(QtWidgets.QGraphicsView):

    def __init__(self, pixmap):

        QtWidgets.QGraphicsView.__init__(self)

        self.pixmap = QtGui.QPixmap(pixmap)

        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff )
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff )

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint or QtCore.Qt.Popup)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.showFullScreen()

        d = QtWidgets.QDesktopWidget()
        self.desktopH = d.height()
        self.desktopW = d.width()

        self.displayPixmap()

        self.pan = False
        self.panStartX = 0
        self.panStartY = 0
        print("constructed")
        closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Escape'), self)
        closeShortcut.activated.connect(self.close)


    def displayPixmap(self):
        scene = QtWidgets.QGraphicsScene()
        scene.addPixmap(self.pixmap)
        self.setScene(scene)
        if self.pixmap.height() > self.desktopH and self.pixmap.width() > self.desktopW:
            if self.desktopW > self.pixmap.width()*self.desktopH/self.pixmap.height():
                self.scale(self.desktopH/self.pixmap.height(),self.desktopH/self.pixmap.height())
            else: self.scale(self.desktopW/self.pixmap.width(),self.desktopW/self.pixmap.width())

    def wheelEvent(self, event):
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        scaleFactor = 1.15
        center = self.mapToScene(self.viewport().rect().center())
        if event.delta() > 0:
            self.scale(scaleFactor, scaleFactor)
        else:
            self.scale(1.0 / scaleFactor, 1.0 / scaleFactor)
        self.centerOn(center)


class addNickWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        print(type(parent))
        self.parent = parent
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("Add Nick")
        #self.setStyleSheet("QLineEdit{background-color:#3F4038;color:white;border-radius:3px;padding:2px}")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.move(400,100)
        self.resize(500,150)
        #components
        self.nickField = QtWidgets.QLineEdit()
        self.idField = QtWidgets.QLineEdit()
        self.nameLabel = QtWidgets.QLabel("")
        self.roomLabel = QtWidgets.QLabel("")
        self.saveButton = QtWidgets.QPushButton("Add")
        #Layout
        widgetLayout = QtWidgets.QVBoxLayout(self)
        widgetLayout.addStretch(True)
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(QtWidgets.QLabel("Enter Nick:"))
        hbox1.addWidget(QtWidgets.QLabel("Enter IDNo:"))
        widgetLayout.addLayout(hbox1)
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addWidget(self.nickField)
        hbox2.addWidget(self.idField)
        widgetLayout.addLayout(hbox2)
        widgetLayout.addStretch(True)
        hbox3 = QtWidgets.QHBoxLayout()
        hbox3.addWidget(self.nameLabel)
        hbox3.addWidget(self.roomLabel)
        widgetLayout.addLayout(hbox3)
        hbox4 = QtWidgets.QHBoxLayout()
        hbox4.addStretch(True)
        hbox4.addWidget(self.saveButton)
        widgetLayout.addLayout(hbox4)
        self.show()

        #signals
        self.idField.textChanged.connect(self.idFieldHandler)
        self.nickField.textChanged.connect(self.nickFieldHandler)
        self.saveButton.clicked.connect(self.addNick)

        #Shortcut
        returnKeyShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Return'), self)
        returnKeyShortcut.activated.connect(self.addNick)
        closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Escape'), self)
        closeShortcut.activated.connect(self.close)

    def idFieldHandler(self):
        rec = self.parent.database.idValid(self.idField.text())
        if rec:
            self.nameLabel.setText(rec[2])
            self.roomLabel.setText(rec[4] + " " + rec[5])
            self.idField.setStyleSheet("background-color:#40a348")#change to green
        else:
            self.nameLabel.setText("")
            self.roomLabel.setText("")
            if self.idField.text() == "":
                self.idField.setStyleSheet("background-color:#3F4038")#change to grey
            else:
                self.idField.setStyleSheet("background-color:#C20417")#change to red

    def nickFieldHandler(self):
        if self.nickField.text() == "":
            self.nickField.setStyleSheet("background-color:#3F4038")#change to grey
        else:
            self.nickField.setStyleSheet("background-color:#40a348")#change to green

    def addNick(self):
        if self.nickField.text().strip() == "":
            QtWidgets.QMessageBox.information(self, "Nopes!", "Nick not valid!", QtWidgets.QMessageBox.Ok)
            return None
        rec = self.parent.database.idValid(self.idField.text())
        if rec:
            success = self.parent.database.addNick(self.nickField.text(), self.idField.text())
            if success:
                QtWidgets.QMessageBox.information(self, "Yolo!", "Successfully Added!", QtWidgets.QMessageBox.Ok)
                self.nickField.setText("")
                self.idField.setText("")
            else:
                QtWidgets.QMessageBox.information(self, "Nopes!", "Nick already exists!", QtWidgets.QMessageBox.Ok)
        else:
            QtWidgets.QMessageBox.information(self, "Nopes!", "ID not valid!", QtWidgets.QMessageBox.Ok)


class newDeptList(QtWidgets.QWidget):

    def __init__(self, parent = None):

        QtWidgets.QWidget.__init__(self, parent)
        #self.setStyleSheet("QLineEdit{background-color:#3F4038;color:white;border-radius:3px;padding:2px}")
        self.setWindowTitle("New Department List")
        self.setWindowFlags(QtCore.Qt.Window)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.move(400,100)
        self.resize(400,500)
        self.deptNameLabel = QtWidgets.QLabel("Department/Club:")
        self.deptNameField = QtWidgets.QLineEdit()
        self.saveButton = QtWidgets.QPushButton("Save")

        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.deptNameLabel)
        hbox1.addWidget(self.deptNameField)

        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch()
        hbox2.addWidget(self.saveButton)

        self.numFields = 500
        self.fields = [QtWidgets.QLineEdit() for i in range(self.numFields)]
        vbox = QtWidgets.QVBoxLayout(self)
        widget = QtWidgets.QWidget(self)
        widget.setLayout(vbox)
        scrollableArea = QtWidgets.QScrollArea()
        scrollableArea.setWidget(widget)
        scrollableArea.setWidgetResizable(True)
        for i in range(self.numFields): vbox.addWidget(self.fields[i])

        widgetLayout = QtWidgets.QVBoxLayout(self)
        widgetLayout.addLayout(hbox1)
        widgetLayout.addWidget(scrollableArea)
        widgetLayout.addLayout(hbox2)

        self.saveButton.clicked.connect(self.save)
        self.show()

        closeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Escape'), self)
        closeShortcut.activated.connect(self.close)


    def save(self):
        def function():
            if self.deptNameField.text() == "": return -1
            try:
                list_ = []
                for field in self.fields:
                    if field.text() != "": list_.append(field.text())
                outfile = open(os.getcwd() + os.sep + "WorkForce Lists" + os.sep + self.deptNameField.text() + ".txt", 'w')
                for rec in list_:
                    outfile.write(rec + "\n")
                outfile.close()
                return 1
            except:
                return 0
        result = function()
        if result == -1: return None
        if result:
            QtWidgets.QMessageBox.information(self, "Success!!!","File saved successfully!!!", QtWidgets.QMessageBox.Ok)
            self.deptNameField.setText("")
            for field in self.fields: field.setText("")
        else:
            QtWidgets.QMessageBox.information(self, "Fail!!!","File not saved!!!", QtWidgets.QMessageBox.Ok)
