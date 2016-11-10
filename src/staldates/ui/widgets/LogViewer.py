from PySide.QtGui import QVBoxLayout, QTableWidget, QTableWidgetItem
from staldates.ui.widgets.Dialogs import handlePyroErrors
from staldates.ui.widgets.Screens import ScreenWithBackButton


class LogViewerScreen(ScreenWithBackButton):

    def __init__(self, controller, mainWindow):
        self.controller = controller
        ScreenWithBackButton.__init__(self, "System Log", mainWindow)

    def makeContent(self):

        layout = QVBoxLayout()

        self.table = LogViewer()
        layout.addWidget(self.table)

        return layout

    @handlePyroErrors
    def displayLog(self):
        entries = self.controller.getLog()
        self.table.displayLog(entries)


class LogViewer(QTableWidget):
    def __init__(self):
        super(LogViewer, self).__init__()
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Time", "Severity", "Message"])
        self.resizeColumnsToContents()

    def displayLog(self, entries):
        self.clearContents()
        self.setRowCount(len(entries))

        for i, entry in enumerate(entries):
            self.setItem(i, 0, QTableWidgetItem(entry.asctime))
            self.setItem(i, 1, QTableWidgetItem(entry.levelname))
            self.setItem(i, 2, QTableWidgetItem(entry.message))

        self.resizeColumnsToContents()
        self.horizontalHeader().setStretchLastSection(True)
        self.scrollToBottom()
