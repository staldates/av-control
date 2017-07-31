from avx.devices.net.atem import VideoSource, MessageTypes
from avx.devices.net.atem.utils import NotInitializedException
from PySide.QtCore import QObject, Signal
from PySide.QtGui import QIcon
from staldates.ui.widgets.Dialogs import errorBox


def with_atem(func):
    def inner(elf, *args):
        if elf.atem:
            try:
                func(elf, *args)
            except NotInitializedException:
                errorBox("Controller is not connected to the visuals switcher!")
    return inner


class Input(QObject):

    changedState = Signal()

    def __init__(self, source, label, icon=None):
        super(Input, self).__init__()
        self.source = source
        self.label = label
        self.icon = icon
        self.isLive = False
        self.isPreview = False
        self.canBeUsed = True

    def set_label(self, new_label):
        if new_label != self.label:
            self.label = new_label
            self.changedState.emit()

    def set_live(self, isLive):
        if isLive != self.isLive:
            self.isLive = isLive
            self.changedState.emit()

    def set_preview(self, isPreview):
        if isPreview != self.isPreview:
            self.isPreview = isPreview
            self.changedState.emit()


def _default_inputs():
    return {source: Input(source, name, icon) for (source, name, icon) in [
        (VideoSource.INPUT_1, "Camera 1", QIcon(":icons/camera-video")),
        (VideoSource.INPUT_2, "Camera 2", QIcon(":icons/camera-video")),
        (VideoSource.INPUT_3, "Camera 3", QIcon(":icons/camera-video")),
        (VideoSource.INPUT_4, "DVD", QIcon(":icons/media-optical")),
        (VideoSource.INPUT_5, "Visuals PC", QIcon(":icons/computer")),
        (VideoSource.INPUT_6, "PC Video", QIcon(":icons/video-display")),
        (VideoSource.BLACK, "Black", QIcon(":icons/blackscreen")),
        (VideoSource.MEDIA_PLAYER_1, "Logo", QIcon(":icons/aldates"))
    ]}


class Output(QObject):

    changedState = Signal()

    def __init__(self, label, label_source):
        super(Output, self).__init__()
        self.label = label
        self.source = None
        self.label_source = label_source

    # Change the note of which source is being sent to this aux
    def set_source(self, source):
        if source != self.source:
            self.source = source
            self.changedState.emit()

    def set_label(self, label):
        if label != self.label:
            self.label = label
            self.changedState.emit()

    def __repr__(self, *args, **kwargs):
        return "<Output: {} (Internal ID {}) Showing: {} >".format(self.label, self.label_source, self.source)


def _default_outputs():
    return {
        0: Output("Record", VideoSource.AUX_1),
        1: Output("Stage", VideoSource.AUX_2),
        2: Output("Gallery", VideoSource.AUX_3),
        3: Output("Aux 4", VideoSource.AUX_4),
        4: Output("Aux 5", VideoSource.AUX_5),
        5: Output("Aux 6", VideoSource.AUX_6),
    }


class DSK(QObject):

    changedState = Signal()

    def __init__(self, idx):
        super(DSK, self).__init__()
        self.idx = idx
        self.onAir = False
        self.rate = 1

    def set_on_air(self, onAir):
        if self.onAir != onAir:
            self.onAir = onAir
            self.changedState.emit()

    def set_rate(self, rate):
        if self.rate != rate:
            self.rate = rate
            self.changedState.emit()

    def __repr__(self, *args, **kwargs):
        return "<DSK #{} (on air: {}) >".format(self.idx, self.onAir)


class SwitcherState(QObject):

    inputsChanged = Signal()

    def __init__(self, atem):
        super(SwitcherState, self).__init__()
        self.atem = atem
        self.inputs = _default_inputs()
        self.outputs = _default_outputs()
        self.dsks = {0: DSK(1), 1: DSK(2)}

        if atem:
            self.updateInputs(atem.getInputs())
            self.updateTally(atem.getTally())
            self.updateOutputs(atem.getAuxState())
            self.updateDSKs(atem.getDSKState())

    def updateInputs(self, inputs):
        for source, props in inputs.iteritems():
            if source in self.inputs:
                self.inputs[source].set_label(props['name_long'])
            else:
                self.inputs[source] = Input(source, props['name_long'], None)
            self.inputs[source].canBeUsed = props['me_availability']['ME1']
        self.inputsChanged.emit()

        for output in self.outputs.values():
            if output.label_source in inputs:
                output.set_label(inputs[output.label_source]['name_long'])

    def updateTally(self, tallyMap):
        for source, tally in tallyMap.iteritems():
            if source in self.inputs:
                self.inputs[source].set_preview(tally['prv'])
                self.inputs[source].set_live(tally['pgm'])

    def updateOutputs(self, auxMap):
        for aux, source in auxMap.iteritems():
            if aux in self.outputs:
                if source in self.inputs:
                    self.outputs[aux].set_source(self.inputs[source])
                else:
                    print "BAD THINGS"
                    self.outputs[aux].set_source(source)

    def updateDSKs(self, dskMap):
        for idx, dsk in dskMap.iteritems():
            if idx in self.dsks:
                self.dsks[idx].set_on_air(dsk['on_air'])
                self.dsks[idx].set_rate(dsk['rate'])

    def handleMessage(self, msgType, data):
        if msgType == MessageTypes.TALLY:
            self.updateTally(data)
        elif msgType == MessageTypes.AUX_OUTPUT_MAPPING:
            self.updateOutputs(data)
        elif msgType == MessageTypes.DSK_STATE:
            self.updateDSKs(data)
        elif msgType == MessageTypes.INPUTS_CHANGED:
            self.updateInputs(self.atem.getInputs())
