import unittest
from azenqos_plugin_dialog import TableWindow

class TableTest(unittest.TestCase):
    def test_universe(self):
        table = TableWindow(None,'Hello')
        self.assertEqual(table.title, 'Hello')

if __name__ == '__main__':
    unittest.main()