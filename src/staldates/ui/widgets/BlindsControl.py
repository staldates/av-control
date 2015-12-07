from avx.StringConstants import StringConstants
from Pyro4.errors import NamingError, ProtocolError
from PySide.QtCore import Qt
from PySide.QtGui import QButtonGroup, QGridLayout
from staldates.ui.widgets.Buttons import IDedButton, SvgButton
from staldates.ui.widgets.Screens import ScreenWithBackButton


class BlindsControl(ScreenWithBackButton):
    '''
    Controls for the blinds.
    '''

    def __init__(self, blindsDevice, mainWindow):
        self.blindsDevice = blindsDevice
        ScreenWithBackButton.__init__(self, "Blinds", mainWindow)

    def makeContent(self):
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

        return layout

    def raiseUp(self):
        blindID = self.blinds.checkedId()
        try:
            self.blindsDevice.raiseUp(blindID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def lowerDown(self):
        blindID = self.blinds.checkedId()
        try:
            self.blindsDevice.lower(blindID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)

    def stop(self):
        blindID = self.blinds.checkedId()
        try:
            self.blindsDevice.stop(blindID)
        except NamingError:
            self.mainWindow.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.mainWindow.errorBox(StringConstants.protocolErrorText)
