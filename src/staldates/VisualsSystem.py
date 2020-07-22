from avx.devices.net.atem import VideoSource, MessageTypes as ATEMMessageTypes
from avx.devices.net.atem.utils import NotInitializedException
from avx.devices.net.hyperdeck import TransportState, MessageTypes as HyperDeckMessageTypes
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
        self.tally = {}

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

    def set_tally(self, tally):
        for me, sources in tally.iteritems():
            self.tally.setdefault(me, {})['pgm'] = self.source in sources['pgm']
            self.tally.setdefault(me, {})['pvw'] = self.source in sources['pvw']
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
        (VideoSource.ME_1_PROGRAM, "Stream mix", None),
        (VideoSource.ME_1_PREVIEW, "Stream preview", None),
        (VideoSource.ME_2_PROGRAM, "Main mix", None),
        (VideoSource.ME_2_PREVIEW, "Preview", None),
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
        0: Output("Church", VideoSource.AUX_1),
        1: Output("Record", VideoSource.AUX_2),
        2: Output("Stage", VideoSource.AUX_3),
        3: Output("Gallery", VideoSource.AUX_4),
        4: Output("Aux 5", VideoSource.AUX_5),
        5: Output("Aux 6", VideoSource.AUX_6),
    }


class USK(QObject):
    changedState = Signal()

    def __init__(self, me_index, keyer_index):
        super(USK, self).__init__()
        self.me_index = me_index
        self.keyer_index = keyer_index
        self.onAir = False

    def set_on_air(self, onAir):
        if self.onAir != onAir:
            self.onAir = onAir
            self.changedState.emit()


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


class Transition(QObject):
    changedProps = Signal()

    def __init__(self):
        super(Transition, self).__init__()
        self.rate = 1

    def set_rate(self, rate):
        if self.rate != rate:
            self.rate = rate
            self.changedProps.emit()


class MixTransition(Transition):
    pass


class FadeToBlack(QObject):

    activeChanged = Signal(bool)
    rateChanged = Signal(int)

    def __init__(self):
        super(FadeToBlack, self).__init__()
        self.active = False
        self.rate = 25

    def set_active(self, active):
        if self.active != active:
            self.active = active
            self.activeChanged.emit(active)

    def set_rate(self, rate):
        if self.rate != rate:
            self.rate = rate
            self.rateChanged.emit(rate)


class SwitcherState(QObject):

    inputsChanged = Signal()
    connectionChanged = Signal(bool)

    def __init__(self, atem, me=1):
        super(SwitcherState, self).__init__()
        self.atem = atem
        self.me = me
        self.inputs = _default_inputs()
        self.outputs = _default_outputs()
        self.usks = {
            0: {
                0: USK(0, 0),
                1: USK(0, 1),
            },
            1: {
                0: USK(1, 0),
                1: USK(1, 1),
            },
        }
        self.dsks = {0: DSK(1), 1: DSK(2)}
        self.ftb = FadeToBlack()
        self.mixTransition = MixTransition()
        self.connected = False

        self._initFromAtem()

    def _initFromAtem(self):
        if self.atem:
            try:
                self.updateConnectedness(self.atem.isConnected())
                self.updateInputs(self.atem.getInputs())
                self.updateTally(self.atem.getTally())
                self.updateOutputs(self.atem.getAuxState())
                self.updateUSKs(self.atem.getUSKState())
                self.updateDSKs(self.atem.getDSKState())
                self.updateFTBState(self.atem.getFadeToBlackState(me=self.me))
                self.updateFTBRate(self.atem.getFadeToBlackProperties(me=self.me)['rate'])
                self.updateMixTransitionProps(self.atem.getMixTransitionProps(me=self.me))
            except NotInitializedException:
                pass

    def updateConnectedness(self, isConnected):
        if isConnected != self.connected:
            self.connected = isConnected
            self.connectionChanged.emit(isConnected)

    def updateInputs(self, inputs):
        for source, props in inputs.iteritems():
            if source in self.inputs and 'name_long' in props:
                self.inputs[source].set_label(props['name_long'])
            elif 'name_long' in props:
                self.inputs[source] = Input(source, props['name_long'], None)
        self.inputsChanged.emit()

        for output in self.outputs.values():
            if output.label_source in inputs and 'name_long' in inputs[output.label_source]:
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

    def updateUSKs(self, uskMap):
        for me_index, keyers in uskMap.iteritems():
            meks = self.usks.setdefault(me_index, {})
            for key_index, keyer in keyers.iteritems():
                if key_index not in meks:
                    meks[key_index] = USK(me_index, key_index)
                meks[key_index].set_on_air(keyer.get('on_air', False))

    def updateDSKs(self, dskMap):
        for idx, dsk in dskMap.iteritems():
            if idx in self.dsks:
                self.dsks[idx].set_on_air(dsk['on_air'])
                self.dsks[idx].set_rate(dsk['rate'])

    def updateFTBState(self, state):
        active = state and (state['full_black'] or state['in_transition'])
        self.ftb.set_active(active)

    def updateFTBRate(self, rate):
        self.ftb.set_rate(rate)

    def updateMixTransitionProps(self, props):
        if 'rate' in props:
            self.mixTransition.set_rate(props['rate'])

    def updateFullTally(self, tally):
        for ip in self.inputs.itervalues():
            ip.set_tally(tally)

    @property
    def me_index(self):
        return self.me - 1

    def handleMessage(self, msgType, data):
        if msgType == ATEMMessageTypes.TALLY:
            self.updateTally(data)
        elif msgType == ATEMMessageTypes.FULL_TALLY:
            self.updateFullTally(data)
        elif msgType == ATEMMessageTypes.AUX_OUTPUT_MAPPING:
            self.updateOutputs(data)
        elif msgType == ATEMMessageTypes.USK_STATE:
            self.updateUSKs(data)
        elif msgType == ATEMMessageTypes.DSK_STATE:
            self.updateDSKs(data)
        elif msgType == ATEMMessageTypes.INPUTS_CHANGED:
            self.updateInputs(self.atem.getInputs())
        elif msgType == ATEMMessageTypes.FTB_CHANGED:
            if self.me_index in data:
                self.updateFTBState(data[self.me_index])
        elif msgType == ATEMMessageTypes.FTB_RATE_CHANGED:
            if self.me_index in data:
                self.updateFTBRate(data[self.me_index])
        elif msgType == ATEMMessageTypes.TRANSITION_MIX_PROPERTIES_CHANGED:
            if self.me_index in data:
                self.updateMixTransitionProps(data[self.me_index])
        elif msgType == ATEMMessageTypes.ATEM_CONNECTED:
            self._initFromAtem()
        elif msgType == ATEMMessageTypes.ATEM_DISCONNECTED:
            self.updateConnectedness(False)


class HyperdeckState(QObject):

    transportChange = Signal(dict)
    clipsListChange = Signal(dict)

    def __init__(self, hyperdeck):
        super(HyperdeckState, self).__init__()
        self.deck = hyperdeck
        self.clip_listing = {}

        self.transport = {
            "status": TransportState.STOPPED
        }

        if self.deck:
            self.transport = self.deck.getTransportState()

    def handleMessage(self, msgType, data):
        if msgType == HyperDeckMessageTypes.TRANSPORT_STATE_CHANGED:
            self.transport = data
            self.transportChange.emit(data)
        if msgType == HyperDeckMessageTypes.CLIP_LISTING:
            self.clip_listing = data
            self.clipsListChange.emit(data)
