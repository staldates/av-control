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
        layout.addWidget(og, 1, 5, 1, 2)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 5)

        self.setLayout(layout)

    def preview(self):
        self.atem.setPreview(self.inputs.checkedButton().input.source)
