from staldates.ui.tests.GuiTest import GuiTest
from mock import MagicMock
from staldates.ui.widgets.OverlayControl import OverlayControl
from avx.devices.net.atem.constants import VideoSource


class TestOverlayControl(GuiTest):
    def setUp(self):
        self.atem = MagicMock()
        self.dsk = MagicMock()
        self.dsk.idx = 0
        self.dsk.onAir = False
        self.dsk.rate = 10

        self.oc = OverlayControl(self.dsk, self.atem)

    def testInitialisation(self):
        self.dsk.changedState.connect.assert_called_once_with(self.oc.update_from_dsk)

        self.atem.setDSKFillSource.assert_called_once_with(0, VideoSource.INPUT_5)
        self.atem.setDSKKeySource.assert_called_once_with(0, VideoSource.INPUT_5)
        self.atem.setDSKParams.assert_called_once_with(0, preMultiplied=False, gain=500, clip=210)

    def testSetRate(self):
        self.atem.reset_mock()
        self.findButton(self.oc, "+").click()
        self.atem.setDSKRate.assert_called_once_with(0, 11)
        self.assertEqual(11, self.oc.rate.value())

        self.atem.reset_mock()
        self.findButton(self.oc, "-").click()
        self.atem.setDSKRate.assert_called_once_with(0, 10)
        self.assertEqual(10, self.oc.rate.value())

    def testOnAir(self):
        btnOnAir = self.findButton(self.oc, "On Air")
        btnAutoFade = self.findButton(self.oc, "Auto Fade")

        self.assertFalse(btnOnAir.isChecked())
        btnOnAir.click()

        self.atem.setDSKOnAir.assert_called_once_with(0, True)
        self.dsk.onAir = True
        self.oc.update_from_dsk()
        self.assertTrue(btnOnAir.isChecked())

        btnAutoFade.click()
        self.atem.performDSKAuto.assert_called_once_with(0)
        self.dsk.onAir = False
        self.oc.update_from_dsk()
        self.assertFalse(btnOnAir.isChecked())
