from PyQt5 import QtCore, QtWidgets, QtGui
import sys, os
import niggerFiles


class ButtonPrev(QtWidgets.QPushButton):

    def __init__(self, parent=None):

        QtWidgets.QPushButton.__init__(self)

        dispX = 2
        dispY = 2
        radEllipse = 15
        lenRect = 30
        height = 30

        self.setFixedSize(lenRect + radEllipse + 2*dispX,height+2*dispY)

        self.setStyleSheet("QPushButton { background-color : #3F4038;}")
        
        region1 = QtGui.QRegion(QtCore.QRect(dispX, dispY, 2*radEllipse, height), QtGui.QRegion.Ellipse)
        region2 = QtGui.QRegion(QtCore.QRect(dispX + radEllipse, dispY, lenRect, height), QtGui.QRegion.Rectangle)
        region3 = QtGui.QRegion(QtCore.QRect(dispX + lenRect, dispY, 2*radEllipse, height), QtGui.QRegion.Ellipse)
        region4 = region1.united(region2)
        self.region = region4.subtracted(region3)
        self.setMask(self.region)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

class ButtonNext(QtWidgets.QPushButton):

    def __init__(self, parent=None):

        QtWidgets.QPushButton.__init__(self)

        dispX = 2
        dispY = 2
        radEllipse = 15
        lenRect = 30
        height = 30

        self.setFixedSize(lenRect + radEllipse + 2*dispX,height+2*dispY)

        self.setStyleSheet("QPushButton { background-color : #3F4038;}")
        
        region1 = QtGui.QRegion(QtCore.QRect(dispX - radEllipse, dispY, 2*radEllipse, height), QtGui.QRegion.Ellipse)
        region2 = QtGui.QRegion(QtCore.QRect(dispX, dispY, lenRect, height), QtGui.QRegion.Rectangle)
        region3 = QtGui.QRegion(QtCore.QRect(dispX + lenRect - radEllipse, dispY, 2*radEllipse, height), QtGui.QRegion.Ellipse)
        region4 = region2.united(region3)
        self.region = region4.subtracted(region1)
        self.setMask(self.region)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

class ButtonFullScreen(QtWidgets.QPushButton):

    def __init__(self, parent=None):

        QtWidgets.QPushButton.__init__(self)

        dispX = 2
        dispY = 2
        radEllipse = 15
        lenRect = 60
        height = 30

        self.setFixedSize(lenRect + 2*radEllipse + 2*dispX,height+2*dispY)

        self.setStyleSheet("QPushButton { background-color : #3F4038;}")
        
        region1 = QtGui.QRegion(QtCore.QRect(dispX, dispY, 2*radEllipse, height), QtGui.QRegion.Ellipse)
        region2 = QtGui.QRegion(QtCore.QRect(dispX + radEllipse, dispY, lenRect, height), QtGui.QRegion.Rectangle)
        region3 = QtGui.QRegion(QtCore.QRect(dispX + lenRect, dispY, 2*radEllipse, height), QtGui.QRegion.Ellipse)
        region4 = region1.united(region2)
        self.region = region4.united(region3)
        self.setMask(self.region)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

class ButtonRotate(QtWidgets.QPushButton):
    def __init__(self, parent=None):

        QtWidgets.QPushButton.__init__(self)

        dispX = 2
        dispY = 2
        height = 30
        radEllipse = height/2

        self.setFixedSize(height + 2*dispX, height +2 * dispY)

        self.setStyleSheet("QPushButton { background-color : #3F4038;}")
        
        self.region = QtGui.QRegion(QtCore.QRect(dispX, dispY, height, height), QtGui.QRegion.Ellipse)
        self.setMask(self.region)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)



class displayWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        self.setupWidget()

    def setupWidget(self):
        #image viewer dimensions
        self.widgetWidth = self.parent.parent.configurator.displayWidgetViewerWidth
        self.widgetHeight = self.parent.parent.configurator.displayWidgetViewerHeight

        self.backGroundTexture = self.parent.parent.configurator.displayWidgetBackgroundTexture
        #print("texture1",self.backGroundTexture)
        
        
        
        
        self.backGroundTexture = self.parent.parent.configurator.displayWidgetBackgroundTexture.replace("\\", "/")
        #print("texture2",self.backGroundTexture)
        #print()
        #self.backGroundTexture = ".//resources//Satin_Black_Texture.jpg"
