from PySide.QtGui import QButtonGroup, QGridLayout, QLabel, QWidget, QIcon, QMessageBox, QSizePolicy
from PySide.QtCore import QSize, Qt
from staldates.ui.widgets.Buttons import ExpandingButton, OptionButton
from Pyro4.errors import NamingError, ProtocolError
from avx.StringConstants import StringConstants
from staldates.ui.widgets.Screens import ScreenWithBackButton


class CameraButton(ExpandingButton):

    def __init__(self):
        super(CameraButton, self).__init__()
        self.setIconSize(QSize(64, 64))


class PlusMinusButtons(QWidget):

    def __init__(self, caption):
        super(PlusMinusButtons, self).__init__()
        self.upButton = CameraButton()
        self.upButton.setIcon(QIcon("icons/list-add.svg"))

        self.downButton = CameraButton()
        self.downButton.setIcon(QIcon("icons/list-remove.svg"))

        self.caption = QLabel("<b>" + caption + "</b>")
        self.caption.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        self.initLayout()

    def initLayout(self):

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.upButton, 0, 0)
        layout.addWidget(self.caption, 1, 0)
        layout.addWidget(self.downButton, 2, 0)

        layout.setRowStretch(0, 2)
        layout.setRowStretch(1, 2)
        layout.setRowStretch(2, 2)


class PlusMinusAutoButtons(PlusMinusButtons):

    def __init__(self, caption):
        self.autoButton = CameraButton()
        self.autoButton.setText("Auto")
        super(PlusMinusAutoButtons, self).__init__(caption)

    def initLayout(self):
        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.upButton, 0, 0)
        layout.addWidget(self.caption, 1, 0)
        layout.addWidget(self.autoButton, 2, 0)
        layout.addWidget(self.downButton, 3, 0)

        layout.setRowStretch(0, 2)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 2)


class CameraControl(QWidget):
    '''
    GUI to control a camera.
    '''

    def __init__(self, camera):
        super(CameraControl, self).__init__()
        self.camera = camera
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.btnUp = CameraButton()
        layout.addWidget(self.btnUp, 0, 1, 2, 1)
        self.btnUp.pressed.connect(self.camera.moveUp)
        self.btnUp.released.connect(self.camera.stop)
        self.btnUp.clicked.connect(self.deselectPreset)
        self.btnUp.setIcon(QIcon("icons/go-up.svg"))

        self.btnLeft = CameraButton()
        layout.addWidget(self.btnLeft, 1, 0, 2, 1)
        self.btnLeft.pressed.connect(self.camera.moveLeft)
        self.btnLeft.released.connect(self.camera.stop)
        self.btnLeft.clicked.connect(self.deselectPreset)
        self.btnLeft.setIcon(QIcon("icons/go-previous.svg"))

        self.btnDown = CameraButton()
        layout.addWidget(self.btnDown, 2, 1, 2, 1)
        self.btnDown.pressed.connect(self.camera.moveDown)
        self.btnDown.released.connect(self.camera.stop)
        self.btnDown.clicked.connect(self.deselectPreset)
        self.btnDown.setIcon(QIcon("icons/go-down.svg"))

        self.btnRight = CameraButton()
        layout.addWidget(self.btnRight, 1, 2, 2, 1)
        self.btnRight.pressed.connect(self.camera.moveRight)
        self.btnRight.released.connect(self.camera.stop)
        self.btnRight.clicked.connect(self.deselectPreset)
        self.btnRight.setIcon(QIcon("icons/go-next.svg"))

        zoomInOut = PlusMinusButtons("Zoom")
        zoomInOut.upButton.pressed.connect(self.camera.zoomIn)
        zoomInOut.upButton.released.connect(self.camera.stopZoom)
        zoomInOut.upButton.clicked.connect(self.deselectPreset)
        zoomInOut.downButton.pressed.connect(self.camera.zoomOut)
        zoomInOut.downButton.released.connect(self.camera.stopZoom)
        zoomInOut.downButton.clicked.connect(self.deselectPreset)

        layout.addWidget(zoomInOut, 0, 3, 4, 1)

        focus = PlusMinusAutoButtons("Focus")
        focus.upButton.pressed.connect(self.camera.focusFar)
        focus.upButton.released.connect(self.camera.focusStop)
        focus.upButton.clicked.connect(self.deselectPreset)
        focus.downButton.pressed.connect(self.camera.focusNear)
        focus.downButton.released.connect(self.camera.focusStop)
        focus.downButton.clicked.connect(self.deselectPreset)
        def autoFocusAndDeselect():
            self.camera.focusAuto()
            self.deselectPreset()
        focus.autoButton.clicked.connect(autoFocusAndDeselect)
        layout.addWidget(focus, 0, 4, 4, 1)

        brightness = PlusMinusButtons("Backlight Comp")
        brightness.upButton.clicked.connect(self.camera.backlightCompOn)
        brightness.downButton.clicked.connect(self.camera.backlightCompOff)
        layout.addWidget(brightness, 0, 5, 4, 1)

        presets = QGridLayout()
        presets.setRowStretch(0, 2)
        presets.setRowStretch(1, 1)

        self.presetGroup = QButtonGroup()

        for i in range(0, 6):
            btnPresetRecall = CameraButton()
            presets.addWidget(btnPresetRecall, 0, i, 1, 1)
            btnPresetRecall.setText(str(i + 1))
            btnPresetRecall.clicked.connect(lambda: self.recallPreset(i))
            btnPresetRecall.setCheckable(True)
            self.presetGroup.addButton(btnPresetRecall, i)

            btnPresetSet = CameraButton()
            presets.addWidget(btnPresetSet, 1, i, 1, 1)
            btnPresetSet.setText("Set")
            btnPresetSet.clicked.connect(lambda: self.storePreset(i))

        layout.addLayout(presets, 4, 0, 3, 6)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.btnLeft.pressed.emit()
        elif e.key() == Qt.Key_Right:
            self.btnRight.pressed.emit()
        elif e.key() == Qt.Key_Up:
            self.btnUp.pressed.emit()
        elif e.key() == Qt.Key_Down:
            self.btnDown.pressed.emit()

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.btnLeft.released.emit()
        elif e.key() == Qt.Key_Right:
            self.btnRight.released.emit()
        elif e.key() == Qt.Key_Up:
            self.btnUp.released.emit()
        elif e.key() == Qt.Key_Down:
            self.btnDown.released.emit()

    def storePreset(self, index):
        try:
            result = self.camera.storePreset(index)
            self.presetGroup.buttons()[index].setChecked(True)
            return result
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def recallPreset(self, index):
        try:
            return self.camera.recallPreset(index)
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def deselectPreset(self):
        # Yuck.
        self.presetGroup.setExclusive(False)
        while (self.presetGroup.checkedId() >= 0):
            self.presetGroup.checkedButton().setChecked(False)
        self.presetGroup.setExclusive(True)

    def errorBox(self, text):
        msgBox = QMessageBox()
        msgBox.setText(text)
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.exec_()


