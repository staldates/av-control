from PySide.QtGui import QWidget, QIcon, QLabel, QHBoxLayout
from PySide.QtCore import Signal, Qt
from staldates.ui.widgets.Buttons import ExpandingButton


class TouchSpinner(QWidget):
    valueChanged = Signal(int)

    def __init__(self, parent=None):
        super(TouchSpinner, self).__init__(parent)
        self._value = 50
        self._max = 100
        self._min = 0

        layout = QHBoxLayout()

        btnMinus = ExpandingButton()
        btnMinus.setIcon(QIcon(":icons/list-remove"))
        btnMinus.clicked.connect(lambda: self.setValue(self._value - 1))
        layout.addWidget(btnMinus, 1)

        self.lblValue = QLabel(self.formattedValue(self._value))
        self.lblValue.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.lblValue, 1)

        btnPlus = ExpandingButton()
        btnPlus.setIcon(QIcon(":icons/list-add"))
        btnPlus.clicked.connect(lambda: self.setValue(self._value + 1))
        layout.addWidget(btnPlus, 1)

        self.setLayout(layout)

    def setValue(self, value):
        if value > self._max:
            newValue = self._max
        elif value < self._min:
            newValue = self._min
        else:
            newValue = value
        if value != self._value:
            self._value = newValue
            self.valueChanged.emit(newValue)
            self.lblValue.setText(self.formattedValue(newValue))

    def setMaximum(self, maxi):
        self._max = maxi

    def setMinimum(self, mini):
        self._min = mini

    def value(self):
        return self._value

    def formattedValue(self, value):
        return "{}".format(value)


class FrameRateTouchSpinner(TouchSpinner):

    def __init__(self, fps=25, parent=None):
        self._fps = fps
        super(FrameRateTouchSpinner, self).__init__(parent)

    def formattedValue(self, value):
        secs = value / self._fps
        frames = value % self._fps
        return "{:0d}:{:02d}".format(secs, frames)
