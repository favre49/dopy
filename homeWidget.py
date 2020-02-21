from PyQt5 import QtCore, QtWidgets
import sys,os

class homeWidget(QtWidgets.QWidget):
    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.parent = parent
        self.setupUi()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

    def setupUi(self):

        self.billButton = QtWidgets.QPushButton("Bill",self)
        self.billButton.setStyleSheet(self.parent.configurator.homeWidgetBillButtonStyleSheet)
        
        self.emailButton = QtWidgets.QPushButton("Email",self)
        self.emailButton.setStyleSheet(self.parent.configurator.homeWidgetEmailerButtonStyleSheet)

        self.unbillButton = QtWidgets.QPushButton("Review Billed",self)
        self.unbillButton.setStyleSheet(self.parent.configurator.homeWidgetReviewBilledButtonStyleSheet)

        self.merchButton = QtWidgets.QPushButton("Merch",self)
        self.merchButton.setStyleSheet(self.parent.configurator.homeWidgetMerchButtonStyleSheet)

        self.festLabel = QtWidgets.QLabel(self.parent.configurator.homeWidgetFestName,self)
        self.festLabel.setStyleSheet(self.parent.configurator.homeWidgetFestLabelFont)

        self.billButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.emailButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.unbillButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.merchButton.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.billButton.setFixedSize(300,300)
        self.emailButton.setFixedSize(300,300)
        self.unbillButton.setFixedSize(300,300)
        self.merchButton.setFixedSize(300,300)

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.addWidget(self.billButton,0,0)
        self.gridLayout.addWidget(self.unbillButton,0,1)
        self.gridLayout.addWidget(self.emailButton,1,0)
        self.gridLayout.addWidget(self.merchButton,1,1)

        self.vertLayout = QtWidgets.QVBoxLayout()
        self.vertLayout.addStretch()
        self.vertLayout.addLayout(self.gridLayout)
        self.vertLayout.addStretch()

        self.leftvlayout = QtWidgets.QVBoxLayout()
        self.leftvlayout.addStretch()
        self.leftvlayout.addWidget(self.festLabel)

        self.widgetLayout = QtWidgets.QHBoxLayout()
        self.widgetLayout.addStretch()
        #hspacer1 = QtWidgets.QSpacerItem(100,100)
        self.widgetLayout.addLayout(self.vertLayout)
        self.widgetLayout.addStretch()
        self.widgetLayout.addLayout(self.leftvlayout)
        #hspacer2 = QtWidgets.QSpacerItem(100,100)
        
        self.setLayout(self.widgetLayout)

        #Connect Buttons#
        self.billButton.clicked.connect(lambda : self.parent.setupCentralWidget("billing"))
        self.unbillButton.clicked.connect(lambda : self.parent.setupCentralWidget("unbilling"))
        self.emailButton.clicked.connect(lambda : self.parent.setupCentralWidget("emailer"))
        self.merchButton.clicked.connect(lambda : self.parent.setupCentralWidget("merch"))

