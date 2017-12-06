from PySide.QtCore import Qt
from PySide.QtGui import QWidget, QVBoxLayout, QHBoxLayout,\
    QButtonGroup, QLabel
from staldates.preferences import Preferences
from staldates.ui.widgets.Labels import TitleLabel
from staldates.ui.widgets.TouchSpinner import FrameRateTouchSpinner,\
    TouchSpinner
from staldates.VisualsSystem import with_atem
from staldates.ui.widgets.Buttons import ExpandingButton


class JoystickInvertPreference(QWidget):
    def __init__(self, parent=None):
        super(JoystickInvertPreference, self).__init__(parent)

        layout = QHBoxLayout()
        self._btnGroup = QButtonGroup()

        self.btnNormal = ExpandingButton()
        self.btnNormal.setText('Down')
        self.btnNormal.setCheckable(True)
        self.btnNormal.clicked.connect(self.set_preference)
        self._btnGroup.addButton(self.btnNormal)
        layout.addWidget(self.btnNormal)

        self.btnInvert = ExpandingButton()
        self.btnInvert.setText('Up')
        self.btnInvert.setCheckable(True)
        self.btnInvert.clicked.connect(self.set_preference)
        self._btnGroup.addButton(self.btnInvert)
        layout.addWidget(self.btnInvert)

        self.setLayout(layout)

        self.update_from_preferences()
        Preferences.subscribe(self.update_from_preferences)

    def update_from_preferences(self):
        invert_y = Preferences.get('joystick.invert_y', False)
        self.btnInvert.setChecked(invert_y)
        self.btnNormal.setChecked(not invert_y)

    def set_preference(self):
        Preferences.set('joystick.invert_y', self.btnInvert.isChecked())


class SensitivityPreference(QWidget):
    def __init__(self, preference_name, label, parent=None):
        super(SensitivityPreference, self).__init__(parent)
        self.preference_name = preference_name

        layout = QHBoxLayout()

        label = QLabel(label)
        label.setAlignment(Qt.AlignRight)
        layout.addWidget(label, 1)

        self.spinner = TouchSpinner()
        self.spinner.setMaximum(10)
        self.spinner.setMinimum(1)

        self.update_from_preferences()
        Preferences.subscribe(self.update_from_preferences)
        self.spinner.valueChanged.connect(lambda v: Preferences.set(preference_name, float(v) / 10))
        layout.addWidget(self.spinner, 2)

        self.setLayout(layout)

    def update_from_preferences(self):
        self.spinner.setValue(int(Preferences.get(self.preference_name, 0.5) * 10))


class PreferencesWidget(QWidget):
    def __init__(self, controller, transition, parent=None):
        super(PreferencesWidget, self).__init__(parent)
        self.controller = controller
        self.transition = transition
        self.atem = controller['ATEM']

        layout = QVBoxLayout()

        layout.addWidget(TitleLabel('Preferences'))

        mixRate = FrameRateTouchSpinner()
        mixRate.setValue(transition.rate)
        mixRate.setMaximum(250)
        mixRate.setMinimum(1)
        mixRate.valueChanged.connect(self.setMixRate)

        layout.addWidget(QLabel('Mix rate (seconds:frames):'))
        layout.addWidget(mixRate)

        layout.addWidget(QLabel('Joystick forward means:'))
        layout.addWidget(JoystickInvertPreference())

        layout.addWidget(QLabel('Joystick sensitivity:'))
        layout.addWidget(SensitivityPreference('joystick.sensitivity.pan', 'Pan'))
        layout.addWidget(SensitivityPreference('joystick.sensitivity.tilt', 'Tilt'))
        layout.addWidget(SensitivityPreference('joystick.sensitivity.zoom', 'Zoom'))

        self.setLayout(layout)

    @with_atem
    def setMixRate(self, rate):
        self.atem.setMixTransitionRate(rate)
