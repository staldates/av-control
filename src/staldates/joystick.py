from enum import Enum
from Pyro4.errors import PyroError
from staldates.preferences import Preferences
from threading import Thread

import math
import struct
import time


EVENT_BUTTON = 0x01  # button pressed/released
EVENT_AXIS = 0x02  # axis moved
EVENT_INIT = 0x80  # button/axis initialized
EVENT_FORMAT = "IhBB"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)


class Joystick(Thread):
    def __init__(self, device):
        super(Joystick, self).__init__()
        self.daemon = True

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

    def parse_event(self, evt):
        _, value, evt_type, number = struct.unpack(EVENT_FORMAT, evt)

        if (evt_type & ~EVENT_INIT) == EVENT_AXIS:
            # print "{} Axis {}: value {}".format(time, number, value)
            self._on_axis(number, value)
        elif (evt_type & ~EVENT_INIT) == EVENT_BUTTON:
            # print "{} Button {}: value {}".format(time, number, value)
            self._on_button(number, value)

    def run(self):
        while True:
            evt = self.device.read(EVENT_SIZE)
            self.parse_event(evt)


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
    def from_axes(x, y, deadzone=0, invert_y=False):
        if invert_y:
            y = -y
        if x > deadzone:
            if y > deadzone:
                return Direction.UP_RIGHT
            elif y < -deadzone:
                return Direction.DOWN_RIGHT
            else:
                return Direction.RIGHT
        elif x < -deadzone:
            if y > deadzone:
                return Direction.UP_LEFT
            elif y < -deadzone:
                return Direction.DOWN_LEFT
            else:
                return Direction.LEFT
        else:
            if y > deadzone:
                return Direction.UP
            elif y < -deadzone:
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
        elif axis < -deadzone:
            return Zoom.OUT
        return Zoom.STOP


PREFS_INVERT_Y = 'joystick.invert_y'


class CameraJoystickAdapter(Thread):
    def __init__(self, js=None):
        super(CameraJoystickAdapter, self).__init__()
        self.daemon = True
        if js:
            js.add_axis_handler(self._handle_axis)
        self._axes = [0, 0, 0, 0]
        self.set_camera(None)
        self.set_on_move(None)
        self.update_preferences()
        Preferences.subscribe(self.update_preferences)

    def update_preferences(self):
        self.invert_y = Preferences.get(PREFS_INVERT_Y, False)

    def set_camera(self, camera):
        self._camera = camera
        self._last_sent_pan_tilt = None
        self._last_sent_zoom = (Zoom.STOP, 2)

    def set_on_move(self, on_move):
        self._on_move_inner = on_move

    def _on_move(self):
        if self._on_move_inner:
            self._on_move_inner()

    def _handle_axis(self, axis, value):
        if axis > 3:
            return

        self._axes[axis] = value

    def run(self):
        while True:
            self._update_camera()
            time.sleep(0.1)

    def map_pan(self, axis):
        """Should return a value between 1 and 24 inclusive."""
        raw = abs(axis)
        return int(1 + math.ceil(23 * raw / 32767))

    def map_tilt(self, axis):
        """Should return a value between 1 and 20 inclusive."""
        raw = abs(axis)
        return int(1 + math.ceil(19 * raw / 32767))

    def map_zoom(self, axis):
        """Should return a value between 2 and 7 inclusive."""
        raw = abs(axis)
        return int(2 + math.ceil(5 * raw / 32767))

    def _update_camera(self):
        if self._camera is None:
            return
        direction = Direction.from_axes(self._axes[0], self._axes[1], invert_y=self.invert_y)
        pan_speed = self.map_pan(self._axes[0])
        tilt_speed = self.map_tilt(self._axes[1])

        try:
            if (direction, pan_speed, tilt_speed) != self._last_sent_pan_tilt:
                getattr(self._camera, direction.value)(pan_speed, tilt_speed)
                self._last_sent_pan_tilt = (direction, pan_speed, tilt_speed)
                # print self._last_sent_pan_tilt

            zoom_dir = Zoom.from_axis(self._axes[3])
            zoom_speed = self.map_zoom(self._axes[3])

            if (zoom_dir, zoom_speed) != self._last_sent_zoom:
                if zoom_dir == Zoom.STOP:
                    self._camera.zoomStop()
                else:
                    getattr(self._camera, zoom_dir.value)(zoom_speed)
                self._last_sent_zoom = (zoom_dir, zoom_speed)
                # print self._last_sent_zoom

            if direction != Direction.STOP or zoom_dir != Zoom.STOP:
                self._on_move()
        except PyroError:
            pass


JOYSTICK_MAX = 32767
JOYSTICK_HALF = JOYSTICK_MAX / 2


def _linear_interp(raw, max_value, sensitivity):
    """Linearly interpolates values based on a given percentage sensitivity value.

    The sensitivity represents the percentage of max_value this function should return at 50% input (which is assumed to be a short e.g.
    the max value from a joystick axis will be 32767).

    Output value is determined by linear interpolation based on that point and the min/max possible output values.

    Setting sensitivity = 0.5 will result in a fully linear response across the entire joystick axis range.
    """
    sensitivity_value = math.ceil(max_value * sensitivity)
    if raw <= JOYSTICK_HALF:
        return max(1, int(math.ceil(sensitivity_value * raw / JOYSTICK_HALF)))
    else:
        return max(1, int(sensitivity_value + math.ceil((2 * (raw - JOYSTICK_HALF) * (max_value - 1 - sensitivity_value) / JOYSTICK_MAX))))


class SensitivityPrefsCameraJoystickAdapter(CameraJoystickAdapter):
    def __init__(self, js=None, interpolation_function=_linear_interp):
        CameraJoystickAdapter.__init__(self, js=js)
        self._interp = interpolation_function

    def update_preferences(self):
        CameraJoystickAdapter.update_preferences(self)
        self._set_speed_params()

    def set_camera(self, camera):
        super(SensitivityPrefsCameraJoystickAdapter, self).set_camera(camera)
        self._set_speed_params()

    def _set_speed_params(self):
        if self._camera:
            self.max_pan = self._camera.maxPanSpeed
            self.max_tilt = self._camera.maxTiltSpeed
            self.min_zoom = self._camera.minZoomSpeed
            self.max_zoom = self._camera.maxZoomSpeed
        else:
            self.max_pan = 0x18
            self.max_tilt = 0x14
            self.min_zoom = 2
            self.max_zoom = 7

        self.pan_sensitivity = Preferences.get('joystick.sensitivity.pan', 0.5)
        self.tilt_sensitivity = Preferences.get('joystick.sensitivity.tilt', 0.5)
        self.zoom_sensitivity = Preferences.get('joystick.sensitivity.zoom', 0.5)

    def map_pan(self, axis):
        return self._interp(abs(axis), self.max_pan, self.pan_sensitivity)

    def map_tilt(self, axis):
        return self._interp(abs(axis), self.max_tilt, self.tilt_sensitivity)

    def map_zoom(self, axis):
        return max(self.min_zoom, self._interp(abs(axis), self.max_zoom, self.zoom_sensitivity))
