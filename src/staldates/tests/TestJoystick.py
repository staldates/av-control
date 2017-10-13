from staldates.joystick import Joystick, Direction, Zoom, CameraJoystickAdapter

import unittest
import struct
from mock import MagicMock


EVENT_FORMAT = "IhBB"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)


class TestJoystick(unittest.TestCase):
    def testEventParsing(self):
        js = Joystick('/dev/null')

        button_handler = MagicMock()
        axis_handler = MagicMock()

        js.add_axis_handler(axis_handler)
        js.add_button_handler(button_handler)

        evtBtn1Press = struct.pack(EVENT_FORMAT, 1138, 1, 0x01, 1)
        js.parse_event(evtBtn1Press)
        button_handler.assert_called_once_with(1, 1)
        button_handler.reset_mock()

        evtBtn1Release = struct.pack(EVENT_FORMAT, 1138, 0, 0x01, 1)
        js.parse_event(evtBtn1Release)
        button_handler.assert_called_once_with(1, 0)
        button_handler.reset_mock()

        evtAxis1 = struct.pack(EVENT_FORMAT, 1138, 12345, 0x02, 1)
        js.parse_event(evtAxis1)
        axis_handler.assert_called_once_with(1, 12345)
        axis_handler.reset_mock()

        evtAxis3 = struct.pack(EVENT_FORMAT, 1138, -15432, 0x02, 3)
        js.parse_event(evtAxis3)
        axis_handler.assert_called_once_with(3, -15432)
        axis_handler.reset_mock()

    def testDirection(self):
        def do_test(x, y, expected):
            direction = Direction.from_axes(x, y)
            self.assertEqual(expected, direction)

        for x, y, expected in [
            (0, 0, Direction.STOP),
            (0, 1, Direction.UP),
            (1, 1, Direction.UP_RIGHT),
            (1, 0, Direction.RIGHT),
            (1, -1, Direction.DOWN_RIGHT),
            (0, -1, Direction.DOWN),
            (-1, -1, Direction.DOWN_LEFT),
            (-1, 0, Direction.LEFT),
            (-1, 1, Direction.UP_LEFT),
        ]:
            do_test(x, y, expected)

        # Test deadzone
        self.assertEqual(Direction.STOP, Direction.from_axes(10, 10, 10))

    def testZoom(self):
        def do_test(z, expected):
            zoom = Zoom.from_axis(z)
            self.assertEqual(expected, zoom)

        for z, expected in [
            (0, Zoom.STOP),
            (-1, Zoom.OUT),
            (1, Zoom.IN)
        ]:
            do_test(z, expected)


class TestCameraJoystickAdapter(unittest.TestCase):
    def testHandlesAxes(self):
        camera = MagicMock()

        cja = CameraJoystickAdapter(None)
        cja.set_camera(camera)

        cja._handle_axis(1, -32768)
        cja._update_camera()
        camera.moveDown.assert_called_once_with(1, 20)

        cja._handle_axis(1, 32767)
        cja._update_camera()
        camera.moveUp.assert_called_once_with(1, 20)

        cja._handle_axis(1, 0)
        cja._update_camera()
        camera.stop.assert_called_once()

        camera.reset_mock()

        cja._handle_axis(0, 1)
        cja._update_camera()
        camera.moveRight.assert_called_once_with(1, 1)

        cja._handle_axis(0, -1)
        cja._update_camera()
        camera.moveLeft.assert_called_once_with(1, 1)

        cja._handle_axis(0, 0)
        cja._update_camera()
        camera.stop.assert_called_once()

        cja._handle_axis(3, -32768)
        cja._update_camera()
        camera.zoomOut.assert_called_once_with(7)

        cja._handle_axis(3, 32767)
        cja._update_camera()
        camera.zoomIn.assert_called_once_with(7)

        cja._handle_axis(3, 0)
        cja._update_camera()
        camera.zoomStop.assert_called_once()

    def testCallsOnMove(self):
        camera = MagicMock()
        cja = CameraJoystickAdapter(None)
        cja.set_camera(camera)

        on_move = MagicMock()
        cja.set_on_move(on_move)

        cja._handle_axis(0, -16535)
        cja._update_camera()
        cja._handle_axis(0, 0)
        cja._update_camera()

        on_move.assert_called_once()
