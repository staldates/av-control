from PySide.QtCore import Signal
from PySide.QtGui import QWidget, QGridLayout, QButtonGroup, QIcon
from staldates.VisualsSystem import Input
from avx.devices.net.atem.constants import VideoSource
from staldates.ui.widgets.Buttons import InputButton, ExpandingButton


class AllInputsPanel(QWidget):

    inputSelected = Signal(Input)

    def __init__(self, switcherState, parent=None):
        super(AllInputsPanel, self).__init__(parent)

        self.switcherState = switcherState
        self.selectedInput = None
        self.page = 0
        self.sources = []

        self.layout = QGridLayout()
        self.input_buttons = QButtonGroup()

        self.btnPageUp = ExpandingButton()
        self.btnPageUp.setIcon(QIcon(":icons/go-up"))
        self.btnPageUp.clicked.connect(lambda: self.setPage(self.page - 1))
        self.layout.addWidget(self.btnPageUp, 0, 5, 3, 1)

        self.btnPageDown = ExpandingButton()
        self.btnPageDown.setIcon(QIcon(":icons/go-down"))
        self.btnPageDown.clicked.connect(lambda: self.setPage(self.page + 1))
        self.layout.addWidget(self.btnPageDown, 3, 5, 3, 1)

        for col in range(5):
            self.layout.setColumnStretch(col, 1)
            for row in range(3):
                btn = InputButton(None)
                self.layout.addWidget(btn, row * 2, col, 2, 1)
                self.input_buttons.addButton(btn)
                btn.clicked.connect(self.selectInput)
                btn.setFixedWidth(120)

        self.setLayout(self.layout)

        def handle_inputs_changed():
            self.setSources()
            self.displayInputs()

        self.switcherState.inputsChanged.connect(handle_inputs_changed)
        handle_inputs_changed()

    def setSources(self):
        self.sources = [vs for vs in VideoSource if vs in self.switcherState.inputs.keys()]

    def displayInputs(self):

        idx = 0
        start = self.page * 15
        end = start + 15

        self.input_buttons.setExclusive(False)
        for btn in self.input_buttons.buttons():
            btn.hide()
            btn.setChecked(False)
        self.input_buttons.setExclusive(True)

        for vs in self.sources[start:end]:
            inp = self.switcherState.inputs[vs]
            row = (idx / 5) * 2
            col = idx % 5

            btn = self.layout.itemAtPosition(row, col).widget()
            btn.setInput(inp)
            btn.setChecked(inp == self.selectedInput)
            btn.show()

            idx += 1

        self.btnPageUp.setEnabled(self.page > 0)
        self.btnPageDown.setEnabled(end < len(self.switcherState.inputs))

    def setPage(self, page):
        self.page = page
        self.displayInputs()

    def selectInput(self):
        inputBtn = self.sender()
        self.selectedInput = inputBtn.input
        self.inputSelected.emit(inputBtn.input)
