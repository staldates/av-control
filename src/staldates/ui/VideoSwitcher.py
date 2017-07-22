from PySide.QtGui import QWidget


class VideoSwitcher(QWidget):

    def __init__(self, atem, mainWindow, switcherState):
        super(VideoSwitcher, self).__init__()
        self.mainWindow = mainWindow
        self.atem = atem
        self.switcherState = switcherState
        self.setupUi()

    def setupUi(self):
        pass
