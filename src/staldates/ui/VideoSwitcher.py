from PySide.QtGui import QLabel, QWidget, QGridLayout, QHBoxLayout, QButtonGroup, QIcon
from PySide.QtCore import QMetaObject, Qt, Slot
from staldates.ui.widgets.Buttons import InputButton, CameraSelectionButton
from staldates.ui.ExtrasSwitcher import ExtrasSwitcher
from staldates.ui.CameraControls import CameraControl, AdvancedCameraControl
from staldates.ui.EclipseControls import EclipseControls
import logging
from staldates.ui.StringConstants import StringConstants
from staldates.ui.widgets.OutputsGrid import OutputsGrid
from staldates.VisualsSystem import IOEnum, MainSwitcherInputs, MainSwitcher


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
        self.btnCamera1.setInput(MainSwitcherInputs.camera1)
        inputsGrid.addWidget(self.btnCamera1)
        self.inputs.addButton(self.btnCamera1, 1)
        self.btnCamera1.setIcon(QIcon(":icons/camera-video"))

        self.btnCamera2 = CameraSelectionButton(2)
        self.btnCamera2.setInput(MainSwitcherInputs.camera2)
        inputsGrid.addWidget(self.btnCamera2)
        self.inputs.addButton(self.btnCamera2, 2)
        self.btnCamera2.setIcon(QIcon(":icons/camera-video"))

        self.btnCamera3 = CameraSelectionButton(3)
        self.btnCamera3.setInput(MainSwitcherInputs.camera3)
        inputsGrid.addWidget(self.btnCamera3)
        self.inputs.addButton(self.btnCamera3, 3)
        self.btnCamera3.setIcon(QIcon(":icons/camera-video"))

        self.btnDVD = InputButton()
        self.btnDVD.setInput(MainSwitcherInputs.dvd)
        inputsGrid.addWidget(self.btnDVD)
        self.inputs.addButton(self.btnDVD, 4)
        self.btnDVD.setIcon(QIcon(":icons/media-optical"))

        self.btnExtras = InputButton()
        self.btnExtras.setText("Extras")
        inputsGrid.addWidget(self.btnExtras)
        self.btnExtras.setIcon(QIcon(":icons/video-display"))
        self.inputs.addButton(self.btnExtras, 5)

        self.btnVisualsPC = InputButton()
        self.btnVisualsPC.setInput(MainSwitcherInputs.visualsPC)
        inputsGrid.addWidget(self.btnVisualsPC)
        self.inputs.addButton(self.btnVisualsPC, 6)
        self.btnVisualsPC.setIcon(QIcon(":icons/computer"))

        self.btnBlank = InputButton()
        self.btnBlank.setInput(MainSwitcherInputs.blank)
        inputsGrid.addWidget(self.btnBlank)
        self.inputs.addButton(self.btnBlank, 0)

        gridlayout.addLayout(inputsGrid, 0, 0, 1, 7)

        self.extrasSwitcher = ExtrasSwitcher(self.controller)
        self.extrasSwitcher.inputSelected.connect(self.handleExtrasSelect)
        self.btnExtras.setInput(None)
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
            EclipseControls(self.controller["Main Scan Converter"]) if self.controller.hasDevice("Main Scan Converter") else QLabel(StringConstants.noDevice),  # Visuals PC
        ]
        self.advPanels = [
            None,
            AdvancedCameraControl("Camera 1", self.controller["Camera 1"], self.mainWindow) if self.controller.hasDevice("Camera 1") else None,
            AdvancedCameraControl("Camera 2", self.controller["Camera 2"], self.mainWindow) if self.controller.hasDevice("Camera 1") else None,
            AdvancedCameraControl("Camera 3", self.controller["Camera 3"], self.mainWindow) if self.controller.hasDevice("Camera 1") else None,
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
        myInput = self.inputs.checkedButton().input
        logging.debug("Input selected: " + str(myInput))
        if inputID >= 0 and myInput:
            myInput.preview(self.controller)
        self.gridlayout.removeWidget(self.gridlayout.itemAtPosition(1, 0).widget())
        for p in self.panels:
            p.hide()
        chosenPanel = self.panels[inputID]
        self.gridlayout.addWidget(chosenPanel, 1, 0, 1, 5)
        chosenPanel.show()

        # Prevent certain options from being selectable
        if myInput == MainSwitcher.input.visualsPC or myInput == MainSwitcher.input.blank:
            self.outputsGrid.setEnabled(True)
            self.outputsGrid.btnPCMix.setEnabled(False)
        elif myInput is None:
            self.outputsGrid.setEnabled(False)
            self.outputsGrid.btnPCMix.setEnabled(True)
        else:
            self.outputsGrid.setEnabled(True)
            self.outputsGrid.btnPCMix.setEnabled(True)

    def handleOutputSelect(self):
        outputChannel = self.sender().ID
        inputChannel = self.inputs.checkedButton().input
        if inputChannel:
            inputChannel.toMain(self.controller, outputChannel)

    def handlePCMixSelect(self):
        inputChannel = self.inputs.checkedButton().input
        if inputChannel:
            inputChannel.toPCMix(self.controller)

    @Slot(IOEnum)
    def handleExtrasSelect(self, extrasInput):
        if extrasInput is not None:
            self.outputsGrid.inputNames[5] = extrasInput.label
        else:
            # Not sure under what circumstances, if any, this will arise
            self.btnExtras.setText("Extras")
            self.outputsGrid.inputNames[5] = "Extras"
        self.btnExtras.setInput(extrasInput)
        self.handleInputSelect()

    def showAdvPanel(self):
        sender = self.sender()
        inputID = self.sender().ID if hasattr(sender, "ID") else None
        if inputID is not None and self.advPanels[inputID] is not None:
            self.mainWindow.showScreen(self.advPanels[inputID])

    def updateOutputMappings(self, mapping):
        print mapping
        self.outputsGrid.updateOutputMappings(mapping)
