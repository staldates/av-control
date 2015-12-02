from avx.devices.Device import Device
from mock import MagicMock
from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.tests.TestUtils import MockController
from staldates.ui.widgets.BlindsControl import BlindsControl
from staldates.ui.MainWindow import MainWindow


class TestBlindsControl(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = MockController()
        self.mockBlindsDevice = Device("Test")
        self.mockController.addDevice(self.mockBlindsDevice)
        self.mockMainWindow = MainWindow(self.mockController)

    def testBlinds(self):
        bc = BlindsControl(self.mockBlindsDevice, self.mockMainWindow)

        self.mockBlindsDevice.raiseUp = MagicMock()
        self.mockBlindsDevice.lower = MagicMock()
        self.mockBlindsDevice.stop = MagicMock()

        self.findButton(bc, "All").click()
        self.findButton(bc, "Raise").click()
        self.mockBlindsDevice.raiseUp.assert_called_once_with(0)
        self.findButton(bc, "Lower").click()
        self.mockBlindsDevice.lower.assert_called_once_with(0)
        self.findButton(bc, "Stop").click()
        self.mockBlindsDevice.stop.assert_called_once_with(0)

        self.mockBlindsDevice.raiseUp.reset_mock()
        self.mockBlindsDevice.lower.reset_mock()
        self.mockBlindsDevice.stop.reset_mock()

        self.findButton(bc, "3").click()
        self.findButton(bc, "Raise").click()
        self.mockBlindsDevice.raiseUp.assert_called_once_with(3)
        self.findButton(bc, "Lower").click()
        self.mockBlindsDevice.lower.assert_called_once_with(3)
        self.findButton(bc, "Stop").click()
        self.mockBlindsDevice.stop.assert_called_once_with(3)

        self.mockMainWindow.stepBack = MagicMock()
        self.findButton(bc, "Back").click()
        self.assertEqual(1, self.mockMainWindow.stepBack.call_count)
