from PySide.QtCore import Qt, QFile, QCoreApplication
from PySide.QtGui import QApplication
from avx.controller.Controller import Controller, VersionMismatchError
import argparse
import atexit
import fcntl  # @UnresolvedImport
import logging
import os
import sys

import Pyro4

from avcontrol import AvControlClient, InvokeEvent, Invoker
from staldates.ui import resources  # @UnusedImport  # Initialises the Qt resources
from staldates.ui.PowerRoom import PowerRoomControl
from staldates.ui.widgets import Dialogs
from staldates.ui.widgets.Dialogs import handlePyroErrors


Pyro4.config.COMMTIMEOUT = 3  # seconds

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

        adminPin = os.environ.get("ADMIN_PIN", None)
        myapp = PowerRoomControl(controller, adminPin)

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
