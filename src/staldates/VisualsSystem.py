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
        controller["Main"].sendInputToOutput(self.sourceChannel, 1)
        controller["Extras"].sendInputToOutput(ExtrasSwitcherInputs.mainSwitcherOutput.sourceChannel, EXTRAS_OUTPUT_TO_PREVIEW)

    @handlePyroErrors
    def toPCMix(self, controller):
        # 5 and 6 are wired opposite ways around on preview and main switchers
        if self == MainSwitcherInputs.extras:
            controller["Preview"].sendInputToOutput(6, 2)
        elif self == MainSwitcherInputs.visualsPC:
            controller["Preview"].sendInputToOutput(5, 2)
        else:
            controller["Preview"].sendInputToOutput(self.sourceChannel, 2)

    @handlePyroErrors
    def toMain(self, controller, mainChannel):
        controller["Main"].sendInputToOutput(self.sourceChannel, mainChannel)


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
        controller["Extras"].sendInputToOutput(self.sourceChannel, EXTRAS_OUTPUT_TO_PREVIEW)

    @handlePyroErrors
    def toPCMix(self, controller):
        controller["Extras"].sendInputToOutput(self.sourceChannel, 2)
        controller["Preview"].sendInputToOutput(6, 2)

    @handlePyroErrors
    def toMain(self, controller, mainChannel):
        controller["Extras"].sendInputToOutput(self.sourceChannel, 1)
        controller["Main"].sendInputToOutput(5, mainChannel)
