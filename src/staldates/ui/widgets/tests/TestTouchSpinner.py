from mock import MagicMock, call
from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.widgets.TouchSpinner import TouchSpinner


class TestTouchSpinner(GuiTest):
    def testValueChange(self):
        ts = TouchSpinner()
        signal_receiver = MagicMock()
        ts.valueChanged.connect(signal_receiver)

        self.assertEqual(50, ts.value())
        self.findButton(ts, '+').click()
        self.assertEqual(51, ts.value())
        self.findButton(ts, '-').click()
        self.assertEqual(50, ts.value())

        signal_receiver.assert_has_calls([
            call(51),
            call(50)
        ])

        ts.valueChanged.disconnect(signal_receiver)

    def testMinMax(self):
        ts = TouchSpinner()
        ts.setMinimum(49)
        ts.setMaximum(51)

        plus = self.findButton(ts, '+')
        minus = self.findButton(ts, '-')

        self.assertEqual(50, ts.value())
        plus.click()
        self.assertEqual(51, ts.value())
        self.assertFalse(plus.isEnabled())
        minus.click()
        minus.click()
        self.assertTrue(plus.isEnabled())
        self.assertFalse(minus.isEnabled())

        ts.setValue(52)
        self.assertEqual(51, ts.value())
        ts.setValue(42)
        self.assertEqual(49, ts.value())
