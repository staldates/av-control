from PySide.QtGui import QLabel, QToolButton, QSizePolicy, QVBoxLayout, QImage,\
    QPainter, QPixmap, QIcon
from PySide.QtCore import Qt, QSize, Signal, QEvent
from PySide.QtSvg import QSvgRenderer


class ExpandingButton(QToolButton):

    def __init__(self, parent=None):
        super(ExpandingButton, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setIconSize(QSize(48, 48))
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)


class InputButton(ExpandingButton):

    longpress = Signal()

    def __init__(self, parent=None):
        super(InputButton, self).__init__(parent)
        self.setCheckable(True)
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.input = None
        self.grabGesture(Qt.TapAndHoldGesture)

    def setInput(self, myInput):
        self.input = myInput

    def event(self, evt):
        if evt.type() == QEvent.Gesture:
            gesture = evt.gesture(Qt.TapAndHoldGesture)
            if gesture:
                if gesture.state() == Qt.GestureState.GestureFinished:
                    self.longpress.emit()
                    return True
        return super(InputButton, self).event(evt)


class IDedButton(ExpandingButton):

    def __init__(self, ID, parent=None):
        super(IDedButton, self).__init__(parent)
        self.ID = ID


class OutputButton(IDedButton):

    def __init__(self, ID, parent=None):
        super(OutputButton, self).__init__(ID, parent)
        self.inputDisplay = QLabel()
        self.inputDisplay.setText("-")
        layout = QVBoxLayout()
        layout.addWidget(self.inputDisplay)
        layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
        self.setLayout(layout)

    def setInputText(self, text):
        self.inputDisplay.setText(text)


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
