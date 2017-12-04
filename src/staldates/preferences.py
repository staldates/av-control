from PySide.QtCore import QObject, Signal

import os
import simplejson


_PREFS_DIR = os.path.expanduser('~/.config/av-control')
_PREFS_FILE = os.path.join(_PREFS_DIR, 'preferences.json')


class _PrefsInstance(QObject):
    changed = Signal()

    def __init__(self):
        QObject.__init__(self)
        self._prefs = {}
        self._load()

    def _load(self):
        try:
            with open(_PREFS_FILE, 'r') as prefs_file:
                self._prefs = simplejson.load(prefs_file)
        except Exception:
            print 'No prefs file found or prefs file unreadable'

    def _save(self):
        try:
            if not os.path.exists(_PREFS_DIR):
                os.makedirs(_PREFS_DIR)
            with open(_PREFS_FILE, 'w') as prefs_file:
                simplejson.dump(self._prefs, prefs_file)
        except Exception:
            print 'Exception while trying to save preferences file'
            raise

    def __getattr__(self, name):
        if name[0] == '_':
            return super(_PrefsInstance, self).__getattr__(name)
        return self._prefs[name]

    def __setattr__(self, name, value):
        if name[0] == '_':
            return super(_PrefsInstance, self).__setattr__(name, value)
        self._prefs[name] = value
        self._save()
        self.changed.emit()


class _PreferencesType(type):
    _instance = _PrefsInstance()

    def __getattr__(self, name):
        return getattr(self._instance, name)

    def __setattr__(self, name, value):
        return setattr(self._instance, name, value)


class Preferences:
    """Preferences are accessed statically e.g. `Preferences.my_setting`. Don't instantiate the class."""
    __metaclass__ = _PreferencesType

    def __init__(self):
        raise Exception("Preferences should not be instantiated")
