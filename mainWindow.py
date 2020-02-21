from PyQt5 import QtWidgets, QtCore, QtGui
from operator import itemgetter
import sys, os, random, time, webbrowser
import bill, unbill, merch, homeWidget, chorePlay, email_ui, config, sendtoprinter, niggerFiles
sys.path.insert(1, '/usr/local/lib/python3.6/site-packages/PyQt5')

class mainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.databaseFilePath = "resources" +os.sep+ "database.db"
        self.database = niggerFiles.Students(self.databaseFilePath)
        self.configurator = config.configurator()
        self.iAmBoredPath = os.getcwd() + os.sep + "i am bored"
        self.widget = None
        self.setupStatusBar()
        self.setupMenuBar()
        self.setupCentralWidget()
        QtWidgets.QApplication.instance().setStyleSheet(self.configurator.applicationStyleSheet)

    def setupStatusBar(self):

        result = self.database.checkDatabase()
        if result:
            message = "Database Check Completed. {} Student Record, {} Nicks. ".format(result[0], result[1])
            if result[2]:
                message += "Passwords Verified"
            else:
                message += "Passwords Database Invalid"
        else:
            message = "Database Invalid. Use generate option."
        self.statusBar().showMessage(message, 10000)



    def setupMenuBar(self):

        self.menuBar = self.menuBar()
        #creating menus
        self.menus = {}
        self.menus["filemenu"] = self.menuBar.addMenu("File")
        self.menus["modesmenu"] = self.menuBar.addMenu("Modes")
        self.menus["optionsmenu"] = self.menuBar.addMenu("Options")
        #listing munuitems (pos,menu,name,action,shortcut)
        self.menuItems = {}
        self.menuItems["loaddatabase"] = [0,"filemenu", "Load Database", None, None]
        self.menuItems["newdeptlist"] = [1,"filemenu", "New Dept List", None, 'Ctrl+D']
        self.menuItems["generatebill"] = [4,"filemenu", "Generate Bill", None, None]
        self.menuItems["addnick"] = [2,"filemenu", "Add Nick", None, 'Ctrl+N']
        self.menuItems["sendtoprinter"] = [3,"filemenu", "send2printer", None, 'Ctrl+S']
        self.menuItems["home"] = [0,"modesmenu", "Home", None, None]
        self.menuItems["billing"] = [1,"modesmenu", "Billing", None, None]
        self.menuItems["reviewbilled"] = [2,"modesmenu", "Review Billed", None, None]
        self.menuItems["emailer"] = [3,"modesmenu", "Emailer", None, None]
        self.menuItems["merch"] = [4,"modesmenu", "Merch", None, None]
        self.menuItems["changepassword"] = [0,"optionsmenu", "Change Passwords", None, 'Ctrl+P']
        #self.menuItems["themes"] = [1,"optionsmenu", "Themes", None, 'Ctrl+T']
        self.menuItems["configure"] = [1,"optionsmenu", "Configure", None, 'F1']

        #creating menuactions and shortcuts
        list_ = []
        for rec in self.menuItems.values():
            list_.append(rec)
        list_.sort(key = itemgetter(1,0))
        for menuItem in list_:
            menuItem[3] = self.menus[menuItem[1]].addAction(menuItem[2])
            if menuItem[4] != None: menuItem[3].setShortcut(menuItem[4])

