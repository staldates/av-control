from PySide.QtGui import QFrame, QGridLayout, QLabel
from staldates.ui.widgets.Buttons import OutputButton, ExpandingButton
from PySide.QtCore import Signal, QSignalMapper, Qt


class MainMixControl(QFrame):
    cut = Signal()
    take = Signal()

    def __init__(self, parent=None):
        super(MainMixControl, self).__init__(parent)
        layout = QGridLayout()

        label = QLabel('Main mix', None)
        label.setAlignment(Qt.AlignHCenter)
        layout.addWidget(label, 0, 0, 1, 2)

        btnTake = ExpandingButton()
        btnTake.setProperty("class", "mainMix")
        btnTake.setText("Cut")
        btnTake.clicked.connect(self.cut.emit)
        layout.addWidget(btnTake, 1, 0)

        btnFade = ExpandingButton()
        btnFade.setProperty("class", "mainMix")
        btnFade.setText("Fade")
        btnFade.clicked.connect(self.take.emit)
        layout.addWidget(btnFade, 1, 1)

        self.setLayout(layout)


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

        mainMixFrame = MainMixControl()
        mainMixFrame.cut.connect(self.cut.emit)
        mainMixFrame.take.connect(self.take.emit)

        layout.addWidget(mainMixFrame, 0, 0, 1, 2)

        self.aux_buttons = []

        for idx, output in switcherState.outputs.iteritems():
            ob = OutputButton(output)
            layout.addWidget(ob, 1 + (idx / 2), idx % 2)
            ob.clicked.connect(self.signalMapper.map)
            self.signalMapper.setMapping(ob, idx)
            self.aux_buttons.append(ob)

        self.signalMapper.mapped.connect(self.registerClick)

        btnAll = ExpandingButton()
        btnAll.setProperty("class", "mainMix")
        btnAll.setText("Mix to all")
        btnAll.clicked.connect(self.mainToAll.emit)
        layout.addWidget(btnAll, 4, 0)

        self.btnAll = ExpandingButton()
        self.btnAll.setText("All")
        self.btnAll.clicked.connect(self.all.emit)
        layout.addWidget(self.btnAll, 4, 1)

        layout.setColumnMinimumWidth(0, 100)
        layout.setColumnMinimumWidth(1, 100)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        layout.setRowStretch(0, 2)
        for i in range(1, 5):
            layout.setRowStretch(i, 1)

        self.setLayout(layout)

    def registerClick(self, idx):
        self.selected.emit(idx)

    def setAuxesEnabled(self, enabled):
        for button in self.aux_buttons:
            button.setEnabled(enabled)
        self.btnAll.setEnabled(enabled)
