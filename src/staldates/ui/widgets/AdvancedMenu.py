from avx._version import __version__ as _avx_version
from PySide.QtGui import QVBoxLayout, QLabel
from staldates.ui.widgets.LogViewer import LogViewer
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.ui.widgets.Screens import ScreenWithBackButton
from staldates.ui._version import __version__ as _ui_version


class AdvancedMenu(ScreenWithBackButton):
    '''
    Place to hide magical advanced system features.
    '''

    def __init__(self, controller, mainWindow):
        self.controller = controller
        self.mainWindow = mainWindow
        super(AdvancedMenu, self).__init__("Advanced Options", mainWindow)

    def makeContent(self):
        layout = QVBoxLayout()

        lblVersion = QLabel()
        lblVersion.setText("av-control version {0} (avx version {1})".format(_ui_version, _avx_version))
        layout.addWidget(lblVersion)

        self.lv = LogViewer(self.controller, self.mainWindow)

        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        layout.addWidget(log)

        btnAutoTrack = ExpandingButton()
        btnAutoTrack.setText("Recalibrate Extras scan converter")
        btnAutoTrack.clicked.connect(lambda: self.controller["Extras Scan Converter"].recalibrate())
        layout.addWidget(btnAutoTrack)

        btnQuit = ExpandingButton()
        btnQuit.setText("Exit AldatesX")
        btnQuit.clicked.connect(self.mainWindow.close)
        layout.addWidget(btnQuit)

        return layout

    def showLog(self):
        self.lv.displayLog()
        self.mainWindow.showScreen(self.lv)
