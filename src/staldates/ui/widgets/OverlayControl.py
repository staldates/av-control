from PySide.QtGui import QWidget, QGridLayout, QLabel, QSpinBox
from staldates.ui.widgets.Buttons import ExpandingButton
from PySide.QtCore import Qt


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

        layout.addWidget(QLabel("Rate:"), 2, 0)

        self.rate = QSpinBox()
        self.rate.setMinimum(1)
        self.rate.setMaximum(250)
        self.rate.valueChanged.connect(self.setRate)
        self.rate.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.rate, 3, 0)

        self.update_from_dsk()

        self.setLayout(layout)

    def update_from_dsk(self):
        self.onAirButton.setChecked(self.dsk.onAir)
        self.rate.setValue(self.dsk.rate)

    def setOnAir(self):
        self.atem.setDSKOnAir(self.dsk.idx, self.onAirButton.isChecked())

    def takeAuto(self):
        self.atem.performDSKAuto(self.dsk.idx)

    def setRate(self, rate):
        self.atem.setDSKRate(self.dsk.idx, rate)
