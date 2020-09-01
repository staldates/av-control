from avx.devices.net.atem.constants import VideoSource
from PySide.QtGui import QLabel, QToolButton, QSizePolicy, QVBoxLayout, QImage,\
    QPainter, QPixmap, QIcon, QHBoxLayout
from PySide.QtCore import Qt, QSize, Signal, QEvent, QTimer
from PySide.QtSvg import QSvgRenderer

import time


class DebouncedButtonMixin(object):
    DEBOUNCE_DELAY = 0.25

    def __init__(self, *args, **kwargs):
        super(DebouncedButtonMixin, self).__init__(*args, **kwargs)
        self._lastClick = time.time()

    def event(self, evt):
        if evt.type() == QEvent.MouseButtonRelease:
            now = time.time()
            if now - self._lastClick < self.DEBOUNCE_DELAY:
                evt.ignore()
                self.setDown(False)
                return True
            else:
                self._lastClick = now
        return super(DebouncedButtonMixin, self).event(evt)


class LongPressButtonMixin(object):
    longpress = Signal()

    def __init__(self, *args, **kwargs):
        super(LongPressButtonMixin, self).__init__(*args, **kwargs)
        self.grabGesture(Qt.TapAndHoldGesture)
        self._has_longpressed = False

    def event(self, evt):
        if evt.type() == QEvent.Gesture and self.isEnabled():
            gesture = evt.gesture(Qt.TapAndHoldGesture)
            if gesture:
                if gesture.state() == Qt.GestureState.GestureFinished:
                    self.longpress.emit()
                    self._has_longpressed = True
                    return True
        elif evt.type() == QEvent.MouseButtonPress:
            self._has_longpressed = False
        elif evt.type() == QEvent.MouseButtonRelease:
            if self._has_longpressed:
                evt.ignore()
                self.setDown(False)
                return True
        return super(LongPressButtonMixin, self).event(evt)


class ExpandingButton(DebouncedButtonMixin, QToolButton):

    def __init__(self, parent=None):
        super(ExpandingButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setIconSize(QSize(48, 48))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


def _add_line_breaks(text, every_n=10):
    if len(text) <= every_n:
        return text
    by_word = text.split(' ')

    lines = []
    line = ''
    while len(by_word) > 0:
        next_word = by_word.pop(0)
        if len(line) + len(next_word) + 1 > every_n:
            lines.append(line.strip())
            line = ''
        line += next_word + ' '
    lines.append(line.strip())

    return '\n'.join(lines)


class InputButton(LongPressButtonMixin, ExpandingButton):

    def __init__(self, myInput, main_me=1, parent=None):
        super(InputButton, self).__init__(parent)
        self.main_me = main_me
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        layout = QHBoxLayout()
        self.previewDot = QLabel()
        self.previewDot.setPixmap(pixmap_from_svg(':icons/preview_dot', 16, 16))
        self.previewDot.setVisible(False)
        layout.addWidget(self.previewDot)
        layout.setAlignment(self.previewDot, Qt.AlignTop)

        layout.addStretch()

        self.liveDot = QLabel()
        self.liveDot.setPixmap(pixmap_from_svg(':icons/live_dot', 16, 16))
        self.liveDot.setVisible(False)
        layout.addWidget(self.liveDot)
        layout.setAlignment(self.liveDot, Qt.AlignTop)

        self.setLayout(layout)

        self.input = None
        self.setInput(myInput)

    def setInput(self, myInput):
        if self.input:
            self.input.changedState.disconnect(self._update_from_input)
        self.input = myInput
        if self.input:
            self.input.changedState.connect(self._update_from_input)
            self._update_from_input()
        else:
            self.setIcon(QIcon())
            self.setText("Extras")

    def _update_from_input(self):
        self.setText(_add_line_breaks(self.input.label))
        if self.input.icon:
            self.setIcon(self.input.icon)
        else:
            self.setIcon(QIcon())

        me_tally = self.input.tally.get(self.main_me - 1, {'pgm': False, 'pvw': False})

        self.setProperty("isLive", me_tally['pgm'])
        self.setProperty("isPreview", me_tally['pvw'])

        isPreviewElsewhere = False
        isLiveElsewhere = False
        for me, tally in self.input.tally.iteritems():
            if me != self.main_me - 1:
                if tally['pvw']:
                    isPreviewElsewhere = True
                if tally['pgm']:
                    isLiveElsewhere = True
        self.previewDot.setVisible(isPreviewElsewhere)
        self.liveDot.setVisible(isLiveElsewhere)

        self.style().unpolish(self)
        self.style().polish(self)


class FlashingInputButton(InputButton):
    def __init__(self, myInput, main_me=1, parent=None):
        super(FlashingInputButton, self).__init__(myInput, main_me, parent)
        self.flashing = False
        self._flashState = 0
        self._timer = QTimer()
        self._timer.timeout.connect(self._flash)
        self._timer.start(500)

    def setFlashing(self, flashing):
        self.flashing = flashing

    def _flash(self):
        if self.flashing and self._flashState == 0:
            self._flashState = 1
            self.setProperty("flashing", True)
        elif self.property("flashing"):
            self._flashState = 0
            self.setProperty("flashing", False)
        self.style().unpolish(self)
        self.style().polish(self)


class IDedButton(ExpandingButton):

    def __init__(self, ID, parent=None):
        super(IDedButton, self).__init__(parent)
        self.ID = ID


class OutputButton(LongPressButtonMixin, ExpandingButton):

    def __init__(self, myOutput, main_me=VideoSource.ME_1_PROGRAM, parent=None):
        super(OutputButton, self).__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)  # Sneakily hide our actual text
        self._main_me = main_me

        self.textDisplay = QLabel()
        self.stateDisplay = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.textDisplay)
        layout.addWidget(self.stateDisplay)

        self.textDisplay.setObjectName("textDisplay")

        self.stateDisplay.setObjectName("stateDisplay")
        self.stateDisplay.setAlignment(Qt.AlignHCenter)

        self.setLayout(layout)

        self.output = myOutput
        self.output.changedState.connect(self._update_from_output)
        self._update_from_output()

    def _update_from_output(self):
        self.setText(self.output.label)

        if self.output.source and hasattr(self.output.source, "label"):
            self.stateDisplay.setText(self.output.source.label)
            # Highlight if this output is not showing the M/E we're controlling
            self.stateDisplay.setProperty("highlight", (self.output.source.source != self._main_me))
        else:
            self.stateDisplay.setText("-")
            self.stateDisplay.setProperty("highlight", False)
        self.stateDisplay.style().unpolish(self.stateDisplay)
        self.stateDisplay.style().polish(self.stateDisplay)

    def setText(self, text):
        self.textDisplay.setText(text)


class OptionButton(ExpandingButton):

    def __init__(self, parent=None):
        super(OptionButton, self).__init__(parent)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)


class SvgButton(ExpandingButton):
    def __init__(self, svgImage, width, height, parent=None):
        super(SvgButton, self).__init__(parent)
        icon = QIcon(pixmap_from_svg(svgImage, width, height))
        self.setIcon(icon)
        self.setIconSize(QSize(width, height))


def pixmap_from_svg(svgImage, width, height):
    svg_renderer = QSvgRenderer(svgImage)
    image = QImage(width, height, QImage.Format_ARGB32)
    # Set the ARGB to 0 to prevent rendering artifacts
    image.fill(0x00000000)
    svg_renderer.render(QPainter(image))
    return QPixmap.fromImage(image)
