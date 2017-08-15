from avx._version import __version__ as _avx_version
from PySide.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from staldates.ui.widgets.LogViewer import LogViewer
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.ui.widgets.Screens import ScreenWithBackButton
from staldates.ui._version import __version__ as _ui_version
from staldates.ui.widgets.TouchSpinner import FrameRateTouchSpinner
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
        layout = QVBoxLayout()

        lblVersion = QLabel()
        lblVersion.setText("av-control version {0} (avx version {1})".format(_ui_version, _avx_version))
        layout.addWidget(lblVersion)

        mixCtl = QHBoxLayout()
        mixCtl.addWidget(QLabel("Mix rate:"))

        mixRate = FrameRateTouchSpinner()
        mixRate.setValue(self.transition.rate)
        mixRate.setMaximum(250)
        mixRate.setMinimum(1)
        mixRate.valueChanged.connect(self.setMixRate)

        mixCtl.addWidget(mixRate)

        layout.addLayout(mixCtl)

        self.lv = LogViewer(self.controller, self.mainWindow)

        log = ExpandingButton()
        log.setText("Log")
        log.clicked.connect(self.showLog)
        layout.addWidget(log)

        btnQuit = ExpandingButton()
        btnQuit.setText("Exit AV Control")
        btnQuit.clicked.connect(self.mainWindow.close)
        layout.addWidget(btnQuit)

        return layout

    @with_atem
    def setMixRate(self, rate):
        self.atem.setMixTransitionRate(rate)

    def showLog(self):
        self.lv.displayLog()
        self.mainWindow.showScreen(self.lv)
