from unittest import TestCase
from staldates.VisualsSystem import SwitcherState
from mock import MagicMock
from avx.devices.net.atem.constants import VideoSource, MessageTypes


class TestSwitcherState(TestCase):

    def setUp(self):
        self.atem = MagicMock()
        self.ss = SwitcherState(self.atem)

    def testTally(self):
        inp = self.ss.inputs[VideoSource.INPUT_1]

        self.assertFalse(inp.isLive)
        self.assertFalse(inp.isPreview)

        self.ss.handleMessage(MessageTypes.TALLY, {VideoSource.INPUT_1: {'pgm': False, 'prv': True}})
        self.assertFalse(inp.isLive)
        self.assertTrue(inp.isPreview)

        self.ss.handleMessage(MessageTypes.TALLY, {VideoSource.INPUT_1: {'pgm': True, 'prv': False}})
        self.assertTrue(inp.isLive)
        self.assertFalse(inp.isPreview)

        self.ss.handleMessage(MessageTypes.TALLY, {VideoSource.INPUT_1: {'pgm': True, 'prv': True}})
        self.assertTrue(inp.isLive)
        self.assertTrue(inp.isPreview)
