from staldates.ui.tests.GuiTest import GuiTest
from mock import MagicMock
from staldates.VisualsSystem import Output
from staldates.ui.widgets.OutputsGrid import OutputsGrid
from avx.devices.net.atem.constants import VideoSource


class TestOutputsGrid(GuiTest):
    def testSendSignals(self):
        ss = MagicMock()
        ss.outputs = {
            0: Output("Aux 1", VideoSource.AUX_1),
            1: Output("Aux 2", VideoSource.AUX_2),
        }

        og = OutputsGrid(ss)
        handler = MagicMock()
        og.selected.connect(handler)

        btn = self.findButton(og, "Aux 1")
        self.assertTrue(btn is not None)
        btn.click()
        handler.assert_called_once_with(0)
        handler.reset_mock()

        btn = self.findButton(og, "Aux 2")
        self.assertTrue(btn is not None)
        btn.click()
        handler.assert_called_once_with(1)

        takeHandler = MagicMock()
        og.take.connect(takeHandler)

        btn = self.findButton(og, "Church / Main")
        self.assertTrue(btn is not None)
        btn.click()
        takeHandler.assert_called_once_with()

        allHandler = MagicMock()
        og.all.connect(allHandler)

        btn = self.findButton(og, "All")
        self.assertTrue(btn is not None)
        btn.click()
        takeHandler.assert_called_once_with()

        mainToAllHandler = MagicMock()
        og.mainToAll.connect(mainToAllHandler)

        btn = self.findButton(og, "Main to\nall auxes")
        self.assertTrue(btn is not None)
        btn.click()
        mainToAllHandler.assert_called_once_with()
