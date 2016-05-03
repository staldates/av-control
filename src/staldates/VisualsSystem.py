EXTRAS_INPUT_FROM_MAIN = 7
EXTRAS_OUTPUT_TO_PREVIEW = 3


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

    def preview(self, controller):
        controller["Main"].sendInputToOutput(self.sourceChannel, 1)
        controller["Extras"].sendInputToOutput(EXTRAS_INPUT_FROM_MAIN, EXTRAS_OUTPUT_TO_PREVIEW)

    def toPCMix(self, controller):
        # 5 and 6 are wired opposite ways around on preview and main switchers
        if self.sourceChannel == 5:
            controller["Preview"].sendInputToOutput(6, 2)
        elif self.sourceChannel == 6:
            controller["Preview"].sendInputToOutput(5, 2)
        else:
            controller["Preview"].sendInputToOutput(self.sourceChannel, 2)

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

    def __init__(self, sourceChannel):
        super(ExtrasInput, self).__init__(sourceChannel)

    def preview(self, controller):
        controller["Extras"].sendInputToOutput(self.sourceChannel, EXTRAS_OUTPUT_TO_PREVIEW)

    def toPCMix(self, controller):
        controller["Extras"].sendInputToOutput(self.sourceChannel, 2)
        controller["Preview"].sendInputToOutput(6, 2)

    def toMain(self, controller, mainChannel):
        controller["Extras"].sendInputToOutput(self.sourceChannel, 1)
        controller["Main"].sendInputToOutput(5, mainChannel)


class ProxyInput(Input):

    def __init__(self, extrasSwitcher):
        super(ProxyInput, self).__init__(None)
        self.extrasSwitcher = extrasSwitcher

    def preview(self, controller):
        self.extrasSwitcher.takePreview()

    def toPCMix(self, controller):
        pass

    def toMain(self, controller, mainChannel):
        pass


#
# Main switcher inputs:
# 0 - Blank
# 1 - Camera 1
# 2 - Camera 2
# 3 - Camera 3
# 4 - DVD player
# 5 - Extras switcher out 1
# 6 - Visuals PC via scan converter
# 7 - empty (former RGBHV)
# 8 - empty (former RGBHV)
#

blank = BlankMainInput()
camera1 = MainInput(1)
camera2 = MainInput(2)
camera3 = MainInput(3)
dvd = MainInput(4)
# Extras switcher not an explicit input
visualsPC = MainInput(6)

#
# Extras switcher inputs:
# 1 - Extras 1
# 2 - Extras 2
# 3 - Extras 3
# 4 - Extras 4
# 5 - empty
# 6 - empty
# 7 - empty
# 8 - Visuals PC video
#

extras1 = ExtrasInput(1)
extras2 = ExtrasInput(2)
extras3 = ExtrasInput(3)
extras4 = ExtrasInput(4)
visualsPCVideo = ExtrasInput(8)
