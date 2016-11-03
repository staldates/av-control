from PySide.QtGui import QHBoxLayout, QVBoxLayout, QButtonGroup
from staldates.ui.widgets.Buttons import ExpandingButton, OptionButton
from staldates.ui.widgets.Dialogs import handlePyroErrors
from staldates.ui.widgets.Screens import ScreenWithBackButton
from staldates.ui.widgets.Labels import TitleLabel


def _safelyConnect(signal, slot):
    signal.connect(handlePyroErrors(slot))


class LightingControl(ScreenWithBackButton):

    def __init__(self, lightsDevice, mainWindow):
        self.lights = lightsDevice
        ScreenWithBackButton.__init__(self, "Lighting", mainWindow)

    def makeContent(self):
        layout = QHBoxLayout()

        layout.addLayout(self._welcomeAreaControls())
        layout.addLayout(self._modeControls())

        return layout

    def _welcomeAreaControls(self):
        def onOff(presetString):
            @handlePyroErrors
            def inner(isOn):
                if isOn:
                    self.lights.activate(presetString)
                else:
                    self.lights.deactivate(presetString)
            return inner

        layout = QHBoxLayout()

        gallery_ext = QVBoxLayout()

        gallery_ext.addWidget(TitleLabel("Gallery and External"))

        gallery = ExpandingButton()
        gallery.setText("Gallery")
        gallery.setCheckable(True)
        gallery.toggled.connect(onOff("St Aldate's.Welcome Area.gall on"))
        gallery_ext.addWidget(gallery)

        external = ExpandingButton()
        external.setText("External Lights")
        external.setCheckable(True)
        external.toggled.connect(onOff("EXTERIOR.Section Zero.ENTRA ONLY ON"))
        gallery_ext.addWidget(external)

        layout.addLayout(gallery_ext)

        welcomeArea = QVBoxLayout()

        welcomeArea.addWidget(TitleLabel("Welcome Area"))

        full = OptionButton()
        full.setText("100%")
        _safelyConnect(full.clicked, lambda: self.lights.activate("St Aldate's.Welcome Area.Welcome100%"))
        welcomeArea.addWidget(full)

        std = OptionButton()
        std.setText("70%")
        _safelyConnect(std.clicked, lambda: self.lights.activate("St Aldate's.Welcome Area.Welcome70%"))
        welcomeArea.addWidget(std)

        off = OptionButton()
        off.setText("Off")
        _safelyConnect(off.clicked, lambda: self.lights.activate("St Aldate's.Welcome Area.Ent&GalOFF"))
        welcomeArea.addWidget(off)

        self.welcomeArea = QButtonGroup()
        self.welcomeArea.addButton(full, 1)
        self.welcomeArea.addButton(std, 2)
        self.welcomeArea.addButton(off, 3)

        layout.addLayout(welcomeArea)

        return layout

    def _modeControls(self):
        layout = QVBoxLayout()
        layout.addWidget(TitleLabel("Lighting Mode"))

        normal = OptionButton()
        normal.setText("Normal")
        _safelyConnect(normal.clicked, lambda: self.lights.execute("goto default"))
        layout.addWidget(normal)

        late = OptionButton()
        late.setText("8.15 Service")
        _safelyConnect(late.clicked, lambda: self.lights.execute("Goto 8:15"))
        layout.addWidget(late)

        test = OptionButton()
        test.setText("Test (All @50%)")
        _safelyConnect(test.clicked, lambda: self.lights.activate("St Aldate's.Section Zero.All at 50"))
        layout.addWidget(test)

        self.modes = QButtonGroup()
        self.modes.addButton(normal, 1)
        self.modes.addButton(late, 2)
        self.modes.addButton(test, 3)

        return layout
