from PySide.QtGui import QWidget, QVBoxLayout
from staldates.ui.widgets.ScanConverterControls import EclipseWidget
from Pyro4.errors import ProtocolError, NamingError
from avx.StringConstants import StringConstants


class EclipseControls(QWidget):

    def __init__(self, controller, deviceID):
        super(EclipseControls, self).__init__()
        self.deviceID = deviceID

        if controller.hasDevice(deviceID):
            self.device = controller[deviceID]
            layout = QVBoxLayout(self)
            eclipse = EclipseWidget()
            layout.addWidget(eclipse)

            eclipse.btnOverscan.toggled.connect(self.toggleOverscan)
            eclipse.btnFreeze.toggled.connect(self.toggleFreeze)
            eclipse.btnFade.toggled.connect(self.toggleFade)
            eclipse.btnOverlay.toggled.connect(self.toggleOverlay)

    def toggleOverscan(self):
        try:
            if self.sender().isChecked():
                self.device.overscanOn()
            else:
                self.device.overscanOff()
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleFreeze(self):
        try:
            if self.sender().isChecked():
                self.device.freeze()
            else:
                self.device.unfreeze()
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleOverlay(self):
        try:
            if self.sender().isChecked():
                self.device.overlayOn()
            else:
                self.device.overlayOff()
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)

    def toggleFade(self):
        try:
            if self.sender().isChecked():
                self.device.fadeOut()
            else:
                self.device.fadeIn()
        except NamingError:
            self.errorBox(StringConstants.nameErrorText)
        except ProtocolError:
            self.errorBox(StringConstants.protocolErrorText)
