'''
Created on 16 Apr 2013

@author: jrem
'''
import unittest
from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.tests.TestUtils import MockController
from staldates.ui.VideoSwitcher import VideoSwitcher
from mock import MagicMock
from staldates.VisualsSystem import DSK
from staldates import VisualsSystem
from staldates.ui.widgets.AllInputsPanel import AllInputsPanel
from avx.devices.net.atem.constants import VideoSource


class TestVideoSwitcher(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = MockController()

        self.switcherState = MagicMock()
        self.switcherState.dsks = {0: DSK(1)}
        self.switcherState.inputs = VisualsSystem._default_inputs()

        self.mainWindow = MagicMock()

    def makeVS(self):
        return VideoSwitcher(self.mockController, self.mainWindow, self.switcherState)

    def testSelectiveInputButtons(self):
        # FSR tests will segfault if a camera device is added
        # I think it's as a result of Qt connect() calls
        # But still, it's useful to test that the camera buttons are hidden when
        # no cameras are present in the controller.
        vs = self.makeVS()
        self.assertTrue(self.findButton(vs, "Camera 1") is None)
        self.assertTrue(self.findButton(vs, "Camera 2") is None)
        self.assertTrue(self.findButton(vs, "Camera 3") is None)
        self.assertFalse(self.findButton(vs, "Extras") is None)

    def testExtrasButton(self):
        vs = self.makeVS()
        extrasBtn = self.findButton(vs, "Extras")

        self.assertFalse(extrasBtn is None)
        all_inputs = extrasBtn.property("panel")
        self.assertTrue(isinstance(all_inputs, AllInputsPanel))

        self.assertTrue(extrasBtn.input is None)  # At first, it has no input
        self.assertTrue(self.findButton(vs, "Camera 1") is None)  # No button for Camera 1 in window
        self.assertTrue(self.findButton(vs, "All").isEnabled())  # Before we click Extras, All button is enabled

        extrasBtn.click()

        self.assertFalse(self.findButton(vs, "Camera 1") is None)  # A Camera 1 button has appeared! (In the AllInputsPanel)
        self.assertFalse(self.findButton(vs, "All").isEnabled())  # Disabled as button has no input
        self.findButton(vs, "Camera 1").click()
        self.assertEqual(extrasBtn.input, self.switcherState.inputs[VideoSource.INPUT_1])  # Button has input set
        self.assertTrue(self.findButton(vs, "All").isEnabled())  # All button is enabled again


if __name__ == "__main__":
    unittest.main()
