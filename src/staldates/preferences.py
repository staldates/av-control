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
        dotpath = name.split('.')
        return self._get_dotpath(self._prefs, dotpath, default)

    def set(self, name, value):
        dotpath = name.split('.')
        if self._set_dotpath(self._prefs, dotpath, value):
            self._changed.emit(name, value)

    def _get_dotpath(self, container, path, default):
        if len(path) == 1:
            return container.get(path[0], default)
        else:
            next_container = path.pop(0)
            if next_container in container:
                return self._get_dotpath(
                    container[next_container],
                    path,
                    default
                )
            else:
                return default

    def _set_dotpath(self, container, path, value):
        if len(path) == 1:
            # We have reached the leaf
            if path[0] not in container or container[path[0]] != value:
                container[path[0]] = value
                self._save()
                return True
        else:
            next_container = path.pop(0)
            return self._set_dotpath(
                container.setdefault(next_container, {}),
                path,
                value
            )
        return False


class Preferences(object):
    """
    Preferences are accessed statically e.g. `Preferences.get(my_setting)`.
    Don't instantiate the class.
    """
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
