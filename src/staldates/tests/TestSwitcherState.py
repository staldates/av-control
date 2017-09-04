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

    def testUpdateInputs(self):
        atem = MagicMock()

        atem.getInputs.return_value = {
            VideoSource.COLOUR_1: {'name_long': 'A long name for a new input', 'me_availability': {'ME1': True}},
            VideoSource.AUX_1: {'name_long': 'A label for the output', 'me_availability': {'ME1': False}}
        }
        ss = SwitcherState(atem)

        atem.getInputs.assert_called_once()
        self.assertTrue(VideoSource.COLOUR_1 in ss.inputs)
        self.assertEqual('A long name for a new input', ss.inputs[VideoSource.COLOUR_1].label)
        self.assertEqual("A label for the output", ss.outputs[0].label)

        atem.getInputs.return_value = {
            VideoSource.COLOUR_1: {'name_long': 'a new name for the existing input', 'me_availability': {'ME1': True}},
            VideoSource.AUX_1: {'name_long': 'A label for the output', 'me_availability': {'ME1': False}}
        }

        ss.handleMessage(MessageTypes.INPUTS_CHANGED, None)
        self.assertEqual('a new name for the existing input', ss.inputs[VideoSource.COLOUR_1].label)

    def testUpdateOutputs(self):
        atem = MagicMock()
        atem.getAuxState.return_value = {0: VideoSource.INPUT_1, 1: VideoSource.COLOUR_1, 2: VideoSource.BLACK}
        ss = SwitcherState(atem)

        atem.getAuxState.assert_called_once()
        self.assertEqual(ss.inputs[VideoSource.INPUT_1], ss.outputs[0].source)
        self.assertEqual(VideoSource.COLOUR_1, ss.outputs[1].source)

        ss.handleMessage(MessageTypes.AUX_OUTPUT_MAPPING, {0: VideoSource.INPUT_2})
        self.assertEqual(ss.inputs[VideoSource.INPUT_2], ss.outputs[0].source)

    def testUpdateDSKs(self):
        atem = MagicMock()
        atem.getDSKState.return_value = {0: {'on_air': False, 'rate': 3}, 1: {'on_air': True, 'rate': 77}}
        ss = SwitcherState(atem)

        atem.getDSKState.assert_called_once()
        self.assertTrue(ss.dsks[1].onAir)

        handler = MagicMock()
        ss.dsks[1].changedState.connect(handler)

        ss.handleMessage(MessageTypes.DSK_STATE, {1: {'on_air': False, 'rate': 88}})
        self.assertEqual(2, handler.call_count)
        self.assertFalse(ss.dsks[1].onAir)
        self.assertEqual(88, ss.dsks[1].rate)

    def testUpdateFTB(self):
        atem = MagicMock()
        atem.getFadeToBlackState.return_value = {'full_black': True, 'in_transition': False}
        atem.getFadeToBlackProperties.return_value = {'rate': 17}
        ss = SwitcherState(atem)

        atem.getFadeToBlackState.assert_called_once()
        atem.getFadeToBlackProperties.assert_called_once()
        self.assertEqual(17, ss.ftb.rate)
        self.assertTrue(ss.ftb.active)

        aHandler = MagicMock()
        ss.ftb.activeChanged.connect(aHandler)
        ss.handleMessage(MessageTypes.FTB_CHANGED, {0: {'full_black': False, 'in_transition': False}})
        aHandler.assert_called_once()
        self.assertFalse(ss.ftb.active)

        rHandler = MagicMock()
        ss.ftb.rateChanged.connect(rHandler)
        ss.handleMessage(MessageTypes.FTB_RATE_CHANGED, {0: 42})
        rHandler.assert_called_once_with(42)
        self.assertEqual(42, ss.ftb.rate)
