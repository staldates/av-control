from staldates.ui.widgets.Screens import ScreenWithBackButton
from PySide.QtGui import QGridLayout, QIcon, QButtonGroup
from staldates.ui.widgets.Buttons import ExpandingButton
from PySide.QtCore import Qt
from avx.devices.net.hyperdeck import TransportState


def _make_button(caption, icon, onclick):
    b = ExpandingButton()
    b.setIcon(QIcon(icon))
    b.setText(caption)
    b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    b.clicked.connect(onclick)
    return b


class RecorderControl(ScreenWithBackButton):
    def __init__(self, hyperdeck, state, mainWindow):
        self.hyperdeck = hyperdeck
        self.state = state
        super(RecorderControl, self).__init__("Recorder", mainWindow)
        self.state.transportChange.connect(self.updateState)
        if self.hyperdeck:
            self.updateState(state.transport)

    def makeContent(self):
        layout = QGridLayout()

        skipBack = _make_button("Back", ":icons/media-skip-backward", self.hyperdeck.prev)
        layout.addWidget(skipBack, 0, 0)

        self.btngroup = QButtonGroup()

        self.btnRecord = _make_button("Record", ":icons/media-record", self.hyperdeck.record)
        self.btnRecord.setCheckable(True)
        self.btngroup.addButton(self.btnRecord)
        layout.addWidget(self.btnRecord, 0, 1)

        self.btnPlay = _make_button("Play", ":icons/media-playback-start", self.hyperdeck.play)
        self.btnPlay.setCheckable(True)
        self.btngroup.addButton(self.btnPlay)
        layout.addWidget(self.btnPlay, 0, 2)

        self.btnStop = _make_button("Stop", ":icons/media-playback-stop", self.hyperdeck.stop)
        self.btnStop.setCheckable(True)
        self.btngroup.addButton(self.btnStop)
        layout.addWidget(self.btnStop, 0, 3)

        skipForward = _make_button("Forward", ":icons/media-skip-forward", self.hyperdeck.next)
        layout.addWidget(skipForward, 0, 4)

        return layout

    def updateState(self, state):
        if 'status' in state:
            self.btnRecord.setChecked(state['status'] == TransportState.RECORD)
            self.btnPlay.setChecked(state['status'] == TransportState.PLAYING)
            self.btnStop.setChecked(state['status'] != TransportState.RECORD and state['status'] != TransportState.PLAYING)
