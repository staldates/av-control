from PySide.QtCore import QObject, Signal

import os
import simplejson


_PREFS_DIR = os.path.expanduser('~/.config/av-control')
_PREFS_FILE = os.path.join(_PREFS_DIR, 'preferences.json')


class _PrefsInstance(QObject):
    _changed = Signal(str, object)

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

    def get(self, name, default=None):
        return self._prefs.get(name, default)

    def set(self, name, value):
        if name not in self._prefs or self._prefs[name] != value:
            self._prefs[name] = value
            self._save()
            self._changed.emit(name, value)


class Preferences(object):
    """Preferences are accessed statically e.g. `Preferences.my_setting`. Don't instantiate the class."""
    _instance = _PrefsInstance()

    def __init__(self):
        raise Exception("Preferences should not be instantiated")

    @classmethod
    def get(cls, name, default=None):
        return cls._instance.get(name, default)

    @classmethod
    def set(cls, name, value):
        return cls._instance.set(name, value)

    @classmethod
    def subscribe(cls, callback):
        cls._instance._changed.connect(callback)
