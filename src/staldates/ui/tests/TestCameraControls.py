'''
Created on 15 Apr 2013

@author: jrem
'''
from avx.CameraPosition import CameraPosition
from avx.devices.Device import Device
from mock import MagicMock
from PySide.QtCore import Qt
from PySide.QtTest import QTest
from staldates.ui.CameraControls import CameraControl, AdvancedCameraControl
from staldates.ui.tests.GuiTest import GuiTest


class Test(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)

        self.mockMainWindow = MagicMock()

        self.cam = Device("Test Camera")
        self.cam.moveUp = MagicMock(return_value=1)
        self.cam.moveDown = MagicMock(return_value=1)
        self.cam.moveLeft = MagicMock(return_value=1)
        self.cam.moveRight = MagicMock(return_value=1)
        self.cam.stop = MagicMock(return_value=1)
        self.cam.recallPreset = MagicMock(return_value=1)
        self.cam.whiteBalanceAuto = MagicMock(return_value=1)
        self.cam.whiteBalanceIndoor = MagicMock(return_value=1)
        self.cam.whiteBalanceOutdoor = MagicMock(return_value=1)
        self.cam.whiteBalanceOnePush = MagicMock(return_value=1)
        self.cam.whiteBalanceOnePushTrigger = MagicMock(return_value=1)
        self.cam.zoomIn = MagicMock(return_value=1)
        self.cam.zoomOut = MagicMock(return_value=1)
        self.cam.zoomStop = MagicMock(return_value=1)
        self.cam.focusNear = MagicMock(return_value=1)
        self.cam.focusFar = MagicMock(return_value=1)
        self.cam.focusStop = MagicMock(return_value=1)
        self.cam.focusAuto = MagicMock(return_value=1)
        self.cam.backlightCompOn = MagicMock(return_value=1)
        self.cam.backlightCompOff = MagicMock(return_value=1)
        self.cam.storePreset = MagicMock(return_value=1)
        self.cam.recallPreset = MagicMock(return_value=1)

        self.cc = CameraControl(self.cam)

    def testCannotSelectMultiplePresets(self):
        ''' See https://github.com/jamesremuscat/aldatesx/issues/23'''
        buttons = self.cc.presetGroup.buttons()

        self.assertEqual(-1, self.cc.presetGroup.checkedId())
        self.cc.btnDown.click()
        buttons[1].click()
        self.assertTrue(buttons[1].isChecked())
        self.assertFalse(buttons[0].isChecked())
        buttons[0].click()
        self.assertEqual(0, self.cc.presetGroup.checkedId())
        self.assertTrue(buttons[0].isChecked())
        self.assertFalse(buttons[1].isChecked())

    def testMoveCamera(self):
        self.cc.btnUp.pressed.emit()
        self.cam.moveUp.assert_called_once_with()
        self.cc.btnUp.released.emit()
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

        self.cc.btnDown.pressed.emit()
        self.cam.moveDown.assert_called_once_with()
        self.cc.btnDown.released.emit()
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

        self.cc.btnLeft.pressed.emit()
        self.cam.moveLeft.assert_called_once_with()
        self.cc.btnLeft.released.emit()
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

        self.cc.btnRight.pressed.emit()
        self.cam.moveRight.assert_called_once_with()
        self.cc.btnRight.released.emit()
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

    def testMoveCameraWithKeyboard(self):
        QTest.keyPress(self.cc, Qt.Key_Up)
        self.cam.moveUp.assert_called_once_with()
        QTest.keyRelease(self.cc, Qt.Key_Up)
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

        QTest.keyPress(self.cc, Qt.Key_Down)
        self.cam.moveDown.assert_called_once_with()
        QTest.keyRelease(self.cc, Qt.Key_Down)
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

        QTest.keyPress(self.cc, Qt.Key_Left)
        self.cam.moveLeft.assert_called_once_with()
        QTest.keyRelease(self.cc, Qt.Key_Left)
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

        QTest.keyPress(self.cc, Qt.Key_Right)
        self.cam.moveRight.assert_called_once_with()
        QTest.keyRelease(self.cc, Qt.Key_Right)
        self.cam.stop.assert_called_once_with()
        self.cam.stop.reset_mock()

    def testPresets(self):
        self.findButton(self.cc, "2").click()
        self.cam.recallPreset.assert_called_once_with(1)
        self.findButton(self.cc, "Set").click()  # finds the first one
        self.cam.storePreset.assert_called_once_with(0)
        self.assertEquals(0, self.cc.presetGroup.checkedId())

# Tests for advanced camera controls

    def testGetCameraPosition(self):
        fakePosition = CameraPosition(111, 222, 333)
        self.cam.getPosition = MagicMock(return_value=fakePosition)
        self.acc = AdvancedCameraControl("Test", self.cam, self.mockMainWindow)
        self.findButton(self.acc, "Get Position").click()
        self.cam.getPosition.assert_called_once_with()
        self.assertEqual("111", self.acc.posDisplay.itemAtPosition(0, 1).widget().text())
        self.assertEqual("222", self.acc.posDisplay.itemAtPosition(1, 1).widget().text())
        self.assertEqual("333", self.acc.posDisplay.itemAtPosition(2, 1).widget().text())

    def testChangeWhiteBalance(self):
        self.acc = AdvancedCameraControl("Test", self.cam, self.mockMainWindow)
        self.assertFalse(self.findButton(self.acc, "Set").isEnabled())

        self.findButton(self.acc, "Auto").click()
        self.cam.whiteBalanceAuto.assert_called_once_with()
        self.assertFalse(self.findButton(self.acc, "Set").isEnabled())

        self.findButton(self.acc, "Indoor").click()
        self.cam.whiteBalanceIndoor.assert_called_once_with()
        self.assertFalse(self.findButton(self.acc, "Set").isEnabled())

        self.findButton(self.acc, "Outdoor").click()
        self.cam.whiteBalanceOutdoor.assert_called_once_with()
        self.assertFalse(self.findButton(self.acc, "Set").isEnabled())

        self.findButton(self.acc, "One Push").click()
        self.cam.whiteBalanceOnePush.assert_called_once_with()
        self.assertTrue(self.findButton(self.acc, "Set").isEnabled())

        self.findButton(self.acc, "Set").click()
        self.cam.whiteBalanceOnePushTrigger.assert_called_once_with()
