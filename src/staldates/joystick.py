from enum import Enum
from threading import Thread

import math
import struct
import time
from avx.devices.serial.VISCACamera import VISCACamera


EVENT_BUTTON = 0x01  # button pressed/released
EVENT_AXIS = 0x02  # axis moved
EVENT_INIT = 0x80  # button/axis initialized
EVENT_FORMAT = "IhBB"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)


class Joystick(Thread):
    def __init__(self, device):
        super(Joystick, self).__init__()

        self._axis_handlers = []
        self._button_handlers = []
        self.device = open(device, 'r')

    def add_axis_handler(self, handler):
        self._axis_handlers.append(handler)

    def add_button_handler(self, handler):
        self._button_handlers.append(handler)

    def _on_axis(self, axis, value):
        for handler in self._axis_handlers:
            handler(axis, value)

    def _on_button(self, button, value):
        for handler in self._button_handlers:
            handler(button, value)

    def run(self):
        while True:
            evt = self.device.read(EVENT_SIZE)
            time, value, evt_type, number = struct.unpack(EVENT_FORMAT, evt)

            if (evt_type & ~EVENT_INIT) == EVENT_AXIS:
                # print "{} Axis {}: value {}".format(time, number, value)
                self._on_axis(number, value)
            elif (evt_type & ~EVENT_INIT) == EVENT_BUTTON:
                # print "{} Button {}: value {}".format(time, number, value)
                self._on_button(number, value)


class Direction(Enum):
    UP = "moveUp"
    UP_RIGHT = "moveUpRight"
    RIGHT = "moveRight"
    DOWN_RIGHT = "moveDownRight"
    DOWN = "moveDown"
    DOWN_LEFT = "moveDownLeft"
    LEFT = "moveLeft"
    UP_LEFT = "moveUpLeft"
    STOP = "stop"

    @staticmethod
    def from_axes(x, y, deadzone=0):
        y = -1 * y
        if x > deadzone:
            if y > deadzone:
                return Direction.UP_RIGHT
            elif y < -1 * deadzone:
                return Direction.DOWN_RIGHT
            else:
                return Direction.RIGHT
        elif x < -1 * deadzone:
            if y > deadzone:
                return Direction.UP_LEFT
            elif y < -1 * deadzone:
                return Direction.DOWN_LEFT
            else:
                return Direction.LEFT
        else:
            if y > deadzone:
                return Direction.UP
            elif y < -1 * deadzone:
                return Direction.DOWN
            else:
                return Direction.STOP


class Zoom(Enum):
    IN = "zoomIn"
    OUT = "zoomOut"
    STOP = "zoomStop"

    @staticmethod
    def from_axis(axis, deadzone=0):
        if axis > deadzone:
            return Zoom.IN
        elif axis < -1 * deadzone:
            return Zoom.OUT
        return Zoom.STOP


def pan_speed_from_axis(axis):
    # Must return between 1 and 24 inclusive (0 when stopped)
    raw = abs(axis)
    return int(1 + math.ceil(23 * raw / 32767))


def tilt_speed_from_axis(axis):
    # Must return between 1 and 20 inclusive (0 when stopped)
    raw = abs(axis)
    return int(1 + math.ceil(19 * raw / 32767))


def zoom_speed_from_axis(axis):
    # Must return between 2 and 7 inclusive
    raw = abs(axis)
    return int(2 + math.ceil(5 * raw / 32767))


class CameraJoystickAdapter(Thread):
    def __init__(self, js, map_pan=pan_speed_from_axis, map_tilt=tilt_speed_from_axis, map_zoom=zoom_speed_from_axis):
        super(CameraJoystickAdapter, self).__init__()
        if js:
            js.add_axis_handler(self._handle_axis)
        self._axes = [0, 0, 0, 0]
        self.map_pan = map_pan
        self.map_tilt = map_tilt
        self.map_zoom = map_zoom
        self.set_camera(None)

    def set_camera(self, camera):
        self._camera = camera
        self._last_sent_pan_tilt = None
        self._last_sent_zoom = None

    def _handle_axis(self, axis, value):
        if axis > 3:
            return

        self._axes[axis] = value

    def run(self):
        while True:
            self._update_camera()
            time.sleep(0.1)

    def _update_camera(self):
        if self._camera is None:
            return
        direction = Direction.from_axes(self._axes[0], self._axes[1])
        pan_speed = self.map_pan(self._axes[0])
        tilt_speed = self.map_tilt(self._axes[1])

        if (direction, pan_speed, tilt_speed) != self._last_sent_pan_tilt:
            self._last_sent_pan_tilt = (direction, pan_speed, tilt_speed)
            # print self._last_sent_pan_tilt
            getattr(self._camera, direction.value)(pan_speed, tilt_speed)

        zoom_dir = Zoom.from_axis(self._axes[3])
        zoom_speed = self.map_zoom(self._axes[3])

        if (zoom_dir, zoom_speed) != self._last_sent_zoom:
            self._last_sent_zoom = (zoom_dir, zoom_speed)
            # print self._last_sent_zoom
            if zoom_dir == Zoom.STOP:
                self._camera.zoomStop()
            else:
                getattr(self._camera, zoom_dir.value)(zoom_speed)


if __name__ == "__main__":
    dev_str = "/dev/input/js1"
    js = Joystick(dev_str)
    cja = CameraJoystickAdapter(js)

    cam = VISCACamera("Camera 1", "/dev/ttyUSB0", 1)
    cam.initialise()

    cja.set_camera(cam)
    js.start()
    cja.start()
