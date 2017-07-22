from avx.devices.net.atem import VideoSource, MessageTypes
from PySide.QtCore import QObject, Signal
from PySide.QtGui import QIcon


class Input(QObject):

    changedState = Signal()

    def __init__(self, source, label, icon=None):
        super(Input, self).__init__()
        self.source = source
        self.label = label
        self.icon = icon
        self.isLive = False
        self.isPreview = False

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
        (VideoSource.BLACK, "Black", QIcon(":icons/blackscreen"))
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


class SwitcherState(QObject):
    def __init__(self, atem):
        self.inputs = _default_inputs()
        self.outputs = _default_outputs()

        if atem:
            self.updateInputs(atem.getInputs())
            self.updateTally(atem.getTally())
            self.updateOutputs(atem.getAuxState())

    def updateInputs(self, inputs):
        for source, props in inputs.iteritems():
            if source in self.inputs:
                self.inputs[source].set_label(props['name_long'])
            else:
                self.inputs[source] = Input(source, props['name_long'], None)

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
                    self.outputs[aux].set_source(source)

    def handleMessage(self, msgType, data):
        if msgType == MessageTypes.TALLY:
            self.updateTally(data)
        elif msgType == MessageTypes.AUX_OUTPUT_MAPPING:
            self.updateOutputs(data)
