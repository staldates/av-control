from PySide.QtGui import QWidget, QStackedLayout, QGridLayout, QLabel,\
    QVBoxLayout, QFrame
from staldates.ui.widgets.Labels import TitleLabel
from staldates.ui.widgets.Buttons import ExpandingButton
from PySide.QtCore import QTimer
from staldates.admin import restart_avx_controller, restart_server


TIMEOUT = 1000 * 60 * 5  # five minutes until PIN entry expires


class PinProtectedScreen(QWidget):
    def __init__(self, pin=None, parent=None):
        super(PinProtectedScreen, self).__init__(parent)
        self.pin = pin
        self.authenticatedAt = None

        self.stack = QStackedLayout()
        self.pinIdx = self.stack.addWidget(self.pinScreen())
        self.innerIdx = self.stack.addWidget(self.innerScreen())

        self.setLayout(self.stack)
        self.authenticate(None)

    def authenticate(self, pin):
        if pin == self.pin:
            self.stack.setCurrentIndex(self.innerIdx)
            QTimer.singleShot(TIMEOUT, self.reset)
        else:
            self.stack.setCurrentIndex(self.pinIdx)

    def reset(self):
        self.pinEntry.setText("")
        self.authenticate(None)

    def pinScreen(self):
        layout = QGridLayout()

        layout.addWidget(TitleLabel("Please enter PIN to access admin functions"), 0, 0, 1, 5)

        pinEntry = TitleLabel("")
        self.pinEntry = pinEntry
        layout.addWidget(pinEntry, 1, 1, 1, 3)

        def numberButton(num):
            btn = ExpandingButton(text=num)

            def btnClick():
                pinEntry.setText(pinEntry.text() + num)
                self.authenticate(pinEntry.text())
            btn.clicked.connect(btnClick)
            return btn

        layout.addWidget(numberButton("7"), 2, 1)
        layout.addWidget(numberButton("8"), 2, 2)
        layout.addWidget(numberButton("9"), 2, 3)
        layout.addWidget(numberButton("4"), 3, 1)
        layout.addWidget(numberButton("5"), 3, 2)
        layout.addWidget(numberButton("6"), 3, 3)
        layout.addWidget(numberButton("1"), 4, 1)
        layout.addWidget(numberButton("2"), 4, 2)
        layout.addWidget(numberButton("3"), 4, 3)

        delBtn = ExpandingButton(text="<")
        delBtn.clicked.connect(lambda: pinEntry.setText(pinEntry.text()[0:-1]))
        layout.addWidget(delBtn, 5, 1)

        layout.addWidget(numberButton("0"), 5, 2)

        clrBtn = ExpandingButton(text="Clear")
        clrBtn.clicked.connect(lambda: pinEntry.setText(""))
        layout.addWidget(clrBtn, 5, 3)

        for i in range(0, 5):
            layout.setColumnStretch(i, 1)

        widget = QWidget()
        widget.setLayout(layout)
        return widget

    def innerScreen(self):
        return QLabel("Authenticated")


class AdminScreen(PinProtectedScreen):
    def __init__(self, pin=None, parent=None):
        PinProtectedScreen.__init__(self, pin=pin, parent=parent)

    def innerScreen(self):
        layout = QVBoxLayout()

        layout.addWidget(TitleLabel("Administrative functions"))

        btnRestartAVX = ExpandingButton(text="Restart AVX controller process")
        btnRestartAVX.clicked.connect(restart_avx_controller)
        layout.addWidget(btnRestartAVX)

        btnRestartMachine = ExpandingButton(text="Restart control server")
        btnRestartMachine.clicked.connect(restart_server)
        layout.addWidget(btnRestartMachine)

        widget = QFrame()
        widget.setLayout(layout)
        return widget
