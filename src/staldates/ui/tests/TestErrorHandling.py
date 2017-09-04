from PySide import QtCore, QtGui
from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.widgets.Dialogs import handlePyroErrors

import Pyro4


class TestErrorHandling(GuiTest):

    def _testDialogShowsWithText(self, func, dialog_text):
        def assert_about_dialog(dia):
            self.assertFalse(dia.isHidden())
            self.assertTrue(dia.text().startswith("<span style=\"color: white;\">{}".format(dialog_text)), "Dialog text was {}, expected {}".format(dia.text(), dialog_text))
            return True

        def close_dialog():
            found_dialog = False
            for tlw in self.app.topLevelWidgets():
                if tlw.__class__ == QtGui.QMessageBox:
                    found_dialog = True
                    try:
                        self.test_result = assert_about_dialog(tlw)
                    finally:
                        tlw.accept()
            self.assertTrue(found_dialog)

        t = QtCore.QTimer()
        t.timeout.connect(close_dialog)
        t.start(0.5)

        self.test_result = False

        func()

        self.assertTrue(self.test_result, "Test failed, see earlier output for details.")

    def testHandlePyroErrors(self):
        def timeout():
            raise Pyro4.errors.TimeoutError()

        def comms():
            raise Pyro4.errors.CommunicationError()

        self._testDialogShowsWithText(handlePyroErrors(timeout), "Communication with the controller timed out.")
        self._testDialogShowsWithText(handlePyroErrors(comms), "(CommunicationError)")
        self._testDialogShowsWithText(handlePyroErrors(comms, "Extra message"), "Extra message")
