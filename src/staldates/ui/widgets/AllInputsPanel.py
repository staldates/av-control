from PySide.QtCore import Signal
from PySide.QtGui import QWidget, QVBoxLayout, QScrollArea, QGridLayout,\
    QButtonGroup
from staldates.VisualsSystem import Input
from avx.devices.net.atem.constants import VideoSource
from staldates.ui.widgets.Buttons import InputButton


class AllInputsPanel(QWidget):

    inputSelected = Signal(Input)

    def __init__(self, switcherState, parent=None):
        super(AllInputsPanel, self).__init__(parent)

        self.switcherState = switcherState

        layout = QVBoxLayout()

        scrollArea = QScrollArea()

        self.input_buttons = QButtonGroup()

        self.inputsGrid = QGridLayout()
        scrollArea.setLayout(self.inputsGrid)

        layout.addWidget(scrollArea)
        self.setLayout(layout)

        self.displayInputs()

    def displayInputs(self):
        for btn in self.input_buttons.buttons()[:]:
            self.inputsGrid.removeWidget(btn)
            self.input_buttons.removeButton(btn)

        idx = 0
        for vs in VideoSource:
            if vs in self.switcherState.inputs.keys():
                inp = self.switcherState.inputs[vs]
                if inp.canBeUsed:
                    btn = InputButton(inp)

                    btn.clicked.connect(self.selectInput)

                    row = idx / 5
                    col = idx % 5
                    self.inputsGrid.addWidget(btn, row, col)
                    self.input_buttons.addButton(btn)
                    btn.setMinimumHeight(100)
                    idx += 1

    def selectInput(self):
        inputBtn = self.sender()
        self.inputSelected.emit(inputBtn.input)
