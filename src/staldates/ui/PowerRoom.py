from PySide.QtCore import Qt
from PySide.QtGui import QIcon, QMainWindow, QStackedWidget, QWidget, \
    QHBoxLayout, QVBoxLayout, QButtonGroup, QToolButton, QSizePolicy

from staldates.ui.widgets.Clock import Clock
from staldates.ui.widgets.LogViewer import LogViewer
from staldates.ui.widgets.Status import SystemStatus
from staldates.ui.widgets.BlindsControl import BlindsControl


class PowerRoomControl(QMainWindow):

    def __init__(self, controller):
        super(PowerRoomControl, self).__init__()
        self.controller = controller

        self.setWindowTitle("av-control - power room interface")
        self.resize(1024, 600)
        self.setWindowIcon(QIcon(":icons/video-display"))

        self.setCentralWidget(PowerRoomControls(controller, self))

    def showPowerDialog(self, message):
        self.pnd.message = message
        self.pnd.exec_()

    def hidePowerDialog(self):
        self.pnd.close()
        if self.stack.currentWidget() == self.spc:
            self.stepBack()

    def updateOutputMappings(self, mapping):
        pass


class PowerRoomControls(QWidget):
    def __init__(self, controller, parent=None):
        QWidget.__init__(self, parent)
        layout = QVBoxLayout()

        stack = QStackedWidget()

        layout.addWidget(stack)

        bottomBar = QHBoxLayout()

        self.screenButtons = QButtonGroup()

        def addScreen(name, screenWidget, icon=None):
            button = QToolButton()
            button.setText(name)
            button.setCheckable(True)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            if icon:
                button.setIcon(QIcon(icon))
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            idx = stack.addWidget(screenWidget)
            button.clicked.connect(lambda: stack.setCurrentIndex(idx))
            self.screenButtons.addButton(button, idx)
            bottomBar.addWidget(button)
            return idx

        lv = LogViewer()
        lv_idx = addScreen("Logs", lv, ":icons/logs")
        self.screenButtons.buttons()[lv_idx].clicked.connect(lambda: lv.displayLog(controller.getLog()))

        addScreen("Blinds", BlindsControl(controller['Blinds']), ":icons/blinds")

        self.screenButtons.buttons()[0].setChecked(True)

        bottomBar.addWidget(Clock())
        bottomBar.addWidget(SystemStatus(controller))

        layout.addLayout(bottomBar)
        self.setLayout(layout)
