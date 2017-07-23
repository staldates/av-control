from avx.devices.net.atem.constants import VideoSource
from PySide.QtGui import QWidget, QGridLayout, QHBoxLayout, QButtonGroup
from staldates.ui.widgets.Buttons import InputButton
from staldates.ui.widgets.OutputsGrid import OutputsGrid
from staldates.ui.CameraControls import CameraControl


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

        input_buttons_config = [
            (VideoSource.INPUT_1, CameraControl(self.controller["Camera 1"]) if self.controller.hasDevice("Camera 1") else None, None),
            (VideoSource.INPUT_2, CameraControl(self.controller["Camera 2"]) if self.controller.hasDevice("Camera 2") else None, None),
            (VideoSource.INPUT_4, None, None),
            (VideoSource.INPUT_5, None, None),
            (VideoSource.INPUT_6, None, None),
            (VideoSource.BLACK, None, None)
        ]

        for source, panel, adv_panel in input_buttons_config:
            btn = InputButton(self.switcherState.inputs[source])
            btn.setProperty("panel", panel)
            btn.setProperty("adv_panel", adv_panel)
            btn.clicked.connect(self.preview)
            btn.clicked.connect(self.displayPanel)
            btn.longpress.connect(self.displayAdvPanel)
            self.inputs.addButton(btn)
            inputs_grid.addWidget(btn)

        layout.addLayout(inputs_grid, 0, 0, 1, 7)

        og = OutputsGrid(self.switcherState)

        og.take.connect(self.take)
        og.selected.connect(self.sendToAux)
        og.mainToAll.connect(self.sendMainToAllAuxes)
        og.all.connect(self.sendToAll)

        layout.addWidget(og, 1, 5, 1, 2)

        self.blankWidget = QWidget()
        layout.addWidget(self.blankWidget, 1, 0, 1, 5)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 5)

        self.setLayout(layout)

    def preview(self):
        self.atem.setPreview(self.inputs.checkedButton().input.source)

    def take(self):
        self.atem.performCut()

    def sendToAux(self, auxIndex):
        self.atem.setAuxSource(auxIndex + 1, self.inputs.checkedButton().input.source)

    def sendToAll(self):
        self.take()
        for aux in self.switcherState.outputs.keys():
            self.sendToAux(aux)

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
        pass