#############GUI
        self.pixmap = QtGui.QPixmap()

        #imageViewer
        self.imageViewer = QtWidgets.QGraphicsView()
        self.imageViewer.setFixedSize(self.widgetWidth, self.widgetHeight)
        #print(self.backGroundTexture)
        self.imageViewer.setStyleSheet("QWidget {background-image: url(" + self.backGroundTexture + ") }")
        self.imageViewer.setAlignment(QtCore.Qt.AlignCenter)
        
        #No scrollbars
        self.imageViewer.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff )
        self.imageViewer.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff )

        #Buttons
        self.rotateCounterClockwiseButton = ButtonRotate()
        self.rotateClockwiseButton = ButtonRotate()
        self.nextButton = ButtonNext()
        self.previousButton = ButtonPrev()
        self.fullScreenButton = ButtonFullScreen()

        #Layout
        widgetLayout = QtWidgets.QVBoxLayout()

        widgetLayout.addWidget(self.imageViewer)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(True)
        hbox.addWidget(self.previousButton)
        hbox.addWidget(self.rotateCounterClockwiseButton)
        hbox.addWidget(self.fullScreenButton)
        hbox.addWidget(self.rotateClockwiseButton)
        hbox.addWidget(self.nextButton)
        hbox.addStretch(True)
        widgetLayout.addLayout(hbox)

        self.setLayout(widgetLayout)

###################Signals

        self.previousButton.clicked.connect(lambda: self.loadSnap(-1))
        self.nextButton.clicked.connect(lambda: self.loadSnap(1))
        self.fullScreenButton.clicked.connect(self.fullScreen)
        self.rotateClockwiseButton.clicked.connect(self.rotate("clockwise"))
        self.rotateCounterClockwiseButton.clicked.connect(self.rotate("counterClockwise"))

#######################KeyboardShortcuts

        nextSnapShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('PgDown'), self)
        previousSnapShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('PgUp'), self)
        rotateClockwiseShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Right'), self)
        rotateCounterClockwiseShortcut = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Left'), self)
        nextSnapShortcut.activated.connect(lambda: self.loadSnap(1))
        previousSnapShortcut.activated.connect(lambda: self.loadSnap(-1))
        rotateClockwiseShortcut.activated.connect(self.rotate("clockwise"))
        rotateCounterClockwiseShortcut.activated.connect(self.rotate("counterClockwise"))
        
        
    
    def setPixmap(self):

        scene = QtWidgets.QGraphicsScene()
        self.imageViewer.setScene(scene)
        
        #Resize the snap to fit the screen, keeping the aspect ratio
        try:
            if self.widgetWidth > self.pixmap.width()*self.widgetHeight/self.pixmap.height():
                w,h = self.pixmap.width()*self.widgetHeight/self.pixmap.height(),self.widgetHeight
            else: w,h = self.widgetWidth,self.pixmap.height()*self.widgetWidth/self.pixmap.width()
            scene.addPixmap(self.pixmap.scaled(w,h))
        except:
            scene = QtWidgets.QGraphicsScene()
            self.imageViewer.setScene(scene)
            scene.addPixmap(QtGui.QPixmap())       

    
    def loadSnap(self, diff = 0):

        #If any entry is invalid in propertiesWidget - do nothing
        for validity in self.parent.propertiesWidget.validity:
            if validity == -1: return None

        #for first and last snap cases - do nothing
        if (diff == 1 and self.parent.roll.hasNext()) or (diff == -1 and self.parent.roll.hasPrevious()) or (diff == 0):
            if diff != 0:
                self.parent.roll.currentPos += diff
                self.parent.propertiesWidget.refresh()
                self.parent.leftWidget.refresh()
                try:
                    self.parent.propertiesWidget.idFields[0].setFocus()
                except:
                    pass
            try:
                #for rec in self.parent.roll.snapList:
                   # print(rec.name)
                path = self.parent.roll.path + os.sep + self.parent.roll.getSnap().name
                #print("path1=", path)
            except:
                path = self.parent.roll.getSnap().path
            #print("pathcheckyo", path)
            self.pixmap = QtGui.QPixmap(path)
            self.setPixmap()
            #print("pixmapsetyo")


    def rotate(self, direction):
        def rotateClockwise():
            self.pixmap = self.pixmap.transformed(QtGui.QTransform().rotate(90))
            self.setPixmap()
        def rotateCounterClockwise():
            self.pixmap = self.pixmap.transformed(QtGui.QTransform().rotate(-90))
            self.setPixmap()
        return rotateClockwise if direction == "clockwise" else rotateCounterClockwise

        
    def fullScreen(self):
        self.fullScreenViewer = niggerFiles.fullScreenViewer(self.pixmap)
        self.fullScreenViewer.show()


