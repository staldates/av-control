'''
Created on 16 Apr 2013

@author: jrem
'''
import unittest
from staldates.ui.tests.GuiTest import GuiTest
from staldates.ui.tests.TestUtils import MockController


class TestVideoSwitcher(GuiTest):

    def setUp(self):
        GuiTest.setUp(self)
        self.mockController = MockController()

if __name__ == "__main__":
    unittest.main()
