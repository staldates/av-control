from PySide.QtCore import Signal
from PySide.QtGui import QWidget, QVBoxLayout, QScrollArea, QGridLayout
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

        self.inputsGrid = QGridLayout()
        scrollArea.setLayout(self.inputsGrid)

        layout.addWidget(scrollArea)
        self.setLayout(layout)

        self.displayInputs()

    def displayInputs(self):
        while not self.inputsGrid.isEmpty():
            item = self.inputsGrid.takeAt(0)
            self.inputsGrid.removeItem(item)

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
                    idx += 1

    def selectInput(self):
        inputBtn = self.sender()
        self.inputSelected.emit(inputBtn.input)
