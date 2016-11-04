from avx._version import __version__ as version


class MockController(object):
    def __init__(self):
        self.devices = {}

    def hasDevice(self, deviceID):
        return deviceID in self.devices.keys()

    def addDevice(self, device):
        self.devices[device.deviceID] = device

    def __getitem__(self, item):
        return self.devices.get(item)

    def getVersion(self):
        return version
