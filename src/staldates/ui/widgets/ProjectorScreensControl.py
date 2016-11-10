from PySide.QtCore import Qt
from PySide.QtGui import QButtonGroup, QGridLayout, QWidget, QVBoxLayout
from staldates.ui.widgets.Buttons import IDedButton, SvgButton
from staldates.ui.widgets.Dialogs import handlePyroErrors
from staldates.ui.widgets.Screens import ScreenWithBackButton


class ProjectorScreensControlScreen(ScreenWithBackButton):
    '''
    Controls for the projector screens.
    '''

    def __init__(self, screensDevice, mainWindow):
        self.screensDevice = screensDevice
        ScreenWithBackButton.__init__(self, "Projector Screens", mainWindow)

    def makeContent(self):
        layout = QVBoxLayout()
        layout.addWidget(ProjectorScreenControl(self.screensDevice))
        return layout


class ProjectorScreenControl(QWidget):
    def __init__(self, screensDevice, parent=None):
        super(ProjectorScreenControl, self).__init__(parent)
        self.screensDevice = screensDevice

        layout = QGridLayout()

        self.screens = QButtonGroup()

        btnLeft = IDedButton(1)
        btnLeft.setText("Left")
        layout.addWidget(btnLeft, 1, 0, 1, 2)
        btnLeft.setCheckable(True)
        self.screens.addButton(btnLeft, 1)

        btnAll = IDedButton(0)
        btnAll.setText("Both")
        layout.addWidget(btnAll, 1, 2, 1, 3)
        btnAll.setCheckable(True)
        btnAll.setChecked(True)
        self.screens.addButton(btnAll, 0)

        btnRight = IDedButton(2)
        btnRight.setText("Right")
        layout.addWidget(btnRight, 1, 5, 1, 2)
        btnRight.setCheckable(True)
        self.screens.addButton(btnRight, 2)

        btnRaise = SvgButton(":icons/go-up", 96, 96)
        btnRaise.setText("Raise")
        btnRaise.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnRaise, 2, 1, 1, 3)
        btnRaise.clicked.connect(self.raiseUp)

        btnLower = SvgButton(":icons/go-down", 96, 96)
        btnLower.setText("Lower")
        btnLower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnLower, 3, 1, 1, 3)
        btnLower.clicked.connect(self.lowerDown)

        btnStop = SvgButton(":icons/process-stop", 96, 96)
        btnStop.setText("Stop")
        btnStop.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        layout.addWidget(btnStop, 2, 4, 2, 2)
        btnStop.clicked.connect(self.stop)

        self.setLayout(layout)

    @handlePyroErrors
    def raiseUp(self):
        screenID = self.screens.checkedId()
        self.screensDevice.raiseUp(screenID)

    @handlePyroErrors
    def lowerDown(self):
        screenID = self.screens.checkedId()
        self.screensDevice.lower(screenID)

    @handlePyroErrors
    def stop(self):
        screenID = self.screens.checkedId()
        self.screensDevice.stop(screenID)
