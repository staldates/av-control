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
        super(AdvancedMenu, self).__init__("Preferences", mainWindow)

    def makeContent(self):
        layout = QVBoxLayout()

        prefs = PreferencesWidget(self.controller, self.transition)
        layout.addWidget(prefs)

        self.lv = LogViewer(self.controller, self.mainWindow)

        bottom_row = QHBoxLayout()

        lblVersion = QLabel()
        lblVersion.setText("av-control version {0}\navx version {1}".format(_ui_version, _avx_version))
        bottom_row.addWidget(lblVersion)

        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        bottom_row.addWidget(log)

        btnQuit = ExpandingButton()
        btnQuit.setText("Exit AV Control")
        btnQuit.clicked.connect(self.mainWindow.close)
        bottom_row.addWidget(btnQuit)

        for i in range(3):
            bottom_row.setStretch(i, 1)

        layout.addLayout(bottom_row)

        return layout

    @with_atem
    def setMixRate(self, rate):
        self.atem.setMixTransitionRate(rate)

    def showLog(self):
        self.lv.displayLog()
        self.mainWindow.showScreen(self.lv)
