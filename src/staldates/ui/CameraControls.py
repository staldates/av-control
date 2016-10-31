from PySide.QtGui import QButtonGroup, QGridLayout, QLabel, QWidget, QIcon, QSizePolicy
from PySide.QtCore import QSize, Qt
from staldates.ui.widgets.Buttons import ExpandingButton, OptionButton
from staldates.ui.widgets.Screens import ScreenWithBackButton
from staldates.ui.widgets.Dialogs import handlePyroErrors


class CameraButton(ExpandingButton):

    def __init__(self):
        super(CameraButton, self).__init__()
        self.setIconSize(QSize(64, 64))


class PlusMinusButtons(QWidget):

    def __init__(self, caption):
        super(PlusMinusButtons, self).__init__()
        self.upButton = CameraButton()
        self.upButton.setIcon(QIcon(":icons/list-add"))

        self.downButton = CameraButton()
        self.downButton.setIcon(QIcon(":icons/list-remove"))

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


def _safelyConnect(signal, slot):
    signal.connect(handlePyroErrors(slot))


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
        _safelyConnect(self.btnUp.pressed, self.camera.moveUp)
        _safelyConnect(self.btnUp.released, self.camera.stop)
        _safelyConnect(self.btnUp.clicked, self.deselectPreset)
        self.btnUp.setIcon(QIcon(":icons/go-up"))

        self.btnLeft = CameraButton()
        layout.addWidget(self.btnLeft, 1, 0, 2, 1)
        _safelyConnect(self.btnLeft.pressed, self.camera.moveLeft)
        _safelyConnect(self.btnLeft.released, self.camera.stop)
        _safelyConnect(self.btnLeft.clicked, self.deselectPreset)
        self.btnLeft.setIcon(QIcon(":icons/go-previous"))

        self.btnDown = CameraButton()
        layout.addWidget(self.btnDown, 2, 1, 2, 1)
        _safelyConnect(self.btnDown.pressed, self.camera.moveDown)
        _safelyConnect(self.btnDown.released, self.camera.stop)
        _safelyConnect(self.btnDown.clicked, self.deselectPreset)
        self.btnDown.setIcon(QIcon(":icons/go-down"))

        self.btnRight = CameraButton()
        layout.addWidget(self.btnRight, 1, 2, 2, 1)
        _safelyConnect(self.btnRight.pressed, self.camera.moveRight)
        _safelyConnect(self.btnRight.released, self.camera.stop)
        _safelyConnect(self.btnRight.clicked, self.deselectPreset)
        self.btnRight.setIcon(QIcon(":icons/go-next"))

        zoomInOut = PlusMinusButtons("Zoom")
        _safelyConnect(zoomInOut.upButton.pressed, self.camera.zoomIn)
        _safelyConnect(zoomInOut.upButton.released, self.camera.zoomStop)
        _safelyConnect(zoomInOut.upButton.clicked, self.deselectPreset)
        _safelyConnect(zoomInOut.downButton.pressed, self.camera.zoomOut)
        _safelyConnect(zoomInOut.downButton.released, self.camera.zoomStop)
        _safelyConnect(zoomInOut.downButton.clicked, self.deselectPreset)

        layout.addWidget(zoomInOut, 0, 3, 4, 1)

        focus = PlusMinusAutoButtons("Focus")
        _safelyConnect(focus.upButton.pressed, self.camera.focusFar)
        _safelyConnect(focus.upButton.released, self.camera.focusStop)
        _safelyConnect(focus.upButton.clicked, self.deselectPreset)
        _safelyConnect(focus.downButton.pressed, self.camera.focusNear)
        _safelyConnect(focus.downButton.released, self.camera.focusStop)
        _safelyConnect(focus.downButton.clicked, self.deselectPreset)

        def autoFocusAndDeselect():
            self.camera.focusAuto()
            self.deselectPreset()
        _safelyConnect(focus.autoButton.clicked, autoFocusAndDeselect)
        layout.addWidget(focus, 0, 4, 4, 1)

        brightness = PlusMinusButtons("EV Comp")
        _safelyConnect(brightness.upButton.clicked, self.camera.backlightCompOn)
        _safelyConnect(brightness.downButton.clicked, self.camera.backlightCompOff)
        layout.addWidget(brightness, 0, 5, 4, 1)

        presets = QGridLayout()
        presets.setRowStretch(0, 2)
        presets.setRowStretch(1, 1)

        self.presetGroup = QButtonGroup()

        for i in range(0, 6):
            btnPresetRecall = CameraButton()
            presets.addWidget(btnPresetRecall, 0, i, 1, 1)
            btnPresetRecall.setText(str(i + 1))
            _safelyConnect(btnPresetRecall.clicked, lambda i=i: self.recallPreset(i))
            btnPresetRecall.setCheckable(True)
            self.presetGroup.addButton(btnPresetRecall, i)

            btnPresetSet = CameraButton()
            presets.addWidget(btnPresetSet, 1, i, 1, 1)
            btnPresetSet.setText("Set")
            _safelyConnect(btnPresetSet.clicked, lambda i=i: self.storePreset(i))

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

    @handlePyroErrors
    def storePreset(self, index):
        print "Storing preset " + str(index)
        result = self.camera.storePreset(index)
        self.presetGroup.buttons()[index].setChecked(True)
        return result

    @handlePyroErrors
    def recallPreset(self, index):
        print "Recalling preset " + str(index)
        return self.camera.recallPreset(index)

    def deselectPreset(self):
        # Yuck.
        self.presetGroup.setExclusive(False)
        while (self.presetGroup.checkedId() >= 0):
            self.presetGroup.checkedButton().setChecked(False)
        self.presetGroup.setExclusive(True)


class AdvancedCameraControl(ScreenWithBackButton):

    def __init__(self, title, camera, mainScreen):
        self.camera = camera
        super(AdvancedCameraControl, self).__init__(title, mainScreen)

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
        _safelyConnect(btnAuto.clicked, self.camera.whiteBalanceAuto)
        whiteBalanceGrid.addWidget(btnAuto, 1, 0)

        btnIndoor = OptionButton()
        btnIndoor.setText("Indoor")
        _safelyConnect(btnIndoor.clicked, self.camera.whiteBalanceIndoor)
        whiteBalanceGrid.addWidget(btnIndoor, 2, 0)

        btnOutdoor = OptionButton()
        btnOutdoor.setText("Outdoor")
        _safelyConnect(btnOutdoor.clicked, self.camera.whiteBalanceOutdoor)
        whiteBalanceGrid.addWidget(btnOutdoor, 3, 0)

        btnOnePush = OptionButton()
        btnOnePush.setText("One Push")
        _safelyConnect(btnOnePush.clicked, self.camera.whiteBalanceOnePush)
        whiteBalanceGrid.addWidget(btnOnePush, 4, 0)

        btnOnePushTrigger = ExpandingButton()
        btnOnePushTrigger.setText("Set")
        _safelyConnect(btnOnePushTrigger.clicked, self.camera.whiteBalanceOnePushTrigger)
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

    @handlePyroErrors
    def displayPosition(self):
        pos = self.camera.getPosition()

        self.posDisplay.itemAtPosition(0, 1).widget().setText(str(pos.pan))
        self.posDisplay.itemAtPosition(1, 1).widget().setText(str(pos.tilt))
        self.posDisplay.itemAtPosition(2, 1).widget().setText(str(pos.zoom))
