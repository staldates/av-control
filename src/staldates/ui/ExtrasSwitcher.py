'''
Created on 10 Nov 2012

@author: james
'''
from PySide.QtGui import QWidget, QGridLayout, QHBoxLayout, QButtonGroup, QPixmap, QLabel, QSizePolicy
from PySide.QtCore import Signal
from staldates.ui.widgets.Buttons import InputButton
from staldates.ui.widgets.Dialogs import handlePyroErrors
from staldates.ui.widgets.ScanConverterControls import OverscanFreezeWidget
from staldates.VisualsSystem import ExtrasSwitcherInputs


class ExtrasSwitcher(QWidget):
    '''
    The extras switcher.
    '''

    inputSelected = Signal(object)

    def __init__(self, controller):
        super(ExtrasSwitcher, self).__init__()
        self.controller = controller
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)

        inputs = QButtonGroup()

        btnE1 = InputButton(self)
        btnE1.setInput(ExtrasSwitcherInputs.extras1)
        layout.addWidget(btnE1, 0, 0)
        inputs.addButton(btnE1, 1)
        btnE1.clicked.connect(self.takePreview)

        btnE2 = InputButton(self)
        btnE2.setInput(ExtrasSwitcherInputs.extras2)
        layout.addWidget(btnE2, 0, 1)
        inputs.addButton(btnE2, 2)
        btnE2.clicked.connect(self.takePreview)

        btnE3 = InputButton(self)
        btnE3.setInput(ExtrasSwitcherInputs.extras3)
        layout.addWidget(btnE3, 0, 2)
        inputs.addButton(btnE3, 3)
        btnE3.clicked.connect(self.takePreview)

        btnE4 = InputButton(self)
        btnE4.setInput(ExtrasSwitcherInputs.extras4)
        layout.addWidget(btnE4, 0, 3)
        inputs.addButton(btnE4, 4)
        btnE4.clicked.connect(self.takePreview)

        btnEVideo = InputButton(self)
        btnEVideo.setInput(ExtrasSwitcherInputs.visualsPCVideo)
        layout.addWidget(btnEVideo, 0, 4)
        inputs.addButton(btnEVideo, 8)
        btnEVideo.clicked.connect(self.takePreview)

        self.inputs = inputs

        self._maybeAddScanConverterControls(layout)

        self.noInputWarning = NoInputSelectedWarning(self)
        layout.addWidget(self.noInputWarning, 1, 0, 1, 4)

    @handlePyroErrors
    def _maybeAddScanConverterControls(self, layout):
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

    def takePreview(self, *args):
        currentInput = self.currentInput()
        if currentInput:
            currentInput.preview(self.controller)
            self.inputSelected.emit(currentInput)
            self.noInputWarning.setVisible(False)
        else:
            self.noInputWarning.setVisible(True)

    @handlePyroErrors
    def toggleOverscan(self, overscan):
        if overscan:
            self.controller["Extras Scan Converter"].overscanOn()
        else:
            self.controller["Extras Scan Converter"].overscanOff()

    @handlePyroErrors
    def toggleFreeze(self, freeze):
        if freeze:
            self.controller["Extras Scan Converter"].freeze()
        else:
            self.controller["Extras Scan Converter"].unfreeze()


class NoInputSelectedWarning(QWidget):
    def __init__(self, parent=None):
        super(NoInputSelectedWarning, self).__init__(parent)
        layout = QHBoxLayout()

        img = QLabel(self)
        img.setPixmap(QPixmap(":icons/warning"))
        img.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(img)
        layout.addWidget(QLabel("No input is currently selected"))

        self.setLayout(layout)
