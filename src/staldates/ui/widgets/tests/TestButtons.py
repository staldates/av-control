from staldates.ui.tests.GuiTest import GuiTest
from staldates.VisualsSystem import Input, Output
from avx.devices.net.atem.constants import VideoSource
from staldates.ui.widgets.Buttons import InputButton, OutputButton


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

    def testOutputButton(self):
        some_input = Input(VideoSource.INPUT_1, "My input", None)
        main_mix = Input(VideoSource.ME_1_PROGRAM, "Main mix", None)

        my_output = Output("Some Output", VideoSource.AUX_1)

        ob = OutputButton(my_output)
        ob_state = ob.stateDisplay

        self.assertEqual('-', ob_state.text())
        self.assertFalse(ob_state.property("highlight"))

        my_output.set_source(some_input)
        self.assertEqual('My input', ob_state.text())
        self.assertTrue(ob_state.property("highlight"))

        my_output.set_source(main_mix)
        self.assertEqual('Main mix', ob_state.text())
        self.assertFalse(ob_state.property("highlight"))
