class Input(object):

    def __init__(self, sourceChannel):
        self.sourceChannel = sourceChannel

    def preview(self, controller):
        pass

    def toPCMix(self, controller):
        pass

    def toMain(self, controller):
        pass


class MainInput(Input):

    def __init__(self, sourceChannel):
        super(MainInput, self).__init__(sourceChannel)

    def preview(self, controller):
        # 5 and 6 are wired opposite ways around on preview and main switchers
        if self.sourceChannel == 5:
            controller.switch("Preview", 6, 1)
        elif self.sourceChannel == 6:
            controller.switch("Preview", 5, 1)
        else:
            controller.switch("Preview", self.sourceChannel, 1)

    def toPCMix(self, controller):
        # 5 and 6 are wired opposite ways around on preview and main switchers
        if self.sourceChannel == 5:
            controller.switch("Preview", 6, 2)
        elif self.sourceChannel == 6:
            controller.switch("Preview", 5, 2)
        else:
            controller.switch("Preview", self.sourceChannel, 2)

    def toMain(self, controller, mainChannel):
        controller.switch("Main", self.sourceChannel, mainChannel)


class ExtrasInput(Input):

    def __init__(self, sourceChannel):
        super(ExtrasInput, self).__init__(sourceChannel)

    def preview(self, controller):
        controller.switch("Extras", self.sourceChannel, 2)
        controller.switch("Preview", 6, 1)

    def toPCMix(self, controller):
        controller.switch("Preview", self.sourceChannel, 2)

    def toMain(self, controller, mainChannel):
        controller.switch("Extras", self.sourceChannel, 1)
        controller.switch("Main", 5, mainChannel)

camera1 = MainInput(1)
camera2 = MainInput(2)
camera3 = MainInput(3)
dvd = MainInput(4)
visualsPC = MainInput(5)

extras1 = ExtrasInput(1)
extras2 = ExtrasInput(2)
extras3 = ExtrasInput(3)
extras4 = ExtrasInput(4)
visualsPCVideo = ExtrasInput(8)
