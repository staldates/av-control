from PySide.QtGui import QFrame, QGridLayout
from staldates.ui.widgets.Buttons import OutputButton, ExpandingButton
from PySide.QtCore import Signal, QSignalMapper


class OutputsGrid(QFrame):

    cut = Signal()
    take = Signal()
    mainToAll = Signal()
    all = Signal()
    selected = Signal(int)

    def __init__(self, switcherState, parent=None):
        super(OutputsGrid, self).__init__(parent)

        self.signalMapper = QSignalMapper(self)

        layout = QGridLayout()

        btnTake = ExpandingButton()
        btnTake.setText("Cut")
        btnTake.clicked.connect(self.cut.emit)
        layout.addWidget(btnTake, 0, 0)

        btnFade = ExpandingButton()
        btnFade.setText("Fade")
        btnFade.clicked.connect(self.take.emit)
        layout.addWidget(btnFade, 0, 1)

        self.aux_buttons = []

        for idx, output in switcherState.outputs.iteritems():
            ob = OutputButton(output)
            layout.addWidget(ob, 1 + (idx / 2), idx % 2)
            ob.clicked.connect(self.signalMapper.map)
            self.signalMapper.setMapping(ob, idx)
            self.aux_buttons.append(ob)

        self.signalMapper.mapped.connect(self.registerClick)

        btnMainToAll = ExpandingButton()
        btnMainToAll.setText("Main to\nall auxes")
        btnMainToAll.clicked.connect(self.mainToAll.emit)
        layout.addWidget(btnMainToAll, 4, 0)

        self.btnAll = ExpandingButton()
        self.btnAll.setText("All")
        self.btnAll.clicked.connect(self.all.emit)
        layout.addWidget(self.btnAll, 4, 1)

        layout.setColumnMinimumWidth(0, 100)
        layout.setColumnMinimumWidth(1, 100)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)

    def registerClick(self, idx):
        self.selected.emit(idx)

    def setAuxesEnabled(self, enabled):
        for button in self.aux_buttons:
            button.setEnabled(enabled)
        self.btnAll.setEnabled(enabled)
