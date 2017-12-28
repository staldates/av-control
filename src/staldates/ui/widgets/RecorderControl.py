from avx.devices.net.atem.constants import VideoSource
from avx.devices.net.hyperdeck import TransportState, TransportMode
from staldates.ui.widgets.Buttons import ExpandingButton
from staldates.ui.widgets.Screens import ScreenWithBackButton
from PySide.QtGui import QGridLayout, QIcon, QButtonGroup, QWidget, QTableWidget,\
    QTableWidgetItem, QAbstractItemView
from PySide.QtCore import Qt, QSignalMapper
from staldates.ui.widgets.Labels import TitleLabel


def _make_button(caption, icon, onclick):
    b = ExpandingButton()
    b.setIcon(QIcon(icon))
    b.setText(caption)
    b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    b.clicked.connect(onclick)
    return b


class RecorderClipSelectionScreen(QWidget):
    def __init__(self, hyperdeck, state, mainWindow):
        super(RecorderClipSelectionScreen, self).__init__()
        self.hyperdeck = hyperdeck
        self.state = state
        self.mainWindow = mainWindow

        self.selected_clip = None

        layout = QGridLayout()

        lblTitle = TitleLabel("Select clip")
        layout.addWidget(lblTitle, 0, 0, 1, 2)

        self.clipTable = QTableWidget()
        self.clipTable.setColumnCount(2)
        self.clipTable.setHorizontalHeaderLabels(['ID', 'Clip name'])
        self.clipTable.horizontalHeader().setStretchLastSection(True)
        self.clipTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.clipTable.itemSelectionChanged.connect(self._onClipSelected)

        layout.addWidget(self.clipTable, 1, 0, 1, 2)

        b = ExpandingButton()
        b.setText("Back")
        b.setIcon(QIcon(":icons/go-previous"))
        b.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        b.clicked.connect(mainWindow.stepBack)
        layout.addWidget(b, 2, 0)

        self.btnSelect = ExpandingButton()
        self.btnSelect.setText("Cue clip")
        self.btnSelect.clicked.connect(self._cueClip)
        layout.addWidget(self.btnSelect, 2, 1)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 0)

        self.setLayout(layout)

        self.populateClipsList(state.clip_listing)
        state.clipsListChange.connect(self.populateClipsList)
        state.transportChange.connect(self._updateClipSelectionFromState)

    def populateClipsList(self, clipsList):
        self.selected_clip = None
        self.btnSelect.setEnabled(False)
        self.clipTable.clearContents()
        self.clipTable.setRowCount(len(clipsList))
        for idx, (clip_id, val) in enumerate(clipsList.iteritems()):
            self.clipTable.setItem(idx, 0, QTableWidgetItem(str(clip_id)))
            self.clipTable.setItem(idx, 1, QTableWidgetItem(val['name']))

    def _updateClipSelectionFromState(self, state):
        if 'clip id' in state:
            clip_id = state['clip id']
            for row in range(self.clipTable.rowCount()):
                this_id = self.clipTable.item(row, 0)
                if this_id.text() == str(clip_id):
                    self.clipTable.selectRow(row)
                    break

    def _onClipSelected(self):
        selected_items = self.clipTable.selectedItems()
        if selected_items:
            self.selected_clip = int(selected_items[0].text())
            self.btnSelect.setEnabled(True)
        else:
            self.btnSelect.setEnabled(False)

    def _cueClip(self):
        if self.selected_clip:
            self.mainWindow.stepBack()
            self.hyperdeck.gotoClip(self.selected_clip)


