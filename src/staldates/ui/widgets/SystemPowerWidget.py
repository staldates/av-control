from avx.Sequencer import ControllerEvent, DeviceEvent, LogEvent, SleepEvent,\
    BroadcastEvent, CompositeEvent
from PySide.QtCore import Qt
from PySide.QtGui import QHBoxLayout
from staldates import MessageTypes
from staldates.ui.widgets.Buttons import SvgButton
from staldates.ui.widgets.Dialogs import handlePyroErrors
from staldates.ui.widgets.Screens import ScreenWithBackButton

import logging


_DEVICES_TO_DEINITIALISE = [
    # On power-off, deinitialise only these devices - e.g. these are devices on
    # switched power rather than permanent power.
    'ATEM',
    'Recorder',
    'Camera 1',
    'Camera 2',
    'Camera 3'
]


class SystemPowerWidget(ScreenWithBackButton):

    def __init__(self, controller, mainWindow):
        self.controller = controller
        ScreenWithBackButton.__init__(self, "System Power", mainWindow)

    def makeContent(self):

        buttons = QHBoxLayout()

        self.btnOff = SvgButton(":icons/lightbulb_off", 128, 128)
        self.btnOff.setText("Off")
        self.btnOff.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btnOff.clicked.connect(self.powerOff)
        buttons.addWidget(self.btnOff)

        self.btnOn = SvgButton(":icons/lightbulb_on", 128, 128)
        self.btnOn.setText("On")
        self.btnOn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.btnOn.clicked.connect(self.powerOn)
        buttons.addWidget(self.btnOn)

        return buttons

    @handlePyroErrors
    def powerOn(self):
        self.controller.sequence(
            BroadcastEvent(MessageTypes.SHOW_POWER_ON, "Client", None),
            LogEvent(logging.INFO, "Turning system power on"),
            DeviceEvent("Power", "on", 1),
            SleepEvent(3),
            DeviceEvent("Power", "on", 2),
            SleepEvent(3),
            DeviceEvent("Power", "on", 3),
            SleepEvent(3),
            DeviceEvent("Power", "on", 4),
            ControllerEvent("initialise"),  # By this time all things we care about to initialise will have been switched on
            BroadcastEvent(MessageTypes.HIDE_POWER, "Client", None),
            LogEvent(logging.INFO, "Power on sequence complete")
        )

    @handlePyroErrors
    def powerOff(self):
        self.controller.sequence(
            BroadcastEvent(MessageTypes.SHOW_POWER_OFF, "Client", None),
            LogEvent(logging.INFO, "Turning system power off"),
            CompositeEvent(
                *map(
                    lambda deviceID: DeviceEvent(deviceID, "deinitialise"),
                    [d for d in _DEVICES_TO_DEINITIALISE if self.controller.hasDevice(d)]
                )
            ),
            DeviceEvent("Power", "off", 4),
            SleepEvent(3),
            DeviceEvent("Power", "off", 3),
            SleepEvent(3),
            DeviceEvent("Power", "off", 2),
            SleepEvent(3),
            DeviceEvent("Power", "off", 1),
            DeviceEvent("bridge", "deinitialise"),
            BroadcastEvent(MessageTypes.HIDE_POWER, "Client", None),
            LogEvent(logging.INFO, "Power off sequence complete")
        )
