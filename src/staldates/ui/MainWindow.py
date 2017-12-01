from PySide.QtGui import QGridLayout, QIcon, QMainWindow, QStackedWidget, QWidget,\
    QHBoxLayout
from PySide.QtCore import Qt
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.ui.widgets.Clock import Clock
from staldates.ui.widgets.SystemPowerWidget import SystemPowerWidget
from staldates.ui.VideoSwitcher import VideoSwitcher
from staldates.ui.widgets.Dialogs import PowerNotificationDialog
from staldates.ui.widgets.BlindsControl import BlindsControl
from staldates.ui.widgets.AdvancedMenu import AdvancedMenu
from staldates.ui.widgets import Dialogs
from staldates.ui.widgets.LightingControl import LightingControl
from staldates.ui.widgets.Status import SystemStatus
from staldates.VisualsSystem import SwitcherState, HyperdeckState
from staldates import MessageTypes
from staldates.ui.StringConstants import StringConstants
from staldates.ui.widgets.RecorderControl import RecorderControl
from avx.devices.net.hyperdeck import TransportState


class MainWindow(QMainWindow):

    def __init__(self, controller, joystickAdapter=None):
        super(MainWindow, self).__init__()
        self.controller = controller

        self.setWindowTitle("av-control")
        self.resize(1024, 600)
        self.setWindowIcon(QIcon(":icons/video-display"))

        atem = controller['ATEM']
        self.switcherState = SwitcherState(atem)

        self.mainScreen = VideoSwitcher(controller, self, self.switcherState, joystickAdapter)

        # This is possibly a bad / too complicated idea...
        # self.mainScreen.setEnabled(self.switcherState.connected)
        # self.switcherState.connectionChanged.connect(self.mainScreen.setEnabled)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.mainScreen)

        outer = QWidget()
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.stack, 0, 0, 1, 7)

        column = 0

        self.spc = SystemPowerWidget(controller, self)

        syspower = ExpandingButton()
        syspower.setText("Power")
        syspower.clicked.connect(self.showSystemPower)
        syspower.setIcon(QIcon(":icons/system-shutdown"))
        syspower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        mainLayout.addWidget(syspower, 1, column)
        column += 1

        if controller.hasDevice("Blinds"):
            self.bc = BlindsControl(controller["Blinds"], self)

            blinds = ExpandingButton()
            blinds.setText("Blinds")
            blinds.clicked.connect(lambda: self.showScreen(self.bc))
            blinds.setIcon(QIcon(":icons/blinds"))
            blinds.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            mainLayout.addWidget(blinds, 1, column)
            column += 1

        if controller.hasDevice("Lights"):
            self.lightsMenu = LightingControl(controller["Lights"], self)

            lights = ExpandingButton()
            lights.setText("Lights")
            lights.clicked.connect(lambda: self.showScreen(self.lightsMenu))
            lights.setIcon(QIcon(":icons/lightbulb_on"))
            lights.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            mainLayout.addWidget(lights, 1, column)
            column += 1

        if controller.hasDevice("Recorder"):
            hyperdeck = controller['Recorder']
            self.hyperdeckState = HyperdeckState(hyperdeck)
            self.recorderScreen = RecorderControl(hyperdeck, atem, self.hyperdeckState, self)
            recorder = ExpandingButton()
            recorder.setText("Recorder")
            recorder.setIcon(QIcon(":icons/drive-optical"))
            recorder.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            recorder.clicked.connect(lambda: self.showScreen(self.recorderScreen))
            mainLayout.addWidget(recorder, 1, column)
            column += 1

            def update_recorder_icon(transport):
                if 'status' in transport:
                    if transport['status'] == TransportState.RECORD:
                        recorder.setIcon(QIcon(":icons/media-record"))
                    elif transport['status'] == TransportState.PLAYING:
                        recorder.setIcon(QIcon(":icons/media-playback-start"))
                    else:
                        recorder.setIcon(QIcon(":icons/drive-optical"))
            self.hyperdeckState.transportChange.connect(update_recorder_icon)

        self.advMenu = AdvancedMenu(self.controller, self.switcherState.mixTransition, atem, self)

        adv = ExpandingButton()
        adv.setText("Advanced")
        adv.setIcon(QIcon(":icons/applications-system"))
        adv.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        adv.clicked.connect(lambda: self.showScreen(self.advMenu))
        mainLayout.addWidget(adv, 1, column)
        column += 1

        for i in range(column):
            mainLayout.setColumnStretch(i, 1)

        tray = QHBoxLayout()
        tray.addWidget(Clock())
        tray.addWidget(SystemStatus(controller))
        mainLayout.addLayout(tray, 1, column)

        mainLayout.setRowStretch(0, 8)
        mainLayout.setRowStretch(1, 0)

        outer.setLayout(mainLayout)

        self.setCentralWidget(outer)

        self.pnd = PowerNotificationDialog(self)
        self.pnd.accepted.connect(self.hidePowerDialog)

    def showScreen(self, screenWidget):
        if self.stack.currentWidget() == screenWidget:
            self.stepBack()
        else:
            self.stack.insertWidget(0, screenWidget)
            self.stack.setCurrentWidget(screenWidget)

    def showSystemPower(self):
        self.showScreen(self.spc)

    def stepBack(self):
        self.stack.removeWidget(self.stack.currentWidget())

    def errorBox(self, text):
        Dialogs.errorBox(text)

    def showPowerDialog(self, message):
        self.pnd.message = message
        self.pnd.exec_()

    def hidePowerDialog(self):
        self.pnd.close()
        if self.stack.currentWidget() == self.spc:
            self.stepBack()

    def updateOutputMappings(self, deviceID, mapping):
        self.mainScreen.updateOutputMappings({deviceID: mapping})

    def handleMessage(self, msgType, sourceDeviceID, data):
        if msgType == MessageTypes.SHOW_POWER_ON:
            self.showPowerDialog(StringConstants.poweringOn)
        elif msgType == MessageTypes.SHOW_POWER_OFF:
            self.showPowerDialog(StringConstants.poweringOff)
        elif msgType == MessageTypes.HIDE_POWER:
            self.hidePowerDialog()
        elif sourceDeviceID == "ATEM":
            self.switcherState.handleMessage(msgType, data)
        elif sourceDeviceID == "Recorder":
            self.hyperdeckState.handleMessage(msgType, data)
