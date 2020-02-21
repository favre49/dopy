from PyQt5 import QtCore, QtWidgets
import sys, os

class itemComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None, clothes=False):

        QtWidgets.QComboBox.__init__(self)
        self.parent = parent
        self.model = QtCore.QStringListModel()
        if clothes:
            self.itemList = self.parent.parent.parent.configurator.clothesItemList
        else:
            self.itemList = self.parent.parent.parent.configurator.restItemList
        self.model.setStringList(self.itemList)
        self.addItems(self.itemList)

        self.setEditable(True)

        self.completer = CustomQCompleter(self)
        self.completer.setModel(self.model)


        self.setCompleter(self.completer)
        self.setEditText('')

        # self.setGeometry(200, 100, 400, 300)

class quantityBox(QtWidgets.QLineEdit):

    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self)
        self.parent = parent
        self.setText('')
        # self.setGeometry(200, 100, 400, 300)

class sizeComboBox(QtWidgets.QComboBox):

    def __init__(self, parent=None):

        QtWidgets.QComboBox.__init__(self)
        self.parent = parent
        self.model = QtCore.QStringListModel()
        self.sizeList = ["S", "M", "L", "XL", "XXL"]

        self.model.setStringList(self.sizeList)
        self.addItems(self.sizeList)

        self.setEditable(True)

        self.completer = CustomQCompleter(self)
        self.completer.setModel(self.model)


        self.setCompleter(self.completer)
        self.setEditText('')

        # self.setGeometry(200, 100, 400, 300)

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

class centralWidget(QtWidgets.QWidget):

    def __init__(self, parent = None):
        QtWidgets.QWidget.__init__(self)
        self.parent = parent
        self.setupWidget()

    def setupWidget(self):

        self.database = self.parent.database
        # self.setFixedHeight(self.parent.parent.configurator.centralWidgetMerchHeight)
        self.setFixedHeight(440)
#############Gui Components
        self.syncButton = QtWidgets.QPushButton("Sync")

        self.idFieldLabel = QtWidgets.QLabel(r'ID Number (in format: 201XAXPSXXXX)')
        self.idFieldLabel.setWordWrap(True)
        self.idField = QtWidgets.QLineEdit("")

        self.isOutstiField = QtWidgets.QCheckBox("Outsti (Hover over text to view the checkbox)")

        self.clothesNameFields = []
        self.clothesSizeFields = []
        self.restNameFields = []
        self.quantityFields = []

        for entry in range(0, 5):        
            self.clothesNameFields.append(itemComboBox(self, True))
            self.clothesSizeFields.append(sizeComboBox(self))
            self.restNameFields.append(itemComboBox(self, False))
            self.quantityFields.append(quantityBox(self))

        self.doneButton = QtWidgets.QPushButton("Done")

        hboxSync = QtWidgets.QHBoxLayout()
        hboxSync.addStretch(True)
        hboxSync.addWidget(self.syncButton)

        hboxId = QtWidgets.QHBoxLayout()
        hboxId.addWidget(self.idFieldLabel)
        hboxId.addWidget(self.idField)

        hboxOutsti = QtWidgets.QHBoxLayout()
        hboxOutsti.addWidget(self.isOutstiField)

        hboxDone = QtWidgets.QHBoxLayout()
        hboxDone.addStretch(True)
        hboxDone.addWidget(self.doneButton)

        widgetLayout = QtWidgets.QVBoxLayout()
        widgetLayout.addLayout(hboxSync)
        widgetLayout.addLayout(hboxId)
        widgetLayout.addLayout(hboxOutsti)

        clothesVbox = QtWidgets.QVBoxLayout()
        restVbox = QtWidgets.QVBoxLayout()

        clothesLabel = QtWidgets.QLabel('Clothes based Items')
        restLabel = QtWidgets.QLabel('Non-Clothes based Items')
        clothesVbox.addWidget(clothesLabel)
        restVbox.addWidget(restLabel)

        for entry in range(0, 5):
            hbox = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel('Item-'+str(entry + 1))
            hbox.addWidget(label)
            hbox.addWidget(self.clothesNameFields[entry])
            hbox.addWidget(self.clothesSizeFields[entry])
            clothesVbox.addLayout(hbox)

            hbox = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel('Item-'+str(entry + 1))
            hbox.addWidget(label)
            hbox.addWidget(self.restNameFields[entry])
            hbox.addWidget(self.quantityFields[entry])
            restVbox.addLayout(hbox)

        itemsHbox = QtWidgets.QHBoxLayout()
        itemsHbox.setSpacing(12)
        itemsHbox.addLayout(clothesVbox)
        itemsHbox.addStretch(True)
        itemsHbox.addLayout(restVbox)

        widgetLayout.addLayout(itemsHbox)
        widgetLayout.addLayout(hboxDone)
        self.setLayout(widgetLayout)

    def refresh(self):
        self.idField.setText("")
        self.isOutstiField.setChecked(False)
        for entry in range(0, 5):
            self.clothesNameFields[entry].setEditText('')
            self.clothesSizeFields[entry].setEditText('')
            self.restNameFields[entry].setEditText('')
            self.quantityFields[entry].setText('')