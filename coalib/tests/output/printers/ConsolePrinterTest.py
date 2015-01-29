import sys
import os
import tempfile
import unittest
import pickle

sys.path.insert(0, ".")
from coalib.output.printers.ConsolePrinter import ConsolePrinter


class NullWriter:
    def write(self, *args):
        pass


class ConsolePrinterTestCase(unittest.TestCase):
    def test_printing(self):
        self.outputfile = os.path.join(tempfile.gettempdir(), "ConsolePrinterTestFile")
        with open(self.outputfile, "w") as self.handle:
            self.uut = ConsolePrinter(output=self.handle)

            self.uut.print("\ntest", "message", color="green")
            self.uut.print("\ntest", "message", color="greeeeen")
            self.uut.print("\ntest", "message")

        with open(self.outputfile, "r") as self.handle:
            self.assertEqual(self.handle.readlines(),
                             ['\033[0;32m\n',
                              'test message\n',
                              '\033[0m\n',
                              'test message\n',
                              '\n',
                              'test message\n'])

        os.remove(self.outputfile)

    def test_pickling(self):
        outputfile = os.path.join(tempfile.gettempdir(), "ConsolePrinterPickleTestFile")
        with open(outputfile, "wb") as f:
            pickle.dump(ConsolePrinter(), f)

        with open(outputfile, "rb") as f:
            obj = pickle.load(f)

        self.assertIsInstance(obj, ConsolePrinter)
        obj.print("test")  # print will use the output param, this will ensure that the printer is valid

        os.remove(outputfile)


if __name__ == '__main__':
    unittest.main(verbosity=2)
