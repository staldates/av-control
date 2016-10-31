import argparse
import atexit
import fcntl  # @UnresolvedImport
import logging
import sys

from avx.Client import Client
from avx.controller.Controller import Controller, VersionMismatchError
from Pyro4.errors import NamingError, CommunicationError
from PySide.QtCore import Qt, QFile, QObject, QCoreApplication, QEvent
from PySide.QtGui import QApplication
from staldates.ui import resources  # @UnusedImport  # Initialises the Qt resources
from staldates.ui.MainWindow import MainWindow
from staldates.ui.StringConstants import StringConstants
from staldates.ui.widgets import Dialogs


class AvControlClient(Client):

    def __init__(self, avcontrol):
        super(AvControlClient, self).__init__()
        self.avcontrol = avcontrol

    def errorBox(self, text):
        invoke_in_main_thread(self.avcontrol.errorBox, text)
        return True

    def showPowerOnDialog(self):
        invoke_in_main_thread(self.avcontrol.showPowerDialog, StringConstants.poweringOn)
        return True

    def showPowerOffDialog(self):
        invoke_in_main_thread(self.avcontrol.showPowerDialog, StringConstants.poweringOff)
        return True

    def hidePowerDialog(self):
        invoke_in_main_thread(self.avcontrol.hidePowerDialog)
        return True

    def updateOutputMappings(self, mapping):
        invoke_in_main_thread(self.avcontrol.updateOutputMappings, mapping)
        return True


class InvokeEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, fn, *args, **kwargs):
        QEvent.__init__(self, InvokeEvent.EVENT_TYPE)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class Invoker(QObject):

    def event(self, event):
        event.fn(*event.args, **event.kwargs)

        return True

_invoker = Invoker()


def invoke_in_main_thread(fn, *args, **kwargs):
    QCoreApplication.postEvent(_invoker,
                               InvokeEvent(fn, *args, **kwargs))


def main():
    pid_file = 'av-control.pid'
    fp = open(pid_file, 'w')
    try:
        fcntl.lockf(fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        # another instance is running
        print "av-control is already running."
        sys.exit(1)

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                        level=logging.INFO)
    app = QApplication(sys.argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--fullscreen",
                        help="Run in fullscreen mode and hide the mouse cursor",
                        action="store_true")
    parser.add_argument("-c",
                        help="Specify the controller ID to connect to",
                        metavar="CONTROLLERID",
                        default="")
    args = parser.parse_args()

    try:
        ssf = QFile(":/stylesheet")
        ssf.open(QFile.ReadOnly)
        styleSheet = str(ssf.readAll())
        app.setStyleSheet(styleSheet)
    except IOError:
        # never mind
        logging.warn("Cannot find stylesheet, using default system styles.")

    try:
        controller = Controller.fromPyro(args.c)

        myapp = MainWindow(controller)

        client = AvControlClient(myapp)
        client.setDaemon(True)
        client.start()
        client.started.wait()
        atexit.register(lambda: controller.unregisterClient(client.uri))

        controller.registerClient(client.uri)

        if args.fullscreen:
            QApplication.setOverrideCursor(Qt.BlankCursor)
            myapp.showFullScreen()
        else:
            myapp.show()
        sys.exit(app.exec_())

    except (NamingError, CommunicationError) as e:
        Dialogs.errorBox("Unable to connect to controller. Please check network connections and try again. (Error details: " + str(e) + ")")
    except VersionMismatchError as e:
        Dialogs.errorBox(str(e))

if __name__ == '__main__':
    main()
