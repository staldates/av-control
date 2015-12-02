from PySide.QtGui import QHBoxLayout, QVBoxLayout
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.ui.widgets.Screens import ScreenWithBackButton


class LightingControl(ScreenWithBackButton):

    def __init__(self, lightsDevice, mainWindow):
        self.lights = lightsDevice
        ScreenWithBackButton.__init__(self, "Welcome Area Lights", mainWindow)

    def makeContent(self):
        layout = QHBoxLayout()

        gallery = QVBoxLayout()

        galleryOn = ExpandingButton()
        galleryOn.setText("Gallery")
        gallery.addWidget(galleryOn)

        external = ExpandingButton()
        external.setText("External Lights")
        gallery.addWidget(external)

        layout.addLayout(gallery)

        welcomeArea = QVBoxLayout()

        full = ExpandingButton()
        full.setText("100%")
        welcomeArea.addWidget(full)

        std = ExpandingButton()
        std.setText("70%")
        welcomeArea.addWidget(std)

        off = ExpandingButton()
        off.setText("Off")
        welcomeArea.addWidget(off)

        layout.addLayout(welcomeArea)

        return layout
