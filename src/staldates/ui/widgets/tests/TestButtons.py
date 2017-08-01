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
        self.assertEqual("A new\nlabel", ib.text())

        self.assertFalse(ib.property("isLive"))
        self.assertFalse(ib.property("isPreview"))

        my_input.set_live(True)
        self.assertTrue(ib.property("isLive"))
        self.assertFalse(ib.property("isPreview"))

        my_input.set_live(False)
        self.assertFalse(ib.property("isLive"))
        self.assertFalse(ib.property("isPreview"))

        my_input.set_preview(True)
        self.assertFalse(ib.property("isLive"))
        self.assertTrue(ib.property("isPreview"))

        my_input.set_preview(False)
        self.assertFalse(ib.property("isLive"))
        self.assertFalse(ib.property("isPreview"))