class AdvancedCameraControl(ScreenWithBackButton):

    def __init__(self, camera, mainScreen):
        self.camera = camera
        super(AdvancedCameraControl, self).__init__(camera.deviceID, mainScreen)

    def makeContent(self):
        layout = QGridLayout()

        self.posDisplay = QGridLayout()

        self.posDisplay.addWidget(QLabel("Pan:"), 0, 0)
        self.posDisplay.addWidget(QLabel("Tilt:"), 1, 0)
        self.posDisplay.addWidget(QLabel("Zoom:"), 2, 0)

        self.posDisplay.addWidget(QLabel(), 0, 1)
        self.posDisplay.addWidget(QLabel(), 1, 1)
        self.posDisplay.addWidget(QLabel(), 2, 1)

        layout.addLayout(self.posDisplay, 1, 0)

        btnGetPos = ExpandingButton()
        btnGetPos.setText("Get Position")
        btnGetPos.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(btnGetPos, 2, 0)
        btnGetPos.clicked.connect(self.displayPosition)

        whiteBalanceGrid = QGridLayout()
        wbTitle = QLabel("White Balance")
        wbTitle.setAlignment(Qt.AlignCenter)
        whiteBalanceGrid.addWidget(wbTitle, 0, 0, 1, 2)

        btnAuto = OptionButton()
        btnAuto.setText("Auto")
        btnAuto.clicked.connect(self.camera.whiteBalanceAuto)
        whiteBalanceGrid.addWidget(btnAuto, 1, 0)

        btnIndoor = OptionButton()
        btnIndoor.setText("Indoor")
        btnIndoor.clicked.connect(self.camera.whiteBalanceIndoor)
        whiteBalanceGrid.addWidget(btnIndoor, 2, 0)

        btnOutdoor = OptionButton()
        btnOutdoor.setText("Outdoor")
        btnOutdoor.clicked.connect(self.camera.whiteBalanceOutdoor)
        whiteBalanceGrid.addWidget(btnOutdoor, 3, 0)

        btnOnePush = OptionButton()
        btnOnePush.setText("One Push")
        btnOnePush.clicked.connect(self.camera.whiteBalanceOnePush)
        whiteBalanceGrid.addWidget(btnOnePush, 4, 0)

        btnOnePushTrigger = ExpandingButton()
        btnOnePushTrigger.setText("Set")
        btnOnePushTrigger.clicked.connect(self.camera.whiteBalanceOnePushTrigger)
        btnOnePushTrigger.setEnabled(False)
        whiteBalanceGrid.addWidget(btnOnePushTrigger, 4, 1)

        self.wbOpts = QButtonGroup()
        self.wbOpts.addButton(btnAuto, 1)
        self.wbOpts.addButton(btnIndoor, 2)
        self.wbOpts.addButton(btnOutdoor, 3)
        self.wbOpts.addButton(btnOnePush, 4)
        self.wbOpts.buttonClicked.connect(lambda: btnOnePushTrigger.setEnabled(self.wbOpts.checkedId() == 4))

        layout.addLayout(whiteBalanceGrid, 1, 1, 2, 1)

        return layout

    def displayPosition(self):
        pos = self.camera.getPosition()

        self.posDisplay.itemAtPosition(0, 1).widget().setText(str(pos.pan))
        self.posDisplay.itemAtPosition(1, 1).widget().setText(str(pos.tilt))
        self.posDisplay.itemAtPosition(2, 1).widget().setText(str(pos.zoom))
