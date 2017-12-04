from PySide.QtGui import QWidget, QFormLayout, QVBoxLayout
from staldates.ui.widgets.Labels import TitleLabel
from staldates.ui.widgets.TouchSpinner import FrameRateTouchSpinner
from staldates.VisualsSystem import with_atem


class PreferencesWidget(QWidget):
    def __init__(self, controller, transition, parent=None):
        super(PreferencesWidget, self).__init__(parent)
        self.controller = controller
        self.transition = transition
        self.atem = controller['ATEM']

        layout = QVBoxLayout()

        layout.addWidget(TitleLabel('Preferences'))

        prefsLayout = QFormLayout()

        mixRate = FrameRateTouchSpinner()
        mixRate.setValue(transition.rate)
        mixRate.setMaximum(250)
        mixRate.setMinimum(1)
        mixRate.valueChanged.connect(self.setMixRate)

        prefsLayout.addRow('Mix rate:', mixRate)

        layout.addLayout(prefsLayout)
        self.setLayout(layout)

    @with_atem
    def setMixRate(self, rate):
        self.atem.setMixTransitionRate(rate)
