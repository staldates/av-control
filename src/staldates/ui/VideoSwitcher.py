from PySide.QtGui import QLabel, QWidget, QGridLayout, QHBoxLayout, QButtonGroup, QIcon
from PySide.QtCore import QMetaObject, Qt
from staldates.ui.widgets.Buttons import InputButton, CameraSelectionButton
from staldates.ui.ExtrasSwitcher import ExtrasSwitcher
from staldates.ui.CameraControls import CameraControl, AdvancedCameraControl
from Pyro4.errors import ProtocolError, NamingError
from avx.StringConstants import StringConstants
from staldates.ui.EclipseControls import EclipseControls
import logging
from staldates.ui.widgets.OutputsGrid import OutputsGrid
from staldates import VisualsSystem
from staldates.VisualsSystem import ProxyInput


class VideoSwitcher(QWidget):

    def __init__(self, controller, mainWindow):
        super(VideoSwitcher, self).__init__()
        self.controller = controller
        self.mainWindow = mainWindow
        self.setupUi()

    def setupUi(self):

        gridlayout = QGridLayout()
        self.setLayout(gridlayout)

        ''' Buttons added to inputs should have a numeric ID set equal to their input number on the Aldates main switcher. '''
        self.inputs = QButtonGroup()

        inputsGrid = QHBoxLayout()

        self.btnCamera1 = CameraSelectionButton(1)
        self.btnCamera1.setText("Camera 1")
        self.btnCamera1.setInput(VisualsSystem.camera1)
        inputsGrid.addWidget(self.btnCamera1)
        self.inputs.addButton(self.btnCamera1, 1)
        self.btnCamera1.setIcon(QIcon("icons/camera-video.svg"))

        self.btnCamera2 = CameraSelectionButton(2)
        self.btnCamera2.setText("Camera 2")
        self.btnCamera2.setInput(VisualsSystem.camera2)
        inputsGrid.addWidget(self.btnCamera2)
        self.inputs.addButton(self.btnCamera2, 2)
        self.btnCamera2.setIcon(QIcon("icons/camera-video.svg"))

        self.btnCamera3 = CameraSelectionButton(3)
        self.btnCamera3.setText("Camera 3")
        self.btnCamera3.setInput(VisualsSystem.camera3)
        inputsGrid.addWidget(self.btnCamera3)
        self.inputs.addButton(self.btnCamera3, 3)
        self.btnCamera3.setIcon(QIcon("icons/camera-video.svg"))

        self.btnDVD = InputButton()
        self.btnDVD.setText("DVD")
        self.btnDVD.setInput(VisualsSystem.dvd)
        inputsGrid.addWidget(self.btnDVD)
        self.inputs.addButton(self.btnDVD, 4)
        self.btnDVD.setIcon(QIcon("icons/media-optical.svg"))

        self.btnExtras = InputButton()
        self.btnExtras.setText("Extras")
        inputsGrid.addWidget(self.btnExtras)
        self.btnExtras.setIcon(QIcon("icons/video-display.svg"))
        self.inputs.addButton(self.btnExtras, 5)

        self.btnVisualsPC = InputButton()
        self.btnVisualsPC.setText("Visuals PC")
        self.btnVisualsPC.setInput(VisualsSystem.visualsPC)
        inputsGrid.addWidget(self.btnVisualsPC)
        self.inputs.addButton(self.btnVisualsPC, 6)
        self.btnVisualsPC.setIcon(QIcon("icons/computer.svg"))

        self.btnBlank = InputButton()
        self.btnBlank.setText("Blank")
        self.btnBlank.setInput(VisualsSystem.blank)
        inputsGrid.addWidget(self.btnBlank)
        self.inputs.addButton(self.btnBlank, 0)

        gridlayout.addLayout(inputsGrid, 0, 0, 1, 7)

        self.extrasSwitcher = ExtrasSwitcher(self.controller)
        self.btnExtras.setInput(ProxyInput(self.extrasSwitcher))
        self.blank = QWidget(self)
        gridlayout.addWidget(self.blank, 1, 0, 1, 5)

        self.outputsGrid = OutputsGrid()

        gridlayout.addWidget(self.outputsGrid, 1, 5, 1, 2)

        gridlayout.setRowStretch(0, 1)
        gridlayout.setRowStretch(1, 5)
        QMetaObject.connectSlotsByName(self)
        self.setInputClickHandlers()
        self.setOutputClickHandlers(self.outputsGrid)
        self.configureInnerControlPanels()
        self.gridlayout = gridlayout

    def configureInnerControlPanels(self):
        self.panels = [
            QWidget(),  # Blank
            CameraControl(self.controller["Camera 1"]) if self.controller.hasDevice("Camera 1") else QLabel(StringConstants.noDevice),
            CameraControl(self.controller["Camera 2"]) if self.controller.hasDevice("Camera 2") else QLabel(StringConstants.noDevice),
            CameraControl(self.controller["Camera 3"]) if self.controller.hasDevice("Camera 3") else QLabel(StringConstants.noDevice),
            QLabel(StringConstants.noDevice),  # DVD - no controls
            self.extrasSwitcher if self.controller.hasDevice("Extras") else QLabel(StringConstants.noDevice),  # Extras
            EclipseControls(self.controller, "Main Scan Converter") if self.controller.hasDevice("Main Scan Converter") else QLabel(StringConstants.noDevice),  # Visuals PC
        ]
        self.advPanels = [
            None,
            AdvancedCameraControl("Camera 1", self.controller["Camera 1"], self.mainWindow),
            AdvancedCameraControl("Camera 2", self.controller["Camera 2"], self.mainWindow),
            AdvancedCameraControl("Camera 3", self.controller["Camera 3"], self.mainWindow),
            None,
            None,
            None
        ]

    def setInputClickHandlers(self):
        for btn in self.inputs.buttons():
            btn.clicked.connect(self.handleInputSelect)
            btn.longpress.connect(self.showAdvPanel)

    def setOutputClickHandlers(self, outputsGrid):
        outputsGrid.connectMainOutputs(self.handleOutputSelect)
        ''' btnPCMix is a special case since that's on a different switcher '''
        outputsGrid.connectPreviewOutputs(self.handlePCMixSelect)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_0:
            self.btnBlank.click()
        elif e.key() == Qt.Key_1:
            self.btnCamera1.click()
        elif e.key() == Qt.Key_2:
            self.btnCamera2.click()
        elif e.key() == Qt.Key_3:
            self.btnCamera3.click()
        elif e.key() == Qt.Key_4:
            self.btnDVD.click()
        elif e.key() == Qt.Key_5:
            self.btnExtras.click()
        elif e.key() == Qt.Key_6:
            self.btnVisualsPC.click()
        elif e.key() == Qt.Key_Space:
            self.outputsGrid.btnAll.click()
        else:
            self.panels[self.inputs.checkedId()].keyPressEvent(e)

    def keyReleaseEvent(self, e):
        self.panels[self.inputs.checkedId()].keyReleaseEvent(e)

    def handleInputSelect(self):
        inputID = self.inputs.checkedId()
        logging.debug("Input selected: " + str(inputID))
        if inputID >= 0:
            try:
                myInput = self.inputs.checkedButton().input
                if myInput:
                    myInput.preview(self.controller)
            except NamingError:
                self.mainWindow.errorBox(StringConstants.nameErrorText)
            except ProtocolError:
                self.mainWindow.errorBox(StringConstants.protocolErrorText)
        self.gridlayout.removeWidget(self.gridlayout.itemAtPosition(1, 0).widget())
        for p in self.panels:
            p.hide()
        chosenPanel = self.panels[inputID]
        self.gridlayout.addWidget(chosenPanel, 1, 0, 1, 5)
        chosenPanel.show()

        # Prevent certain options from being selectable
        if inputID == 6 or inputID == 0:
            self.outputsGrid.btnPCMix.setEnabled(False)
        else:
            self.outputsGrid.btnPCMix.setEnabled(True)

    def handleOutputSelect(self):
        outputChannel = self.sender().ID
        inputID = self.inputs.checkedId()
        checkedExtrasButton = self.extrasSwitcher.inputs.checkedButton()
        inputChannel = checkedExtrasButton.input if (inputID == 5 and checkedExtrasButton) else self.inputs.checkedButton().input
        if inputChannel:
            try:
                inputChannel.toMain(self.controller, outputChannel)
            except NamingError:
                self.mainWindow.errorBox(StringConstants.nameErrorText)
            except ProtocolError:
                self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def handlePCMixSelect(self):
        inputID = self.inputs.checkedId()
        checkedExtrasButton = self.extrasSwitcher.inputs.checkedButton()
        checkedExtrasButton
        inputChannel = checkedExtrasButton.input if (inputID == 5 and checkedExtrasButton) else self.inputs.checkedButton().input
        if inputChannel:
            try:
                inputChannel.toPCMix(self.controller)
            except NamingError:
                self.mainWindow.errorBox(StringConstants.nameErrorText)
            except ProtocolError:
                self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def showAdvPanel(self):
        sender = self.sender()
        inputID = self.sender().ID if hasattr(sender, "ID") else None
        if inputID is not None and self.advPanels[inputID] is not None:
            self.mainWindow.showScreen(self.advPanels[inputID])

    def updateOutputMappings(self, mapping):
        self.outputsGrid.updateOutputMappings(mapping)