##########connecting universal menuActions:
        #Load database
        self.menuItems["loaddatabase"][3].triggered.connect(self.generateDatabase)
        #New Dept List
        self.menuItems["newdeptlist"][3].triggered.connect(lambda: niggerFiles.newDeptList(self))
        #Add Nick
        self.menuItems["addnick"][3].triggered.connect(lambda: niggerFiles.addNickWidget(self))
        #Send 2 Printer
        self.menuItems["sendtoprinter"][3].triggered.connect(lambda: sendtoprinter.sendToPrinter(self))
        #Generate Bill
        self.menuItems["generatebill"][3].triggered.connect(self.billGenerator)
        #password Widget
        self.menuItems["changepassword"][3].triggered.connect(lambda: niggerFiles.passwordWidget(self))
        #cofigure option
        self.menuItems["configure"][3].triggered.connect(self.configureOptionHandler)
        #i am bored
        iambored = self.menus['optionsmenu'].addMenu("I Am Bored")
        setPathOption = iambored.addAction("Set Path")
        boredOption = iambored.addAction("Yes I Am")
        boredOption.setShortcut('F2')
        setPathOption.triggered.connect(self.setIAmBoredPath)
        boredOption.triggered.connect(self.iAmBored)
        #widgets
        self.menuItems["home"][3].triggered.connect(lambda: self.setupCentralWidget("home"))
        self.menuItems["billing"][3].triggered.connect(lambda: self.setupCentralWidget("billing"))
        self.menuItems["reviewbilled"][3].triggered.connect(lambda: self.setupCentralWidget("unbilling"))
        self.menuItems["emailer"][3].triggered.connect(lambda: self.setupCentralWidget("emailer"))
        self.menuItems["merch"][3].triggered.connect(lambda: self.setupCentralWidget("merch"))


    def setupCentralWidget(self, widget = "home"):

        if widget == "home":

            if self.widget != None: self.widget.close()
            self.widget = homeWidget.homeWidget(self)
            self.setCentralWidget(self.widget)
            self.menuItems["loaddatabase"][3].setEnabled(True)
            self.menuItems["home"][3].setDisabled(True)
            self.menuItems["billing"][3].setEnabled(True)
            self.menuItems["reviewbilled"][3].setEnabled(True)
            self.menuItems["emailer"][3].setEnabled(True)
            self.menuItems["merch"][3].setEnabled(True)
            self.widget.setStyleSheet(self.configurator.homeWidgetStyleSheet)


        elif widget == "billing":
            if self.widget != None: self.widget.close()
            self.widget = bill.billingWidget(self)
            self.widget.setStyleSheet(self.configurator.otherWidgetsStyleSheet)

            self.setCentralWidget(self.widget)

            ###enable/disable meunitems
            self.menuItems["loaddatabase"][3].setDisabled(True)
            self.menuItems["home"][3].setEnabled(True)
            self.menuItems["billing"][3].setDisabled(True)
            self.menuItems["reviewbilled"][3].setEnabled(True)
            self.menuItems["emailer"][3].setEnabled(True)
            self.menuItems["merch"][3].setEnabled(True)

            self.widget.loadNewFolder()

        elif widget == "unbilling":
            if self.widget != None: self.widget.close()
            self.widget = unbill.unbillingWidget(self)
            self.widget.setStyleSheet(self.configurator.otherWidgetsStyleSheet)
            self.setCentralWidget(self.widget)

            ###enable/disable meunitems
            self.menuItems["loaddatabase"][3].setDisabled(True)
            self.menuItems["home"][3].setEnabled(True)
            self.menuItems["billing"][3].setEnabled(True)
            self.menuItems["reviewbilled"][3].setDisabled(True)
            self.menuItems["emailer"][3].setEnabled(True)
            self.menuItems["merch"][3].setEnabled(True)


        elif widget == "emailer":
            if self.widget != None: self.widget.close()
            self.widget = email_ui.Email_Ui(self)
            self.widget.setStyleSheet(self.configurator.otherWidgetsStyleSheet)
            self.setCentralWidget(self.widget)

            ###enable/disable meunitems
            self.menuItems["loaddatabase"][3].setEnabled(True)
            self.menuItems["home"][3].setEnabled(True)
            self.menuItems["billing"][3].setEnabled(True)
            self.menuItems["reviewbilled"][3].setEnabled(True)
            self.menuItems["emailer"][3].setDisabled(True)
            self.menuItems["merch"][3].setEnabled(True)
            self.widget.loadNewFolder()

        elif widget == "merch":
            if self.widget != None: self.widget.close()
            self.widget = merch.merchWidget(self)
            self.widget.setStyleSheet(self.configurator.otherWidgetsStyleSheet)
            self.setCentralWidget(self.widget)

            ###enable/disable menuitems
            self.menuItems["loaddatabase"][3].setDisabled(True)
            self.menuItems["home"][3].setEnabled(True)
            self.menuItems["billing"][3].setEnabled(True)
            self.menuItems["reviewbilled"][3].setEnabled(True)
            self.menuItems["emailer"][3].setEnabled(True)
            self.menuItems["merch"][3].setDisabled(True)

    def billGenerator(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Locate the Billed Snaps Folder")
        path =  QtCore.QDir.toNativeSeparators(path);
        if path == "": return None #FileDialog closed
        billingList = chorePlay.readSnaps(path)
        chorePlay.generateBill(billingList, self.database)

    def setIAmBoredPath(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Locate an interesting Folder")
        if path != "": self.iAmBoredPath = path

    def iAmBored(self):

        try:
            files = os.listdir(self.iAmBoredPath)
            fileNo = random.randint(0,len(files)-1)
            os.startfile(self.iAmBoredPath + os.sep + files[fileNo])
        except:
            return None

    def configureOptionHandler(self):
        webbrowser.open(self.configurator.configFilePath)

    def generateDatabase(self):
        chorePlay.generateDatabase()
        self.database = niggerFiles.Students(self.databaseFilePath)
        self.setupStatusBar()


app = QtWidgets.QApplication(sys.argv)

app.setStyle(QtWidgets.QStyleFactory.create("Plastique"))

ex = mainWindow()
splash_pic = QtGui.QPixmap("resources"+os.sep+"Icons"+os.sep+"logo.png")
splash_screen = QtWidgets.QSplashScreen(splash_pic,QtCore.Qt.WindowStaysOnTopHint)
splash_screen.setMask(splash_pic.mask())
splash_screen.show()
app.processEvents()

time.sleep(2)
splash_screen.finish(ex)
ex.showMaximized()
sys.exit(app.exec_())
