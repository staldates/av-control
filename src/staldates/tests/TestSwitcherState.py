from unittest import TestCase
from staldates.VisualsSystem import SwitcherState
from mock import MagicMock
from avx.devices.net.atem.constants import VideoSource, MessageTypes


class TestSwitcherState(TestCase):

    def testTally(self):
        atem = MagicMock()
        ss = SwitcherState(atem)
        inp = ss.inputs[VideoSource.INPUT_1]

        self.assertFalse(inp.isLive)
        self.assertFalse(inp.isPreview)

        ss.handleMessage(MessageTypes.TALLY, {VideoSource.INPUT_1: {'pgm': False, 'prv': True}})
        self.assertFalse(inp.isLive)
        self.assertTrue(inp.isPreview)

        ss.handleMessage(MessageTypes.TALLY, {VideoSource.INPUT_1: {'pgm': True, 'prv': False}})
        self.assertTrue(inp.isLive)
        self.assertFalse(inp.isPreview)

        ss.handleMessage(MessageTypes.TALLY, {VideoSource.INPUT_1: {'pgm': True, 'prv': True}})
        self.assertTrue(inp.isLive)
        self.assertTrue(inp.isPreview)

    def testLoadInputList(self):
        atem = MagicMock()

        atem.getInputs.return_value = {VideoSource.COLOUR_1: {'name_long': 'A long name for a new input', 'me_availability': {'ME1': True}}}
        ss = SwitcherState(atem)

        atem.getInputs.assert_called_once()
        self.assertTrue(VideoSource.COLOUR_1 in ss.inputs)
        self.assertEqual('A long name for a new input', ss.inputs[VideoSource.COLOUR_1].label)
