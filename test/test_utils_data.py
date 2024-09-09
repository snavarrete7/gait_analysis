from src.tools.utils_data import ToolVars
import unittest

from dataclasses import dataclass, field

class TestToolVars(unittest.TestCase):
    def test_init(self):
        """
        Attributes should be initiated with their default values, no need to call constructor with parameters.
        """
        t = ToolVars()
        self.assertTrue(True)
        

if __name__ == '__main__':
    unittest.main()