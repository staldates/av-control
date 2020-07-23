from avx.devices.net.atem.constants import VideoSource
from PySide.QtCore import Qt
from PySide.QtGui import QWidget, QGridLayout, QLabel
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.VisualsSystem import with_atem
from staldates.ui.widgets.TouchSpinner import FrameRateTouchSpinner


class OverlayControl(QWidget):

    def __init__(self, usk, mixTransition, atem, parent=None):
        super(OverlayControl, self).__init__(parent)
        self.atem = atem
        self.usk = usk
        self.mixTransition = mixTransition

        usk.changedState.connect(self.update_from_usk)

        layout = QGridLayout()

        lbl = QLabel("Overlay on main output:")
        lbl.setAlignment(Qt.AlignHCenter)
        layout.addWidget(lbl, 0, 0, 2, 1)

        self.onAirButton = ExpandingButton()
        self.onAirButton.setText("On Air")
        self.onAirButton.setCheckable(True)
        self.onAirButton.clicked.connect(self.setOnAir)

        layout.addWidget(self.onAirButton, 0, 1, 2, 1)

        self.autoButton = ExpandingButton()
        self.autoButton.setText("Auto Fade")
        self.autoButton.clicked.connect(self.takeAuto)

        layout.addWidget(self.autoButton, 2, 1, 2, 1)

        lblRate = QLabel("Fade rate:")
        lblRate.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        layout.addWidget(lblRate, 2, 0)

        self.rate = FrameRateTouchSpinner()
        self.rate.setMinimum(1)
        self.rate.setMaximum(250)
        self.rate.valueChanged.connect(self.setRate)
        self.mixTransition.changedProps.connect(self.update_from_mix_transition)
        layout.addWidget(self.rate, 3, 0)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)

        self.resetParams()
        self.update_from_usk()
        self.update_from_mix_transition()

        self.setLayout(layout)

    def update_from_usk(self):
        self.onAirButton.setChecked(self.usk.onAir)
        self.onAirButton.setProperty("isLive", self.usk.onAir)
        self.onAirButton.style().unpolish(self.onAirButton)
        self.onAirButton.style().polish(self.onAirButton)

    def update_from_mix_transition(self):
        self.rate.setValue(self.mixTransition.rate)

    @with_atem
    def setRate(self, rate):
        self.atem.setMixTransitionRate(
            rate,
            self.usk.me_index + 1
        )

    @with_atem
    def setOnAir(self):
        self.atem.setUSKOnAir(
            self.usk.me_index + 1,
            self.usk.keyer_index + 1,
            self.onAirButton.isChecked()
        )

    @with_atem
    def takeAuto(self):
        self.atem.setNextTransition(
            TransitionStyle.MIX,
            bkgd=False,
            key1=self.usk.keyer_index == 0,
            key2=self.usk.keyer_index == 1,
            key3=self.usk.keyer_index == 2,
            key4=self.usk.keyer_index == 3,
            me=self.me
        )
        self.atem.performAutoTake(me=self.me)

    @with_atem
    def resetParams(self):
        self.atem.setUSKFillSource(
            self.usk.me_index + 1,
            self.usk.keyer_index + 1,
            VideoSource.INPUT_5
        )
        self.atem.setUSKKeySource(
            self.usk.me_index + 1,
            self.usk.keyer_index + 1,
            VideoSource.INPUT_5
        )
        self.atem.setUSKParams(
            self.usk.me_index + 1,
            self.usk.keyer_index + 1,
            preMultiplied=False,
            gain=500,
            clip=210,
            invert=False
        )
