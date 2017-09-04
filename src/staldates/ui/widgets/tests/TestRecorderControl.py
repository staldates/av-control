from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.widgets.RecorderControl import RecorderControl
from mock import MagicMock
from avx.devices.net.hyperdeck import TransportState


class TestRecorderControl(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        mainWindow = MagicMock()
        state = MagicMock()
        self.hyperdeck = MagicMock()

        state.transport = {'status': TransportState.STOPPED}

        self.rc = RecorderControl(self.hyperdeck, state, mainWindow)

    def testTransportControls(self):
        self.assertTrue(self.rc.btnStop.isChecked())
        self.assertFalse(self.rc.btnPlay.isChecked())
        self.assertFalse(self.rc.btnRecord.isChecked())

        self.rc.btnRecord.click()
        self.hyperdeck.record.assert_called_once()
        self.rc.btnStop.click()
        self.hyperdeck.stop.assert_called_once()
        self.rc.btnPlay.click()
        self.hyperdeck.play.assert_called_once()
        self.findButton(self.rc, "Back").click()
        self.hyperdeck.prev.assert_called_once()
        self.findButton(self.rc, "Forward").click()
        self.hyperdeck.next.assert_called_once()

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
