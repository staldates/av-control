from avx.devices.net.atem.constants import VideoSource, TransitionStyle
from PySide.QtGui import QWidget, QGridLayout, QHBoxLayout, QButtonGroup, QLabel,\
    QMenu
from staldates.ui.widgets.Buttons import InputButton, FlashingInputButton
from staldates.ui.widgets.OutputsGrid import OutputsGrid
from staldates.ui.CameraControls import CameraControl, AdvancedCameraControl
from staldates.ui.StringConstants import StringConstants
from staldates.ui.widgets.AllInputsPanel import AllInputsPanel
from staldates.ui.widgets.OverlayControl import OverlayControl
from staldates.VisualsSystem import with_atem
from staldates.ui.widgets.FadeToBlackControl import FadeToBlackControl


class VideoSwitcher(QWidget):

    def __init__(self, controller, mainWindow, switcherState):
        super(VideoSwitcher, self).__init__()
        self.mainWindow = mainWindow
        self.atem = controller['ATEM']
        self.controller = controller
        self.switcherState = switcherState
        self.setupUi()

    def setupUi(self):
        layout = QGridLayout()

        inputs_grid = QHBoxLayout()
        self.inputs = QButtonGroup()

        def ifDevice(deviceID, func):
            if self.controller.hasDevice(deviceID):
                return func()
            return (None, None, None)

        self.input_buttons_config = [
            ifDevice("Camera 1", lambda: (VideoSource.INPUT_1, CameraControl(self.controller["Camera 1"]), AdvancedCameraControl("Camera 1", self.controller["Camera 1"], self.mainWindow))),
            ifDevice("Camera 2", lambda: (VideoSource.INPUT_2, CameraControl(self.controller["Camera 2"]), AdvancedCameraControl("Camera 2", self.controller["Camera 2"], self.mainWindow))),
            ifDevice("Camera 3", lambda: (VideoSource.INPUT_3, CameraControl(self.controller["Camera 3"]), AdvancedCameraControl("Camera 3", self.controller["Camera 3"], self.mainWindow))),
            (VideoSource.INPUT_4, QLabel(StringConstants.noDevice), None),
            (VideoSource.INPUT_5, OverlayControl(self.switcherState.dsks[0], self.atem), None),
            (VideoSource.INPUT_6, QLabel(StringConstants.noDevice), None)
        ]

        for source, panel, adv_panel in self.input_buttons_config:
            if source:
                btn = InputButton(self.switcherState.inputs[source])
                btn.setProperty("panel", panel)
                btn.setProperty("adv_panel", adv_panel)
                btn.clicked.connect(self.preview)
                btn.clicked.connect(self.displayPanel)
                btn.longpress.connect(self.displayAdvPanel)
                self.inputs.addButton(btn)
                inputs_grid.addWidget(btn)

        self.extrasBtn = InputButton(None)
        self.inputs.addButton(self.extrasBtn)
        self.extrasBtn.clicked.connect(self.preview)
        self.extrasBtn.clicked.connect(self.displayPanel)

        # An empty menu means the button will be given a "down arrow" icon
        # without actually showing a menu when pressed.
        self.extrasBtn.setMenu(QMenu())

        self.allInputs = AllInputsPanel(self.switcherState)
        self.extrasBtn.setProperty("panel", self.allInputs)

        self.allInputs.inputSelected.connect(self.setExtraInput)

        inputs_grid.addWidget(self.extrasBtn)

        self.blackBtn = FlashingInputButton(self.switcherState.inputs[VideoSource.BLACK])
        inputs_grid.addWidget(self.blackBtn)
        self.inputs.addButton(self.blackBtn)
        self.blackBtn.clicked.connect(self.preview)
        self.blackBtn.clicked.connect(self.displayPanel)
        self.ftb = FadeToBlackControl(self.switcherState.ftb, self.atem)
        self.blackBtn.setProperty("panel", self.ftb)
        self.blackBtn.flashing = self.switcherState.ftb.active
        self.switcherState.ftb.activeChanged.connect(self.blackBtn.setFlashing)

        layout.addLayout(inputs_grid, 0, 0, 1, 7)

        self.og = OutputsGrid(self.switcherState)

        self.og.take.connect(self.take)
        self.og.cut.connect(self.cut)
        self.og.selected.connect(self.sendToAux)
        self.og.mainToAll.connect(self.sendMainToAllAuxes)
        self.og.all.connect(self.sendToAll)

        layout.addWidget(self.og, 1, 5, 1, 2)

        self.blankWidget = QWidget()
        layout.addWidget(self.blankWidget, 1, 0, 1, 5)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 5)

        self.setLayout(layout)

    def setExtraInput(self, inp):
        self.extrasBtn.setInput(inp)
        self.preview()

    @with_atem
    def preview(self):
        checkedButton = self.inputs.checkedButton()
        if checkedButton and checkedButton.input:
            self.og.setAuxesEnabled(True)
            if self.atem:
                self.atem.setPreview(checkedButton.input.source)
        else:
            self.og.setAuxesEnabled(False)

    @with_atem
    def cut(self):
        self.atem.performCut()

    @with_atem
    def take(self):
        self.atem.setNextTransition(TransitionStyle.MIX, bkgd=True, key1=False, key2=False, key3=False, key4=False)
        self.atem.performAutoTake()

    @with_atem
    def sendToAux(self, auxIndex):
        if self.inputs.checkedButton().input:
            self.atem.setAuxSource(auxIndex + 1, self.inputs.checkedButton().input.source)

    @with_atem
    def sendToAll(self):
        if self.inputs.checkedButton().input:
            self.atem.setProgram(self.inputs.checkedButton().input.source)
            for aux in self.switcherState.outputs.keys():
                self.sendToAux(aux)

    @with_atem
    def sendMainToAllAuxes(self):
        for aux in self.switcherState.outputs.keys():
            self.atem.setAuxSource(aux + 1, VideoSource.ME_1_PROGRAM)

    def displayPanel(self):
        panel = self.inputs.checkedButton().property("panel")
        layout = self.layout()
        existing = layout.itemAtPosition(1, 0)
        if existing:
            widget = existing.widget()
            widget.hide()
            layout.removeWidget(widget)
            if panel:
                # display panel
                layout.addWidget(panel, 1, 0, 1, 5)
                panel.show()
            else:
                # hide panel
                layout.addWidget(self.blankWidget, 1, 0, 1, 5)
                self.blankWidget.show()

    def displayAdvPanel(self):
        panel = self.sender().property("adv_panel")
        if panel:
            self.mainWindow.showScreen(panel)
