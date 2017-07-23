from PySide.QtGui import QWidget, QGridLayout, QLabel
from staldates.ui.widgets.Buttons import ExpandingButton


class OverlayControl(QWidget):

    def __init__(self, dsk, atem, parent=None):
        super(OverlayControl, self).__init__(parent)
        self.atem = atem
        self.dsk = dsk

        dsk.changedState.connect(self.update_from_dsk)

        layout = QGridLayout()

        layout.addWidget(QLabel("Overlay on main output:"), 0, 0, 1, 2)

        self.autoButton = ExpandingButton()
        self.autoButton.setText("Auto Fade")
        self.autoButton.clicked.connect(self.takeAuto)

        layout.addWidget(self.autoButton, 1, 0)

        self.onAirButton = ExpandingButton()
        self.onAirButton.setText("On Air")
        self.onAirButton.setCheckable(True)
        self.onAirButton.clicked.connect(self.setOnAir)

        layout.addWidget(self.onAirButton, 1, 1)
        self.update_from_dsk()

        self.setLayout(layout)

    def update_from_dsk(self):
        self.onAirButton.setChecked(self.dsk.onAir)

    def setOnAir(self):
        self.atem.setDSKOnAir(self.dsk.idx, self.onAirButton.isChecked())

    def takeAuto(self):
        self.atem.performDSKAuto(self.dsk.idx)
