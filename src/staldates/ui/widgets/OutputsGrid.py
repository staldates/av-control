from PySide.QtGui import QFrame, QGridLayout
from staldates.ui.widgets.Buttons import OutputButton, ExpandingButton
from PySide.QtCore import Signal


class OutputsGrid(QFrame):

    take = Signal()
    mainToAll = Signal()
    press = Signal()

    def __init__(self, switcherState, parent=None):
        super(OutputsGrid, self).__init__(parent)

        layout = QGridLayout()

        btnMain = ExpandingButton()
        btnMain.setText("Church / Main")
        layout.addWidget(btnMain, 0, 0, 1, 2)

        for idx, output in switcherState.outputs.iteritems():
            ob = OutputButton(output)
            layout.addWidget(ob, 1 + (idx / 2), idx % 2)

        btnMainToAll = ExpandingButton()
        btnMainToAll.setText("Main to\nall auxes")
        layout.addWidget(btnMainToAll, 4, 0)

        btnAll = ExpandingButton()
        btnAll.setText("All")
        layout.addWidget(btnAll, 4, 1)

        layout.setColumnMinimumWidth(0, 100)
        layout.setColumnMinimumWidth(1, 100)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(1, 1)

        self.setLayout(layout)
