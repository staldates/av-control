from staldates.ui.widgets.Dialogs import handlePyroErrors
from enum import Enum

EXTRAS_OUTPUT_TO_PREVIEW = 3


class Input(Enum):
    def __init__(self, sourceChannel, label):
        self.sourceChannel = sourceChannel
        self.label = label

    def preview(self, controller):
        pass

    def toPCMix(self, controller):
        pass

    def toMain(self, controller, mainChannel):
        pass


class Output(Enum):
    def __init__(self, destChannel, label):
        self.destChannel = destChannel
        self.label = label


class MainSwitcherInputs(Input):
    blank = (0, "Blank")
    camera1 = (1, "Camera 1")
    camera2 = (2, "Camera 2")
    camera3 = (3, "Camera 3")
    dvd = (4, "DVD")
    extras = (5, "Extras")
    visualsPC = (6, "Visuals PC")
# 7 - empty (former RGBHV)
# 8 - empty (former RGBHV)

    @handlePyroErrors
    def preview(self, controller):
        if self.sourceChannel == 0:
            return
        controller[MainSwitcher.device].sendInputToOutput(self.sourceChannel, MainSwitcher.output.extras_switcher_input.destChannel)
        controller[ExtrasSwitcher.device].sendInputToOutput(ExtrasSwitcher.input.mainSwitcherOutput.sourceChannel, ExtrasSwitcher.output.preview_monitor.destChannel)

    @handlePyroErrors
    def toPCMix(self, controller):
        # 5 and 6 are wired opposite ways around on preview and main switchers
        if self == MainSwitcherInputs.extras:
            controller[PreviewSwitcher.device].sendInputToOutput(PreviewSwitcher.input.extras.sourceChannel, PreviewSwitcher.output.pc_mix.destChannel)
        elif self == MainSwitcherInputs.visualsPC:
            controller[PreviewSwitcher.device].sendInputToOutput(PreviewSwitcher.input.visualsPC.sourceChannel, PreviewSwitcher.output.pc_mix.destChannel)
        else:
            controller[PreviewSwitcher.device].sendInputToOutput(self.sourceChannel, PreviewSwitcher.output.pc_mix.destChannel)

    @handlePyroErrors
    def toMain(self, controller, mainChannel):
        controller[MainSwitcher.device].sendInputToOutput(self.sourceChannel, mainChannel)


class MainSwitcherOutputs(Output):
    all = (0, "All")
    extras_switcher_input = (1, "Extras switcher input")
    monitor1 = (2, "Monitor 1")  # Formerly projectors
    font = (3, "Font")
    church = (4, "Church")
    welcome = (5, "Welcome")
    gallery = (6, "Gallery")
    special = (7, "Stage")
    record = (8, "Record")


class ExtrasSwitcherInputs(Input):
    extras1 = (1, "Extras 1")
    extras2 = (2, "Extras 2")
    extras3 = (3, "Extras 3")
    extras4 = (4, "Extras 4")
# 5 - empty
# 6 - empty
    mainSwitcherOutput = (7, "Main output")
    visualsPCVideo = (8, "PC video")

    @handlePyroErrors
    def preview(self, controller):
        controller[ExtrasSwitcher.device].sendInputToOutput(self.sourceChannel, ExtrasSwitcher.output.preview_monitor.destChannel)

    @handlePyroErrors
    def toPCMix(self, controller):
        controller[ExtrasSwitcher.device].sendInputToOutput(self.sourceChannel, ExtrasSwitcher.output.preview_switcher_input.destChannel)
        controller[PreviewSwitcher.device].sendInputToOutput(PreviewSwitcher.input.extras.sourceChannel, PreviewSwitcher.output.pc_mix.destChannel)

    @handlePyroErrors
    def toMain(self, controller, mainChannel):
        controller[ExtrasSwitcher.device].sendInputToOutput(self.sourceChannel, ExtrasSwitcher.output.main_switcher_input.destChannel)
        controller[MainSwitcher.device].sendInputToOutput(5, mainChannel)


class ExtrasSwitcherOutputs(Output):
    main_switcher_input = (1, "Main switcher")
    preview_switcher_input = (2, "Preview switcher")
    preview_monitor = (3, "Preview monitor")


class PreviewSwitcherInputs(Input):
    camera1 = (1, "Camera 1")
    camera2 = (2, "Camera 1")
    camera3 = (3, "Camera 1")
    dvd = (4, "DVD")
    visualsPC = (5, "Visuals PC")
    extras = (6, "Extras")


class PreviewSwitcherOutputs(Output):
    unused = (1, "Unused")
    pc_mix = (2, "PC Mix")


class MainSwitcher(object):
    device = "Main"
    input = MainSwitcherInputs
    output = MainSwitcherOutputs


class PreviewSwitcher(object):
    device = "Preview"
    input = PreviewSwitcherInputs
    output = PreviewSwitcherOutputs


class ExtrasSwitcher(object):
    device = "Extras"
    input = ExtrasSwitcherInputs
    output = ExtrasSwitcherOutputs
