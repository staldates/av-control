'''
Created on 10 Nov 2012

@author: james
'''
from staldates.ui.StringConstants import StringConstants
from Pyro4.errors import ProtocolError, NamingError
from PySide.QtGui import QWidget, QGridLayout, QButtonGroup, QMessageBox
from PySide.QtCore import Signal
from staldates.ui.widgets.Buttons import InputButton
from staldates.ui.widgets.ScanConverterControls import OverscanFreezeWidget
from staldates import VisualsSystem


class ExtrasSwitcher(QWidget):
    '''
    The extras switcher.
    '''

    inputSelected = Signal(VisualsSystem.Input)

    def __init__(self, controller):
        super(ExtrasSwitcher, self).__init__()
        self.controller = controller
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)

        inputs = QButtonGroup()

        btnE1 = InputButton(self)
        btnE1.setText("Extras 1")
        btnE1.setInput(VisualsSystem.extras1)
        layout.addWidget(btnE1, 0, 0)
        inputs.addButton(btnE1, 1)
        btnE1.clicked.connect(self.takePreview)

        btnE2 = InputButton(self)
        btnE2.setText("Extras 2")
        btnE2.setInput(VisualsSystem.extras2)
        layout.addWidget(btnE2, 0, 1)
        inputs.addButton(btnE2, 2)
        btnE2.clicked.connect(self.takePreview)

        btnE3 = InputButton(self)
        btnE3.setText("Extras 3")
        btnE3.setInput(VisualsSystem.extras3)
        layout.addWidget(btnE3, 0, 2)
        inputs.addButton(btnE3, 3)
        btnE3.clicked.connect(self.takePreview)

        btnE4 = InputButton(self)
        btnE4.setText("Extras 4")
        btnE4.setInput(VisualsSystem.extras4)
        layout.addWidget(btnE4, 0, 3)
        inputs.addButton(btnE4, 4)
        btnE4.clicked.connect(self.takePreview)

        btnEVideo = InputButton(self)
        btnEVideo.setText("Visuals PC video")
        btnEVideo.setInput(VisualsSystem.visualsPCVideo)
        layout.addWidget(btnEVideo, 0, 4)
        inputs.addButton(btnEVideo, 8)
        btnEVideo.clicked.connect(self.takePreview)

        self.inputs = inputs

        if self.controller.hasDevice("Extras Scan Converter"):
            scControl = OverscanFreezeWidget()
            layout.addWidget(scControl, 1, 4)
            scControl.btnOverscan.toggled.connect(self.toggleOverscan)
            scControl.btnFreeze.toggled.connect(self.toggleFreeze)

    def currentInput(self):
        button = self.inputs.checkedButton()
        if button is None:
            return None
        return button.input

    def takePreview(self):
        currentInput = self.currentInput()
        if currentInput:
            currentInput.preview(self.controller)
            self.inputSelected.emit(currentInput)

    def toggleOverscan(self):
        try:
            if self.sender().isChecked():
                self.controller["Extras Scan Converter"].overscanOn()
            else:
                self.controller["Extras Scan Converter"].overscanOff()
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleFreeze(self):
        try:
            if self.sender().isChecked():
                self.controller["Extras Scan Converter"].freeze()
            else:
                self.controller["Extras Scan Converter"].unfreeze()
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def errorBox(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()
