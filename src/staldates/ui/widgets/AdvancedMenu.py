from avx._version import __version__ as _avx_version
from PySide.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from staldates.ui.widgets.LogViewer import LogViewer
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.ui.widgets.Preferences import PreferencesWidget
from staldates.ui.widgets.Screens import ScreenWithBackButton
from staldates.ui._version import __version__ as _ui_version
from staldates.VisualsSystem import with_atem


class AdvancedMenu(ScreenWithBackButton):
    '''
    Place to hide magical advanced system features.
    '''

    def __init__(self, controller, transition, atem, mainWindow):
        self.controller = controller
        self.mainWindow = mainWindow
        self.transition = transition
        self.atem = atem
        super(AdvancedMenu, self).__init__("Advanced Options", mainWindow)

    def makeContent(self):
        layout = QHBoxLayout()

        prefs = PreferencesWidget(self.controller, self.transition)
        layout.addWidget(prefs, 1)

        rhs = QVBoxLayout()

        lblVersion = QLabel()
        lblVersion.setText("av-control version {0} (avx version {1})".format(_ui_version, _avx_version))
        rhs.addWidget(lblVersion)

        self.lv = LogViewer(self.controller, self.mainWindow)

        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        rhs.addWidget(log)

        btnQuit = ExpandingButton()
        btnQuit.setText("Exit AV Control")
        btnQuit.clicked.connect(self.mainWindow.close)
        rhs.addWidget(btnQuit)

        layout.addLayout(rhs, 1)

        return layout

    @with_atem
    def setMixRate(self, rate):
        self.atem.setMixTransitionRate(rate)

    def showLog(self):
        self.lv.displayLog()
        self.mainWindow.showScreen(self.lv)
