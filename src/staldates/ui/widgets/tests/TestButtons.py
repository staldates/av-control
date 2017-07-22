from staldates.ui.tests.GuiTest import GuiTest
from staldates.VisualsSystem import Input
from avx.devices.net.atem.constants import VideoSource
from staldates.ui.widgets.Buttons import InputButton


class TestButtons(GuiTest):

    def testInputButton(self):
        my_input = Input(VideoSource.INPUT_1, "My input", None)

        ib = InputButton(my_input)
        self.assertEqual("My input", ib.text())

        my_input.set_label("A new label")
        self.assertEqual("A new label", ib.text())

        self.assertEqual("", ib.stateDisplay.text())
        my_input.set_live(True)
        self.assertEqual("LIVE", ib.stateDisplay.text())
        my_input.set_live(False)
        self.assertEqual("", ib.stateDisplay.text())

        my_input.set_preview(True)
        self.assertEqual("PREV", ib.stateDisplay.text())
        my_input.set_preview(False)
        self.assertEqual("", ib.stateDisplay.text())
