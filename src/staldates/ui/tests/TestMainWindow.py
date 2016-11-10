'''
Created on 17 Apr 2013

@author: jrem
'''
from mock import MagicMock
from staldates.ui.MainWindow import MainWindow
from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.tests.TestUtils import MockController
from staldates.ui.VideoSwitcher import VideoSwitcher
from staldates.ui.widgets.SystemPowerWidget import SystemPowerScreen
from staldates.ui.widgets.LogViewer import LogViewerScreen
from staldates.ui.widgets.ProjectorScreensControl import ProjectorScreensControlScreen
from avx.devices.Device import Device


class TestMainWindow(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = MockController()
        self.mockController.sequence = MagicMock(return_value=1)

        self.screens = Device("Screens")
        self.screens.lower = MagicMock(return_value=1)
        self.screens.raiseUp = MagicMock(return_value=1)
        self.screens.stop = MagicMock(return_value=1)
        self.mockController.addDevice(self.screens)

        self.main = MainWindow(self.mockController)

    def getCurrentScreen(self):
        return self.main.stack.currentWidget()

    def testSystemPower(self):
        spcButton = self.findButton(self.main, "Power")
        self.assertFalse(spcButton is None)

        spcButton.click()
        spc = self.getCurrentScreen()
        self.assertTrue(isinstance(spc, SystemPowerScreen))
        self.findButton(spc, "On").click()
        self.assertEquals(self.mockController.sequence.call_count, 1)

        self.findButton(spc, "Off").click()
        self.assertEquals(self.mockController.sequence.call_count, 2)
        # Probably ought to verify exactly what has been sequenced...

        self.findButton(spc, "Back").click()
        self.assertTrue(isinstance(self.main.stack.currentWidget(), VideoSwitcher))

    def testLog(self):
        entry = FakeLogEntry("2013-04-17 18:45:38", "ERROR", "This is a test message")
        self.mockController.getLog = MagicMock(return_value=[entry])

        advMenuButton = self.findButton(self.main, "Advanced")
        advMenuButton.click()
        top = self.getCurrentScreen()

        logButton = self.findButton(top, "Log")
        logButton.click()
        lw = self.main.stack.currentWidget()
        self.assertTrue(isinstance(lw, LogViewerScreen))
        self.assertEqual(self.mockController.getLog.call_count, 1)

    def testScreens(self):
        self.findButton(self.main, "Screens").click()
        top = self.getCurrentScreen()
        self.assertTrue(isinstance(top, ProjectorScreensControlScreen))

        self.findButton(top, "Raise").click()
        self.screens.raiseUp.assert_called_once_with(0)

        self.findButton(top, "Lower").click()
        self.screens.lower.assert_called_once_with(0)

        self.findButton(top, "Stop").click()
        self.screens.stop.assert_called_once_with(0)

        self.screens.lower.reset_mock()
        self.screens.raiseUp.reset_mock()

        self.findButton(top, "Left").click()
        self.findButton(top, "Raise").click()
        self.screens.raiseUp.assert_called_once_with(1)
        self.findButton(top, "Right").click()
        self.findButton(top, "Lower").click()
        self.screens.lower.assert_called_once_with(2)


class FakeLogEntry(object):

    def __init__(self, asctime, level, message):
        self.asctime = asctime
        self.levelname = level
        self.message = message
