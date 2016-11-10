from PySide.QtCore import Qt
from PySide.QtGui import QButtonGroup, QGridLayout, QWidget, QVBoxLayout
from staldates.ui.widgets.Buttons import IDedButton, SvgButton
from staldates.ui.widgets.Screens import ScreenWithBackButton
from staldates.ui.widgets.Dialogs import handlePyroErrors


class BlindsControlScreen(ScreenWithBackButton):
    '''
    Controls for the blinds.
    '''

    def __init__(self, blindsDevice, mainWindow):
        self.blindsDevice = blindsDevice
        ScreenWithBackButton.__init__(self, "Blinds", mainWindow)

    def makeContent(self):
        layout = QVBoxLayout()
        layout.addWidget(BlindsControl(self.blindsDevice))
        return layout


class BlindsControl(QWidget):
    def __init__(self, blindsDevice):
        super(BlindsControl, self).__init__()
        self.blindsDevice = blindsDevice
        layout = QGridLayout()

        self.blinds = QButtonGroup()

        for i in range(1, 7):
            btn = IDedButton(i)
            btn.setText(str(i))
            layout.addWidget(btn, 0, i - 1)
            btn.setCheckable(True)
            self.blinds.addButton(btn, i)

        btnAll = IDedButton(0)
        btnAll.setText("All")
        layout.addWidget(btnAll, 0, 6)
        btnAll.setCheckable(True)
        btnAll.setChecked(True)
        self.blinds.addButton(btnAll, 0)

        btnRaise = SvgButton(":icons/go-up", 96, 96)
        btnRaise.setText("Raise")
        btnRaise.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnRaise, 1, 1, 1, 3)
        btnRaise.clicked.connect(self.raiseUp)

        btnLower = SvgButton(":icons/go-down", 96, 96)
        btnLower.setText("Lower")
        btnLower.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        layout.addWidget(btnLower, 2, 1, 1, 3)
        btnLower.clicked.connect(self.lowerDown)

        btnStop = SvgButton(":icons/process-stop", 96, 96)
        btnStop.setText("Stop")
        btnStop.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        layout.addWidget(btnStop, 1, 4, 2, 2)
        btnStop.clicked.connect(self.stop)

        self.setLayout(layout)

    @handlePyroErrors
    def raiseUp(self):
        blindID = self.blinds.checkedId()
        self.blindsDevice.raiseUp(blindID)

    @handlePyroErrors
    def lowerDown(self):
        blindID = self.blinds.checkedId()
        self.blindsDevice.lower(blindID)

    @handlePyroErrors
    def stop(self):
        blindID = self.blinds.checkedId()
        self.blindsDevice.stop(blindID)
