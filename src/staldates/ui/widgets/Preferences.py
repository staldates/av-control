from PySide.QtCore import Qt
from PySide.QtGui import QWidget, QVBoxLayout, QHBoxLayout,\
    QButtonGroup, QLabel, QGridLayout
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


class NumericPreference(QWidget):
    def __init__(self, preference_name, label, min, max, default, parent=None):
        super(NumericPreference, self).__init__(parent)
        self.preference_name = preference_name
        self.default = default

        layout = QHBoxLayout()

        label = QLabel(label)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(label, 1)

        self.spinner = TouchSpinner()
        self.spinner.setMaximum(max)
        self.spinner.setMinimum(min)

        self.update_from_preferences()
        Preferences.subscribe(self.update_from_preferences)
        self.spinner.valueChanged.connect(self.update_from_ui)
        layout.addWidget(self.spinner, 2)

        self.setLayout(layout)

    def update_from_ui(self, value):
        Preferences.set(self.preference_name, value)

    def update_from_preferences(self):
        self.spinner.setValue(
            Preferences.get(self.preference_name, self.default)
        )


class SensitivityPreference(NumericPreference):
    def __init__(self, preference_name, label, parent=None):
        super(SensitivityPreference, self).__init__(preference_name, label, 1, 10, 0.5, parent)

    def update_from_ui(self, value):
        Preferences.set(preference_name, float(value) / 10)

    def update_from_preferences(self):
        self.spinner.setValue(int(Preferences.get(self.preference_name, 0.5) * 10))


class PreferencesWidget(QWidget):
    def __init__(self, controller, transition, parent=None):
        super(PreferencesWidget, self).__init__(parent)
        self.controller = controller
        self.transition = transition
        self.atem = controller['ATEM']

        layout = QGridLayout()

        mixRate = FrameRateTouchSpinner()
        mixRate.setValue(transition.rate)
        mixRate.setMaximum(250)
        mixRate.setMinimum(1)
        mixRate.valueChanged.connect(self.setMixRate)

        layout.addWidget(QLabel('Mix rate'), 0, 0)
        layout.addWidget(mixRate, 0, 1)

        layout.addWidget(QLabel('Joystick forward\nmeans'), 1, 0)
        layout.addWidget(JoystickInvertPreference(), 1, 1)

        lblBank = QLabel('Camera preset bank')
        lblBank.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(lblBank, 2, 0)
        layout.addWidget(
            NumericPreference('camera.presets.bank', '', 0, 7, 0),
            2,
            1
        )

        lblSensitivity = QLabel('Joystick sensitivity')
        lblSensitivity.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(lblSensitivity, 0, 2)
        layout.addWidget(SensitivityPreference('joystick.sensitivity.pan', 'Pan'), 0, 3)
        layout.addWidget(SensitivityPreference('joystick.sensitivity.zoom', 'Zoom'), 1, 3)
        layout.addWidget(SensitivityPreference('joystick.sensitivity.tilt', 'Tilt'), 2, 3)

        self.setLayout(layout)

    @with_atem
    def setMixRate(self, rate):
        self.atem.setMixTransitionRate(rate)
