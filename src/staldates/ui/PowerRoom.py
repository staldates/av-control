from PySide.QtGui import QIcon, QMainWindow, QStackedWidget, QWidget, \
    QHBoxLayout, QButtonGroup, QGridLayout

from staldates.ui.widgets.BlindsControl import BlindsControl
from staldates.ui.widgets.Buttons import OptionButton
from staldates.ui.widgets.Clock import Clock
from staldates.ui.widgets.Dialogs import PowerNotificationDialog
from staldates.ui.widgets.LogViewer import LogViewer
from staldates.ui.widgets.ProjectorScreensControl import ProjectorScreenControl
from staldates.ui.widgets.Status import ControllerConnectionStatus, SystemStatus


class PowerRoomControl(QMainWindow):

    def __init__(self, controller):
        super(PowerRoomControl, self).__init__()
        self.controller = controller

        self.setWindowTitle("av-control - power room interface")
        self.resize(800, 600)
        self.setWindowIcon(QIcon(":icons/video-display"))

        self.controls = PowerRoomControls(controller, self)
        self.setCentralWidget(self.controls)

        self.pnd = PowerNotificationDialog(self)
        self.pnd.accepted.connect(self.hidePowerDialog)

    def showPowerDialog(self, message):
        self.pnd.message = message
        self.pnd.exec_()

    def hidePowerDialog(self):
        self.pnd.close()

    def updateOutputMappings(self, mapping):
        self.controls.systemStatus.updateOutputMappings(mapping)


class PowerRoomControls(QWidget):
    def __init__(self, controller, parent=None):
        QWidget.__init__(self, parent)
        layout = QGridLayout()

        stack = QStackedWidget()

        layout.addWidget(stack, 0, 0)

        bottomBar = QHBoxLayout()

        self.screenButtons = QButtonGroup()

        def addScreen(name, screenWidget, icon=None):
            button = OptionButton()
            button.setText(name)
            if icon:
                button.setIcon(QIcon(icon))
            idx = stack.addWidget(screenWidget)
            button.clicked.connect(lambda: stack.setCurrentIndex(idx))
            self.screenButtons.addButton(button, idx)
            bottomBar.addWidget(button)
            return idx

        self.systemStatus = SystemStatus(controller)

        addScreen("Status", self.systemStatus, ":icons/applications-system")

        lv = LogViewer()
        lv_idx = addScreen("Logs", lv, ":icons/logs")
        self.screenButtons.buttons()[lv_idx].clicked.connect(lambda: lv.displayLog(controller.getLog()))

        addScreen("Blinds", BlindsControl(controller['Blinds']), ":icons/blinds")
        addScreen("Screens", ProjectorScreenControl(controller['Screens']), ":icons/screens")

        self.screenButtons.buttons()[0].setChecked(True)

        bottomBar.addWidget(Clock())
        bottomBar.addWidget(ControllerConnectionStatus(controller))

        layout.addLayout(bottomBar, 1, 0)
        layout.setRowStretch(0, 8)
        layout.setRowStretch(1, 0)
        self.setLayout(layout)
