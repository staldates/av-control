'''
Created on 18 Apr 2013

@author: james
'''
from avx.devices.Device import Device
from mock import MagicMock
from staldates.ui.EclipseControls import EclipseControls
from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.tests.TestUtils import MockController


class TestEclipseControls(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = MockController()

        self.conv = Device("Test Scan Converter")
        self.conv.fadeIn = MagicMock(return_value=1)
        self.conv.fadeOut = MagicMock(return_value=1)
        self.conv.overlayOn = MagicMock(return_value=1)
        self.conv.overlayOff = MagicMock(return_value=1)
        self.conv.overscanOn = MagicMock(return_value=1)
        self.conv.overscanOff = MagicMock(return_value=1)
        self.conv.freeze = MagicMock(return_value=1)
        self.conv.unfreeze = MagicMock(return_value=1)
        self.mockController.addDevice(self.conv)

    def testControls(self):

        ec = EclipseControls(self.mockController, "Test Scan Converter")
        self.findButton(ec, "Overscan").click()
        self.conv.overscanOff.assert_called_once_with()
        self.findButton(ec, "Overscan").click()
        self.conv.overscanOn.assert_called_once_with()

        self.findButton(ec, "Freeze").click()
        self.conv.freeze.assert_called_once_with()
        self.findButton(ec, "Freeze").click()
        self.conv.unfreeze.assert_called_once_with()

        self.findButton(ec, "Fade").click()
        self.conv.fadeOut.assert_called_once_with()
        self.findButton(ec, "Fade").click()
        self.conv.fadeIn.assert_called_once_with()

        self.findButton(ec, "Overlay").click()
        self.conv.overlayOn.assert_called_once_with()
        self.findButton(ec, "Overlay").click()
        self.conv.overlayOff.assert_called_once_with()
