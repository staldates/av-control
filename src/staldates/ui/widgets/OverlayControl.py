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

        lbl = QLabel("Overlay on main output:")
        lbl.setAlignment(Qt.AlignHCenter)
        layout.addWidget(lbl, 0, 0, 1, 2)

        self.autoButton = ExpandingButton()
        self.autoButton.setText("Auto Fade")
        self.autoButton.clicked.connect(self.takeAuto)

        layout.addWidget(self.autoButton, 1, 0)

        self.onAirButton = ExpandingButton()
        self.onAirButton.setText("On Air")
        self.onAirButton.setCheckable(True)
        self.onAirButton.clicked.connect(self.setOnAir)

        layout.addWidget(self.onAirButton, 1, 1, 3, 1)

        lblRate = QLabel("Rate:")
        lblRate.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        layout.addWidget(lblRate, 2, 0)

        self.rate = QSpinBox()
        self.rate.setMinimum(1)
        self.rate.setMaximum(250)
        self.rate.valueChanged.connect(self.setRate)
        self.rate.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.rate, 3, 0)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)

        self.update_from_dsk()

        self.setLayout(layout)

    def update_from_dsk(self):
        self.onAirButton.setChecked(self.dsk.onAir)
        self.onAirButton.setProperty("isLive", self.dsk.onAir)
        self.onAirButton.style().unpolish(self.onAirButton)
        self.onAirButton.style().polish(self.onAirButton)
        self.rate.setValue(self.dsk.rate)

    def setOnAir(self):
        self.atem.setDSKOnAir(self.dsk.idx, self.onAirButton.isChecked())

    def takeAuto(self):
        self.atem.performDSKAuto(self.dsk.idx)

    def setRate(self, rate):
        self.atem.setDSKRate(self.dsk.idx, rate)
