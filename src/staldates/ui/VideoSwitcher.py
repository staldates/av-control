from PySide.QtGui import QWidget, QGridLayout, QHBoxLayout, QButtonGroup
from staldates.ui.widgets.Buttons import InputButton
from avx.devices.net.atem.constants import VideoSource
from staldates.ui.widgets.OutputsGrid import OutputsGrid


class VideoSwitcher(QWidget):

    def __init__(self, atem, mainWindow, switcherState):
        super(VideoSwitcher, self).__init__()
        self.mainWindow = mainWindow
        self.atem = atem
        self.switcherState = switcherState
        self.setupUi()

    def setupUi(self):
        layout = QGridLayout()

        inputs_grid = QHBoxLayout()
        self.inputs = QButtonGroup()

        input_buttons_config = [
            (VideoSource.INPUT_1, None, None),
            (VideoSource.INPUT_2, None, None),
            (VideoSource.INPUT_4, None, None),
            (VideoSource.INPUT_5, None, None),
            (VideoSource.INPUT_6, None, None),
            (VideoSource.BLACK, None, None)
        ]

        for source, _, _ in input_buttons_config:
            btn = InputButton(self.switcherState.inputs[source])
            btn.clicked.connect(self.preview)
            self.inputs.addButton(btn)
            inputs_grid.addWidget(btn)

        layout.addLayout(inputs_grid, 0, 0, 1, 7)

        og = OutputsGrid(self.switcherState)

        og.take.connect(self.take)
        og.selected.connect(self.sendToAux)
        og.mainToAll.connect(self.sendMainToAllAuxes)
        og.all.connect(self.sendToAll)

        layout.addWidget(og, 1, 5, 1, 2)

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
