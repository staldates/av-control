from PySide.QtGui import QIcon, QHBoxLayout
from PySide.QtCore import Qt, QSize
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.ui.widgets.Screens import ScreenWithBackButton
from avx.Sequencer import ControllerEvent, DeviceEvent, SleepEvent


class SystemPowerWidget(ScreenWithBackButton):

    def __init__(self, controller, mainWindow):
        self.controller = controller
        ScreenWithBackButton.__init__(self, "System Power", mainWindow)

    def makeContent(self):

        buttons = QHBoxLayout()

        self.btnOff = ExpandingButton()
        self.btnOff.setText("Off")
        self.btnOff.setIcon(QIcon("icons/lightbulb_off.svg"))
        self.btnOff.setIconSize(QSize(128, 128))
        self.btnOff.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btnOff.clicked.connect(self.powerOff)
        buttons.addWidget(self.btnOff)

        self.btnOn = ExpandingButton()
        self.btnOn.setText("On")
        self.btnOn.setIcon(QIcon("icons/lightbulb_on.svg"))
        self.btnOn.setIconSize(QSize(128, 128))
        self.btnOn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btnOn.clicked.connect(self.powerOn)
        buttons.addWidget(self.btnOn)

        return buttons

    def powerOn(self):
        self.controller.sequence(
            ControllerEvent("showPowerOnDialogOnClients"),
            DeviceEvent("Power", "on", 1),
            SleepEvent(3),
            DeviceEvent("Power", "on", 2),
            SleepEvent(3),
            DeviceEvent("Power", "on", 3),
            SleepEvent(3),
            DeviceEvent("Power", "on", 4),
            ControllerEvent("initialise"),  # By this time all things we care about to initialise will have been switched on
            ControllerEvent("hidePowerDialogOnClients")
        )

    def powerOff(self):
        self.controller.sequence(
            ControllerEvent("showPowerOffDialogOnClients"),
            DeviceEvent("Power", "off", 4),
            SleepEvent(3),
            DeviceEvent("Power", "off", 3),
            SleepEvent(3),
            DeviceEvent("Power", "off", 2),
            SleepEvent(3),
            DeviceEvent("Power", "off", 1),
            ControllerEvent("hidePowerDialogOnClients"),
        )