class RecorderControl(ScreenWithBackButton):
    def __init__(self, hyperdeck, atem, state, mainWindow):
        self.hyperdeck = hyperdeck
        self.atem = atem
        self.state = state
        self.mainWindow = mainWindow
        super(RecorderControl, self).__init__("Recorder", mainWindow)
        self.state.transportChange.connect(self.updateState)
        if self.hyperdeck:
            self.updateState(state.transport)

    def makeContent(self):
        layout = QGridLayout()

        self.btnGroupSDCard = QButtonGroup()

        self.sdSlotMapper = QSignalMapper()

        for i in range(2):
            btn = ExpandingButton()
            btn.setCheckable(True)
            btn.setText("SD card {}".format(i + 1))
            btn.clicked.connect(self.sdSlotMapper.map)
            self.sdSlotMapper.setMapping(btn, i + 1)
            self.btnGroupSDCard.addButton(btn, i)
            layout.addWidget(btn, 0, i)

        self.sdSlotMapper.mapped.connect(self.hyperdeck.selectSlot)

        self.btnSetPreview = ExpandingButton()
        self.btnSetPreview.setText("To preview")
        self.btnSetPreview.clicked.connect(lambda: self.atem.setPreview(VideoSource.INPUT_7))
        layout.addWidget(self.btnSetPreview, 0, 4)

        btnClearPeaks = ExpandingButton()
        btnClearPeaks.setText("Clear VU peaks")
        btnClearPeaks.clicked.connect(self.atem.resetAudioMixerPeaks)
        layout.addWidget(btnClearPeaks, 0, 5)

        self.btnGroupTransportMode = QButtonGroup()

        self.btnPlaybackMode = ExpandingButton()
        self.btnPlaybackMode.setCheckable(True)
        self.btnPlaybackMode.setChecked(True)
        self.btnPlaybackMode.setText("Playback mode")
        self.btnGroupTransportMode.addButton(self.btnPlaybackMode)
        self.btnPlaybackMode.clicked.connect(lambda: self._setRecordMode(False))
        layout.addWidget(self.btnPlaybackMode, 1, 1, 1, 2)

        self.btnRecordMode = ExpandingButton()
        self.btnRecordMode.setCheckable(True)
        self.btnRecordMode.setText("Record mode")
        self.btnGroupTransportMode.addButton(self.btnRecordMode)
        self.btnRecordMode.clicked.connect(lambda: self._setRecordMode(True))
        layout.addWidget(self.btnRecordMode, 1, 3, 1, 2)

        self.btnSkipBack = _make_button("Back", ":icons/media-skip-backward", self.hyperdeck.prev)
        layout.addWidget(self.btnSkipBack, 2, 0)

        self.btngroup = QButtonGroup()

        self.btnPlay = _make_button("Play", ":icons/media-playback-start", self.hyperdeck.play)
        self.btnPlay.setCheckable(True)
        self.btngroup.addButton(self.btnPlay)
        layout.addWidget(self.btnPlay, 2, 1)

        self.btnLoopPlay = _make_button("Loop", ":icons/media-playback-loop", lambda: self.hyperdeck.play(loop=True))
        layout.addWidget(self.btnLoopPlay, 2, 2)

        self.btnSkipForward = _make_button("Forward", ":icons/media-skip-forward", self.hyperdeck.next)
        layout.addWidget(self.btnSkipForward, 2, 3)

        self.btnStop = _make_button("Stop", ":icons/media-playback-stop", self.hyperdeck.stop)
        self.btnStop.setCheckable(True)
        self.btngroup.addButton(self.btnStop)
        layout.addWidget(self.btnStop, 2, 4)

        self.btnRecord = _make_button("Record", ":icons/media-record", self.hyperdeck.record)
        self.btnRecord.setCheckable(True)
        self.btnRecord.setEnabled(False)
        self.btngroup.addButton(self.btnRecord)
        layout.addWidget(self.btnRecord, 2, 5)

        self.clipSelectionScreen = RecorderClipSelectionScreen(self.hyperdeck, self.state, self.mainWindow)
        self.btnChooseClip = ExpandingButton()
        self.btnChooseClip.setText("Select clip")
        self.btnChooseClip.clicked.connect(self._showClipSelection)
        layout.addWidget(self.btnChooseClip, 3, 1, 1, 2)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 2)
        layout.setRowStretch(3, 1)

        return layout

    def updateState(self, state):
        if 'status' in state:
            self.btnRecord.setChecked(state['status'] == TransportState.RECORD)
            self.btnPlay.setChecked(state['status'] == TransportState.PLAYING)
            self.btnStop.setChecked(state['status'] != TransportState.RECORD and state['status'] != TransportState.PLAYING)
        currentSlot = state.get('active slot', 1)
        self.btnGroupSDCard.button(currentSlot - 1).setChecked(True)

    def _setRecordMode(self, isRecordMode):
        if isRecordMode:
            self.btnSkipBack.setEnabled(False)
            self.btnSkipForward.setEnabled(False)
            self.btnPlay.setEnabled(False)
            self.btnPlay.setChecked(False)
            self.btnLoopPlay.setEnabled(False)
            self.btnRecord.setEnabled(True)
            self.hyperdeck.setTransportMode(TransportMode.RECORD)
        else:
            self.btnSkipBack.setEnabled(True)
            self.btnSkipForward.setEnabled(True)
            self.btnPlay.setEnabled(True)
            self.btnLoopPlay.setEnabled(True)
            self.btnRecord.setEnabled(False)
            self.btnRecord.setChecked(False)
            self.hyperdeck.setTransportMode(TransportMode.PLAYBACK)

    def _showClipSelection(self):
        self.mainWindow.showScreen(self.clipSelectionScreen)
        self.hyperdeck.broadcastClipsList()
