from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.widgets.RecorderControl import RecorderControl
from mock import MagicMock
from avx.devices.net.hyperdeck import TransportState, TransportMode
from avx.devices.net.atem.constants import VideoSource


class TestRecorderControl(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        mainWindow = MagicMock()
        state = MagicMock()
        self.hyperdeck = MagicMock()
        self.atem = MagicMock()

        state.transport = {'status': TransportState.STOPPED}

        self.rc = RecorderControl(self.hyperdeck, self.atem, state, mainWindow)

    def testTransportControls(self):
        self.assertTrue(self.rc.btnStop.isChecked())
        self.assertFalse(self.rc.btnPlay.isChecked())
        self.assertFalse(self.rc.btnRecord.isChecked())

        self.rc.btnStop.click()
        self.hyperdeck.stop.assert_called_once()
        self.rc.btnPlay.click()
        self.hyperdeck.play.assert_called_once()
        self.findButton(self.rc, "Back").click()
        self.hyperdeck.prev.assert_called_once()
        self.findButton(self.rc, "Forward").click()
        self.hyperdeck.next.assert_called_once()

        self.findButton(self.rc, "Record mode").click()

        self.rc.btnRecord.click()
        self.hyperdeck.record.assert_called_once()

    def testUpdateTransportState(self):
        self.rc.updateState({'status': TransportState.STOPPED})
        self.assertTrue(self.rc.btnStop.isChecked())
        self.assertFalse(self.rc.btnPlay.isChecked())
        self.assertFalse(self.rc.btnRecord.isChecked())

        self.rc.updateState({'status': TransportState.PLAYING})
        self.assertFalse(self.rc.btnStop.isChecked())
        self.assertTrue(self.rc.btnPlay.isChecked())
        self.assertFalse(self.rc.btnRecord.isChecked())

        self.rc.updateState({'status': TransportState.RECORD})
        self.assertFalse(self.rc.btnStop.isChecked())
        self.assertFalse(self.rc.btnPlay.isChecked())
        self.assertTrue(self.rc.btnRecord.isChecked())

    def testSDSlotSelection(self):
        self.findButton(self.rc, "SD card 1").click()
        self.hyperdeck.selectSlot.assert_called_once_with(1)
        self.hyperdeck.reset_mock()
        self.findButton(self.rc, "SD card 2").click()
        self.hyperdeck.selectSlot.assert_called_once_with(2)

    def testUpdateSlotSelection(self):
        slot1 = self.findButton(self.rc, "SD card 1")
        slot2 = self.findButton(self.rc, "SD card 2")

        self.assertTrue(slot1.isChecked())
        self.assertFalse(slot2.isChecked())

        self.rc.updateState({'slot id': 2})
        self.assertFalse(slot1.isChecked())
        self.assertTrue(slot2.isChecked())

        self.rc.updateState({'slot id': 1})
        self.assertTrue(slot1.isChecked())
        self.assertFalse(slot2.isChecked())

        self.hyperdeck.selectSlot.assert_not_called()

    def testAtemFunctions(self):
        self.findButton(self.rc, 'To preview').click()
        self.atem.setPreview.assert_called_once_with(VideoSource.INPUT_7)

        self.findButton(self.rc, 'Clear VU peaks').click()
        self.atem.resetAudioMixerPeaks.assert_called_once()

    def testSetTransportMode(self):
        self.findButton(self.rc, 'Playback mode').click()
        self.hyperdeck.setTransportMode.assert_called_once_with(TransportMode.PLAYBACK)

        self.assertTrue(self.findButton(self.rc, 'Back').isEnabled())
        self.assertTrue(self.findButton(self.rc, 'Play').isEnabled())
        self.assertTrue(self.findButton(self.rc, 'Loop').isEnabled())
        self.assertTrue(self.findButton(self.rc, 'Forward').isEnabled())
        self.assertTrue(self.findButton(self.rc, 'Stop').isEnabled())
        self.assertFalse(self.findButton(self.rc, 'Record').isEnabled())

        self.hyperdeck.reset_mock()

        self.findButton(self.rc, 'Record mode').click()
        self.hyperdeck.setTransportMode.assert_called_once_with(TransportMode.RECORD)

        self.assertFalse(self.findButton(self.rc, 'Back').isEnabled())
        self.assertFalse(self.findButton(self.rc, 'Play').isEnabled())
        self.assertFalse(self.findButton(self.rc, 'Loop').isEnabled())
        self.assertFalse(self.findButton(self.rc, 'Forward').isEnabled())
        self.assertTrue(self.findButton(self.rc, 'Stop').isEnabled())
        self.assertTrue(self.findButton(self.rc, 'Record').isEnabled())
