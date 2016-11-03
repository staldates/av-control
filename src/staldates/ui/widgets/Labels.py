from PySide.QtGui import QLabel
from PySide.QtCore import Qt


class TitleLabel(QLabel):
    def __init__(self, title, parent=None):
        super(TitleLabel, self).__init__(parent)
        self.setText(title)
        self.setAlignment(Qt.AlignCenter)
