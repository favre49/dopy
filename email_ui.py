from PyQt5 import QtCore, QtWidgets, QtGui
import sys, os, csv, re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.header import Header
from email import encoders
from getpass import getpass
from smtplib import SMTP_SSL
from base64 import encode
from collections import namedtuple
from random import randint

class Email_Ui(QtWidgets.QWidget):
    def __init__(self, parent = None):
        self.parent = parent
        super(Email_Ui,self).__init__()
        self.setupUi()
        self.show()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def setupUi(self):

        self.prevSnap =QtWidgets.QLabel("Previous Snap:",self)
        self.currSnap = QtWidgets.QLabel("This Snap:",self)
        self.prevPeople = QtWidgets.QLabel("No. Of Peepals:",self)
        self.prevStatus = QtWidgets.QLabel("Status",self)
        self.currPeople = QtWidgets.QLabel("No. Of Peepals:",self)
        self.currStatus = QtWidgets.QLabel("Status",self)
        self.folderButton = QtWidgets.QPushButton("Choose Folder...",self)
        #self.boredButton = QtWidgets.QPushButton("I am bored!",self)

        self.vLayout_left = QtWidgets.QVBoxLayout()
        self.vLayout_left.addStretch(True)
        self.vLayout_left.addWidget(self.folderButton)
        self.vLayout_left.addStretch(True)
        self.vLayout_left.addWidget(self.currSnap)
        self.vLayout_left.addWidget(self.currPeople)
        self.vLayout_left.addWidget(self.currStatus)
        self.vLayout_left.addStretch(True)
        self.vLayout_left.addWidget(self.prevSnap)
        self.vLayout_left.addWidget(self.prevPeople)
        self.vLayout_left.addWidget(self.prevStatus)
        #self.vLayout_left.addWidget(self.boredButton)
        self.vLayout_left.addStretch(True)

        self.vLayout_center = QtWidgets.QVBoxLayout()
        self.pictureViewer = QtWidgets.QLabel(self)

        self.hLayout_center = QtWidgets.QHBoxLayout()
        self.prevButton = QtWidgets.QPushButton("<< Previous",self)
        self.nextButton = QtWidgets.QPushButton("Next >>",self)

        self.hLayout_center.addStretch(True)
        self.hLayout_center.addWidget(self.prevButton)
        self.hLayout_center.addWidget(self.nextButton)
        self.hLayout_center.addStretch(True)

        self.vLayout_center.addWidget(self.pictureViewer)
        self.vLayout_center.addLayout(self.hLayout_center)

        self.vLayout_right = QtWidgets.QVBoxLayout()
        self.hboxlist = []
        self.idfield = []
        self.statusfield = []

        self.scrollWidget = QtWidgets.QWidget()
        self.widgetVBox = QtWidgets.QVBoxLayout()


        for i in range(100):
            self.idfield.append(QtWidgets.QLineEdit("",self))
            self.idfield[i].setMaximumWidth(180)
            self.statusfield.append(QtWidgets.QLabel("-",self))
            self.hboxlist.append(QtWidgets.QHBoxLayout())

            self.hboxlist[i].addWidget(self.idfield[i])
            #self.hboxlist[i].addStretch(True)
            self.hboxlist[i].addWidget(self.statusfield[i])

            self.vLayout_right.addLayout(self.hboxlist[i])

        self.widgetVBox.addLayout(self.vLayout_right)
        self.scrollWidget.setLayout(self.widgetVBox)

        self.scrollarea = QtWidgets.QScrollArea()
        self.scrollarea.setWidget(self.scrollWidget)
        self.scrollarea.setWidgetResizable(True)

        self.vLayout_xright=QtWidgets.QVBoxLayout()
        self.hLayout_right = QtWidgets.QHBoxLayout()

        self.emailButton = QtWidgets.QPushButton("Email",self)
        self.saveButton = QtWidgets.QPushButton("Save to sheet",self)

        self.hLayout_right.addStretch(True)
        self.hLayout_right.addWidget(self.emailButton)
        self.hLayout_right.addWidget(self.saveButton)

        self.vLayout_xright.addWidget(self.scrollarea)
        #self.vLayout_xright.addStretch()
        self.vLayout_xright.addLayout(self.hLayout_right)

        self.hLayout_bottom = QtWidgets.QHBoxLayout()
        self.progressBar = QtWidgets.QProgressBar(self)
        self.hLayout_bottom.addWidget(self.progressBar)

        self.hLayout_top = QtWidgets.QHBoxLayout()

        self.hLayout_top.addLayout(self.vLayout_left)
        self.hLayout_top.addStretch()
        self.hLayout_top.addLayout(self.vLayout_center)
        self.hLayout_top.addStretch()
        self.hLayout_top.addLayout(self.vLayout_xright)
        #self.hLayout_top.addStretch()

        widgetLayout = QtWidgets.QVBoxLayout()
        widgetLayout.addLayout(self.hLayout_top)
        widgetLayout.addLayout(self.hLayout_bottom)
        self.setLayout(widgetLayout)
        self.resize(1024,720)
        
        self.emailer = Emailer(self)
        self.path = ''

        self.folderButton.connect(self.folderButton, QtCore.SIGNAL("clicked()"),self.pathLoader)
        for i in range(100):
            self.idfield[i].textChanged.connect(self.textFieldCaller(i))
        self.emailButton.connect(self.emailButton,QtCore.SIGNAL("clicked()"),self.emailer.emailAll)
        self.saveButton.connect(self.saveButton, QtCore.SIGNAL("clicked()"),lambda snaplist = self.emailer.snaplist,combilist=self.emailer.combilist:self.emailer.fileWriter(snaplist,combilist))
        self.prevButton.connect(self.prevButton, QtCore.SIGNAL("clicked()"),self.prevHandler)
        self.nextButton.connect(self.nextButton, QtCore.SIGNAL("clicked()"),self.nextHandler)
        #self.boredButton.connect(self.boredButton,QtCore.SIGNAL("clicked()"),self.boredHandler)

        self.emailexp = re.compile(".+@.+\..+")#compile reg ex for email id

    #functions#
    def pathLoader(self):
        self.path=QtWidgets.QFileDialog.getExistingDirectory(parent=None, caption='Choose A File')
        if self.path == '':
            QtWidgets.QMessageBox.about(self,"Choose a valid folder!","You chose nothing. Choose something")
            return None

        self.pathlist = os.listdir(self.path)
        self.foundflag = 0
        for k in self.pathlist:
            if os.path.splitext(k)[1] == '.csv':
                print(self.emailer.snaplist)
                print(os.path.splitext(k)[1])
                self.csvfile = self.path + os.sep + k
                self.foundflag = 1
                
        if self.foundflag == 0:
            QtWidgets.QMessageBox.about(self,"Choose Another Folder!","Folder ain't got no csv file.Choose another folder.")
            return None
        else:
            self.emailer.fileReader()
            print(self.emailer.snaplist)
            self.progressBar.setMinimum(0)
            self.progressBar.setMaximum(len(self.emailer.snaplist))
            
            for sublist in self.emailer.combilist:
                for details in sublist:
                    print(details)
            self.picIndex = 0
            print(self.emailer.snaplist[self.picIndex])
            self.pictureViewer.setPixmap(QtGui.QPixmap(self.path + os.sep + self.emailer.snaplist[self.picIndex]).scaled(1024/2,681/2))
            self.textFieldFiller(self.picIndex)

    def nextHandler(self):
        if self.path == '':
            return None
        else:
            if self.picIndex < (len(self.emailer.snaplist)-1):
                self.picIndex = self.picIndex + 1
                self.pictureViewer.setPixmap(QtGui.QPixmap(self.path + os.sep + self.emailer.snaplist[self.picIndex]).scaled(1024/2,681/2))
                self.textFieldFiller(self.picIndex)   
            else:
                return None

    def prevHandler(self):
        if self.path == '':
            return None
        else:
            if self.picIndex > 0:
                self.picIndex = self.picIndex - 1
                self.pictureViewer.setPixmap(QtGui.QPixmap(self.path + os.sep + self.emailer.snaplist[self.picIndex]).scaled(1024/2,681/2))
                self.textFieldFiller(self.picIndex)
            else:
                return None
            
    def textFieldFiller(self,index):
        """Fill text fields with existing data"""
        self.tempsublist = self.emailer.combilist[index]
        print("tempsublist before",self.tempsublist)
        self.emailer.combilist[index] = []
        for i in range(100):
            self.idfield[i].setText("")
        print("tempsublist after",self.tempsublist)
        for details in self.tempsublist:
            self.idfield[details.index].setText(details.emailid)
            print(details)
            if details.status == '0':
                self.statusfield[details.index].setText("Not Sent")
            elif details.status == '1':
                self.statusfield[details.index].setText("Sent")
            else:
                self.statusfield[details.index].setText("-")

    def textFieldCaller(self,textIndex):
        def textFieldHandler():
            print("Jigga", textIndex)
            sublist = self.emailer.combilist[self.picIndex]
            print("sublist",sublist)
            emailadd = self.idfield[textIndex].text()
            print("emailadd",emailadd)
            if self.emailexp.match(emailadd):
                self.idfield[textIndex].setStyleSheet("background-color:#40a348")#Change colour to green
                if textIndex > len(self.tempsublist)-1:
                    temptuple = self.emailer.Combituple(emailadd,'0',textIndex)
                    sublist.append(temptuple)
                    print("Appended Valid")
                    self.statusfield[textIndex].setText("Not Sent")
                else:
                    if(self.tempsublist[textIndex].emailid == emailadd):
                        temptuple = self.emailer.Combituple(emailadd,self.tempsublist[textIndex].status,textIndex)
                        sublist.append(temptuple)
                        if temptuple.status == '1':
                            self.statusfield[textIndex].setText("Sent")
                        else:
                            self.statusfield[textIndex].setText("Not Sent")
                            
                        print("Same as before")
                    else:
                        temptuple = self.emailer.Combituple(emailadd,'0',textIndex)
                        sublist.append(temptuple)
                        print("Replaced Valid")
                        self.statusfield[textIndex].setText("Not Sent")
            else:
                self.idfield[textIndex].setStyleSheet("background-color:#C20417")#Change colour to red
                self.statusfield[textIndex].setText("-")
                if textIndex < len(sublist):
                    sublist.pop(textIndex)
                    print("Invalid Popped")
                else:
                    if(self.idfield[textIndex].text() == ''):
                        self.idfield[textIndex].setStyleSheet("background-color:#3F4038")
                    else:
                        self.idfield[textIndex].setStyleSheet("background-color:#C20417")
                        
                    print("Final else clause")
                #self.emailer.combilist[self.picIndex] = tempsublist[:]
        return textFieldHandler


    def closeEvent(self, event):

        reply = QtWidgets.QMessageBox.question(self, 'Quit?',
            "Unsaved data will be lost.\nSure about it?", QtWidgets.QMessageBox.Yes |
            QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

class Emailer():
    snaplist = []
    combilist = []
    sublist = []
    Combituple = namedtuple('Details',['emailid','status','index'])

    def __init__(self,parent):
        self.parent = parent

    def fileReader(self):
        """Read the details from the path and saves them in a list"""
        if self.parent.path == '':
            QtWidgets.QMessageBox.about(self.parent,"Choose a valid folder!","You chose nothing. Choose something")
            return None
        
        print(self.parent.csvfile)
        with open(self.parent.csvfile,"r") as csvf:
            studentReader = csv.reader(csvf,delimiter = ';')
            rownum = 0
            for row in studentReader:
                colnum = 0
                for col in row:
                    if colnum%2 == 0:
                        self.snaplist.append(col)
                        colnum+=1
                    else:
                        i=0
                        indexcnt = 0
                        length = len(col.split("|"))
                        print(length)
                        if(length > 1):
                            while i < length:
                                try:
                                    c = self.Combituple(col.split("|")[i],col.split("|")[i+1],indexcnt)
                                except:
                                    return None
                                self.sublist.append(c)
                                indexcnt=indexcnt+1
                                i = i + 2
                            print("sublist=",self.sublist)
                            self.combilist.append(self.sublist[:])
                            print("combilist=",self.combilist)
                            self.sublist[:] = []
                            #print("2:",self.combilist)
                            colnum+=1

                        else:
                            c = self.Combituple("","",indexcnt)
                            self.sublist.append(c)
                            self.combilist.append(self.sublist[:])
                            self.sublist[:] = []
                            colnum+=1
                rownum+=1

    def fileWriter(self,snaplist,combilist):
        """Write all the changes to file"""
        with open(self.parent.csvfile,"w") as csvf:
            detailsWriter = csv.writer(csvf,delimiter=';',lineterminator='\n')
            detailsList = []
            print(snaplist)
            for sublist in combilist:
                detailstring = ''
                for details in sublist:
                    detailstring = detailstring + details.emailid + "|" + str(details.status) + "|"
                detailsList.append(detailstring[:-1])
            detailsWriter.writerows(zip(snaplist,detailsList))
                    
    def massMailer(self):
        """Send mail to all users in the csv file"""
        paris = range(len(self.snaplist))
        login,password = 'adwait.d10@gmail.com',getpass('Gmail Password:')
        text="Yolo?"
        self.newlist = []
        print(self.combilist)
        self.tempcombilist = self.combilist[:]
        print(self.tempcombilist)
        self.combilist = []

        for niggers in paris:
            templist = self.tempcombilist[niggers]
            print(templist)

            for currDetails in templist:
                if currDetails.status == 1:
                    print("Chill,message be sent to the nigga already")

                else:
                    snappath = self.snaplist[niggers]
                    attachmentName = snappath.split("\\")[-1]

                    #Add From,To,Subject and Body#
                    msg = MIMEMultipart()
                    msg.attach(MIMEText(text))
                    msg['From'] = login
                    msg['To'] = currDetails.emailid
                    msg['Subject'] = Header('Dept. Of Photography Snaps','utf-8')

                    #Add attachment to mail#
                    attachment = MIMEBase('application',"octet-stream")
                    attachment.set_payload(open(self.parent.path + os.sep + snappath,"rb").read())
                    encoders.encode_base64(attachment)
                    attachment.add_header('Content-Disposition', 'attachment;filename="%s"'%attachmentName)

                    msg.attach(attachment)

                    s = SMTP_SSL('smtp.gmail.com',465,timeout=10)
                    s.set_debuglevel(0)
                    try:
                        s.login(login,password)
                        s.sendmail(msg['From'],msg['To'],msg.as_string())
                        newDetails = currDetails._replace(status=1)
                        print(newDetails)
                        self.newlist.append(newDetails)
                        self.parent.progressBar.setValue(self.parent.progressBar.value() + 1)
                    finally:
                        s.close()
            self.combilist.append(self.newlist[:])
            self.newlist = []
        self.fileWriter(self.snaplist,self.combilist)

    def emailAll(self):
        """Save changes to file and send email"""
        if self.parent.path == '':
            return None
        else:
            self.fileWriter(self.snaplist,self.combilist)
            self.massMailer()

def main():
    app = QtWidgets.QApplication(sys.argv)
    ex = Email_Ui()
    app.setStyle(QtWidgets.QStyleFactory.create("Plastique"))
    app.setStyleSheet("""
QWidget{background-color:#000400;color:#62BECB;}
    QPushButton{border-radius:3px;border-width:1px;border-color:#0E4E5A;border-style:outset;padding:5px}
    QPushButton:hover{background-color:#62BECB;color:white;border-radius:3px;border-color:#0E4E5A;border-width:1px;border-style:outset;}
    QPushButton:pressed{background-color:#0E4E5A;color:white;}
    QLineEdit{background-color:#3F4038;color:white;border-radius:3px;padding:2px}""")
    app.exec_()    

#if __name__ == '__main__':
    #main()
