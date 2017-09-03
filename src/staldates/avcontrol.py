import argparse
import atexit
import fcntl  # @UnresolvedImport
import logging
import os
import Pyro4
import sys

from avx.Client import Client
from avx.controller.Controller import Controller, VersionMismatchError
from PySide.QtCore import Qt, QFile, QObject, QCoreApplication, QEvent
from PySide.QtGui import QApplication
from staldates.ui import resources  # @UnusedImport  # Initialises the Qt resources
from staldates.ui.MainWindow import MainWindow
from staldates.ui.widgets import Dialogs
from staldates.ui.widgets.Dialogs import handlePyroErrors
from staldates.joystick import Joystick, CameraJoystickAdapter


Pyro4.config.COMMTIMEOUT = 3  # seconds


class AvControlClient(Client):

    def __init__(self, avcontrol):
        super(AvControlClient, self).__init__()
        self.avcontrol = avcontrol

    def errorBox(self, text):
        invoke_in_main_thread(self.avcontrol.errorBox, text)
        return True

    @Pyro4.expose
    def handleMessage(self, msgType, sourceDeviceID, data):
        invoke_in_main_thread(self.avcontrol.handleMessage, msgType, sourceDeviceID, data)


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


@handlePyroErrors(extraMessage="Cannot start application due to a network error -")
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

        if os.path.exists("/dev/input/js0"):
            js = Joystick("/dev/input/js0")
            js.start()
        else:
            js = None

        jsa = CameraJoystickAdapter(js)
        jsa.start()
        myapp = MainWindow(controller, jsa)

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

    except VersionMismatchError as e:
        Dialogs.errorBox(str(e))


if __name__ == '__main__':
    main()
