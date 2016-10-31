from PySide.QtGui import QWidget, QVBoxLayout
from staldates.ui.widgets.Dialogs import handlePyroErrors
from staldates.ui.widgets.ScanConverterControls import EclipseWidget


class EclipseControls(QWidget):

    def __init__(self, device):
        super(EclipseControls, self).__init__()
        self.device = device

        if device:
            layout = QVBoxLayout(self)
            eclipse = EclipseWidget()
            layout.addWidget(eclipse)

            eclipse.btnOverscan.toggled.connect(self.toggleOverscan)
            eclipse.btnFreeze.toggled.connect(self.toggleFreeze)
            eclipse.btnFade.toggled.connect(self.toggleFade)
            eclipse.btnOverlay.toggled.connect(self.toggleOverlay)

    @handlePyroErrors
    def toggleOverscan(self, overscan):
        if overscan:
            self.device.overscanOn()
        else:
            self.device.overscanOff()

    @handlePyroErrors
    def toggleFreeze(self, freeze):
        if freeze:
            self.device.freeze()
        else:
            self.device.unfreeze()

    @handlePyroErrors
    def toggleOverlay(self, overlay):
        if overlay:
            self.device.overlayOn()
        else:
            self.device.overlayOff()

    @handlePyroErrors
    def toggleFade(self, fade):
        if fade:
            self.device.fadeOut()
        else:
            self.device.fadeIn()
