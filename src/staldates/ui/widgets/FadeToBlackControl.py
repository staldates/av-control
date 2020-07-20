from PySide.QtGui import QWidget, QGridLayout, QLabel
from staldates.ui.widgets.TouchSpinner import FrameRateTouchSpinner
from staldates.ui.widgets.Buttons import ExpandingButton
from PySide.QtCore import Qt


class FadeToBlackControl(QWidget):
    def __init__(self, ftb, atem, me=1, parent=None):
        super(FadeToBlackControl, self).__init__(parent)
        self.atem = atem
        self.ftb = ftb
        self.me = me

        layout = QGridLayout()

        lblRate = QLabel("Rate")
        lblRate.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        layout.addWidget(lblRate, 0, 0)

        self.rate = FrameRateTouchSpinner()
        self.rate.setValue(self.ftb.rate)

        layout.addWidget(self.rate, 1, 0)

        self.btnFade = ExpandingButton()
        self.btnFade.setText("Fade to Black")
        self.btnFade.setCheckable(True)
        self.btnFade.setChecked(self.ftb.active)
        layout.addWidget(self.btnFade, 1, 1)

        self.ftb.rateChanged.connect(self.rate.setValue)
        self.ftb.activeChanged.connect(self.btnFade.setChecked)

        if self.atem:
            self.rate.valueChanged.connect(lambda v: self.atem.setFadeToBlackRate(v, me=self.me))
            self.btnFade.clicked.connect(lambda: self.atem.performFadeToBlack(me=self.me))

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)

        self.setLayout(layout)
