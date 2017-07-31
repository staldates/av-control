from PySide.QtGui import QLabel, QToolButton, QSizePolicy, QVBoxLayout, QImage,\
    QPainter, QPixmap, QIcon
from PySide.QtCore import Qt, QSize, Signal, QEvent
from PySide.QtSvg import QSvgRenderer


class ExpandingButton(QToolButton):

    longpress = Signal()

    def __init__(self, parent=None):
        super(ExpandingButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setIconSize(QSize(48, 48))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.grabGesture(Qt.TapAndHoldGesture)

    def event(self, evt):
        if evt.type() == QEvent.Gesture:
            gesture = evt.gesture(Qt.TapAndHoldGesture)
            if gesture:
                if gesture.state() == Qt.GestureState.GestureFinished:
                    self.longpress.emit()
                    return True
        return super(ExpandingButton, self).event(evt)


class InputButton(ExpandingButton):

    def __init__(self, myInput, parent=None):
        super(InputButton, self).__init__(parent)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
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
        self.setText(self.input.label)
        if self.input.icon:
            self.setIcon(self.input.icon)
        else:
            self.setIcon(QIcon())

        self.setProperty("isLive", self.input.isLive)
        self.setProperty("isPreview", self.input.isPreview)

        self.style().unpolish(self)
        self.style().polish(self)


class IDedButton(ExpandingButton):

    def __init__(self, ID, parent=None):
        super(IDedButton, self).__init__(parent)
        self.ID = ID


class OutputButton(ExpandingButton):

    longpress = Signal()

    def __init__(self, myOutput, parent=None):
        super(OutputButton, self).__init__(parent)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.grabGesture(Qt.TapAndHoldGesture)

        self.stateDisplay = QLabel()
        layout = QVBoxLayout()
        layout.addWidget(self.stateDisplay)
        layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.setLayout(layout)

        self.output = myOutput
        self.output.changedState.connect(self._update_from_output)
        self._update_from_output()

    def _update_from_output(self):
        self.setText(self.output.label)

        if self.output.source and hasattr(self.output.source, "label"):
            self.stateDisplay.setText(self.output.source.label)
        else:
            self.stateDisplay.setText("-")


class OptionButton(ExpandingButton):

    def __init__(self, parent=None):
        super(OptionButton, self).__init__(parent)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)


class CameraSelectionButton(InputButton, IDedButton):
    pass


class SvgButton(ExpandingButton):
    def __init__(self, svgImage, width, height, parent=None):
        super(SvgButton, self).__init__(parent)
        svg_renderer = QSvgRenderer(svgImage)
        image = QImage(width, height, QImage.Format_ARGB32)
        # Set the ARGB to 0 to prevent rendering artifacts
        image.fill(0x00000000)
        svg_renderer.render(QPainter(image))
        pixmap = QPixmap.fromImage(image)
        icon = QIcon(pixmap)
        self.setIcon(icon)
        self.setIconSize(QSize(width, height))
