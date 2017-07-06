"""Unit test for textbox module
"""

import unittest

from ..size import Size
from ..textbox import TextBox

class TextBoxUnitTest(unittest.TestCase):

    def test_1_constr(self):

        box = TextBox(x0=Size(1), y0=Size(2), width=Size(4), height=Size(8), text='abc')
        self.assertEqual(box.x0.value, 1)
        self.assertEqual(box.y0.value, 2)
        self.assertEqual(box.width.value, 4)
        self.assertEqual(box.height.value, 8)
        self.assertEqual(box.text, 'abc')

    def test_2_dim(self):

        box = TextBox(x0=Size(1), y0=Size(2), width=Size(4), height=Size(8))
        self.assertEqual(box.x1.value, 5)
        self.assertEqual(box.y1.value, 10)
        self.assertEqual(box.midx.value, 3)
        self.assertEqual(box.midy.value, 6)

    def test_3_split(self):

        box = TextBox(width='36pt', font_size='10pt')
        lines = box._splitText('abcdefg')
        self.assertEqual(lines, ['abcdefg'])
        lines = box._splitText('abcdefg ABCDEFG')
        self.assertEqual(lines, ['abcdefg', 'ABCDEFG'])
        lines = box._splitText('abcdefg     ABCDEFG')
        self.assertEqual(lines, ['abcdefg', 'ABCDEFG'])
        lines = box._splitText('abc defg   ABCD EFG')
        self.assertEqual(lines, ['abc', 'defg', 'ABCD', 'EFG'])

    def test_4_reflow(self):

        box = TextBox(width='36pt', text='abcdefg ABCDEFG', font_size='10pt',
                      line_spacing='3pt', padding='5pt')
        box.reflow()
        self.assertEqual(box.height.pt, 10 * 2 + 3 + 2 * 5)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TextBoxUnitTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
