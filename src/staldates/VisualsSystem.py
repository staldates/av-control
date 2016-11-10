from staldates.ui.widgets.Dialogs import handlePyroErrors
from enum import Enum

EXTRAS_OUTPUT_TO_PREVIEW = 3


class IOEnum(Enum):
    def __init__(self, number, label):
        self.number = number
        self.label = label


class Input(object):

    def __init__(self, sourceChannel):
        self.sourceChannel = sourceChannel

    def preview(self, controller):
        pass

    def toPCMix(self, controller):
        pass

    def toMain(self, controller, mainChannel):
        pass


class MainInput(Input):

    def __init__(self, sourceChannel):
        super(MainInput, self).__init__(sourceChannel)

    @handlePyroErrors
    def preview(self, controller):
        controller["Main"].sendInputToOutput(self.sourceChannel, 1)
        controller["Extras"].sendInputToOutput(ExtrasSwitcherInputs.mainSwitcherOutput.number, EXTRAS_OUTPUT_TO_PREVIEW)

    @handlePyroErrors
    def toPCMix(self, controller):
        # 5 and 6 are wired opposite ways around on preview and main switchers
        if self.sourceChannel == MainSwitcherInputs.extras.number:
            controller["Preview"].sendInputToOutput(6, 2)
        elif self.sourceChannel == MainSwitcherInputs.visualsPC:
            controller["Preview"].sendInputToOutput(5, 2)
        else:
            controller["Preview"].sendInputToOutput(self.sourceChannel, 2)

    @handlePyroErrors
    def toMain(self, controller, mainChannel):
        controller["Main"].sendInputToOutput(self.sourceChannel, mainChannel)


class BlankMainInput(MainInput):

    def __init__(self):
        super(BlankMainInput, self).__init__(0)

    def toPCMix(self, controller):
        pass

    def preview(self, controller):
        pass


class ExtrasInput(Input):

    def __init__(self, ioenum):
        super(ExtrasInput, self).__init__(ioenum.number)
        self.name = ioenum.label

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


class ProxyInput(Input):

    def __init__(self, extrasSwitcher):
        super(ProxyInput, self).__init__(None)
        self.extrasSwitcher = extrasSwitcher

    def preview(self, controller):
        print "PROXY"
        self.extrasSwitcher.takePreview()

    def toPCMix(self, controller):
        pass

    def toMain(self, controller, mainChannel):
        pass


class MainSwitcherInputs(IOEnum):
    blank = (0, "Blank")
    camera1 = (1, "Camera 1")
    camera2 = (2, "Camera 2")
    camera3 = (3, "Camera 3")
    dvd = (4, "DVD")
    extras = (5, "Extras")
    visualsPC = (6, "Visuals PC")
# 7 - empty (former RGBHV)
# 8 - empty (former RGBHV)


blank = BlankMainInput()
camera1 = MainInput(MainSwitcherInputs.camera1.number)
camera2 = MainInput(MainSwitcherInputs.camera2.number)
camera3 = MainInput(MainSwitcherInputs.camera3.number)
dvd = MainInput(MainSwitcherInputs.dvd.number)
# Extras switcher not an explicit input
visualsPC = MainInput(MainSwitcherInputs.visualsPC.number)


class ExtrasSwitcherInputs(IOEnum):
    extras1 = (1, "Extras 1")
    extras2 = (2, "Extras 2")
    extras3 = (3, "Extras 3")
    extras4 = (4, "Extras 4")
# 5 - empty
# 6 - empty
    mainSwitcherOutput = (7, "Main output")
    visualsPCVideo = (8, "PC video")


extras1 = ExtrasInput(ExtrasSwitcherInputs.extras1)
extras2 = ExtrasInput(ExtrasSwitcherInputs.extras2)
extras3 = ExtrasInput(ExtrasSwitcherInputs.extras3)
extras4 = ExtrasInput(ExtrasSwitcherInputs.extras4)
visualsPCVideo = ExtrasInput(ExtrasSwitcherInputs.visualsPCVideo)
