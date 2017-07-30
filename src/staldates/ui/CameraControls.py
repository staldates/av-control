from avx.devices.serial.VISCACamera import Aperture, Shutter, Gain
from enum import Enum
from PySide.QtGui import QButtonGroup, QGridLayout, QLabel, QWidget, QIcon, QHBoxLayout, QComboBox,\
    QSizePolicy
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

        for i in range(1, 7):
            btnPresetRecall = CameraButton()
            presets.addWidget(btnPresetRecall, 0, i, 1, 1)
            btnPresetRecall.setText(str(i))
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
        self.presetGroup.buttons()[index - 1].setChecked(True)
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


class ExposureControl(QWidget):

    class Mode(Enum):
        AUTO = 1
        TV = 2
        AV = 4
        MANUAL = 8

        def __or__(self, other):
            return self.value | other.value

    def __init__(self, camera):
        super(ExposureControl, self).__init__()
        self.camera = camera
        self.initUI()

    def initUI(self):
        layout = QGridLayout()

        title = QLabel("Exposure")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title, 0, 0, 1, 4)

        btnAuto = OptionButton()
        btnAuto.setText("Full Auto")
        _safelyConnect(btnAuto.clicked, self.camera.setAutoExposure)
        btnAuto.setChecked(True)

        layout.addWidget(btnAuto, 1, 0)

        btnTV = OptionButton()
        btnTV.setText("Tv")
        _safelyConnect(btnTV.clicked, self.camera.setShutterPriority)

        layout.addWidget(btnTV, 1, 1)

        btnAV = OptionButton()
        btnAV.setText("Av")
        _safelyConnect(btnAV.clicked, self.camera.setAperturePriority)

        layout.addWidget(btnAV, 1, 2)

        btnManual = OptionButton()
        btnManual.setText("M")
        _safelyConnect(btnManual.clicked, self.camera.setManualExposure)

        layout.addWidget(btnManual, 1, 3)

        layout.addWidget(QLabel("Aperture"), 2, 0)

        self.aperture = QComboBox(self)
        for a in list(Aperture):
            self.aperture.addItem(a.label, userData=a)
        self.aperture.currentIndexChanged.connect(self.setAperture)
        self.aperture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.aperture.setEnabled(False)

        layout.addWidget(self.aperture, 2, 1, 1, 3)

        layout.addWidget(QLabel("Shutter"), 3, 0)

        self.shutter = QComboBox(self)
        for s in list(Shutter):
            self.shutter.addItem(s.label, userData=s)
        self.shutter.currentIndexChanged.connect(self.setShutter)
        self.shutter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.shutter.setEnabled(False)

        layout.addWidget(self.shutter, 3, 1, 1, 3)

        layout.addWidget(QLabel("Gain"), 4, 0)

        self.gain = QComboBox(self)
        for g in list(Gain):
            self.gain.addItem(g.label, userData=g)
        self.gain.currentIndexChanged.connect(self.setGain)
        self.gain.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.gain.setEnabled(False)

        layout.addWidget(self.gain, 4, 1, 1, 3)

        self.exposureButtons = QButtonGroup()
        self.exposureButtons.addButton(btnAuto, self.Mode.AUTO.value)
        self.exposureButtons.addButton(btnTV, self.Mode.TV.value)
        self.exposureButtons.addButton(btnAV, self.Mode.AV.value)
        self.exposureButtons.addButton(btnManual, self.Mode.MANUAL.value)

        self.exposureButtons.buttonClicked.connect(self.onExposureMethodSelected)

        layout.setRowStretch(0, 0)
        layout.setRowStretch(1, 1)
        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 1)
        layout.setRowStretch(4, 1)

        self.setLayout(layout)

    def onExposureMethodSelected(self):
        checked = self.exposureButtons.checkedId()
        self.aperture.setEnabled(checked & (self.Mode.MANUAL | self.Mode.AV))
        self.shutter.setEnabled(checked & (self.Mode.MANUAL | self.Mode.TV))
        self.gain.setEnabled(checked & self.Mode.MANUAL.value)

    @handlePyroErrors
    def setAperture(self, idx):
        ap = self.aperture.itemData(idx)
        self.camera.setAperture(ap)

    @handlePyroErrors
    def setShutter(self, idx):
        sh = self.shutter.itemData(idx)
        self.camera.setShutter(sh)

    @handlePyroErrors
    def setGain(self, idx):
        g = self.gain.itemData(idx)
        self.camera.setGain(g)


class AdvancedCameraControl(ScreenWithBackButton):

    def __init__(self, title, camera, mainScreen):
        self.camera = camera
        super(AdvancedCameraControl, self).__init__(title, mainScreen)

    def makeContent(self):
        layout = QHBoxLayout()

        self.exposureControls = ExposureControl(self.camera)
        layout.addWidget(self.exposureControls)

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

        layout.addLayout(whiteBalanceGrid)

        return layout
